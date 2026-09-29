---
name: nook-anim
description: 代码渲染为主的短视频动画生产 skill。用户要做动画短片、Logo 片头动效、定格动画、手绘/白板讲解动画、火柴人小剧场、MG 动效与数据信息图、水墨/撕纸风短片、口播 B-roll 动画与章节标题卡动画（给教程、科普视频配画面）、歌词 MV 画面，或要求"用代码做视频""不用视频模型做动画"时使用。按内容类型选叙事骨架、按风格卡选技术路线，生图补足角色与场景（本地 ComfyUI Qwen Image 2.1），配乐走 MiniMax Music3 并由代码对拍，最后用 nookanim 引擎逐帧渲染成片。不用于单纯剪辑已有视频素材或只要一张图。
---

# 1 nook-anim

把一个内容需求做成一条动画短视频。画面由代码渲染为主，生图补足代码画不出的角色和场景，生视频默认关闭。用到的模型（千问 Image 2.1、MiniMax-Music3）的使用条款，以各自官方仓库的 LICENSE 为准。

设计说明：本 skill 由作者在 Obsidian 里的设计蓝本演化而来，正文即当前有效版本；后续改动直接改本 skill。

## 1.1 生产流程

每一步完成后再进下一步。标"把关"的节点把产物给用户过目；用户明确说"一路做到成品、不要再核对"时，只在最后交付成片。

1. 定内容类型与叙事骨架。读 [references/content.md](references/content.md)。
2. 选风格卡。读 [references/styles/](references/styles/) 下对应的卡；风格卡决定技术路线和素材清单模板。技术路由规则见 [references/tech-routing.md](references/tech-routing.md)。
3. 写一句话情节和节拍表。（把关）
4. 拆分镜表：每个镜头的时长、机位、画面节点、角色排期、代码任务、声音、素材。格式见 content.md。
5. 列素材清单，按三级出图：原素材 → 组合素材 → 首帧。读 [references/image-gen.md](references/image-gen.md)。角色定稿。（把关）
6. 标注坐标：场景里的平面四角、角色锚点与接触点（笔尖、帆尖、眼睛）。用预览工作台点击取坐标。
7. 写场景文件 `scene.py`，接口见 [references/scene-api.md](references/scene-api.md)。
8. 动态分镜：素材缺的用灰色剪影占位，先跑通全片节奏；抽帧拼图自查后给用户。（把关）
9. 补齐素材、按反馈精修。每轮改完先抽帧检查再整片渲染。
10. 配乐与对拍：读 [references/music.md](references/music.md)。先按官方 music-caption-rewriter 生成 caption，并向用户确认 brief。
11. 正片：去掉镜头号，对拍渲染，从最终 mp4 抽帧质检后交付。（把关）质检按 [references/checklist.md](references/checklist.md) 逐条对照，规则的来由在 [references/rules.md](references/rules.md)；"已验证"只根据成片下结论，不根据流程走完下结论。

## 1.2 硬规则

全部规则与来由见 [references/rules.md](references/rules.md)。最常踩的几条：

- 角色一律原创（例如 Captain Nook），不画知名 IP 角色。
- 给出图模型的提示词只写要什么。否定句、参考图里的多余元素，都会被带进画面。
- 同一角色的所有姿势都从同一张母版编辑；两样东西在镜头里一起动，就做成一张组合素材。
- 场景道具放进场景坐标（底部落在桌面/纸面、接触阴影、按景深轻虚化），不做成贴在屏幕上的图层。
- 每帧只由时间 t 决定。整片渲染前按镜头抽帧拼图检查。渲染时让用户能看到进度（预览工作台）。
- 配乐的时长和速度不听提示词：生成更长的音乐 → 测真实节拍 → 截取补收尾 → 让画面对音乐。

## 1.3 引擎

引擎代码在 `scripts/nookanim/`（v0.5.0），Python 3.10 以上（3.14 实测可用），依赖 numpy、opencv-python、pillow、scipy、imageio-ffmpeg。风格模块：sketch（手绘线稿）、collage（撕纸拼贴）、wash（水墨）、stick（火柴人）、mg（扁平动态图形），其余为通用模块，见 [references/scene-api.md](references/scene-api.md)。机器相关设置（ComfyUI 地址、字体、ffmpeg、音乐工作流）用环境变量覆盖，见 `scripts/nookanim/config.py`。

```bash
# run.py 会自动把 scripts/ 加入 sys.path，任何电脑上都不用设 PYTHONPATH；下面的 <S> 指本 skill 的 scripts 目录
python <S>/run.py comfy image jobs.json --out 素材                                  # 出图
python <S>/run.py render path/to/scene.py stills 3.5 7.9 --labels                  # 静帧
python <S>/run.py render path/to/scene.py sheet --every 1.5                        # 抽帧拼图自查
python <S>/preview_launcher.py path/to/scene.py --port 8765                        # 预览工作台（含渲染进度、点击取坐标）
python <S>/run.py comfy music --caption cap.txt --max 30 --seeds 301,302 --out music   # 配乐（需 NOOKANIM_MUSIC_WORKFLOW）
python <S>/run.py music music/music_s301.mp3 --dur 20 --end-by 19.3 --anchors 3,6,9 --out-dir .
python <S>/run.py render path/to/scene.py video --out film.mp4 --audio final_mix.wav --warp warp.json
```

场景文件里的素材路径一律写成相对 `scene.py` 的路径（`pathlib.Path(__file__).parent / "素材"`），这样工程目录在任何电脑、任何盘符下都能直接渲染。

样例工程（在本 skill 的 `examples/` 里，可直接渲染）：

- `examples/02_draw_direction/`《画个方向》手绘线稿、纯代码，完全基于引擎写成，写新场景时照它起步。
- `examples/05_last_pizza/`《最后一块披萨》火柴人、纯代码，含代码合成音效。
- `examples/06_cat_day/`《一只猫的一天》扁平动态图形、纯代码，含代码合成音效与配乐。
- `examples/tutorial_kit/` 教程视频 Broll 与章节标题的共用件（桌面舞台、玻璃卡片、图标、角色走路、标题动效与音效）加一条 Broll、一条标题和批量渲染脚本。角色姿势、桌面背景、标题字 PNG 由千问出图，素材不随库提供，做法见 [references/image-gen.md](references/image-gen.md)。给口播视频配画面时照它起步，流程见 [references/content.md](references/content.md) 的"给口播视频配 Broll 与标题"，风格见 [references/styles/07_教程桌面舞台.md](references/styles/07_教程桌面舞台.md)。

用法：`cd examples/05_last_pizza && python <S>/run.py render scene.py video --out film.mp4`，`<S>` 是本 skill 的 `scripts/` 目录。撕纸拼贴、水墨水彩、纸片定格三种风格的样例依赖千问出的素材，没有随库提供，写法见各自风格卡。

## 1.4 交付

项目文件夹按 `成片/`、`过程图/`（JPG）、`工程/`（scene.py、音效与配乐脚本、warp.json、配乐源 mp3、`素材/` PNG）组织。mp4 体积大，用 git 管理的项目需要在 `.gitignore` 里为成片目录加例外。项目笔记里记下素材清单、踩坑与修正。
