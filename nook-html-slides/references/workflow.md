# Workflow

Use this workflow for every new HTML slide deck.

For formal PPTX, editable decks, or long decks, also read `ppt-preflight.md` before generation. The extra gates there override any temptation to move straight from material to finished deck.

## 1. Context

Collect these answers together when possible:

1. Purpose: pitch deck / tutorial / strategy report / research brief / conference talk / internal presentation.
2. Audience: boss / team / client / students / public / peers.
3. Desired outcome: understand / believe / decide / learn / act.
4. Length: short 5-10 / medium 10-20 / long 20+.
5. Density: speaker-led / reading-first.
6. Content status: all content ready / rough notes / topic only.
7. Assets: screenshots, logo, data, images, charts, brand colors, existing PPT or article.

Prefer choices over open questions. Use open input only for source material and special constraints.

## 2. Deck Folder

Create a standalone deck folder:

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

Use the current date for `YYMMDD`. Use an English slug. Put the Chinese title in `brief.md`.

## 3. Fact And Asset Check

Before writing slides:

- Identify time-sensitive facts, data, companies, products, policies, prices, market shares, people, and claims that need sources.
- Use browsing when information may be current, high stakes, or source-specific.
- List uncertain claims before generating final slide content.
- Record important assets in `assets/assets_manifest.yml`.
- Use official or user-provided logos and product screenshots when possible.
- Do not use AI images to replace real product UI, brand evidence, or factual evidence.

First version manifest fields:

```yaml
- asset_id:
  asset_type:
  intended_slide:
  role:
  source:
  source_priority:
  rights_note:
  needs_verification:
  visual_fit:
  style_notes:
  decision:
```

## 4. Content Plan

Produce:

- Core judgment.
- Narrative line.
- Suggested slide count.
- Slide-by-slide main message.
- Short one-line title per slide.
- Visual role for each slide: screenshot / chart / diagram / photo / main visual / text-only statement.
- Recommended presentation form for each slide when the deck is formal, long, or intended as editable PPTX.

Rules:

- One slide, one main message.
- Titles never wrap. Rewrite long titles.
- Main slides stay word-light and visual-heavy.
- Long explanations go into notes, comments, appendix, or `content/outline.md`.

Ask for user confirmation before generating the full deck.

For long decks, confirm by page group first, then expand to slide-level details. Do not ask the user to approve 20-30 pages in one undifferentiated table.

Hard gate:

- If the user says "continue", "go on", "下一步", or similar after the outline, do not interpret it as approval.
- Respond with a confirmation question that includes the proposed slide count and visible on-slide copy.
- Do not create the accepted `output/deck.html` or PPTX until the user approves the content gate or explicitly says to skip confirmation.

## 4.5 Page Form Plan

For formal PPTX, editable decks, or long decks, confirm page forms after content and before generation.

Do this as a guided interaction, not as hidden model judgment.

For each slide, provide:

1. Recommended component or presentation form.
2. Reason for the recommendation.
3. Two alternatives.
4. Required assets or screenshots.
5. User decision.

Prefer grouped confirmation for long decks:

1. Confirm section structure first.
2. Confirm one page group at a time.
3. Confirm slide-level forms inside that group.
4. Generate only after the group or full deck is approved, depending on the user's intent.

Use the maintained component library when possible. If no component fits, propose a new component before building the deck.

Use choice-style prompts when asking about forms. Example:

| Slide | Recommended form | Why | Alternatives | Assets needed |
|---|---|---|---|---|
| Five-layer model | Timeline-like hierarchy | The point is progression, not only stack order | Pyramid; five cards | One overview illustration |
| Xinjiang case layer 1 | Screenshot-led evidence page | The real chat is the proof | Image-text page; process cards | Doubao chat screenshot |

If the user chooses a different form, follow the user's decision and update the page plan.

If a case is the climax of the deck, expand it into a page group instead of compressing it into one slide. For example, a five-layer Xinjiang roadtrip case may need one opener, one or more pages per layer, and a result page with real screenshots such as chat, map, Obsidian, and agent workflow evidence.

## 5. Visual Theme And Palette

Use the maintained visual theme assets. Do not generate new theme options for every deck.

Show the fixed gallery:

```text
assets/theme-gallery/index.html
assets/theme-gallery/palette-options.html
assets/theme-gallery/theme-gallery-fullpage.png
```

The gallery shows all 5 default themes:

1. Minimal Keynote.
2. Calm Strategy.
3. Research Brief.
4. Product Tutorial.
5. Pitch Proposal.

After presenting the gallery, recommend suitable directions based on purpose, audience, density, asset state, and desired outcome.

Ask the user to pick one theme or identify elements to mix.

After the theme is chosen, show the maintained palette options from `assets/theme-gallery/palette-options.html` and `references/theme-system.md`. Ask the user to choose one palette or provide a brand color.

Hard gate:

- Do not choose a default visual theme for the user.
- Do not treat text-only theme descriptions as enough for first-time users.
- Do not choose a default palette for the user.
- Do not generate the accepted `output/deck.html` until the user confirms the visual direction.
- If the gallery or palette registry needs improvement, update the theme assets and `references/theme-system.md`; do not patch the whole workflow.

## 6. Enhancement Plan

Before generating the deck, decide:

- Which slides need real screenshots or product images.
- Which slides need user-provided screenshots, stickers, photos, maps, software UI, Obsidian views, or agent logs.
- Which slides need charts and data.
- Which slides can use AI-generated non-text visuals.
- Which slides need motion.
- Which slides should stay simple.

Do not add visuals just to decorate. Every visual must clarify, prove, or focus the message.

Keep factual screenshots faithful. Frame, crop, annotate, or mask private details, but do not replace real UI evidence with AI-generated images. Logo stays original and small. IP characters must be user-provided and style-transferred before use.

Also state whether Open Design will be used:

- `Open Design: yes` means the user approved using Open Design and the available command/handoff path is recorded.
- `Open Design: no` means the current deliverable will be a local HTML deck generated directly in the project.
- `Open Design: unknown` means pause and ask before implying any Open Design involvement.

## 7. HTML Deck

Generate `output/deck.html`.

Minimum requirements:

- Fixed 16:9 stage.
- Self-contained HTML where practical.
- Inline CSS and JS for v0.
- Theme tokens in `:root`.
- Keyboard navigation.
- No scrolling inside slides.
- No title wrapping.
- No overlapping elements.

Use HTML comments for speaker notes or implementation notes, not visible slide text.

## 8. Validate

Run visual and structural checks before delivery. Use `references/validation-checklist.md`.

If browser automation is available, screenshot at desktop and one smaller viewport. If not available, still inspect DOM/CSS and clearly state the limitation.

Fix issues before final delivery.
