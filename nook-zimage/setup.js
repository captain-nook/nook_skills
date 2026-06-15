#!/usr/bin/env node

import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import readline from "node:readline/promises";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SERVER_PATH = path.resolve(__dirname, "server", "index.js");
const SERVER_DIR = path.resolve(__dirname, "server");
const ENV_PATH = path.resolve(__dirname, ".env");
const MCP_NAME = "nook-zimage";
const home = os.homedir();

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

console.log("nook-zimage setup");
console.log("This writes your ModelScope key to local .env and configures the MCP server when possible.");

let apiKey = process.argv[2] || process.env.MS_API_KEY || "";
if (!apiKey) apiKey = await promptSecret("MS_API_KEY");
if (!apiKey || apiKey.length < 8) {
  console.error("Missing or invalid MS_API_KEY.");
  process.exit(1);
}

const env = {
  MS_API_KEY: apiKey,
  MS_API_BASE_URL: process.env.MS_API_BASE_URL || "https://api-inference.modelscope.cn",
  MS_IMAGE_MODEL: process.env.MS_IMAGE_MODEL || "Tongyi-MAI/Z-Image-Turbo",
  ZIMAGE_OUTPUT_DIR: process.env.ZIMAGE_OUTPUT_DIR || "output",
  ZIMAGE_DRY_RUN: process.env.ZIMAGE_DRY_RUN || "false"
};

console.log("Installing MCP server dependencies...");
execSync("npm install", { cwd: SERVER_DIR, stdio: "inherit" });

const envText = Object.entries(env)
  .map(([key, value]) => `${key}=${String(value).replace(/\r?\n/g, "")}`)
  .join("\n") + "\n";
fs.writeFileSync(ENV_PATH, envText, "utf8");
console.log(`Wrote ${ENV_PATH}`);

let configured = 0;

function mergeJson(filePath, updater) {
  let cfg = {};
  if (fs.existsSync(filePath)) {
    try { cfg = JSON.parse(fs.readFileSync(filePath, "utf8")); } catch {}
  }
  updater(cfg);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(cfg, null, 2), "utf8");
}

function tryFirst(paths, label, updater) {
  for (const p of paths) {
    const dir = path.dirname(p);
    if (!fs.existsSync(dir)) continue;
    mergeJson(p, updater);
    console.log(`${label} configured: ${p}`);
    configured++;
    return true;
  }
  return false;
}

const stdEntry = { command: "node", args: [SERVER_PATH], env };

function vscodeStorageUpdater(storageKey) {
  return (cfg) => {
    let servers = {};
    try { servers = JSON.parse(cfg[storageKey] ?? "{}"); } catch {}
    servers[MCP_NAME] = stdEntry;
    cfg[storageKey] = JSON.stringify(servers);
  };
}

tryFirst(
  [path.join(home, ".claude", "claude_desktop_config.json")],
  "Claude Code",
  (cfg) => { cfg.mcpServers ??= {}; cfg.mcpServers[MCP_NAME] = stdEntry; }
);

tryFirst(
  [path.join(home, ".kiro", "mcp.json")],
  "Kiro",
  (cfg) => { cfg.mcpServers ??= {}; cfg.mcpServers[MCP_NAME] = stdEntry; }
);

tryFirst(
  [
    path.join(home, "AppData", "Roaming", "Cursor", "User", "globalStorage", "storage.json"),
    path.join(home, "Library", "Application Support", "Cursor", "User", "globalStorage", "storage.json"),
    path.join(home, ".config", "Cursor", "User", "globalStorage", "storage.json")
  ],
  "Cursor",
  vscodeStorageUpdater("cursor.mcp.servers")
);

tryFirst(
  [
    path.join(home, "AppData", "Roaming", "Windsurf", "User", "globalStorage", "storage.json"),
    path.join(home, "Library", "Application Support", "Windsurf", "User", "globalStorage", "storage.json"),
    path.join(home, ".config", "Windsurf", "User", "globalStorage", "storage.json")
  ],
  "Windsurf",
  vscodeStorageUpdater("cursor.mcp.servers")
);

tryFirst(
  [path.join(home, ".continue", "config.json")],
  "Continue",
  (cfg) => { cfg.mcpServers ??= {}; cfg.mcpServers[MCP_NAME] = stdEntry; }
);

console.log(configured > 0
  ? `Done. Configured ${configured} client(s). Restart your agent.`
  : `No supported agent config found. Add manually: node "${SERVER_PATH}" with MS_API_KEY in env.`
);
