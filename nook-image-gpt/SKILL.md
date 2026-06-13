# 1 nook-image-gpt

通过中转站调用 GPT Image 2.0 生成和编辑图片的 MCP 工具。

## 1.1 前置条件

- Node.js >= 18
- 中转站 API Key（[用量查询页](https://sub.jarodfund.xyz/key-usage)）

## 1.2 安装

```bash
cd 82_Skills/nook-skills/skills/nook-image-gpt/server
npm install
```

## 1.3 MCP 配置

### 1.3.1 opencode

编辑 `~/.config/opencode/opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "nook-image-gpt": {
      "type": "local",
      "command": [
        "node",
        "<仓库绝对路径>/82_Skills/nook-skills/skills/nook-image-gpt/server/index.js"
      ],
      "enabled": true,
      "environment": {
        "IMAGE_API_KEY": "sk-你的API密钥"
      }
    }
  }
}
```

### 1.3.2 Claude Code / Kiro CLI

在项目根目录（或 `~/.claude/`）创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "nook-image-gpt": {
      "command": "node",
      "args": ["<仓库绝对路径>/82_Skills/nook-skills/skills/nook-image-gpt/server/index.js"],
      "env": {
        "IMAGE_API_KEY": "sk-你的API密钥"
      }
    }
  }
}
```

重启 Claude Code 后，直接在对话里说「帮我生成一张图」即可，模型会自动调用 `generate_image` tool。

> ⚠️ Claude Code 沙箱模式下 MCP server 无法发出网络请求，建议用 opencode 或 Cursor 调用。

### 1.3.3 Cursor / Windsurf

图形界面添加 MCP Server：
- **Command**: `node`
- **Args**: `<仓库绝对路径>/index.js`
- **Env**: `IMAGE_API_KEY=sk-你的API密钥`

## 1.4 中转站 URL 自定义

默认使用 `https://sub.jarodfund.xyz`，如果需要切换其他中转站，在 `environment` 中添加 `IMAGE_API_BASE`：

```json
"environment": {
  "IMAGE_API_KEY": "sk-你的API密钥",
  "IMAGE_API_BASE": "https://你的中转站地址"
}
```

## 1.5 Tool 参考

### 1.5.1 generate_image

| 参数 | 必填 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| prompt | 是 | string | — | 生图提示词 |
| size | 否 | string | `1024x1024` | `1024x1024` / `2048x2048` / `2048x1152` / `3840x2160` / `2160x3840` |
| n | 否 | number | 1 | 生成数量（最大 10） |
| save_to_dir | 否 | string | — | 保存目录，传入则存为 PNG 并返回路径 |

**返回格式（base64 模式）：**

```json
{ "images": [{ "b64_json": "<base64..." }] }
```

**返回格式（save_to_dir 模式）：**

```json
{ "saved_to": ["/path/to/nook_gpt_xxx_0.png"] }
```

### 1.5.2 edit_image

用于图生图、参考图重绘、局部 mask 编辑。内部调用 `/v1/images/edits`，以 multipart 方式上传图片文件。

| 参数 | 必填 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| prompt | 是 | string | — | 编辑/重绘提示词 |
| image_path | 否 | string | — | 单张源图片路径 |
| image_paths | 否 | string[] | — | 多张参考图路径；与 `image_path` 至少传一个 |
| mask_path | 否 | string | — | 局部编辑 PNG mask 路径，透明区域会被编辑 |
| size | 否 | string | `1024x1024` | `1024x1024` / `2048x2048` / `2048x1152` / `3840x2160` / `2160x3840` |
| n | 否 | number | 1 | 生成数量（最大 10） |
| save_to_dir | 否 | string | — | 保存目录，传入则存为 PNG 并返回路径 |

**返回格式同 `generate_image`。**

**示例：**

```json
{
  "prompt": "保留人物身份和构图，改成电影海报质感，暖色布光",
  "image_path": "D:/nook_vault/tmp/source.png",
  "size": "1024x1024",
  "save_to_dir": "D:/nook_vault/output/imagegen"
}
```

## 1.6 触发路由

| 场景 | 调用方式 |
|------|----------|
| GPT Image 2.0（jarodfund 中转） | `generate_image`（默认模型 `gpt-image-2`） |
| GPT Image 2.0 图生图/改图 | `edit_image`（默认模型 `gpt-image-2`） |

未来扩展：

| 场景 | tool |
|------|------|
| Google Imagen | 后续添加 |
| z-image | 后续添加 |

## 1.7 从其他 Skill 调用

```markdown
## 出图环节
1. 调用 `generate_image` tool：
   - prompt: <根据上下文生成的提示词>
   - size: 按场景选择（见 size-reference）
2. 使用返回的 base64 或文件路径嵌入后续环节

## 图生图/改图环节
1. 调用 `edit_image` tool：
   - prompt: <编辑目标或风格迁移要求>
   - image_path/image_paths: <源图片路径>
   - mask_path: <可选，局部编辑时传入>
   - size: 按场景选择（见 size-reference）
2. 使用返回的 base64 或文件路径嵌入后续环节
```

## 1.8 安全说明

- API Key 通过 MCP 配置的 `environment` 字段注入，不硬编码
- 如需 `.env` 管理，可在启动前 `set IMAGE_API_KEY=sk-xxx`
