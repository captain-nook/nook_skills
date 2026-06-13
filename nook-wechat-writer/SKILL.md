---
name: nook-wechat-writer
description: Write, revise, review, title, and adapt Chinese WeChat official-account articles using the nook content-production method. Use when the user asks to write a 公众号文章, produce a long-form Chinese article, turn materials into an article, refine an article draft, remove AI flavor from a WeChat article, design an article angle, generate publishable titles/summaries, compare or integrate Khazix/花叔-style writing workflows, convert between WeChat articles and short-video scripts, or build a publishable article from notes, research, transcripts, links, or rough ideas.
---

# 1 nook-wechat-writer

Use this skill to produce Chinese WeChat official-account articles with a clear reader value, real judgment, natural paragraph prose, and layered review.

The skill is not a prompt-template generator. It is a writing workflow: clarify the value, shape the topic, process materials, write the draft, then review hard for structure, source attribution, AI flavor, and sensitive information.

**Constraint-based generation**: This skill uses mandatory checkpoints and explicit prohibition rules (L0) to ensure output quality. Models must verify compliance with L0 rules before presenting any draft. This approach treats critical formatting and language rules as hard constraints, not suggestions.

## 1.1 Core Rules

### 1.1.1 L0: Absolute Prohibitions (Never Break)

These rules are mandatory for all outputs. Any violation = draft rejected. Check before every output.

**Formatting prohibitions:**
- No blank lines between natural prose paragraphs inside the article body.
- Do not remove required block separators: YAML end, HTML/template blocks, images, intro blockquote, and headings must be separated from adjacent content by blank lines when writing Markdown for WeChat Converter.
- The intro blockquote must be followed by one blank line. Otherwise the first body paragraph may be swallowed into the quote.
- Images must be standalone Markdown image lines with blank lines before and after. This applies especially to fixed head/tail images.
- HTML/template blocks such as `section` must be closed, then followed by a blank line before any Markdown image, blockquote, heading, or prose.
- No checkboxes, no hanging indents, no large bullet-list blocks in body prose.
- Use natural paragraph prose as default. Lists only when information is genuinely list-shaped.

**Language prohibitions:**
- No parallelism patterns: "不是……而是……" (max 1-2 uses per article, only for real contrast), "第一、第二、第三" enumeration, consecutive same-structure sentences (3+ in a row), consecutive rhetorical questions.
- No formal checklist block structures: "定问题这块，我会问：...选材料这块，我会问：..." or "第一块...第二块..." patterns. Use natural paragraph flow with "比如，..." instead.
- No AI-flavor filler words: 综上所述, 值得注意的是, 不难发现, 本质上, 换句话说, 不可否认, 随着技术的发展, 在当今时代, 让我们来看看, 首先/其次/最后 (as paragraph starters), 赋能, 打造闭环, 深度融合, 全方位提升, 压舱石, 信息搜集官.
- No bookish phrasing: 选题站住, 材料铺满, 承担推进任务, 拉出来的观点, 结构重量, 把读者往前推, 进入问题, 丢在岔路里.
- No defensive explanations: avoid phrases like "研究别人可以很坦荡，借鉴也可以很正常" that explain away potential criticism. Just state what to do.
- Use "我/你" in natural contexts, not stiff "作者/读者" labels.
- Prefer colloquial verbs: "干的事" over "要问的是", "可没有" over "没有" for emphasis.

**Content prohibitions:**
- No table-of-contents announcements in the intro (e.g. "这篇文章将讨论……").
- No opening with source, creator, or process notes before the reader's pain point is established.
- No borrowed frameworks or judgments without source attribution at first use.
- No abstract method discussions without at least 2-3 concrete first-hand details.
- No prescriptive/teaching-tone endings (e.g. "下次你应该..." or "不妨先问自己..."). Prefer endings that回环 to the intro question, offer an open reflection, or share the author's current thinking without instructing the reader.

### 1.1.2 L1: Core Rules

- Do not start writing immediately. For publishable article work, the first response must stop at candidate value points, one recommended main line, and a temporary `publish_title`; no body text, headings, intro, or summary prose before the user confirms one value point or one angle.
- First identify the article's main value: what should the reader understand, judge, or do differently after reading?
- Treat research subjects, tools, creators, and internal process notes as supporting material, not as the automatic article center.
- If using another creator's explicit framework or judgment, introduce the source at first use.
- Prefer natural paragraph prose. Do not turn the article into a one-sentence-per-line outline.
- Avoid habitual AI phrasing, especially empty transitions, excessive "not X but Y", and parallel-question scaffolding.
- Put `summary` in YAML frontmatter. Body must start with one blockquote intro paragraph, followed by one blank line.
- Publishable AI-channel articles must include publishing metadata in YAML: `publish_title`, `publish_summary`, `publish_description`, `publish_tags`, and `delivery_links`.
- `publish_title` should usually target about 30 Chinese characters when possible. Its goal is to increase click-through rate while staying true, legal, logical, and fully supported by the article. A good title must let ordinary readers understand within 2 seconds: this is related to me, opening it is useful, and there is a reason to keep reading. Before generating a title, the model must actively consult the title hot-word bank in `references/wechat-style-and-review.md`: pick relevant object/platform/tool words, pain-point words, value/result words, and curiosity/contrast/number hooks before writing. Do not skip this step. Title principles: (1) Stand in the reader's shoes and show tangible benefits or value, not abstract concepts like "从完整到准确" or "判断权回到你手里". (2) Dig into real pain points: feeling unnoticed, struggling to improve quality, wanting to monetize but unable to build an IP. (3) Include concrete, relatable problems or questions (avoid abstract concepts like "分水岭" or "边界"). (4) Include hot keywords related to the topic (tool names, concepts, platforms like AI, 公众号, 写作). (5) Show clear value or outcome (what readers will learn or be able to do). (6) Include specific deliverable if applicable (e.g., "四个动作", "三个方法"). (7) Quantify when possible, using real numbers, steps, time, quantities, or before/after contrasts; do not invent results or imply guaranteed outcomes the article cannot support. (8) Focus on the author's own methodology and value, not on riding the coattails of research subjects (e.g., avoid "研究花叔和卡兹克" in titles). (9) Use concrete, perceivable contrasts to create impact (e.g., "以前4小时，现在10分钟" or "想要3句话，AI写2000字"). Numbers and time comparisons are powerful. (10) Use colloquial, everyday language instead of abstract or formal concepts. Replace abstract terms with expressions people actually say: "不出活儿" instead of "缺少边界", "白忙活" instead of "效率低下", "听不懂人话" instead of "理解偏差". (11) Avoid grand narratives; focus on specific, relatable scenarios. "写总结" is better than "使用AI工具". (12) Titles may emphasize real pain points, real benefits, real contrast, and real suspense, but must not fabricate facts, exaggerate results, create false conflict, or promise anything the article does not deliver.
- Draft `publish_title` early, before final polish. Do not wait until publication to think about the title; the title should help test the article's reader value, keywords, curiosity, and search surface during drafting.
- `publish_summary` must be under 100 Chinese characters, create curiosity without spoiling the whole article, and must not fabricate facts, exaggerate results, or promise value the article does not deliver.
- `publish_tags` must include core promotion/search keywords for the topic, such as tool names, workflow names, and concept keywords.
- For publishable drafts, do not repeat the title as a body heading.
- For publishable drafts, the body must contain structural headings: normally 2-4 level-one `#` headings, optional `##` only when naturally needed, and no `####` or deeper headings.
- The intro blockquote must be a single natural paragraph. No hard character count; aim for roughly 3 lines on a mobile screen. The intro is just an entry point—keep it brief and inviting, start from a concrete pain point or scene, do not pack in details or preview the full argument. A one-line slogan still fails review.
- After the intro/body separator, do not add blank lines between ordinary prose paragraphs. However, keep block-level separators around headings, Markdown images, HTML/template blocks, and the intro blockquote. The rule is "no blank line between prose paragraphs", not "no blank line anywhere".
- When preparing Markdown for WeChat Converter, if prose paragraphs are written as consecutive lines without blank lines, each ordinary prose paragraph line should end with two spaces to force a Markdown hard break, unless the converter/template layer will output each paragraph as an independent `<p>` or `<section>` node.
- After the intro, do not jump straight into the first heading. Use one or two natural prose paragraphs to enter through a concrete event, story, or conflict before the first structural heading. For AI-channel pieces, prefer the sequence: long-term pain point -> real usage scene -> why the system helps -> where it still fails -> why that failure matters.
- Headings should be short, colloquial, and down-to-earth, usually 4-6 Chinese characters. Prefer conversational phrasing such as questions (e.g. "怎么选题？") over formal labels (e.g. "选题先过关"). Avoid long explanatory headings or bookish tones.
- Treat excessive parallelism, repeated rhetorical questions, and repeated "not X but Y" structures as rewrite blockers, not polish notes.
- Before writing or revising real AI-channel articles in the user's vault, consult the user's own article database first. Ask the user for their article database location if not specified. Use the latest 2 same-type pieces plus 1-3 keyword-related pieces when available.
- When the user asks for publishable AI-channel article work, the user's own article database is mandatory reference, not optional inspiration.
- Final delivery must state which database pieces were consulted and what style/process rules were extracted. If the database was not consulted, state why.
- Every publishable article must include at least 2-3 concrete first-hand details: a specific experience, a real tool interaction, a particular failure, or an actual editing decision the author made. Abstract method discussions without personal anchors are not publishable.
- Avoid repetitive examples that demonstrate the same pattern. If using multiple examples, ensure each shows a different dimension or aspect. Do not use similar metaphors or scenarios multiple times (e.g., "收拾房间" and "收拾桌子" are redundant).
- Do not dump full prompt text or detailed prompt versions into the article body. Describe the effect or contrast instead. Readers care about outcomes, not verbatim prompts.
- Avoid framing technology evolution as personal habit change. Instead of "以前我用AI的习惯是...现在我发现...", frame it as "前两年的技术...现在的模型...". Attribute changes to technology advancement, not user behavior shifts.
- Check logical relationships in arguments carefully. Avoid oversimplified linear claims like "越X越Y" unless the relationship is genuinely linear. Consider whether the relationship is actually multidimensional or conditional.
- Verify that metaphors and golden sentences have internal logical consistency. Avoid mixing incompatible conceptual frameworks (e.g., architectural + mechanical metaphors without clear connection).
- Use concrete, specific details over generic descriptions. Include actual tool names (Obsidian, Claude), framework names (PARA), realistic numbers ("1分钟" not "十几秒", "2000字" not "3000字"). Specific details make scenarios more real and relatable.
- Use truly colloquial language, not just "avoid formal language". Use expressions people actually say in conversation: "秀肌肉" instead of "展示能力", "不是一码事" instead of "完全不一样". Read the text aloud - if it sounds like a person talking, it's right.
- When revising after user hand-edits, learn from what the user cut: usually shorten over-explained paragraphs, remove cautious meta-explanations, use punchier headings, preserve natural jokes or mild complaints when they fit, and prefer plain tool-role explanations like "工作手册" or "仓库/施工队" over polished conceptual prose.
- Watch for repetition at all levels: similar examples showing the same pattern, metaphors reused in different sections, points restated without adding new insight. Delete ruthlessly. One vivid example beats three similar ones.
- Consider perspective shifts. Not every observation needs to come from "我". Sometimes "很多人开始意识到" is more effective than "我开始意识到". Vary the narrative voice to avoid self-centeredness.
- Endings must offer something new - a forward-looking thought, an open question, or a shift in perspective. Do not just restate the main argument or recycle metaphors already used in the body. If the ending only summarizes, rewrite it.
- Always do a sensitive-information pass before final delivery.
- When preparing a version that may be shared publicly or open-sourced, remove private names, local absolute paths, internal folder names that are only meaningful in the user's vault, tokens, IDs, secrets, and any sensitive workflow details that would not make sense to strangers.

## 1.2 Execution Contract

Use this fixed loop for publishable article work:

1. Input: topic or rough idea, target reader, available materials, and whether the task is draft, rewrite, or review.
2. Output: 2-3 candidate value points, a recommendation for the main line, and a temporary `publish_title` if the task is publishable.
3. Checkpoint: the user confirms one value point or one angle before full drafting starts.
4. Output: a full article draft in the required WeChat format, including YAML, intro, headings, and natural paragraphs.
5. **Mandatory L0 Check**: Before presenting the draft, explicitly confirm each L0 rule:
   - [ ] No blank lines between ordinary prose paragraphs
   - [ ] Required block separators preserved around YAML, HTML/template blocks, images, intro blockquote, and headings
   - [ ] Intro blockquote is followed by one blank line and does not swallow the first body paragraph
   - [ ] Fixed head/tail images are standalone image lines with blank lines around them
   - [ ] WeChat Converter source uses hard-break prose lines or independent paragraph HTML nodes so body text does not collapse into one paragraph
   - [ ] No checkboxes, hanging indents, or large bullet blocks
   - [ ] No parallelism: "不是……而是……" (checked count: __), "第一、第二、第三", consecutive same-structure sentences
   - [ ] No AI-flavor words: 综上所述, 值得注意的是, 本质上, 换句话说, 随着技术的发展, 让我们来看看, 首先/其次/最后, 赋能, 打造闭环, 压舱石, 信息搜集官
   - [ ] No bookish phrasing: 选题站住, 材料铺满, 承担推进任务, 把读者往前推, 进入问题, 丢在岔路里
   - [ ] Using "我/你" naturally, not "作者/读者"
   - [ ] No table-of-contents announcements in intro
   - [ ] Borrowed frameworks attributed at first use
   - [ ] At least 2-3 concrete first-hand details included
   If any item fails, fix before presenting the draft.
6. Checkpoint: run three visible review passes.
   - Pass 1: facts, names, links, metadata, and sensitive information.
   - Pass 2: structure, intro, headings, paragraph flow, and support for each section.
   - Pass 3: style, AI flavor, repeated parallelism, and final reading feel. During this pass, you must load and execute `../nook-humanizer-zh-review/SKILL.md` as the anti-AI-flavor sub-review layer, then merge fixes with WeChat rules taking priority.
7. Output: final `publish_title`, `publish_summary`, `publish_tags`, and `delivery_links`, plus a short review note describing what changed in each pass, including the Humanizer pass findings.
8. Stop condition: if a blocking issue appears in any pass, fix the draft before moving on. Do not carry known problems into the final delivery.

## 1.3 Reference Loading

Load references only as needed:

- For any article task, read `references/nook-content-principles.md`.
- For topic design, angle selection, or first drafts, read `references/wechat-production-workflow.md`.
- For rewriting, final polish, formatting, or AI-flavor review, read `references/wechat-style-and-review.md`.
- When the task involves creator-method research, Khazix/花叔 references, topic calibration, article archetypes, or preserving the user's content-system lineage, read `references/creator-source-patterns.md`.
- When converting between WeChat articles, short-video scripts, Xiaohongshu titles, or spoken drafts, read `references/channel-adaptation.md`.
- For any AI-flavor review, human-feel review, style review, or final polish pass, also read `../nook-humanizer-zh-review/SKILL.md`, `../nook-humanizer-zh-review/references/anti-ai-review-checklist.md`, and `../nook-humanizer-zh-review/references/wechat-adaptation.md`. This is a mandatory sub-review layer, not optional inspiration.
- For open-source or public-release material, read `references/open-source-safety-and-attribution.md`.

## 1.4 Default Workflow

1. Clarify the task and available materials.
2. Consult the user's AI-channel article database and extract relevant style/process cues.
3. Identify the reader, main value, and article type.
4. Decide whether the topic is ready; if not, propose a sharper angle instead of drafting.
5. Build a lightweight structure that serves the main value.
6. Write the article in natural Chinese prose.
7. **Execute mandatory L0 check**: Before presenting the draft, verify all L0 absolute prohibitions (formatting, language, content). Fix any violations immediately.
8. Review in three visible passes: hard facts, reader understanding, human judgment/style. The third pass must include a visible `nook-humanizer-zh-review` sub-pass for AI flavor, fake smoothness, mechanical sentence patterns, and missing concrete anchors.
9. Check source attribution and sensitive information.
10. For real production drafts in the user's vault, save the Markdown artifact to the appropriate local content repository before summarizing it.
11. Deliver the draft or revision in the format requested by the user, including database-reference notes and review notes.

## 1.5 Output Format

For publishable WeChat drafts, default to:

```markdown
---
title: 内部短标题
publish_title: 发布标题，建议接近 30 个字
summary: 写一段内部摘要，放在元信息里
publish_summary: 公众号摘要，不超过 100 字
publish_description: 发布说明、配套物料和链接备注
status: draft
tags:
  - 根据主题填写标签
publish_tags:
  - 根据主题填写发布话题标签
delivery_links: []
---
> One-paragraph intro.

Body starts here.
```

If the user asks for planning only, output the angle, reader value, main structure, and risks instead of a full draft.

If the user asks for review, prioritize findings and concrete revision advice before praise or summary.

## 1.6 Review Checklist

- The article's main value is visible early.
- Each section serves the main line.
- External frameworks are attributed when first used.
- Materials are processed, not dumped.
- The draft avoids obvious AI flavor and ornamental parallelism.
- The ending adds judgment or closure rather than slogans.
- No keys, tokens, private database IDs, local absolute paths, or private account information remain.
