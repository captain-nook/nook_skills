# nook-qwen-image

ModelScope **Qwen-Image** 出图 skill：中文海报、公众号头图、小红书封面、印刷物和强文字排版场景的默认选择。

## Quick Deploy — 拿到链接就部署

把下面这条 URL 丢给自己的 AI 客户端（Trae IDE / Codex CLI / Claude Code / Kiro / Cursor / Windsurf / Continue 都行），告诉它「**部署这个项目**」，然后在提示时贴上你的 [ModelScope SDK Token](https://modelscope.cn/my/myaccesstoken)，其它 MCP 配置它会自动写好。

```
https://github.com/captain-nook/nook_skills/tree/main/nook-qwen-image
```

也可以手动：

```bash
git clone https://github.com/captain-nook/nook_skills.git
cd nook_skills/nook-qwen-image
npm install
node setup.js    # 粘贴 MS_API_KEY
```

装完**重启 agent**，然后在 agent 里直接说中文就行。

## 什么时候用我

| 你说 | 走 | 备注 |
|---|---|---|
| 「生一个美女」/「出图」/「测试」/「草图」/「背景」/「draft」 | `nook-zimage` | 默认走那条，便宜快 |
| 「小红书封面」/「公众号头图」/「海报」/「高质量」/「中文」/「印刷」 | `nook-qwen-image` ← 你在这里 | 强中文排版 |
| 「给这张图加个标题」/「给小姐姐加个封面」/「换背景但保留人物」 | `nook-qwen-image` 的 `submit_qwen_image_edit_task` | 图像编辑：把 zimage 的结果喂进来，加中文 |
| 「改图」/「换背景」/「image to image」 | `nook-image2-gpt` | 图生图，单独项目 |

## 组合用法（zimage → qwen edit）

最快出小红书封面的套路：

1. 先让 agent 用 zimage 生一张底图
2. 把 zimage 的 `image_path` 喂给 `submit_qwen_image_edit_task`，prompt 写清楚要保留什么、加什么文字

agent 跟用户对话时，只要说「给小姐姐加个春日穿搭封面」就能自动串起来。

## 输出处理

- 默认：图片返回到对话里（agent 渲染 `![...](file:///...)` 内联显示）。
- 指定路径：直接说「存到 `D:\images\cover.jpg`」，会落盘到那个绝对路径。
- 不传路径时，本地也保一份到 `<project>/output/`，方便复看。

## 卸载

```bash
node setup.js --remove
```

会从所有 agent 的 MCP 配置里移除 `nook-qwen-image`，并清掉本地 `.env`。

## 详细文档

- [SKILL.md](./SKILL.md) — 完整工具说明、参数、MCP 工具 schema。
- [references/agent-deployment.md](./references/agent-deployment.md) — 各 AI 客户端配置路径排错。
- [AGENTS.md](./AGENTS.md) — AI Agent 看到的「快速部署」操作流程。
