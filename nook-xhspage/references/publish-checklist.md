# 发布前检查

1. 运行 `python xhs.py selftest`，全部通过。它已包含：skill 目录里没有本机路径和个人信息、字体许可文件在位、示例和素材库完整。
2. 示例图和截图：`assets/examples/`、`examples/inputs/` 里的图逐张看过，没有账号、邮箱、密钥、内部项目名。
3. 版权：字体（思源黑体、霞鹜文楷，OFL）的许可在 `assets/fonts/LICENSE-fonts.txt`；素材库全部是自生成，不含他人 Logo 和带字图；默认品牌的人物和 Logo 属于作者，发布时确认保留或换成中性示例；去 AI 味的规则参考 `nook-alive`，其来源标注见它的 ATTRIBUTION.md。
4. 依赖：`requirements.txt` 和 `setup.bat` 在干净机器上跑通；不需要 ComfyUI。
5. 体积：字体约 37MB，素材库几十 MB；`.gitignore` 里不放 `output/`。
6. 命名：与 `nook-xhsdesign` 的分工写清楚（它只出视觉方案和提示词，本 skill 渲染图）。
7. 版本号和 CHANGELOG 已更新。
