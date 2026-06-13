---
name: nook-card
description: |
  Create reusable knowledge cards and optional card-to-video handoff specs from user topics, copy, and style references.
  Use when the user asks for knowledge cards, card images, social cards, cover cards, OpenDesign card generation, card style systems, or Remotion-ready card videos. Always confirm production intent, card count, card asset ratio, output layers, and motion needs before generating.
---

# nook-card

> [!IMPORTANT]
> ### 🛑 CRITICAL SYSTEM DIRECTIVE: LAZY-LOADING & INTERACTION GATE LOCK
> - **Initial State**: You are locked in `STATE: REQUIREMENT_GATHERING` (Mandatory).
> - **Soft-Lock Guardrail**: Under this initial state, you are **ABSOLUTELY FORBIDDEN** from generating `card-spec.json`, generating `remotion-handoff.json`, or executing any Python/OpenDesign rendering commands or scripts.
> - **Absolute Restriction**: On your first turn, your **SOLE PERMITTED ACTION** is to print the [STAGE 1 QUESTIONNAIRE] below. Do not try to bypass this gate by assuming defaults or generating content upfront. Any silent execution or pre-generation is considered a Fatal Failure of the system.
> - **Lazy-Loading**: Do NOT pre-load or process `card-spec.schema.json`, `opendesign-card-contract.md` or style specifications during this stage to prevent token pollution and pre-generation bias. Only read them after the user explicitly grants confirmation.

---

## Stage 1: Step-by-Step Progressive Choices (First-Turn Response Template)
When a user initiates a task, you MUST reply using exactly the following Markdown template. Fill in the placeholder `{...}` with the user's specific topic, and **DO NOT** output any large tables, draft layouts, copy, or specs yet. Do not decide or assume anything.

### 📋 Nook-Card 视频卡片生成器 - 极简向导 (第 1 步)
您好！我是您的 Nook-Card 协同设计助手。收到您的话题：**“{用户的话题}”**。

为了用最轻松、零门槛的方式帮您定制卡片与视频，我们拒绝复杂的问答和长篇大论的方案点评，采用**多轮极简单选题**！请问您这次作品的**生产意图与视觉风格**是什么？

#### 1️⃣ 请选择您想使用的【静态视觉风格】（4套可选）
*   **[A] 经典触感软拟态风 (`tactile_soft_skeuomorphic_card`)**
    *   *特点：Confident Confident 黑色粗描边、按压质感黄色按钮、macOS 三色指示灯，极具实体交互感。*
*   **[B] 毛玻璃层叠卡片风 (`glassmorphism_layered_card`)**
    *   *特点：透光磨砂面板、优雅的光泽渐变背景、柔和的背部模糊与发光边框，科技高级感十足。*
*   **[C] 波普漫画卡片风 (`pop_art_comic_card`)**
    *   *特点：高饱和度漫画配色、网格半调网点、爆炸对话框，情绪饱满、社媒抓眼传播利器。*
*   **[D] 手账拼贴卡片风 (`analog_journal_collage_card`)**
    *   *特点：温暖纸张肌理、撕边胶带拼贴、手写体点缀、轻微偏转，充满人文温和叙事感。*

#### 2️⃣ 请选择您想搭配的【视频动效预设】（4套可选）
*   **[1] 下方弹出居中呼吸 (`pop_breathe`)**
    *   *特点：多张卡片依次从下方以物理回弹弹出到屏幕中央，带有悬浮轻微呼吸和阴影漂移。*
*   **[2] 时间轴成长展开 (`timeline_arrow_reveal`)**
    *   *特点：箭头或引导路径逐步生长，卡片在路径两侧交替弹出，极具教程和步骤秩序感。*
*   **[3] 竖卡走马灯聚焦 (`portrait_carousel_focus`)**
    *   *特点：多张卡片以 3D 轨迹旋转切换，正面聚焦卡清晰可读，背后卡片柔和淡出模糊。*
*   **[4] 动态对比柱状升起 (`dynamic_compare_bars`)**
    *   *特点：若干对比数据柱随卡片依次升起，数值实时滚动增长，适合数据对比或排名。*
*   **[0] 仅制作静态卡片** (不需要视频动效)

---
**💡 极简操作**：
请选择您的搭配！例如：**A1** (经典拟态风格 + 弹出呼吸动效) 或 **C2** (波普漫画风格 + 时间轴展开动效)。

直接回复 **“字母+数字”** (如 **A1**、**B3**、**A0**) 即可！我们将根据您的选择，为您精准解锁第 2 步的画幅比例确认与核心文案极简定制。

---

Use this skill to produce knowledge cards with a reusable style system. The skill is interactive: do not generate final visual assets until content hierarchy and output constraints are confirmed, unless the user explicitly says to decide directly.

## Read First

- Workflow: `references/workflow.md`
- Global production rules: `references/global-production-rules.md`
- Style registry: `references/style-registry.md`
- Interaction protocol: `references/interaction-protocol.md`
- Motion registry: `references/motion-registry.md`
- Default style: `references/styles/tactile-soft-skeuomorphic-card.md`
- OpenDesign adaptation notes: `references/opendesign-adapter.md`
- OpenDesign card contract: `references/opendesign-card-contract.md`
- Quality checklist: `references/checklist.md`
- Remotion handoff: `references/remotion-handoff.md`

Load only the references needed for the current task.

## Default Process

1. Identify production intent first: static-only, motion-ready assets, or static plus motion video.
2. Always ask for requirements first unless the current request already includes enough detail.
3. Ask in the two-dimension model: selected preset and concrete requirements.
4. For static cards, read the global production rules, style registry, and selected style reference.
5. Confirm both the video/stage canvas and the card asset ratio. Do not assume they are the same.
6. Confirm card count and split method before rendering if the content has steps, categories, chapters, or list structure.
7. If motion is possible, confirm `transparent_asset` output before generating final assets. Generate `preview_composite` separately for human review.
8. Prepare `card-spec.json` using `references/opendesign-card-contract.md` and the selected style tokens.
9. Render and quality-check the card assets.
10. If and only if video is requested, read the motion registry, confirm the selected motion preset, then prepare `remotion-handoff.json` and render the video.

## Defaults

- Default style: `tactile_soft_skeuomorphic_card`
- Default output: motion-ready transparent card asset plus preview composite when motion is possible; preview composite only when static-only is confirmed.
- Default video/stage canvas: landscape `1920 x 1080` / `16:9`.
- Card asset ratio is separate from video/stage canvas; in landscape videos, portrait or vertical cards may be better for multi-card layouts.
- Portrait stage `1080 x 1920` remains an explicit option at task start.
- Default motion preset: `pop_breathe`
- Default primary video delivery: MOV / ProRes 4444 / alpha
- Optional preview video: WebM / VP8 / alpha
- Default engine path: OpenDesign-compatible HTML/CSS preview plus structured JSON spec

## Do Not

- Do not treat one reference image as a fixed template.
- Do not skip content hierarchy confirmation when the user expects collaboration.
- Do not mix style tokens from different styles unless the user asks for a hybrid.
- Do not enter motion/video workflow if the user only asks for a static card.
- Do not ask motion questions before static cards are accepted, unless the user explicitly starts with a video request.
- Do not generate a Remotion video before the static card direction is approved.
- Do not generate final static assets before deciding whether they must be motion-ready and transparent.
- Do not bake a full-canvas decorative background into card assets that may be used for alpha video; put that background in `preview_composite` or the Remotion scene instead.
