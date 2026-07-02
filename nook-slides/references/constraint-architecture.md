# Constraint architecture

Use this reference when maintaining the generation pipeline, component schemas, or a visual-system package.

## 0. Core diagnosis

The model must not be responsible for visual layout.

The recurring failure mode is letting the model perform both content planning and visual composition. Content planning is probabilistic but reviewable. Visual composition needs deterministic geometry. If the model is allowed to decide coordinates, spacing, alignment, colors, font sizes, connectors, or image-slot geometry, the result will drift even when examples are provided.

PPT Master's stability comes from the opposite boundary:

```text
AI outputs structured content data.
Code renders the approved template geometry.
```

Treat every accepted deck as a fill-in-the-blanks job. The model may choose or recommend a component from an approved list during planning, but it must never invent visual parameters.

## 1. Four execution layers and two human gates

The production system uses four deterministic layers between two human gates.

### Gate 0: approve the visual system

Build and approve the visual system before using it in production. A production visual system needs reference provenance, tokens, structural skeletons, maintained component source, positive samples, negative samples, and rendered review.

### Layer 1: lock content

Confirm slide count and every visible character before generation. Store the accepted copy in a source file and a machine-readable visible-copy manifest. An accepted `deck_plan.json` must contain both files' SHA-256 hashes, and validation must compare the plan's visible fields with the manifest exactly.

Do not rewrite, summarize, trim, reorder, normalize punctuation, or replace line breaks during rendering.

### Layer 2: map page function

Map every page through four levels:

```text
atomic elements
→ structural skeleton
→ natural page form
→ approved zine component and variant
```

The model may recommend a page family and an approved component. It must not position atomic elements, choose coordinates, tune spacing, resize boxes, pick colors, or create connectors.

Use selection instead of open design:

- choose from approved `component` enum;
- choose from approved `variant` enum;
- fill declared slots only;
- leave all geometry to the renderer.

### Layer 3: validate the contract

Validate the plan before opening PowerPoint generation:

- component and variant are approved;
- fields use the declared schema;
- item counts fit the chosen variant;
- image slots have a source or an approved placeholder;
- page numbers are continuous;
- accepted plans match the locked-content hash;
- no construction text appears in visible copy.

Fail on mismatch. Never repair a mismatch by deleting confirmed content or silently changing variants.

For model-facing structured output, prefer JSON Schema / Structured Outputs / tool-use equivalents over free text. The component name and variant name must be enums. Fields must reject unknown keys. Slot text should carry max-length guidance and be validated before rendering.

### Layer 4: render deterministically

Render from maintained component source. The renderer fills named properties and asset slots. It must not invent layouts, text, colors, shapes, or connectors.

The maintained component source is the machine authority. Generate both the reusable manual component-library PPTX and automatic decks from the same component definitions. Treat the PPTX library and screenshots as visual golden artifacts, not a second geometry source.

### Gate 5: inspect the rendered artifact

Technical validity is necessary but insufficient. Inspect the real rendered slides for hierarchy, density, visual carrier, unwanted wrapping, overlap, theme drift, and similarity to approved golden samples.

## 1.1 Responsibility boundary

| Layer | Responsibility | Owner | Output |
|---|---|---|---|
| Content understanding | Parse source, extract outline, compress ideas | Agent | structured outline |
| Page planning | Recommend page count, page function, component choice | Agent + user | confirmed page-component mapping |
| Data mapping | Fill approved component slots and validate JSON | Agent + code | valid `deck_plan.json` |
| Rendering | Produce PPTX from fixed geometry and assets | code only | editable PPTX |

The renderer is the only layer allowed to know layout coordinates. The Agent only knows component IDs, variants, field names, text limits, and asset-slot requirements.

## 1.2 Current production scope

Do not chase old planning taxonomies during production runs. The executable scope is the approved `zine.*` schema contract:

1. `zine.hero-title`;
2. `zine.statement`;
3. `zine.big-number`;
4. `zine.process-cards`;
5. `zine.timeline`;
6. `zine.cycle`;
7. `zine.hierarchy`;
8. `zine.comparison`;
9. `zine.card-group`;
10. `zine.image-text`;
11. `zine.image-collage`;
12. `zine.brand-master`;
13. `zine.generated-asset`.

These are the only component IDs accepted by `deck_plan.json`. When speaking with the user, translate them into natural Chinese page forms. When writing the plan, use the exact approved IDs and variants.

Future component families may be added only after the schema, contract, deterministic renderer, and visual golden artifacts exist. Missing components are blockers, not invitations to improvise.

## 2. Global nook presentation constitution

These rules sit above all visual themes:

1. Prefer less text to more text.
2. Put ordinary text inside a deliberate visual carrier.
3. Prefer a table or structural diagram when it explains a relationship better than prose.
4. Prefer a real screenshot when the page makes a factual product or event claim.
5. Prefer a dominant image when the speaker can carry the explanation orally.
6. Allow a pure-text page only for an approved statement or equivalent transition component.
7. Do not shrink type to rescue excess content. Split the page or reopen the content gate.

Every ordinary page needs a `visual_carrier`: image, screenshot, chart, table, structural skeleton, or approved statement treatment.

## 3. Structural skeletons

Prioritize these skeletons before expanding page families:

| Skeleton | Required visible grammar |
|---|---|
| linear path | direction, ordered steps, connectors or arrows |
| chronological axis | one axis, nodes, time labels, node-to-content guides |
| closed loop | closed path, direction, repeated nodes |
| hierarchy | parent-child, stack, nesting, pyramid, or dependency |
| mirrored comparison | matched fields around a shared divider or baseline |
| parallel collection | peers with the same fields and no implied direction |

Remove color and text during review. The relationship must remain recognizable.

## 4. Variant capacity

Parameterization is bounded. Approve count-specific variants instead of allowing infinite compression.

Examples:

- timeline: 3-node, 4-node, 5-node; 6-8 nodes require a separately approved two-row variant or a split page;
- process: 3-step, 4-step, 5-step;
- comparison: 2-side or 3-side;
- card group: 3-card or 4-card.

If the confirmed content does not fit, stop. Do not trim arrays, reduce font size indefinitely, or fall back to a generic card grid.

## 5. Machine files

- `assets/schemas/deck-plan-v1.schema.json`: portable plan contract.
- `scripts/plan_contract.py`: dependency-free runtime enforcement.
- `scripts/validate_plan.py`: validation without PPTX generation.
- `scripts/build_deck.py`: deterministic renderer after validation.
