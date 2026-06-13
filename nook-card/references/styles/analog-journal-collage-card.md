# 手账拼贴卡片风

Version: v0.1  
Updated: 2026-05-21  
style_id: `analog_journal_collage_card`  
Status: 初版规范 / 待验证

## Use

适合个人方法论、旅行/生活笔记、课程复盘、温和叙事型知识卡。视觉目标是“像真实手账页面，但内容层级仍然清楚”。

## Design Tokens

```json
{
  "canvas": {
    "default": "1920x1080",
    "portrait": "1080x1920",
    "safe_area_ratio": 0.075
  },
  "color": {
    "background": "#F4E6CF",
    "paper_1": "#FFF8E8",
    "paper_2": "#F7E9D2",
    "paper_3": "#EFE1C7",
    "ink": "#24201A",
    "muted_ink": "#6A5C4A",
    "accent_red": "#C64A3B",
    "accent_blue": "#2E6F9E",
    "accent_green": "#5D8B59",
    "tape_yellow": "rgba(255,230,156,0.72)",
    "tape_mint": "rgba(194,228,218,0.62)"
  },
  "texture": {
    "paper_fiber_opacity": [0.05, 0.12],
    "grain_scale_px": [2, 5],
    "line_opacity": [0.08, 0.18]
  },
  "shape": {
    "paper_radius_px_at_1920": [4, 22],
    "photo_radius_px_at_1920": [0, 12],
    "tape_radius_px_at_1920": [2, 8],
    "scrap_rotation_degrees": [-1.8, 1.8]
  },
  "shadow": {
    "paper": "0 10px 28px rgba(54,42,26,0.16)",
    "small_scrap": "0 5px 14px rgba(54,42,26,0.14)"
  },
  "typography": {
    "hero_weight": 850,
    "body_weight": 550,
    "hero_size_px_at_1920": [64, 132],
    "body_size_px_at_1920": [28, 40],
    "handwritten_accent_ratio": [0.08, 0.18]
  }
}
```

## Layout Rules

- Main paper block width: `60%-86%` of landscape canvas; `74%-90%` of portrait canvas.
- Main body text rotation must be `0deg`; only tape, stickers, photos, stamps, and small notes may rotate.
- Use `1-3` collage accents per card. More than `3` accents need a deliberate scrapbook layout.
- Long content should become checklist rows, notebook lines, or clipped sub-notes.
- Keep at least one clean reading column; the card must not become a moodboard.
- Use one fresh accent color per card to avoid an all-brown result.

## Required Anchors

At least three must appear:

- paper surface
- low-opacity paper fiber or grain
- tape or sticker
- small rotated scrap
- handwritten accent label
- stamp, date label, paperclip, clipped photo, or margin note

## Negative Constraints

- Do not make key content handwritten-only.
- Do not use hard comic outlines.
- Do not exceed `12%` texture opacity.
- Do not rotate main body paragraphs.
- Do not let warm paper colors collapse into low-contrast beige-on-beige.

## Quality Checklist

- Main reading order is clear.
- Decorative scraps feel handmade but do not cover content.
- Body text remains readable in video overlay use.
- Texture is visible only as material, not dirt.
- The style feels personal and analog while staying suitable for knowledge cards.
