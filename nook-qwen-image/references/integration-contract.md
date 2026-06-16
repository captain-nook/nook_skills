# nook-qwen-image Integration Contract

`nook-qwen-image` is an atomic high-quality text-to-image provider for Chinese poster and cover material.

## Boundary

Upper-layer skills handle:

- art direction and prompt construction;
- asset organization;
- final poster layout and deterministic typography;
- deciding when to use `nook-zimage` for faster cheaper drafts.

`nook-qwen-image` handles:

- submitting a ModelScope Qwen-Image task;
- polling for the result;
- downloading generated images;
- returning local image paths.

## MCP Flow

```text
submit_qwen_image_task
-> get_qwen_image_result until status = succeeded
-> use image_paths[0]
```

Example:

```json
{
  "prompt": "Chinese editorial magazine cover, clean premium composition, large empty title area, cinematic lighting",
  "size": "1080x1440",
  "n": 1
}
```

## Provider Selection

Use `nook-qwen-image` when:

- Chinese poster or cover quality matters;
- Chinese or English text rendering may be part of the image concept;
- the asset is closer to production than a quick draft.

Use `nook-zimage` when:

- the task is a fast test;
- many low-cost variations are needed;
- the output is only background or mood material.

## Required Upstream Record

Upper-layer projects should record:

```yaml
image_provider: nook-qwen-image
task_id:
prompt:
size:
output_images:
purpose:
created:
status:
```
