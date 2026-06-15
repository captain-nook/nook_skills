#!/usr/bin/env node
/**
 * nook-image2-gpt 一键部署脚本
 * 用法：node setup.js sk-YOUR_API_KEY [https://custom-relay-base-url]
 */

import { execSync } from "child_process";
import fs from "fs";
import path from "path";
import os from "os";
import readline from "readline/promises";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SERVER_PATH = path.resolve(__dirname, "server", "index.js");
const SERVER_DIR = path.resolve(__dirname, "server");
const ENV_PATH = path.resolve(__dirname, ".env");
const MCP_NAME = "nook-image2-gpt";
const home = os.homedir();
const DEFAULT_API_BASE_URL = "https://sub.jarodfund.xyz/v1";

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
      if (char === "\u0003") {
        stdin.setRawMode(false);
        stdin.pause();
        stdin.off("data", onData);
        reject(new Error("Cancelled"));
        return;
      }
      if (char === "\r" || char === "\n") return finish(value.trim());
      if (char === "\b" || char === "\u007f") {
        if (value.length > 0) {
          value = value.slice(0, -1);
          stdout.write("\b \b");
        }
        return;
      }
      value += char;
      stdout.write("*".repeat([...char].length));
    }

    stdin.on("data", onData);
  });
}

// ── API key ──────────────────────────────────────────────────────────────────
let apiKey = process.argv[2] || process.env.IMAGE_API_KEY || "";
if (!apiKey) {
  console.log("nook-image2-gpt setup");
  console.log("This will write your key to local .env and agent MCP config.");
  apiKey = await promptSecret("IMAGE_API_KEY");
}
if (!apiKey || apiKey.length < 8) {
  console.error("Missing or invalid IMAGE_API_KEY.");
  console.error("Usage: node setup.js [YOUR_API_KEY] [https://custom-relay-base-url]");
  process.exit(1);
}

let apiBase = process.argv[3] || process.env.IMAGE_API_BASE_URL || "";
if (!apiBase) {
  apiBase = await promptText("IMAGE_API_BASE_URL", DEFAULT_API_BASE_URL);
}
const env = {
  IMAGE_API_KEY: apiKey,
  IMAGE_API_BASE_URL: apiBase,
  IMAGE_MODEL: process.env.IMAGE_MODEL || "gpt-image-2",
  IMAGE_RESPONSE_FORMAT: "b64_json",
  IMAGE_DRY_RUN: "false",
  IMAGE_OUTPUT_DIR: process.env.IMAGE_OUTPUT_DIR || "output"
};

// ── npm install ──────────────────────────────────────────────────────────────
console.log("📦 Installing dependencies...");
execSync("npm install", { cwd: SERVER_DIR, stdio: "inherit" });

// ── write local .env for tools that launch the server without env forwarding ──
const envText = Object.entries(env)
  .map(([key, value]) => `${key}=${String(value).replace(/\r?\n/g, "")}`)
  .join("\n") + "\n";
fs.writeFileSync(ENV_PATH, envText, "utf8");
console.log(`✅ Wrote ${ENV_PATH}`);

// ── helpers ──────────────────────────────────────────────────────────────────
let configured = 0;

function mergeJson(filePath, updater) {
  let cfg = {};
  if (fs.existsSync(filePath)) {
    try { cfg = JSON.parse(fs.readFileSync(filePath, "utf8")); } catch {}
  }
  updater(cfg);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(cfg, null, 2));
}

function tryFirst(paths, label, updater) {
  for (const p of paths) {
    const dir = path.dirname(p);
    if (!fs.existsSync(dir)) continue;
    mergeJson(p, updater);
    console.log(`✅ ${label} → ${p}`);
    configured++;
    return true;
  }
  return false;
}

// Standard mcpServers format: { mcpServers: { name: { command, args, env } } }
const stdEntry = { command: "node", args: [SERVER_PATH], env };

// VSCode-storage format (cursor.mcp.servers is a JSON string)
function vscodeStorageUpdater(storageKey) {
  return (cfg) => {
    let servers = {};
    try { servers = JSON.parse(cfg[storageKey] ?? "{}"); } catch {}
    servers[MCP_NAME] = stdEntry;
    cfg[storageKey] = JSON.stringify(servers);
  };
}

// ── Configure each agent ─────────────────────────────────────────────────────

// Claude Code — user-level (~/.claude/claude_desktop_config.json)
tryFirst(
  [path.join(home, ".claude", "claude_desktop_config.json")],
  "Claude Code",
  (cfg) => { cfg.mcpServers ??= {}; cfg.mcpServers[MCP_NAME] = stdEntry; }
);

// Kiro
tryFirst(
  [path.join(home, ".kiro", "mcp.json")],
  "Kiro",
  (cfg) => { cfg.mcpServers ??= {}; cfg.mcpServers[MCP_NAME] = stdEntry; }
);

// opencode
tryFirst(
  [
    path.join(home, ".config", "opencode", "opencode.json"),
    path.join(home, "AppData", "Roaming", "opencode", "opencode.json"),
  ],
  "opencode",
  (cfg) => {
    cfg.mcp ??= {};
    cfg.mcp[MCP_NAME] = { type: "local", command: ["node", SERVER_PATH], enabled: true, environment: env };
  }
);

// Cursor
tryFirst(
  [
    path.join(home, "AppData", "Roaming", "Cursor", "User", "globalStorage", "storage.json"),
    path.join(home, "Library", "Application Support", "Cursor", "User", "globalStorage", "storage.json"),
    path.join(home, ".config", "Cursor", "User", "globalStorage", "storage.json"),
  ],
  "Cursor",
  vscodeStorageUpdater("cursor.mcp.servers")
);

// Windsurf (same storage format as Cursor)
tryFirst(
  [
    path.join(home, "AppData", "Roaming", "Windsurf", "User", "globalStorage", "storage.json"),
    path.join(home, "Library", "Application Support", "Windsurf", "User", "globalStorage", "storage.json"),
    path.join(home, ".config", "Windsurf", "User", "globalStorage", "storage.json"),
  ],
  "Windsurf",
  vscodeStorageUpdater("cursor.mcp.servers")
);

// Cline (VS Code extension)
tryFirst(
  [
    path.join(home, "AppData", "Roaming", "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings", "cline_mcp_settings.json"),
    path.join(home, "Library", "Application Support", "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings", "cline_mcp_settings.json"),
    path.join(home, ".config", "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings", "cline_mcp_settings.json"),
  ],
  "Cline",
  (cfg) => { cfg.mcpServers ??= {}; cfg.mcpServers[MCP_NAME] = stdEntry; }
);

// Continue (VS Code extension)
tryFirst(
  [path.join(home, ".continue", "config.json")],
  "Continue",
  (cfg) => { cfg.mcpServers ??= {}; cfg.mcpServers[MCP_NAME] = stdEntry; }
);

// Zed
tryFirst(
  [path.join(home, ".config", "zed", "settings.json")],
  "Zed",
  (cfg) => {
    cfg.context_servers ??= {};
    cfg.context_servers[MCP_NAME] = {
      command: { path: "node", args: [SERVER_PATH], env },
    };
  }
);

// ── Result ───────────────────────────────────────────────────────────────────
console.log(configured > 0
  ? `\n🎉 Done! Configured ${configured} client(s). Restart your agent.`
  : `\n⚠️  No agent found. Add manually:\n   name: ${MCP_NAME}\n   command: node "${SERVER_PATH}"\n   env: IMAGE_API_KEY=${apiKey}`
);
