# 出图模型设置

本 skill 的 Nook 本地默认出图通道是 Codex Desktop 内置图片生成能力。

这条能力不需要用户提供 `OPENAI_API_KEY`。它在 Codex 会话日志中表现为：

- `image_generation_call`
- `image_generation_end`

生成结果通常保存到：

`$CODEX_HOME/generated_images/<thread-id>/`

如果用户使用 Codex Desktop 且当前会话暴露了内置图片生成工具，本 skill 优先使用该内置能力。

## 本地默认规则

凡是普通出图、改图、图生图、视频封面、高清化、风格迁移等请求，默认走 Codex Desktop 内置出图能力。

不要默认走这些路径：

- `image_gen.py`
- OpenAI SDK / Images API
- baoyu-imagine
- xai_router_image
- Replicate
- OpenRouter
- Azure
- DashScope
- Seedream / Jimeng
- 任何其他外部 provider 或 CLI

只有用户明确说“用某某模型”“用某某工具”“走 API/CLI”“用某某 provider”时，才使用对应外部通道。

## 当前运行时没有内置出图入口时

如果当前会话没有暴露 Codex Desktop 内置出图工具，必须这样处理：

1. 明确告诉用户：当前运行时没有暴露 Codex Desktop 内置出图能力。
2. 不要自行切到 CLI/API。
3. 不要要求用户提供 `OPENAI_API_KEY`。
4. 不要把问题说成模型无权限、key 缺失或 API 错误。
5. 只在用户明确选择 fallback 时，才走开源配置中的外部后端。

正确说法：

> 当前运行时没有暴露 Codex Desktop 内置出图通道，所以我不能直接触发默认无 key 出图。需要重新进入/重建带 image generation 工具的 Codex Desktop 会话，或由你明确指定一个外部模型通道作为 fallback。

## 开源用户配置

这个 skill 要开源，所以不能依赖作者本机的 Codex Desktop 内置能力。开源用户需要能够自主选择生图模型和 key。

开源版配置原则：

- 仓库只提供配置样例。
- 不写入真实 key。
- 不写入作者私有 base URL。
- 不写死只能用某一个 provider。
- 用户自己选择 provider/model/key。
- agent 不得在用户配置失败时自行换模型。

配置样例见：

`nook-tv-cover.config.example.yaml`

### 推荐部署方式

1. 将整个 `nook-tv-cover` 文件夹复制到自己的 Codex skills 目录。
2. 保留 `SKILL.md`、`references/`、`assets/` 和 `nook-tv-cover.config.example.yaml`。
3. 如果运行环境有 Codex Desktop 内置出图能力，不需要额外配置 key。
4. 如果要使用外部 OpenAI-compatible 图片模型，复制配置样例：

```bash
cp nook-tv-cover.config.example.yaml nook-tv-cover.config.yaml
```

5. 在系统环境变量里设置 key，不要写进仓库：

```bash
export OPENAI_API_KEY="your_api_key_here"
```

6. 如果使用自定义兼容网关，再设置：

```bash
export OPENAI_BASE_URL="https://your-compatible-endpoint.example.com"
```

7. 在 `nook-tv-cover.config.yaml` 中选择自己的 `provider`、`model`、`api_key_env` 和可选的 `base_url_env`。

Windows PowerShell 示例：

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
$env:OPENAI_BASE_URL="https://your-compatible-endpoint.example.com"
```

不要提交 `nook-tv-cover.config.yaml`，不要把真实 key、私有 base URL 或个人网关写入 Markdown。

## 外部后端隐私规则

带参考图的封面生成会把图片内容发送给模型后端。

规则：

- Codex Desktop 内置出图能力属于本地默认通道。
- 第三方 provider、OpenRouter、聚合网关、个人 CLI 等都视为外部后端。
- 使用外部后端上传用户私有参考图前，必须明确告知并取得用户同意。
- 不要把用户 key 写入仓库、Markdown 或配置样例的真实值。

## 常见故障

### 默认出图入口不存在

停止，并告诉用户：

> 当前运行时没有暴露 Codex Desktop 内置出图能力，无法执行默认无 key 出图。请重新进入带 image generation 工具的 Codex Desktop 会话，或明确指定一个外部出图后端作为 fallback。

### 用户明确选择外部后端但缺 key

停止，并告诉用户缺少哪一个环境变量，例如：

> 你选择了外部后端 `openai`，但当前没有找到 `OPENAI_API_KEY`。

### 外部后端返回权限错误

停止，并告诉用户具体错误。不要自动换模型。
