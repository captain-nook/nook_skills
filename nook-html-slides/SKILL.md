---
name: nook-html-slides
description: Create Chinese-first HTML slide decks and template-driven editable PPTX decks from topics, notes, outlines, articles, data, or assets. Use when the user asks to make slides, PPT, presentation, deck, HTML slides, course/tutorial slides, strategy/report/pitch slides, or wants an AI-assisted PowerPoint alternative with guided content/page-form confirmation, visual-system template selection, exact visible-text locking, template-filled editable PPTX generation, image planning, and validation.
---

# 1 nook-html-slides

Create Chinese-first slide decks with a stable workflow: content first, page-form confirmation second, template filling third, validation last.

## 1.1 Core Rules

- For HTML decks, produce HTML as the primary artifact. For editable PPTX decks, PPTX is the primary artifact and must follow `references/template-driven-pptx.md` first.
- For editable PPTX, the selected template is the highest visual authority, and confirmed visible text must be copied exactly. Use `references/ppt-native-workflow.md` only for native PPTX validation and export discipline.
- Use a fixed 16:9 slide stage, designed internally at 1920 x 1080 or an equivalent fixed canvas, then scale the whole stage to the viewport.
- Keep slides word-light and visual-heavy. One slide carries one main message.
- Never allow slide titles to wrap. Rewrite long titles before designing.
- Do not generate final slide pages directly with an image model. Use image models only for non-text assets such as backgrounds, conceptual visuals, or atmosphere.
- Use real screenshots, logos, charts, and product images when the content depends on factual or product evidence.
- Do not proceed from content to full deck until the content outline, exact visible text, page forms, assets, and visual template are confirmed, unless the user explicitly asks to skip confirmation.
- For formal PPTX, editable decks, or long decks, also use `references/ppt-preflight.md`: confirm content, per-slide presentation form, and assets before generating the accepted deck.
- Treat confirmation as a hard gate. If the user says "continue", "go on", "下一步", or similar, ask for the required confirmation instead of silently choosing defaults.
- Do not choose a visual theme for the user. Recommend options, explain tradeoffs, and wait for the user to pick one or approve a mix.
- Text descriptions of visual themes are not enough. Present the fixed visual theme gallery before asking the user to choose a theme unless the user explicitly declines previews.
- Visual themes are maintained as template files/packages, not reinvented per deck. The selected template is the highest visual authority. Update template assets and references when themes or palettes change.
- Mark any deck generated before user confirmation as an unapproved prototype, not as the accepted deck.

## 1.2 Required Workflow

1. **Collect context**: Ask for purpose, audience, target outcome, length, density, available content, and assets.
2. **Create a deck folder**: Use `YYMMDD-deck-slug/` with `brief.md`, `content/`, `assets/`, `data/`, `output/`, and `notes/`.
3. **Check facts and assets early**: Identify time-sensitive facts, data sources, logos, screenshots, images, and copyright or style risks.
4. **Plan content**: Produce the core judgment, narrative line, suggested slide count, and slide-by-slide main messages. Keep slide titles short.
5. **Confirm content**: Ask the user to approve or adjust the outline.
6. **Confirm page forms**: For formal PPTX or long decks, recommend a component/presentation form for each slide, give alternatives, and wait for the user's choice.
7. **Offer visual directions**: Show the fixed 5-theme gallery from `assets/theme-gallery/`, then recommend suitable themes for the current deck.
8. **Confirm visual direction**: Let the user choose one theme or mix specific elements, then choose a palette from that theme's color options.
9. **Plan assets and enhancements**: Decide which slides need screenshots, charts, AI-generated non-text visuals, motion, real assets, logo, IP, or user stickers.
10. **Generate deck**: Make `output/deck.html` for HTML decks. For editable PPTX, copy/fill the selected template with locked text and assets; do not redraw the style from scratch.
11. **Validate and fix**: Check 16:9 stage, title wrapping, text overflow, element overlap, readability, consistent style, asset loading, and visual density.
12. **Deliver**: Provide the local output path. Offer optional PDF, image export, or deployment only after the first deck works.

## 1.3 Confirmation Gates

Before generating the full deck, stop at these gates:

1. **Content gate**: show the proposed slide count, slide titles, and visible on-slide copy. Ask the user to confirm, shorten, reorder, or rewrite.
2. **Page-form gate**: for formal PPTX or long decks, show the recommended presentation form for each slide, with alternatives. Ask the user to confirm or choose another form.
3. **Theme gate**: show the fixed visual gallery of the 5 maintained themes. Ask the user to choose one theme or a mix.
4. **Palette gate**: after theme selection, show that theme's maintained palette options. Ask the user to choose one palette or provide a brand color.
5. **Asset/enhancement gate**: list planned visuals, charts, screenshots, motion, Open Design usage, logo, IP, and user-provided stickers/screenshots. Ask the user to approve or remove them.

Only after all required gates are passed may `output/deck.html` be generated as the accepted deck. If the user explicitly says to skip gates, record that in `notes/build-log.md`.

## 1.4 Open Design Usage

Open Design is optional, not automatic.

- If Open Design CLI / daemon is available and the user wants to use it, record the intended command or handoff path before running it.
- If Open Design is not used, say clearly that the current output is a local HTML deck or prototype generated by Codex, not an Open Design artifact.
- Do not imply that Open Design was used unless it was actually invoked.

## 1.5 When to Read References

- Read `references/workflow.md` before starting any deck task.
- Read `references/ppt-preflight.md` before formal PPTX generation, editable deck generation, or any long deck where page forms and user assets must be confirmed.
- Read `references/template-driven-pptx.md` before generating or modifying any editable PPTX.
- Read `references/visual-system-templates.md` before choosing or filling any maintained visual-system template.
- Read `references/ppt-native-workflow.md` for editable PPTX export and validation discipline.
- Read `references/duotone-zine-component-registry.md` when the chosen or approved visual system is 双色独立刊物风 / duotone independent-zine style.
- Read `references/theme-system.md` before presenting visual theme or palette options.
- Read `references/visual-themes.md` when choosing or implementing visual directions.
- Read `references/validation-checklist.md` before final delivery and after any substantial revision.

## 1.6 Default Visual Themes

Use these as v0 choices. They are starting points, not final permanent limits.

1. **Minimal Keynote**: Apple-like, low density, single main visual, large whitespace.
2. **Calm Strategy**: Executive decision material, single accent color, metrics, roadmap, decision cards.
3. **Research Brief**: Evidence-led, charts and tables, two-color grid or monochrome report feel.
4. **Product Tutorial**: Screenshot-led teaching, step numbers, callouts, low distraction.
5. **Pitch Proposal**: Strong grid, single signal color, problem-solution-evidence-action flow.

## 1.7 HTML Generation Requirements

- Keep CSS and JS inline for the first version unless asset complexity requires a folder.
- Use stable dimensions for slide elements. Avoid layouts that shift when content changes.
- Use CSS variables for theme tokens: background, text, muted, accent, surface, line, radius, font families.
- Put long explanations in speaker notes, comments, `content/outline.md`, or appendix slides, not on main slides.
- Use visible text only for actual slide content. Do not render internal labels like "preview", "template", "style option", file paths, or workflow notes inside slides.
- Include keyboard navigation if generating a multi-slide deck.
- Include `prefers-reduced-motion` support if animations are added.

## 1.8 Output Discipline

For every generated deck, keep project artifacts organized:

```text
YYMMDD-deck-slug/
├── brief.md
├── content/
│   └── outline.md
├── assets/
│   └── assets_manifest.yml
├── data/
├── output/
│   ├── deck.html
│   └── screenshots/
└── notes/
    └── build-log.md
```

If a user provides existing materials, do not overwrite them. Copy or reference them from the deck folder and record them in `assets/assets_manifest.yml`.

## 1.9 Editable PPTX Discipline

Editable PPTX is fragile. Treat it as a component-driven export target, not as a freeform drawing surface.

- Every slide must be mapped to a component ID before PPTX generation; this is an internal build artifact, not a separate user approval step.
- Reuse the selected template file/package before inventing a layout. Do not build a new freeform script when a template exists.
- Fill the selected template from the confirmed note. If using a visual intermediate, it must come from the same template, not from a new design.
- Use named image slots and preserve image aspect ratios.
- Validate the PPTX package and visual constraints before delivery.
- If PowerPoint asks to repair the file, mark the build as failed and report the failing area.
## 1.10 Component Mapping Behavior

Component mapping belongs to the skill, not to the user conversation.

- Use the component registry and mapping heuristics automatically after content and page forms are confirmed.
- Do not ask the user to approve component IDs, slot IDs, or validation fields.
- Ask the user only when content, page form, factual assets, logo, IP character, or placeholder permission is missing.
- Keep any `component_map` as an internal construction sheet or build artifact.
- Report mapping as a concise build summary, not as a new confirmation gate.
## 1.11 Template And Text Lock

Editable PPTX generation is template filling, not redesign.

- Treat the selected template file/package as the highest visual authority.
- Treat the confirmed content/page-form note as the only source of visible slide text.
- Copy every visible word and punctuation mark from the confirmed note; do not rewrite during generation.
- Put construction notes, build warnings, file paths, component IDs, slot IDs, and placeholder explanations in logs or notes, not on the slide canvas.
- Use placeholder text only inside an image slot that will be covered by the replacement image.
- If a page has too little text for a large component, choose a smaller template variant or an image-led layout; do not leave “bathtub with two grapes” empty containers.
- For missing screenshots, show only minimal in-slot placeholder text, then keep the rest of the slide audience-facing.
## 1.12 Component Generator Discipline

For maintained editable PPTX visual systems, prefer the reusable component generator before writing any one-off deck script.

Use `scripts/build_deck.py` with a locked `deck_plan.json`:

```bash
python scripts/build_deck.py --plan path/to/deck_plan.json --out path/to/deck.pptx
```

Required behavior:

- The plan is the only visible-text source.
- Each page must declare a maintained component ID.
- The generator must print visible progress: `LOAD`, `CHECK`, `BUILD`, `RENDER`, `SAVE`, `VALIDATE`, `DONE`.
- If one page or component fails, report the exact page/component and continue only when the failure is safely skippable; do not disappear silently.
- Do not write a new 30-page hard-coded script when `build_deck.py` can consume a plan.
- Use `scripts/validate_deck.py` after generation.
- Use `scripts/diagnose_deck.py` after generation to catch component-quality issues such as excessive black blocks, too many text boxes, dense pages, sparse pages, and shape overload.

This is the default route for 双色独立刊物风 and future maintained template systems.
## Non-negotiable template rule

For PPTX generation with the duotone independent-zine visual system, do not freely redraw the deck.

Use the template package first:

- Read `references/duotone-zine-template-package.md` when this visual system is selected.
- Use `assets/templates/duotone-zine/component-library-v0.3.1.pptx` as the highest visual authority.
- Use `assets/templates/duotone-zine/component-library-source.py` to inspect exact geometry when generating native PPTX.
- Generation is template filling: choose an approved component variant, copy/reproduce its geometry, replace text/images/logo only.
- If a confirmed page cannot map to an approved component variant, stop and report the missing template variant. Do not improvise a new layout.
- Do not use arbitrary card spreading, arbitrary connector networks, oversized blank image placeholders, or construction notes on slide canvas.

PPT Master reference path: treat the workflow as a harness. The harness owns the route and constraints; the model supplies content judgment but must not bypass the template package.

