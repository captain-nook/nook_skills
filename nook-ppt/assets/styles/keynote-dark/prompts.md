# 发布会·暗场：出图提示词与颜色分工

出图用本地 ComfyUI 的 Qwen Image 2.1 加速通道：
`python scripts/comfy_image.py jobs_xxx.json --out raw`（也可以把 prompt 交给任意图像 API）。已有任务：`jobs_hero.json`（早期通用：玻璃球、方块、光带）、`jobs_meaning.json`（按内容意象重出的 10 张）、`jobs_hero.json`、`jobs_para.json`、`jobs_bento.json`（四张主体靠右的横幅）、`jobs_curve.json`（曲线、沙漏）。

## 提示词骨架
`A premium 3D render on a pure black background: <主体>, <材质与光>, fine film grain, soft reflections, deep black empty space around. Cinematic keynote product shot.`

- 背景一律写 pure black / near-black，图才能在深色页里融进去、在浅色页里变成深色圆角卡。
- 主体：磨砂玻璃、拉丝钛金属、玻璃环、发光沙漏这类"产品"质感；不要写人物、文字、界面。
- 想让主体靠右，要写 "the left two thirds of the frame is completely empty black, the subject sits in the right third"。
- 只写要什么，不写否定句（写了反而会被画出来）。

## 颜色分工（不要混）
- 底：纯黑（或浅色版的冷色渐变）。
- 卡面：中性石墨 / 中性白，不染色。
- 光：只出现在卡片下沿亮边、向下洒的投影、卡下很淡的光池里。默认冰白，蓝色版把光换成蓝并压弱。
- 强调色：一个蓝（深色 5AB0FF，浅色 0066CC）。
- **不使用紫色**。分类色需要多种时用 橙 / 蓝 / 绿 / 冰白。
- 图片里已有的颜色（橙色纸飞机、绿色叠片）可以保留，不要再让页面色光去呼应。

## 复用已有图
`raw/` 里的图可以直接复用：玻璃球（hero_orb）、方块（hero_para）、光带（hero_flow）、四个横幅（bento_*）、沙漏、三个正方形主体（tile_*）。色相偏移用 PIL 做，不占 GPU：见 `bento_r.png`（由紫色版 `bento_r_violet.png` 偏移为绿色）。

## 配图要有内容含义（261002 复核三份样片后写下）
抽象 3D 图好看，但必须对应这一页的意思。三份样片的意象：
- 费曼学习法：封面=玻璃对话气泡（讲给别人听）；"学会不等于讲得出来"=密封玻璃罐里困着一团光（知道，出不来）；"四步循环"=三个箭头首尾相追的玻璃环；"卡点"=拼图缺一块、缺口发光；收尾=对话气泡扩散的声波。
- PARA：封面=四个发光方块（四个抽屉）；"存得越多，找得越慢"=乱堆溢出的玻璃文件堆；四个抽屉=纸飞机（项目）、轨道环（领域）、玻璃叠片（资源）、钛金属盒（归档）；收尾=玻璃问号（先问有什么用）。
- 遗忘曲线：封面=衰减的光带；66%=沙漏；"合上书"=合上的玻璃书（书页边缘透光）；收尾=一次次被托起的锯齿光带（复习把曲线拉回来）。

经验：
- 暖色光要后处理成偏冷（罐里的暖白光用通道乘数调冷），否则和整套冷色调不一致。
- 抽象主体也会被裁掉或没画对（循环环被裁、书站着像一扇门）：多出两个候选、挑一个，描述里写"整体都在画面内""放平、倾斜一点"。
- 紫色一律用色相偏移改掉（PIL，不占 GPU）：`bento_r`、`hero_para` 的原图以 `_violet` 备份。
- 封面/章节底图在 `make_bg.py` 里按"主体中心"摆位：主体居中的图，用 `dx = 目标中心 - 主体中心` 计算偏移，别凭感觉。
