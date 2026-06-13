#!/usr/bin/env node
/**
 * nook-image-gpt 一键部署脚本
 *
 * 用法（agent 执行）：
 *   node setup.js sk-你的key
 *   IMAGE_API_KEY=sk-你的key node setup.js
 */

import { execSync } from "child_process";
import fs from "fs";
import path from "path";
import os from "os";

const SERVER_PATH = path.resolve(import.meta.dirname, "server", "index.js");
const MCP_NAME = "nook-image-gpt";
const home = os.homedir();

// ── 1. Get API key ───────────────────────────────────────────────────────────
const apiKey = process.argv[2] || process.env.IMAGE_API_KEY;
if (!apiKey || !apiKey.startsWith("sk-")) {
  console.error("Usage: node setup.js sk-YOUR_API_KEY");
  console.error("Get your key at: https://sub.jarodfund.xyz/key-usage");
  process.exit(1);
}

// ── 2. npm install ───────────────────────────────────────────────────────────
console.log("📦 Installing dependencies...");
execSync("npm install", {
  cwd: path.join(import.meta.dirname, "server"),
  stdio: "inherit",
});

// ── 3. Configure clients ─────────────────────────────────────────────────────
let configured = 0;

function mergeJson(filePath, updater) {
  let cfg = {};
  if (fs.existsSync(filePath)) cfg = JSON.parse(fs.readFileSync(filePath, "utf8"));
  updater(cfg);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(cfg, null, 2));
}

// opencode
const opencodePaths = [
  path.join(home, ".config", "opencode", "opencode.json"),
  path.join(home, "AppData", "Roaming", "opencode", "opencode.json"),
];
for (const p of opencodePaths) {
  if (!fs.existsSync(p)) continue;
  mergeJson(p, (cfg) => {
    cfg.mcp ??= {};
    cfg.mcp[MCP_NAME] = {
      type: "local",
      command: ["node", SERVER_PATH],
      enabled: true,
      environment: { IMAGE_API_KEY: apiKey },
    };
  });
  console.log(`✅ opencode → ${p}`);
  configured++;
  break;
}

// Claude Code / Kiro — user-level mcp.json
const claudePath = path.join(home, ".claude", "mcp.json");
if (fs.existsSync(path.join(home, ".claude"))) {
  mergeJson(claudePath, (cfg) => {
    cfg.mcpServers ??= {};
    cfg.mcpServers[MCP_NAME] = {
      command: "node",
      args: [SERVER_PATH],
      env: { IMAGE_API_KEY: apiKey },
    };
  });
  console.log(`✅ Claude Code / Kiro → ${claudePath}`);
  configured++;
}

// Cursor
const cursorPaths = [
  path.join(home, "AppData", "Roaming", "Cursor", "User", "globalStorage", "storage.json"),
  path.join(home, ".config", "Cursor", "User", "globalStorage", "storage.json"),
];
for (const p of cursorPaths) {
  if (!fs.existsSync(p)) continue;
  mergeJson(p, (cfg) => {
    let servers = {};
    try { servers = JSON.parse(cfg["cursor.mcp.servers"] ?? "{}"); } catch {}
    servers[MCP_NAME] = {
      command: "node",
      args: [SERVER_PATH],
      env: { IMAGE_API_KEY: apiKey },
    };
    cfg["cursor.mcp.servers"] = JSON.stringify(servers);
  });
  console.log(`✅ Cursor → ${p}`);
  configured++;
  break;
}

// ── 4. Result ────────────────────────────────────────────────────────────────
if (configured === 0) {
  console.warn("\n⚠️  No agent config found. Manual setup:");
  console.warn(`   MCP server name: ${MCP_NAME}`);
  console.warn(`   command: node "${SERVER_PATH}"`);
  console.warn(`   env: IMAGE_API_KEY=${apiKey}`);
} else {
  console.log(`\n🎉 Done! Configured ${configured} client(s). Restart your agent.`);
}
