# H3 batch manifest

The manifest is the reusable interface between a storyboard and the batch runner. The `tasks` array controls the batch size. Three tasks, seven tasks, and one hundred tasks use the same schema and the same command.

## Required task fields

| Field | Meaning |
|---|---|
| `id` | Unique stable task ID used in logs and resume state. |
| `mode` | `I2VA`, `FL2VA`, `L2VA`, `Ref2VA`, or `T2VA`. |
| `prompt` | The official H3 prompt structure for this task. |
| `output_prefix` | ASCII-safe SaveVideo prefix, unique within the batch. |

Optional organization fields such as `video_id`, `scene_id`, and `sequence` can identify which final video and edit position a clip belongs to. They do not change the generation logic; ordering is the order of the `tasks` array.

Mode-specific fields:

- `I2VA`: `first_frame`
- `FL2VA`: `first_frame` and `last_frame`
- `Ref2VA`: `references`, with at least two ComfyUI input aliases
- `T2VA`: no image field
- `L2VA`: `last_frame` and a workflow template with a last-frame input

## Optional defaults and overrides

Put common values under `defaults`. A task can override `comfy_url`, workflow paths, `megapixels`, `duration`, `poll_seconds`, and `max_retries`.

Use `seed` to set the first attempt seed. Each retry increments it so the same failed sample is not reproduced. If omitted, the runner creates a seed and records it.

Use the optional `prompt_checks` object to turn shot-specific requirements into submission gates: `expected_dialogue` requires the exact `<d>[Chinese] ...</d>` line and direct speaker binding; `calm_cloud_sea: true` rejects disaster-wave language and requires stable cloud height plus subtle lateral internal drift; `opening_subject_required: true` rejects off-screen entrance wording. The runner always validates the official field order and `non_diegetic_music: N/A` before submission.

Inference output is not final approval. The state file uses `attempts`, `awaiting_qc`, `rework_pending`, and `completed`. Only a clip that passes technical and semantic review belongs in `completed`. Store failure reasons and the failure-specific prompt revision before retrying a semantic failure. The runner pauses while any task is in `awaiting_qc`. Record the decision with `scripts/set_h3_qc_result.ps1`. For a semantic retry, pass the manifest path and the complete revised official prompt so the task prompt is updated before resubmission. The retry increments the attempt number and seed and writes to a new attempt-specific output prefix, so the rejected file cannot be mistaken for the new result.

```json
{
  "defaults": {
    "comfy_url": "http://127.0.0.1:8188",
    "workspace": ".",
    "i2v_workflow": "workflow-i2v.json",
    "l2v_workflow": "workflow-l2va.json",
    "ref2v_workflow": "workflow-ref2va.json",
    "t2v_workflow": "workflow-t2va.json",
    "megapixels": 0.9,
    "duration": 4,
    "poll_seconds": 30,
    "max_retries": 3,
    "output_dir": ""
  },
  "tasks": [
    {
      "id": "clip-001",
      "mode": "I2VA",
      "prompt": "integrated_multimodal_description: ...\noverall_soundscape: ...\nnon_diegetic_music: N/A",
      "first_frame": "first_frame_001.png",
      "prompt_checks": {
        "calm_cloud_sea": true,
        "opening_subject_required": true
      },
      "output_prefix": "video/clip-001"
    },
    {
      "id": "clip-002",
      "mode": "Ref2VA",
      "prompt": "subject_definitions: ...\nsummary: ...\nretention_analysis: ...\ndetailed_description: ...\noverall_soundscape: ...\nnon_diegetic_music: N/A",
      "references": ["character_sheet.png", "scene_002.png"],
      "output_prefix": "video/clip-002",
      "duration": 5
    }
  ]
}
```

The manifest can contain any number of task objects. Keep it project-local because it contains private asset aliases and prompts. Share the skill folder separately; share a manifest only when its prompts and assets are intended for the recipient.
