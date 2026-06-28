# Editable PPTX native workflow

Use this reference before generating any formal editable PPTX.

## 1. Non-negotiables

1. Do not generate a full PPTX directly from a natural-language page plan with freeform layout code. Use the selected template file/package as the starting point.
2. Do not ignore the selected template. If a template/component fits, copy/fill it instead of redrawing it.
3. Do not invent arbitrary connector networks. Connectors must come from component rules.
4. Do not stretch images. Use slot rules: `contain`, `cover`, or deliberate `crop`.
5. Do not deliver a PPTX that PowerPoint has to repair. A repair warning means build failure.
6. Do not replace factual screenshots with AI-generated images.
7. Keep logos original and small. Style-transfer only user-provided IP characters or decorative illustrations.

## 2. Required pipeline

1. Consume the confirmed content plan and page-form plan.
2. Map each slide to a template slide/component; keep any component map internal.
3. Fill the selected template with locked visible text and assets. Any visual intermediate must come from the selected template.
4. Inspect or screenshot the visual intermediate for overflow, overlap, image fit, and style drift.
5. Export native PPTX from the same template/component definitions.
6. Validate the PPTX package and slide count.
7. Re-open or parse the PPTX with a trusted library when available.
8. Deliver only after validation passes. If validation fails, report the failed checks and do not call it finished.

## 3. Component map schema

Use this schema as the source of truth between page planning and deck generation:

```yaml
- page_no:
  component_id:
  variant:
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
      safe_area:
  validation:
    max_headline_chars:
    max_body_chars:
    min_font_size:
    no_title:
    notes:
```

Every generated slide must have a component ID. If no component fits, stop and propose a component addition before building.

## 4. Duotone zine component registry

The canonical registry lives in `duotone-zine-component-registry.md`. Use that file as the maintained source. The table below is only a compact reminder.

For the current duotone independent-zine style, use this first component whitelist:

| ID | Component | Main use |
|---|---|---|
| `zine.hero-title` | 巨型标题页 | Cover, chapter opener, strong statement |
| `zine.statement` | 一句话判断页 | Result, transition, warning |
| `zine.big-number` | 大数字页 | Metrics, numbering, stage summary |
| `zine.process-cards` | 流程卡组 | Process, method steps, chain explanation |
| `zine.timeline` | 时间轴 | History, evolution, milestones |
| `zine.cycle` | 循环图 | Feedback loop, rhythm, iteration |
| `zine.hierarchy` | 层级图 | Layers, dependency, upstream/downstream |
| `zine.comparison` | 对比图 | Old/new, before/after, tradeoff |
| `zine.image-text` | 图文混排页 | Main image plus short judgment |
| `zine.image-collage` | 图片拼贴页 | Multi-screenshot evidence or visual story |
| `zine.brand-master` | IP / Logo 母版页 | Logo slot, IP slot, brand asset rules |
| `zine.generated-asset` | 出图资产页 | AI illustration and image-asset intake |

Allowed variants, not new top-level components:

1. `zine.image-text.screenshot-evidence`: one faithful screenshot as primary evidence, short claim, optional small callouts.
2. `zine.image-collage.evidence-triptych`: one main evidence image plus two secondary evidence images.
3. `zine.process-cards.action-path`: linear action path, no freeform connector maze.
4. `zine.hierarchy.timeline-like`: layers with progression emphasis, used when a hierarchy also changes over time.

## 5. Image slot rules

1. A slide may only place images into named slots.
2. Screenshots default to `contain` unless the slot explicitly says `crop`.
3. Decorative illustrations may use `cover` if the safe area is protected.
4. Never distort aspect ratio.
5. If the important subject is off-center, adjust crop position; do not resize randomly.
6. Missing real screenshots become clearly marked placeholders.

## 6. Text rules

1. Visible text must be copied exactly from the confirmed content/page-form note. Do not rewrite during generation.
2. Keep visible copy short. If text exceeds the component limit, stop and report the content/template mismatch; do not silently rewrite or shrink indefinitely.
2. Titles are optional. Do not force a title on every slide.
3. Slides show results and judgments, not oral setup.
4. Put explanations into speaker notes or the source note, not into dense slide text.
5. For duotone zine style: Chinese titles use 思源宋体; Chinese body uses 霞鹜文楷.

## 7. Validation checklist

Before delivery, check:

1. PPTX zip contains `[Content_Types].xml`, `ppt/presentation.xml`, slide XML files, relationships, and media.
2. Slide count matches the component map.
3. No required media file is missing.
4. No text box exceeds its component limit.
5. No image is stretched outside aspect ratio.
6. No element overlaps unless the component explicitly uses layered shadows or print-offset effects.
7. Connector count and connector positions match the component pattern.
8. Fonts are declared according to the style rules.
9. If PowerPoint repair is required, the build has failed.

## 8. Speed discipline

The component map is an internal build artifact owned by the skill, not a user-facing confirmation loop.

If the user has already confirmed content and page forms, do not ask them to redo that work. Generate the component map from the confirmed plan, use placeholders for missing assets when approved, and move to visual intermediate validation.

Ask the user again only when:

1. A required content decision is missing.
2. A page cannot be mapped to the component library.
3. A factual screenshot or brand/IP asset is required and has not been approved as a placeholder.
4. The user explicitly asks to review each page before generation.

## 9. Failure behavior

If validation fails, stop and report:

1. Which slide failed.
2. Which component failed.
3. Whether the issue is content length, image fit, asset missing, connector layout, PPTX package validity, or PowerPoint repair risk.
4. The smallest next fix.

Do not keep patching a broken PPTX silently.
## 10. Template filling correction

For decks with an approved template, the generator must copy/fill the template. Building a new script that only imitates the template is a failure mode.

Do not put construction notes on the slide canvas. Terms such as “后补”, “占位”, “不伪造”, “REAL SCREENSHOT ONLY”, component IDs, or file paths belong in logs or inside replaceable image placeholders only.
