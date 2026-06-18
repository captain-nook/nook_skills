# V04-2 提示词模板

本文件给 agent 执行时直接套用。每次生成前，先替换主题、标题、人物、场景和标签。

## 通用约束

所有小红书封面都必须满足：

```text
vertical 3:4 Xiaohongshu cover image.
Huge simplified Chinese headline, readable in thumbnail.
The headline must be the first visual element and occupy about 35%-45% of the image.
If there is a person, show upper body from waist to head with torso and hands visible, not a headshot.
No text covering eyes, nose, or mouth.
No watermark, no QR code, no English text.
Avoid dead empty space.
Not corporate PPT.
Not a lifestyle app screen.
No neat bottom navigation buttons.
No quiet documentary photo with tiny title.
The design layer must dominate the photo layer.
```

## 人脸冲击封面

```text
Use case: ads-marketing
Asset type: Xiaohongshu cover image, vertical 3:4 mobile cover
Style system: 人脸冲击封面, also known internally as 人物冲击贴纸风, viral Chinese social media cover.
Primary request: Create a viral Xiaohongshu cover about {topic}, not a clean lifestyle photo.
Scene/backdrop: bright high-saturation social media cover scene, warm coral and matcha green accents, visible stickers and torn paper layers.
Subject: Asian {gender} creator, {age}, visible upper body from waist to head with torso and hands visible, expressive surprised / excited / confident face, actively pointing or holding a foreground object, not a passive lifestyle portrait, not a headshot.
Composition/framing: person on the right or center-right occupying 40%-50%; huge headline on left and upper center occupying 40%-50%; foreground food/product/object card close to camera; no dead empty space.
Text (verbatim): "{title_line_1}\n{title_line_2}"
Small labels: "{label_1}", "{label_2}".
Typography: huge bold simplified Chinese, red / white / hot pink, thick black outline, hard sticker shadow, slight perspective tilt, title larger than the face.
Design details: irregular torn-paper stickers, star stickers, hand-drawn arrows, highlight strokes, speech bubbles, before/after mini cards, energetic Xiaohongshu style.
Constraints: exact readable Chinese text; no text covering eyes, nose, mouth; no watermark; no QR code; no English text; no neat green bottom menu buttons; no app UI cards; no quiet clean recipe poster.
```

### 人脸冲击封面：减脂 / 食谱专项补充

当主题是减脂、菜谱、健身餐、家常菜时，必须强化“爆款封面”而不是“食谱 App”：

```text
Food/fitness cover add-on:
Use one expressive Asian woman creator in apron or sport-casual outfit, upper body visible, excited expression, pointing at huge headline.
Show 2-3 healthy dishes as foreground stickers or cutout plates, close to camera, with thick white outlines and shadow, not arranged as neat menu buttons.
Add a strong contrast badge such as "30天挑战", "吃饱也能瘦", "一周不重样".
Use big diagonal title blocks and torn-paper labels.
Avoid calm kitchen lifestyle photography, avoid soft beige minimalism, avoid bottom tab/menu layout, avoid three equal green buttons.
The cover must look like a viral Xiaohongshu thumbnail, not a recipe app page.
```

## 手账拼贴种草

```text
Use case: ads-marketing
Asset type: Xiaohongshu cover image, vertical 3:4 mobile cover
Style system: 手账拼贴种草, also known internally as 撕纸手账种草风.
Primary request: Create a Xiaohongshu {topic} cover with authentic torn-paper scrapbook style.
Scene/backdrop: cozy {scene}, warm daylight, green and cream palette, lifestyle aesthetic.
Subject: Asian {gender}, visible upper body from waist to head, natural lifestyle pose, not a headshot.
Composition/framing: large irregular torn paper title sheet on upper-left and center; subject/product on right/lower-right; layered paper and tape fill the frame.
Text (verbatim): "{title_line_1}\n{title_line_2}"
Small labels: "{label_1}", "{label_2}".
Typography: large readable simplified Chinese with hand-written feeling, dark green ink, placed on rough torn paper with real fibrous edges.
Design details: masking tape, note cards, paper grain, hand-drawn hearts, circles, arrows, small stickers, layered collage, not neat rectangles.
Constraints: exact readable Chinese text; no text over face; no watermark; no QR code; no English text.
```

## 产品截图主视觉

```text
Use case: ads-marketing
Asset type: Xiaohongshu cover image, vertical 3:4 mobile cover
Style system: 产品截图主视觉, also known internally as 科技教程爆款风.
Primary request: Create a viral Xiaohongshu cover for {topic}.
Scene/backdrop: modern creator desk, laptop, abstract cyan dashboard glow, tech atmosphere without readable fake UI text.
Subject: Asian {gender} creator, visible upper body from waist to head, pointing at the title, confident expression, not a headshot.
Composition/framing: person on lower-right occupying 35%-45%; huge title on upper-left and center occupying 35%-45%; secondary tech labels around it; no dead empty space.
Text (verbatim): "{title_line_1}\n{title_line_2}"
Small labels: "{label_1}", "{label_2}".
Typography: huge bold simplified Chinese, white and electric cyan, thick black outline, neon glow, dynamic perspective.
Design details: neon arrows, warning labels, angular panels, sticker-style tags, energetic tutorial cover, not corporate PPT.
Constraints: exact Chinese text; no text over face; no watermark; no QR code; no English text; no readable fake UI text besides specified Chinese labels.
```

## 近大远小对比封面

```text
Use case: ads-marketing
Asset type: Xiaohongshu cover image, vertical 3:4 mobile cover
Style system: 近大远小对比封面, also known internally as 黑橙冲击对比风.
Primary request: Create a viral Xiaohongshu transformation cover about {topic}.
Scene/backdrop: dramatic black-orange {scene}, diagonal light streaks, high contrast.
Subject: Asian {gender}, visible upper body from waist to head, confident expression, not a headshot.
Composition/framing: person on right/lower-right occupying 40%-50%; huge diagonal title on left/top occupying 35%-45%; before/after contrast elements in lower third; no dead empty space.
Text (verbatim): "{title_line_1}\n{title_line_2}"
Small labels: "{label_1}", "{label_2}".
Typography: huge bold simplified Chinese, orange and white, thick black outline, rough brush shadow, diagonal perspective.
Design details: before/after arrows, torn tape, rough brush strokes, starburst, diagonal orange blocks, high-impact poster style, not clean PPT.
Constraints: exact readable Chinese text; no text over face; no watermark; no QR code; no English text.
```
