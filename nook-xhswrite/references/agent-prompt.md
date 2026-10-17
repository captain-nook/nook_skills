---
title: 给 agent 的提示词（用户版）
---

规则都写在 SKILL.md 里，用户不需要写长提示词。

## 用户最少只要说这一句

```text
用 nook-xhswrite 把这篇做成小红书图文：<素材文件路径>
```

agent 没注册 skill 时，补一句路径：

```text
先读 <skills 目录>/nook-xhswrite/SKILL.md，再按它做。素材：<素材文件路径>
```

## 给测试和对比用的完整版（弱模型、新 agent 验收时用）

```text
先完整读 nook-xhswrite 和 nook-xhspage 的 SKILL.md（xhspage 的 1.5 硬规则必须遵守）。
素材：<路径>。工作文件夹：素材旁边的 xhs_<名>/。
按关卡一个一个做，每个关卡写完文件就停下等我确认。
最后汇报贴出 deliver 的真实输出和退出码，有提醒逐条列出。
```

验收看五件事：是否问了品牌；是否逐关卡停下；图上数字和日期是否都在 facts 里；`deliver` 是否真的通过；skill 目录里有没有被改动（`git status`）。
