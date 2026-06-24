# 1 nook-title

`nook-title` 是一个用于生成、分析和评分中文公众号标题 / AI 媒体标题的 Codex skill。它适合处理已经写完的 Obsidian 稿件、文章事实素材、链接内容或候选标题列表。

这个 skill 的重点不是单纯“写得炸”，而是在事实不翻车的前提下，把标题写得更有点击理由。它会优先抓取明确实体、真实数字、具体动作、冲突关系、后果和读者相关性。

你可以用很自然的话触发它，例如：

```text
给我取几个标题
帮这篇稿子想 10 个公众号标题
评估这几个标题哪个更适合发布
```

## 1.1 它会做什么

- 从稿件或素材中提取标题钩子：实体、数字、动作、对比、后果和事实边界。
- 生成多种标题方向：高点击 AI 媒体版、稳一点的公众号版、搜索友好版。
- 对候选标题做表层评分，判断标题强度和风险。
- 标出容易翻车的地方，例如编造数字、没有来源的榜单、把传言写成事实。

## 1.2 文件说明

- `SKILL.md`：主技能说明和触发描述。
- `references/high-density-ai-news-patterns.md`：高密度 AI 媒体标题结构和钩子词。
- `references/title-safety.md`：事实边界、夸张控制和标题安全规则。
- `references/sample-titles.md`：通用标题校准样本。
- `scripts/analyze_titles.py`：统计标题长度、标点、数字和英文实体出现率。
- `scripts/score_titles.py`：对候选标题做表层强度和风险评分。

## 1.3 脚本用法

```bash
python scripts/analyze_titles.py titles.txt
python scripts/score_titles.py candidates.txt
```

脚本要求输入 UTF-8 文本文件，每行一个标题。
