# 纸片手作：视觉与提示词

- 气质：桌面上的手工纸片：撕边纸片（`parts.py` 现画：撕边、纤维白边、纸纹、投影）、胶带、回形针、纸片剪出的小图标；浅色底牛皮纸桌面，深色底夜间台灯桌面。
- 图标：`deco/` 里 18 个（原 12 个加 6 个：日历、秒表、信封、放大镜、纸箱、旗子）。出图任务在 `jobs_base.json`（原 12 个加底图）和 `jobs_meaning.json`（新增 6 个）。
- 提示词骨架：`Handmade torn paper collage icon, layered cut and torn colored paper pieces with visible white fibrous torn edges, rich paper grain, soft realistic drop shadows between paper layers, warm palette of coral, mustard, mint, sky blue and cream, viewed flat from above, centered on a transparent background, no text. The icon shows <主体>`，走原始通道（`"lora": null`），透明底（`"alpha": true`）。
- 图示零件用 `card_fn=` 接 `paper_card`，让周历、矩阵、循环的格子都是撕边纸片（见 `examples/build_papercraft_rhythm.py`）。
- 配图规则：图标对应这一页的意思（日历=一周安排，秒表=时间预算，纸箱=库存，放大镜=复盘）。
