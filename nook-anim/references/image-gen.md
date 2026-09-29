# 出图：本地 ComfyUI Qwen Image 2.1

提示词写法以官方仓库 [Qwen-Image-2.1](https://github.com/QwenLM/Qwen-Image-2.1) 的提示词规范为准（观察者视角、透明图固定前后缀、编辑用 `<image1>` 指代参考图）。本篇只写动画生产里的用法。

## 1 通道

草稿、批量、测试一律走加速通道：UNET `qwen_image_2.1_int8_convrot` + 8 步加速 LoRA `p_qwen_image_2.1_8step_v0.1`，CFG 1.0，euler + simple。编辑模式用官方节点 `TextEncodeQwenImage21` 接参考图，画布用它输出的 latent（跟随第一张参考图），加速通道也能做编辑。3060 12G 上每张约 15–30 秒。定稿需要更高质感时再切官方原始工作流。

没装加速 LoRA 的机器（报 `lora_name ... not in` 的 400 错误），在 jobs 里写 `"lora": null`，引擎自动去掉 LoRA 节点、改用 25 步和 CFG 1（同官方模板），也可以用 `"steps"`、`"cfg"` 自己指定。5060 Ti 16G 上三张 1024×768 编辑图在排队后约数分钟出完。

`python <S>/run.py comfy image jobs.json --out 素材` 批量提交（`<S>` 指本 skill 的 scripts 目录），jobs.json 的字段见 `scripts/nookanim/comfy.py` 顶部说明。

速度参考：有 8 步加速 LoRA 时，3060 12G 每张约 15–30 秒；没有加速 LoRA（25 步）时，5060 Ti 16G 上 1024×768 的编辑图每张约 1–2.5 分钟，2048×640 的标题字每张约 30–60 秒。

**许可**：以千问 Image 2.1 官方仓库的 LICENSE 为准。

## 2 三级素材

原素材：人物全身像、每件道具、场景，各出一张单独的。之后所有出图都以它们为参考。

组合素材（透明底）：多图参考生成，"让 `<image1>` 的人物抱着 `<image2>` 的笔"。判断标准是两样东西在镜头里是否一起动。

首帧：每个镜头一张完整场景，作为比例、位置、阴影方向的对位参考；人物静止的段落可以直接用首帧配代码推镜。

## 3 提示词模板

角色风格基准句（纸片定格）：paper cut-out cartoon character, flat hand-drawn illustration with watercolor and colored pencil texture, clean dark outlines, a thin white paper border around the whole silhouette like a sticker cut out from paper.

姿势编辑（从母版）：Keep the boy from `<image1>` exactly as he is: his face, hair, clothes, … and the flat hand-drawn paper cut-out style with a thin white paper border. + 动作描述（只写要什么）。

组合动作：在上面基础上加 Keep the giant marker from `<image2>` exactly as it is: … 再写两者的空间关系与接触方式。

船上状态（以人船组合图为母版）：换姿势时给目标姿势的独立参考图，写 Replace the boy in `<image1>` with the boy from `<image2>` in his exact … pose, at the same size, standing inside the hull …

局部小改（眨眼）：Keep everything in `<image1>` exactly the same … Change only his left eye … 这类局部编辑很稳，可替代代码画眼皮。

## 4 挑图

每轮出图后拼成棋盘格底的对照图检查：角色是否走样、透明边缘是否干净、道具是否分裂、方向是否正确（方向反了可以代码水平翻转）。

## 5 标题字：千问出"纯文字透明 PNG"，代码做动效

需要有设计感的立体标题字（章节卡、主标题）时，字交给千问出透明底 PNG，动效和音效用代码：
文字保证是千问渲出来的原字，代码只负责下落、压扁回弹、波浪逐字起跳、扫光、震屏、彩纸和音效，不切开字形。实测 2048×640 一张约 30–60 秒；出完必须逐张核对字有没有错（中文、中英混排都要看）。

提示词骨架（文生图 + RGBA 包装，中文文字放双引号里）：
`The image features the title "……" as huge glossy italic lettering, centered. Every character is extremely bold with thick rounded strokes and leans forward ten degrees. Each character is filled with a bright high-key glossy gradient: luminous sky cyan at the upper left, fading through pale periwinkle blue and near-white lavender in the middle, to soft orchid pink at the lower right, so the letters look light, airy and shiny rather than dark. A large soft white specular highlight covers the top third of every stroke. A thick deep navy blue outline surrounds every character, with a thin bright electric blue neon line just outside it. A solid dark navy extrusion gives the letters a heavy three-dimensional side face falling toward the lower right, and a soft cyan neon glow radiates around the lettering. Short neon slash accents in cyan and yellow fan out near the upper left and upper right corners. The lettering fills most of the canvas width ... The image contains only the lettering and its accents.`

颜色要写成"明亮、通透、高调"的走向，不要写"紫、洋红"：写成"蓝到紫到洋红"出来的是深紫暗沉的字，和封面对不上。两行的主标题用 1600×1024，其余用 2048×640，两个字的用 1280×640。

## 6 桌面舞台与走路姿势

整期共用一张千问出的"虚化工作室 + 桌面"背景，角色站在桌面线上，信息面板浮在半空，下方留给字幕。背景提示词的要点：低机位、桌面横贯画面下方五分之一、左边一摞纯色书脊的书、右边一个黑杯子、桌面中间空着、背后完全虚化的深蓝工作室、青色环境光加琥珀色桌沿光。
角色走路：以站姿为母版编辑出两张迈步姿势（一张右腿在前、一张左腿在前），运行时两帧交替，加上下起伏和轻微摇摆。
