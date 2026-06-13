# Global Production Rules

Version: v0.2  
Updated: 2026-05-21  
Purpose: define global defaults that apply to all nook-card static cards and videos unless the user overrides them.

## Output Folders

All generated assets must stay under the current workspace:

```text
outputs/
```

Folder rules:

```text
outputs/cards/<slug>/
outputs/videos/<slug>/
```

## Default Stage Canvas

Default video/stage canvas is horizontal:

```json
{
  "width": 1920,
  "height": 1080,
  "aspect_ratio": "16:9",
  "orientation": "landscape"
}
```

At the start of each `nook-card` task, Codex should treat landscape as the default stage, but explicitly keep portrait as an available option.

Stage canvas and card asset ratio are separate decisions. A landscape `1920 x 1080` video may use portrait card assets, square card assets, or mixed cards depending on the motion preset and layout.

Supported common options:

| Option | Size | Use |
| --- | --- | --- |
| `landscape` | `1920 x 1080` | default, presentations, video overlays, desktop layouts |
| `portrait` | `1080 x 1920` | vertical video, mobile social platforms |
| `square` | `1080 x 1080` | social feed posts |
| `custom` | user specified | special cases |

## Static Card Defaults

- Default style: `tactile_soft_skeuomorphic_card`.
- Default production intent: ask first; do not silently assume static-only or motion-ready.
- Default stage canvas when needed: landscape `1920 x 1080`.
- Default card asset ratio: choose from content and likely motion layout; do not assume it equals the stage canvas.
- Multi-card landscape videos often prefer portrait or compact card assets so cards can be arranged, stacked, or animated.
- Default output folder: `outputs/cards/<slug>/`.
- Required output: `card-spec.json`.
- Motion-ready primary output: `transparent_asset` with transparent outer background.
- Human-review output: `preview_composite` with temporary preview background.
- Preferred preview output: `index.html`.
- Optional still outputs: `card.svg`, `card.png`.

## Output Layer Model

Static outputs must distinguish between card assets and preview composites:

| Output layer | Meaning | Background rule |
| --- | --- | --- |
| `transparent_asset` | Card-only asset for Remotion, PR, FCP, DaVinci, or later layout composition | Outer canvas is transparent; only the card, its own shadow, internal materials, and attached decorative elements remain |
| `preview_composite` | Human-review render for checking style and readability | May include a full-canvas background, gradient, scene, or stage preview |
| `source_editable` | Optional OpenDesign/HTML source | Should preserve layer separation |

If a task may enter motion, generate `transparent_asset` first and `preview_composite` second. Do not bake preview backgrounds into motion-ready assets.

Style-specific note:

- Glassmorphism may need a background to show the material. Keep the outer asset transparent and put any background used to demonstrate blur in `preview_composite` or the Remotion scene layer.
- Pop art, tactile, and hand-journal styles may include internal card texture, stickers, shadows, or attached shapes, but should not include a full-stage background in `transparent_asset`.

## Video Defaults

- Default motion preset: `pop_breathe`.
- Default orientation: landscape `1920 x 1080`.
- Default fps: `30`.
- Default duration: voiceover-driven when narration exists; otherwise use the selected motion preset default.
- Default background: transparent.
- Default primary output: MOV with alpha.
- Default primary codec: ProRes 4444.
- Default pixel format: `yuva444p10le` when available.
- Default image format: `png`.
- Optional preview output: WebM with alpha (`vp8 + yuva420p`).
- Default output folder: `outputs/videos/<slug>/`.
- Required output: `remotion-handoff.json`.
- Hold behavior: never fully static; keep subtle breathing, micro drift, shadow shift, or perspective/camera motion.
- Camera/perspective motion: optional, mild, and only when it helps depth or sequence clarity.

## Video Delivery Priority

Primary delivery for editing software:

```text
video.mov
codec: ProRes 4444
alpha: yes
```

Optional browser preview:

```text
video.webm
codec: VP8
pixel format: yuva420p
alpha: yes
```

## Interaction Rule

Even with defaults, Codex must first ask production-intent and static-card requirements when `nook-card` is triggered. The user should answer via step-by-step choices:

1. Static-only or motion-ready?
2. Stage canvas if motion is possible?
3. Which card style?
4. Concrete card requirements, including card count and split method?
5. Card asset ratio and output layers?

After the static card is accepted, Codex asks whether to enter motion. Only then should Codex ask:

1. Which motion preset?
2. Concrete motion requirements?

If the user says "默认" or "你定", use the defaults above.
