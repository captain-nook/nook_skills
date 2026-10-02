# 东方雅集：出图提示词与颜色分工

出图用本地 ComfyUI 的 Qwen Image 2.1 加速通道：`python scripts/comfy_image.py jobs_yaji.json --out raw`。任务有两批：`jobs_yaji.json`（通用山水花木：远山、明月松枝、竹、梅、鹤、松，可用于与自然、静、雅有关的内容）和 `jobs_yaji_meaning.json`（四象限样片的**内容意象**：日晷、案头卷轴、烽火台、磨刀、驿使快马、落叶随水、登高望远）。每个主体各有宣纸版 _l 和暗墨青版 _d。

## 提示词骨架
- 浅色（宣纸）：`A Chinese ink wash painting (shuimo) on warm off-white xuan rice paper with delicate paper fibers, soft grey-black ink, refined and minimal, generous empty paper. <主体>`
- 深色（暗墨青）：`A refined Chinese drawing in thin gold ink contour lines on a deep ink-green (dark teal-black) background with subtle paper grain, soft dark jade gradients, premium and minimal, generous empty dark space. <主体>`
- 想让主体靠右：`the left two thirds of the frame is completely empty, the subject sits in the right third.`
- 主体只写要什么（竹、梅枝、鹤、松、明月与松枝、层叠远山）。**不要在提示词里写"没有人物"之类的否定句**：实测写了反而容易出人；换一个更具体的正向主体（"一丛竹子加几块小石头"）并换种子。
- 图里不放文字和印章（文字会画错）；印章由代码画成原生形状。

## 颜色分工
- 浅色：底宣纸暖白 `F4EFE3`，字墨色 `26211C`，强调只用朱砂 `B23A2F`，细线与边用淡金 `B08D57`，次要字 `6A6157`。
- 深色：底暗墨青 `0E1A19`，字宣纸白 `EFE8D8`，强调淡金 `D9B873`，边与线金色低透明度。朱砂在暗底上对比度不够，只留给印章。
- 不用蓝色、紫色；一页最多一个强调色。

## 底图
`make_bg.py` 用代码生成宣纸（云纹加颗粒加纤维）和暗墨青底，封面、章节用出图结果放大。改纹理强度改 `noise()` 的第二个参数。

## 配图要有内容含义（重要）
261002 的第一版样片用松、竹、鹤、梅，风格很东方，但和"四象限时间管理"没有关系，被指出后全部重画。规则：**先为每一页想好意象，再出图**。
- 例：封面=日晷（时间）；"忙"=案头堆满的卷轴；重要且紧急=烽火台；重要不紧急=磨刀（磨刀不误砍柴工）；紧急不重要=驿使快马（可托人）；不紧急不重要=落叶随水（放手）；收尾=登高望远（先看重要的）。
- 通用山水花木的图保留在 raw/，只在内容本身与自然、静、雅有关时才用。
- 实测：写具体的朝代器物（"方形夯土烽燧，顶部有垛口"）才不会画成灯塔；金线暗色版容易自己长出人形或动物，遇到就换更具体的正向描述并换种子。
