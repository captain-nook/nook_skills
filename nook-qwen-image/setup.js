#!/usr/bin/env node

import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import readline from "node:readline/promises";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SERVER_PATH = path.resolve(__dirname, "server", "index.js").replace(/\\/g, "/");
const SERVER_DIR = path.resolve(__dirname, "server");
const ENV_PATH = path.resolve(__dirname, ".env");
const MCP_NAME = "nook-qwen-image";
const home = os.homedir();

// --- CLI flags --------------------------------------------------------------
const args = process.argv.slice(2);
const FLAGS = { remove: false, agent: null, key: null, help: false };
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === "--remove" || a === "-r") FLAGS.remove = true;
  else if (a === "--agent" || a === "-a") FLAGS.agent = args[++i] || null;
  else if (a === "--help" || a === "-h") FLAGS.help = true;
  else if (a.startsWith("--agent=")) FLAGS.agent = a.slice("--agent=".length);
  else if (!a.startsWith("-")) FLAGS.key = a;
}

if (FLAGS.help) {
  console.log(`Usage: node setup.js [key] [--agent <name>] [--remove]
  key        ModelScope API key (or set MS_API_KEY env var)
  --agent    Limit to a single client: claude|codex|trae|cursor|kiro|windsurf|continue
  --remove   Remove MCP entries from detected agent configs and delete .env
  -h, --help Show this help
`);
  process.exit(0);
}

const SUPPORTED_AGENTS = ["claude", "codex", "trae", "cursor", "kiro", "windsurf", "continue"];
const targetAgents = (FLAGS.agent ? [FLAGS.agent.toLowerCase()] : SUPPORTED_AGENTS)
  .filter((a) => SUPPORTED_AGENTS.includes(a));
if (FLAGS.agent && !SUPPORTED_AGENTS.includes(FLAGS.agent.toLowerCase())) {
  console.error(`Unknown --agent "${FLAGS.agent}". Supported: ${SUPPORTED_AGENTS.join(", ")}`);
  process.exit(1);
}
const forceAgent = (process.env.NOOK_SETUP_AGENT_FORCE || "").toLowerCase();
if (forceAgent && SUPPORTED_AGENTS.includes(forceAgent)) {
  console.log(`(forced agent: ${forceAgent} via NOOK_SETUP_AGENT_FORCE)`);
}

// --- helpers ---------------------------------------------------------------
async function promptText(question, defaultValue = "") {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const suffix = defaultValue ? ` (${defaultValue})` : "";
  const answer = (await rl.question(`${question}${suffix}: `)).trim();
  rl.close();
  return answer || defaultValue;
}

async function promptSecret(question) {
  if (!process.stdin.isTTY) return promptText(question);
  return await new Promise((resolve, reject) => {
    const stdin = process.stdin;
    const stdout = process.stdout;
    let value = "";
    stdout.write(`${question}: `);
    stdin.setRawMode(true);
    stdin.resume();
    stdin.setEncoding("utf8");
    function finish(result) {
      stdin.setRawMode(false);
      stdin.pause();
      stdin.off("data", onData);
      stdout.write("\n");
      resolve(result);
    }
    function onData(char) {
      if (char === "\u0003") { reject(new Error("Cancelled")); return; }
      if (char === "\r" || char === "\n") return finish(value.trim());
      if (char === "\b" || char === "\u007f") {
        if (value.length > 0) { value = value.slice(0, -1); stdout.write("\b \b"); }
        return;
      }
      value += char;
      stdout.write("*".repeat([...char].length));
    }
    stdin.on("data", onData);
  });
}

function readEnvValue(envPath, key) {
  if (!fs.existsSync(envPath)) return "";
  const envText = fs.readFileSync(envPath, "utf8");
  for (const raw of envText.split(/\r?\n/)) {
    const line = raw.trim().replace(/^\uFEFF/, "");
    if (!line || line.startsWith("#") || !line.includes("=")) continue;
    const index = line.indexOf("=");
    const foundKey = line.slice(0, index).trim();
    if (foundKey !== key) continue;
    return line.slice(index + 1).trim().replace(/^["']|["']$/g, "");
  }
  return "";
}

console.log(FLAGS.remove ? "nook-qwen-image uninstall" : "nook-qwen-image setup");
console.log(FLAGS.remove
  ? "Removing MCP entries from detected agent configs and deleting .env."
  : "Writes your ModelScope key to local .env and configures the Qwen-Image MCP server when possible.");

// --- 1. env handling --------------------------------------------------------
if (FLAGS.remove) {
  if (fs.existsSync(ENV_PATH)) {
    fs.unlinkSync(ENV_PATH);
    console.log(`Removed ${ENV_PATH}`);
  } else {
    console.log("No .env to remove.");
  }
} else {
  // First, try to share MS_API_KEY with nook-zimage sibling if present.
  const siblingEnvPath = path.resolve(__dirname, "..", "nook-zimage", "nook-zimage", ".env");
  const existingKey = readEnvValue(ENV_PATH, "MS_API_KEY") || readEnvValue(siblingEnvPath, "MS_API_KEY");

  let apiKey = FLAGS.key || process.env.MS_API_KEY || existingKey || "";
  if (!apiKey) apiKey = await promptSecret("MS_API_KEY");
  if (!apiKey || apiKey.length < 8) {
    console.error("Missing or invalid MS_API_KEY (need at least 8 chars).");
    process.exit(1);
  }

  const env = {
    MS_API_KEY: apiKey,
    MS_API_BASE_URL: process.env.MS_API_BASE_URL || "https://api-inference.modelscope.cn",
    MS_IMAGE_MODEL: process.env.MS_IMAGE_MODEL || "Qwen/Qwen-Image",
    QWEN_IMAGE_OUTPUT_DIR: process.env.QWEN_IMAGE_OUTPUT_DIR || "output",
    QWEN_IMAGE_DRY_RUN: process.env.QWEN_IMAGE_DRY_RUN || "false",
  };

  if (fs.existsSync(path.join(SERVER_DIR, "package.json"))) {
    console.log("Installing MCP server dependencies...");
    execSync("npm install --cache .npm-cache", { cwd: SERVER_DIR, stdio: "inherit" });
  } else {
    console.log(`No server/package.json found at ${SERVER_DIR}; skipping npm install.`);
  }

  const envText = Object.entries(env)
    .map(([key, value]) => `${key}=${String(value).replace(/\r?\n/g, "")}`)
    .join("\n") + "\n";
  fs.writeFileSync(ENV_PATH, envText, "utf8");
  console.log(`Wrote ${ENV_PATH}`);
}

// --- 2. MCP config writers --------------------------------------------------
let configured = 0;
let removed = 0;

function mergeJson(filePath, updater) {
  let cfg = {};
  if (fs.existsSync(filePath)) {
    try { cfg = JSON.parse(fs.readFileSync(filePath, "utf8")); } catch {}
  }
  updater(cfg);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(cfg, null, 2), "utf8");
}

function tryFirst(paths, label, updater, isRemove) {
  for (const p of paths) {
    const dir = path.dirname(p);
    if (!fs.existsSync(dir)) continue;
    mergeJson(p, updater);
    if (isRemove) {
      console.log(`${label} cleaned: ${p}`);
      removed++;
    } else {
      console.log(`${label} configured: ${p}`);
      configured++;
    }
    return true;
  }
  return false;
}

function tryFirstToml(filePath, label, builder, remover) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) return false;
  let content = "";
  if (fs.existsSync(filePath)) content = fs.readFileSync(filePath, "utf8");
  const next = FLAGS.remove ? remover(content) : builder(content);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(filePath, next, "utf8");
  if (FLAGS.remove) { console.log(`${label} cleaned: ${filePath}`); removed++; }
  else { console.log(`${label} configured: ${filePath}`); configured++; }
  return true;
}

const stdEntry = { command: "node", args: [SERVER_PATH], env: { MS_API_KEY: process.env.MS_API_KEY || readEnvValue(ENV_PATH, "MS_API_KEY") || "" } };

function buildJsonAdd(servers) {
  return (cfg) => { cfg[servers] ??= {}; cfg[servers][MCP_NAME] = stdEntry; };
}
function buildJsonRemove(servers) {
  return (cfg) => { if (cfg[servers]) delete cfg[servers][MCP_NAME]; };
}

function buildJsonAddTopMcp() {
  return (cfg) => { cfg.mcpServers ??= {}; cfg.mcpServers[MCP_NAME] = stdEntry; };
}
function buildJsonRemoveTopMcp() {
  return (cfg) => { if (cfg.mcpServers) delete cfg.mcpServers[MCP_NAME]; };
}

function vscodeStorageJsonAdd(storageKey) {
  return (cfg) => {
    let servers = {};
    try { servers = JSON.parse(cfg[storageKey] ?? "{}"); } catch {}
    servers[MCP_NAME] = stdEntry;
    cfg[storageKey] = JSON.stringify(servers);
  };
}
function vscodeStorageJsonRemove(storageKey) {
  return (cfg) => {
    let servers = {};
    try { servers = JSON.parse(cfg[storageKey] ?? "{}"); } catch {}
    delete servers[MCP_NAME];
    cfg[storageKey] = JSON.stringify(servers);
  };
}

function buildCodexTomlAdd(content) {
  const block = [
    "",
    `[mcp_servers.${MCP_NAME}]`,
    `command = "node"`,
    `args = ["${SERVER_PATH}"]`,
    `env = { MS_API_KEY = "${(process.env.MS_API_KEY || readEnvValue(ENV_PATH, "MS_API_KEY") || "").replace(/"/g, '\\"')}" }`,
    `startup_timeout_sec = 120`,
    `tool_timeout_sec = 300`,
    ""
  ].join("\n");
  // Drop existing block first, then append.
  return buildCodexTomlRemove(content) + block;
}
function buildCodexTomlRemove(content) {
  const re = new RegExp(`\\n*\\[mcp_servers\\.${MCP_NAME}\\]\\n[\\s\\S]*?(?=\\n\\[|\\n*$|\\Z)`, "m");
  return content.replace(re, "").replace(/\n{3,}/g, "\n\n");
}

// --- 3. Apply per-agent ----------------------------------------------------
const want = (name) => targetAgents.includes(name) && (!forceAgent || forceAgent === name);

if (want("claude")) {
  tryFirst(
    [path.join(home, ".claude", "claude_desktop_config.json")],
    "Claude Code",
    FLAGS.remove ? buildJsonRemoveTopMcp() : buildJsonAddTopMcp(),
    FLAGS.remove
  );
}

if (want("kiro")) {
  tryFirst(
    [path.join(home, ".kiro", "mcp.json")],
    "Kiro",
    FLAGS.remove ? buildJsonRemoveTopMcp() : buildJsonAddTopMcp(),
    FLAGS.remove
  );
}

if (want("trae")) {
  tryFirst(
    [
      path.join(home, "AppData", "Roaming", "Trae", "User", "globalStorage", "mcp.json"),
      path.join(home, "AppData", "Roaming", "Trae CN", "User", "globalStorage", "mcp.json"),
      path.join(home, "AppData", "Roaming", "Trae-CN", "User", "globalStorage", "mcp.json"),
      path.join(home, "Library", "Application Support", "Trae", "User", "globalStorage", "mcp.json"),
      path.join(home, ".config", "Trae", "User", "globalStorage", "mcp.json"),
    ],
    "Trae IDE",
    FLAGS.remove ? buildJsonRemoveTopMcp() : buildJsonAddTopMcp(),
    FLAGS.remove
  );
}

if (want("codex")) {
  const codexPath = path.join(home, ".codex", "config.toml");
  if (fs.existsSync(path.dirname(codexPath))) {
    tryFirstToml(codexPath, "Codex CLI", buildCodexTomlAdd, buildCodexTomlRemove);
  } else {
    console.log(`Codex CLI skipped: ${path.dirname(codexPath)} not found.`);
  }
}

if (want("cursor")) {
  tryFirst(
    [
      path.join(home, "AppData", "Roaming", "Cursor", "User", "globalStorage", "storage.json"),
      path.join(home, "Library", "Application Support", "Cursor", "User", "globalStorage", "storage.json"),
      path.join(home, ".config", "Cursor", "User", "globalStorage", "storage.json"),
    ],
    "Cursor",
    FLAGS.remove ? vscodeStorageJsonRemove("cursor.mcp.servers") : vscodeStorageJsonAdd("cursor.mcp.servers"),
    FLAGS.remove
  );
}

if (want("windsurf")) {
  tryFirst(
    [
      path.join(home, "AppData", "Roaming", "Windsurf", "User", "globalStorage", "storage.json"),
      path.join(home, "Library", "Application Support", "Windsurf", "User", "globalStorage", "storage.json"),
      path.join(home, ".config", "Windsurf", "User", "globalStorage", "storage.json"),
    ],
    "Windsurf",
    FLAGS.remove ? vscodeStorageJsonRemove("cursor.mcp.servers") : vscodeStorageJsonAdd("cursor.mcp.servers"),
    FLAGS.remove
  );
}

if (want("continue")) {
  tryFirst(
    [path.join(home, ".continue", "config.json")],
    "Continue",
    FLAGS.remove ? buildJsonRemoveTopMcp() : buildJsonAddTopMcp(),
    FLAGS.remove
  );
}

// --- 4. Done ----------------------------------------------------------------
if (FLAGS.remove) {
  console.log(removed > 0
    ? `Uninstall complete. Removed ${removed} client(s). Repo folder untouched.`
    : "Uninstall complete. No client configs found.");
} else {
  console.log(configured > 0
    ? `Done. Configured ${configured} client(s). Restart your agent, then try "出一张测试图 512x512".`
    : `No supported agent config found. Add manually: node "${SERVER_PATH}" with MS_API_KEY in env.`);
}
