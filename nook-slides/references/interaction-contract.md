# Interaction Contract

This contract makes the slide workflow portable across agents and computers. Every agent must externalize the workflow state into the deck project folder, then validate that state before moving to the next gate.

## 1. State File

Create and maintain this file from the first deck response after intake:

```text
notes/interaction-state.json
```

The state file is the authority for the current gate, confirmed decisions, pending decision cards, and renderer target. Chat history is only supporting context. If a new agent joins later, it must read `notes/interaction-state.json` before continuing.

Every state file must include this policy:

```json
{
  "interaction_policy": {
    "default_to_choices": true,
    "max_intake_questions_per_round": 3,
    "max_decision_cards_per_round": 4,
    "source_material_open_allowed": true,
    "text_lock_after_gate": "gate2_page_forms"
  }
}
```

Validate before every gate transition:

```bash
python scripts/validate_interaction_state.py path/to/notes/interaction-state.json
```

If validation fails, do not advance. Fix the state or reopen the relevant gate.

## 2. Gate Order

The only allowed order is:

```text
intake
-> gate1_content
-> gate2_page_forms
-> gate3_visual_system
-> gate4_assets
-> final_lock
-> plan_built
-> rendered
-> delivered
```

An agent may stay inside a gate, reopen the current gate, or mark a gate blocked. It must not skip ahead because the user said "继续", "可以", "好的", "差不多", or gave general encouragement.

Gate 2 is the last place where visible copy may be micro-adjusted. Once Gate 2 is confirmed, write the text lock to `locks` and do not change visible text during visual-system choice, asset planning, deck-plan creation, rendering, or diagnostics. If later text changes are required, reopen Gate 2 or Gate 1; do not patch text in the production path.

## 3. Question Policy

Default to choices.

Rules:

- Do not ask eight intake questions at once.
- Ask at most three intake questions per round.
- Ask one open source-material question only when the user has not provided the material.
- For purpose, audience, outcome, length, density, delivery target, and asset strategy, offer 2-4 choices with a recommended default.
- If enough information can be reasonably inferred, state the default assumption and move forward instead of asking.
- Record active questions in `active_questions` before asking; validate the state before moving on.
- Ask exactly one confirmation question at the end of each gate output.

Allowed intake question shape:

```text
我先按默认方案推进，缺口只确认这 3 项：

1. 用途
A 培训课件（推荐）
B 汇报
C 方案说明

2. 篇幅
A 8-12 页（推荐）
B 5-7 页
C 13 页以上

3. 交付
A editable PPTX（推荐，默认 双色独立刊物风）
B schema/prototype
```

Do not ask the user to fill a long briefing form.

## 4. Approval Rules

Only explicit approval for the active gate counts.

Accepted Chinese approvals:

- Gate 1: `确认内容`, `内容确认`, `确认这一版文案`.
- Gate 2: `确认页面形式`, `确认版式方案`, `按这个页面形式`, `页面形式确认并锁定文字`.
- Gate 3: `确认视觉系统`, `就选双色独立刊物风`, `就选东方暗调雅集风`, `就选明亮街舞贴纸风`.
- Gate 4: `确认资产计划`, `资产计划确认`.
- Final lock: `最终确认`, `锁定最终文案`, `可以生成最终 deck_plan`.

Non-approval phrases:

- `继续`
- `可以`
- `好的`
- `嗯`
- `差不多`
- `先这样`
- `你看着办`

When the user uses a non-approval phrase after a draft, ask one narrow confirmation question instead of advancing.

## 5. Response Parsing

Decision cards are the only place where compact replies are allowed.

Rules:

- Accept `1A 2C 3A 4D` only when active cards with IDs `1`, `2`, `3`, `4` exist in `pending_decision_cards`.
- Reject answers that reference missing card IDs or option letters.
- If the user gives prose plus card choices, apply the card choices only when every active card is answered unambiguously.
- If the user says "重做", "不满意", or "不像填空题", mark the active gate `in_progress`, keep prior choices as superseded history, and present a corrected fill-in decision path.
- If Gate 2 has already been confirmed and the user asks for visible-copy changes, reopen Gate 2 or Gate 1 before changing text.

## 6. Gate Output Templates

Gate 1 content confirmation:

```text
| Page | Page title | Visible copy | Visual carrier |
|---|---|---|---|
```

End with exactly one question:

```text
请回复“确认内容”，或指出要改的页码。
```

Gate 2 default page-form plan:

```text
| Page | Natural page form | Why this form | Needs decision |
|---|---|---|---|
```

End with exactly one question:

```text
请回复“页面形式确认并锁定文字”，或回复“进入选择题”让我逐页给 3-4 个选项。
```

Gate 2 decision card:

```text
1. P04 页面标题
推荐：自然页型
A 保持推荐
B 另一个已批准页型
C 另一个已批准页型
D 拆成两页
```

Gate 3 visual system choice:

```text
1. 双色独立刊物风：editable PPTX renderer available
2. 东方暗调雅集风：schema/prototype only until renderer approval
3. 明亮街舞贴纸风：schema/prototype only until renderer approval
```

Gate 4 asset plan:

```text
| Asset | Slide | Type | Source | Decision |
|---|---|---|---|---|
```

## 7. Text Lock

Gate 1 confirms a complete visible-copy draft. Gate 2 may make explicit micro-edits only to fit the selected page form, such as shorter labels, card splits, image placeholders, or page splits.

When Gate 2 is confirmed:

- Save `content/accepted-copy.md`.
- Save `content/visible-copy.json`.
- Write these fields into `notes/interaction-state.json`:

```json
{
  "locks": {
    "text_locked": true,
    "locked_after_gate": "gate2_page_forms",
    "accepted_copy_path": "content/accepted-copy.md",
    "visible_copy_path": "content/visible-copy.json",
    "approved_at": "YYYY-MM-DDTHH:MM:SS+08:00"
  }
}
```

After that point, no later step may edit visible text. Rendering must fail or reopen the proper gate instead of silently changing text.

## 8. Fill-In Discipline

The agent may recommend content, page forms, and asset decisions, but final production must be expressed as filled fields:

```text
confirmed copy -> natural page form -> approved component -> approved variant -> named schema fields
```

If no approved component or variant fits, stop and report the missing template. Do not invent a new component, one-off renderer, ad-hoc CSS, or slide layout.

## 9. Portability Invariant

A deck project is resumable only when these files exist or are intentionally pending in `interaction-state.json`:

- `brief.md`
- `content/source.md`
- `content/accepted-copy.md`
- `content/visible-copy.json`
- `assets/assets_manifest.yml`
- `data/deck_plan.json`
- `notes/interaction-state.json`
- `notes/build-log.md`

If any required file is missing for a confirmed gate, reopen that gate or mark the workflow blocked. Do not infer confirmed state from memory.
