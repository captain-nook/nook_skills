# Planning Layer

## Asset Extraction

Extract and rate:

```yaml
asset_profile:
  result: none/weak/mid/strong
  pain: none/weak/mid/strong
  pitfall: none/weak/mid/strong
  viewpoint: none/weak/mid/strong
  case: none/weak/mid/strong
  list: none/weak/mid/strong
  process: none/weak/mid/strong
```

Hard limits:

- No result: do not use result model.
- No real subject: do not use case model.
- No list: do not use list model.
- Weak evidence: downgrade to viewpoint or observation.

## Platform Routing

```yaml
douyin:
  tasks: 引流 / 互动 / 打标签
  models: 结果型 / 观点型 / 避坑型 / 热点型
xiaohongshu:
  tasks: 搜索 / 收藏 / 信任
  models: 清单型 / 避坑型 / 效果种草型 / 过程型
shipinhao:
  tasks: 信任 / 转化 / 业务价值
  models: 痛点型 / 案例型 / 过程型 / 结果型 / 观点型
```

## Source Lane Ratio

Default: each platform gets 2 `anchor_lane` items and 2 `live_lane` items.

Adjust:

- Strong transcript/project: use 3+1.
- Strong current topic/platform samples: use 1+3.
- Single hot topic: max 2-3 items total.

## Weekly Matrix

```yaml
douyin:
  - result
  - result_or_pitfall
  - viewpoint
  - pitfall_or_hotspot
xiaohongshu:
  - list_carousel
  - pitfall_carousel
  - result_video
  - process_or_seed_video
shipinhao:
  - pain
  - case_or_process
  - result
  - conversion_or_viewpoint
```

## Content Brief

```yaml
content_brief:
  content_id:
  platform:
  format:
  selected_model:
  primary_task:
  target_audience:
  commercial_step:
  source_lane:
  source_asset:
  asset_strength:
  evidence_to_show:
  opening_model:
  hook_fill:
  body_fill:
  ending_path:
  do_not_teach:
  visual_need:
  validation_metric:
  risk_note:
```

## Fatigue Check

Reject or revise if:

- Same hot topic appears in more than 3 items.
- Same result appears more than 2 times on one platform.
- Same hook pattern appears more than 2 times on one platform.
- Xiaohongshu carousels have the same save reason.
- WeChat Channels has no business or paid-context item.
