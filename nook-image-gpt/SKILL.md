# nook-image-gpt

GPT Image 2.0 生图 MCP 工具。MCP Server 代码位于 **nook_mcp** 仓库。

详见：https://github.com/captain-nook/nook_mcp/tree/main/nook-image-gpt

## Tool

> 注：该 relay 中转仅支持文字生图，不支持图生图。

| 参数 | 必填 | 说明 |
|------|------|------|
| prompt | 是 | 生图提示词 |
| size | 否 | 分辨率，默认 `1024x1024` |
| n | 否 | 生成数量，默认 1 |
| save_to_dir | 否 | 保存目录路径，不设则返回 base64 |

## 触发

| 场景 | tool |
|------|------|
| GPT Image 2.0 中转 | `generate_image` |
