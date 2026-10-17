# 素材库

透明底 PNG 贴纸（161 个），512×512，风格统一：白色模切边、藏青线稿、橙黄奶油加浅蓝填充。分五类：object 物件、character 涂鸦小人、symbol 符号、nature 自然装饰、tool 工具图标。`manifest.json` 是索引（id、文件、中文名、分类、标签）。agent 只按 id 引用，不直接写文件路径。

线条类（箭头、红框、红圈、波浪线、勾、叉、毛笔衬底）不在库里，由引擎用代码画。库里不含任何品牌 Logo 和带文字的图。

生成方式：条目清单和提示词在 `scripts/lib_items.py`，本机 ComfyUI（Qwen Image 2.1，透明 PNG）出图，每条出 1 到 2 个候选，人工挑选。没有 ComfyUI 的使用者直接用本库。追加素材时按同样的提示词前缀，并把条目写进 manifest。
