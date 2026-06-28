---
name: nook-trave
description: Create system-driven self-driving travel roadbooks, especially long China road trips such as Xinjiang routes. Use when the user asks for a self-driving itinerary, roadbook, route guide, travel manual, multi-day driving plan, or on-trip replanning; supports guided questioning, external information orchestration, route/weather/hotel evidence, and mobile-first vertical HTML/PDF-style roadbook production.
---

# Nook Trave

Use this skill to plan and produce a practical self-driving travel roadbook. The target output is a mobile-first vertical travel magazine roadbook that can be opened in the car every day, not a short text itinerary.

## Core Rule

Work as a planning system, not a copywriter. Ask only decision-changing questions, call or plan external tools where facts are time-sensitive, keep status visible during long work, and produce a roadbook that supports real on-road decisions.

## Workflow

1. Extract the user's explicit constraints: departure place, dates or season, day limit, route goal, self-driving mode, budget clues, must-see places.
2. Identify missing safety and feasibility fields: travelers, health risks, vehicle, drivers, daily driving tolerance, lodging level, food constraints, route tradeoff attitude.
3. Open with a short ritual-style welcome when the skill is first triggered. Tell the user there is a complete self-driving planning method ready, the trip will be built step by step, and they only need to answer 8 simple questions before route options are proposed.
4. Ask one question at a time. Label progress clearly as `问题 1/8`, `问题 2/8`, etc. Wait for the user's answer before asking the next question. Do not show all 8 questions in one message.
5. Generate route direction options when the trip is complex, such as comfortable, balanced, and coverage-oriented versions. Ask the user to choose one route direction. After the user chooses, directly start the next planning stage, usually a daily city skeleton or route framework with an overall route map. Do not ask for another confirmation before starting.
6. Gather or request evidence: map route data, weather, official road/scenic notices, hotels, restaurants, platform notes, and user-provided links or copied text.
7. Build structured roadbook data before writing the final HTML. Include route summary, days, meals, hotels, spots, weather, risks, contacts, assets, evidence, and verification status.
8. Generate a Markdown content draft only as an editable base.
9. Generate or collect image and map assets.
10. Render the main deliverable as a vertical HTML roadbook. Offer PDF export when useful.
11. End with a verification checklist and known assumptions. Never invent current hotel phone numbers, live road status, scenic policies, or weather.

## Opening Ritual

When this skill is triggered for a new trip, start with a concise welcome in Chinese:

```text
收到。我们已经准备好一整套自驾规划方法，会把这趟旅行拆成路线、节奏、住宿、餐食、风险和随车路书来一步步完成。

开始之前，你只需要回答 8 个简单问题。我会一个一个问，每题答完再进入下一题；答完 8 个问题后，我会先给你路线方向选项，不会直接跳到完整路书。
```

Then ask only `问题 1/8`.
## Status Visibility

During long work, emit short status lines outside the final roadbook:

```text
[需求] 已识别出发地、天数和覆盖目标。
[地图] 正在核算每日公里数和驾驶时间。
[天气] 正在拆分住宿城市和高海拔节点天气。
[酒店] 正在筛选每晚住宿区域和候选酒店。
[图片] 正在生成封面和章节图。
[排版] 正在渲染竖屏 HTML 路书。
```

These status lines belong in the agent conversation only. Do not put process explanations such as "Agent is working" into the final roadbook.

## Required First Questions

For a long self-driving route, confirm these fields unless already known. Ask them one at a time, in this order, with visible progress:

1. Travelers: adults, children, elderly people, multiple cars.
2. Health risks: altitude sensitivity, heart/lung disease, severe carsickness, pregnancy, mobility limitations.
3. Vehicle: fuel car, SUV, EV, rental car, off-road vehicle.
4. Drivers: number of reliable long-distance drivers.
5. Driving tolerance: comfortable daily kilometer limit and maximum acceptable emergency day.
6. Travel goal: comfort, coverage, photography, food, family-friendly, human culture.
7. Lodging level: economy, comfortable, local high-rated, luxury.
8. Tradeoff attitude: fewer places and easier days, balanced, or cover more with higher fatigue.

Each question should be short and multiple choice when possible. After the user answers, acknowledge the answer in one short sentence and ask the next numbered question. After question 8/8 is answered, summarize the constraints and provide route direction options.

## Map Work Visibility

When generating maps, emit visible conversation status lines before and during the work. For example: `[地图] 正在生成 Day 1-5 的路线底图。`, `[地图] 已生成总览图和每日底图，正在写入路书。` These status lines must not be inserted into the final roadbook. The final roadbook should contain the maps and verification notes, not process narration.
## Route Skeleton Map

When producing a daily city skeleton for a long self-driving trip, include an overall route map in the same response. If verified map data is not available yet, produce a clearly labeled schematic map and say it is not a navigation map. Use Mermaid or HTML/SVG only as a schematic, then later replace or supplement it with Amap/Gaode evidence when doing mileage and drive-time verification.
## Route Metrics Gate

After Amap/Gaode driving metrics are available, treat them as a route quality gate. If any day exceeds about 700 km or 8 hours, do not present the route as comfortable or balanced. Propose a split day, use the buffer day, delete a non-core node, or mark it as a deliberate high-intensity transit day. Keep the user's chosen driving tolerance visible when explaining the adjustment.
## Final Roadbook Requirements

The final roadbook must answer daily operational questions:

- In the morning: where to go, how far, how long, what to wear, when to leave.
- Around 11:00: where to eat lunch, whether parking is convenient, what backup food plan exists.
- Around 16:00: what city is ahead, how long to the hotel, whether to delete a spot.
- In the evening: hotel name, phone status, address, parking, dinner, laundry, refuel/charge, next-day risks.

For 20-25 day Xinjiang-style routes, aim for a large roadbook, typically dozens of vertical pages. Include cover, overview, route maps, daily chapters, spot pages, hotel/contact pages, food/supply pages, weather/clothing pages, risk backup pages, budget, and verification checklist.

## When To Read References

- Read `references/workflow.md` when designing the interaction, route option flow, status stream, or on-trip replanning.
- Read `references/roadbook-spec.md` before generating a full roadbook or deciding page structure.
- Read `references/tool-strategy.md` before calling or planning external resources such as maps, weather, hotels, platform links, image generation, or official sources.

## Template And Script

Use `assets/roadbook-template/template.html` as the vertical HTML base.

Use `scripts/render_roadbook.py` to render structured JSON into HTML:

```bash
python scripts/render_roadbook.py --data assets/roadbook-template/sample-data.json --template assets/roadbook-template/template.html --out output/roadbook.html
```

The sample data is only a template example. Real trips require fresh route, weather, hotel, image, evidence, and verification data.
Use `scripts/build_static_map.py` to create Amap static map URLs or download static map images from structured route points:

```bash
python scripts/build_static_map.py --data assets/roadbook-template/sample-map-route.json --print-url
python scripts/build_static_map.py --data assets/roadbook-template/sample-map-route.json --out output/maps/overview.png
```

Downloading requires `AMAP_WEB_SERVICE_KEY` or `--key`. If no key is available, still output the URL and mark the map as pending download.

## Writing Rules

- Write directly. Avoid padded phrases and avoid "not X but Y" framing unless it carries real contrast.
- Keep final roadbook language actionable, specific, and concise.
- Mark generated images as atmospheric or illustrative when they are not verified real photos.
- Mark schematic maps as schematic. Do not present them as navigation maps.
- Use verification states: verified, needs recheck, user-confirm, unavailable, assumed.
- Keep process documents out of the published roadbook.
