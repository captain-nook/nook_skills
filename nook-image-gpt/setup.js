#!/usr/bin/env node
/**
 * nook-image-gpt 一键部署脚本
 * 用法：node setup.js sk-YOUR_API_KEY [https://custom-relay-base-url]
 */

import { execSync } from "child_process";
import fs from "fs";
import path from "path";
import os from "os";

const SERVER_PATH = path.resolve(import.meta.dirname, "server", "index.js");
const MCP_NAME = "nook-image-gpt";
const home = os.homedir();

// ── API key ──────────────────────────────────────────────────────────────────
const apiKey = process.argv[2] || process.env.IMAGE_API_KEY;
if (!apiKey || !apiKey.startsWith("sk-")) {
  console.error("Usage: node setup.js sk-YOUR_API_KEY");
  console.error("Get your key: https://sub.jarodfund.xyz/key-usage");
  process.exit(1);
}
const apiBase = process.argv[3] || null;
const env = { IMAGE_API_KEY: apiKey, ...(apiBase ? { IMAGE_API_BASE: apiBase } : {}) };

// ── npm install ──────────────────────────────────────────────────────────────
console.log("📦 Installing dependencies...");
execSync("npm install", { cwd: path.join(import.meta.dirname, "server"), stdio: "inherit" });

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
