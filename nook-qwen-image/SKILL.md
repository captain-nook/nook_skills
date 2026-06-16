---
name: nook-qwen-image
description: Atomic high-quality text-to-image skill backed by ModelScope Qwen-Image. Use when Codex needs Chinese poster, cover, editorial image, typography-heavy visual material, or higher-quality Chinese/English text rendering through a paid ModelScope image channel; use nook-zimage for cheap fast drafts, batch tests, and low-stakes background exploration.
---

# nook-qwen-image

High-quality text-to-image provider using ModelScope `Qwen/Qwen-Image`.

Use this as an atomic image provider. It generates local image files from prompts; it does not design final layouts, place deterministic typography, or package finished poster files.

## Quick Deploy (one-shot, for AI agents)

If a user just gave you this repo URL and said "deploy" / "install" / "set it up" / "部署":

1. Clone to a stable path (not a temp folder — the MCP config records the absolute path).
   ```bash
   git clone https://github.com/captain-nook/nook_skills.git
   cd nook_skills/nook-qwen-image
   ```
2. Run `node setup.js`. It will ask for the user's `MS_API_KEY` (ModelScope SDK token). If you (the agent) have no TTY, pass it via env or argv: `MS_API_KEY=xxx node setup.js`.
3. Setup auto-detects Trae IDE / Codex CLI / Claude Code / Cursor / Windsurf / Kiro / Continue and writes the MCP config. If your client is missing, see `references/agent-deployment.md`.
4. Restart the user's agent and probe with "给我出一张测试图 512x512".

Uninstall: `node setup.js --remove`.

## Setup (manual)

From this skill folder:

```bash
node setup.js
```

Optional flags:

```bash
node setup.js <ms_api_key>           # skip the prompt
node setup.js --agent codex          # only write Codex CLI config
node setup.js --agent trae           # only write Trae IDE config
node setup.js --remove               # remove MCP entry + delete .env
```

Setup writes local `.env`, installs MCP dependencies, and attempts to add the MCP server to every supported agent config.

If a single client needs manual registration, the path table is in `references/agent-deployment.md`.

## Provider Selection Heuristic

When the user gives a natural-language image request, route by intent:

| User says | Use | Why |
|---|---|---|
| "生一个美女" / "出图" / "测试" / "草图" / "draft" / "背景" / "explore" / "mood" / "cheap" / "练手" | `nook-zimage` | Cheap/fast Z-Image-Turbo |
| "小红书封面" / "公众号头图" / "海报" / "标题图" / "中文" / "高质量" / "印刷" / "typography" / "editorial" / "印刷品" | `nook-qwen-image` | High-quality Qwen-Image with strong Chinese typography |
| "改图" / "换背景" / "image to image" / "edit" | `nook-image2-gpt` (separate project) | Image-to-image editing |

**Default if unclear** → `nook-zimage` (cheaper, faster). The user can always re-render with the other model.

## MCP Usage

MCP server name: `nook-qwen-image`

Tools:

- `submit_qwen_image_task(prompt, size?, n?, output_path?)`
- `get_qwen_image_result(task_id)`

Standard flow:

```text
1. submit_qwen_image_task(prompt, size, n, output_path?)
2. Poll get_qwen_image_result(task_id) every 5-10 seconds
3. When status = succeeded, use image_path (or image_paths[0]) and render it inline
```

If the user named a path (e.g. "存到 D:\\images\\cat.jpg", "save to my Desktop"), pass it as `output_path`. Otherwise the file lands in `<project>/output/`.

## Output Handling

The MCP tools return JSON like:

```json
{
  "task_id": "qwen_img_20260615_142301_a1b2c3d4",
  "status": "succeeded",
  "image_path": "C:\\nook-skills\\nook-qwen-image\\output\\qwen_img_...jpg",
  "image_paths": ["..."],
  "output_path": null
}
```

**Always display the generated image** to the user inline so they can see it. Use a `file:///` absolute URL on Windows; on macOS/Linux a plain absolute path also works:

```markdown
![generated image](file:///C:/nook-skills/nook-qwen-image/output/qwen_img_20260615_142301_a1b2c3d4.jpg)
```

If the user did not specify a path, use the default `output/` directory and present the result inline. If the user named a path, the file already lives at that path; mention the absolute path in plain text (no need for Markdown image tag if the user only asked to "save to disk").

## CLI Usage

Use CLI when MCP tools are not available:

```bash
python scripts/generate.py "Chinese editorial poster cover, clean composition, premium magazine style" --size 1080x1440
```

The script prints `OUTPUT_PATH=<absolute path>` on success.

## Share Server

Use the share server when a trusted colleague or friend needs a simple browser UI.

```bash
python scripts/share_server.py --host 127.0.0.1 --port 7861 --token <shared-token>
```

For LAN or tunnel sharing, bind intentionally:

```bash
python scripts/share_server.py --host 0.0.0.0 --port 7861 --token <shared-token>
```

Keep `MS_API_KEY` on the server side. Do not put the ModelScope key in a browser, static page, or client-side script. Use a token when binding beyond localhost.

## Xiaohongshu Cover Rendering

Use Qwen-Image for the background, then render exact Chinese title text with:

```bash
python scripts/render_xhs_cover.py --background output/bg.jpg --output output/cover.jpg --title 魔搭社区免费出图 --subtitle Qwen-image
```

## Sizes

Accepted size formats:

- `1024x1024`
- `1024*1024`
- `720x1280`
- `1080x1440`
- `1440x1080`
- `1280x720`

See `references/size-reference.md` for recommendations.

## Integration Rule

Upper-layer skills such as `nook-poster` should:

- create art-directed prompts for Qwen-Image;
- call this provider for high-quality image material;
- save the output path in their own asset records;
- place final text, layout, QR codes, and deterministic typography in their own renderer unless intentional image-baked text is required.

For Chinese title or poster concepts, Qwen-Image may be asked to render short Chinese text inside the image, but final publishable typography should still be checked visually.
