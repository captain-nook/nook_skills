# Remotion Handoff

Version: v0.2

Use this reference when the user wants a nook-card output to become a dynamic video. Do not create a video before the card asset direction is approved.

Motion presets are maintained in `references/motion-registry.md`. Each video task should choose one `motion_id` and then describe concrete requirements for that task.

Default video canvas is landscape `1920 x 1080`. Portrait `1080 x 1920` is available when the user asks for vertical video.

Video canvas and card asset ratio are separate. A landscape video may use portrait cards, square cards, or compact landscape cards. Confirm this before rendering final card assets.

Default primary delivery is MOV with alpha for editing software:

```text
format: mov
codec: ProRes 4444
alpha: yes
```

WebM with alpha may be generated as a preview or browser-friendly extra, but it is not the primary editing deliverable.

## Required Handoff Files

- `card-spec.json`: static card content, hierarchy, layout, assets, and style ID.
- `transparent_asset`: card-only PNG/SVG/HTML render with transparent outer background.
- `preview_composite`: optional human-review image with a temporary full-canvas background.
- `remotion-handoff.json`: composition size, scenes, duration, animation intent, voiceover, subtitles, and sound notes.
- `video.mov`: primary editing output.
- `preview-frame.png`: still preview.
- Optional `video.webm`: browser preview with alpha.

## Scene Model

Each scene should include:

| Field | Meaning |
| --- | --- |
| `scene_id` | Stable scene identifier |
| `image_asset` | Transparent card asset path preferred |
| `preview_asset` | Optional preview composite path for review only |
| `card_asset_ratio` | Card's own ratio, independent from stage canvas |
| `duration` | Scene duration in seconds |
| `animation` | Motion intent, such as slide-in, hard pop, cursor click, or button press |
| `voiceover` | Optional narration text |
| `subtitle` | Optional subtitle text |
| `music_sfx` | Optional sound notes |
| `delivery` | Primary format and optional preview format |

## Motion Principles

- Preserve the static card's hard-shadow tactile style.
- Use `transparent_asset` for motion composition. Do not animate preview backgrounds unless they are explicitly part of the scene.
- Keep each card as an independent layer so Remotion can arrange, stack, orbit, reveal, or sequence cards freely.
- When narration exists, set duration from the voiceover rhythm instead of using a fixed default.
- Prefer crisp positional motion, scale pops, cursor interactions, and button press states.
- Avoid over-soft blur transitions that weaken the hard-edged card identity.
- Keep text readable throughout motion; do not animate dense text too aggressively.
- Never leave the hold phase absolutely still. Use subtle breathing, tiny shake, shadow drift, path flow, chart pulse, or mild camera movement.
- Perspective/camera motion is allowed when useful, but keep it mild enough that the video remains usable as an editing overlay.

## Delivery Model

Recommended `outputs` block:

```json
{
  "outputs": {
    "primary": "video.mov",
    "preview": "video.webm",
    "preview_frame": "preview-frame.png",
    "card_assets": ["../cards/<slug>/transparent/card-01.png"],
    "review_assets": ["../cards/<slug>/preview/card-01.png"]
  },
  "delivery": {
    "primary_format": "mov",
    "primary_codec": "prores_4444",
    "alpha_required": true,
    "editing_software": ["Premiere Pro", "Final Cut Pro", "DaVinci Resolve"]
  }
}
```
