# Workflow

Use this workflow for every `nook-slides` task.

The workflow is a controlled fill-in-the-blanks pipeline. The Agent helps decide content and page forms, then fills an approved schema. The renderer owns layout.

This workflow is governed by `references/interaction-contract.md`. Maintain `notes/interaction-state.json` throughout the run and validate it before every gate transition:

```bash
python scripts/validate_interaction_state.py path/to/notes/interaction-state.json
```

If the interaction state and chat history disagree, the state file wins until the user explicitly reconfirms the active gate.

## 1. Intake

Collect these items before planning:

1. Source material: Markdown, notes, article, outline, transcript, or topic.
2. Purpose: talk, course, report, proposal, demo, review, or social sharing.
3. Audience: team, boss, client, students, public, peers.
4. Desired outcome: understand, believe, decide, learn, or act.
5. Length: short 5-7, medium 8-12, long 13+.
6. Density: speaker-led or reading-first.
7. Assets: screenshots, logo, data, images, charts, brand colors, existing deck.
8. Delivery target: schema-only, prototype, sample review, or editable PPTX.

Prefer choices over open-ended questions. Ask open questions only for source material and special constraints.

Do not ask all eight intake items at once. Use `interaction_policy.max_intake_questions_per_round` from `notes/interaction-state.json`; the current maximum is 3 questions per round. Ask for source material openly only when it is missing. For purpose, audience, outcome, length, density, delivery target, and assets, use 2-4 choices and mark a recommended default.

If the user has provided enough context, infer defaults and continue. Record any active questions in `active_questions` and validate the state before moving to Gate 1.

## 2. Deck Folder

Create one standalone folder:

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
└── notes/
    ├── interaction-state.json
    └── build-log.md
```

Use the current date for `YYMMDD`. Use an English slug. Put the Chinese title in `brief.md`.

Initialize `notes/interaction-state.json` immediately after creating the folder. Use `assets/schemas/interaction-state-v1.schema.json` as the shape reference and `references/interaction-state.example.json` as a minimal example.

## 3. Gate 1: Draft Content Lock

The content gate confirms slide count and a first complete visible-copy draft.

Output for confirmation:

| Page | Page title | Visible copy | Visual carrier |
|---|---|---|---|

Rules:

- Confirm titles, body text, card text, labels, image placeholders, and punctuation.
- Keep visible text short. If the source is long, propose shorter copy before confirmation.
- If the user says "continue", "继续", "可以", "好的", or any non-specific approval after seeing a draft, ask a confirmation question instead of treating it as approval.
- Save draft copy notes when useful.
- Only the explicit approvals defined in `references/interaction-contract.md` confirm this gate.
- After confirmation, write every page into `notes/interaction-state.json` with `content_status: "confirmed"` and validate the state file.

After this gate, the deck has a complete copy draft. Gate 2 may still trigger local copy revisions when a page form needs cards, shorter labels, image placeholders, or different visible slots.

## 4. Gate 2: Page Form Lock

Use `references/component-contract.md`.

Gate 2 must minimize user typing.

Default path:

1. Recommend a complete page-form plan for the whole deck.
2. Mark low-risk pages as adopted by default.
3. Show only the pages that need judgment: multiple good forms, risky density, missing assets, or local copy changes.
4. Ask one confirmation question: accept the default plan, enter refinement, or name specific pages to adjust.
5. If the user says they are not satisfied, want control, or want to decide every page, enter full refinement. Do not ask them to write open-ended instructions for every page.

Refinement path:

1. Ask at most four decision cards per round.
2. Each decision card must be a multiple-choice question with 3-4 options.
3. Use a compact reply format such as `1A 2C 3A 4D`.
4. Avoid open-ended per-page feedback unless the user explicitly asks for it.
5. For long decks, only ask about pages that need human judgment; do not force the user to review every page.

Full refinement path:

1. Use when the user rejects the default plan or wants to decide every page.
2. Process the deck in batches of at most four pages.
3. For each page, provide 3-4 approved page-form choices and mark the recommendation.
4. After each batch, accept compact replies and continue to the next batch until all pages are decided.
5. If the user's choice requires visible-copy changes, collect those changes as local revisions after the page-form choice, not before.

Decision card format:

```text
1. P04 五层状态
推荐：5 卡片时间轴
A 保持推荐
B 层级堆叠
C 并列知识卡
D 拆成两页
```

Use natural Chinese page names for the user. Do not ask the user to approve component IDs or slot IDs.

When a table is useful, keep it short and use it as a summary, not as the main approval mechanism.

After the user confirms, map every page internally to:

```text
natural page form -> zine component -> approved variant -> schema fields
```

If no approved component or variant fits, stop and report the missing template. Do not invent a new page.

If this gate changes visible text, show the affected pages again and ask the user to confirm those local revisions. Do not restart the whole workflow.

Gate 2 is the final visible-copy adjustment point. Micro-edits are allowed only before Gate 2 confirmation and only when needed for the selected page form. After Gate 2 confirmation, later steps must not edit visible text.

Before leaving this gate, write each page form into `notes/interaction-state.json`:

```text
natural_form -> component -> variant -> status confirmed
```

Clear `pending_decision_cards`, then validate the state file.

Also create the production text lock before leaving Gate 2:

- Save `content/accepted-copy.md`.
- Save `content/visible-copy.json`.
- Write `locks.text_locked: true`.
- Write `locks.locked_after_gate: "gate2_page_forms"`.
- Write `locks.accepted_copy_path`, `locks.visible_copy_path`, and `locks.approved_at`.
- Validate `notes/interaction-state.json`.

## 5. Gate 3: Visual System

Use `references/visual-systems.md`.

Ask the user to choose one of:

1. 双色独立刊物风.
2. 东方暗调雅集风.
3. 明亮街舞贴纸风.

State renderer availability:

- 双色独立刊物风 can produce editable PPTX.
- 东方暗调雅集风 and 明亮街舞贴纸风 are allowed for schema planning/prototype work until deterministic renderers are approved.

Do not present retired English themes.

Before leaving this gate, write `visual_system.theme`, `visual_system.status`, and `visual_system.renderer_status` into `notes/interaction-state.json`, then validate the state file. For `editable-pptx`, the validator must block `oriental-dark-yaji` and `bright-street-dance` until deterministic renderers are approved.

Do not edit visible text in this gate. If the chosen visual system makes the text unsuitable, reopen Gate 2.

## 6. Gate 4: Asset Plan

Create or update `assets/assets_manifest.yml`.

Asset strategy:

1. Factual images use placeholders unless the user provides real files. This includes software UI, product screenshots, real charts, logos, maps, dashboards, documents, and evidence photos.
2. Do not generate fake factual screenshots, fake product interfaces, fake charts, fake maps, fake logos, or fake evidence.
3. Decorative images should be generated when useful. This includes cover visuals, abstract illustrations, mood images, icons, non-factual case illustrations, and atmosphere images.
4. A slide deck should keep enough visual weight. Do not remove images only to make asset handling easier.
5. Placeholder labels must be short and slide-safe. Put replacement instructions in the asset manifest or build log, not on the slide canvas.

For each asset, record:

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
  decision:
```

Rules:

- Use real screenshots, real charts, real product images, and official/user-provided logos when they prove factual claims.
- Use AI-generated images only for non-text illustrations, atmosphere, or non-factual visual support.
- Missing factual evidence stays as an approved image-slot placeholder.
- Do not put construction warnings on the slide canvas.

Before leaving this gate, write `assets.status: "confirmed"` and every asset decision into `notes/interaction-state.json`, then validate the state file. A factual asset with `source: ai_generated` must fail validation.

Do not edit visible text in this gate. If an asset decision requires a wording change, reopen Gate 2.

## 7. Build `deck_plan.json`

Build `data/deck_plan.json` from the confirmed gates.

Before writing the plan, verify the Gate 2 visible-copy lock:

- `content/accepted-copy.md` already exists.
- `content/visible-copy.json` already exists.
- `notes/interaction-state.json` has `locks.text_locked: true`.
- Include hashes of both files in accepted `deck_plan.json` as `content_lock`.
- Validate `notes/interaction-state.json`.

Rules:

- Use only approved `theme` values.
- Use only approved `component` and `variant` values.
- Use only schema fields.
- Include `visual_carrier`.
- Include `content_lock` for accepted final plans.
- Do not normalize punctuation or rewrite confirmed copy.

Validate before rendering:

```bash
python scripts/validate_plan.py path/to/deck_plan.json
```

If validation fails, fix the plan or reopen the appropriate gate. Do not bypass validation.

## 8. Render

For editable PPTX with 双色独立刊物风:

```bash
python scripts/build_deck.py --plan path/to/deck_plan.json --out path/to/output/deck.pptx
python scripts/validate_deck.py path/to/output/deck.pptx
python scripts/diagnose_deck.py path/to/output/deck.pptx
```

For 东方暗调雅集风 or 明亮街舞贴纸风:

- Stop before editable PPTX generation unless an approved renderer exists.
- Deliver schema/prototype outputs only if the user approved that target.
- Do not write a one-off renderer to make the run look successful.

## 9. Delivery

Deliver:

1. Local path to `deck_plan.json`.
2. Local path to generated PPTX when available.
3. Component-map/build-log paths when generated.
4. Validation result.
5. Any blocked renderer or missing-template issue.

Keep the summary short. The user cares whether the deck is generated, where it is, and whether constraints were respected.
