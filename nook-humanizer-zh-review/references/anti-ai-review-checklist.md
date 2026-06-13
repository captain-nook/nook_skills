# Anti-AI Review Checklist

Use this checklist during the humanizer pass. The goal is to identify what must be deleted, simplified, grounded, or rewritten.

## 1. Quick Scan

Check whether the draft has any of these surface signals:

- filler transitions: 综上所述、值得注意的是、不难发现、本质上、换句话说、此外;
- grand openings: 随着技术的发展、在当今时代、今天我们来聊聊;
- corporate words: 赋能、闭环、深度融合、全方位提升、关键作用;
- false contrast: 不是……而是……、不仅……而且……、这不仅仅是……更是……;
- neat triplets: three nouns, three adjectives, three benefits, three questions used only to look complete;
- assistant residue: 希望这对你有帮助、如果你需要、当然可以、让我们;
- generic ending: 未来可期、这只是开始、让我们拭目以待、下次你可以;
- repeated paragraph rhythm: every paragraph is a summary, every sentence has similar length.

If the issue is only a surface phrase, delete or replace it. If the issue is sentence scaffolding, rewrite the sentence.

## 2. Concrete Anchor Check

For every major claim, ask:

- Is there a specific action, scene, tool interaction, failure, number, source, or editing decision?
- Can the reader or viewer picture what happened?
- Is the source named when the claim depends on outside authority?
- Is the example real, hypothetical, or pretending to be real?

If a paragraph has only concepts and no anchor, add real material from the source draft. If no real material exists, mark it as a missing-input risk instead of inventing.

## 3. Rhythm Check

Look for machine-like smoothness:

- consecutive same-length clauses;
- repeated sentence openings;
- repeated rhetorical questions;
- every paragraph ending with a short conclusion;
- every section using the same shape: problem -> explanation -> summary.

Repairs:

- combine repeated frames into one natural paragraph;
- vary sentence length only when it helps meaning;
- remove ornamental setup lines;
- let one sentence state the judgment directly.

## 4. Human Judgment Check

A draft should show a real person making choices. Check:

- Does it say what the author thinks, or only summarize what "people" think?
- Does it admit boundary or uncertainty when needed?
- Does it avoid fake certainty?
- Does the ending add a real shift, not just a summary?
- Is there any unnecessary beautiful sentence that hides a weak point?

If the text is clean but bloodless, add a grounded judgment. Do not add theatrical emotion.

## 5. Fake Human Voice Check

Human voice is not the same as casual slang. Watch for:

- staged scenes that are too perfect;
- dramatic phrases such as "后背一凉" or "凌晨三点" when not real;
- fake self-talk without information;
- jokes or complaints that do not point to a real problem;
- oral particles added to make writing look casual.

Repair by returning to the actual issue, action, or decision.

## 6. Rewrite Decision

Use this order:

1. Delete filler.
2. Simplify the sentence.
3. Replace abstract evaluation with concrete detail.
4. Merge repeated frames.
5. Rewrite the paragraph.
6. Ask for missing real detail.

Do not stop at word replacement when the structure is the problem.

## 7. Pass Note Template

Use this short note in parent-skill reviews:

```markdown
Humanizer pass:
- 命中问题：列出 1-4 个主要问题。
- 处理方式：说明删掉、改句、补具体锚点或重写的地方。
- 剩余风险：无 / 缺少真实细节 / 需要用户确认来源。
```
