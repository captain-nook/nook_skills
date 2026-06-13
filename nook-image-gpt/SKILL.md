# nook-image-gpt

通过中转站调用 GPT Image 2.0 生成和编辑图片的 MCP 工具。

> **前置要求**：使用前必须先完成下方「部署」章节，将 MCP server 注册到你的 agent 客户端。SKILL.md 本身只是使用说明，不能独立运行。

---

## 1. 部署（一次性操作）

### 1.1 安装依赖

```bash
cd <本文件所在目录>/server
npm install
```

### 1.2 获取 API Key

前往 [用量查询页](https://sub.jarodfund.xyz/key-usage) 获取你的 API Key（格式：`sk-...`）。

### 1.3 注册 MCP Server

在你的 agent 客户端里配置，把 `<server路径>` 替换成你本机 `server/index.js` 的**绝对路径**，`sk-你的key` 替换成真实 key。

**opencode** — 编辑 `~/.config/opencode/opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "nook-image-gpt": {
      "type": "local",
      "command": ["node", "<server路径>/index.js"],
      "enabled": true,
      "environment": {
        "IMAGE_API_KEY": "sk-你的key"
      }
    }
  }
}
```

**Cursor / Windsurf** — 图形界面 Settings → MCP → Add Server：
- Command: `node`
- Args: `<server路径>/index.js`
- Env: `IMAGE_API_KEY=sk-你的key`

**Claude Code / Kiro** — 在项目根目录创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "nook-image-gpt": {
      "command": "node",
      "args": ["<server路径>/index.js"],
      "env": {
        "IMAGE_API_KEY": "sk-你的key"
      }
    }
  }
}
```

> ⚠️ Claude Code 沙箱模式下出站网络受限，建议用 opencode 或 Cursor。

### 1.4 验证

重启客户端后，在对话里说「生成一张蓝色圆形图标」，模型应自动调用 `generate_image` tool 并返回图片。

### 1.5 切换中转站（可选）

默认使用 `https://sub.jarodfund.xyz`。如需切换，在配置的 `environment` / `env` 里加：

```
IMAGE_API_BASE=https://你的中转站地址
```

---

## 2. 给 AI 模型的使用说明

> 以下内容供 AI 阅读，描述如何调用本工具。

### 2.1 MCP 依赖声明

本 skill 依赖 **`nook-image-gpt` MCP server** 提供的两个 tool：`generate_image` 和 `edit_image`。

**必须通过这两个 tool 完成所有出图操作，不得自行编写代码或调用其他 API。** 如果 tool 列表里没有这两个名字，说明 MCP server 未启动，需要提示用户先完成部署。

### 2.2 tool：generate_image（文生图）

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | 是 | — | 生图提示词 |
| `size` | 否 | `1024x1024` | `1024x1024` / `2048x2048` / `2048x1152` / `3840x2160` / `2160x3840` |
| `n` | 否 | 1 | 生成数量（最大 10） |
| `save_to_dir` | 否 | — | 传入则存为 PNG 文件并返回路径；不传则返回 base64 |

**返回**：

```json
{ "saved_to": ["/path/to/nook_gpt_xxx_0.png"] }
// 或
{ "images": [{ "b64_json": "..." }] }
```

### 2.3 tool：edit_image（图生图 / 局部编辑）

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | 是 | — | 编辑目标或风格迁移描述 |
| `image_path` | 否 | — | 单张源图路径 |
| `image_paths` | 否 | — | 多张参考图路径（与 `image_path` 至少传一个） |
| `mask_path` | 否 | — | PNG mask 路径，透明区域被编辑 |
| `size` | 否 | `1024x1024` | 同上 |
| `n` | 否 | 1 | 生成数量（最大 10） |
| `save_to_dir` | 否 | — | 同上 |

**返回格式同 `generate_image`。**

### 2.4 尺寸选择建议

| 场景 | 推荐 size |
|------|-----------|
| 头像、图标、方形插图 | `1024x1024` |
| 封面图、宽屏插图 | `2048x1152` |
| 高清方图 | `2048x2048` |
| 桌面壁纸、横幅 | `3840x2160` |
| 手机壁纸、海报 | `2160x3840` |

---

## 3. 在其他 Skill 中调用（原子 skill 接入协议）

当你的 skill 需要出图时，在 SKILL.md 对应章节粘贴以下 snippet，替换括号内的占位符：

```markdown
### 出图（依赖 nook-image-gpt MCP）

前置检查：确认 tool 列表中存在 `generate_image`，否则提示用户先部署 nook-image-gpt。

**文生图：**
调用 `generate_image`：
- prompt: <根据上下文构造的提示词>
- size: <按场景从尺寸表选择>
- save_to_dir: <输出目录，留空则返回 base64>

**图生图：**
调用 `edit_image`：
- prompt: <改图/风格迁移要求>
- image_path: <源图片绝对路径>
- size: <按场景选择>
- save_to_dir: <输出目录>

返回值处理：
- save_to_dir 模式：用 `saved_to[0]` 路径继续流程
- base64 模式：用 `images[0].b64_json` 嵌入后续处理
```

**示例（小红书图文生产 skill 的出图章节）：**

```markdown
## 4. 出图环节

依赖 nook-image-gpt MCP 的 `generate_image` tool。

1. 根据笔记正文提炼视觉关键词，构造英文 prompt
2. 调用 `generate_image`：
   - prompt: <英文视觉描述>
   - size: `2048x1152`（小红书封面横图）
   - save_to_dir: <项目输出目录>
3. 将返回的 `saved_to[0]` 路径作为封面图插入排版环节
```
