# 1 CHANGELOG

## 1.1 0.1-alpha（2026-10-16）
- 首次建立：手账内页 7 页、图示页 6 页、封面 3 张，浅色、深色两套；素材库 135 个；路径全部相对化。

## 1.2 0.1-alpha 续（2026-10-16）
- 新增命令行 xhs.py（list-types / list-assets / validate / preview / render）和 spec.py 校验；render.py 实现 19 个页型（含目录、金句、封底、封面三种）；示例 demo_paper / demo_dark / demo_more_dark / bad_plan。
- 迁入天蓝款 theme=sky：封面、内页、图示页共用手绘版式；示例 demo_paper_sky、demo_more_sky。
- 新增 lint.py（去 AI 味表面表达检查，接入 validate）、lint-text 命令、截图必须在 inputs/ 的检查；示例改用 examples/inputs/。
- 品牌设置改为第一次必须设置（brand.py、setup 命令、退出码 3），存用户目录；支持无人物、无 Logo；账号名可自定义。
- 去掉页码；新增船票画框（默认，可关）；主题色值重调和对比度自检 check-themes；渲染后留白检查；贴纸判断逻辑 decor.py 和 suggest-assets；meta.subject_terms 校验；主色橙调深以达对比度。
- 修正：船票改为独立风格 ticket；深色重做为三个版本（炭灰、淡墨蓝、暖夜纸），默认暖夜纸；品牌设置的“画框”改为“默认风格”。
- 去掉 sky 天蓝款，保留 paper、dark、ticket 三套；船票票根的 Logo 放在白色底板上，和票根蓝色拉开对比。
- 深色定为暖夜纸，去掉其余版本和 dark_variant 选项。

## 0.2（2026-10-17）
- 页型 19 到 22（时间轴、大数字、多截图）；素材库 135 到 161；本地界面；selftest；check-post 和 deliver；数字出处和夸大承诺提醒；贴纸压字检查；无人物版式；去掉早期演示代码；requirements 补 numpy。

## 0.3（2026-10-17）
- 来自 opencode + glm-5.3-flash 的真实试跑：事实核对改为强制（数字、日期必须在 meta.facts 里，禁用“真相”等定论词）；缺关卡文件时 render 拒绝；deliver 拒绝自带示例；出图默认写在方案所在文件夹，不再写进 skill 目录；stats 页版式改为数字在上标签在下，宽数字不再压字；SKILL.md 新增 1.5 硬规则（不许改 skill 文件、放不下只能缩短文字、汇报照实）；selftest 增加反例（38 项）。

## 0.4（2026-10-20）
- 新增通用款，任何人开箱即用：薄荷风格 mint（薄荷白底、墨绿蓝字、珊瑚红强调，封面和内页各一张插画底图）；虚拟 IP 人物「薄荷」三个姿态加圆形头像 Logo，素材在 `assets/brand/mint/` 和 `assets/themes/mint/`。
- `setup --default` 改为通用款（默认风格 mint，账号名可用 `--name` 改）；作者本人的船长款改为 `setup --captain`，旧配置里的 `mode=default` 仍按船长款读取，不受影响。
- 留白检查在底色是插画底图时，改为与底图逐像素比较；主题自检增加 mint；selftest 增加通用款素材和 demo_mint。
- 薄荷配色贴纸 49 个（`assets/library/mint/`，同 id，渲染时自动替换）；示例 demo_mint_reading.json（9 页，读书主题）和 docs/mint-showcase.jpg。
- 示例 demo_mint.json，docs 增加 demo-mint.jpg、mint-ip.jpg，styles-overview 增加薄荷一行。

