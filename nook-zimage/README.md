# nook-zimage

ModelScope **Z-Image Turbo** 出图 skill：低价、快速、草图 / 练手 / 背景 / 任意「先看个图」场景的默认选择。

## Quick Deploy — 拿到链接就部署

把下面这条 URL 丢给自己的 AI 客户端（Trae IDE / Codex CLI / Claude Code / Kiro / Cursor / Windsurf / Continue 都行），告诉它「**部署这个项目**」，然后在提示时贴上你的 [ModelScope SDK Token](https://modelscope.cn/my/myaccesstoken)，其它 MCP 配置它会自动写好。

```
https://github.com/captain-nook/nook_skills/tree/main/nook-zimage
```

也可以手动：

```bash
git clone https://github.com/captain-nook/nook_skills.git
cd nook_skills/nook-zimage
npm install
node setup.js    # 粘贴 MS_API_KEY
```

装完**重启 agent**，然后在 agent 里直接说中文就行。

## 什么时候用我

| 你说 | 走 | 备注 |
|---|---|---|
| 「生一个美女」/「出图」/「测试」/「草图」/「背景」/「draft」 | `nook-zimage` ← 你在这里 | 默认走这条，便宜快 |
| 「小红书封面」/「公众号头图」/「海报」/「高质量」/「中文」/「印刷」 | `nook-qwen-image` | 强中文排版，参考兄弟 skill |
| 「改图」/「换背景」/「image to image」 | `nook-image2-gpt` | 图生图，单独项目 |

## 输出处理

- 默认：图片返回到对话里（agent 渲染 `![...](file:///...)` 内联显示）。
- 指定路径：直接说「存到 `D:\images\cat.jpg`」，会落盘到那个绝对路径。
- 不传路径时，本地也保一份到 `<project>/output/`，方便复看。

## 卸载

```bash
node setup.js --remove
```

会从所有 agent 的 MCP 配置里移除 `nook-zimage`，并清掉本地 `.env`。

## 详细文档

- [SKILL.md](./SKILL.md) — 完整工具说明、参数、MCP 工具 schema。
- [references/agent-deployment.md](./references/agent-deployment.md) — 各 AI 客户端配置路径排错。
- [AGENTS.md](./AGENTS.md) — AI Agent 看到的「快速部署」操作流程。
