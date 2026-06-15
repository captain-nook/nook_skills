# nook-image2-gpt

异步任务驱动的 GPT-Image-2 图片生成 MCP 工具。通过中转站 API 调用，支持文生图和图生图。

**核心设计：** 不阻塞等待 → 提交任务立即返回 `task_id`，轮询查结果。避免 MCP 请求超时。

---

## Architecture

```
Agent/Skill
  │  submit_image_task(prompt, mode, ...)
  │  ──────────────►
  │                  MCP Server (Node.js)
  │                    │  后台 worker 调用中转站 API
  │                    │  (status: queued → processing → succeeded/failed)
  │  get_image_result(task_id)
  │  ◄──────────────
  │  { status, image_paths, error }
```

**为什么用异步任务层？**
- GPT-Image-2 生成耗时 30-60s（甚至更长），远超 MCP stdio 的合理超时窗口
- 同步调用会阻塞 Agent 数分钟，用户体验极差
- 拆成 `submit` + `get` 两个工具，Agent 可自行决定轮询频率，中间状态可见

**速度分析（实测数据）：**

| 场景 | 耗时 | 说明 |
|---|---|---|
| 网络往返（代理→中转站） | ~1.2s | 本地 proxy 延迟可忽略 |
| 文生图（短提示词 ≤20字） | 30-45s | 瓶颈在中转站上游模型 |
| 文生图（长提示词 ≥50字） | 45-90s 或超时 | 推荐用短提示词 |
| 图生图 n=1 | 45-65s | 单张编辑 |
| 图生图 n≥2 | 易超时（≥5min） | 上游限制，推荐 n=1 |

**瓶颈不在本地网络或代理，而在中转站对接的上游模型推理速度。** GPT-Image-2 本身是慢模型。如果需要更快的出图体验，需要更换上游模型或中转站。

---

## MCP Tools

| Tool | 作用 | 说明 |
|---|---|---|
| `submit_image_task` | 提交出图任务 | 立即返回 `task_id`，后台异步执行 |
| `get_image_result` | 查询任务状态 | 轮询，返回 `{status, image_paths, error}` |

### submit_image_task

| 参数 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `prompt` | 是 | — | 提示词，越短出图越快 |
| `size` | 否 | `1024x1024` | `1024x1024` / `2048x2048` / `2048x1152` / `3840x2160` / `2160x3840` |
| `n` | 否 | 1 | 生成数量（1-4，图生图推荐 1） |
| `mode` | 否 | `text_to_image` | `text_to_image` 或 `image_to_image` |
| `input_image_path` | 图生图时必填 | — | 源图片绝对路径 |

**返回：** `{ task_id, status: "queued", estimated_wait }`

### get_image_result

| 参数 | 必填 | 说明 |
|---|---|---|
| `task_id` | 是 | `submit_image_task` 返回的 ID |

**返回：**
- `status`: `queued` / `processing` / `succeeded` / `failed` / `not_found`
- `image_paths`: 成功时的图片路径数组
- `error`: 失败时的错误信息
- `estimated_wait`: 预估剩余等待秒数

---

## 被其他 Skill 调用

本 MCP 设计为原子级图片生成能力，供上层 Skill（如 "小红书内容生产系统"）组装调用。

在目标 SKILL.md 中粘贴以下片段即可编排：

```markdown
### 出图（依赖 nook-image2-gpt MCP）

检查 tool 列表中存在 `submit_image_task` 和 `get_image_result`，否则提示用户部署。

1. 调用 `submit_image_task` 提交任务
   - prompt: <构造提示词>
   - size: <按场景选择>
   - mode: text_to_image / image_to_image
   - input_image_path: <图生图时传入>

2. 轮询 `get_image_result(task_id)` 直到 status 为 succeeded 或 failed
   - 建议间隔 10-15s，最多 30 次（约 5 分钟）
   - 返回 image_paths[0] 即为图片路径

3. 若 failed，重试或报错
```

上层 Skill 只需通过 MCP 工具名调用即可，不需要关心中转站地址、API Key、代理等底层细节。

---

## Setup

### 前置条件

- Node.js ≥ 20
- 一个中转站 API Key（兼容 OpenAI `/v1/images/generations` 和 `/v1/images/edits` 接口）
- 可选：HTTP 代理（如网络需要）

### 安装

```bash
# 方式 A：一键部署（推荐；按提示输入 key/url，自动安装依赖、写入 .env、写入 Agent 配置）
node setup.js

# 方式 B：非交互部署（适合自动化；key 会出现在 shell 历史里，不推荐给普通用户）
node setup.js sk-your-key-here https://your-relay-server/v1

# 方式 C：手动部署
cd server && npm install
cd ..

# 在 nook-image2-gpt 根目录创建 .env 文件
cat > .env << EOF
IMAGE_API_KEY=sk-your-key-here
IMAGE_API_BASE_URL=https://your-relay-server/v1
IMAGE_MODEL=gpt-image-2
IMAGE_DRY_RUN=false
IMAGE_OUTPUT_DIR=output
EOF
```

### Agent 配置（.mcp.json）

```json
{
  "mcpServers": {
    "nook-image2-gpt": {
      "command": "node",
      "args": ["path/to/server/index.js"],
      "env": {
        "IMAGE_API_KEY": "sk-your-key-here",
        "IMAGE_API_BASE_URL": "https://your-relay-server/v1",
        "IMAGE_MODEL": "gpt-image-2",
        "IMAGE_RESPONSE_FORMAT": "b64_json",
        "IMAGE_DRY_RUN": "false",
        "IMAGE_OUTPUT_DIR": "output",
        "HTTPS_PROXY": "http://proxy:port",
        "HTTP_PROXY": "http://proxy:port"
      }
    }
  }
}
```

**注：** 代理地址仅当网络需要通过代理访问中转站时设置。若无此需求，可移除。

---

## Configuration

| 环境变量 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `IMAGE_API_KEY` | 是 | — | 中转站 API Key |
| `IMAGE_API_BASE_URL` | 否 | `https://sub.jarodfund.xyz/v1` | 中转站基础 URL |
| `IMAGE_MODEL` | 否 | `gpt-image-2` | 模型名称 |
| `IMAGE_RESPONSE_FORMAT` | 否 | `b64_json` | 返回格式 |
| `IMAGE_DRY_RUN` | 否 | `true` | 设置为 `false` 启用真实调用；`setup.js` 会自动写入 `false` |
| `IMAGE_OUTPUT_DIR` | 否 | `output` | 图片保存目录 |
| `HTTPS_PROXY` | 否 | — | HTTPS 代理地址 |
| `HTTP_PROXY` | 否 | — | HTTP 代理地址 |

---

## Security

- `.env` 文件已被 `.gitignore` 排除，**不会提交到 Git**
- API Key 仅存在于 `.env` 或 Agent 配置中，代码只通过环境变量读取
- `setup.js` 和 `.env.example` 中均使用 `sk-your-key-here` 占位
- 中转站 URL 在代码中有默认 fallback，但建议通过环境变量覆盖

---

## 图片输出策略

**每出一张立即落盘，不等待任务完成。**

- MCP Server 收到 API 返回的任意一张图片，立刻解码写入磁盘
- 即使 `n=2` 中第二张图失败，第一张图已确保保存
- 即使任务最终状态为 `failed`，任何已返回的图片文件都存在，不会丢失
- 输出目录通过 `IMAGE_OUTPUT_DIR` 配置（建议设为用户可见的目录）

**为什么这样做？**
- API 按调用计费，不管图片质量、尺寸是否合格，费用已产生
- 图片落地后用户就拿到了，不依赖后续任务状态流转
- 中途打断 agent 会话，已保存的图片文件不受影响

