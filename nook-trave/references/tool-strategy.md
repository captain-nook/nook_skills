# Tool Strategy

## Principle

Use tools for unstable facts and the model for synthesis. Mark every important fact with source and verification status.

## Preferred Resource Roles

| Resource | Use | Notes |
|---|---|---|
| Amap/Gaode | route, mileage, drive time, POI, traffic | default map source when available |
| Baidu Map | fallback map/POI | use if Amap unavailable |
| Weather MCP/API | forecast, wind, temperature, clothing | query by daily lodging city and high-risk nodes |
| Search | official notices, scenic policies, road control | prefer official or recent sources |
| Xiaohongshu/Mafengwo | travel experience, recent pitfalls, subjective notes | non-blocking; use links/copy/OCR if available |
| Hotel/OTA/POI | hotel names, phone, parking, price level | do not invent phone numbers |
| Image generation | cover and chapter atmosphere | mark as generated/illustrative when not real photo |
| Local filesystem | save data, assets, draft, HTML, checklist | keep reusable outputs organized |

## Verification States

Use these states consistently:

- verified: checked from a current reliable source;
- needs recheck: likely useful but must be checked before departure;
- user-confirm: requires user or phone confirmation;
- unavailable: could not obtain;
- assumed: default assumption used to keep planning moving.

## Platform Links

Do not depend on a public Xiaohongshu or Mafengwo API. If the user provides links, try to read them when practical. If blocked by login, anti-scraping, or high token cost, ask for copied text, screenshots, or the user's own summary. Platform content should become structured evidence, not raw copied text in the roadbook.

## Maps

During route skeleton planning, include a first visual route map immediately. If current map data has not been verified, label it as a schematic and do not present distances or drive times as verified. Later, use Amap/Gaode or fallback map data to verify mileage, drive time, route feasibility, and daily map links.

Use `scripts/build_static_map.py` as the first implementation path for Amap static maps. It accepts structured route points, emits a static map URL without a key, and downloads the image when `AMAP_WEB_SERVICE_KEY` is available. Keep downloaded maps under `output/maps/` or the roadbook asset folder.

For final roadbooks:

- include an overall route map or schematic;
- include daily route notes or maps;
- mark schematic maps as schematic;
- do not claim a schematic is a navigation map;
- keep map links or evidence in the data package when available.

## Weather

Query multiple nodes rather than only the largest city. For Xinjiang, include lodging cities, mountain/high-altitude sections, lake/grassland sections, desert sections, and border/highland sections.

Translate weather into decisions: clothing, start time, delete/keep spots, high wind warning, rain/snow road caution, UV and hydration.

## Hotels

Hotel information should include name, area, phone status, address, parking, breakfast, laundry, cancellation, and why it fits the route. If unavailable, write `待查询` or `待电话复核`.

## Images

Image priority:

1. user-provided real images;
2. official or usable sourced images with attribution;
3. searched images with source notes;
4. AI-generated atmospheric images;
5. placeholder plus search prompt.

Generated images are acceptable for cover and atmosphere, but do not present them as verified scene photos.

## Output Package

For substantial roadbooks, create or maintain:

```text
roadbook.md
roadbook.html
assets/
data/roadbook-data.json
data/evidence.json
data/verification.json
verification-checklist.md
```

The current skill ships a starter renderer and template; extend it when richer maps, contacts, and PDF export are required.
