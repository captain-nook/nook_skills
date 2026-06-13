# nook-image-gpt

通过中转站调用 GPT Image 2.0 生成和编辑图片的 MCP 工具。

**MCP server 名称：`nook-image-gpt`**
**提供 tool：`generate_image`、`edit_image`**

---

## 1. 部署（agent 执行，用户零操作）

收到用户发来的 GitHub 地址后，按以下步骤执行：

1. 克隆仓库到本地任意目录
2. 向用户索取 API Key（获取地址：https://sub.jarodfund.xyz/key-usage）
3. 在仓库根目录执行：
   ```
   node setup.js sk-用户的key
   ```
4. 提示用户重启 agent 客户端

脚本自动完成：安装依赖 + 写入 opencode / Claude Code / Cursor 的 MCP 配置。

---

## 2. AI 使用说明

> 以下内容供 AI 阅读。

### 2.1 MCP 依赖

本 skill 依赖 **`nook-image-gpt` MCP server**。

调用出图时，**必须使用下方两个 tool**，不得自行编写代码或调用其他 API。
若 tool 列表中没有这两个名字，说明 MCP server 未启动，提示用户重启 agent。

### 2.2 generate_image（文生图）

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | 是 | — | 生图提示词 |
| `size` | 否 | `1024x1024` | 见下方尺寸表 |
| `n` | 否 | 1 | 生成数量（最大 10） |
| `save_to_dir` | 否 | — | 保存目录；不传则返回 base64 |

**返回：**
```json
{ "saved_to": ["/path/nook_gpt_xxx_0.png"] }
// 或
{ "images": [{ "b64_json": "..." }] }
```

### 2.3 edit_image（图生图 / 局部编辑）

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | 是 | — | 编辑目标描述 |
| `image_path` | 否 | — | 单张源图路径 |
| `image_paths` | 否 | — | 多张参考图（与 image_path 至少传一个） |
| `mask_path` | 否 | — | PNG mask，透明区域被编辑 |
| `size` | 否 | `1024x1024` | 见下方尺寸表 |
| `n` | 否 | 1 | 生成数量（最大 10） |
| `save_to_dir` | 否 | — | 保存目录；不传则返回 base64 |

### 2.4 尺寸表

| size | 比例 | 适用场景 |
|------|------|----------|
| `1024x1024` | 1:1 | 头像、图标（默认） |
| `2048x2048` | 1:1 | 高清方图 |
| `2048x1152` | 16:9 | 封面图、宽屏插图 |
| `3840x2160` | 16:9 | 桌面壁纸、横幅 |
| `2160x3840` | 9:16 | 手机壁纸、海报 |

---

## 3. 在其他 Skill 中调用

在你的 SKILL.md 的出图章节中粘贴以下片段：

```markdown
### 出图（nook-image-gpt）

前置检查：tool 列表中必须存在 `generate_image`（来自 nook-image-gpt MCP）。

文生图：调用 `generate_image`
- prompt: <按上下文构造的提示词>
- size: <从尺寸表按场景选择>
- save_to_dir: <输出目录>

图生图：调用 `edit_image`
- prompt: <改图 / 风格迁移描述>
- image_path: <源图片绝对路径>
- size: <按场景选择>
- save_to_dir: <输出目录>

返回值：save_to_dir 模式取 saved_to[0]，base64 模式取 images[0].b64_json
```
