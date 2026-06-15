# nook-image2-gpt 调用契约

本文件给上层生产级 skill 使用。`nook-image2-gpt` 是原子出图能力，只负责把提示词或源图提交给 MCP，并返回本地图片路径。

## 边界

上层 skill 负责：

- 判断是否需要出图。
- 构造提示词。
- 管理源图、参考图、输出图的项目归档位置。
- 记录用途、prompt、来源、授权和后续裁切要求。
- 决定是否重试、换模型、换尺寸或降级。

`nook-image2-gpt` 负责：

- 通过 `submit_image_task` 提交文生图或图生图任务。
- 通过 `get_image_result` 查询任务状态。
- 把成功返回的图片保存到本地。
- 返回稳定的 `image_path` / `image_paths`。

## 标准调用流程

```text
1. 调 submit_image_task
2. 保存 task_id 到上层任务记录
3. 每 10-15 秒调 get_image_result
4. status = succeeded：读取 image_paths
5. status = failed：读取 error，决定是否重试
6. status = not_found：提示 MCP server 可能重启或 output/.tasks 丢失
```

## 文生图参数

```json
{
  "prompt": "short, concrete image prompt",
  "mode": "text_to_image",
  "size": "1024x1024",
  "n": 1
}
```

## 图生图参数

```json
{
  "prompt": "edit instruction or visual direction",
  "mode": "image_to_image",
  "input_image_path": "absolute/path/to/source.png",
  "size": "1024x1024",
  "n": 1
}
```

## 上层 skill 必须记录

每次真实出图后，上层项目应保存一条记录：

```yaml
image_provider: nook-image2-gpt
task_id:
mode:
prompt:
size:
source_image:
output_images:
created:
purpose:
status:
error:
```

## 对大 skill 的建议

- 不要让出图模型直接生成带文字的最终卡片、PPT 页或海报。
- 用它生成素材、底图、主体图、氛围图，再由上层确定性系统排版。
- 默认 `n: 1`，生产链路要稳定优先，不要为了抽卡一次生成太多。
- 上层 skill 应该把最终可用图片搬进自己的 `assets/` 或项目输出目录，不要长期依赖 MCP 的临时输出目录。
