# 波普漫画卡片风

Version: v0.1  
Updated: 2026-05-21  
style_id: `pop_art_comic_card`  
Status: 初版规范 / 待验证

## Use

适合强观点、社媒传播图、夸张对比、活动提示、标题型知识卡。视觉目标是“高能量、强对比、漫画感、可一眼抓住重点”。

## Design Tokens

```json
{
  "canvas": {
    "default": "1920x1080",
    "portrait": "1080x1920",
    "safe_area_ratio": 0.065
  },
  "color": {
    "ink": "#050505",
    "surface": "#FFF8E8",
    "yellow": "#FFD400",
    "cyan": "#00AEEF",
    "magenta": "#FF2DAA",
    "red": "#F03A2F",
    "blue": "#1B4DFF",
    "white": "#FFFFFF",
    "max_palette_colors_per_card": 5
  },
  "stroke": {
    "major_px_at_1920": [8, 14],
    "minor_px_at_1920": [4, 8],
    "color": "#050505"
  },
  "shadow": {
    "type": "hard_offset",
    "offset_px_at_1920": [10, 28],
    "color": "#050505"
  },
  "radius": {
    "panel_px_at_1920": [0, 28],
    "bubble_px_at_1920": [32, 80],
    "sticker_px_at_1920": [10, 24]
  },
  "halftone": {
    "dot_radius_px": [3, 9],
    "spacing_px": [12, 28],
    "opacity": [0.18, 0.42],
    "avoid_body_text_area": true
  },
  "typography": {
    "hero_weight": 900,
    "hero_size_px_at_1920": [96, 220],
    "body_weight": 800,
    "body_size_px_at_1920": [30, 46],
    "letter_spacing": 0,
    "outline_allowed": true
  }
}
```

## Layout Rules

- Hero text should occupy `28%-48%` of canvas height for a single-message card.
- Use one dominant visual device only: burst, speech bubble, diagonal ray field, or huge number.
- Secondary content should become stickers, numbered strips, speech bubbles, or small caption blocks.
- Maintain a black outline around major colored shapes.
- Halftone dots should sit in background zones or large colored shapes, not behind small body text.
- Asymmetry is allowed, but the largest text must remain readable within `1.5s` glance time.

## Required Anchors

At least three must appear:

- high-saturation yellow/cyan/magenta/red palette
- thick black outline
- halftone dots
- hard offset shadow
- burst or speech-bubble shape
- large compressed hero type

## Negative Constraints

- Do not use pastel-only palettes.
- Do not use soft glass blur.
- Do not create a flat corporate slide with a few bright colors; the comic outline and halftone system are required.
- Do not use more than `3` competing hero elements.
- Do not let decorative shapes cover or fragment Chinese characters.

## Quality Checklist

- At thumbnail size, the hero text is still the first thing seen.
- Color count is controlled and not rainbow noise.
- Major shapes have black outlines.
- Halftone dots are visible but do not damage readability.
- The card feels energetic without becoming visually chaotic.
