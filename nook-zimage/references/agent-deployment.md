# Agent Deployment Guide

This file complements `AGENTS.md`. Read both before deploying.

## Path table — where to write MCP config per agent

| Agent | Config file (Windows) | Config file (macOS / Linux) | Format | Field name |
|---|---|---|---|---|
| Claude Code | `%APPDATA%\Claude\claude_desktop_config.json` | `~/Library/Application Support/Claude/claude_desktop_config.json` | JSON | `mcpServers` |
| Kiro | `%USERPROFILE%\.kiro\mcp.json` | `~/.kiro/mcp.json` | JSON | `mcpServers` |
| Cursor | `%APPDATA%\Cursor\User\globalStorage\storage.json` | `~/Library/Application Support/Cursor/User/globalStorage/storage.json` | JSON | `cursor.mcp.servers` (stringified inside `storage.json`) |
| Windsurf | `%APPDATA%\Windsurf\User\globalStorage\storage.json` | `~/Library/Application Support/Windsurf/User/globalStorage/storage.json` | JSON | `cursor.mcp.servers` |
| Continue | `%USERPROFILE%\.continue\config.json` | `~/.continue/config.json` | JSON | `mcpServers` |
| **Trae IDE** | `%APPDATA%\Trae\User\globalStorage\mcp.json` | `~/Library/Application Support/Trae/User/globalStorage/mcp.json` | JSON | `mcpServers` |
| **Codex CLI** | `%USERPROFILE%\.codex\config.toml` | `~/.codex/config.toml` | **TOML** | `[mcp_servers.<name>]` |

## Per-agent config snippets

### Trae IDE (Windows / macOS / Linux)

File: `%APPDATA%\Trae\User\globalStorage\mcp.json`

```json
{
  "mcpServers": {
    "nook-zimage": {
      "command": "node",
      "args": ["C:/nook-skills/nook-zimage/server/index.js"],
      "env": {
        "MS_API_KEY": "REPLACE_AT_RUNTIME"
      }
    }
  }
}
```

> Trae reads `env` from the config file directly. `setup.js` writes the real key in.

### Codex CLI (Windows / macOS / Linux)

File: `~/.codex/config.toml`

```toml
[mcp_servers.nook-zimage]
command = "node"
args = ["C:/nook-skills/nook-zimage/server/index.js"]
env = { MS_API_KEY = "REPLACE_AT_RUNTIME" }
startup_timeout_sec = 120
tool_timeout_sec = 300
```

> Codex is **TOML**, not JSON. Trailing commas are invalid. The `env` table uses `KEY = "value"` syntax (TOML).

> Preferred method: call the Codex CLI directly so it owns the config layout:
>
> ```bash
> codex mcp add nook-zimage -- node "C:/nook-skills/nook-zimage/server/index.js" --env MS_API_KEY=xxx
> ```

### Cursor / Windsurf

`storage.json` already contains UI state. The MCP servers are stored as a **stringified** JSON value under the `cursor.mcp.servers` key:

```json
{
  "cursor.mcp.servers": "{\"nook-zimage\":{\"command\":\"node\",\"args\":[\"C:/nook-skills/nook-zimage/server/index.js\"],\"env\":{\"MS_API_KEY\":\"xxx\"}}}",
  ...
}
```

`setup.js` handles the stringification automatically.

## Troubleshooting

### Tools not visible after restart

1. **Path is wrong**: `args` must be **absolute**. Relative paths break when the agent's working directory differs from the project.
2. **JSON / TOML syntax error**: run the file through a validator (`jq` for JSON, `tomlq` for TOML).
3. **Codex rejected the env block**: Codex expects `env = { KEY = "value" }` (TOML, no JSON-style quotes around keys).
4. **Trae rejected the field name**: Trae uses `mcpServers` (camelCase, capital S), not `mcp_servers`.
5. **Permission denied** on Windows: the `node` binary must be on `PATH` for the agent's user. Test in a regular `cmd` window first.

### `setup.js` did not detect the agent

- Make sure the agent's config directory exists (e.g. `%APPDATA%\Trae\User\globalStorage\`).
- If using a custom path, set the env var `NOOK_SETUP_AGENT_FORCE=claude|codex|trae|cursor|kiro|windsurf|continue` and re-run `node setup.js`.

### `node setup.js` is not interactive (no TTY)

Pass the key directly:

```bash
node setup.js <your_modelscope_key>
# or
MS_API_KEY=<your_modelscope_key> node setup.js
```

### ModelScope returns 401

The `MS_API_KEY` is wrong, expired, or not yet bound to an Alibaba Cloud account. Get a fresh SDK token from <https://modelscope.cn/my/myaccesstoken>.

### ModelScope returns "task not found" or 404

The `baseUrl` may be behind a proxy. Set `MS_API_BASE_URL` in `.env` to your endpoint (default `https://api-inference.modelscope.cn`).

### Image saved but agent cannot display it

Use a `file:///` absolute URL in the Markdown image tag, e.g.

```markdown
![img](file:///C:/nook-skills/nook-zimage/output/zimg_xxx.jpg)
```

## Uninstall

```bash
node setup.js --remove
```

This removes the MCP entry from every detected agent config and deletes `.env`. The repo folder is left untouched.
