---
title: JSON schema 与页型清单
status: 设计已确认，已实现于 scripts/spec.py 和 scripts/render.py（实现与本文略有出入时以 spec.py 为准，`xhs.py list-types` 可列出现行词表）
---

这份文档定下 agent 和引擎之间的接口：agent 只填一份 JSON，引擎负责校验和出图。目标读者是能力较弱的模型，所以全部用封闭词表、固定字段和字数上限，错了就报中文错并给出可选项。方向和背景见 设计讨论。确认后才批量生成素材库。

# 1 总体约定

三个主题：`paper`（手账浅色，主款）、`dark`（深色）、`ticket`（船票风，蓝白）。一份 JSON 只用一个主题，页与页之间不混用。规格固定 3:4（1242×1656），不支持其他比例。页数 3 到 9 张（建议 6 到 8），第一张必须是封面类，最后一张必须是收尾页，中间相邻两张页型不同。键名用英文，页型 id 用英文，字段值用中文。需要高亮的词用 `[[词]]` 标出，一个字段最多一处。

品牌信息不写进每份 JSON，放在一份 `brand.json` 里，换账号只改这一个文件：账号名（小标签文字）、Logo 图（浅底和深底两张）、人物图（最多三个姿态）、页码是否显示。没有人物图时，用到人物的页型自动换成无人物版，或报错提示换页型。

# 2 JSON 结构

`meta` 的字段：`theme`（paper、dark、ticket）、`title`（只用来命名输出）、`subject_terms`（必填，1 到 4 个主题词，封面或第 2 页必须出现）、`no`（可选，票号，只在 ticket 风格的票根上显示）。

```json
{
  "meta": { "theme": "paper", "title": "Claude 帮我搭的 5 套提效工具" },
  "pages": [
    { "type": "cover_list",  "fields": { ... } },
    { "type": "step",        "fields": { ... } },
    { "type": "closing",     "fields": { ... } }
  ]
}
```

`meta.title` 只用来命名输出文件，不画在图上。每页只有 `type` 和 `fields` 两个键。贴纸、截图都用引用：贴纸写素材库里的 id，截图写相对路径。位置类的值（红框、箭头）写成 0 到 1 的相对比例，不写像素。

# 3 页型清单

下面每个页型给出：用途、字段、字数上限。字数按中文字计，英文单词和数字一个算一个字。上限来自现有样片的版式，是引擎的硬限制。

## 3.1 封面类（第 1 张，三选一）

`cover_list` 榜单清单封面。用于“N 个工具、N 条方法”类，收藏型内容。字段：`lead` 开头半句（≤8 字），`number` 大数字（1 到 2 位数字），`unit` 数字后的词（≤6 字，带高亮），`items` 清单项（3 到 5 条，每条 ≤10 字），`footnote` 手写小注（≤10 字），`pose` 人物姿态（a、b、c 之一，可省，默认 c），`sticker` 贴纸 id（1 个）。

`cover_person` 人物大字封面。用于观点、反常识、结果承诺。字段：`line1`（≤5 字）、`line2`（≤6 字，含高亮词），`sub1`、`sub2` 手写副标题两行（各 ≤10 字），`note` 便签（可省：`title` ≤8 字，`items` 2 到 3 条各 ≤8 字），`pose`（默认 a），`stickers` 贴纸 id（1 到 2 个）。

`cover_quote` 极简大字封面。用于一句话观点、提示词、金句。字段：`lines` 四行大字（每行 ≤5 字，最后一行含高亮），`caption` 手写小注（≤12 字），`stickers`（0 到 1 个）。

## 3.2 内页类

`step` 步骤教程页。用于“第 N 步 + 一张真实截图”。字段：`step_no`（1 到 9），`title`（≤10 字），`subtitle`（≤16 字，可写“A → B → C”），`screenshot` 截图相对路径，`red_box` 红框 `[x, y, w, h]`（0 到 1，可省），`arrow` 箭头 `{"from": [x, y], "to": [x, y]}`（可省），`label` 便签贴字（≤8 字，可省），`stickers`（0 到 2 个）。截图由用户提供，不用生成图冒充。

`prompt` 提示词页。用于一条能直接复制的指令。字段：`title`（≤8 字），`tag` 标签字（≤4 字，默认“提示词”），`body` 指令正文（2 到 4 句，每句 ≤18 字，支持高亮），`storyboard` 小人分镜（可省：3 个 `{ "sticker": id, "label": ≤4 字 }`），`sticker`（1 个）。

`idea` 观点大字页。用于一页一个判断。字段：`lines` 三行大字（每行 ≤6 字，最后一行含高亮），`caption` 手写三行说明（每行 ≤10 字，可省），`stickers`（0 到 2 个）。

`list` 清单页。用于并列的几项。字段：`title`（≤10 字，含高亮），`items` 3 到 5 条，每条 `{ "name": ≤10 字, "desc": ≤14 字 }`，`footnote`（≤12 字，可省），`stickers`（0 到 2 个）。

`compare` 对比页。用于前后、新旧、A 对 B。字段：`title`（≤8 字，含高亮），`left` 和 `right` 各 `{ "tag": ≤3 字, "points": 3 条各 ≤10 字, "sticker": id }`（左边默认红叉，右边默认对勾），`footer`（≤14 字，可省）。

`result` 成果页。用于展示做出来的东西。字段：`title`（≤10 字，含高亮），`images` 1 到 2 张成品图相对路径（像照片贴在纸上），`caption` 手写批注（≤12 字），`sticker`（0 到 1 个）。成品图由用户提供，注意隐私。

`closing` 收尾页（最后一张）。字段：`line1`、`line2`（各 ≤7 字，含高亮），`hint` 手写一句（≤12 字），`actions` 固定三项（收藏、点赞、关注），每项可改说明（≤8 字），`pose`（默认 c），`sticker`（0 到 1 个）。

## 3.3 暂不做、之后补的页型

`cycle` 循环、`matrix` 矩阵、`pyramid` 金字塔、`chart_line` 折线或柱状、`funnel` 漏斗。这些是 nook-ppt 里的图示，手账版还没做。在做出来之前，agent 遇到这类内容用 `list` 或 `step` 代替，skill 里写明。

# 4 素材库 manifest

素材库是一份 `manifest.json` 加一个文件夹的透明 PNG。每个素材一条：

```json
{ "id": "bulb", "file": "stickers/bulb.png", "cn": "灯泡", "category": "object",
  "tags": ["想法", "灵感", "提示", "新点子"], "use_in": ["cover_person", "idea", "prompt"], "size": 768 }
```

分类：`object` 物件（电脑、键盘、文档、文件夹、日历、时钟、放大镜、灯泡、齿轮、火箭、书、笔、剪刀、胶带等），`character` 情绪小人（困惑、思考、开心、惊讶、疲惫、庆祝、指向、举牌等），`symbol` 符号（星光、爆炸线、问号、感叹号、气泡等），`nature` 装饰（叶子、花、云、邮票、相机等），`tool` 工具类图标（不含他人品牌 Logo，用通用的终端、代码块、浏览器窗口等）。线条类（箭头、红框、红圈、波浪线、勾、叉、毛笔衬底）不进库，由代码画，因为 Qwen 画这类不稳定。初步目标是 100 条左右，之后可以追加。agent 选素材只能按 id，引擎提供 `list-assets` 命令按标签和用途筛选，列出可选项。

# 5 引擎命令

```
xhs list-types                         列出全部页型和字段说明
xhs list-assets [--tag 想法] [--use cover_person]
xhs validate plan.json                 只校验，不出图
xhs preview plan.json --page 2         只出第 2 页
xhs render plan.json --out 输出目录     全量出图，同时生成总览图
```

校验规则：页型和主题不在词表里就报错并列出可选项；必填字段缺失、字数超限、贴纸 id 不存在、截图文件不存在、`[[ ]]` 高亮多于一处，都报错；第一张不是封面类、最后一张不是收尾页、相邻两页同型、页数超出 3 到 9，报错。每条报错写成“第 N 页，字段 X：问题，怎么改”。出图后引擎再量一次字，放不下也报同样格式的错，不悄悄缩字。退出码：0 通过，1 校验失败，2 出图失败。

# 6 一份最小示例

```json
{
  "meta": { "theme": "paper", "title": "5套提效工具" },
  "pages": [
    { "type": "cover_person", "fields": {
        "line1": "重复的活", "line2": "交给 [[AI]]",
        "sub1": "我和 Claude 搭了", "sub2": "一整套工作流",
        "note": { "title": "已经交出去的", "items": ["PPT 动效", "公众号封面", "代码动画"] },
        "stickers": ["bulb", "sparkle"] } },
    { "type": "step", "fields": {
        "step_no": 1, "title": "填 5 样，点一下", "subtitle": "期号 → 标题 → 姿态 → 生成",
        "screenshot": "shots/tool.png", "red_box": [0.06, 0.12, 0.33, 0.72], "label": "先填左边", "stickers": ["camera"] } },
    { "type": "closing", "fields": { "line1": "收藏起来，", "line2": "搭你的 [[第一套]]", "hint": "有问题，评论区问我" } }
  ]
}
```

# 7 用户确认结果（261016）

键名用英文（给 agent 看，不用人读）。页数 3 到 9 张。字数上限暂按样片估，不当硬标准：引擎先按样片版式设软上限，执行时由 agent 看溢出报错再调整。品牌设定要可选：默认是船长，别人部署后只在第一次设置自己的 Logo 和 IP 形象，写入用户目录下的 `brand.json`，之后不再询问；引擎启动先查有没有 `brand.json`，没有就进入一次性设置（`xhs setup`），也可以跳过、直接用默认船长。

新增页型：`toc` 目录页（列 3 到 6 个要点，带序号）；`quote` 金句页（一句话大字，可当中间页）；`back_cover` 封底页（一行大字，例如“我是某某，保持关注”，加人物或 Logo；规则：不放二维码、不放联系方式、不放导流话术，只放名字和一句话）。最后一张的规则改为 `closing` 或 `back_cover` 二选一。

素材库指透明 PNG 的贴纸、涂鸦小人、图标，不含 Logo。用户认可的类型：手指、小星星、树枝、灯泡等；AI 科技领域加上电脑、笔记本、本子、笔等。先一次性生成并入库，再做图示类页型。素材库在 `assets/library/`，分 object、character、symbol、nature、tool 五类，条目清单在 `scripts/lib_items.py`。

# 补充：新增页型

`timeline` 时间轴（events 3 到 5 项，每项 time、name、desc）、`stats` 大数字页（items 2 到 3 项，每项 number、unit、label）、`shots` 多截图页（shots 2 到 3 张，captions）。现行页型和字段以 `python xhs.py list-types` 为准。
