---
name: nook-h3
description: "Generate, monitor, quality-check, and retry MiniMax H3 video clips through a local ComfyUI API. Use when a storyboard or task manifest must be converted into I2VA, FL2VA, L2VA, Ref2VA, or T2VA clips with official prompt structure, explicit references, sequential polling, semantic output review, failure-specific retries, and resumable batching for any number of tasks."
---

# nook-h3

Use this skill when a local storyboard needs to become MiniMax H3 clips through ComfyUI. The skill is an orchestration layer: it does not contain ComfyUI, model weights, private assets, or credentials.

The number of clips is data, not code. Put 3, 7, 100, or any other number of tasks in a manifest and use the same batch runner. A final edited video can contain many tasks; the runner treats each generated clip as one task and does not need to know the final edit length.

## Read before operating

1. Read the installed official `h3-prompt-writing` skill and its mode-specific references.
2. Read [h3-prompt-contract.md](references/h3-prompt-contract.md) for the compact local contract.
3. Read [workflow-and-assets.md](references/workflow-and-assets.md) for workflow configuration and node mapping.
4. Read [manifest-schema.md](references/manifest-schema.md) when creating or reviewing a batch manifest.
5. Read [quality-control.md](references/quality-control.md) before declaring any generated clip complete or starting an unattended batch.

Do not hard-code a user's drive letter, project title, storyboard filename, asset names, or task count into this skill.

## Select the generation mode

- `I2VA`: a supplied still is the concrete first frame.
- `FL2VA`: supplied stills define both the first and last frame.
- `Ref2VA`: character, scene, prop, or relationship images guide generation but are not required to be literal frames.
- `T2VA`: the storyboard explicitly has no usable image reference.
- `L2VA`: a supplied still is the target last frame and the opening is inferred by the model; use a workflow template that exposes a last-frame input.

Use the mode stated by the storyboard or manifest. Do not replace a required reference image with a generated predecessor. If a character identity must stay consistent, always use the designated original identity sheet.

## Prompt and task rules

- Follow the official prompt field names and order for the selected mode.
- Keep structural prompt text in English unless the official skill says otherwise. Preserve user-provided dialogue and visible text exactly in its original language.
- Use stable speaker IDs throughout a project. Put speech in the timeline and keep `overall_soundscape` for environmental sound and Foley.
- Describe duration, aspect ratio, camera behavior, subject movement, scene movement, soundscape, and non-diegetic music explicitly.
- Walking shots need natural, audible footsteps. Busy locations need their local ambience. Keep BGM separate when it will be edited later by setting non-diegetic music to `N/A`.
- If the story is celestial, describe moving mist/cloud layers with depth and continuity in every applicable task; say what they must not obscure.
- Keep each task as one continuous clip unless the selected workflow and storyboard explicitly require a different structure.
- Run `scripts/test_h3_prompt.ps1` directly for one-off preflight checks. Both submission scripts invoke it automatically before touching the ComfyUI queue. For a single task, pass `-ExpectedDialogue`, `-CalmCloudSea`, and `-OpeningSubjectRequired` when applicable; batch tasks use the equivalent optional `prompt_checks` gates.

## Single task

Use `scripts/submit_h3_workflow.ps1` after resolving the workspace, workflow JSON, input aliases, endpoint, duration, megapixels, and prompt. Pass the workflow explicitly when sharing the skill between machines:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\submit_h3_workflow.ps1 `
  -Mode Ref2VA `
  -Workspace '.\video-project' `
  -WorkflowPath '.\video-project\workflow-ref2va.json' `
  -Prompt $prompt `
  -ReferenceImages @('hero_multiview.png','scene01.png') `
  -OutputPrefix 'video/clip-001' `
  -Megapixels 0.9 -Duration 4 -Wait
```

The helper submits UTF-8 JSON and can poll one prompt to inference completion. Inference success is not content approval: inspect the actual output under [quality-control.md](references/quality-control.md) before marking the clip complete or submitting the next clip.

After inference, run `scripts/prepare_h3_qc.py` to extract a contact sheet, standard WAV audio, and technical report. For a dialogue shot, run `scripts/check_h3_dialogue.ps1` with the exact expected line. Then perform the remaining semantic checks in [quality-control.md](references/quality-control.md). These reports are evidence, not automatic semantic approval.

## Batch task

Use `scripts/run_h3_batch.ps1` with a manifest. It submits exactly one task, polls `/history/{prompt_id}` until inference success, records the attempt as `awaiting_qc`, and pauses before any next submission. Treat `awaiting_qc` as unfinished. Review the output against the shot card and [quality-control.md](references/quality-control.md), then use `scripts/set_h3_qc_result.ps1` to record `pass`, `retry`, `rework`, or `manual`. Only a passed clip belongs in `completed`. On failure, use a new seed and a failure-specific prompt revision. Move a clip that reaches its immediate retry limit into `rework_pending`, continue the first-pass queue, and revisit rework items after the remaining shots so one difficult clip cannot block a long batch.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_h3_batch.ps1 `
  -ManifestPath '.\h3_tasks.json'
```

The manifest array is the only place that determines the batch size. To create 3, 7, or 100 clips, add that many task objects; no script change is required. For several finished videos, either use one manifest per video or put all clips in one manifest with a `video_id` metadata field and unique output prefixes. Every task should have a unique `id`, explicit `mode`, official prompt, output prefix, and the references required by its mode.

Before a long unattended batch, verify ComfyUI is reachable, the selected workflow templates exist, all input aliases are available to ComfyUI, the GPU can sustain the run, and the computer will not sleep. Never launch two runners against the same queue unless the user explicitly wants concurrent scheduling.

Transient submission, capacity, network, and inference failures are recorded per attempt and retried with a new seed using exponential backoff. Configure `retry_backoff_seconds`, `retry_backoff_max_seconds`, and `max_retries` in the manifest. Reaching the retry limit moves the task to `rework_pending`; it must not be marked complete.

Treat the storyboard or manifest as the production source of truth. Do not run a project-specific legacy script merely because it exists beside the storyboard. Before submission, compare the task ID, mode, duration, opening composition, reference aliases, and output prefix against the current shot card.

## Sharing with another person

Share the entire `nook-h3` folder, not only `SKILL.md`. The recipient should:

1. Place the folder in a skill directory supported by their Codex setup, such as `~/.codex/skills/` or a project-local `.agents/skills/` directory.
2. Install or otherwise make available the official `h3-prompt-writing` skill.
3. Start ComfyUI with the MiniMax H3 custom nodes and load their own workflow JSON files.
4. Copy their own input images into ComfyUI's input directory and use the aliases visible to their installation.
5. Copy [manifest-schema.md](references/manifest-schema.md), create a private `h3_tasks.json`, adjust the endpoint/workflow paths, and run `run_h3_batch.ps1`.
6. Keep the generated state and logs local. Do not share private absolute paths, model files, API keys, or personal assets unless intended.

This skill is reusable across projects because the project-specific data lives in the manifest, workflow files, and input assets supplied by the person running it.
