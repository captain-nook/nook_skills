# Duotone Zine Component Registry

Use this registry only when the selected visual system is `duotone-zine` / 双色独立刊物风.

The executable authority is still `assets/schemas/deck-plan-v1.schema.json` and `scripts/plan_contract.py`. This file explains the approved components in human terms.

## 1. Visual Principle

双色独立刊物风 is a template system, not a mood prompt.

- Big words.
- Few words.
- Many images.
- Strong image hierarchy.
- Text inside deliberate containers.
- Paper/ink/duotone rhythm.
- Real screenshots for factual claims.

The Agent chooses components and fills slots. The renderer decides layout.

## 2. Approved Components And Variants

| Component | Chinese page form | Approved variants |
|---|---|---|
| `zine.hero-title` | 封面页 / 开场页 | `cover-left-type-right-image`, `cover-image-right`, `case-opener` |
| `zine.statement` | 一句话判断页 | `single-judgement`, `fragment-cards` |
| `zine.big-number` | 大数字页 | `three-column` |
| `zine.process-cards` | 流程页 | `four-step`, `three-deliverables`, `system-chain` |
| `zine.timeline` | 时间轴页 | `four-event`, `five-layer`, `cpr` |
| `zine.cycle` | 循环页 | `four-node`, `action-rhythm` |
| `zine.hierarchy` | 层级页 | `four-layer`, `skill-structure`, `five-layer-preview` |
| `zine.comparison` | 对比页 | `two-column`, `three-case-summary`, `template-vs-context`, `old-solutions`, `shell` |
| `zine.card-group` | 并列卡片页 | `parallel-three` |
| `zine.image-text` | 图文页 / 截图证据页 | `large-image-left`, `illustration-statement`, `screenshot-evidence`, `project-structure`, `project-root` |
| `zine.image-collage` | 图片拼贴页 | `three-image`, `evidence-triptych` |
| `zine.brand-master` | 品牌资产页 | `logo-ip-rules` |
| `zine.generated-asset` | 出图资产页 | `asset-spec` |

Do not use any component or variant outside this table.

## 3. Mapping Heuristics

Use these after the user confirms page forms:

1. 封面、章节开场、案例开场 -> `zine.hero-title`.
2. 强判断、转场、引导思考 -> `zine.statement`.
3. 三个数字、三个动作、三个结果 -> `zine.big-number`.
4. 方法、步骤、产出链路 -> `zine.process-cards`.
5. 历史、路线、阶段、层层展开 -> `zine.timeline`.
6. 反馈循环、重复工作节奏 -> `zine.cycle`.
7. 层级、系统结构、依赖关系 -> `zine.hierarchy`.
8. 新旧、前后、左右、多个方案比较 -> `zine.comparison`.
9. 三个平级观点且没有方向关系 -> `zine.card-group`.
10. 一个真实截图或主视觉承载重点 -> `zine.image-text`.
11. 三张图片共同证明一个链条 -> `zine.image-collage`.
12. Logo、IP、品牌规范 -> `zine.brand-master`.
13. 插图或图像生成要求 -> `zine.generated-asset`.

If no mapping fits, stop and report the missing component. Do not improvise.

## 4. Clean Slide Rule

Allowed on slide canvas:

- confirmed visible copy;
- approved image placeholders inside image slots;
- template-defined visual elements.

Forbidden on slide canvas:

- component IDs;
- slot IDs;
- file paths;
- build notes;
- construction warnings;
- "真实截图后补";
- "后续替换";
- "不伪造";
- "REAL SCREENSHOT ONLY".

Put build details in logs, not slides.
