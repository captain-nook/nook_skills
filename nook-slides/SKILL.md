---
name: nook-slides
description: Create Chinese-first slide decks and editable PPTX plans through a strict template-filling workflow. Use whenever the user asks to make slides, PPT, presentation, deck, course slides, report slides, or to turn Markdown/notes/articles into slides. This skill must use the current three Chinese visual systems, locked visible copy, approved component schemas, and deterministic rendering; it must not free-design layouts.
---

# 1 nook-slides

This skill builds slide decks by filling approved templates. It is not a free-design slide generator.

The Agent may understand content, split pages, recommend page forms, choose approved components, fill schema fields, and run validation. The Agent must not choose coordinates, font sizes, colors, spacing, connectors, shadows, or ad-hoc layouts. Visual presentation belongs to maintained template packages and deterministic renderers.

## 1.1 Current Production Mode

Use this current mode before any older note, gallery, or process draft.

- Current visual systems are three Chinese systems only:
  - `duotone-zine` / 双色独立刊物风.
  - `oriental-dark-yaji` / 东方暗调雅集风.
  - `bright-street-dance` / 明亮街舞贴纸风.
- The old English theme gallery is retired from production triggering. Do not present it as a current choice.
- Current executable contract is `assets/schemas/deck-plan-v1.schema.json` plus `scripts/plan_contract.py`.
- Current interaction contract is `references/interaction-contract.md` plus `scripts/validate_interaction_state.py`.
- The top-level component contract is global and theme-independent. Every production visual system must implement the same 13 approved components with the same relative structural skeletons. A theme may change color, font choices, corner radius, line style, texture, image treatment, and decorative language; it must not add, remove, rename, or rearrange component slots.
- Theme component libraries for visual-system development must be generated from the `duotone-zine` component source by running `assets/templates/extract_duotone_component_skeleton.py`, then `assets/templates/generate_theme_component_libraries.py`. Do not hand-write the global skeleton or hand-draw a separate 13-page library for each theme.
- Real editable PPTX rendering currently uses the deterministic `duotone-zine` renderer in `scripts/build_deck.py`.
- `oriental-dark-yaji` and `bright-street-dance` may be used for schema planning and visual-system development only until their deterministic PPTX renderers are approved. If the user chooses one of them for final editable PPTX, stop and report the missing renderer.
- A generated deck is a fill-in-the-blanks artifact: final locked copy + selected visual system + approved component/variant + named slots.

## 1.2 Startup Self-Check

Before doing deck work, answer these internally. If any answer is unknown, read the referenced files before proceeding.

1. Visual systems: exactly three Chinese systems from `references/visual-systems.md`.
2. Component contract: approved `zine.*` components and variants from `assets/schemas/deck-plan-v1.schema.json` and `references/component-contract.md`.
3. Rendering mode: schema-only, sample review, or editable PPTX.
4. Renderer availability: editable PPTX is currently allowed only for `duotone-zine`.
5. Agent authority: content planning and schema filling only; no visual layout authority.
6. Interaction state: read `references/interaction-contract.md`; create or update `notes/interaction-state.json`; validate it with `scripts/validate_interaction_state.py` before every gate transition.
7. Question policy: default to choices, ask at most three intake questions per round, and do not ask a long open-ended briefing form.
8. Text lock: Gate 2 may micro-adjust visible copy for page-form fit; once Gate 2 is confirmed, visible text is locked for actual PPT production.

If a user asks for a one-shot final deck, still follow the gates unless they explicitly says to skip confirmation. If confirmation is skipped, write a prototype plan, mark `plan_status: "prototype"`, and do not claim the copy is accepted.

## 1.3 Production Workflow

Follow this sequence for every deck.

1. Read `references/workflow.md` and `references/interaction-contract.md`.
2. Collect source material, purpose, audience, target outcome, length, density, and available assets.
3. Create a project folder for the deck with `brief.md`, `content/`, `assets/`, `data/`, `output/`, and `notes/`.
4. Create `notes/interaction-state.json` from `assets/schemas/interaction-state-v1.schema.json` shape. Keep it current throughout the run.
5. Gate 1: draft-lock content. Confirm slide count and a first complete visible-copy draft.
6. Before leaving Gate 1, update `notes/interaction-state.json` and run `python scripts/validate_interaction_state.py path/to/notes/interaction-state.json`.
7. Gate 2: lock page form. First provide an agent-recommended default plan that can be accepted with one confirmation. If the user wants refinement, or says they are not satisfied and want to decide pages themselves, switch to choice-based decision cards. Ask at most four cards per round. Do not require row-by-row open-ended feedback. Page-form decisions may trigger local copy revisions.
8. Before leaving Gate 2, save `content/accepted-copy.md` and `content/visible-copy.json`, set `locks.text_locked: true` and `locks.locked_after_gate: "gate2_page_forms"` in `notes/interaction-state.json`, then validate it.
9. Gate 3: choose one of the three Chinese visual systems. Do not invent a style.
10. Before leaving Gate 3, update and validate `notes/interaction-state.json`; for editable PPTX, non-duotone themes must fail as blocked until their deterministic renderers are approved.
11. Gate 4: plan assets. Mark each screenshot, real image, chart, illustration, logo, and placeholder. Factual images such as software UI, product screenshots, real charts, logos, and evidence photos must use user-provided assets or approved placeholders. Decorative images such as covers, icons, abstract illustrations, and non-factual atmosphere images should be generated when the user has not provided better assets.
12. Before leaving Gate 4, update and validate `notes/interaction-state.json`.
13. Verify the Gate 2 text lock, update and validate `notes/interaction-state.json`, then fill `deck_plan.json` using only approved fields.
14. Run `python scripts/validate_plan.py path/to/deck_plan.json`.
15. For editable PPTX with `duotone-zine`, run `python scripts/build_deck.py --plan path/to/deck_plan.json --out path/to/deck.pptx`.
16. Run `scripts/validate_deck.py` and `scripts/diagnose_deck.py` after PPTX generation.
17. Deliver local paths and a concise build note. Report any missing renderer/template as a blocking issue, not as a design choice.

## 1.4 Hard Prohibitions

- Do not use retired English themes as current production choices.
- Do not free-design a slide.
- Do not generate coordinates, CSS layout rules, DrawingML geometry, font sizes, colors, shadows, connector paths, or spacing during deck generation.
- Do not create temporary components because a page is hard to fit.
- Do not treat a new visual system as a new component taxonomy. New themes skin the global 13 components; they do not invent theme-only components.
- Do not edit visible text after Gate 2 is confirmed. Gate 2 may micro-adjust copy before confirmation; after `locks.text_locked=true`, any text change reopens Gate 2 or Gate 1.
- Do not trim arrays, shorten confirmed copy, normalize punctuation, or switch variants silently to pass validation.
- Do not put construction notes, component IDs, slot IDs, file paths, warnings, or build labels on slide canvas.
- Do not fake factual screenshots, product UI, charts, logos, or brand evidence with AI images.
- Do not leave decorative image slots empty when the deck needs visual weight; generate non-factual decorative assets or ask for a different asset strategy.
- Do not claim `oriental-dark-yaji` or `bright-street-dance` editable PPTX is production-ready before their deterministic renderers exist.
- Do not make the user manage extra process review files just to approve gates; keep gate decisions in chat unless the artifact is part of the final build contract.
- Do not treat "continue", "继续", "可以", "好的", "差不多", or general encouragement as gate approval.
- Do not ask all intake questions at once. Ask at most three intake questions per round, prefer 2-4 choices, and use reasonable defaults when possible.
- Do not cross a gate without updating `notes/interaction-state.json` and passing `scripts/validate_interaction_state.py`.
- Do not infer confirmed workflow state from memory or chat if `notes/interaction-state.json` is missing or contradicts the chat.

## 1.5 Reference Loading

Load only what the current step requires.

- Always read `references/workflow.md` for deck work.
- Always read `references/interaction-contract.md` for deck work.
- Read `references/constraint-architecture.md` before changing or explaining constraints, schemas, rendering authority, or failure modes.
- Read `references/visual-systems.md` before discussing style choices.
- Read `references/component-contract.md` before content/page-form confirmation or schema filling.
- Read `references/template-driven-pptx.md` before any editable PPTX generation.
- Read `references/duotone-zine-data-contract.md` and `references/duotone-zine-component-registry.md` before creating a `duotone-zine` accepted plan.
- Read `references/validation-checklist.md` before final delivery.

## 1.6 Output Discipline

Use this folder shape for deck artifacts:

```text
YYMMDD-deck-slug/
├── brief.md
├── content/
│   ├── source.md
│   ├── accepted-copy.md
│   └── visible-copy.json
├── assets/
│   └── assets_manifest.yml
├── data/
│   └── deck_plan.json
├── output/
│   ├── deck.pptx
│   ├── deck-component-map.json
│   └── deck-build-log.md
└── notes/
    ├── interaction-state.json
    └── build-log.md
```

Accepted plans must include `content_lock` hashes from the final visible-copy lock. Prototype plans may omit them, but must not be presented as final accepted decks.
