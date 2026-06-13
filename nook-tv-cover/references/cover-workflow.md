# 视频封面生成工作流

## 用户引导

封面任务开始时，一次性收集或推断这些信息：

- 人物图：先让用户上传人物参考图。可以是真人口播截图、真人白底图、IP 图、白底 IP 图、半身图或场景图。
- 人物图处理：确认人物需要保留哪些身份特征、服装、发型、麦克风或道具；如果是场景图，默认需要抠出人物主体并弱化原背景；如果是白底图，默认直接分离人物。
- 平台：长封面（YouTube）、短封面（B站）、竖封面（抖音/小红书/视频号）。
- 标题：没有标题时先用临时标题出 draft。
- 内容主题：教程、工具评测、观点、案例复盘或产品发布。
- 人物来源：真人 / IP / 白底图 / 场景图。默认优先保留身份，不替换脸，不替换服装。
- 风格：默认科技风；也可以让用户从科技证据层、真人实景压暗、产品界面主视觉、高饱和爆款、极简大字中选。
- 参考图：默认风格参考图必带，人物参考图按平台选择，主题素材可选。
- 候选数量：默认先出 1 张烟测图，通过后再批量出 2-4 张。
- 文案锁定：批量生成前必须锁定主标题、副标题和英文标签；同一批次变体必须逐字一致。
- 透视锁定：批量生成前必须锁定标题透视方向、倾斜角度、字厚度、描边、阴影和渐变强度；同一批次变体必须保持一致。

不要反复问零碎问题。能安全推断时直接推断，并在结果里说明。

### 推荐提问顺序

1. 请先上传人物参考图。真人口播截图、白底图、IP 图、场景图都可以。
2. 这次封面讲什么内容？给一句主题或视频标题也可以。
3. 你想用哪个标题？如果没有，我先给你 3 个候选。
4. 要生成哪类封面：长封面、短封面、竖封面，还是三类全部？
5. 风格选哪一套：科技证据层、真人实景压暗、产品界面主视觉、高饱和爆款、极简大字，还是默认科技风？
6. 有产品截图、Logo、界面图或其他素材要放进封面吗？
7. 先出 1 张烟测图，还是每类直接出 2-4 张候选？

### 人物图类型

真人口播截图：

- 保留真实脸型、五官关系、发型、服装、麦克风、支架和口播气质。
- 人物必须做风格迁移，不能把实拍人物硬贴到虚拟背景上。

真人白底图：

- 默认先把人物从白底中分离出来。
- 可以换背景，但不能换脸或换服装。

IP 图：

- 可以用于视频封面，但必须是用户明确提供或明确要求。
- 保留 IP 形象识别度，不改成真人。

场景图：

- 默认识别人像主体，把人物从原场景中分离。
- 原背景可以压暗、虚化、保留为实景背景，也可以替换为虚拟背景。

### 抠图和背景分离要求

本 skill 必须具备人物分离意识。提示词中要明确：

- isolate the person from the original background
- preserve identity, face, hair, clothing, microphone and key props
- remove or de-emphasize the original background when using a virtual cover background
- keep clean edges, no dirty cutout halo, no pasted-photo look

如果模型输出出现硬贴、脏边、背景混乱，应优先重跑人物分离，而不是只调标题。

## 默认风格

默认使用“科技风封面风格”。

核心结构：

- 深蓝黑底，青蓝、蓝紫、品红少量点缀。
- 大标题是第一视觉，必须有透视、粗描边、厚阴影和渐变。
- 默认标题使用强透视字效；同一批次保持相同倾斜方向、相近倾斜角度、相同厚度、描边、阴影和渐变强度。
- 人物是第二视觉，通常在右侧或三分之一位置。
- 视频人物必须压住标题边缘，让人物进入标题层级；标题保持可辨认即可，不要求完整无遮挡。
- 视频人物必须保持原始比例，不能为了填满画面而放大；人物从头顶到可见身体底部默认只占画布高度约 65%，画面顶部到人物头顶默认留出约 35% 空白。
- 工具界面、代码窗口、产品截图、箭头和标签构成内容证据层。
- 画面要像同一个账号的长期封面系统，而不是每期随机换风格。
- 文字默认做 2 到 3 排，保留大标题、小标题和可选补充短语。
- 文字需要中英文混排，英文必须拼写准确。
- 装饰元素可以适当增加 HUD、文本框、代码块、界面碎片、标签条和小注释。

默认风格参考：

`assets/style/figma-codex-cover-style-reference.webp`

正式风格参考：

`assets/style/figma-codex-cover-style-reference.webp`

## 平台尺寸

### 长封面

适用：YouTube。

- YouTube：`1280x720`

### 短封面

适用：B站。

- B站：`1146x717`

### 竖封面

适用：抖音、小红书、视频号竖版。

- 比例：`3:4`
- 推荐生成尺寸：`1242x1660`
- 竖屏强标题要放在上半部，人物和证据层不能被平台 UI 遮挡。

## 人物规则

视频平台：

- 默认使用用户提供的真人口播截图。
- 如果用户提供 IP 图、白底图或场景图，也可以使用，但必须在 prompt 里明确它是人物参考图，不是公众号默认 IP。
- 以实际人脸为准，服装必须与口播画面一致。
- 可以适当美化，但不能认不出。
- 麦克风、支架、桌面口播场景等关键元素尽量保留。
- 不能使用公众号 IP 代替真人。
- 必须把真人整体重绘成与封面背景统一的海报化/插画化人物。
- 不允许保留原始实拍质感后直接贴到科技背景上。
- 需要抠图或背景分离时，必须保持人物边缘干净，避免白边、脏边、硬贴感。
- 横屏人物整体高度默认约为画布高度 65%；人物不能顶到上边缘，头顶上方需要约 35% 画布高度的呼吸空间。
- 人物应作为前景遮住标题一小段边缘，遮挡范围以不影响标题识别为准。
- 风格偏移要克制：真人基础上轻微卡通化，不要变成纯漫画人物。
- 皮肤要干净自然，避免脏污纹理、过重颗粒、蜡像感和塑料感。
- 可以使用清晰描边或边缘光，让人物更适合科技封面。

## Prompt 模板

```text
Use case: ads-marketing
Asset type: <平台> cover
Primary request: 生成一张科技风封面风格的封面。
Input images:
- Image 1: style reference, use for color, typography energy, composition density, tech texture.
- Image 2: character/person reference, preserve identity and role.
- Image 3: optional topic material, use only as content evidence.
Canvas: <比例和尺寸>
Text (verbatim): "<标题>"
Copy lock: for every image in the same batch, use the exact same title, subtitle, and English tag verbatim. Do not rewrite copy between variants unless the user explicitly asks for copy testing.
Perspective lock: use strong perspective typography. Keep the same title slant direction, similar slant angle, same extrusion thickness, outline weight, shadow depth, and gradient intensity for all variants in the same batch. Do not mix flat text with perspective text.
Composition: giant title as first visual; character as second visual; UI/code/tool evidence as third visual. For video covers, place the character in the foreground overlapping the title edge; keep the title recognizable, not perfectly unobstructed. Keep the character's original proportions. The visible character height, from top of head to bottom of visible body, should be about 65% of canvas height. The empty space from the top edge of the canvas to the top of the head should be about 35% of canvas height.
Character extraction: isolate the person from the original background when needed; preserve identity, face, hair, clothing, microphone and key props; remove or de-emphasize the original background for virtual backgrounds; keep clean edges with no pasted-photo look.
Style: dark blue tech background, cyan/magenta/purple highlights, bold outlined title, thick shadow, slight distressed texture, dynamic arrows and interface panels.
Constraints: keep Chinese text readable; keep 2-3 rows when possible; include large title, small subtitle, and optional short line; maintain perspective; mix Chinese with a bit of English/tag feel; no pseudo text in main title; no watermark; do not copy unrelated brand logos from references.
Avoid: WeChat/public-account cover, article cover, IP character, minimal flat poster, business-blue template, soft illustration, random cyberpunk clutter, wrong character source, wrong clothes, wrong platform ratio.
```

## 验收标准

每张封面必须检查：

- 第一眼能读标题。
- 第二眼能看到人物。
- 第三眼能理解主题证据。
- 标题没有错字、伪字和严重糊字。
- 同一批次所有成品的主标题、副标题和英文标签逐字一致。
- 同一批次标题透视方向、倾斜角度、字厚度、描边、阴影和渐变强度一致。
- 人物来源符合平台规则。
- 视频人物保持原比例，没有被拉伸、压扁或放大填满画面。
- 视频人物垂直高度约为画布高度 65%，头顶上方约有 35% 画布高度的呼吸空间。
- 视频人物压住标题边缘，并形成前景遮挡关系。
- 平台裁切后主体不丢失。
- 和默认参考图属于同一套视觉系统。
- 最终图已经保存到项目输出目录。
