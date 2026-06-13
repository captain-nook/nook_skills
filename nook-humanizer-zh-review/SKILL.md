---
name: nook-humanizer-zh-review
description: Review and rewrite Chinese content to remove AI flavor while preserving nook's real judgment, concrete details, and channel-specific style. Use as a sub-review skill during final style review, AI-flavor review, human-feel review, and polish for WeChat articles, long-form drafts, video transcripts, spoken scripts, and other nook content.
---

# nook-humanizer-zh-review

Use this skill as a focused review layer for Chinese anti-AI-flavor editing.

It is not a writing skill, title skill, or structure-design skill. It does not decide the article angle, video core line, publishing metadata, or content format. The parent skill keeps control of the content form; this skill checks whether the final language still sounds like AI.

## Core Position

AI flavor is not only a word-choice problem. In nook content, it usually comes from four failures:

1. The text uses familiar AI patterns: filler transitions, exaggerated significance, neat triplets, false contrasts, promotional language, assistant-like politeness, and generic positive endings.
2. The text is too smooth: every paragraph lands cleanly, every sentence has the same rhythm, and the ending summarizes instead of adding judgment.
3. The text lacks anchors: it has concepts and claims but not enough concrete actions, actual observations, editing decisions, failures, tool interactions, or named sources.
4. The text performs personality: it adds fake oral language, staged emotion, or dramatic examples instead of real human judgment.

The goal is not to make text messy. The goal is to make it concrete, direct, bounded, and believable.

## Mandatory Use

Parent nook skills must load this skill when entering any of these stages:

- 去 AI 味
- AI flavor review
- 人味校验
- 风格审校
- final polish
- rewrite for natural Chinese
- spoken realism review

For WeChat articles, use this after the article structure and publishing format already work.

For video transcripts, use this after the spoken line and teleprompter body already work.

## Reference Loading

Load references according to context:

- Always read `references/anti-ai-review-checklist.md`.
- Read `references/humanizer-zh-mapping.md` when comparing against Humanizer-zh-derived pattern categories.
- For WeChat articles, read `references/wechat-adaptation.md`.
- For video transcripts or spoken scripts, read `references/video-adaptation.md`.
- For provenance, public release, or open-source work, read `ATTRIBUTION.md`.

## Execution Contract

Use this fixed review loop:

1. Identify the parent content type: WeChat article, long-form note, video transcript, short script, or other.
2. Keep the parent skill's formatting and structural rules as higher priority.
3. Scan for AI-pattern issues at five levels:
   - word/phrase: filler terms, promotional words, assistant voice;
   - sentence: false contrast, neat triplets, over-balanced clauses, same-length rhythm;
   - paragraph: every paragraph sounds like a mini-summary, abstract stacks, fake transitions;
   - evidence: vague attribution, no concrete details, unsupported big claims;
   - ending: slogan, generic positive outlook, teaching-tone summary.
4. Decide the repair type:
   - delete a phrase;
   - simplify a sentence;
   - merge or split sentences;
   - replace abstract claim with concrete detail;
   - rewrite a paragraph;
   - ask for missing real detail if the problem cannot be honestly fixed.
5. Apply only the minimum rewrite needed to remove AI flavor without damaging the parent content form.
6. Produce a visible review note listing the main AI-flavor issues found and what was changed.

## Hard Rules

- Do not replace real judgment with safe neutrality.
- Do not make text artificially casual.
- Do not add fake personal stories, fake dates, fake users, fake data, or fake sources.
- Do not rewrite WeChat articles into video scripts.
- Do not rewrite video transcripts into article prose.
- Do not remove necessary repetition from video transcripts just because repetition looks redundant on the page.
- Do not optimize only by word substitution. If the sentence pattern is the problem, rewrite the sentence.
- If the draft lacks real details, say so. Do not invent them.

## Output Format

When used as a sub-review, output or include:

```markdown
Humanizer pass:
- 命中问题：...
- 处理方式：删词 / 改句 / 重写段落 / 保留但标注边界
- 剩余风险：无 / 需要用户补真实细节
```

For direct review tasks, provide:

1. Main findings.
2. Revised text.
3. Short change note.

## Pass Criteria

A draft passes this skill only when:

- no obvious AI filler or assistant voice remains;
- repeated false contrasts and neat triplets are removed or reduced;
- abstract claims have concrete anchors or honest boundaries;
- the text keeps channel-specific form;
- the reader or viewer can feel a real person made choices, not just a model completed a structure.
