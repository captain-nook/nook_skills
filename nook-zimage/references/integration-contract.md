# nook-zimage Integration Contract

`nook-zimage` is an atomic text-to-image provider for cheap drafts and background assets.

## Boundary

Upper-layer skills handle:

- prompt construction;
- art direction;
- output asset organization;
- final layout and typography;
- deciding when to upgrade to `nook-image2-gpt`.

`nook-zimage` handles:

- submitting a ModelScope Z-Image Turbo task;
- polling for the result;
- downloading the image;
- returning local image paths.

## MCP Flow

```text
submit_zimage_task
→ get_zimage_result until status = succeeded
→ use image_paths[0]
```

Example:

```json
{
  "prompt": "misty mountain lake background, editorial photography, no text, no logo",
  "size": "1080x1440",
  "n": 1
}
```

## Provider Selection

Use `nook-zimage` when:

- the task is text-to-image only;
- cost matters;
- the asset is for draft, mood exploration, or poster background testing;
- small visual imperfections are acceptable.

Use `nook-image2-gpt` when:

- image-to-image is required;
- the image is a high-stakes final asset;
- quality matters more than cost;
- reference image fidelity matters.

## Required Upstream Record

Upper-layer projects should record:

```yaml
image_provider: nook-zimage
task_id:
prompt:
size:
output_images:
purpose:
created:
status:
```
