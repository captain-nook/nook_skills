---
title: V05 HTML 模板地图
type: reference
status: active
---

# V05 HTML 模板地图

本文给 agent 使用。目标是让 agent 明确：`nook-cover` 的 HTML 模板不是“凭感觉排版”，而是四套可执行的封面骨架。

## 入口

```text
scripts/render-xhs-v05-contract.cjs
```

Brief 可以提供真实主视觉图片：

```json
{
  "main_visual_image": "assets/example-person.png"
}
```

也可以使用绝对路径：

```json
{
  "main_visual_path": "D:/Nook Lab/example-person.png"
}
```

如果图片路径存在，renderer 会把图片放进当前模板的主视觉区域；如果不存在，则自动回退到占位视觉。

运行方式：

```bash
node scripts/render-xhs-v05-contract.cjs examples/xhs-v05/face-diet-brief.json output/v05-face-diet
```

如果本机没有 Playwright 浏览器，也可以先生成 HTML：

```bash
node scripts/render-xhs-v05-contract.cjs examples/xhs-v05/face-diet-brief.json output/v05-face-diet --html-only
```

## 四套模板

### 1. 人脸冲击封面

Brief:

```text
examples/xhs-v05/face-diet-brief.json
```

合同名：

```text
face-impact-v05
```

适合：

- 真人出镜。
- 生活方式、减脂、学习、避坑、挑战类封面。
- 需要强标题冲击的内容。

HTML 必须实现：

- 左上或中左超大三行标题。
- 红字 / 黑字交替，白描边，黑色硬阴影。
- 标题后方有大面积撕纸。
- 右侧保留人物安全区。
- 前景贴纸承载菜名、道具、关键词。

图片通道负责：

- 真人半身照。
- 表情、手势、真实菜品或道具。

### 2. 手账拼贴种草

Brief:

```text
examples/xhs-v05/scrapbook-cafe-brief.json
```

合同名：

```text
scrapbook-collage-v05
```

适合：

- 探店、好物、生活方式、旅行、小清单。
- 需要“收藏感”“种草感”的封面。

HTML 必须实现：

- 标题拆成 2-3 张纸条。
- 多张照片卡错位叠放。
- 至少 2 条胶带。
- 手绘虚线圈、箭头、短线。
- 小便签承载卖点。

图片通道负责：

- 店铺照片、物品照片、局部细节。

### 3. 产品截图主视觉

Brief:

```text
examples/xhs-v05/product-ai-brief.json
```

合同名：

```text
product-hero-v05
```

适合：

- 工具、软件、AI 工作流、网页产品、插件教程。
- 需要展示截图或产品界面的封面。

HTML 必须实现：

- 深色科技背景。
- 透视截图框。
- 标题压在截图框附近，不做普通顶部标题。
- 箭头指向截图关键区域。
- 底部小卡片承载步骤或结果。

图片通道负责：

- 真实产品截图。
- 软件界面、网页界面、工具结果图。

### 4. 前后对比封面

Brief:

```text
examples/xhs-v05/compare-fitness-brief.json
```

合同名：

```text
perspective-compare-v05
```

适合：

- 改造前后。
- 避坑前后。
- 方法论前后。
- 学习、健身、效率、设计优化对比。

HTML 必须实现：

- 黑橙或强对比分割背景。
- 大标题斜压进画面。
- 前景对比卡近大远小。
- 对比卡内出现“以前 / 现在”或“错误 / 正确”。
- 人物或场景只做第二视觉。

图片通道负责：

- 人物状态图。
- 场景图。
- 对比素材。

## 关键边界

HTML 层能稳定控制：

- 中文文字正确。
- 字号、层级、描边、阴影。
- 撕纸、胶带、箭头、星标、便签、对比卡。
- 构图和缩略图可读性。

HTML 层不能凭空产生：

- 真实人物。
- 真实照片。
- 真实产品截图。
- 真实食物。

因此，生产级工作流应该是：

```text
主题与文案 -> 选择视觉系统 -> 生成 brief -> 准备或生成主视觉图片 -> HTML 模板包装 -> Playwright 截图 -> QA
```

如果 image2.0 / qwen-image / zimage 直出的整图已经满足中文、构图和风格 QA，也可以直接采用整图；但默认发布路径仍应保留 HTML 文字层作为稳定方案。
