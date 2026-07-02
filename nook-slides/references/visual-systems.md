# Visual Systems

This is the current visual-system authority for `nook-slides`.

The production workflow has exactly three Chinese visual systems. Do not present retired English theme sets as current choices.

## 1. Current Systems

| Theme ID | Chinese name | Current role | Editable PPTX renderer |
|---|---|---|---|
| `duotone-zine` | 双色独立刊物风 | reference production system | available through `scripts/build_deck.py` |
| `oriental-dark-yaji` | 东方暗调雅集风 | 13-component visual library exists; renderer not approved | not approved yet |
| `bright-street-dance` | 明亮街舞贴纸风 | 13-component visual library exists; renderer not approved | not approved yet |

For real editable PPTX delivery, use `duotone-zine` unless the user explicitly accepts a schema-only or prototype result for another system.

If the user chooses `oriental-dark-yaji` or `bright-street-dance` and asks for final editable PPTX, stop and explain that the visual system still needs a deterministic renderer. Do not improvise a PPTX or redraw the style from scratch.

The two non-production visual libraries are generated as fill-in-the-blanks artifacts:

```text
assets/templates/duotone-zine/component-library-source.py
-> assets/templates/extract_duotone_component_skeleton.py
-> assets/templates/global-component-skeleton-v1.json
+ theme tokens in assets/templates/generate_theme_component_libraries.py
= theme component-library-v0.1.0.pptx
```

The duotone source owns page order, component IDs, named image slots, card counts, relative positions, and structural relationships. The extracted skeleton records those facts. Theme tokens own only color, typography, shape radius, line weight, shadow behavior, and theme code labels.

## 2. 双色独立刊物风

Use for creator methods, thinking tools, editorial explainers, personal knowledge systems, AI workflow talks, and decks that benefit from a printed independent-zine feeling.

Visual grammar:

- Big words, few words, many images.
- Paper texture, strong ink, duotone accents, editorial rhythm.
- Text sits inside deliberate containers.
- Black blocks are emphasis, not default decoration.
- Real screenshots and images are preferred when the slide makes factual claims.

Renderer status:

- `deck_plan.json` schema: available.
- Deterministic editable PPTX renderer: available.
- Validation scripts: available.

## 3. 东方暗调雅集风

Use for cultural, tea, incense, history, oriental aesthetics, slow lifestyle, and quiet object-led decks.

Visual grammar:

- Dark brown-black canvas.
- Warm light and quiet object photography.
- Song-style display typography.
- Thin low-contrast lines.
- Small seal-red accents.
- Slow page rhythm and few words.

Renderer status:

- Schema planning: allowed.
- 13-component visual library: `assets/templates/oriental-dark-yaji/component-library-v0.1.0.pptx`.
- golden review: allowed when assets exist.
- Editable PPTX production: blocked until deterministic renderer is approved.

## 4. 明亮街舞贴纸风

Use for dance, sports, youth recruitment, camps, challenges, community activities, and high-energy action decks.

Visual grammar:

- Bright white or pale blue background.
- Cutout person or motion figure as the main visual.
- Bubble titles, thick black outlines, stickers, retro windows, pixel icons.
- Sky blue with hot pink and lime support accents.
- Energetic hierarchy, not random sticker scattering.

Renderer status:

- Schema planning: allowed.
- 13-component visual library: `assets/templates/bright-street-dance/component-library-v0.1.0.pptx`.
- golden review: allowed when assets exist.
- Editable PPTX production: blocked until deterministic renderer is approved.

## 5. Retired Theme Set

The old English gallery is not the current production system. Do not ask the user to choose from it during current production work. If old files mention it, treat those files as historical material.
