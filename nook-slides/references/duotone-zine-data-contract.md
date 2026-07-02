# Duotone zine data contract

Use this reference when asking an Agent to produce or repair a `deck_plan.json` for the duotone independent-zine visual system.

This file is the model-facing fill-in-the-blanks contract. It does not describe visual layout. It describes what data each approved component may receive. The renderer owns coordinates, fonts, colors, spacing, connectors, and image-slot geometry.

Read `duotone-zine-component-registry.md` first when planning pages. The maintained `zine.*` components are the current executable standard and must remain the schema authority until a new visual template package is actually approved.

Do not use the temporary production IDs from the discarded 260630 renderer experiment in accepted `deck_plan.json` files. A real deck plan must target maintained template components directly.

## 1. Global rules

The Agent may only:

1. choose an approved `component`;
2. choose an approved `variant`;
3. fill declared fields;
4. reference declared image slots;
5. shorten or split content before confirmation.

The Agent must not:

1. add coordinates, sizes, colors, font names, margins, alignment, line positions, or connector geometry;
2. add unknown fields;
3. create unapproved component names or variants;
4. trim arrays silently to fit a component;
5. place construction notes on slides;
6. rewrite locked visible copy during rendering.

Every page object must include:

```json
{
  "page_no": 1,
  "component": "approved component id",
  "variant": "approved variant id",
  "visual_carrier": "statement | image | screenshot | chart | table | structure",
  "title": "visible title"
}
```

## 2. Approved maintained component standard

The current accepted schema targets the maintained `zine.*` components. These are not disposable; they are the visual and structural reference standard for all three visual systems.

### `zine.hero-title`

Use for cover, chapter opener, or strong opening page.

Approved variants:

- `cover-left-type-right-image`
- `cover-image-right`
- `case-opener`

Allowed fields:

- `title`: required, <= 18 Chinese chars for cover variants.
- `subtitle`: optional, <= 28 Chinese chars.
- `body`: optional, <= 45 Chinese chars.
- `footer`: optional, <= 20 Chinese chars.
- `image_slots`: optional, 0-1 main image.

Rules:

- Do not use `cards`.
- Do not use multiple images unless a new variant is approved.

### `zine.statement`

Use for one judgment, warning, conclusion, or transition.

Approved variants:

- `single-judgement`
- `fragment-cards`

Allowed fields:

- `title`: required, <= 20 Chinese chars.
- `body`: optional, <= 45 Chinese chars.
- `chips`: optional, 0-3 short labels, each <= 10 Chinese chars.
- `cards`: only for `fragment-cards`, 2-4 fragments, each title <= 12 Chinese chars.

Rules:

- One dominant sentence only.
- Do not use as a normal paragraph page.

### `zine.big-number`

Use when numbers are the main message.

Approved variants:

- `three-column`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `cards`: required, exactly 3 metric cards.

Each card:

- `title`: number or metric value, <= 8 chars.
- `label`: metric label, <= 10 Chinese chars.
- `body`: optional explanation, <= 24 Chinese chars.
- `accent`: optional approved color token.

Rules:

- Do not mix unrelated metrics.
- If there is only one number, use a new approved variant before production.

### `zine.process-cards`

Use for linear workflow, method steps, action path, or chain.

Approved variants:

- `four-step`
- `three-deliverables`
- `system-chain`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `cards`: required, count depends on variant.

Capacity:

- `four-step`: exactly 4 cards.
- `three-deliverables`: exactly 3 cards.
- `system-chain`: 3-5 cards.

Each card:

- `title`: step name, <= 10 Chinese chars.
- `body`: optional short explanation, <= 36 Chinese chars.
- `label`: optional step label, <= 8 chars.
- `accent`: optional approved color token.

Rules:

- The relationship must be directional.
- If the content is not ordered, use `zine.card-group`.

### `zine.timeline`

Use for chronology, milestones, version history, roadmap, or staged migration.

Approved variants:

- `four-event`
- `five-layer`
- `cpr`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `cards`: required, count depends on variant.

Capacity:

- `four-event`: exactly 4 events.
- `five-layer`: exactly 5 events.
- `cpr`: exactly 3 events.

Each card:

- `year`: required time/stage label, <= 8 chars.
- `title`: event title, <= 10 Chinese chars.
- `body`: optional event note, <= 28 Chinese chars.
- `accent`: optional approved color token.

Rules:

- If there is no time or staged order, do not use timeline.
- Do not encode chronological labels in arbitrary body text; use `year`.

### `zine.cycle`

Use for closed feedback loop, repeated work rhythm, or iteration mechanism.

Approved variants:

- `four-node`
- `action-rhythm`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `center`: optional center idea, <= 12 Chinese chars.
- `center_body`: optional, <= 28 Chinese chars.
- `cards`: required, exactly 4 nodes.

Each card:

- `title`: node title, <= 8 Chinese chars.
- `body`: optional, <= 24 Chinese chars.
- `label`: optional sequence label, <= 4 chars.
- `accent`: optional approved color token.

Rules:

- Must describe a loop, not a simple sequence.
- If it does not return to the start, use `zine.process-cards`.

### `zine.hierarchy`

Use for system layers, dependencies, priority stack, or nested structure.

Approved variants:

- `four-layer`
- `skill-structure`
- `five-layer-preview`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `cards`: required, count depends on variant.

Capacity:

- `four-layer`: exactly 4 layers.
- `five-layer-preview`: exactly 5 layers.
- `skill-structure`: 3-6 layers.

Each card:

- `title`: layer name, <= 12 Chinese chars.
- `body`: optional, <= 32 Chinese chars.
- `label`: optional layer label, <= 8 chars.

Rules:

- Use only for vertical, nested, or dependency relationship.
- If time matters more than dependency, use `zine.timeline`.

### `zine.comparison`

Use for old/new, before/after, with/without, option A/B, or tradeoff.

Approved variants:

- `two-column`
- `three-case-summary`
- `template-vs-context`
- `old-solutions`
- `shell`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `cards`: required, count depends on variant.

Capacity:

- `two-column`: exactly 2 sides.
- `template-vs-context`: exactly 2 sides.
- `shell`: exactly 2 sides.
- `three-case-summary`: exactly 3 sides.
- `old-solutions`: 2-5 compared items.

Each card:

- `title`: side or option name, <= 12 Chinese chars.
- `body`: matched fields or short description, <= 50 Chinese chars.
- `label`: optional decision tag, <= 8 chars.
- `accent`: optional approved color token.

Rules:

- Sides should be comparable using matched fields.
- If the cards are just peers, use `zine.card-group`.

### `zine.card-group`

Use for parallel peer modules, cases, roles, examples, or deliverables with no direction.

Approved variants:

- `parallel-three`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `body`: optional framing sentence, <= 45 Chinese chars.
- `cards`: required, exactly 3 peers.

Each card:

- `title`: peer title, <= 12 Chinese chars.
- `body`: peer description, <= 36 Chinese chars.
- `label`: optional, <= 8 chars.
- `accent`: optional approved color token.

Rules:

- No arrows, timeline labels, loop logic, or hierarchy should be implied by the data.

### `zine.image-text`

Use when one image or screenshot anchors the page.

Approved variants:

- `large-image-left`
- `illustration-statement`
- `screenshot-evidence`
- `project-structure`
- `project-root`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `body`: optional, <= 60 Chinese chars.
- `footer`: optional source/caption, <= 32 Chinese chars.
- `image_slots`: required, exactly 1 main image slot.

Image slot:

- `path` for real asset, or `placeholder` for approved placeholder.
- `fit`: `contain` or `cover`.
- `status`: optional asset status.
- `focus_x` / `focus_y`: optional crop focus only, not layout.

Rules:

- If the page makes a factual UI/product claim, the image must be a real screenshot.
- Do not generate fake factual screenshots.

### `zine.image-collage`

Use for multi-image evidence or visual story.

Approved variants:

- `three-image`
- `evidence-triptych`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `body`: optional, <= 45 Chinese chars.
- `image_slots`: required, exactly 3 images.

Rules:

- One image is visually primary by template, not by Agent coordinates.
- Do not use as an equal dense grid unless a new variant is approved.

### `zine.brand-master`

Use for logo, IP, QR, mascot, or brand usage rules.

Approved variants:

- `logo-ip-rules`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `body`: optional, <= 60 Chinese chars.
- `cards`: optional, 2-4 usage rules.
- `image_slots`: optional, 1-4 brand/IP slots.

Rules:

- Logo keeps original identity.
- IP must be user-provided before style transfer.
- QR must not be fake in production.

### `zine.generated-asset`

Use for AI-generated illustration, style-transfer plan, non-factual title visual, or asset intake.

Approved variants:

- `asset-spec`

Allowed fields:

- `title`: required, <= 18 Chinese chars.
- `body`: optional, <= 60 Chinese chars.
- `cards`: optional, 3-4 asset steps or constraints.
- `image_slots`: optional, 1 generated asset slot.

Rules:

- Generated images are for non-text, non-factual visual assets.
- Do not use image generation for final slide text or factual screenshots.

## 3. Error handling

If content does not fit the chosen component:

1. split the page;
2. choose another approved component;
3. ask the user to approve a new component variant.

Never solve overflow by inventing coordinates, shrinking text indefinitely, deleting cards, trimming nodes, or changing a variant silently.
