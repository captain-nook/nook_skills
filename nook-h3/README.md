# nook-h3

一个面向 MiniMax H3 + ComfyUI 的可复用视频生成 Skill。

它负责把“分镜表或任务清单”转换成可执行的视频生成任务：选择 H3 工作流、组织官方格式提示词、挂载首帧/尾帧/参考图、提交 UTF-8 API 请求、逐条监听任务、输出技术证据、逐镜质检、失败重试、保存状态并支持断点续跑。

它不包含 ComfyUI、H3 模型权重、私有素材、账号凭证或任何特定项目的分镜内容。

![H3 scene reference example](assets/readme/h3-scene-street.png)

![H3 scene reference example: shop](assets/readme/h3-scene-tea-shop.png)

![H3 character reference example](assets/readme/h3-hero-multiview.png)

上面的图片只是 README 的视觉示意。实际使用时，应替换成当前项目自己的场景图、人物设定图和分镜物料。

## 目录

- [它解决什么问题](#它解决什么问题)
- [工作方式](#工作方式)
- [目录结构](#目录结构)
- [安装与依赖](#安装与依赖)
- [任务清单](#任务清单)
- [工作流模式](#工作流模式)
- [提示词要求](#提示词要求)
- [单条生成](#单条生成)
- [批量生成](#批量生成)
- [3条、7条、100条应该怎么做](#3条7条100条应该怎么做)
- [断点续跑与失败处理](#断点续跑与失败处理)
- [分享给别人](#分享给别人)
- [常见问题](#常见问题)
- [隐私与边界](#隐私与边界)

## 它解决什么问题

直接在 ComfyUI 中手动反复填写提示词、替换图片、调整时长，再等待视频完成，容易出现以下问题：

- 中文提示词通过 API 传输时编码损坏；
- 首帧、尾帧和参考图挂错工作流；
- 还没生成完成就提交下一条任务，导致队列失控；
- 推理成功就被误当成可用成片，台词、肢体、构图、运镜、云层和环境声没有经过质检；
- 生成失败后不知道从哪里继续；
- 同一个角色在不同镜头里误用了上一条生成结果；
- 3条和100条任务需要不同脚本，无法复用；
- 把一次性项目路径和素材名误写进通用工具，无法分享。

`nook-h3` 把这些变化放入外部任务清单，把执行逻辑固定在脚本里。任务数量、提示词、时长、工作流和素材仍然由使用者控制。

## 工作方式

```text
分镜表 / 任务清单
        │
        ▼
  h3_tasks.json
        │
        ▼
  nook-h3 执行器
        │ 选择模式、挂载物料、设置画幅/精度/时长
        ▼
  ComfyUI /prompt
        │
        ▼
  ComfyUI /history/{prompt_id}
        │ 轮询推理结果并记录输出
        ▼
  技术报告 + 接触表 + 语义质检
        │ 合格进入下一条；不合格换种子并按失败项重跑
        ▼
  可用视频片段 + 状态文件 + 日志
```

一个 `task` 是一段 H3 视频素材，不等同于最终剪辑后的整条视频。最终视频可以由多个 task 组成。

执行器始终遵循：

1. 读取任务清单；
2. 校验任务字段和工作流；
3. 提交一条任务；
4. 轮询该任务直到成功或失败；
5. 保存 prompt ID、输出文件和状态；
6. 生成技术报告与接触表，按分镜检查主体、构图、运镜、环境运动、台词和声音；
7. 合格后才进入下一条；不合格则更换种子并按失败项重跑。

## 目录结构

```text
nook-h3/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── h3-prompt-contract.md
│   ├── manifest-schema.md
│   ├── quality-control.md
│   └── workflow-and-assets.md
├── scripts/
│   ├── prepare_h3_qc.py
│   ├── check_h3_dialogue.ps1
│   ├── set_h3_qc_result.ps1
│   ├── run_h3_batch.ps1
│   ├── test_h3_prompt.ps1
│   └── submit_h3_workflow.ps1
└── assets/
    └── readme/
        └── h3-scene-street.png
```

其中：

- `SKILL.md`：给 Agent 读取的执行规则；
- `README.md`：给人阅读的安装、配置和使用说明；
- `references/`：H3 提示词、任务清单和工作流配置说明；
- `scripts/submit_h3_workflow.ps1`：提交并可选等待一条任务；
- `scripts/run_h3_batch.ps1`：按照清单顺序逐条生成，并在每条输出后强制暂停质检；
- `scripts/test_h3_prompt.ps1`：在提交前检查官方字段顺序、精确台词标签、无 BGM 设置和可选的镜头级规则；
- `scripts/prepare_h3_qc.py`：生成技术报告和接触表，供 Agent 做逐镜语义质检；
- `scripts/check_h3_dialogue.ps1`：使用 Windows 离线中文识别器核对预期台词，输出匹配与置信度证据；
- `scripts/set_h3_qc_result.ps1`：记录通过、立即重试、返工或人工复核，并解除或保留队列闸门；
- `assets/readme/`：只用于仓库 README 的展示图，不参与视频生成。

## 安装与依赖

### 必需环境

- Windows PowerShell；
- 已安装并可运行的 ComfyUI；
- ComfyUI 中可用的 MiniMax H3 自定义节点；
- 与当前节点版本匹配的 H3 工作流 JSON；
- 本地安装的官方 `h3-prompt-writing` Skill；
- Codex 或其他能够读取 `SKILL.md` 的 Agent 环境。

默认 API 地址为：

```text
http://127.0.0.1:8188
```

如使用其他地址，在任务清单的 `defaults.comfy_url` 中覆盖。

### 安装 Skill

把整个 `nook-h3` 文件夹复制到以下任一位置：

```text
~/.codex/skills/nook-h3
```

或者项目级目录：

```text
<your-project>/.agents/skills/nook-h3
```

不要只复制 `SKILL.md`，否则脚本和参考规范会缺失。

## 任务清单

批量执行器读取一个 JSON 文件，默认文件名可以是 `h3_tasks.json`。完整字段说明见 [references/manifest-schema.md](references/manifest-schema.md)。

最小示例：

```json
{
  "defaults": {
    "comfy_url": "http://127.0.0.1:8188",
    "workspace": ".",
    "i2v_workflow": "workflow-i2v.json",
    "ref2v_workflow": "workflow-ref2va.json",
    "t2v_workflow": "workflow-t2va.json",
    "megapixels": 0.9,
    "duration": 4,
    "poll_seconds": 30,
    "max_retries": 3
  },
  "tasks": [
    {
      "id": "clip-001",
      "video_id": "video-a",
      "sequence": 1,
      "mode": "I2VA",
      "prompt": "integrated_multimodal_description: ...\noverall_soundscape: ...\nnon_diegetic_music: N/A",
      "first_frame": "first_frame_001.png",
      "output_prefix": "video-a/clip-001"
    },
    {
      "id": "clip-002",
      "video_id": "video-a",
      "sequence": 2,
      "mode": "Ref2VA",
      "prompt": "subject_definitions: ...\nsummary: ...\nretention_analysis: ...\ndetailed_description: ...\noverall_soundscape: ...\nnon_diegetic_music: N/A",
      "references": ["character_sheet.png", "scene_002.png"],
      "output_prefix": "video-a/clip-002",
      "duration": 5
    }
  ]
}
```

### 必填字段

每个任务必须有：

- 唯一的 `id`；
- `mode`；
- 按官方规范写成的 `prompt`；
- 唯一的 `output_prefix`。

模式对应的物料：

| 模式 | 必需物料 | 使用含义 |
|---|---|---|
| `I2VA` | `first_frame` | 图片是视频的具体首帧。 |
| `FL2VA` | `first_frame`、`last_frame` | 图片分别锚定首帧和尾帧，中间保持连续运动。 |
| `L2VA` | `last_frame` | 图片是目标尾帧，开场由模型推断；必须使用支持尾帧输入的工作流。 |
| `Ref2VA` | `references` 至少两张 | 图片是角色、场景、道具或关系参考，不必成为严格首帧。 |
| `T2VA` | 无图片字段 | 完全依据文字生成，只有在确实没有可用图片时使用。 |

`video_id`、`scene_id`、`sequence` 是可选的组织信息。它们帮助管理多条成片，不改变生成逻辑。实际执行顺序以 `tasks` 数组顺序为准。

## 工作流模式

### I2VA

适合已经确定画面起点的镜头，例如人物已经站在画面中、环境构图已经固定。执行器会把 `first_frame` 接到首帧节点，并设置提示词、时长、画幅和输出前缀。

### FL2VA

适合需要明确“从哪里开始、到哪里结束”的连续运动。不要在提示词里加入与首尾图不一致的突然切换。

### L2VA

适合只确定结束状态的镜头。必须确认工作流真的支持 `last_frame` 输入，不能把普通 I2VA 工作流直接当作 L2VA 使用。

### Ref2VA

适合角色一致性、场景关系、道具关系和多元素参考。参考图应在任务中明确列出，角色身份表应保持稳定，不要把上一条生成的视频截图偷偷当作人物身份源。

### T2VA

适合没有可用图像物料的文字生视频。只要已有可靠的首帧、尾帧或参考图，优先使用对应的图像工作流。

工作流里的节点 ID 属于具体 JSON 模板，不属于 H3 的固定标准。模板改动后，应在 `defaults.node_map` 或任务级 `node_map` 中重新配置。

## 提示词要求

执行前应读取官方 `h3-prompt-writing` Skill，再根据模式读取官方 base 或 reference 指南。`references/h3-prompt-contract.md` 只是本 Skill 的简要提醒，不能替代官方规范。

基本要求：

- 基础模式按官方顺序使用 `integrated_multimodal_description`、`overall_soundscape`、`non_diegetic_music`；
- Ref2VA 按官方顺序使用六个 section；
- 对白保持原语言，不要把中文台词翻译成英文；
- 台词必须放在时间线中，并明确说话者；
- `overall_soundscape` 描述环境音和动作拟音，不要把环境音漏掉；
- 走路要写脚步声，热闹场景要写人声、摊位声、风声等现场声音；
- 如果后期单独剪 BGM，`non_diegetic_music` 使用 `N/A`；
- 需要云、雾、烟、雨、光尘等动态氛围时，必须描述运动、层次和不能遮挡的主体；
- 提示词中的时长必须和任务的 `duration` 一致；
- 场景参考图只承担场景职责，人物参考图只在需要人物一致性时加入。

批处理还会在提交前运行机械预检。任务可通过 `prompt_checks.expected_dialogue` 要求精确中文台词，通过 `prompt_checks.calm_cloud_sea` 拦截灾难式云海词汇并要求稳定轮廓与轻微横向纹理漂移，通过 `prompt_checks.opening_subject_required` 拦截主体从画外迟入场。预检失败时不会占用 ComfyUI 队列。

## 单条生成

先准备好 ComfyUI 工作流和输入图片，然后运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\submit_h3_workflow.ps1 `
  -Mode Ref2VA `
  -Workspace '.\video-project' `
  -WorkflowPath '.\video-project\workflow-ref2va.json' `
  -Prompt $prompt `
  -ReferenceImages @('character_sheet.png','scene_001.png') `
  -OutputPrefix 'video-a/clip-001' `
  -Megapixels 0.9 `
  -Duration 4 `
  -Wait
```

如果只想提交、不等待，可以去掉 `-Wait`。生产时建议保留等待，确认本条任务完成后再进入下一条。

单条提交也会自动运行提示词预检。镜头有精确中文台词时传入 `-ExpectedDialogue`；要求平静仙界云海时传入 `-CalmCloudSea`；开场主体必须已经在画内时传入 `-OpeningSubjectRequired`。不合格的提示词会在进入 ComfyUI 队列前停止。

脚本使用 UTF-8 `WebClient.UploadData` 提交 JSON，专门避免中文提示词通过 PowerShell 请求体传输时变成问号。

## 批量生成

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_h3_batch.ps1 `
  -ManifestPath .\h3_tasks.json
```

批量脚本会：

1. 检查任务 ID 是否为空或重复；
2. 检查 ComfyUI 的 `/system_stats`；
3. 校验官方提示词结构以及该镜头的 `prompt_checks`；
4. 根据任务模式加载对应工作流；
5. 注入首帧、尾帧、参考图、提示词、时长、精度和输出前缀；
6. 提交一条任务并监听历史记录；
7. 推理成功后写入 `awaiting_qc` 并强制暂停，不提交下一条；
8. 生成技术报告与接触表，再按分镜做语义质检；
9. 合格后写入 `completed`；不合格时更换种子、修订失败项并重跑；
10. 重启后根据状态文件继续，不越过尚未质检的任务。

默认会在 manifest 所在目录生成：

```text
.h3-batch-state.json
h3-batch.log
```

这两个文件包含运行状态和本地输出信息，通常不应该提交到公开仓库。

完成技术与语义质检后，用状态脚本记录结果：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\set_h3_qc_result.ps1 `
  -StatePath .\.h3-batch-state.json `
  -TaskId 'clip-001' `
  -Result retry `
  -FailureReasons @('cloud_wave_motion','subject_late_entry') `
  -PromptRevision 'stable cloud contour; subject fully composed in first frame' `
  -ManifestPath .\h3_tasks.json `
  -RevisedPrompt $revisedPrompt
```

`pass` 会写入 `completed`；`retry` 会解除当前闸门，并在下次运行时自动递增尝试次数、随机种子和输出前缀；提供 `ManifestPath` 与完整 `RevisedPrompt` 时，修订后的官方提示词会同时写回对应任务；`rework` 进入返工队列；`manual` 标记人工复核。

## 3条、7条、100条应该怎么做

不需要修改脚本。

### 只有一条视频素材

在 `tasks` 里写入 3 个、7 个或 100 个任务对象即可：

```text
h3_tasks.json
└── tasks
    ├── clip-001
    ├── clip-002
    ├── ...
    └── clip-100
```

### 多条最终成片

推荐两种方式：

**方式 A：每条最终视频使用一个 manifest。**

适合需要分别重跑、分别归档的项目：

```text
video-a/h3_tasks.json
video-b/h3_tasks.json
video-c/h3_tasks.json
```

**方式 B：一个总 manifest。**

把所有片段放进一个 `tasks` 数组，用 `video_id` 区分属于哪条成片，并在 `output_prefix` 中包含视频 ID：

```text
video-a/clip-001
video-a/clip-002
video-b/clip-001
video-c/clip-001
```

如果是 100 条最终视频，仍然只是 100 个 manifest，或者一个包含所有片段的总 manifest。执行器不关心数量，只关心任务清单和顺序。

## 断点续跑与失败处理

状态文件中的 `completed` 记录包含任务状态、ComfyUI prompt ID、输出文件和完成时间。重新运行同一个 manifest 时，已完成任务会被跳过。

如果在 `defaults.output_dir` 中配置了输出目录，执行器还会按照 `output_prefix` 检查已有输出。建议每个任务使用唯一前缀，避免把别的任务误判为已完成。

ComfyUI 推理成功不等于镜头合格。每条输出都会停在 `awaiting_qc`；只有技术质检和语义质检均通过才写入 `completed`。台词错误、主体迟入画、肢体异常、固定机位、远景云层静止、云层海浪化或现场声音缺失，都应记录失败原因并使用新种子重跑。达到即时重试上限后移入 `rework_pending`，不要把失败素材冒充成片。

## 分享给别人

分享时至少需要说明四层内容：

1. **Skill**：整个 `nook-h3` 文件夹；
2. **官方规则**：官方 `h3-prompt-writing` Skill；
3. **运行环境**：ComfyUI、H3 自定义节点、工作流 JSON；
4. **项目数据**：对方自己的 manifest、输入图片和输出目录。

只分享 `nook-h3` 而不提供工作流和输入图片，对方可以读懂和复用执行逻辑，但不能直接生成与你相同的素材。

建议不要把以下内容放入公开仓库：

- 真实的个人绝对路径；
- API key、token、账号信息；
- 模型权重；
- 不准备公开的人物照片和项目素材；
- 运行日志、prompt ID 和本地输出记录。

## 常见问题

### ComfyUI 能打开，但批量脚本提示 preflight failed

确认 ComfyUI 实际监听地址、端口和防火墙状态。默认地址是 `http://127.0.0.1:8188`，可以在 manifest 的 `defaults.comfy_url` 中修改。

### 中文台词变成问号或乱码

确认使用本 Skill 自带的提交脚本，并保持 JSON、manifest 和提示词文件为 UTF-8。不要把中文提示词改成系统默认编码后再通过 API 发送。

### 参考图找不到

`first_frame`、`last_frame` 和 `references` 使用的是 ComfyUI 输入目录里可见的文件名，不是发送者电脑上的绝对路径。先把图片放到对方 ComfyUI 的 input 目录，再把 manifest 改成对应别名。

### 工作流节点 ID 不匹配

节点 ID 由 JSON 模板决定。打开实际工作流，确认首帧、尾帧、参考图、提示词、时长、分辨率和 SaveVideo 节点，再通过 `node_map` 覆盖默认值。

### 是否可以同时开多个批量执行器

不建议对同一个 ComfyUI 队列同时启动多个 runner。默认设计是单条提交、单条监听、成功后继续，以保证顺序和日志可追踪。

## 隐私与边界

`nook-h3` 只负责本地任务编排，不会自动把素材上传到第三方服务，也不会替用户生成、保存或传播 API 密钥。实际生成结果仍由 ComfyUI、模型、显卡、输入素材和提示词共同决定。

如果要把本 Skill 发布到公开仓库，请先确认 README 展示图、工作流模板和输入素材都可以公开。仓库里的示意图只用于说明工作流，不代表任何项目的固定视觉设定。

## 版本与来源

- Skill 名称：`nook-h3`
- 适用：MiniMax H3 + ComfyUI 本地视频生成
- 发布仓库：<https://github.com/captain-nook/nook_skills>
- 本 README 只描述可迁移的执行方式，不绑定某个项目、镜头数量或电脑路径。
