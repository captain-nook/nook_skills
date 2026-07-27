# nook-search

AnySearch 之上的搜索中间层：把一句人话，翻译成 AnySearch 跑得对、跑得干净、能复用的搜索。

## 这是什么

[AnySearch](https://github.com/anysearch-ai/anysearch-skill) 是一个面向 AI Agent 的搜索 CLI，覆盖 17 个垂直领域（社交平台、学术论文、金融数据、法律文书、代码库等），但它本身只负责"按参数取数"——不懂人话、不做清洗、不管落盘。

nook-search 是包在 AnySearch 外面的一层：

- **意图解释**：把模糊需求（"帮我查一下 XX 最近的动态"）压成结构化意图，缺关键信息就追问，不脑补。
- **参数路由**：判断该走哪个域、哪个子域、传什么参数，keyword 具体化，不用单个泛词。
- **采集编排**：调 AnySearch CLI，优先并行 batch_search，失败自动降级、不静默吞错。
- **结果清洗**：原始 JSON/Markdown → 统一的可读格式，去重、字段对齐、License 三色标注。
- **存储分发**：清洗后的结果落到本地 Markdown，一轮搜索对话一个文件，扁平不建子目录。

五环细则见 [SKILL.md](SKILL.md) 和 `references/` 下的各文档。

## 依赖：AnySearch（务必先部署这个）

nook-search **不包含**任何 AnySearch 的代码，只是调用它的 CLI。使用本 skill 前，你需要先独立部署 AnySearch。

- **项目地址**：https://github.com/anysearch-ai/anysearch-skill
- **License**：Apache License 2.0
- **一句话介绍**：统一的实时搜索引擎 skill，支持通用网页搜索、垂直领域搜索、并行批量搜索、网页内容提取。

### 部署方式（摘要，以官方 README 为准）

1. 从 [Releases](https://github.com/anysearch-ai/anysearch-skill/releases) 下载指定版本压缩包，或直接拉最新 main 分支。
2. 解压后把目录移动/重命名到你的 Agent 平台的 skill 目录，例如：
   - Claude Code：`~/.claude/skills/anysearch`
   - OpenCode：`~/.config/opencode/skills/anysearch`
   - Cursor / Windsurf：`<project>/.skills/anysearch`
3. 首次调用时按官方文档跑一遍运行时探测（Python / Node.js / Shell 三选一），把探测结果写进 `runtime.conf`，避免每次都重新探测。

完整步骤、平台适配细节、常见问题请直接看官方 README（[English](https://github.com/anysearch-ai/anysearch-skill/blob/main/README.md) / [简体中文](https://github.com/anysearch-ai/anysearch-skill/blob/main/README_zh.md)）——这里只摘要，不做二次搬运，避免和官方文档脱节。

### API Key 获取方式

AnySearch 支持匿名访问（速率限制较低），也支持注册 Key 提高限额：

1. 访问 https://anysearch.com/console/api-keys 免费注册一个 API Key。
2. 把 Key 写进 **AnySearch skill 自己目录下**的 `.env` 文件（不是本仓库的 `.env`）：
   ```
   ANYSEARCH_API_KEY=<your_api_key_here>
   ```
   参考本目录下的 [.env.example](.env.example)。
3. Key 的读取优先级：命令行 `--api_key` 参数 > `.env` 文件 > 系统环境变量 > 匿名访问。

**安全提醒**：不要把真实 API Key 提交进任何 git 仓库；`.env` 已经在仓库的 `.gitignore` 里被忽略。

## 安装 nook-search 本身

把 `nook-search/` 整个目录复制到你的 Agent 平台的 skill 目录下即可，例如 Claude Code：

```bash
git clone https://github.com/captain-nook/nook_skills.git
cp -r nook_skills/nook-search ~/.claude/skills/nook-search
```

确保同时已经部署好 AnySearch（见上一节），否则 nook-search 调不到底层搜索能力。

## 存储路径怎么改

本 skill 默认把采集结果存到 `<YOUR_VAULT_PATH>/anysearch库/`，扁平单文件、不建子目录。`<YOUR_VAULT_PATH>` 是占位符，用之前把 [SKILL.md](SKILL.md) 和 `references/05_存储分发_路径契约.md` 里所有 `<YOUR_VAULT_PATH>` 替换成你自己的知识库根目录（比如 Obsidian vault 路径）。

## 目录结构

```
nook-search/
├── SKILL.md                          # 入口：五环流水线总览
├── README.md                         # 本文件
├── .env.example                      # AnySearch API Key 配置示例（供参考，实际填在 AnySearch 目录下）
├── agents/openai.yaml                # Codex UI 识别用
├── assets/
│   ├── domain_map.yaml               # 目标类型 → AnySearch 域组合映射表
│   └── query_translation_patterns.yaml  # query 翻译模式库
└── references/
    ├── 00_双层架构说明.md            # 为什么要分两层
    ├── 01_意图解释_澄清规则.md       # 环 1：把人话变结构化意图
    ├── 02_参数路由_领域映射.md       # 环 2：domain/sub_domain/sdp/keyword
    ├── 03_采集编排_命令组合.md       # 环 3：CLI 调用编排
    ├── 04_结果清洗_排版规则.md       # 环 4：字段清洗、去重、模板
    └── 05_存储分发_路径契约.md       # 环 5：落盘规则
```

## 边界

- 只管 AnySearch 这一条通道，国内需登录平台（小红书/抖音/B站等）不在覆盖范围内。
- 只搜、不写稿、不选题、不出图，搜完交给上层工作流处理。
