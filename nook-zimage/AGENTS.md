# AGENTS.md — Deployment Guide for AI Agents

> Auto-loaded by Claude Code, Codex CLI, Trae IDE, Cursor, Continue, Windsurf, and other MCP-aware agents.
> When a user gives you this repository URL and says "deploy this", "set it up", "install", or similar, follow the steps below.

## What this skill is

This is a **ModelScope text-to-image MCP server** for AI agents.

- **Provider**: ModelScope (`api-inference.modelscope.cn`) via `MS_API_KEY`
- **Tools exposed**: `submit_<name>_task`, `get_<name>_result`
- **Output**: Local image files written to the configured `output/` directory

Read `SKILL.md` for capability details, `references/integration-contract.md` for how upper-layer skills should call this provider, and `references/agent-deployment.md` for full deployment and troubleshooting.

## One-time deployment procedure

When the user says "deploy" / "install" / "set up" this project, do **in order**:

### 1. Clone the repository to a stable path

```bash
git clone https://github.com/captain-nook/nook_skills.git
cd nook_skills/<this-folder>
```

> ⚠️ Clone to a stable location (e.g. `~/nook-skills/<folder>`), **not** a temp folder. The MCP config records the absolute path, so if the folder moves, every agent will break.

### 2. Run `setup.js` and collect the API key

```bash
node setup.js
```

`setup.js` will:
1. Ask the user for `MS_API_KEY` (their ModelScope SDK token)
2. Write the key to `<project>/.env` (kept local, not committed)
3. Run `npm install` inside `server/`
4. Auto-detect the user's AI client and register the MCP server

If you are running non-interactively (e.g. you are an agent that cannot read user input), accept the key from env or argv:

```bash
MS_API_KEY=<key> node setup.js
# or
node setup.js <key>
```

If a sibling `nook-qwen-image/.env` already has a key, setup reuses it so the user does not have to paste twice.

### 3. Restart the user's AI client

| Client | Restart |
|---|---|
| Trae IDE | Close window and reopen |
| Codex CLI | Re-run `codex` |
| Claude Code | Restart terminal session |
| Cursor / Windsurf | Cmd/Ctrl+Shift+P → "Reload Window" |
| Continue (VS Code) | Reload VS Code |

### 4. Verify by listing MCP tools

Tell the user to send a probe prompt:

> "Use this skill to generate a tiny test image (size 512x512)."

If the agent can see `submit_<name>_task` and `get_<name>_result`, deployment is successful.

If the tools are not visible, see `references/agent-deployment.md` § Troubleshooting.

### 5. Report back to the user

Reply with:

> ✓ Deployment complete. Registered to: **\<agent name\>**.
> Your ModelScope key is stored locally in `.env` (not shared).
> Try: "生一个美女" / "出一张草图" / "生成一张背景图".

## Provider selection rule

When the user gives a natural-language image request, route based on intent:

| User says | Use | Why |
|---|---|---|
| "生一个美女" / "出图" / "测试" / "草图" / "draft" / "背景" / "explore" / "mood" / "cheap" / "mood board" | `nook-zimage` | Cheap/fast Z-Image-Turbo |
| "小红书封面" / "公众号头图" / "海报" / "标题图" / "中文" / "高质量" / "印刷" / "typography" / "editorial" | `nook-qwen-image` | High-quality Qwen-Image with strong Chinese typography |
| "改图" / "换背景" / "image to image" / "edit" | `nook-image2-gpt` (separate project) | Image-to-image editing |

**Default if unclear** → `nook-zimage` (cheaper, faster). The user can always re-render with the other model.

## Output handling

The MCP tools return JSON like:

```json
{
  "task_id": "zimg_20260615_142301_a1b2c3d4",
  "status": "succeeded",
  "image_path": "C:\\nook-skills\\nook-zimage\\output\\zimg_...jpg",
  "image_paths": ["..."]
}
```

**Always display the generated image** to the user using Markdown so they can see it inline:

```markdown
![generated image](file:///C:/nook-skills/nook-zimage/output/zimg_20260615_142301_a1b2c3d4.jpg)
```

(Use `file:///` absolute URL on Windows; on macOS/Linux use plain absolute path.)

**If the user named a path** (e.g. "存到 D:\\images\\cat.jpg", "save to my Desktop"), pass it as `output_path` to the submit tool so the file lands there:

```python
submit_zimage_task(
    prompt="...",
    size="1024x1024",
    output_path="D:\\images\\cat.jpg"
)
```

**If the user did not specify a path**, use the default `output/` directory and present the result inline.

## Error recovery

If `setup.js` does not detect the user's agent:

1. Identify the agent manually (ask if needed).
2. Use the path table in `references/agent-deployment.md` to write the MCP config directly.
3. Restart the agent.

If MCP tools are not visible after restart:

- Confirm the config file is valid JSON (or valid TOML for Codex).
- Confirm the `args` path is **absolute** and points to `server/index.js`.
- Run `node server/index.js` manually to check for startup errors.
- See `references/agent-deployment.md` § Troubleshooting for the full list.

If `MS_API_KEY` is wrong, the user will see HTTP 401 from ModelScope. Tell them to re-run `node setup.js`.

## Security note

`MS_API_KEY` is the user's **personal** ModelScope SDK token. Never log it, never echo it, never commit the `.env` file. The MCP server keeps it server-side only.
