# Video Adaptation

Use this reference when applying `nook-humanizer-zh-review` to video transcripts, spoken scripts, or teleprompter drafts.

## 1. Parent Skill Priority

`nook-video-transcript` remains the parent skill. It controls:

- the one-sentence core expression;
- target duration and information density;
- spoken logic;
- opening hook;
- teleprompter-ready body;
- optional visual notes after the transcript;
- transcript database reference;
- video_title, video_description, publish_tags, delivery_links.

The humanizer pass must not rewrite a transcript into article prose.

## 2. Final Standard

The final test is not whether the text looks clean on the page. The final test is:

> Can the speaker say this naturally in one take?

If a sentence is readable but not speakable, rewrite it.

## 3. Video-Specific AI Flavor

Watch especially for:

- article voice copied into a spoken script;
- long sentences that require rereading;
- repeated "不是……而是……" or symmetrical diagnosis lines;
- short punch lines in every paragraph, creating a voiceover-ad feel;
- fake oral language that does not come from a concrete problem;
- too many abstract labels in a row;
- planning words in the spoken body: B-roll, A-roll, scene, shot, 画面, 分镜, 镜头, 灯光, 动作, 场景;
- endings that sound like a public-service announcement or course summary.

## 4. Repair Rules

- Split sentences by breath, not by visual rhythm.
- Keep useful repetition when it helps listening.
- Replace abstract stacks with one concrete scene or action.
- Use ordinary spoken verbs.
- Keep transition lines clear enough for listeners who cannot reread.
- Do not add slang just to look human.
- Do not remove all hesitation; a small boundary or self-correction can make speech more believable when it reflects real judgment.

## 5. Pass Standard

A transcript passes the humanizer layer only when:

- it can be copied into a teleprompter;
- it has no article headings inside the spoken body unless the speaker would actually say them;
- AI-pattern sentences have been removed or rewritten;
- the language sounds like the creator speaking, not like a narration model;
- the spoken rhythm still serves understanding.
