---
name: nook-search
description: AnySearch 之上的搜索大脑。当用户要"把一句模糊需求变成精准搜索并落库"、"让 AI 自己决定搜什么/走哪个域/采几条/存哪里"、"采集-清洗-入库自动跑通"，或上层 skill（选题/调研/竞品/写稿）需要"先搜再写"时使用。AnySearch 只负责按 query 去 17 个域取数并原样回传；本 skill 负责翻译意图、路由域、编排调用、清洗结果、落库。需登录的国内平台（小红书/抖音/B站）不在覆盖范围，请使用专门的国内平台采集工具。
---

# nook-search

把一句人话，翻译成 AnySearch 跑得对、跑得干净、能复用的搜索。AnySearch 是"手脚"（只会按 query 取数），本 skill 是"大脑"（翻译/路由/清洗/落库都在这层）。任何"想用 AnySearch"的请求都先过本 skill。

## 五环流水线

一次搜索 = 五环串行。跳环会漏数据。每一环的 schema 和细则在对应 reference 里。

1. **意图解释** → 把模糊需求压成结构化意图：目标、时间窗、是否有域、缺什么必填项。缺必填直接问（一次最多 3 问），不脑补。→ [01_意图解释](references/01_意图解释_澄清规则.md)
2. **参数路由** → 每条 query 定 domain / sub_domain / sdp / keyword，并写 `why`。见下方「路由」。→ [02_参数路由](references/02_参数路由_领域映射.md)
3. **采集编排** → 跑 CLI。多路优先 `batch_search`（≤5 路），有依赖的（先拿 URL 再 extract）串行。→ [03_采集编排](references/03_采集编排_命令组合.md)
4. **结果清洗** → 原始字段 → 可读 Markdown：去重、排序、字段映射。→ [04_结果清洗](references/04_结果清洗_排版规则.md)
5. **存储分发** → 落库。见下方「存储」。→ [05_存储分发](references/05_存储分发_路径契约.md)

## 路由：Path 1 / Path 2

官方 Decision Flow（CLI `doc` 命令原文，已核实）：

- **Path 2（垂直，默认）**：query 命中 17 域中任一域，就走这条。先 `get_sub_domains` 拿到 sub_domain 和必填参数，再 `search`。垂直结果远好于通用搜索。
- **Path 1（通用，罕见例外）**：仅限零域重叠的纯百科常识（"珠峰多高"）。不带 domain。
- **Hybrid（拿不准时）**：`batch_search` 里放 1 条 Path 1 + N 条 Path 2 并行。官方原话"Coverage beats guessing"。

域映射在 [assets/domain_map.yaml](assets/domain_map.yaml)。首次用某域必须先 `get_sub_domains`（官方硬要求），结果 session 内缓存、不重复调。

## 存储

**固定落 `<YOUR_VAULT_PATH>/anysearch库/`，扁平单文件，不建子文件夹**（`<YOUR_VAULT_PATH>` 替换成你自己的知识库根目录，覆盖此前的 cleaned/raw 双目录方案）。

- 文件名：`yymmdd_主题.md`，直接放在 `anysearch库/` 根目录下。
- **一轮搜索对话 = 一个文件**：不管这一轮里跑了几条 query、几次工具调用，产出的所有结果依次写进同一个 md 文件，不因为多条记录就拆成多个文件。
- 顶部 yaml 表头：采集日期 / 平台 / 关键字 / 域 / 子域 / 耗时 / 结果数。
- 路径模板与示例见 [05_存储分发](references/05_存储分发_路径契约.md)（已同步为扁平单文件方案）。

## 不变量

这些是本 skill 的底线，违反就退回重跑：

- **走五环，不裸调 CLI**。被判定驱动 nook-search 就跑满五环。用户"已经说清楚了"也不跳环 1（至少显式回填意图 schema）。纯调试 CLI 要先跟用户挑明"这是绕开 skill 的裸调用"，且不产出任何 skill 产物。封装性由此而来：上层 skill 只看到五环 schema，看不到 CLI 原文，CLI 改参数不影响上层。
- **真实调用，不编造**。每一步涉及 get_sub_domains / search / batch_search / extract 的，都必须是真实工具调用 + 真实返回。判据：对话记录里找得到这次调用和返回。找不到 = 没跑 = 伪造。绝不用文字"预演"冒充执行——曾发生过整个五环用文字编造域名/条数/耗时、最终什么都没落盘的空转，这条专门堵它。
- **命中域必落域**。query 命中某域却走 Path 1 泛搜索，是最常见的失效（尤其弱模型）。除了零域重叠的纯百科，都要落域。每条 query 的 `why` 写清域判断（命中哪个域 / 判定真无域），不写 = 没判断。
- **keyword 具体化**。禁用单泛词（`AI` / `新闻` / `教程`），用多词短语或专有名词（`AI large models` / `Musk`）。官方：keyword 优先级高于 query。
- **过程可见**。每跑一条 query，执行前后各一句进度给用户看（"正在 code 域检索：query=… → 拿到 8 条，2 条重复"）。日志文件是留痕，替代不了过程可见。
- **失败显性**。单条失败标 `partial` + 原因，整体失败标 `failed` + 摘要。绝不用空结果冒充成功。配额/限流错误（402/429）立即告警停手，读 `Retry-After` 退避。
- **时间窗显性处理**。识别到 72h/24h/本周等：时间词写进 query 自然语言；finance/academic 优先带 `year_from` 的域；有 `published_at` 就硬过滤，没有（如 social_media）标 `time_window_check: FAILED` 并保留全部；需严格过滤提示走 extract。禁止静默忽略。

## 边界

- 只管 AnySearch 这一条通道。国内需登录平台（小红书/抖音/B站等）不在覆盖范围，请另配专门的采集工具。
- 只搜、不写稿、不选题、不出图，搜完交上层 skill。
- 官方口径以 AnySearch CLI 自带的 `doc` 命令输出为准：**Path 2 是 DEFAULT，Path 1 是 RARE EXCEPTION**。
- 新规则只来自真实跑通 + 用户确认，不闭门造车。

## 被上层 skill 复用

nook-search 是可被其他 skill 嵌入调用的中间层：上层 skill 只需要调用五环 schema（意图 → 路由 → 编排 → 清洗 → 存储），不需要直接接触 AnySearch CLI。AnySearch 升级只改本 skill 内部的 `domain_map.yaml`，上层零感知。
