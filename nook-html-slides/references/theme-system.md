# Theme System

This file is the stable visual theme registry for `nook-html-slides`.

Do not reinvent visual themes during a deck task. Maintain themes here and in `assets/theme-gallery/`.

Current status: **draft registry, not a finished design standard**.

Important correction:

- The five theme directions come from the project design contract and prior reference analysis.
- The first palette of each theme is source-backed by the existing design contract.
- Extra palette variants are only candidates until they are reviewed against reference systems and captured in the gallery.
- Do not present unreviewed candidate palettes as final visual standards.

## 1. Visual Assets

The fixed theme gallery lives here:

```text
assets/theme-gallery/
├── index.html
├── palette-options.html
└── theme-gallery-fullpage.png
```

Use these assets when entering the visual selection step. The gallery shows each theme with a cover sample and an inner-page sample. The palette page is a review surface for color options, not proof that all palettes are final.

If the user asks to change, add, or remove visual themes, update this theme system and the gallery assets. Do not patch the task workflow just to adjust aesthetics.

## 2. Selection Flow

When choosing visuals for a deck:

1. Show the 5 fixed themes from `assets/theme-gallery/`.
2. Ask the user to choose one theme.
3. After the theme is chosen, show the color options for that theme.
4. Ask the user to choose one palette or provide a brand color.
5. Only then generate the accepted deck.

Do not choose the theme or palette by default unless the user explicitly asks the agent to decide.

## 3. Provenance

The current five themes are based on:

| Theme | Primary references already recorded in project contract | What was borrowed |
|---|---|---|
| Minimal Keynote | `nook-xhsdesign` minimal keynote direction; Frontend Slides `Studio/design.md`; Frontend Slides style presets such as Swiss Modern / Electric Studio | whitespace, single hero visual, one-line title, restrained element count |
| Calm Strategy | Frontend Slides `Blue Professional/design.md`; Frontend Slides `Signal/design.md`; `nook-PPTdesign` component/token method | cream canvas, single accent color, decision cards, roadmap, metric cards |
| Research Brief | Frontend Slides `Cobalt Grid/design.md`; Frontend Slides `Monochrome/design.md`; `nook-xhsdesign` data visualization direction | grid, two-color/monochrome report feel, chart-led pages, source captions |
| Product Tutorial | `nook-xhsdesign` step breakdown and screenshot annotation directions; Frontend Slides Notebook/Pastel organization patterns; Blue Professional soft cards | screenshot-first page, step markers, callout pins, low-distraction teaching layout |
| Pitch Proposal | Frontend Slides `Neo-Grid Bold/design.md`; `Bold Poster/design.md`; `Studio/design.md`; `nook-xhsdesign` business proposal direction | strong grid, signal color, problem-solution-evidence-action rhythm, hero stats |

Before this registry is treated as production-ready, each theme needs:

1. Source-backed design rationale.
2. Accepted cover and inner-page samples.
3. Accepted palette tokens.
4. Negative examples and anti-pattern checks.
5. Browser screenshots and visual review notes.

## 4. Themes And Palette Options

### Minimal Keynote

Use for product launches, keynote ideas, concept talks, and low-density model explanations.

| Option | Status | Background | Text | Accent | Provenance |
|---|---|---|---|---|---|
| MK-01 Classic Blue | accepted draft | `#f7f7f5` | `#111111` | `#0071e3` | From `260623主题设计系统合同.md` Minimal Keynote tokens |
| MK-02 Graphite | candidate | `#f5f5f2` | `#0f0f0f` | `#3f3f46` | Needs reference-backed review |
| MK-03 Warm Signal | candidate | `#fbfaf4` | `#111111` | `#d97706` | Needs reference-backed review |

### Calm Strategy

Use for executive reports, management decisions, project reviews, and strategy briefings.

| Option | Status | Background | Text | Accent | Provenance |
|---|---|---|---|---|---|
| CS-01 Cobalt Cream | accepted draft | `#fdfae7` | `#111111` | `#1e2bfa` | From `260623主题设计系统合同.md` Calm Strategy tokens |
| CS-02 Forest Cream | candidate | `#fbf8ea` | `#161616` | `#0f766e` | Needs reference-backed review |
| CS-03 Burgundy Memo | candidate | `#fbf5ee` | `#17110f` | `#9f1239` | Needs reference-backed review |

### Research Brief

Use for industry research, trend analysis, competitor analysis, and evidence-led arguments.

| Option | Status | Background | Text | Accent | Provenance |
|---|---|---|---|---|---|
| RB-01 Cobalt Grid | accepted draft | `#f0ebde` | `#1f2be0` | `#1f2be0` | From `260623主题设计系统合同.md` Research Brief cobalt tokens |
| RB-02 Monochrome Paper | accepted draft | `#fafadf` | `#1a1a16` | `#1a1a16` | From `260623主题设计系统合同.md` Research Brief monochrome alternative |
| RB-03 Ink Green | candidate | `#f3f1e6` | `#12312b` | `#0f766e` | Needs reference-backed review |

### Product Tutorial

Use for software tutorials, workflows, tool teaching, and step-by-step demonstrations.

| Option | Status | Background | Text | Accent | Provenance |
|---|---|---|---|---|---|
| PT-01 Clear Blue | accepted draft | `#f8fafc` | `#0f172a` | `#2563eb` | From `260623主题设计系统合同.md` Product Tutorial tokens |
| PT-02 Mint Guide | candidate | `#f6fbf8` | `#10231f` | `#10b981` | Needs reference-backed review |
| PT-03 Amber Coach | candidate | `#fffaf2` | `#1f1710` | `#f59e0b` | Needs reference-backed review |

### Pitch Proposal

Use for pitches, proposals, business plans, resource requests, and action-oriented decks.

| Option | Status | Background | Text | Accent | Provenance |
|---|---|---|---|---|---|
| PP-01 Signal Lime | accepted draft | `#ecece8` | `#0a0a0a` | `#e6ff3d` | From `260623主题设计系统合同.md` Pitch Proposal default tokens |
| PP-02 Warm Red | accepted draft | `#ffffff` | `#1c1410` | `#d8000f` | From `260623主题设计系统合同.md` Pitch Proposal warm red alternative |
| PP-03 Electric Blue | candidate | `#f4f5f7` | `#0a0a0a` | `#2563eb` | Needs reference-backed review |

## 5. Maintenance Rules

- A theme is not accepted until it has at least one cover sample and one inner-page sample.
- A palette is not accepted until it has background, text, muted, line/surface, accent tokens, provenance, and gallery preview.
- Theme changes should update `assets/theme-gallery/index.html` and capture a new gallery screenshot.
- Palette changes should update `assets/theme-gallery/palette-options.html`.
- Keep theme names stable so old deck briefs remain meaningful.
- Do not add one-off visual styles inside individual deck projects unless the user is explicitly exploring a new theme candidate.
- Never present candidate palettes as final choices without saying they are candidates.
