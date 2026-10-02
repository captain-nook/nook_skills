---
name: nook-ppt
version: 2.0-alpha
description: 用"零件 + 网格 + 量字"生成可编辑的 PPTX（Office/PowerPoint 为准）。用户要做 PPT、演示文稿、课件、讲课用的幻灯片、把稿子或大纲变成 PPT、给已有 PPT 换风格时使用。分两类：上台讲的（视觉锚点、少字、留白、点击出现的讲点动效、平滑切换）和给别人看的（好看的 PDF 式文档，不加动效）。文字、表格、图表、流程图全部是原生可编辑对象；主标题、Logo、底图可用千问 Image 2.1 出透明底 PNG；能整合用户提供的讲师照片、截图、视频、Logo。不用于只要一张海报或封面图（用 nook-poster / nook-cover），也不用于 HTML 演示。
---

# 1 nook-ppt

把一份讲稿、大纲或文章，做成一份可以在 PowerPoint 里继续编辑的 PPTX。

版本：2.0-alpha（原型验证中）。技能名固定为 `nook-ppt`，版本号写在这里和 [CHANGELOG.md](CHANGELOG.md)，不写进名字。

## 1.1 三条根本原则

1. **PPT 是视觉锚点，信息靠人讲。** 多字不如少字，少字不如图表，图表不如图片。上台讲的 PPT，每页一个视觉重点，解释放进备注里的讲稿。
2. **零件固定，拼装自由。** Agent 决定用哪个零件、占网格几列几行、放什么内容；坐标、字号、行距、内边距由引擎算。Agent 不写坐标。
3. **每一步都要看得见。** 生成后必须用 PowerPoint 自己导出图片并核验，再对照质量清单看图。没导出看过，不说"做好了"。

## 1.2 两类 PPT（先问清楚这一条）

| | 上台讲（talk） | 给别人看（read） |
|---|---|---|
| 用途 | 讲师现场讲，PPT 是背景和锚点 | 当一份好看的 PDF 文档，独立阅读 |
| 文字 | 少字，但不追求零字；每页只放一个意思 | 不纠结字多字少；能读懂就行 |
| 留白 | 硬要求，要量化检查 | 软要求 |
| 动效 | 一次点击一个讲点；讲点内部自动依次出现 | 不加动效；导出 PDF 元素全在 |
| 切换 | 平滑切换（人物、装饰跨页同名） | 朴素淡入 |
| 备注 | 必须有讲稿 | 可选 |
| 底色 | 深色为主 | 浅色为主 |

详见 [references/modes.md](references/modes.md)。"见山不是山"式的零字高端做法是今后的目标，现在的标准是中高端：一个视觉锚点加一句标题，最多一两个关键词。

## 1.3 流程（有关卡，每个关卡要用户明确确认）

详见 [references/workflow.md](references/workflow.md)。

1. **立项**：确认类型（上台讲 / 给别人看）、素材（讲稿、大纲、用户已有的照片视频截图 Logo）、页数、时长。最多一次问 3 个问题，尽量给选项。
2. **提纲**：每页做什么：页面角色（锚点页、结构页、数据页、素材页）、这一页的一句话、字数预算、**图示类型**（循环、金字塔、漏斗、矩阵、阵列、韦恩、环形图、流程、图表……，见 [references/diagrams.md](references/diagrams.md)）、视觉载体。讲稿逐页对应。内容有结构就画成对应的图，不要全部排成卡片。
3. **素材槽位表**（用户有已有素材时必做）：在设计阶段就和用户约定每个素材怎么呈现，落地时照约定做，不临场发挥。见 [references/slots.md](references/slots.md)。
4. **风格**：从已有风格包里选一套，并选变体（深色 / 蓝色光 / 浅色 / 阅读版）。见 [references/styles.md](references/styles.md)。
5. **资产**：需要生成的插图、人物、底图、标题字，先出图并逐张核对（含文字）；用户提供的素材不重画。**每张图要先想好它表达这一页的什么意象**（隐喻、场景、象征物），不能只是风格好看但与内容无关。
6. **生成**：用 `scripts/slidekit.py` 拼装，运行时会自动做量字、重叠检查、告警。
7. **核验**：`scripts/run_deck.py` 一键完成构建、PowerPoint 逐页导出、溢出检查、自动检查（`lint_deck.py`：字号、对比度、备注、讲点数等）、加动效或导出 PDF、拼总览图；再对照 [references/quality-checklist.md](references/quality-checklist.md) 看图。
8. **交付**：**默认只交付一份带动效的 PPTX**（可编辑），不同时输出静态版、PDF、阅读版等多个版本；中间文件（`*.anim.json`、静态稿）由 `run_deck.py` 自动清理。只有用户明确要"给别人看"的版本或 PDF 时，才走 read 模式（`NOOKPPT_PDF=1` 导出 PDF）。

## 1.4 引擎（scripts/）

- `slidekit.py`：网格与规格（Design Tokens）、量字、零件（标题、文本、卡片、标签、流程、分层带、时间线、表格、图表、图片、人物贴纸、装饰、对话气泡、素材槽位）、动效计划、平滑切换、布局告警。
- `check_deck.ps1`：PowerPoint 导出核验。`-Pptx <文件> -OutDir <目录> [-Pdf <文件>]`（可同时导出 PDF）。存成带 BOM 的 UTF-8，PowerShell 5.1 才不会乱码。
- `animate_deck.ps1`：读取 `*.anim.json` 给 PPTX 加动效和切换。`-In -Out -Plan`。
- `lint_deck.py`：自动检查质量清单里能判的项（标题、替代文字、最小字号、字体数、对比度、讲点数、备注、内容占比、版式节奏、强调色数）。`python lint_deck.py <pptx> --png <导出目录>`，有"否"退出码为 1。
- `package_release.py`：生成发布目录（`python package_release.py <目录> [--full]`）。
- `run_deck.py`：一键流程。`python run_deck.py <构建脚本> [参数...]`；默认只输出一份动效版（替换静态稿，删除 `*.anim.json`）；read 模式只在明确要求时用。环境变量 `NOOKPPT_KEEP=1` 保留中间文件，`NOOKPPT_PDF=1` 让 read 模式导出 PDF。
- 零件还包括：折线图 `linechart()`、卡片光影（主题 `glass` / `glass_img`）、文字渐变光 `text(grad=)`。
- **图示零件**（原生形状 / 原生图表，跟随主题）：`cycle_ring()` 循环、`pyramid()` 金字塔、`funnel()` 漏斗、`matrix()` 带坐标轴的矩阵、`array_grid()` 阵列、`venn()` 韦恩、`donut()` 环形图。什么内容用哪个见 [references/diagrams.md](references/diagrams.md)。
- `deckkit.py`：公共页面小工具 `Kit`（大标题占位符、眉题、角标、圆角图片、`stat_row()` 大数字卡片行、`compare()` 左右对比）和命令行 `cli()`。

最小用法：

```python
import sys; sys.path.insert(0, "<skill>/scripts")
from slidekit import *
deck = Deck(theme=MY_THEME, mode="talk")          # 或 "read"
s = deck.slide(title="现在做 PPT 卡在两个极端", transition="morph")
deck.cards(s, [(cell(0, 0, 6, 3.5), "只能填模板", dict(bullets=["版式固定", "换风格要重做"]))])
deck.save("out.pptx")                             # 同时写出 out.anim.json
```

之后跑 `animate_deck.ps1` 加动效，再跑 `check_deck.ps1` 核验。

## 1.5 硬规则

- 文字必须是真文字（标题走真占位符）；表格、图表用原生对象，图表带数据。图片只用于：主标题、Logo、人物、装饰、底图、用户提供的素材。
- 底图放进版式（母版），不放在页面上，避免误选。
- 关闭自动缩放；字号只取档位；放不下就报错，回到文案改，不悄悄缩字或裁字。
- 事实类图片（截图、真实数据、Logo、人物照片）只用用户提供的，不用生成图冒充。
- 动效默认手动触发：`beat` 是一个讲点（点击一次），`after` 接在上一个之后，`with` 与上一个同时。
- 平滑切换用 `!!名字` 给对象配对；平滑进来的对象不重复播入场动画。
- **删掉没有影响的话**：页面上任何一句话，如果删掉对内容一点影响都没有，就删掉。常见的是口号式标题（"三个数字，记住它""这一周，只做一件事""一张图看懂"）、标签式眉题（TAKEAWAY、小结）、复述前文的结尾、和标题重复的图示中心字、出处标注。结尾页只留一句有信息量的话。
- 只以 Office/PowerPoint 为准，不考虑 WPS。
- 反模板：见 [references/fonts-and-anti-template.md](references/fonts-and-anti-template.md)。

## 1.6 环境与限制

- 需要 Windows + Microsoft PowerPoint（核验、动效、PDF 都通过它的 COM）；依赖见 `requirements.txt`。字体、图片的许可见 [NOTICE.md](NOTICE.md)。
- 出图需要本机 ComfyUI（Qwen Image 2.1）；没有时用已有素材库，或只用代码生成的底图。

- 姿势切换是位置缩放加交叉淡化，不是骨骼插值。
- 字体：本机有的字体直接用；给别人用时才需要打包（静态 TTF 才能嵌入）。
- 线性图标是否转原生形状，待实测；默认 PNG，SVG 兜底。
