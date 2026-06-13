# nook-card Quality Checklist

Version: v0.2

Use this checklist after generating or revising a card. Do not treat a card as finished until all P0 items pass.

## P0 Checks

- Content matches the confirmed copy and hierarchy.
- No typo, missing character, or unintended wording change.
- Main title, subtitle, body, labels, and buttons do not overflow or collide.
- Selected `style_id` matches the style reference.
- Main card preserves the required anchors of the selected style and keeps typography readable.
- Export path and output dimensions match the requested use.
- If motion is possible, `transparent_asset` has transparent outer background and does not include preview-only full-canvas background.
- `card_asset_ratio` and `stage_canvas` are recorded separately when they differ.

## P1 Checks

- Color, depth, texture, and component tokens stay within the selected style tolerance.
- Optional cues such as buttons, labels, icons, stickers, glass chips, or panels support the card rather than distracting.
- `preview_composite` is clearly marked as preview/review output, not the motion source asset.

## P2 Checks

- Composition still belongs to the same visual family when aspect ratio or content density changes.
- The generated card can be described as a reusable layout, not a one-off poster.
- Each card can stand alone as an independent layer for later arrangement or sequencing.
- If video handoff is requested, scene duration, animation intent, and subtitle/voiceover fields are present.
