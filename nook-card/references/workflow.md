# 卡片生产工作流规范

版本：v0.1  
更新日期：2026-05-21  
用途：定义 Codex 如何交互式驱动 OpenDesign 生成知识卡片，并为后续 Remotion 视频化预留接口。  
适用范围：静态知识卡片、系列卡片、视频封面、短视频分镜卡片。

## 工作流目标

用户提出卡片任务后，Codex 不直接盲目出图，而是先读取项目总控笔记、风格库索引和目标风格规范，完成必要的交互确认，再组织 OpenDesign 输入生成卡片。生成后，Codex 需要根据规范做质量检查，并把结果整理为可继续修改或进入 Remotion 的结构化资产。

整个动作分为三个大步骤：

1. 确认生产意图。
2. 设计并输出卡片资产。
3. 出动效视频。

第三步是可选的。如果用户只要静态卡，就只走前两步，不进入 Remotion。

## 默认流程

1. 识别任务

   当用户提到制作知识卡片、封面卡、图文卡、系列卡、OpenDesign 出图、卡片视频化、Remotion 动态化时，Codex 应进入本工作流。

2. 读取规范

   Codex 应读取：

   - `SKILL.md`
   - `references/global-production-rules.md`
   - `references/workflow.md`
   - `references/style-registry.md`
   - 用户指定或默认风格对应的风格规范文档

3. 收集需求

   Codex 需要确认最少必要信息。如果用户已经给出明确内容，不重复提问。

   每轮交互使用两个维度：

   - 用哪个风格/动效？
   - 具体要求是什么？

   但在正式生成前，Codex 必须先确认生产意图：只要静态卡、可能进入动效，还是静态卡加动效一起做。只要后续可能进入动效，就必须把“视频/舞台画幅”和“卡片自身比例”分开确认。

   必要字段：

   | 字段 | 说明 | 默认值 |
   | --- | --- | --- |
   | `topic` | 卡片主题 | 用户原始请求 |
   | `usage` | 用途，如公众号配图、视频封面、课程卡、社媒图 | 知识卡片 |
   | `style_id` | 风格 ID | `tactile_soft_skeuomorphic_card` |
   | `stage_canvas` | 视频/舞台画幅 | 默认横屏 `1920 x 1080` / `16:9`，竖屏可选 |
   | `card_asset_ratio` | 卡片自身比例 | 根据内容和动效布局选择，不默认等于舞台画幅 |
   | `output_layers` | 输出层级 | 可能进入动效时默认 `transparent_asset` + `preview_composite` |
   | `copy` | 卡片文案 | 由 Codex 草拟后确认 |
   | `hierarchy` | 哪些字大、哪些字小、哪些内容作为按钮或标签 | 由 Codex 建议后确认 |
   | `output` | 输出格式，如 PNG、SVG、设计稿、视频素材 | 静态卡阶段默认 HTML/SVG/PNG；视频阶段默认 MOV |

4. 交互确认

   Codex 应先给出一个简洁方案供用户确认，至少包括：

   - 主标题
   - 副标题或说明文字
   - 按钮/标签文案
   - 信息层级
   - 选用风格
   - 舞台画幅与卡片自身比例

   只有在用户确认或明确授权“你直接定”后，才进入 OpenDesign 生成。

5. 判断是否可以生成最终静态物料

   如果用户只需要静态卡，且确认可以把背景烘焙进画面，可以直接生成 `preview_composite`。

   如果后续可能进入动效，则不能只生成带背景成品图。必须先确认：

   - `transparent_asset`：透明外背景的卡片资产。
   - `preview_composite`：带背景的人眼预览图。
   - 卡片自身比例，例如横卡、竖卡、方卡或自定义比例。
   - 舞台画幅，例如横屏 `1920 x 1080`。

6. 组织 OpenDesign 输入

   OpenDesign 输入必须包含：

   - `card-spec.json`：遵循 `references/opendesign-card-contract.md` 和 `references/card-spec.schema.json`。
   - 风格 token：来自目标风格规范。
   - 内容结构：标题、副标题、编号、标签、按钮、注释、背景语境元素。
   - 布局约束：舞台画幅、卡片自身比例、留白、层级、是否需要多张系列图。
   - 输出层级：`transparent_asset`、`preview_composite` 或 `both`。
   - 禁止项：来自目标风格规范的负向约束。

7. 生成卡片资产

   Codex 驱动 OpenDesign 生成卡片原型或成品图。生成后不要立即结束，需要执行质检。

   对于可能进入动效的任务：

   - 主资产必须是透明外背景。
   - 单张卡片应独立生成，方便后续排列组合。
   - 全画布背景只能进入预览图或 Remotion 场景层。
   - 毛玻璃等依赖背景的风格，应将背景作为 preview/stage layer，而不是烘焙进卡片资产外背景。

8. 质检与反馈

   质检维度：

   - 是否符合目标风格 token。
   - 文字是否正确、无错别字、无溢出。
   - 信息层级是否符合用户确认。
   - 色彩、描边、圆角、阴影、底纹是否符合规范。
   - 是否适合目标用途和平台。

9. 迭代

   如果不合格，Codex 应指出问题并重新生成或要求局部修改。最多优先做 `2-3` 轮高价值迭代，再向用户汇报当前状态。

10. 是否进入动效

   卡片资产完成后，Codex 必须询问用户是否进入动效视频。如果用户不需要，到此结束。

11. Remotion 交接

   如果用户要求视频化，Codex 才进入动效步骤，并把静态卡片整理为 Remotion 输入：

   | 字段 | 说明 |
   | --- | --- |
   | `scene_id` | 分镜 ID |
   | `image_asset` | 透明卡片资产路径，优先使用 `transparent_asset` |
   | `duration` | 分镜时长；有口播时优先跟随口播时长 |
   | `animation` | 入场、停留、强调、退场动效 |
   | `voiceover` | 旁白文本 |
   | `subtitle` | 字幕文本 |
   | `music_sfx` | 音乐或音效需求 |
   | `delivery` | 默认 MOV / ProRes 4444 / alpha，可选 WebM 预览 |

   动效全局约束：

   - 配合口播时，时长按口播节奏设置，不机械套用固定秒数。
   - 停留段不能绝对静止，应保留呼吸感、轻微晃动、阴影位移或摄像机漂移。
   - 允许使用轻微透视/摄像机动画，但不得损害文字可读性。

## 交互问题优先级

Codex 应尽量少问，但关键问题不能省。

具体交互规则见 `references/interaction-protocol.md`。

优先级 P0：不确认会导致方向错误

- 这张卡片的主题是什么？
- 用哪套风格？
- 主要给谁看、用在哪里？

优先级 P1：影响画面结构

- 哪句话最大？
- 是否需要按钮、标签、编号？
- 输出比例是竖版、方图还是横版？

优先级 P2：可以由 Codex 先给建议

- 文案是否需要更短？
- 是否做系列卡？
- 是否预留视频动效空间？

## OpenDesign 提示词结构

推荐结构：

```text
Task:
Create a knowledge card based on the following content and style tokens.

Content:
- Title:
- Subtitle:
- Number:
- Buttons:
- Labels:
- Notes:

Style:
- style_id:
- visual_keywords:
- color_tokens:
- stroke_tokens:
- radius_tokens:
- shadow_tokens:
- surface_pattern:
- typography:

Layout:
- canvas_size:
- aspect_ratio:
- hierarchy:
- safe_area:
- dynamic_constraints:

Negative constraints:
- Do not use:
```

## card-spec 中间协议

OpenDesign 生成前，Codex 应先组织 `card-spec.json`。它不是最终设计稿，而是用户确认内容、风格 token、布局槽位和渲染目标的中间协议。

需要读取：

- `references/opendesign-card-contract.md`
- `references/card-spec.schema.json`

关键规则：

- 所有可见文字必须进入 `content.blocks[]`。
- 每个文字块必须有稳定 `id`、语义 `role` 和原文 `text`。
- 信息层级写入 `priority` 和 `emphasis`，不要只靠自然语言描述。
- 组件位置优先写成 `slot`，不要过早锁死绝对坐标。
- 用户确认前，`status` 必须是 `draft`。
- 用户确认后，`status` 才能变成 `confirmed`，并进入 OpenDesign 渲染。

## 输出命名建议

静态卡片：

```text
YYYYMMDD_topic_style_v01.png
YYYYMMDD_topic_style_v01.opendesign.json
```

视频素材：

```text
YYYYMMDD_topic_scene01.png
YYYYMMDD_topic_remotion_v01.mov
```

其中 `topic` 使用短英文或拼音，不使用空格。

## 进入 skill 时的最小指令

未来写入 `SKILL.md` 时，可精简为：

```text
When the user asks for knowledge cards, cover cards, OpenDesign card generation, or Remotion card videos, read the workflow reference and selected style reference. Interactively confirm content hierarchy and output constraints before generating. Use OpenDesign for static card output and prepare Remotion handoff when video is requested.
```
