# nook-tv-cover

![style test contact sheet](assets/examples/style-test-contact-sheet.png)

`nook-tv-cover` 是一个用于生成视频封面的 Codex skill。

它只处理三类视频封面：

- 长封面：YouTube，`1280x720`
- 短封面：B站，`1146x717`
- 竖封面：抖音 / 小红书 / 视频号，`1242x1660`

公众号封面不属于本 skill，请使用单独的 `nook-WeChat-cover`。

## 使用方式

一次正常交互应该是：

1. 用户上传人物参考图。
2. Agent 询问视频主题或关键内容。
3. Agent 提炼或确认主标题、副标题和英文标签。
4. Agent 询问生成哪类封面：长封面、短封面、竖封面，或三类全部。
5. Agent 询问风格：科技证据层、真人实景压暗、产品界面主视觉、高饱和爆款、极简大字，或默认科技风。
6. Agent 询问是否有产品截图、Logo、界面图或其他主题素材。
7. Agent 先生成 1 张烟测图，确认方向后再批量出候选。

如果用户已经给出足够信息，Agent 可以直接推断，不要反复问零碎问题。

## 人物参考图

支持这些人物图：

- 真人口播截图
- 真人白底图
- IP 图
- 白底 IP 图
- 半身图
- 场景图

要求：

- 保留身份特征、脸型、五官关系、发型、服装和关键道具。
- 使用虚拟背景时，需要把人物从原背景中分离出来。
- 白底图默认直接分离人物。
- 场景图默认识别人像主体，原背景可压暗、虚化或替换。
- 避免白边、脏边、硬贴感和“实拍人物贴赛博背景”的问题。

## 风格

当前推荐 5 套可复用风格：

- 科技证据层风格

![科技证据层风格](assets/examples/style-test-01-tech-evidence-long.png)

- 真人实景压暗风格

![真人实景压暗风格](assets/examples/style-test-02-real-background-long.png)

- 产品界面主视觉风格

![产品界面主视觉风格](assets/examples/style-test-03-product-ui-short.png)

- 高饱和爆款风格

![高饱和爆款风格](assets/examples/style-test-04-hype-vertical.png)

- 极简大字风格

![极简大字风格](assets/examples/style-test-05-minimal-vertical.png)

风格、构图和验收细则位于 `references/cover-workflow.md`。

## 首次部署

将整个 `nook-tv-cover` 文件夹复制到你的 Codex skills 目录。

保留这些内容：

- `SKILL.md`
- `README.md`
- `references/`
- `assets/`
- `nook-tv-cover.config.example.yaml`

如果你的 Codex Desktop 会话暴露了内置图片生成能力，可以直接使用，不需要额外 key。

如果你要使用外部 OpenAI-compatible 图片模型，复制配置样例：

```bash
cp nook-tv-cover.config.example.yaml nook-tv-cover.config.yaml
```

然后设置环境变量：

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_BASE_URL="https://your-compatible-endpoint.example.com"
```

Windows PowerShell：

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
$env:OPENAI_BASE_URL="https://your-compatible-endpoint.example.com"
```

如果不需要自定义网关，可以不设置 `OPENAI_BASE_URL`。

不要把真实 key 写入 `nook-tv-cover.config.yaml`、Markdown 或仓库。

## 配置说明

配置样例：

```yaml
image:
  provider: openai
  model: gpt-image-2
  api_key_env: OPENAI_API_KEY
  base_url_env: OPENAI_BASE_URL

output:
  dir: 50_Assets/AI_Images/nook-tv-cover
```

含义：

- `provider`：模型供应商标识。
- `model`：图片模型名称。
- `api_key_env`：从哪个环境变量读取 key。
- `base_url_env`：从哪个环境变量读取兼容接口地址。
- `output.dir`：生成图片保存目录。

## 隐私提醒

如果使用外部模型，人物参考图、产品截图和其他素材会上传到模型后端。

Agent 必须在上传用户私有人物图或素材到外部后端前，明确告知用户并获得同意。

## 不处理

本 skill 不处理：

- 微信公众号封面
- 文章封面
- 公众号双区封面
- 默认公众号 IP 人物封面

这些应由 `nook-WeChat-cover` 处理。
