# Duotone zine component registry

This registry is part of the skill. Do not ask the user to design it for each deck.

Use it when a deck chooses the duotone independent-zine visual system or when an existing duotone zine sample is the approved style source.

## 1. Principle

### Template authority

The registry describes available components, but the actual template file/package is the highest visual authority. Use the registry to select a component; use the template to decide the final look, proportion, spacing, and visible visual grammar. Do not redraw components from scratch when the template exists.

### Mapping authority

The user confirms content and page forms. The skill maps the confirmed page plan to this registry automatically.

Do not present `component_map` as a new user-facing approval step. Treat it as an internal construction sheet unless the user explicitly asks to inspect it.

## 2. Top-level components

| ID | Chinese name | Use when | Hard limits |
|---|---|---|---|
| `zine.hero-title` | 巨型标题页 | cover, chapter opener, strong judgment | 1 headline, optional subline, optional main visual slot |
| `zine.statement` | 一句话判断页 | result, transition, warning | 1 main sentence; no dense body text |
| `zine.big-number` | 大数字页 | metrics, stages, issue numbers | 1-3 numbers; each number has a short label |
| `zine.process-cards` | 流程卡组 | steps, chains, action paths | 3-6 cards; no arbitrary connector maze |
| `zine.timeline` | 时间轴 | evolution, history, milestones, staged change | 3-6 nodes; year/stage labels must share style |
| `zine.cycle` | 循环图 | feedback loop, iteration rhythm | 3-5 nodes; closed loop only |
| `zine.hierarchy` | 层级图 | layers, dependencies, upstream/downstream | 3-6 layers; if progression matters, use timeline-like variant |
| `zine.comparison` | 对比图 | old/new, before/after, tradeoff | 2-3 columns; each side has matched structure |
| `zine.image-text` | 图文混排页 | one main image plus short judgment | 1 main image slot; preserve aspect ratio |
| `zine.image-collage` | 图片拼贴页 | multi-screenshot evidence, visual story | 2-5 image slots; one primary slot must dominate |
| `zine.brand-master` | IP / Logo 母版页 | logo corner, IP intake, brand asset rules | logo remains original; IP must be user-provided |
| `zine.generated-asset` | 出图资产页 | AI illustration, image-generation asset intake | no factual screenshot replacement |

## 3. Approved variants

Variants extend components; they are not new component families.

| Variant | Parent | Use |
|---|---|---|
| `screenshot-evidence` | `zine.image-text` | one faithful screenshot as primary proof, with short claim and optional callout |
| `evidence-triptych` | `zine.image-collage` | one main evidence image plus two supporting images |
| `action-path` | `zine.process-cards` | final action route or operational sequence |
| `system-chain` | `zine.process-cards` | technical/service chain such as Bot → Worker → DB → Reader |
| `timeline-like` | `zine.hierarchy` | hierarchy that also needs progression or migration feeling |
| `skill-structure` | `zine.hierarchy` | folder/skill/module structure |
| `three-deliverables` | `zine.process-cards` | final three-card takeaway |

## 4. Automatic mapping heuristics

Use these rules after content and page forms are confirmed:

1. Strong single judgment -> `zine.statement`.
2. Chapter opener or cover -> `zine.hero-title`.
3. Numeric shock or issue number -> `zine.big-number`.
4. Linear operation or method -> `zine.process-cards`.
5. Historical change, evolution, staged migration -> `zine.timeline`.
6. Feedback, iteration, repeated work rhythm -> `zine.cycle`.
7. Layers, dependencies, personal context stack -> `zine.hierarchy`.
8. Old/new, with/without, before/after -> `zine.comparison`.
9. One real screenshot proves the point -> `zine.image-text` + `screenshot-evidence`.
10. Multiple screenshots prove a chain -> `zine.image-collage` + `evidence-triptych`.
11. Logo/IP question -> `zine.brand-master`.
12. AI illustration or style-transferred IP -> `zine.generated-asset`.

If two components match, choose the one already confirmed by the page-form gate. If no component matches, stop and propose a registry addition before building.

## 5. Internal component_map schema

The implementation may generate a `component_map` file or object, but it is internal by default.

```yaml
- page_no:
  component_id:
  variant:
  source_decision: content_gate | page_form_gate | registry_heuristic | user_override
  content:
    headline:
    subline:
    body:
    cards:
  slots:
    - slot_id:
      asset_type:
      required:
      status:
      fit: contain | cover | crop
  validation:
    max_headline_chars:
    max_body_chars:
    min_font_size:
    preserve_aspect_ratio:
    no_free_connectors:
```

Use this structure to drive generation and validation. Do not require the user to approve it unless a decision is missing.

## 6. User-facing behavior

Ask the user about:

1. Content and visible copy.
2. Page form when the deck is formal or long.
3. Missing factual screenshots or whether placeholders are acceptable.
4. Logo availability.
5. IP character availability and whether style transfer is allowed.

Do not ask the user to approve:

1. Component IDs.
2. Slot IDs.
3. Internal validation fields.
4. The generated `component_map` as a separate stage.

Report component mapping only as a build summary, for example: “30 pages mapped to 12 maintained components; 9 pages use screenshot placeholders.”
## 7. Final-slide cleanliness

Construction labels are forbidden on final slides.

Allowed: minimal placeholder text inside an image slot.

Forbidden outside the image slot: component IDs, slot IDs, “真实截图后补”, “后续替换”, “不伪造”, “REAL SCREENSHOT ONLY”, file paths, and build notes.

