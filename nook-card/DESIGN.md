# nook-card Design System

Version: v0.1  
Default style: `tactile_soft_skeuomorphic_card`

## Visual Theme & Atmosphere

High-tactility knowledge cards with thick black strokes, hard offset shadows, bold Chinese typography, strong action colors, software-window cues, and subtle dotted card surfaces. The result should feel like a clickable UI object, not a flat poster.

## Color Palette & Roles

| Token | Value | Role |
| --- | --- | --- |
| `background` | `#F7F9F8` | cool near-white canvas |
| `surface` | `#FFFFFD` | card surface |
| `ink` | `#010101` | text, stroke, outlines |
| `hard_shadow` | `#0B0B0B` | card and button offset shadows |
| `yellow_action` | `#FDC703` | primary action button |
| `red_action` | `#E03A10` | strong action button |
| `green_status` | `#28C959` | status dot and macOS green |
| `code_panel` | `#272935` | optional software context panel |

## Typography Rules

- Use heavy sans-serif Chinese fonts: Source Han Sans SC, Noto Sans CJK SC, PingFang SC, Microsoft YaHei UI, Arial fallback.
- Primary title weight: `850-900`.
- Secondary text weight: `700-850`.
- Letter spacing: `0`.
- Avoid thin, serif, handwritten, or calligraphic fonts.

## Layout Principles

- Treat the card as a dynamic system, not a fixed template.
- Main card occupies `72%-88%` of canvas width.
- Keep a clear hierarchy: number/title, subtitle/body, labels/buttons.
- Preserve at least two style anchors: thick stroke, hard shadow, dotted surface, macOS dots, action button, cursor, or code panel.

## Depth & Elevation

- Use hard shadows: `blur = 0-4px`, preferably `0px`.
- Card shadow offset: about `2.6%` canvas width horizontally and `3.0%` vertically.
- Button shadow offset: about `2.0%` canvas width horizontally and vertically.
- Shadow edges should be sharp and board-like.

## Surface Pattern

- Card surface uses a subtle dot grid.
- Dot diameter: `0.14%-0.24%` canvas width.
- Grid spacing: `1.6%-2.4%` canvas width.
- Opacity: `4%-7%`, lower behind dense text.

## Do's and Don'ts

Do:

- Use high contrast.
- Keep outlines thick and confident.
- Make buttons feel pressable.
- Keep text readable and unclipped.

Don't:

- Use glassmorphism.
- Use soft blurry neumorphic shadows.
- Use large gradients or bokeh decorations.
- Make a generic flat quote poster.
