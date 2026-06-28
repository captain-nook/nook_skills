# Platform Sampling

Use platform samples when the user asks things like:

- 今天小红书有什么消息？
- 今天抖音有什么热点？
- 这周工作怎么规划？
- 小红书 AI 博主现在都怎么做封面？
- 这个选题在平台上有没有人看？

## Sampling Roles

Platform sampling has three roles:

1. `topic_collection`: find current topics for `live_lane`.
2. `reference_content`: extract platform-native presentation patterns.
3. `comment_language`: collect real user questions, objections, and material requests.

## Keyword Pool

Start with user-provided keywords, then add relevant defaults:

```text
codex, claude code, hermes, 知识库, obsidian, gemini, AI工具, Agent工作流, AI自动化, 知识管理, Cursor, Claude, OpenAI, GPT, AI编程, AI写作
```

Group keywords:

```yaml
core_tools: codex / claude code / gemini / cursor / openai / gpt
workflows: hermes / 知识库 / obsidian / 知识管理 / agent工作流 / AI自动化
business_angles: AI工具 / AI编程 / AI写作 / AI副业 / 自动化办公
```

## Tool-Agnostic Sampling Interface

Do not require a specific crawler in the public skill. If a local sampling tool exists, use it. If not, ask the user for exported samples or do manual search when allowed.

Expected sample input:

```yaml
platform_samples:
  source: local_tool / manual_search / user_export
  platform: xhs / dy / sph / other
  keyword:
  captured_at:
  items:
    - title:
      note_type:
      cover_text:
      structure:
      metrics:
      comments:
      url_or_id:
```

## Small-Sample Limits

Use low-frequency small samples. Prefer 10-30 items per platform query and a small number of top comments per item.

Do not promise official hot lists. Treat sampling as directional evidence.

## Summary Format

After sampling, create or request a summary before planning:

```yaml
sample_summary:
  hot_topics:
    - topic:
      evidence:
      use_as: live_lane / xhs_reference / hook_source / reject
  presentation_patterns:
    cover_patterns:
    page_count_range:
    words_per_page_range:
    common_page_roles:
    save_reasons:
    proof_types:
  comment_language:
    repeated_questions:
    pain_words:
    material_requests:
    objections:
  planning_inputs:
    usable_angles:
    keywords_to_use:
    risks:
```

## Planning Use

- Use `hot_topics` to fill `live_lane`.
- Use `presentation_patterns` to shape Xiaohongshu carousels.
- Use `comment_language` to write hooks, cover pain points, and material names.
- Use `risks` to reject topics that are repetitive, weak, or unsafe.

Never copy sample text. Extract patterns only.
