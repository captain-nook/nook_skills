# OpenDesign Card Contract

Version: v0.2  
Purpose: define the stable intermediate contract between Codex, OpenDesign, HTML/CSS preview, static exports, and Remotion handoff.  
Scope: specification only. This file does not contain a real user case.

## Contract Role

`card-spec.json` is the source of truth for one generated card. It records:

- the selected style,
- the confirmed copy,
- the confirmed hierarchy,
- the layout slots,
- the component order,
- the render target,
- the production intent and output layer model,
- optional video handoff metadata.

OpenDesign should read `card-spec.json` and render a card from it. Remotion should later read the same spec, plus `remotion-handoff.json`, to animate the approved card.

## Lifecycle Status

| Status | Meaning |
| --- | --- |
| `draft` | Codex is still proposing content or hierarchy |
| `confirmed` | User has approved copy, hierarchy, style, and output constraints |
| `rendered` | OpenDesign or HTML/CSS preview has produced a static render |
| `approved` | User has approved the static card |
| `video_ready` | Static card is ready for Remotion handoff |

Codex must not move from `draft` to `confirmed` unless the user confirms or explicitly delegates decisions.

## Canonical JSON Shape

```json
{
  "schema_version": "0.2",
  "status": "draft",
  "style_id": "tactile_soft_skeuomorphic_card",
  "usage": "generic",
  "production": {
    "intent": "motion_ready",
    "stage_canvas": {
      "width": 1920,
      "height": 1080,
      "aspect_ratio": "16:9",
      "orientation": "landscape",
      "safe_area": {
        "top": 0.07,
        "right": 0.08,
        "bottom": 0.07,
        "left": 0.08
      }
    },
    "card_asset": {
      "width": 1080,
      "height": 1440,
      "aspect_ratio": "3:4",
      "orientation": "portrait",
      "outer_background": "transparent",
      "safe_area": {
        "top": 0.07,
        "right": 0.08,
        "bottom": 0.07,
        "left": 0.08
      }
    },
    "output_layers": ["transparent_asset", "preview_composite"]
  },
  "canvas": {
    "width": 1920,
    "height": 1080,
    "aspect_ratio": "16:9",
    "safe_area": {
      "top": 0.07,
      "right": 0.08,
      "bottom": 0.07,
      "left": 0.08
    }
  },
  "content": {
    "blocks": []
  },
  "layout": {
    "density": "balanced",
    "slots": {},
    "component_order": [],
    "anchors_required": ["thick_stroke", "hard_shadow", "dot_surface"]
  },
  "render": {
    "engine": "opendesign-html",
    "entry": "assets/templates/card-base.html",
    "outputs": {}
  },
  "video": {
    "handoff_required": false
  }
}
```

Use relative ratios for `safe_area` and slot positions. Use absolute pixels only for final render dimensions.

`canvas` may describe the preview composite canvas for legacy compatibility. For new specs, `production.stage_canvas` describes the video or preview stage, while `production.card_asset` describes the independent card asset size and shape. Do not assume they are the same.

## Production And Output Layers

The contract distinguishes three related surfaces:

| Field | Meaning |
| --- | --- |
| `production.intent` | `static_only`, `motion_ready`, or `static_plus_motion` |
| `production.stage_canvas` | Full stage or video canvas, such as `1920 x 1080` |
| `production.card_asset` | The card's own render box, which may be portrait, square, landscape, or custom |
| `production.output_layers` | Required outputs: `transparent_asset`, `preview_composite`, and optional `source_editable` |

Output layer rules:

- `transparent_asset` is the primary asset when motion is possible. Its outer background must be transparent.
- `preview_composite` may include a full-canvas background, gradient, or scene for human review.
- Backgrounds used only to demonstrate a material, such as glassmorphism blur, belong in `preview_composite` or Remotion scene layers.
- Single cards should be exported as independent assets so later layouts can arrange, stack, orbit, or sequence them.

## Content Blocks

All visible copy should be represented as `content.blocks[]`.

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Stable block ID, such as `title.main` or `button.primary` |
| `role` | yes | Semantic role: `number`, `title`, `subtitle`, `body`, `label`, `button`, `note`, `caption` |
| `text` | yes | Exact user-approved text |
| `priority` | no | `1` is most important, `5` is least important |
| `emphasis` | no | Visual scale: `hero`, `primary`, `secondary`, `supporting`, `quiet` |
| `slot` | no | Layout slot: `chrome`, `hero`, `content`, `actions`, `meta`, `overlay` |
| `tone` | no | Color role: `ink`, `yellow`, `red`, `green`, `muted`, `inverse` |
| `max_lines` | no | Maximum line count before resizing/reflow |
| `locked` | no | If true, do not rewrite this text |

## Layout Slots

OpenDesign should map layout slots to visual regions:

| Slot | Purpose | Typical components |
| --- | --- | --- |
| `chrome` | software-window cues | macOS dots, status dots, tiny labels |
| `hero` | main information | number, title, large phrase |
| `content` | supporting information | subtitle, bullets, explanation blocks |
| `actions` | call-to-action area | buttons, toggles, tags |
| `meta` | background context | code panel, badges, small notes |
| `overlay` | interaction cues | cursor, click ripple, pointer trail |

Slots are regions, not fixed coordinates. They can stretch or collapse based on content density.

## Component Mapping

| `role` / anchor | HTML class | OpenDesign component name | Notes |
| --- | --- | --- | --- |
| canvas | `.nook-card-canvas` | `NookCard.Canvas` | Owns dimensions and background |
| main card | `.nook-card-surface` | `NookCard.Surface` | Thick stroke, dot grid, hard shadow |
| `chrome` slot | `.nook-card-chrome` | `NookCard.Chrome` | Holds macOS dots/status cues |
| `number` | `.nook-card-number` | `NookCard.Number` | Optional hero numeric marker |
| `title` | `.nook-card-title` | `NookCard.Title` | Highest text hierarchy if no number |
| `subtitle` | `.nook-card-subtitle` | `NookCard.Subtitle` | Secondary explanatory text |
| `body` | `.nook-card-body` | `NookCard.Body` | Dense content, may use bullets |
| `label` | `.nook-card-label` | `NookCard.Label` | Small tag or badge |
| `button` | `.nook-card-button` | `NookCard.Button` | Pressable hard-shadow element |
| `cursor` anchor | `.nook-card-cursor` | `NookCard.Cursor` | Optional interaction hint |
| `code_panel` anchor | `.nook-card-code-panel` | `NookCard.CodePanel` | Optional background context |

Every rendered component should include `data-block-id` when it comes from `content.blocks[]`.

## Data Attributes

Recommended HTML attributes:

```html
<main class="nook-card-canvas" data-style-id="tactile_soft_skeuomorphic_card" data-schema-version="0.2">
  <section class="nook-card-surface" data-component="surface">
    <h1 class="nook-card-title" data-block-id="title.main"></h1>
  </section>
</main>
```

These attributes make browser QA, screenshot comparison, and Remotion extraction easier.

## Dynamic Fitting Rules

- Preserve content priority before decorative anchors.
- Preserve output layer separation before visual convenience.
- If text overflows, first reduce secondary text size, then reduce body density, then collapse optional meta/overlay elements.
- Do not reduce stroke width, hard shadow, or dot surface visibility to solve layout problems.
- Buttons may stack vertically or convert to labels if there are more than two actions.
- `hero` text can wrap, but should not exceed `3` lines unless the user explicitly asks for a text-heavy card.
- Body copy should be grouped into blocks instead of becoming a single long paragraph.
- Do not bake preview backgrounds into `transparent_asset`.
- For motion-ready tasks, validate each card both as a standalone transparent asset and as a preview composite.

## OpenDesign Render Input

Before rendering, Codex should pass OpenDesign:

- `card-spec.json`,
- selected style reference,
- `DESIGN.md`,
- selected HTML/CSS template if the target is HTML preview,
- quality checklist.

OpenDesign should return or update:

- rendered preview path,
- exported `transparent_asset` path if requested,
- exported `preview_composite` path if requested,
- updated `card-spec.json` with render outputs,
- warnings for text overflow, missing fonts, or token violations.

## Remotion Compatibility

Fields that Remotion can inherit directly from `card-spec.json`:

- `canvas.width`
- `canvas.height`
- `production.stage_canvas`
- `production.card_asset`
- `production.output_layers`
- `content.blocks`
- `layout.component_order`
- `render.outputs.transparent_png`, `render.outputs.transparent_svg`, `render.outputs.preview_png`, or `render.outputs.html`
- `video.scene_id`
- `video.motion_intent`
- `video.voiceover`
- `video.subtitle`

Remotion-specific timing and sequence fields belong in `remotion-handoff.json`.
