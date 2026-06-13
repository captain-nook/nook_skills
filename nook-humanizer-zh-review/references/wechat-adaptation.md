# WeChat Adaptation

Use this reference when applying `nook-humanizer-zh-review` to WeChat official-account articles or long-form article drafts.

## 1. Parent Skill Priority

`nook-wechat-writer` remains the parent skill. It controls:

- topic value;
- reader value;
- historical article database reference;
- publish_title, publish_summary, publish_tags, delivery_links;
- intro blockquote;
- heading structure;
- no blank lines inside article body;
- attribution and sensitive-information checks.

The humanizer pass must not break these rules.

## 2. Where to Run

Run this pass during Pass 3 of WeChat review:

1. First check WeChat-specific style: intro, headings, natural paragraphs, no blank lines, no oversized bullet blocks.
2. Then run the humanizer checklist for AI flavor.
3. Merge fixes. If a humanizer suggestion conflicts with WeChat format, WeChat format wins.

## 3. WeChat-Specific AI Flavor

Watch especially for:

- intro that announces a table of contents;
- body that reads like a report summary;
- headings that sound like formal labels instead of conversational anchors;
- repeated "不是……而是……" to manufacture insight;
- paragraphs that only explain concepts without concrete first-hand details;
- endings that teach the reader what to do next instead of returning to the article's real question;
- large list blocks used to simulate structure.

## 4. Repair Rules

- Keep natural paragraph prose as the default.
- Do not create blank lines between body paragraphs.
- Do not turn article prose into one-sentence-per-line rhythm.
- Replace abstract method talk with specific writing, editing, tool-use, or decision details.
- Keep 2-3 first-hand details when the article is publishable.
- Preserve source attribution when a framework or judgment comes from another creator.

## 5. Pass Standard

A WeChat article passes the humanizer layer only when:

- it still obeys WeChat formatting;
- the main value remains clear;
- AI filler and false contrast are removed;
- the draft has concrete details;
- the language sounds like a creator explaining a real concern, not a model completing an article structure.
