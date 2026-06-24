---
name: nook-title
description: Generate, analyze, score, and revise Chinese WeChat/AI-media titles in nook style, including high-density AI news titles with entity/number/action/consequence structures. Use when the user asks for 公众号标题, 给我取几个标题, 候选标题, 标题评分, 标题风格提炼, AI资讯标题, 爆款标题, or title optimization from an Obsidian draft, article facts, notes, links, or finished manuscript.
---

# 1 nook-title

Use this skill to turn article facts into high-click Chinese titles without inventing facts. The user does not need to name a source style; infer the appropriate AI-media title style from the task and facts.

This skill is a title system, not a slogan generator. It must preserve the factual boundary of the source, extract concrete hooks first, then generate and score candidates.

## 1.1 Core Rules

- Generate from facts only. Do not invent numbers, rankings, model names, companies, release status, benchmark results, dates, or user impact.
- Prefer concrete entities over abstract concepts: model, company, product, person, benchmark, number, cost, time, capability, affected group.
- For AI news and high-density media titles, target about 28-42 Chinese display characters when possible. Do not force length if the fact needs more or less room.
- Use punctuation as pacing, not decoration. `!` and `,` are common in high-density AI-media titles, but only use them when there is a real event, contrast, or result.
- Keep the strongest factual hook in the first half of the title.
- Produce multiple structural variants, not ten small wording changes.
- Always include a fact-boundary note when the source is weak, speculative, sponsored, or not directly available.

## 1.2 Required Reference Loading

- For AI news, model/company release, benchmark, tool update, or high-density media titles, read `references/high-density-ai-news-patterns.md`.
- For safety, exaggeration control, and fact-boundary checks, read `references/title-safety.md`.
- When calibrating examples or validating style, read `references/sample-titles.md`.

## 1.3 Workflow

1. Extract title facts before writing:
   - entities: model/company/person/product;
   - numbers: price, time, benchmark, scale, version, count;
   - action: released, leaked, beat, updated, cut cost, failed, got blocked;
   - conflict or contrast: old vs new, A vs B, cost vs capability, promise vs risk;
   - consequence: who is affected and why it matters.
2. Mark facts as `confirmed`, `source-claimed`, or `unclear`.
3. Choose 2-4 title frames from `references/high-density-ai-news-patterns.md`.
4. Generate 8-12 candidates. Include at least:
   - 3 high-impact AI-media variants;
   - 3 steadier WeChat variants;
   - 2 search-friendly variants.
5. Score candidates with these dimensions:
   - fact fidelity;
   - entity clarity;
   - numerical hook;
   - tension/contrast;
   - reader relevance;
   - click strength without hallucination;
   - readability in two seconds.
6. Recommend 2-3 candidates, not one. Explain the tradeoff briefly.
7. If the user asks for a publish title, provide `publish_title`, `publish_summary`, and optional `publish_tags`.

## 1.4 Output Format

For candidate generation:

```markdown
事实钩子：
- 实体：
- 数字：
- 动作/冲突：
- 后果/人群：
- 边界：

候选标题：
1. ...

推荐：
- 第 X 个：理由
- 第 Y 个：理由
```

For title review:

```markdown
标题诊断：
- 最大问题：
- 可保留：
- 风险：

改写：
1. ...
```

## 1.5 Script Use

Use `scripts/analyze_titles.py` when the user provides a list of real titles and asks for pattern extraction or statistics.

Use `scripts/score_titles.py` when the user provides candidate titles and wants a deterministic first-pass check. The script scores surface features only; final judgment must still check source facts and reader fit.

Examples:

```bash
python scripts/analyze_titles.py titles.txt
python scripts/score_titles.py candidates.txt
```

## 1.6 Coordination With Other Nook Skills

- If the task is a full WeChat article, `nook-wechat-writer` owns angle, article structure, and full draft. This skill owns title generation and scoring.
- If final wording feels AI-like or too polished, use `../nook-humanizer-zh-review/SKILL.md` after title facts and structure are settled.
- Do not package or format the article for publication. Publishing assembly belongs to `../nook-wechat-packager/SKILL.md`.
