# Humanizer-zh Mapping for nook

This reference maps Humanizer-zh style pattern detection into nook's content workflow. It should be used as a pattern lens, not as a replacement for nook's own writing rules.

## 1. Content Inflation

Humanizer-zh flags exaggerated significance, legacy claims, promotional language, vague media attention, generic challenge/future sections, and shallow added depth.

In nook, treat these as blockers when the text says a thing is important without showing why.

Common repairs:

- Replace "意义重大 / 关键作用 / 深远影响 / 未来可期" with the concrete thing that happened.
- Replace "专家认为 / 行业报告显示" with a named source, or remove the claim.
- Replace "它代表了某种趋势" with the observable change, user behavior, product feature, or workflow result.
- Delete generic "挑战与展望" endings unless they contain specific next steps or real uncertainty.

## 2. AI Vocabulary and Filler Glue

High-risk terms include:

- 此外
- 值得注意的是
- 不难发现
- 至关重要
- 深入探讨
- 本质上
- 换句话说
- 这意味着
- 不可否认
- 随着技术的发展
- 在当今时代
- 让我们来看看
- 赋能
- 打造闭环
- 深度融合
- 全方位提升
- 充满活力
- 展示 / 彰显 / 体现 / 证明, when used as empty evaluation

Repair priority:

1. Delete the glue if the sentence still works.
2. Replace formal abstract words with ordinary verbs.
3. If the term carries real meaning, keep it but add a concrete anchor.

## 3. Mechanical Sentence Patterns

High-risk patterns:

- 不是……而是……
- 不仅……而且……
- 这不仅仅是……更是……
- 与其说……不如说……
- 首先 / 其次 / 最后 as obvious scaffolding
- consecutive same-structure sentences
- forced three-item lists
- false ranges such as "从 X 到 Y" where X and Y are not a real scale
- balanced clauses with similar length again and again

Repair priority:

1. Directly state the judgment.
2. Keep contrast only when it performs real analysis.
3. Use two items when two are enough.
4. Convert repeated sentence frames into one natural paragraph.

## 4. Formatting and Emphasis Artifacts

Humanizer-zh flags overused dashes, bold text, vertical title-list structures, decorative emojis, and assistant-style formatting.

In nook:

- WeChat articles should use natural paragraphs and a small number of useful headings.
- Video transcripts should use teleprompter-friendly blocks, not article headings inside the spoken body.
- Do not use formatting to manufacture rhythm.
- Do not rely on bold, dashes, or list titles to create fake clarity.

## 5. Assistant Voice and Conversation Residue

High-risk phrases:

- 希望这对你有帮助
- 如果你需要，我还可以……
- 当然可以
- 作为一个 AI
- 根据我的知识截止日期
- 感谢你的提问
- 让我们一起

Repair:

- Delete assistant residue from publishable content.
- If the text needs a reader-facing invitation, write it as part of the content form, not as a chat reply.

## 6. Generic Positive Endings

High-risk endings:

- 总之 / 综上所述
- 未来可期
- 这只是开始
- 让我们拭目以待
- 希望每个人都能……
- 不妨从今天开始……

Repair:

- Return to the opening problem.
- Add a bounded judgment.
- Name the next real uncertainty.
- For video, end with a speakable landing line instead of a slogan.

## 7. Nook-Specific Additions

Humanizer-zh focuses on detectable AI writing traces. nook adds these extra checks:

- Does the draft include real first-hand details?
- Is the judgment owned by the creator?
- Does the example support the point, or only decorate it?
- Is the uncertainty honestly stated?
- Is the text too smooth because it avoids the hard part of the argument?
- Is the language trying to look human instead of being specific?

If these fail, word-level cleanup is not enough. Rewrite the paragraph or ask for missing material.
