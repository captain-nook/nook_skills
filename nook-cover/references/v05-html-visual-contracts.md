# V05 HTML 可执行视觉合同

本文件解决一个核心问题：不要只写“好看、爆款、小红书感”，而要把风格拆成 HTML / CSS / Playwright 可以执行的构图、文字和辅助元素合同。

如果当前运行时没有 image2.0 或外部出图工具，HTML 路线也必须尽量接近“小红书封面设计”，而不是退化成普通照片加字。

## 0. 来自高质量 image2.0 样张的可执行语言

昨天效果好的 image2.0 样张不是普通生活照。它成立的原因是：

- 主标题占画面 45%-55%，不是顶部小标题。
- 标题是贴纸化大字：红字、白描边、黑硬阴影、错位堆叠、轻微倾斜。
- 标题本身就是主视觉，人物是第二视觉。
- 背景不是安静照片，而是红黄撕纸和纸张纹理构成的高能画布。
- 辅助元素不是按钮，而是星星、箭头、手绘线、便签、撕纸、胶带。
- 人物表情有反应，眼睛和嘴巴清晰，手势指向标题或前景物。
- 前景道具贴纸化，有白描边和投影，不像菜单按钮。

把它翻译成 HTML 语言：

```text
canvas: 1080x1440
title_layer: absolute, z-index 30, width 58%-72%, height 38%-55%
title_text: 92-150px, font-weight 900, line-height .86-.98
title_effect: text-shadow 多层白描边 + 黑色硬阴影
title_transform: rotate(-8deg to 4deg), skew(-6deg to 4deg)
paper_layer: irregular torn paper blocks behind title, z-index 10-20
person_layer: z-index 15-25, safe zone preserved
sticker_layer: stars/arrows/tape/badges, z-index 35
background_layer: high-saturation blocks or dimmed photo, not dominant
```

HTML 做不到的部分：

- 真实人脸、真实人物表情、真实菜品、真实产品图。
- 这些必须来自 image2.0、外部原子工具或用户素材。

HTML 必须做到的部分：

- 标题大小、位置、描边、阴影、倾斜、分行。
- 撕纸 / 贴纸 / 胶带 / 箭头 / 星星 / 便签。
- 背景压暗、模糊、遮罩，让设计层成为主体。
- 人脸安全区避让。
- 缩略图可读。

## 1. 全局 HTML 原语

所有模板都只能使用这些可实现原语组合，不要写虚的审美词。

### 1.1 大字贴纸标题

```css
.title-sticker {
  position: absolute;
  z-index: 40;
  font-size: clamp(92px, 11vw, 150px);
  line-height: .88;
  font-weight: 950;
  letter-spacing: 0;
  color: #f11919;
  text-shadow:
    6px 0 #fff, -6px 0 #fff, 0 6px #fff, 0 -6px #fff,
    12px 14px 0 #111;
  transform: rotate(-5deg) skew(-4deg);
}
```

执行要求：

- 主标题必须拆成 2-3 行。
- 标题区域占画面高度 35%-55%。
- 至少一个关键词放大 1.15-1.35 倍，例如 `30天`、`不挨饿`、`别瞎搞`。
- 不能只放在顶部 20% 区域。

### 1.2 撕纸块

HTML 可用 `clip-path: polygon(...)` 做不规则边缘，配合伪元素制造毛边。

```css
.torn-paper {
  position: absolute;
  background: #fff7df;
  filter: drop-shadow(10px 12px 0 rgba(0,0,0,.22));
  clip-path: polygon(
    0 8%, 7% 3%, 15% 7%, 24% 2%, 36% 6%, 46% 3%,
    58% 8%, 71% 2%, 84% 7%, 100% 4%,
    97% 96%, 88% 92%, 75% 98%, 61% 93%, 48% 98%,
    33% 94%, 19% 99%, 8% 93%, 0 97%
  );
}
```

执行要求：

- 撕纸不能是普通圆角矩形。
- 至少 2 层纸片，角度不同。
- 纸片必须和标题或标签发生关系：承载标题、垫在标题后、制造对比卡。

### 1.3 胶带

```css
.tape {
  position: absolute;
  width: 150px;
  height: 44px;
  background: rgba(255, 202, 94, .72);
  transform: rotate(-8deg);
  mix-blend-mode: multiply;
}
```

执行要求：

- 胶带必须压住纸片边角。
- 至少出现 2 条，角度不同。

### 1.4 手绘箭头

HTML 可用边框和伪元素做粗箭头。

```css
.arrow {
  position: absolute;
  width: 130px;
  height: 80px;
  border-bottom: 12px solid #fff;
  border-right: 12px solid #fff;
  transform: rotate(-18deg) skew(-8deg);
  filter: drop-shadow(5px 6px 0 #111);
}
```

执行要求：

- 箭头必须指向标题、人物动作、前景道具或对比卡。
- 不能只是角落装饰。

### 1.5 星星 / 爆炸贴纸

可用文字符号、CSS 多边形或小块组合。

```css
.star {
  position: absolute;
  z-index: 45;
  font-size: 58px;
  color: #ffd92e;
  -webkit-text-stroke: 8px #fff;
  text-shadow: 7px 8px 0 #111;
}
```

执行要求：

- 星星必须分布在标题周围，强化标题轮廓。
- 不要平均撒满全图。

### 1.6 前景贴纸物

当有菜品、产品、截图、卡片时，HTML 必须把它们当贴纸处理。

```css
.foreground-sticker {
  position: absolute;
  z-index: 35;
  border: 8px solid #fff;
  border-radius: 32px;
  box-shadow: 14px 16px 0 rgba(0,0,0,.28);
  transform: rotate(-4deg);
}
```

执行要求：

- 贴纸物可以是图片、卡片、菜名、截图框。
- 不要做成三个等宽按钮。
- 至少一个前景物与标题有重叠或指向关系。

## 2. 四套视觉系统合同

### 2.1 人脸冲击封面

风格承诺：

```text
人物表情 + 超大贴纸标题 + 前景道具 + 高能手绘标注。
不是生活照，不是菜单页。
```

构图合同：

```text
person_box:
  x: 42%-72%
  y: 18%-78%
  w: 32%-48%
  h: 48%-68%

title_box:
  x: 4%-58%
  y: 8%-48%
  w: 58%-72%
  h: 38%-52%

foreground_box:
  x: 4%-58%
  y: 58%-86%
  w: 42%-64%
  h: 18%-28%

decor_density:
  8-14 items: stars, arrows, tape, badges, hand-drawn strokes
```

HTML 必须实现：

- `title-sticker`：红 / 白 / 黑三层大字。
- `torn-paper`：标题后至少一层撕纸底。
- `arrow`：至少 1 个箭头指向标题或人物手势。
- `star`：至少 3 个围绕标题。
- `badge`：1-2 个强爆点，如 `30天挑战`、`吃饱也能瘦`。

出图模型 / 用户素材负责：

- 真人半身。
- 表情和手势。
- 真实菜品、产品或场景。

失败判定：

- 标题只在顶部。
- 人物没有动作表情。
- 画面像生活照。
- 底部按钮式菜名。
- 标题面积低于 35%。

减脂主题专用文案骨架：

```text
title_lines: ["减脂30天", "家常菜谱", "不挨饿"]
badges: ["30天挑战", "吃饱也能瘦"]
foreground_stickers: ["鸡胸沙拉", "西兰花豆腐", "糙米蛋饭"]
arrows: ["指向不挨饿", "指向菜品贴纸"]
```

### 2.2 手账拼贴种草

风格承诺：

```text
多层纸片 + 胶带 + 照片贴纸 + 手绘圈画。
像手账墙，不像整齐信息卡。
```

构图合同：

```text
main_photo_or_object:
  x: 38%-78%
  y: 24%-72%
  w: 38%-52%
  h: 38%-56%

title_papers:
  count: 2-4
  x: 6%-58%
  y: 8%-46%
  rotation: -8deg to 8deg

small_notes:
  count: 3-6
  around main object
```

HTML 必须实现：

- 3 层以上 `torn-paper`。
- 2 条以上 `tape`。
- 标题分布在不同纸片上。
- 手绘箭头 / 圈画 / 虚线至少 3 个。
- 背景纸张纹理或点阵。

失败判定：

- 一张大白纸承载全部标题。
- 纸片边缘太规整。
- 所有元素平行且居中。
- 像 PPT 卡片。

### 2.3 产品截图主视觉

风格承诺：

```text
产品 / 截图是主视觉，标题压在产品边缘或背后，人物只是引导。
```

构图合同：

```text
product_panel:
  x: 12%-88%
  y: 28%-78%
  w: 68%-82%
  h: 38%-52%
  transform: rotate(-4deg to 4deg) perspective

title_box:
  x: 6%-82%
  y: 6%-36%
  w: 70%-88%
  h: 24%-36%

person_optional:
  x: 60%-88%
  y: 52%-86%
  w: 18%-30%
```

HTML 必须实现：

- 一个大截图框或产品框，带厚边框、阴影、倾斜。
- 标题必须贴到截图边缘，不做普通顶部标题。
- 1-3 个小标签即可，避免信息块堆满。
- 箭头指向截图中的关键区域。

失败判定：

- 截图太小。
- 标题被 UI 抢走。
- 像 SaaS 官网 hero。

### 2.4 近大远小对比封面

风格承诺：

```text
前景对比卡近大远小，人物在中景推出，标题斜压进画面。
```

构图合同：

```text
foreground_compare_card:
  x: 6%-78%
  y: 48%-84%
  w: 60%-82%
  h: 24%-36%
  transform: perspective(900px) rotate(-6deg) skew(-8deg)

title_box:
  x: 4%-72%
  y: 6%-42%
  w: 70%-88%
  h: 30%-44%

person_box:
  x: 54%-86%
  y: 24%-78%
  w: 28%-42%
```

HTML 必须实现：

- 一个明显的透视前景卡。
- 卡片里有 `以前 / 现在` 或 `错误 / 正确`。
- 粗箭头连接前后关系。
- 标题带倾斜和硬阴影。

失败判定：

- 没有透视卡。
- 只有普通对比列表。
- 人物和卡片没有关系。

## 3. Agent 执行格式

生成前，agent 必须把所选视觉系统翻译为结构化 brief：

```json
{
  "visual_system": "人脸冲击封面",
  "layout_contract": "face-impact-v05",
  "title_lines": ["减脂30天", "家常菜谱", "不挨饿"],
  "html_primitives": {
    "title": "title-sticker",
    "papers": ["torn-paper:title-back", "torn-paper:badge"],
    "decor": ["arrow:title", "star:title-left", "star:title-right", "tape:paper-corner"],
    "foreground": ["food-sticker-1", "food-sticker-2", "food-sticker-3"]
  },
  "composition_contract": {
    "title_box": { "x": 0.04, "y": 0.08, "w": 0.68, "h": 0.44 },
    "person_box": { "x": 0.46, "y": 0.20, "w": 0.42, "h": 0.58 },
    "foreground_box": { "x": 0.06, "y": 0.62, "w": 0.58, "h": 0.22 }
  },
  "qa_contract": [
    "title_area >= 35%",
    "not app menu",
    "not quiet lifestyle photo",
    "has at least 8 decorative primitives",
    "chosen visual system recognizable at first glance"
  ]
}
```

没有这份 brief，不允许直接渲染。

## 4. HTML 验收优先级

验收时按下面顺序判断：

1. 是否一眼能看出属于哪套视觉系统。
2. 主标题是否是第一视觉。
3. 构图是否符合合同坐标。
4. 文字效果是否贴纸化、描边、倾斜、硬阴影。
5. 辅助元素是否参与叙事，而不是装饰垃圾。
6. 人脸是否安全。
7. 中文是否正确。

中文正确但视觉系统不成立，仍然判定失败。

## 5. 当前 V05 模板路径

V05 的四套 HTML 合同模板目前由同一个渲染器读取不同 brief 实现：

```text
renderer:
scripts/render-xhs-v05-contract.cjs

briefs:
examples/xhs-v05/face-diet-brief.json
examples/xhs-v05/scrapbook-cafe-brief.json
examples/xhs-v05/product-ai-brief.json
examples/xhs-v05/compare-fitness-brief.json
```

运行方式：

```bash
node scripts/render-xhs-v05-contract.cjs examples/xhs-v05/face-diet-brief.json output/v05-face-diet
```

没有安装 Playwright 时，可以先生成 HTML：

```bash
node scripts/render-xhs-v05-contract.cjs examples/xhs-v05/face-diet-brief.json output/v05-face-diet --html-only
```
