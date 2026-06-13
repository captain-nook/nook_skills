# 毛玻璃层叠卡片风

Version: v0.1  
Updated: 2026-05-21  
style_id: `glassmorphism_layered_card`  
Status: 初版规范 / 待验证

## Use

适合科技感封面、抽象概念解释、轻量产品说明、情绪化知识卡。视觉目标是“透明、轻、层叠、有空气感”，但文字必须清晰。

## Design Tokens

```json
{
  "canvas": {
    "default": "1920x1080",
    "portrait": "1080x1920",
    "safe_area_ratio": 0.07
  },
  "color": {
    "background_gradient": ["#101827", "#314B7C", "#B9D6FF", "#F9D7E5"],
    "surface_light": "rgba(255,255,255,0.42-0.68)",
    "surface_dark": "rgba(12,18,32,0.38-0.58)",
    "ink_dark": "#111827",
    "ink_light": "#FFFFFF",
    "muted_dark": "rgba(17,24,39,0.68)",
    "muted_light": "rgba(255,255,255,0.72)",
    "accent": ["#79D8FF", "#BDA6FF", "#FFB8D7"]
  },
  "material": {
    "backdrop_blur_px": [18, 36],
    "backdrop_saturate": [1.15, 1.35],
    "panel_opacity_range": [0.42, 0.72],
    "noise_opacity": [0.015, 0.035]
  },
  "border": {
    "width_px_at_1920": [1, 2],
    "color": "rgba(255,255,255,0.35-0.70)",
    "inner_highlight": "inset 0 1px 0 rgba(255,255,255,0.55)"
  },
  "radius": {
    "main_panel_px_at_1920": [28, 56],
    "small_chip_px_at_1920": [14, 999]
  },
  "shadow": {
    "primary": "0 24px 80px rgba(0,0,0,0.22)",
    "secondary": "0 10px 32px rgba(0,0,0,0.14)"
  },
  "typography": {
    "hero_weight": 850,
    "body_weight": 600,
    "hero_size_px_at_1920": [72, 150],
    "body_size_px_at_1920": [28, 42],
    "line_height": [1.08, 1.35]
  }
}
```

## Layout Rules

- Main glass panel width: `58%-82%` of landscape canvas; `72%-88%` of portrait canvas.
- Layer count: `2-4` translucent panels, including decorative background panels.
- Background must carry a visible gradient, soft image, or abstract color field; the card surface must not become plain white.
- Text layers are always sharp. Apply blur only to the panel background through `backdrop-filter`.
- If content is dense, increase panel opacity up to `0.72` and simplify background detail before reducing type size.
- Primary text contrast ratio should remain above `7:1` against the effective panel color.

## Required Anchors

At least three must appear:

- frosted translucent surface
- backdrop blur
- luminous border
- layered panels
- soft gradient or image background
- small glass chips or pills

## Negative Constraints

- Do not use thick black outlines.
- Do not use hard comic shadows.
- Do not blur readable text.
- Do not put body text directly on a busy background.
- Do not let all surfaces become opaque white.

## Quality Checklist

- Text is readable at 100% and 50% preview scale.
- The main panel is visibly translucent but not muddy.
- Background does not compete with body copy.
- Border highlight is visible but not glowing like neon.
- The result still reads as a card, not a generic gradient poster.
