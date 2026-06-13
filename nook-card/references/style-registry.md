# Style Registry

Version: v0.2  
Updated: 2026-05-21  
Purpose: keep the reusable visual styles for nook-card static cards in one registry.  
Scope: OpenDesign static cards, Remotion card videos, and future Codex skill style selection.

## Principle

Card styles live in this registry. Keep the active list small; the expected long-term size is `7-8` styles.

Each static-card task asks for only two dimensions:

1. `style_id`
2. concrete card requirements

If a style needs detailed tokens, keep the full spec in `references/styles/`. This registry must still contain the selectable ID, summary, core tokens, use cases, dynamic rules, and negative constraints.

## Default Style

```json
{
  "default_style_id": "tactile_soft_skeuomorphic_card",
  "default_style_name": "触感软拟态卡片风",
  "default_canvas": "1920x1080",
  "default_orientation": "landscape",
  "style_doc": "references/styles/tactile-soft-skeuomorphic-card.md"
}
```

## Active Styles

| style_id | 中文名 | 状态 | 规范文档 | 适用场景 |
| --- | --- | --- | --- | --- |
| `tactile_soft_skeuomorphic_card` | 触感软拟态卡片风 | 试验中 / 默认 | `references/styles/tactile-soft-skeuomorphic-card.md` | 知识卡片、教程封面、软件工具类说明、带按钮的行动卡 |
| `glassmorphism_layered_card` | 毛玻璃层叠卡片风 | 初版规范 / 待验证 | `references/styles/glassmorphism-layered-card.md` | 情绪化知识卡、科技感封面、抽象概念解释、轻量产品说明 |
| `pop_art_comic_card` | 波普漫画卡片风 | 初版规范 / 待验证 | `references/styles/pop-art-comic-card.md` | 强观点、标题党封面、社媒传播图、夸张对比和活动提示 |
| `analog_journal_collage_card` | 手账拼贴卡片风 | 初版规范 / 待验证 | `references/styles/analog-journal-collage-card.md` | 个人方法论、旅行/生活笔记、课程复盘、温和叙事型知识卡 |

## Style Summaries

### `tactile_soft_skeuomorphic_card`

Core identity:

- Thick black stroke.
- Hard offset shadow.
- Near-white tactile surface with subtle dot grid.
- High-saturation yellow/red/green accents.
- macOS dots, cursor, button, status lights, and software-interface metaphors.
- Extra-bold Chinese sans typography.

Core tokens:

```json
{
  "background": "#F7F9F8",
  "surface": "#FFFFFD",
  "ink": "#010101",
  "shadow": "#0B0B0B",
  "yellow_action": "#FDC703",
  "red_action": "#E03A10",
  "green_status": "#28C959",
  "stroke_width_px_at_1920": [8, 16],
  "corner_radius_px_at_1920": [34, 76],
  "shadow_type": "hard",
  "surface_pattern": "subtle_dot_grid"
}
```

### `glassmorphism_layered_card`

Core identity:

- Translucent frosted panels over a soft gradient, image, or abstract color field.
- Backdrop blur and mild saturation boost, not flat opacity.
- Thin luminous border and inner highlight.
- Minimal icon/label system, light depth, calm premium feeling.
- Text stays sharp and high contrast; blur never applies to text layers.

Core tokens:

```json
{
  "background": ["#101827", "#314B7C", "#B9D6FF", "#F9D7E5"],
  "surface_rgba": "rgba(255, 255, 255, 0.42-0.68)",
  "dark_surface_rgba": "rgba(12, 18, 32, 0.38-0.58)",
  "backdrop_blur_px": [18, 36],
  "backdrop_saturate": [1.15, 1.35],
  "border_rgba": "rgba(255, 255, 255, 0.35-0.70)",
  "border_width_px_at_1920": [1, 2],
  "corner_radius_px_at_1920": [28, 56],
  "shadow": "0 24px 80px rgba(0,0,0,0.22)",
  "highlight": "inset 0 1px 0 rgba(255,255,255,0.55)"
}
```

Dynamic rules:

- Use `2-4` translucent layers max; more layers make the card look noisy.
- Main content panel occupies `58%-82%` of canvas width in landscape and `72%-88%` in portrait.
- If text grows, reduce background detail first, then increase panel opacity up to `0.72`; do not blur or fade text.
- Primary text contrast ratio should stay above `7:1` against the effective panel color.

Negative constraints:

- Do not use pure white opaque cards.
- Do not place body text directly on busy background.
- Do not use heavy black hard shadows; this style uses soft depth.
- Do not blur text, buttons, or icons.

### `pop_art_comic_card`

Core identity:

- High saturation CMYK-like palette.
- Thick black comic outlines.
- Halftone dots, burst shapes, diagonal rays, sticker labels, speech-bubble components.
- Large compressed display typography, often with offset shadow or stroke.
- Energetic asymmetry; controlled chaos, not random decoration.

Core tokens:

```json
{
  "background": ["#FFD400", "#00AEEF", "#FF2DAA", "#F03A2F"],
  "surface": "#FFF8E8",
  "ink": "#050505",
  "accent_blue": "#00AEEF",
  "accent_magenta": "#FF2DAA",
  "accent_yellow": "#FFD400",
  "accent_red": "#F03A2F",
  "stroke_width_px_at_1920": [6, 14],
  "shadow_offset_px_at_1920": [10, 28],
  "corner_radius_px_at_1920": [0, 28],
  "halftone_dot_radius_px": [3, 9],
  "halftone_spacing_px": [12, 28],
  "max_palette_colors_per_card": 5
}
```

Dynamic rules:

- Hero text should occupy `28%-48%` of canvas height for single-message cards.
- Use at most one major burst or speech bubble per card.
- When content is dense, convert secondary copy into small sticker labels or numbered strips.
- Maintain at least one black outline around each major shape; flat color blocks without outline weaken the style.

Negative constraints:

- Do not use low-saturation pastel palettes.
- Do not use soft glass blur or subtle corporate gradients.
- Do not use more than `3` competing hero elements.
- Do not let halftone patterns sit behind small body text.

### `analog_journal_collage_card`

Core identity:

- Paper, notebook, tape, sticker, stamp, handwriting, clipped-photo, and margin-note metaphors.
- Warm off-white paper surfaces with low-opacity fiber/noise texture.
- Slight rotations and layered scraps, but the main reading path stays orderly.
- Human, personal, reflective, and process-oriented.
- Uses handwritten accent sparingly; body text remains readable sans or serif.

Core tokens:

```json
{
  "background": "#F4E6CF",
  "paper": ["#FFF8E8", "#F7E9D2", "#EFE1C7"],
  "ink": "#24201A",
  "muted_ink": "#6A5C4A",
  "tape": ["rgba(255, 230, 156, 0.72)", "rgba(194, 228, 218, 0.62)"],
  "accent_red": "#C64A3B",
  "accent_blue": "#2E6F9E",
  "accent_green": "#5D8B59",
  "paper_texture_opacity": [0.05, 0.12],
  "corner_radius_px_at_1920": [4, 22],
  "scrap_rotation_degrees": [-1.8, 1.8],
  "shadow": "0 10px 28px rgba(54,42,26,0.16)"
}
```

Dynamic rules:

- Main paper block occupies `60%-86%` of canvas width in landscape and `74%-90%` in portrait.
- Keep body text rotation at `0deg`; only decorative scraps, photos, tape, and labels may rotate.
- Use `1-3` collage accents per card: tape, sticker, stamp, paperclip, photo frame, or margin note.
- If content grows, use notebook lines, checklist rows, or clipped sub-notes rather than shrinking all type.

Negative constraints:

- Do not make the whole card brown or sepia; keep contrast and one fresh accent color.
- Do not use hard comic outlines.
- Do not rely on illegible handwriting for key content.
- Do not overuse texture above `12%` opacity.

## Style Document Required Fields

Each style must include:

- `style_id`
- `style_name`
- `version`
- `reference_assets`
- `design_tokens`
- `dynamic_layout_rules`
- `usage`
- `negative_constraints`
- `quality_checklist`

## Adding A Style

Add a new style only when it will be reused.

Process:

1. Gather `1-3` references or a clear target description.
2. Extract visual DNA: colors, typography, shape language, depth, texture, layout, variable ranges, and negative examples.
3. Register the style in this file.
4. Add or update the detailed style document in `references/styles/`.
5. Validate with at least two content densities:
   - short title + small action area
   - long title + multiple information blocks

Do not exceed `8` active styles unless the user explicitly expands the system.

## Status Definitions

| Status | Meaning |
| --- | --- |
| `初版规范 / 待验证` | Tokens are drafted but need sample renders |
| `试验中` | Has at least one render, still being tuned |
| `默认` | Used when no style is specified |
| `稳定` | Validated across multiple tasks |
| `废弃` | Kept only for history |

## Selection Rules

- If the user specifies a style, use it.
- If unspecified, use `default_style_id`.
- If the user provides a new reference image, decide whether it updates an existing style or becomes a new style.
- Do not mix tokens from different styles unless the user explicitly asks for a hybrid.
- Active style count should stay under `8`.
