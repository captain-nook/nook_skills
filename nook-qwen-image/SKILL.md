---
name: nook-qwen-image
description: Atomic high-quality text-to-image skill backed by ModelScope Qwen-Image. Use when Codex needs Chinese poster, cover, editorial image, typography-heavy visual material, or higher-quality Chinese/English text rendering through a paid ModelScope image channel; use nook-zimage for cheap fast drafts, batch tests, and low-stakes background exploration.
---

# nook-qwen-image

High-quality text-to-image provider using ModelScope `Qwen/Qwen-Image`.

Use this as an atomic image provider. It generates local image files from prompts; it does not design final layouts, place deterministic typography, or package finished poster files.

## Provider Choice

- Use `nook-qwen-image` for Chinese posters, cover images, title-heavy image material, editorial hero images, and high-quality visual exploration.
- Use `nook-zimage` for cheap fast testing, batch drafts, mood images, and low-stakes background assets.
- Use an image-to-image provider for reference-image fidelity, edits, relighting, product preservation, or multi-image composition.

## Setup

From this skill folder:

```bash
node setup.js
```

Required key:

```text
MS_API_KEY=<your ModelScope API key>
```

The setup writes local `.env`, installs MCP dependencies, and attempts to add the MCP server to supported agent configs.

If Codex global config needs manual registration, add:

```toml
[mcp_servers.nook-qwen-image]
command = 'node'
args = ['I:\nook_vault\82_Skills\nook-skills\skills\nook-qwen-image\server\index.js']
startup_timeout_sec = 120
```

## MCP Usage

MCP server name: `nook-qwen-image`

Tools:

- `submit_qwen_image_task`
- `get_qwen_image_result`

Standard flow:

```text
1. submit_qwen_image_task(prompt, size, n)
2. Poll get_qwen_image_result(task_id)
3. Use image_paths[0] after status = succeeded
```

Recommended polling interval: 5-10 seconds.

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
