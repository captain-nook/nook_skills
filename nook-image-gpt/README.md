# nook-image-gpt

GPT Image 2.0 图片生成 / 图生图 MCP 工具，供 agent 调用。

## 部署（agent 执行）

**第一步：** 克隆或下载本仓库

**第二步：** 向用户索取 API Key（获取地址：https://sub.jarodfund.xyz/key-usage）

**第三步：** 在本目录下运行：

```bash
node setup.js sk-用户的key
```

脚本自动完成：安装依赖、检测并写入 opencode / Claude Code / Cursor 配置。

**第四步：** 提示用户重启 agent 客户端。

---

## 切换中转站（可选）

默认使用 `https://sub.jarodfund.xyz`，如需切换：

```bash
node setup.js sk-你的key https://你的中转站地址
```

---

## Tools

| Tool | 说明 |
|------|------|
| `generate_image` | 文生图 |
| `edit_image` | 图生图 / 局部编辑 |

支持尺寸：`1024x1024` / `2048x2048` / `2048x1152` / `3840x2160` / `2160x3840`

详见 [SKILL.md](./SKILL.md)
