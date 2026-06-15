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
