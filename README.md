# Nook Skills

微信公众号内容写作工具集。

## Quick Deploy — 拿到链接就部署

把下面两条 URL 之一丢给自己的 AI 客户端（Trae IDE / Codex CLI / Claude Code / Cursor / Windsurf / Continue 都行），告诉它「**部署这个项目**」，然后你只需要在提示时贴上你的 [ModelScope SDK Token](https://modelscope.cn/my/myaccesstoken)，其它 MCP 配置它会自动写好。

- 出图（中文海报 / 封面 / 高质量文生图）→ https://github.com/captain-nook/nook_skills/tree/main/nook-qwen-image
- 出图（低价快速 / 草图 / 背景 / 练手）→ https://github.com/captain-nook/nook_skills/tree/main/nook-zimage

部署完一次后，自然语言调用就行，agent 会自己按意图选模型：

| 你说 | 用 | 备注 |
|---|---|---|
| 「生一个美女」/「出图」/「测试」/「草图」/「背景」/「draft」 | `nook-zimage` | 默认走这条，便宜快 |
| 「小红书封面」/「公众号头图」/「海报」/「高质量」/「中文」/「印刷」 | `nook-qwen-image` | 强中文排版 |
| 「改图」/「换背景」/「image to image」 | `nook-image2-gpt` | 图生图，单独项目 |

> 想保存到指定路径直接说「存到 D:\images\cat.jpg」，图片会落到那个位置；没说就返回到对话里。

卸载：`node setup.js --remove`。详细排错见各项目下 `references/agent-deployment.md`。

## 项目列表

| Skill | 说明 |
|-------|------|
| `nook-wechat-writer` | 公众号文章写作执行 |
| `nook-humanizer-zh-review` | 中文去 AI 味审校 |
| `nook-card` | 卡片设计 |
| `nook-tv-cover` | TV/哔哩哔哩封面设计 |
| `nook-image-gpt` | GPT Image 2.0 图片生成（MCP server 在 nook_mcp） |
| `nook-image2-gpt` | GPT Image 高质量图生图 / 改图 |
| `nook-zimage` | ModelScope Z-Image Turbo 低成本快速文生图 |
| `nook-qwen-image` | ModelScope Qwen-Image 中文海报、封面和高质量文生图 |
| `third_party/Humanizer-zh` | 第三方去 AI 检测工具 |

每个目录下有对应的 `SKILL.md` 详细说明。
