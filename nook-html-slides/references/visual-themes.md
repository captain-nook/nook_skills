# Visual Themes

These are v0 themes for `nook-html-slides`. They are deliberately minimal and can evolve.

## Shared Rules

- Titles never wrap.
- Slides are word-light and visual-heavy.
- Theme is not just color. Theme must define layout, visual carrier, spacing, type, and component grammar.
- Color is a token layer. Replace accent color with brand color when appropriate.
- Do not use generic purple-blue gradients, decorative blobs, full-page text, or meaningless card grids.
- Always show themes visually before asking a new user to choose. A name and text description are not enough.
- Use the maintained theme gallery in `assets/theme-gallery/`; do not generate new theme previews per deck unless the user is creating or testing a new theme candidate.
- Palette options live in `references/theme-system.md`.

## Fixed Gallery Requirement

The published skill must include a fixed visual gallery with one cover sample and one inner-page sample per theme:

1. Minimal Keynote.
2. Calm Strategy.
3. Research Brief.
4. Product Tutorial.
5. Pitch Proposal.

Location:

```text
assets/theme-gallery/index.html
assets/theme-gallery/palette-options.html
assets/theme-gallery/theme-gallery-fullpage.png
```

If a theme changes, update this gallery and capture a new screenshot. Deck tasks should consume this asset, not recreate it.

## 1. Minimal Keynote

Use for product launches, key ideas, concepts, and keynote-style talks.

Design:

- Large whitespace.
- Single hero visual.
- One-line title.
- Few or no cards.
- Black/white/gray plus one accent.

Tokens:

```css
--bg: #f7f7f5;
--text: #111111;
--muted: #737373;
--accent: #0071e3;
--surface: #ffffff;
```

Typography:

- Display: Noto Sans SC / Alibaba PuHuiTi / HarmonyOS Sans SC, 700.
- Body: Noto Sans SC, 400.
- Title size around 88-112px on 1920 x 1080.

Components:

- `HeroObject`
- `OneLineTitle`
- `QuietSubtitle`
- `MiniMeta`

Avoid dense lists, many cards, decorative icons, and fake premium gradients.

## 2. Calm Strategy

Use for executive reports, management decisions, project reviews, and strategy briefings.

Design:

- Warm cream canvas.
- Single accent color.
- Metric cards, roadmap, decision cards.
- Soft tinted cards with quiet borders.

Tokens:

```css
--bg: #fdfae7;
--text: #111111;
--muted: #6b6b6b;
--hint: #9a9a9a;
--accent: #1e2bfa;
--accent-08: rgba(30, 43, 250, 0.08);
--accent-20: rgba(30, 43, 250, 0.20);
```

Typography:

- Display: Noto Sans SC / HarmonyOS Sans SC, 700.
- Body: Noto Serif SC or Noto Sans SC, 400.
- Metric: Noto Sans SC, 700.

Components:

- `DecisionHeadline`
- `MetricCard`
- `Roadmap`
- `PriorityMatrix`
- `DecisionCard`

Avoid marketing poster energy, business-blue templates, and unexplained data dumps.

## 3. Research Brief

Use for industry research, trend analysis, competitor analysis, and data reports.

Design:

- Chart or table is the main visual.
- Visible or subtle grid.
- Two-color or monochrome palette.
- Source and data scope visible but quiet.

Tokens:

```css
--bg: #f0ebde;
--text: #1f2be0;
--grid: rgba(31, 43, 224, 0.10);
--line: rgba(31, 43, 224, 0.18);
--accent: #1f2be0;
```

Alternative:

```css
--bg: #fafadf;
--text: #1a1a16;
--muted: #5e5e54;
--hint: #8a8a80;
--line: #1a1a16;
```

Typography:

- Display: Noto Serif SC / Source Han Serif SC, 700.
- Body: Noto Sans SC, 400.
- Mono/source: JetBrains Mono / DM Mono.

Components:

- `ResearchHeadline`
- `HeroMetric`
- `EvidenceChart`
- `SourceCaption`
- `TrendIndex`
- `DataLedger`

Avoid unsourced fake charts, multi-color dashboard clutter, and decorative data.

## 4. Product Tutorial

Use for software tutorials, workflows, tools, and step-by-step teaching.

Design:

- Real screenshot dominates the page.
- Steps and callouts are secondary.
- Low-distraction background.
- Clear numbered flow.

Tokens:

```css
--bg: #f8fafc;
--surface: #ffffff;
--text: #0f172a;
--muted: #64748b;
--line: #dce3ee;
--accent: #2563eb;
--accent-soft: rgba(37, 99, 235, 0.10);
--success: #10b981;
--warning: #f59e0b;
```

Typography:

- Display/body: Noto Sans SC / HarmonyOS Sans SC.
- Mono: JetBrains Mono.

Components:

- `ScreenshotFrame`
- `StepDots`
- `CalloutPin`
- `FocusBox`
- `BeforeAfter`
- `ActionResult`

Avoid fake UI, tiny screenshots, long step paragraphs, and too many arrows.

## 5. Pitch Proposal

Use for pitches, proposals, business plans, funding decks, and resource requests.

Design:

- Strong grid.
- One signal color.
- Problem-solution-evidence-action flow.
- Big numbers and strong section pages.

Tokens:

```css
--bg: #ecece8;
--paper: #f5f4ef;
--ink: #0a0a0a;
--accent: #e6ff3d;
--muted: #8a8a85;
```

Alternative:

```css
--bg: #ffffff;
--paper: #f5f2ef;
--ink: #1c1410;
--accent: #d8000f;
```

Typography:

- Display: Noto Sans SC / Alibaba PuHuiTi, 900.
- Body: Noto Sans SC, 400.
- Mono: JetBrains Mono for labels and page numbers.

Components:

- `ProblemPanel`
- `SolutionPanel`
- `EvidencePanel`
- `ActionPanel`
- `HeroStat`
- `MarketMap`
- `MilestoneGrid`

Avoid empty vision slides, unsupported claims, and making every page a loud poster.
