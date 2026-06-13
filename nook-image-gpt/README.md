# nook-image-gpt

MCP Server for GPT Image 2.0 generation and editing. Exposes `generate_image` and `edit_image` tools that any MCP-compatible agent (opencode, Claude Code, Cursor, Windsurf, etc.) can call.

## How it works

Calls `POST /v1/images/generations` for text-to-image and `POST /v1/images/edits` for image-to-image/editing on an OpenAI-compatible relay API. Returned base64 images are either passed back to the agent or saved as PNG files to a local directory.

## Quick start

```bash
# 1. Install dependencies
cd server && npm install

# 2. Add to your agent's MCP config
#    See SKILL.md for opencode / Claude Code / Cursor examples
```

## Configuration

| Env variable | Required | Default | Description |
|---|---|---|---|
| `IMAGE_API_KEY` | Yes | — | Relay API key |
| `IMAGE_API_BASE` | No | `https://sub.jarodfund.xyz` | Custom relay base URL |

## Tool: `generate_image`

| Parameter | Required | Default | Description |
|---|---|---|---|
| `prompt` | Yes | — | Image description |
| `size` | No | `1024x1024` | Resolution (see references/size-reference.md) |
| `n` | No | 1 | Number of images (max 10) |
| `save_to_dir` | No | — | Save as PNG files to this directory |

## Tool: `edit_image`

| Parameter | Required | Default | Description |
|---|---|---|---|
| `prompt` | Yes | — | Edit instruction or image-to-image prompt |
| `image_path` | No | — | Single source image path |
| `image_paths` | No | — | One or more source image paths |
| `mask_path` | No | — | Optional PNG mask path for targeted edits |
| `size` | No | `1024x1024` | Output resolution |
| `n` | No | 1 | Number of images (max 10) |
| `save_to_dir` | No | — | Save as PNG files to this directory |

Pass at least one of `image_path` or `image_paths`.

## Related

- `SKILL.md` — Full documentation with per-agent config examples
- `references/size-reference.md` — Resolution presets table
- `server/` — MCP Server source code
