# Interaction Protocol

Version: v0.2  
Updated: 2026-05-21  
Purpose: define how Codex should interact with the user whenever nook-card is triggered.

## Three Big Steps

The whole workflow has three major steps:

1. Production intent
2. Card assets
3. Motion video

The third step is optional. If the user only wants static cards, stop after the card assets are confirmed and exported.

## Always Ask First & Execution Intercept Lock

> [!CAUTION]
> ### 🛑 LLM RUNTIME GUARDRAIL & SOFT-LOCK
> Whenever `nook-card` is triggered, the AI agent is strictly bound to `STATE: REQUIREMENT_GATHERING`.
> - **The Intercept Gate**: In the first turn of any session, **DO NOT** execute any card specs, **DO NOT** invoke design renderers, and **DO NOT** silently output finished designs. You are soft-locked from code execution.
> - **Sole Output**: You must ONLY output the **Stage 1 Step-by-Step Multiple Choice** template defined in `SKILL.md`. Absolutely **DO NOT** output large layout tables, design specs, or multi-card copy details yet. Keep the interaction to a single simple A/B choice.
> - **Penalty**: Any attempt to bypass this progressive gate or auto-generate visual assets/specs in the first turn without explicit user confirmation is considered a fatal operational failure.

Do not silently choose style, motion, text hierarchy, or output type when the user expects collaboration.

## User-Facing Input Model

Keep the interaction simple. The workflow is staged, not mixed.

In the production-intent stage, the user chooses:

1. static-only or motion-ready
2. video/stage canvas if motion is possible

In the card-asset stage, the user only needs to provide:

1. Which card style?
2. Concrete card requirements?

For static card:

```text
风格：使用哪个 card style？
具体要求：主题、文案、卡片数量、拆卡方式、卡片自身比例、按钮、重点字、输出用途等。
```

If motion-ready assets are requested or likely, Codex must confirm card asset ratio and transparent output before rendering final card assets.

After the card assets are confirmed, Codex asks whether to enter the motion stage. Only if the user says yes, the user provides:

1. Which motion preset?
2. Concrete motion requirements?

```text
动效：使用哪个 motion preset？
具体要求：时长、节奏、是否退场、是否配音/字幕/音效、平台用途等。
```

## Production Intent Questions

Ask as step-by-step choices, not open-ended prompts.

P0 questions:

- 这次只要静态卡，还是后续可能进入动效？
- 如果可能进入动效，视频/舞台画幅是什么？默认横屏 `1920 x 1080`，竖屏 `1080 x 1920` 可选。
- 静态成果要哪一种输出？
  - `transparent_asset`: 透明背景卡片资产，用于 Remotion/PR 合成。
  - `preview_composite`: 带背景预览图，只用于人眼检查。
  - `both`: 同时输出，推荐用于可能进入动效的任务。

## Card Asset Questions

Ask only what is missing.

P0 questions:

- 用哪个风格？If unspecified, offer the default style.
- 卡片自身比例是什么？Do not assume it is the same as the video/stage canvas.
- 做几张卡片？如果内容天然有步骤、分类、清单或章节，必须先确认拆卡方式，不能默认压成一张总览卡。
- 这张卡片要表达什么？如果用户给了笔记，Codex 先提出拆卡方案。
- 文字内容如何处理？哪些必须原样保留，哪些允许 Codex 压缩改写？

P1 questions:

- 卡片数量是多少？如果内容天然分步骤，Codex 可以建议数量。
- 主标题是什么？
- 哪些字必须大？哪些字可以小？
- 是否需要按钮？几个按钮？按钮文案是什么？

P2 questions:

- 是否需要编号？
- 是否需要标签、注释、鼠标、代码面板等语境元素？
- 文案是否允许 Codex 改写？

## Static Card Minimal Confirmation

Before rendering card assets, Codex should confirm no more than these eight items:

1. `style_id`: default `tactile_soft_skeuomorphic_card`.
2. `production_intent`: `static_only`, `motion_ready`, or `static_plus_motion`.
3. `stage_canvas`: default landscape `1920 x 1080` when motion is possible.
4. `card_asset_ratio`: independent card shape, such as portrait card on landscape stage.
5. `output_layers`: `transparent_asset`, `preview_composite`, or `both`.
6. `card_count`: one card or a sequence; for structured content, confirm the split before rendering.
7. `copy_policy`: exact text, rewrite allowed, or mixed.
8. `hierarchy_buttons_labels`: key hierarchy and whether buttons/labels are needed.

Do not ask the user about token-level style details such as exact radius, shadow offset, dot size, font file, or color hex unless the user asks.

## Motion Video Questions

Only ask these after the static card is accepted or the user explicitly asks for video.

P0 questions:

- 用哪个动效？
- 目标平台或用途是什么？
- 默认横屏 `1920 x 1080`，是否需要竖屏 `1080 x 1920`？
- 默认主交付为 MOV / ProRes 4444 / alpha，是否需要额外 WebM 预览？

P1 questions:

- 是否有口播或目标口播时长？如果有，视频时长默认跟随口播。
- 是否要退场？
- 是否需要字幕、旁白或音效？

P2 questions:

- 呼吸感强一点还是弱一点？
- 入场方向是否固定？
- 是否要多卡片连续展示？
- 是否需要轻微摄像机/透视运动？

## Confirmation Gates

Static card gate:

- Codex proposes production intent, stage canvas, card asset ratio, output layers, style, copy, hierarchy, card count, buttons, and output path.
- User confirms or says Codex may decide.
- Codex writes/updates `card-spec.json`.
- Codex renders card assets. If motion is possible, the primary card asset must have transparent outer background.
- Codex asks: 是否继续进入动效视频？

Motion gate:

- Static card is accepted.
- Codex proposes motion preset, duration, entrance, hold behavior, exit behavior, transparency, and output path.
- User confirms or says Codex may decide.
- Codex writes/updates `remotion-handoff.json`.
- Codex renders video.

## Default Choices

If user says "你定" or gives minimal direction:

- Static style: `tactile_soft_skeuomorphic_card`
- Production intent: ask first; do not infer final output type silently
- Stage canvas: landscape `1920 x 1080` / `16:9`
- Card asset ratio: choose based on layout; portrait cards are often preferred for multi-card arrangements on a landscape stage
- Output layers: `both` when motion is possible, otherwise `preview_composite`
- Portrait option: `1080 x 1920` / `9:16`, ask when the task may be mobile or short-video oriented
- Motion preset: `pop_breathe`
- Duration: follow voiceover if present; otherwise use the selected preset default
- Background: transparent for video
- Primary video delivery: MOV / ProRes 4444 / alpha
- Optional video preview: WebM / VP8 / alpha
- Output path: `outputs/cards/<slug>/` and `outputs/videos/<slug>/`
