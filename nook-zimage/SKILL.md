---
name: nook-zimage
description: Atomic low-cost text-to-image skill backed by ModelScope Z-Image Turbo. Use when Codex needs cheap/free text-to-image generation for drafts, background assets, poster materials, testing, or batch visual exploration; use nook-image2-gpt instead for image-to-image or higher-quality production images.
---

# nook-zimage

Low-cost text-to-image provider using ModelScope `Tongyi-MAI/Z-Image-Turbo`.

Use this as an atomic image provider. It generates local image files from prompts; it does not design posters, write text onto images, or make final cards.

## Provider Choice

- Use `nook-zimage` for draft backgrounds, mood images, batch tests, and low-cost text-to-image.
- Use `nook-image2-gpt` for image-to-image, higher-quality production images, or important final assets.

## Setup

From this skill folder:

```bash
node setup.js
```

The setup writes local `.env`, installs MCP dependencies, and attempts to add the MCP server to supported agent configs.

Required key:

```text
MS_API_KEY=<your ModelScope API key>
```

If Codex global config needs manual registration, add:

```toml
[mcp_servers.nook-zimage]
command = 'node'
args = ['I:\nook_vault\82_Skills\nook-skills\skills\nook-zimage\nook-zimage\server\index.js']
startup_timeout_sec = 120
```

## MCP Usage

MCP server name: `nook-zimage`

Tools:

- `submit_zimage_task`
- `get_zimage_result`

Standard flow:

```text
1. submit_zimage_task(prompt, size, n)
2. Poll get_zimage_result(task_id)
3. Use image_paths[0] after status = succeeded
```

Recommended polling interval: 5-10 seconds.

## CLI Usage

Use CLI when MCP tools are not available:

```bash
python scripts/generate.py "misty mountain lake background, cinematic, no text" --size 1024x1440
```

The script prints `OUTPUT_PATH=<absolute path>` on success.

## Share Server

Use the share server when a trusted colleague or friend needs a simple browser UI for fast draft generation.

```bash
python scripts/share_server.py --host 127.0.0.1 --port 7860 --token <shared-token>
```

For LAN or tunnel sharing, bind intentionally:

```bash
python scripts/share_server.py --host 0.0.0.0 --port 7860 --token <shared-token>
```

Keep `MS_API_KEY` on the server side. Do not put the ModelScope key in a browser, static page, or client-side script. Use a token when binding beyond localhost.

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

- create the prompt;
- call this provider for image material only;
- save the output path in their own asset records;
- place text, layout, and final composition in their own deterministic renderer.

Do not ask Z-Image to generate final posters with Chinese text baked into the image.
