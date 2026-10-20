---
name: nook-xhspage
version: 0.4
description: 把一份已定好内容的小红书图文方案，用 Python 脚本渲染成成套的 3:4 手账涂鸦风图片（封面加内页）。四套风格（薄荷、手账浅色、深色、船票风），自带通用 IP 人物「薄荷」，开箱即用，内置 161 个透明贴纸素材库，不依赖 ComfyUI；文字、版式、图示全部是代码画的，字准、可改。只负责"画"，文案由 nook-xhswrite 等写作 skill 先定；用户要求出小红书封面、内页、成套图文图片、手账风图示页时使用。不用于写文案，不用于自动发布。
---

# 1 nook-xhspage

小红书图文的渲染层：输入是一份"笔记方案"（几张图、每张用什么页型、各字段写什么），输出是一套 1242×1656 的 PNG。写作交给 `nook-xhswrite`，视觉策划可参考 `nook-xhsdesign`，本 skill 只负责把方案画出来。

状态：0.4。22 个页型、命令行入口、JSON 校验、161 个素材、本地界面已可用，薄荷（mint，通用款默认）、手账浅色（paper）、深色（dark）、船票风（ticket）四套主题。

## 1.1 三条原则

1. **内容先于呈现。** 没有定好的一句话核心和逐页内容，不画图。字不如表，表不如图，每张图一个意思，长文放在笔记正文里。
2. **只从素材库取贴纸，只用封闭词表。** 页型、主题、贴纸都按 id 引用，不在表里就报错并列出可选项，不临场发挥。没有 ComfyUI 的使用者照样能用。
3. **放不下就回去改文案**，不悄悄缩字；事实类图片（截图、数据、成果）只用用户提供的，不用生成图冒充。

## 1.2 目录

```
nook-xhspage/
  SKILL.md              本文件
  references/           schema.md（接口设计）、acceptance.md（验收标准）、publish-checklist.md（发布前检查）
  scripts/
    paths.py            全部路径从这里来，相对 skill 目录；环境变量见 1.4
    xhs.py              命令行入口
    spec.py             页型、字段、字数上限、校验（改词表只改这里）
    render.py           22 个页型的渲染函数，读 fields，不含写死文案
    pages_core.py pages_hand.py pages_diagram.py   共用的小工具、颜色映射和船票外框、手绘形状
    lib_items.py        素材库条目清单与生成提示词（可选，仅需要追加素材时用）
  assets/
    fonts/              思源黑体、霞鹜文楷（OFL，许可见 LICENSE-fonts.txt）
    brand/mint/         通用款品牌：IP 人物薄荷的 3 个姿态和头像 Logo（--default，可整体替换，见 1.3）
    brand/default/      船长款品牌（作者本人，--captain）
    themes/mint/        薄荷风格的封面底图和内页底图
    library/            素材库：manifest.json + 161 个透明 PNG（5 类）
    examples/           示例用截图和成果图
  setup.bat ui.bat requirements.txt
```

## 1.3 品牌设置（第一次使用必须做，只做一次）

第一次运行时，`validate`、`render`、`preview` 会拒绝执行并退出（退出码 3），打印要问用户的三件事。agent 必须先问用户，不能替用户决定：

1. 有没有自己的 IP 人物形象？（透明底 PNG，最好有抱臂、讲解、邀请三个姿态；没有也可以不用人物）
2. 有没有自己的 Logo？（浅底和深底各一张最好；没有也可以不用）
3. 账号名叫什么？（画在封面左上角的小标签）

用户没有特别说明（没有自己的人物和 Logo，也没提风格），就直接运行 `python xhs.py setup --default`，用通用款：IP 人物薄荷加薄荷风格，不必逐项追问；账号名想改成自己的，再加 `--name`。用户有自己的人物、Logo 或风格要求时，再按下面设置自己的。

用户答完，运行一次 `setup`，之后不再询问：

```
python xhs.py setup --default [--name "账号名"]                 用内置通用款（IP 人物薄荷 + 薄荷风格），只改账号名就能用
python xhs.py setup --captain                                  用作者本人的船长款
python xhs.py setup --name "账号名" --pose-a 人物.png [--pose-b ... --pose-c ...] [--logo-light 浅底.png --logo-dark 深底.png]
python xhs.py setup --name "账号名" --no-person --no-logo      没有人物、没有 Logo
python xhs.py setup --status                                   看当前设置
```

设置存在用户目录 `~/.nook-xhspage/`（环境变量 `NOOK_XHS_HOME` 可改），skill 目录里不放任何个人信息。没有人物时，cover_person 页型不可用（校验会报错并建议换页型），其余页型自动省略人物；没有 Logo 时省略 Logo。要重新设置，再运行一次 `setup`。

## 1.4 运行

需要 Python 3.10+、Pillow、numpy、playwright 和 Chromium（`setup.bat` 一键安装）。出图默认写在 plan.json 所在文件夹的 `out/`（`preview` 写 `_preview/`），不会写进 skill 目录；`--out` 可指定，环境变量 `NOOK_XHS_OUT` 也可改。在 `scripts/` 目录里运行：

```
python xhs.py setup --status                  第一次使用先看品牌是否已设置
python xhs.py list-types                      列出全部 22 个页型、字段和字数上限
python xhs.py list-assets --tag 想法           按标签或分类查素材库 id
python xhs.py suggest-assets plan.json        逐页判断贴纸该放还是不放，给候选 id
python xhs.py validate plan.json              只校验（字段、字数、素材 id、截图位置、去 AI 味、主题词）并给出提醒（夸大承诺、数字出处、贴纸）
python xhs.py preview plan.json --page 2      只出第 2 页
python xhs.py render plan.json [--out 目录]    全量出图，并拼 overview.png；检查文字溢出、留白、贴纸压字
python xhs.py check-post post.md              检查标题 3 个、标签、正文 400 到 800 字、删除测试记录
python xhs.py deliver plan.json post.md       交付：方案校验、正文检查、出图，三项都过才算完成
python xhs.py lint-text 文件.md                检查任意文字里的 AI 味表达
python xhs.py check-themes                    四套主题的对比度自检
python xhs.py selftest                        自检：词表、素材、示例、检查、出图
python xhs.py ui                              本地界面（给不用 agent 的人），也可双击 ui.bat
```

agent 的工作方式：先 `setup --status`，再 `list-types` 和 `list-assets` 看词表，按 nook-xhswrite 的关卡写方案（结构见 `references/schema.md`，12 个框架的示例见 nook-xhswrite 的 `references/plans/`），`deliver` 通过后看图。校验报错都写成“第 N 页（页型），字段 X：问题，怎么改”，照着改即可。退出码：0 通过，1 校验失败，2 出图时发现版面问题（文字放不下、标题过长、留白不足、贴纸压住文字）或出错，3 品牌未设置（先问用户，再 setup）。验收标准见 `references/acceptance.md`。

## 1.5 流程

内容层由 `nook-xhswrite` 负责：事实清单、一句话核心、框架、逐页提纲、素材需求清单，各有停止点，用户确认后才进入渲染。本 skill 接手的是确认过的提纲，工作是：

0. 确认品牌已设置（`setup --status`）；没有就先问用户，见 1.3。
1. 按提纲写方案 JSON（先 `list-types`、`list-assets`），页型和素材 id 只用词表里的。
2. `validate` 通过：它会检查字段、字数、素材 id、截图位置（必须在方案文件旁的 `inputs/` 里，由用户提供）、去 AI 味的表面表达，以及 `meta.subject_terms`（主题词必须出现在封面或第 2 页）。通过后还会提醒不该放的贴纸。`render` 会在出图后检查文字溢出和留白，页面太满报错（退出码 2）。
3. 先出封面候选给用户挑，再 `render` 全部。
4. 逐页看图，按用户意见改；不看图不说"做好了"。
5. 交付成套 PNG；图文下方的正文由 `nook-xhswrite` 写。

风格（mint / paper / dark / ticket）在提纲阶段由用户确认，同一篇从封面到内页用同一套。方案的 `meta` 写 `theme`（mint、paper、dark、ticket）、`title`、`subject_terms`（必填），可选 `no`（印在船票票根上的票号）。

船票风（ticket）是 nook 的品牌符号，只是其中一套视觉体系：蓝白，每页是一张船票，内容在票身，底部票根印账号名、条码、Logo 和票号。其他账号不一定用它，第一次设置品牌时选默认风格，别的风格不受影响。页面不画页码。

贴纸放不放的判断逻辑见 `nook-xhswrite` 的 1.3 节，实现在 `scripts/decor.py`。

## 1.6 硬规则

- 3:4 固定，页面不画页码，3 到 9 张，第一张封面，最后一张收尾或封底；相邻两页不用同一页型，一篇至少用 3 种页型。
- 不放二维码、联系方式、导流话术；封底只放名字和一句话。
- 不使用任何自动发布、自动评论工具，发布全人工。
- 不在图里使用他人品牌 Logo。
- 截图和成果图只用用户提供的，放进方案旁的 `inputs/`；agent 不自己找图，不用占位图或生成图冒充。
- 素材库里没有的贴纸，才考虑用本机 ComfyUI（Qwen Image 2.1）生成，提示词不要写 "hand-drawn"（会画出手），改写 "marker-doodle sticker icon"；线条类（箭头、下划线）由代码画，不用生成。

## 1.7 已知限制

- 字数上限和留白上限是按样片估的，使用中遇到误报或漏报，改 `spec.py` 和 `render.py` 里的 `COVER_LIMIT`。
- 贴纸候选按关键词匹配，会有牵强的，放之前要自己判断。素材库里文档、文件堆、搜索框、标签、笔记本电脑几个条目偏糊，可以按需用 `lib_items.py` 里的提示词重出。
- 手写字用的是随库分发的霞鹜文楷，不是真正的手写体；需要别的字体时换 `assets/fonts/` 并改 `pages_hand.py` 的 CSS。
- 通用款人物薄荷和船长款人物都随库附带：薄荷是本库自生成的虚拟人物，任何人可直接用；船长款属于作者本人，只在 `--captain` 时使用。
- 在 Codex、Antigravity、Trae、OpenCode 上的试跑需要手动做，见 `references/acceptance.md` 第 4 节。

## 1.8 硬规则（执行时必须遵守，脚本会检查其中大部分）

1. **事实只来自素材。** 图上出现的每个数字、日期、版本号，都必须逐个写进 `meta.facts`（每条带素材里的原句）。`validate` 对方案文件夹在 skill 目录之外的方案强制执行：找不到就退出码 1。素材没给的日期、数字、因果，不写；不要自己补“合理的”数字。
2. **推测不能写成结论。** 素材里是“可能、说不定、我猜”的内容，图上也要带这个语气；标题和页面里不能出现“真相、内幕、揭秘、实锤”。
3. **版面放不下时只能缩短文字，不能换内容。** `render` 报溢出、压字、标题过长时，把原来的那句话删减到更短；不许换成另一个数字或另一件事来躲过检查。
4. **不许修改 skill 目录里的任何文件**（scripts、assets、references）。发现版面缺陷，只在报告里写明“哪个页型、什么现象、怎么复现”，由 skill 维护者修；自己的方案换页型或缩短文字绕开。
5. **关卡不能跳。** facts.md、outline.md、needs.md、covers.md 和 plan.json 放在同一个文件夹，缺任何一个 `render` 都会拒绝（`preview` 至少需要 facts.md 和 outline.md）。封面候选要给用户挑，用户没选之前不全量出图。
6. **汇报要照实。** 只报告命令实际的退出码和输出；有提醒就列出，有没验证的就说没验证；不写“全部对应原文”“全部通过”这类没有逐项核对过的话。
7. skill 自带目录里的示例方案只做提醒级检查，不能当成交付物，`deliver` 会拒绝。
