# OpenDesign Skill 接入规范

版本：v0.1  
更新日期：2026-05-21  
用途：记录 OpenDesign 对 skill 的要求，并映射到本项目的知识卡片工作流。  
来源：

- `https://open-design.ai/skills/`
- `https://github.com/nexu-io/open-design/blob/main/docs/skills-protocol.md`
- `https://raw.githubusercontent.com/nexu-io/open-design/main/docs/skills-contributing.md`

## OpenDesign 的核心要求

OpenDesign 的 skill 是一个“可复用 artifact recipe”，即面向某一类产物的生产配方。它不是一个第三方 API 包装器，也不是一次性的营销项目。

基础结构：

```text
skill-root/
├── SKILL.md
├── assets/
├── references/
└── tests/
```

最小必需项：

- 一个独立文件夹。
- 一个 `SKILL.md`。
- `SKILL.md` 内包含 YAML frontmatter 和 Markdown 工作流说明。

常用可选项：

- `assets/`：模板、图片、HTML、CSS、示例资源等。
- `references/`：工作流过程中按需读取的规范、布局、质检清单、风格文档。
- `tests/`：测试 prompt 和输出断言，用于检查 skill 是否还能正常工作。
- `example.html`：当 preview 类型是 HTML/JSX 时，官方贡献要求提供手工构建的示例。

## SKILL.md 基础字段

OpenDesign 兼容 Claude Code 的 `SKILL.md` 基础格式。为保证 Codex skill 发布校验通过，公开发布版本的 `SKILL.md` frontmatter 只保留 `name` 和 `description`；触发词写入 `description`，OpenDesign 扩展配置作为下方可选实现参考保留。

```yaml
---
name: nook-card
description: |
  Create reusable knowledge cards from user-provided topics, copy, and style specs.
  Use when the user asks for knowledge cards, social cards, cover cards, card images,
  OpenDesign card generation, or card-to-video workflows.
---
```

要求：

- `name` 使用英文 ASCII slug。
- `description` 要具体说明产物、场景和边界。
- 触发词应尽量写入 `description`，例如 `knowledge card`、`card image`、`OpenDesign card`、`Remotion-ready card video`、`知识卡片`、`卡片视频`。
- 如果某个 OpenDesign 版本明确支持额外 `triggers` 字段，可以在本地派生版本中加入；公开 Codex skill 版本不要把 `triggers` 作为顶层字段发布。

## OpenDesign 扩展字段

部分 OpenDesign 版本在 frontmatter 中支持 `od:` 扩展，用于 UI 展示、预览、表单输入、参数滑杆和输出声明。公开发布版本暂不把 `od:` 写入 `SKILL.md`，避免破坏 Codex skill 校验；如果你的 OpenDesign 环境需要这些字段，可按下面示例在本地 fork 中添加。

本项目建议：

```yaml
od:
  mode: image
  platform: desktop
  scenario: marketing
  preview:
    type: html
    entry: index.html
  design_system:
    requires: true
    sections: [color, typography, layout, components, depth]
  craft:
    requires: [typography, color, anti-ai-slop]
  inputs:
    - name: topic
      type: string
      required: true
    - name: usage
      type: enum
      values: [wechat, xiaohongshu, video-cover, course-card, generic]
      default: generic
    - name: style_id
      type: enum
      values: [tactile_soft_skeuomorphic_card, glassmorphism_layered_card, pop_art_comic_card, analog_journal_collage_card]
      default: tactile_soft_skeuomorphic_card
    - name: aspect_ratio
      type: enum
      values: ["16:9", "9:16", "1:1", "custom"]
      default: "16:9"
    - name: production_intent
      type: enum
      values: [static_only, motion_ready, static_plus_motion]
      default: static_only
    - name: card_asset_ratio
      type: enum
      values: ["16:9", "9:16", "3:4", "4:3", "1:1", "custom"]
      default: "custom"
    - name: output_layers
      type: enum
      values: [transparent_asset, preview_composite, both]
      default: both
    - name: needs_video_handoff
      type: boolean
      default: false
  parameters:
    - name: visual_density
      type: spacing
      default: 70
      range: [30, 100]
    - name: shadow_offset
      type: spacing
      default: 40
      range: [16, 72]
  outputs:
    primary: example.html
    secondary: [card-spec.json, remotion-handoff.json]
  capabilities_required:
    - file_write
```

说明：

- `mode` 决定 skill 在 OpenDesign 哪个模式中出现。知识卡片可先用 `image`；如果实际产物是 HTML 预览，也可以考虑 `prototype`。
- `preview.type` 建议先用 `html`，因为 HTML/CSS 更适合承载设计 token、动态布局和截图导出。
- `inputs` 对应用户可在侧栏填写的结构化字段。
- `parameters` 对应生成后可调的滑杆参数，例如密度、阴影偏移、字号比例。
- `outputs.secondary` 应包含结构化交接文件，方便后续 Remotion 使用。

## DESIGN.md 与风格规范的关系

OpenDesign 支持给非 design-system skill 注入当前 `DESIGN.md`。官方列出的 DESIGN.md 常见结构包括：

- Visual Theme & Atmosphere
- Color Palette & Roles
- Typography Rules
- Component Stylings
- Layout Principles
- Depth & Elevation
- Do's and Don'ts
- Responsive Behavior
- Agent Prompt Guide

本项目当前的 `01_触感软拟态卡片风格规范.md` 更像详细风格 reference。未来可以额外生成一份 OpenDesign 友好的 `DESIGN.md`，作为当前默认风格的设计系统入口；详细数值仍保留在 `references/styles/` 中。

建议映射：

| 当前文档 | OpenDesign 角色 |
| --- | --- |
| `00_总控笔记.md` | 项目背景，不直接塞进 skill body |
| `01_触感软拟态卡片风格规范.md` | style reference |
| `02_卡片生产工作流规范.md` | skill workflow reference |
| `03_风格库索引.md` | style registry |
| `04_OpenDesign Skill 接入规范.md` | OpenDesign adaptation note |
| 未来 `DESIGN.md` | 当前默认风格的高密度设计系统摘要 |

## 本项目的 skill 目录草案

```text
nook-card/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── DESIGN.md
├── example.html
├── assets/
│   ├── templates/
│   │   └── card-base.html
│   └── samples/
│       └── tactile-soft-skeuomorphic-demo.png
├── references/
│   ├── card-spec.schema.json
│   ├── checklist.md
│   ├── opendesign-card-contract.md
│   ├── opendesign-adapter.md
│   ├── remotion-handoff.md
│   ├── remotion-handoff.schema.json
│   ├── workflow.md
│   ├── style-registry.md
│   ├── styles/
│   │   └── tactile-soft-skeuomorphic-card.md
└── tests/
    └── basic.prompt
```

## 质量门槛

OpenDesign 对 skill 质量的要求给了几个重要启发：

- 如果走官方贡献路径，示例不能是 lorem ipsum 或占位图，要像真实设计师交付的东西。当前 `example.html` 只是架构占位，后续需要替换为真实最小样例。
- 触发词要具体，避免和其他 skill 混淆。
- 每个 skill 应该只生产一种明确类型的 artifact。
- 必须有质检清单，至少覆盖 P0 规则。
- 如果走官方贡献路径，slug 要 ASCII kebab-case。
- 不要把 vendor API wrapper 当成 skill；本项目应该是“卡片生成 recipe”，不是“OpenDesign API wrapper”。
- 图像资源需要控制体积，示例图不应过大。

## 对本项目的结论

1. 本项目的 OpenDesign/Codex skill 命名确认为 `nook-card`；后续所有自有 skill 均使用 `nook` 前缀。
2. 第一版更适合做成 `image` 或 `prototype` mode，而不是 `design-system` mode。
3. 风格本身不应该单独成为 skill；风格应该作为 `references/styles/` 下的可替换配置。
4. 当前“触感软拟态卡片风”应被整理成一个 style reference，并额外生成 `DESIGN.md` 摘要供 OpenDesign 注入。
5. OpenDesign 生成静态卡片后，需要输出 `card-spec.json`，让 Remotion 能读取布局、文案、资产路径和动效建议。
6. 当前阶段先搭好 `nook-card/` 文件架构；后续再做 `example.html` 和 `card-spec.json` 的最小真实样例，验证 OpenDesign 的 preview/export 路径。
