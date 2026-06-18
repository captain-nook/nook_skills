# 部署和使用说明

本文件面向 Codex、Claude Code、Cursor、Zcode 等 AI 编程助手。用户把仓库交给助手后，助手应先阅读 `SKILL.md`，再按本说明部署。

## 1. 安装

把 `nook-cover` 放到本机 skills 目录或当前工作目录下。

```bash
git clone <repo-url>
cd nook-cover
npm install
npx playwright install chromium
npx playwright install chromium-headless-shell
```

如果 Windows 下 npm cache 权限报错，可以改用项目内 cache：

```bash
npm install --cache ./.npm-cache
```

如果 Playwright 浏览器下载很慢，也可以让助手使用本机已有 Chrome / Chromium：

```bash
PLAYWRIGHT_CHROMIUM_EXECUTABLE=/path/to/chrome node scripts/render-xhs-cover.cjs examples/N1-prompt-pack/brief.json output/test
```

Windows PowerShell 示例：

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE="C:\Path\To\chrome.exe"
node scripts/render-xhs-cover.cjs examples/N1-prompt-pack/brief.json output/test
```

如果渲染时报 `chromium_headless_shell` 不存在，优先运行：

```bash
npx playwright install chromium-headless-shell
```

如果当前环境没有 Node 依赖，先按助手所在环境安装 Node.js。不要把 API key 写入文档或提交到 Git。

## 2. 可选配置

如果只使用 Codex Desktop 内置 image2.0，可以不配置外部 key。

如果在 ZCode、Claude Code、Cursor 或普通命令行中使用，通常没有 Codex Desktop 内置 image2.0。此时想得到真人、产品、场景主视觉，必须配置至少一个外部原子出图工具，或让用户提供素材。否则只能生成 HTML / Playwright 文字排版证明。

如果要接入三套原子出图工具，运行：

```bash
node scripts/setup-provider.cjs
```

该脚本会自动寻找同级目录中的：

```text
nook-zimage
nook-qwen-image
nook-image2-gpt
```

并写入本 skill 的 `.env`：

```text
NOOK_COVER_OUTPUT_DIR=./output
NOOK_COVER_DEFAULT_PROVIDER=none
NOOK_ZIMAGE_PATH=
NOOK_QWEN_IMAGE_PATH=
NOOK_IMAGE2_GPT_PATH=
```

这个 `.env` 只是路由表，不保存出图 API key。

各原子工具自己的 API key / base URL 放在各自工具目录的 `.env` 中：

- `nook-zimage`：低成本草图、亚洲人物、背景探索。
- `nook-qwen-image`：中文海报、中文视觉、中文文字参与画面的候选。
- `nook-image2-gpt`：高质量主视觉、图生图、参考图保持。

如果脚本找到这些工具，会询问是否继续运行各自的 `setup.js`。用户也可以手动进入对应目录运行：

```bash
node setup.js
```

原子工具负责提示用户输入自己的 key/url，例如：

```text
MS_API_KEY
MS_API_BASE_URL
IMAGE_API_KEY
IMAGE_API_BASE_URL
```

这些敏感字段不要写进 `nook-cover` 文档，也不要提交到 Git。

## 3. 使用

用户可以直接对助手说：

```text
用 nook-cover 做一张小红书封面。
主题：普通人做封面别再瞎搞。
优先 image2.0 直出，如果中文不准，再用 HTML / 后处理复刻标题层。
输出到我指定的文件夹。
```

如果助手回复“当前运行时没有内置 image2.0”，这是正常情况。此时有三种选择：

```text
1. 配置 nook-zimage / nook-qwen-image / nook-image2-gpt。
2. 提供一张人物、产品、截图或背景素材，让 nook-cover 负责文字层和排版。
3. 只跑 HTML / Playwright 排版证明，用来验证中文、层级和构图。
```

助手执行时要完成：

```text
主题
→ brief
→ 选择视觉系统
→ 选择出图路线
→ 生成封面候选
→ QA
→ 必要时 HTML / 后处理稳定标题层
→ PNG 输出
```

## 4. 发布前检查

发布前必须确认：

- 没有提交 `.env`。
- 没有提交真实 API key、base URL、token。
- 过程图片、失败图、录屏素材留在 `process/`，不要进入发布目录。
- `README.md`、`SKILL.md`、`references/`、`scripts/`、`.env.example` 都随包发布。
