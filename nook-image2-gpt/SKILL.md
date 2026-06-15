---
name: nook-image2-gpt
description: Atomic image generation skill backed by the nook-image2-gpt MCP server. Use when Codex needs stable text-to-image or image-to-image generation through submit_image_task and get_image_result, especially as a low-level image provider for larger skills such as nook-poster.
---

# nook-image2-gpt

异步任务驱动的图片生成 MCP 工具。通过 `submit_image_task` + `get_image_result` 提供文生图和图生图能力。

**MCP server 名称：`nook-image2-gpt`**
**提供 tool：`submit_image_task`、`get_image_result`**

---

## 1. 部署（agent 执行，用户零操作）

1. 克隆仓库到本地
2. 向用户索取中转站 API Key
3. 在本目录执行：`node setup.js`，按提示输入 API Key 和中转站 URL
4. 提示用户重启 agent 客户端

脚本自动完成：安装依赖 + 写入 Agent MCP 配置。

---

## 2. AI 使用说明

> 以下内容供 AI 阅读。

### 2.1 MCP 依赖

本 skill 依赖 **`nook-image2-gpt` MCP server**。

调用出图时，**必须使用 `submit_image_task` 和 `get_image_result` 两个 tool**，不得自行编写代码或调用其他 API。
若 tool 列表中没有这两个名字，说明 MCP server 未启动，提示用户重启 agent。

### 2.2 submit_image_task（提交任务）

| 参数 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `prompt` | 是 | — | 提示词，越短出图越快 |
| `size` | 否 | `1024x1024` | 见下方尺寸表 |
| `n` | 否 | 1 | 生成数量（1-4，图生图推荐 1） |
| `mode` | 否 | `text_to_image` | `text_to_image` 或 `image_to_image` |
| `input_image_path` | 图生图时必填 | — | 源图片绝对路径 |

**返回：** `{ task_id, status: "queued", estimated_wait }`

提交后立即返回，不阻塞。后台 worker 异步执行。

### 2.3 get_image_result（查询结果）

| 参数 | 必填 | 说明 |
|---|---|---|
| `task_id` | 是 | `submit_image_task` 返回的 ID |

**返回：**
- `status`: `queued` / `processing` / `succeeded` / `failed`
- `image_paths`: 成功时的图片路径数组
- `error`: 失败时的错误信息

轮询间隔建议 10-15 秒。成功后取 `image_paths[0]` 作为图片路径。

### 2.4 尺寸表

| size | 比例 | 适用场景 |
|---|---|---|
| `1024x1024` | 1:1 | 头像、图标（默认） |
| `2048x2048` | 1:1 | 高清方图 |
| `2048x1152` | 16:9 | 封面图、宽屏插图 |
| `3840x2160` | 16:9 | 桌面壁纸、横幅 |
| `2160x3840` | 9:16 | 手机壁纸、海报 |

---

## 3. 在其他 Skill 中调用

详细集成约定见 `references/integration-contract.md`。上层生产级 skill 应把本 skill 当作原子出图 provider，只接收本地图片路径，不依赖中转站、API key 或代理细节。

在你的 SKILL.md 的出图章节中粘贴以下片段：

```markdown
### 出图（nook-image2-gpt）

前置检查：tool 列表中必须存在 `submit_image_task` 和 `get_image_result`。

1. 调用 `submit_image_task`
   - prompt: <构造提示词>
   - mode: text_to_image / image_to_image
   - size: <按场景选择>
   - input_image_path: <图生图时传入>

2. 轮询 `get_image_result(task_id)` 直到 status 为 succeeded
   - 间隔 10-15s
   - 成功后取 image_paths[0]
```

本 MCP 只负责出图。提示词构造、图生图源图管理、输出文件搬运由上层 Skill 负责。
