# 出图工具路由

`nook-cover` 不内置出图模型，也不接管 API key。

三套出图工具作为独立原子 skill / 工具维护：

- `nook-zimage`：测试、快速草图、低成本背景探索。
- `nook-qwen-image`：中文海报、中文封面、中文审美相关素材。
- `nook-image2-gpt`：高质量主视觉、图生图、参考图保持、正式素材。

`nook-cover` 负责上游设计 brief、平台 profile、排版规则、HTML 渲染和 PNG 导出。它只在需要素材时，根据 brief 选择一条工具路线。

## 配置方式

首次部署时运行：

```bash
node scripts/setup-provider.cjs
```

该脚本会自动尝试发现同级目录里的三套原子工具，并写入 `nook-cover/.env`：

```text
NOOK_COVER_OUTPUT_DIR=./output
NOOK_COVER_DEFAULT_PROVIDER=none
NOOK_ZIMAGE_PATH=
NOOK_QWEN_IMAGE_PATH=
NOOK_IMAGE2_GPT_PATH=
```

`nook-cover/.env` 是路由表，只告诉大 skill 去哪里找工具。各出图工具的 API key、base URL、模型名，放在各自工具目录的 `.env` 中。发布 `nook-cover` 时不要提交任何 `.env`。

如果 `setup-provider.cjs` 找到了原子工具，它会提示是否立刻进入各工具自己的 `setup.js`：

```bash
cd ../nook-zimage/nook-zimage
node setup.js

cd ../nook-qwen-image
node setup.js

cd ../nook-image2-gpt
node setup.js
```

常见字段：

```text
nook-zimage / nook-qwen-image:
MS_API_KEY=
MS_API_BASE_URL=https://api-inference.modelscope.cn

nook-image2-gpt:
IMAGE_API_KEY=
IMAGE_API_BASE_URL=
```

这几个字段不写入 `nook-cover`，只写入对应原子工具。

## 调用原则

默认优先级：

```text
用户自带素材 > image2 图生图/高质量主视觉 > qwen 中文视觉素材 > zimage 快速背景 > CSS/HTML 占位底图
```

中文标题和最终排版由 `nook-cover` 的 HTML 渲染层控制。不要依赖出图模型生成最终中文标题。

V04-2 之后的实际生产优先级：

```text
快速确认视觉效果 → Codex 内置 image2.0 直接出完整封面
低成本人物 / 草图 / 背景探索 → nook-zimage
中文海报 / 中文文字参与画面 → nook-qwen-image
高质量图生图 / 参考图保持 / 生产级收尾 → nook-image2-gpt 或 Codex 内置 image2.0
中文不准 / 需要批量复刻 → HTML / 后处理标题层
```

也就是说，HTML 不是每次都必须执行。只要 image2.0 的中文和构图已经通过 QA，可以直接使用整图成品。

## 交互式 brief

当信息不足时，agent 应该只问必要问题：

- 做哪个平台：小红书、公众号、B站、YouTube、抖音、视频号。
- 标题或主题是什么。
- 是否有人物、产品、截图、参考图。
- 是否允许调用出图工具；如果允许，优先哪条路线。
- 输出目录是否使用默认值。

用户没有明确要求出图时，先用 `none` 路线生成 HTML/PNG 样张。需要真实主视觉时，再触发对应原子工具。
