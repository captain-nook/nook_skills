# Duotone zine template package

This is the executable template contract for the current duotone independent-zine visual system.

## Highest authority

Use `assets/templates/duotone-zine/component-library-v0.3.1.pptx` as the visual source of truth.

Use `assets/templates/duotone-zine/component-library-source.py` only to inspect the exact coordinates, sizes, colors, and text hierarchy used to create that template.

Do not create a new freeform layout when this template package has a matching page form.

## Production rule

Generation is template filling:

1. Select a page form from the confirmed content/page-form note.
2. Map it to one of the approved template components below.
3. Copy or reproduce the matching component geometry from `component-library-source.py`.
4. Replace only visible text, images, logo, and slot content.
5. If content exceeds a component capacity, stop and report the mismatch. Do not shrink text indefinitely. Do not invent a new layout.

## Approved component variants

| Component | Variant | Capacity | Source slide/function | Notes |
| --- | --- | ---: | --- | --- |
| `zine.hero-title` | `cover-left-type-right-image` | title <= 18 Chinese chars, subtitle <= 28 | `slide_01_cover` | Cover / chapter opener. |
| `zine.statement` | `single-judgement` | title <= 20, body <= 45 | `slide_02_statement` | One strong conclusion. No black construction bars. |
| `zine.big-number` | `three-column` | 3 metrics | `slide_03_numbers` | Numbers only, not long paragraphs. |
| `zine.process-cards` | `four-step` | exactly 4 cards, each 1 title + 2-3 bullets | `slide_04_process_cards` | The current safe process-card template. |
| `zine.timeline` | `four-event` | exactly 4 events | `slide_05_timeline` | Years/stages must share one number style. |
| `zine.cycle` | `four-node` | exactly 4 nodes | `slide_06_cycle` | Closed loop only. |
| `zine.hierarchy` | `four-layer` | exactly 4 layers | `slide_07_hierarchy` | Stacked hierarchy; no arbitrary network. |
| `zine.comparison` | `two-column` | 2 sides | `slide_08_comparison` | Before/after or choice. |
| `zine.image-text` | `large-image-left` | 1 image + short title/body | `slide_09_image_text` | Screenshot/illustration-led. If image is missing, use a small placeholder only. |
| `zine.image-collage` | `three-image` | 3 images | `slide_10_image_collage` | Multi-image page. |
| `zine.brand-master` | `logo-ip-rules` | logo + IP rules | `slide_11_brand_master` | Logo is original small corner mark; IP must be stylized by image generation. |
| `zine.generated-asset` | `asset-spec` | 1 generated asset | `slide_12_generated_asset` | For generated illustration specification and placement. |

## Forbidden fallback

Do not use these fallbacks in production:

- arbitrary network lines;
- auto-spread cards across the canvas;
- blank oversized image placeholders;
- black text blocks or black banners unless copied from an approved template component;
- visible construction notes such as “后补”, “占位”, “不伪造”, component IDs, file paths, or build comments outside a replaceable image slot;
- using a component with a different item count than its approved variant.

## Current limitation

The current first visual system is intentionally narrow. If a deck needs 5-card, 6-card, 7-card, network, pyramid, or dense screenshot annotation pages, create and approve those template variants first. Do not let the production generator improvise them.

## Legacy normalization rules

These rules exist only to protect production from old plans created before the template package was strict.

- `zine.hierarchy.network` is downgraded to `timeline-like`. Arbitrary connector networks are disabled until a formal network template is designed and approved.
- Hierarchy pages with more than 5 cards are trimmed to 5 visible cards. Larger structures must be split or given a new approved template.
- `zine.process-cards.persona-cards` and `zine.process-cards.action-path` are normalized to approved card templates. More than 5 visible cards are trimmed; larger action paths must be split or given a new approved template.
- Historical variant names such as `cover-image-right`, `fragment-cards`, `five-layer`, `cpr`, and `evidence-triptych` may map to existing approved template geometry, but they do not grant permission to invent layout.

The generator must print visible progress and fail fast when normalization cannot produce an approved template fit.

## Executor implementation status

The production renderer must use the same geometry language as `component-library-source.py`.

Current executor status:

- Canvas is 16×9, matching the component library.
- Production paths for `process_cards`, `timeline`, `hierarchy`, `comparison`, and `image_text` have been rewritten to fixed template geometry.
- 5-node timeline pages use a dedicated shallow-card zigzag template with a right arrow; 3-node CPR pages use progressive cards with short arrows.
- Case opener chips use a left 2x3 grid and must not overlap the image slot.
- `_cards_grid` is not allowed in production component renderers. It may remain only as a legacy helper for tests or migration.
- Bounds checks must report zero out-of-slide elements before a deck is handed to the user.
- Layout probe must report clean for text overlap and page-center bias before handoff.
- Titles must be single-line except the main cover; manual line breaks in card/body text are normalized to inline separators to avoid orphan punctuation.

Latest verified output: `260628-AI培训-样张几何执行器-v0.9.pptx`.




