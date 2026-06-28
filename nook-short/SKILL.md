---
name: nook-short
description: Plan and draft Chinese short video and Xiaohongshu image-text content for Douyin, Xiaohongshu, and WeChat Channels. Use when Codex needs to turn a mid-form transcript, project recap, idea, flash thought, hot topic, or platform sample data into a weekly 12-piece content plan, content briefs, direct oral scripts, Xiaohongshu carousel text, or when the user asks what is trending on Xiaohongshu/Douyin/Channels today and platform sampling should inform planning.
---

# nook-short

Use this skill to plan and land short video / image-text content for Douyin, Xiaohongshu, and WeChat Channels.

Default weekly output:

- Douyin: 4 short videos.
- Xiaohongshu: 2 carousels + 2 short videos.
- WeChat Channels: 4 short videos.

## Workflow

1. Identify input source: mid-form transcript, project recap, idea, hot topic, platform samples, or mixed sources.
2. Build two lanes:
   - `anchor_lane`: transcript / project / long-form material; proves ability and expertise.
   - `live_lane`: hot topics / search / platform samples / current observations; adds timeliness and human feel.
3. If the user asks about current platform news or asks for weekly planning without enough live material, run or request platform sampling. See `references/platform-sampling.md`.
4. Extract assets: result, pain, pitfall, viewpoint, case, list, process.
5. Score platform + model fit. See `references/planning-layer.md`.
6. Produce content briefs before drafting.
7. Draft only after each brief has a selected template and filled slots. See `references/writing-templates.md`.
8. For Xiaohongshu carousels, plan cover + pages before writing body text. See `references/xhs-carousel.md`.

## Hard Rules

- Do not turn every item into the same topic. A 12-piece week should contain at least 3 content mother-themes unless the user explicitly accepts a narrow campaign.
- Do not present a project itself as the goal. Show the author's ability, judgment, process, result, or business value through the project.
- Do not write freeform scripts first. Fill the platform template slots first.
- Do not invent cases, metrics, comments, or screenshots.
- Do not copy platform sample titles, text, cover wording, or comments. Use samples only to extract patterns.
- Short-video script bodies must be direct oral text. Do not include camera directions unless the user asks.
- For teleprompter-ready text, keep no blank lines inside the body.

## Output Order

For planning requests, output:

1. Asset judgment.
2. Source lane ratio.
3. Weekly matrix.
4. Content briefs.
5. Open risks or missing inputs.

For landing requests, output:

1. Template fill.
2. Direct script or carousel text.
3. Structure labels.
4. Platform-specific ending path.

## References

- Platform sampling: `references/platform-sampling.md`.
- Planning layer: `references/planning-layer.md`.
- Writing templates: `references/writing-templates.md`.
- Xiaohongshu carousel: `references/xhs-carousel.md`.
