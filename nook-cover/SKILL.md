---
name: nook-cover
description: 建设态多平台封面生产 skill。用于规划或生成小红书、微信公众号、B站、YouTube、抖音、视频号等自媒体平台封面。当前 V0.2 聚焦小红书封面：按运行时选择 Codex image2.0、外部原子出图工具或用户素材生成主视觉，再按需用 HTML / 后处理稳定中文标题层。
---

# 1 nook-cover

`nook-cover` 当前处于建设态。

当前 V0.2 范围：

- 根据一句主题或标题生成一张小红书封面。
- 渲染前先生成内部 poster 风格设计 brief。
- 从 4 套小红书视觉系统中选择一套：人脸冲击封面、手账拼贴种草、产品截图主视觉、近大远小对比封面。
- 按运行时能力选择主视觉路线：Codex Desktop 内置 image2.0、`nook-image2-gpt`、`nook-qwen-image`、`nook-zimage`、用户自带素材。
- 检查中文标题、人脸遮挡、人物占比、标题占比和风格差异。
- 如果中文误写或需要批量复刻，再用 HTML / 后处理重建最终标题层。
- 导出 PNG 供人工视觉检查和发布筛选。

不要把失败的 HTML 固定模板当成设计系统。V04-2 的默认路线是先拿到真实主视觉，确认“像不像小红书”；HTML 只在需要稳定中文、批量替换标题、或可编辑图层时介入。

`nook-cover` 不接管外部工具 API key。外部原子工具仍按 `references/provider-routing.md` 使用：`nook-zimage`、`nook-qwen-image`、`nook-image2-gpt`。在 Codex Desktop 中，普通封面候选可以优先走内置 image2.0；在 ZCode、Claude Code、Cursor 等没有内置 image2.0 的运行时，必须配置外部原子工具或要求用户提供主视觉素材。

小红书爆款封面默认优先走 image2.0。执行前必须读取 `references/image2-direct-cover-contract.md`。如果运行时支持图生图，优先读取 `references/html-sketch-to-image2-workflow.md`：先用 HTML 生成布局草图，再让 image2.0 参考草图重绘成真实封面。HTML 只作为草图、中文兜底、结构验证、批量换字或后处理文字层，不再作为默认主成品路线。

如果运行时没有内置 image2.0，也没有可用外部出图工具和用户素材，不要把纯 HTML 样张包装成“完整小红书封面”。只能交付“中文标题 / 排版结构证明”，并明确说明它缺少真人、产品或场景主视觉。

## 1.1 工作流

```text
主题 / 标题
→ 平台 profile
→ 选择 4 套视觉系统之一
→ 选择可用主视觉路线：Codex image2.0 / 外部原子工具 / 用户素材
→ 人工 / agent QA：中文、脸、标题、风格、缩略图
→ 若中文错误或需要复刻：HTML / 后处理重建标题层
→ PNG 成品输出
```

首次部署或换机器时，运行交互式配置：

```bash
node scripts/setup-provider.cjs
```

该配置只写入本 skill 的工具路径和默认输出目录。各出图工具的 key 必须放在对应工具自己的 `.env` 中。

## 1.1.1 小红书 V04-2 四套视觉系统

### 人脸冲击封面

适合副业、成长、情绪钩子、职业转型。

- 真人半身或三分之二身，不能只有人头。
- 人物占 45%-55%。
- 大标题占 40%-50%，必须是第一视觉，不能只贴在顶部。
- 人物必须有动作或表情，不能是安静生活照。
- 使用厚描边、投影、贴纸、星星、箭头、便利贴。
- 禁止底部三等分按钮、菜单式菜谱卡、App 首页式布局。

别名：人物冲击贴纸风。

### 手账拼贴种草

适合探店、书单、生活方式、护肤、收藏型内容。

- 真实纸张层叠、毛边、胶带、手账材料感。
- 标题在撕纸上，但必须可读。
- 主体可以是人物、咖啡、桌面、产品。
- 不允许用规整矩形冒充撕纸。

别名：撕纸手账种草风。

### 产品截图主视觉

适合 AI 工具、教程、效率、工作流。

- 科技场景和人物讲解者结合。
- 标题是第一视觉，面板只能辅助。
- 允许霓虹、斜切框、箭头、警示贴。
- 避免假 UI 小字抢画面。

别名：科技教程爆款风。

### 近大远小对比封面

适合健身、自律、逆袭、前后变化、避坑。

- 黑橙高对比，斜向动势。
- 标题斜压进画面，强描边。
- 可用 before / after、粗箭头、刷痕。
- 人物必须完整可识别，不遮脸。

别名：黑橙冲击对比风。

## 1.2 当前平台

第一阶段只支持：

- 小红书封面 / 首图

后续平台：

- 微信公众号文章封面
- B站视频封面
- YouTube 缩略图
- 抖音竖版封面
- 视频号封面

## 1.3 参考文件

按需读取，不要一次性加载全部：

- `references/platform-cover-map.md`：平台封面差异和输出 profile。
- `references/xhs-cover-v01.md`：小红书 V0.1 brief、布局族和 QA 规则。
- `references/xhs-poster-v03-visual-systems.md`：小红书 V04 / V04-2 视觉系统修正方向。需要做“更像小红书”“不像 PPT”“爆款封面”的任务时优先读取。
- `references/provider-routing.md`：三套出图工具的独立路由、交互式配置和 key 边界。
- `references/image2-direct-cover-contract.md`：image2.0 直出小红书爆款封面的默认合同。执行小红书封面成品生成时必须优先读取。
- `references/html-sketch-to-image2-workflow.md`：HTML 布局草图到 image2.0 图生图重绘的推荐工作流。运行时具备图生图能力时优先读取。
- `references/v04-2-workflow.md`：当前主流程。执行小红书封面任务时必须读取。
- `references/v05-html-visual-contracts.md`：四套视觉系统的 HTML 可执行构图、文字效果和辅助元素合同。需要生成或修复封面视觉风格时必须读取。
- `references/v05-template-map.md`：V05 四套 HTML 模板的入口、brief 路径、适用场景和图片通道边界。执行 HTML 模板渲染前必须读取。
- `references/v04-2-prompt-recipes.md`：四套风格的 image2.0 提示词模板。
- `references/usage-for-agents.md`：agent 调用本 skill 的执行说明。
- `references/deployment.md`：给 Codex / Claude Code / Cursor / Zcode 的部署和使用说明。
