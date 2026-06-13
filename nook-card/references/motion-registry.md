# Motion Registry

Version: v0.2  
Updated: 2026-05-21  
Purpose: keep reusable Remotion motion presets for nook-card videos in one registry.

## Principle

Motion presets are reusable animation recipes. Keep the active list small; the expected long-term size is `6-8` presets.

Every video task chooses:

1. `motion_id`
2. concrete motion requirements

If the user only wants a static card, do not enter the motion step.

## Global Video Defaults

These apply unless the user overrides them:

| Field | Default |
| --- | --- |
| canvas | `1920 x 1080` |
| orientation | landscape by default; portrait `1080 x 1920` remains optional |
| fps | `30` |
| duration | voiceover-driven when narration exists; otherwise preset default |
| background | transparent |
| primary output | MOV with alpha |
| primary codec | ProRes 4444 |
| primary pixel format | `yuva444p10le` when available |
| optional preview | WebM with alpha |
| preview codec | `vp8` |
| preview pixel format | `yuva420p` |
| image format | `png` |
| hold behavior | never fully static; keep subtle breathing or micro drift |
| camera behavior | optional perspective/camera motion when it helps the preset |
| output folder | `outputs/videos/<slug>/` |

## Global Motion Rules

- Motion should support spoken narration. If the user provides voiceover text or a target narration length, duration follows that timing.
- No scene should be absolutely still. During holds, use subtle breathing, tiny rotation, minor parallax, shadow shift, or camera drift.
- Keep text readable throughout motion; avoid moving dense body text too aggressively.
- Prefer transparent background for overlays.
- Camera/perspective motion is allowed when it clarifies depth, but it should stay mild enough for editing overlays.
- Default camera ranges:
  - `perspective_px`: `900-1600`
  - `rotateX_degrees`: `-4` to `4`
  - `rotateY_degrees`: `-6` to `6`
  - `translateZ_px`: `-80` to `120`
  - hold drift frequency: `0.15-0.45Hz`

## Active Motion Presets

| motion_id | 中文名 | Status | Use When | Default Behavior |
| --- | --- | --- | --- | --- |
| `pop_breathe` | 下方弹出居中呼吸 | 默认 / 已验证 | 单张或少量多张卡片、封面、重点提示 | 卡片从下方弹出到中心，轻微 overshoot，随后呼吸；多张卡片依次弹出并形成稳定组合 |
| `timeline_arrow_reveal` | 时间轴箭头展开 | 核心预设 / 待验证 | 步骤、历史、流程、路线、教程拆解 | 箭头或路径逐步生长，卡片在路径两侧交替出现，可横向、纵向或波浪线 |
| `portrait_carousel_focus` | 竖卡走马灯聚焦 | 核心预设 / 待验证 | 多张竖版卡片连续展示、系列观点、章节列表 | 竖构图卡片围绕中心旋转，正面卡清晰，背后卡模糊、缩小、降低透明度 |
| `dynamic_compare_bars` | 动态对比柱状图 | 核心预设 / 待验证 | 年份数据、指标变化、排名对比、增长故事 | 若干柱状图从下方依次升起，数字和标签跟随更新，保持轻微摄像机或呼吸运动 |

## Candidate Presets

These are retained as future candidates, not the current core set:

| motion_id | 中文名 | Notes |
| --- | --- | --- |
| `cursor_click` | 光标点击 | Useful for software tutorial cards and button confirmation scenes |
| `stack_shuffle` | 卡片堆叠 | Useful for knowledge collections and deck-like reveals |
| `slide_horizontal` | 横向出现 | Useful for left/right comparison scenes |
| `minimal_float` | 极轻浮动 | Useful when the static design should dominate |

## Preset Detail: `pop_breathe`

Default preset. It supports both a single card and a small card set, commonly `3-4` cards, and may extend to `6` cards when layout remains readable.

```json
{
  "motion_id": "pop_breathe",
  "duration_seconds_default": 5,
  "duration_rule": "follow_voiceover_if_present",
  "card_count": {
    "default": 1,
    "common_range": [1, 4],
    "extended_range": [5, 6],
    "multi_card_behavior": "sequential_center_pop"
  },
  "entrance": {
    "type": "spring_pop",
    "from": "bottom",
    "target": "center",
    "translate_y_px": [120, 240],
    "scale_from": [0.62, 0.78],
    "overshoot": [1.035, 1.08],
    "settle_frames": [26, 36],
    "stagger_frames": [8, 20]
  },
  "hold": {
    "type": "breathing",
    "scale_amplitude": [0.004, 0.010],
    "y_amplitude_px": [3, 8],
    "rotation_amplitude_degrees": [0.08, 0.22],
    "frequency_hz": [0.28, 0.48]
  },
  "exit": {
    "type": "none"
  }
}
```

Layout rules:

- `1` card: center the card.
- `2` cards: slightly overlapped pair or split left/right around center.
- `3` cards: center the primary card, place secondary cards slightly behind left/right.
- `4` cards: compact fan or 2x2 balanced group.
- `5-6` cards: grid or arc layout; reduce rotation and shadow overlap to protect readability.
- After all cards enter, the group breathes together; individual cards may have tiny phase offsets.

## Preset Detail: `timeline_arrow_reveal`

Timeline preset for process explanation. It is expected to be used often.

```json
{
  "motion_id": "timeline_arrow_reveal",
  "duration_seconds_default": 8,
  "duration_rule": "follow_voiceover_if_present",
  "path": {
    "orientation_options": ["horizontal", "vertical", "wave"],
    "default_orientation": "horizontal",
    "stroke_width_px_at_1920": [8, 18],
    "arrow_head_size_px_at_1920": [28, 54],
    "growth_method": "svg_stroke_dashoffset_or_mask_reveal"
  },
  "cards": {
    "placement": "alternate_sides_of_path",
    "stagger_after_path_reaches_node_frames": [2, 10],
    "entrance": "scale_pop_plus_short_slide",
    "max_cards_landscape": 6,
    "max_cards_portrait": 5
  },
  "hold": {
    "path_micro_flow": true,
    "card_breathing": true,
    "camera_drift_optional": true
  }
}
```

Behavior:

- The arrow/path grows first, then each node/card appears when the path reaches its position.
- Landscape may use horizontal or wave timelines.
- Portrait may use vertical or wave timelines.
- Cards alternate above/below or left/right of the path.
- For dense content, use small node labels on the timeline and show one larger focused card at a time.

Negative constraints:

- Do not show all cards before the arrow reaches them.
- Do not make the path decorative only; it must explain sequence.
- Do not let cards overlap the arrow head or upcoming nodes.

## Preset Detail: `portrait_carousel_focus`

Carousel preset for vertical card series.

```json
{
  "motion_id": "portrait_carousel_focus",
  "duration_seconds_default": 8,
  "duration_rule": "follow_voiceover_if_present",
  "canvas_preference": "portrait_1080x1920",
  "card_aspect_ratio": "9:16_or_3:4",
  "carousel": {
    "type": "3d_orbit",
    "visible_cards": [3, 7],
    "center_card_scale": [0.86, 1.0],
    "side_card_scale": [0.54, 0.74],
    "side_card_opacity": [0.28, 0.58],
    "side_card_blur_px": [4, 14],
    "rotateY_degrees": [-34, 34],
    "perspective_px": [900, 1400]
  },
  "hold": {
    "center_card_breathing": true,
    "orbit_micro_drift": true
  }
}
```

Behavior:

- Only the card facing the viewer is fully sharp and fully readable.
- Background cards are blurred, dimmed, scaled down, and slightly rotated in perspective.
- The carousel may step card-by-card for narration, or loop slowly for ambient display.
- If used in landscape, keep the carousel centered with extra side falloff.

Negative constraints:

- Do not blur the current front card.
- Do not rotate text so far that it becomes unreadable.
- Do not keep all cards equally sharp; focus hierarchy is required.

## Preset Detail: `dynamic_compare_bars`

Data comparison preset. It may not depend on static card assets, but belongs in the Remotion motion toolkit.

```json
{
  "motion_id": "dynamic_compare_bars",
  "duration_seconds_default": 8,
  "duration_rule": "follow_voiceover_if_present",
  "data": {
    "series_count_recommended": [2, 6],
    "supports_years": true,
    "supports_rankings": true,
    "supports_before_after": true
  },
  "bars": {
    "entrance": "rise_from_baseline",
    "stagger_frames": [8, 24],
    "easing": "out_cubic_or_spring",
    "corner_radius_px_at_1920": [8, 20],
    "min_bar_width_px_at_1920": 44
  },
  "labels": {
    "value_count_up": true,
    "year_or_category_follow_bar": true,
    "emphasis_on_latest_or_largest": true
  },
  "hold": {
    "baseline_breathing": true,
    "camera_drift_optional": true,
    "highlight_pulse_amplitude": [0.02, 0.05]
  }
}
```

Behavior:

- Bars rise one by one from the baseline.
- Values count up while bars grow.
- The latest, largest, or user-specified key bar gets a stronger accent.
- Can use 2D chart motion or mild perspective camera motion.

Negative constraints:

- Do not fake data values.
- Do not animate bars so fast that the comparison cannot be read with narration.
- Do not use excessive 3D distortion for precise charts.

## Adding A Motion Preset

Add a new preset only when it will be reused.

Required fields:

- `motion_id`
- Chinese name
- use case
- default duration rule
- entrance behavior
- hold behavior
- exit behavior
- transparency compatibility
- editing delivery format
- constraints and negative examples

Do not exceed `8` active presets unless the user explicitly expands the system.
