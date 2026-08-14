# H3 workflow and asset contract

This reference describes configuration, not a particular project. Paths and aliases must come from the runner's manifest or command line.

## Endpoint and paths

- Default ComfyUI endpoint: `http://127.0.0.1:8188`
- `workspace`: the directory containing the task manifest, workflow files, or project-specific configuration.
- `i2v_workflow`, `l2v_workflow`, `ref2v_workflow`, and `t2v_workflow`: explicit JSON paths in `defaults` or on the individual task. Relative paths may be resolved from the manifest directory or workspace.
- `first_frame`, `last_frame`, and `references`: ComfyUI input aliases, not private absolute filesystem paths. The image files must already be visible to the ComfyUI installation.
- `output_prefix`: an ASCII-safe SaveVideo prefix such as `video/clip-001`; it is not a local absolute path.

The runner never assumes a user's input or output directory. If output-based resume is needed, set an optional `output_dir` in the manifest defaults. Otherwise the state file is the source of truth.

## Standard node mapping

The bundled examples use the usual MiniMax H3 templates. Node IDs belong to the workflow JSON, not to H3 itself. Verify them in the actual template and override them with `defaults.node_map` or a task-level `node_map` if a template changes.

Typical I2VA/FL2VA mapping:

```text
first_frame    114
resolution     115
duration       105:111
video_node     105:104
save_video     92
```

Typical Ref2VA mapping:

```text
reference_1    137
reference_2    139
extra_refs    140, 141, ...
video_node     136
prompt         138
duration       132
resolution     115
save_video     92
```

Typical T2VA templates use the text/video node, duration node, resolution node, and SaveVideo node from their own JSON. Do not copy I2VA frame nodes into a T2VA template.

L2VA needs a compatible video node with a `last_frame` input. Supply `last_frame` in the task and configure `l2v_workflow` when the installation has a dedicated L2VA template.

## Reference discipline

- A first-frame image is a literal temporal anchor for I2VA/FL2VA.
- A Ref2VA image is a visual guide; list each reference in the task in the intended order.
- Use an original identity sheet for a recurring character. Do not use a previous generated clip as a hidden identity source unless the storyboard explicitly requests it.
- Keep scene-only images scene-only. Put character references in the task's `references` array when the model needs them.
- Prefer explicit, stable aliases over paths that only exist on the sender's computer.

## Configuration example

```json
{
  "defaults": {
    "comfy_url": "http://127.0.0.1:8188",
    "workspace": ".",
    "i2v_workflow": "workflow-i2v.json",
    "ref2v_workflow": "workflow-ref2va.json",
    "t2v_workflow": "workflow-t2va.json",
    "megapixels": 0.9,
    "duration": 4,
    "poll_seconds": 30,
    "max_retries": 3
  },
  "tasks": [
    {
      "id": "clip-001",
      "mode": "I2VA",
      "prompt": "officially structured prompt",
      "first_frame": "first_frame_001.png",
      "output_prefix": "video/clip-001"
    }
  ]
}
```
