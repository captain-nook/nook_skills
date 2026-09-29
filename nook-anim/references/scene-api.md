# 场景文件接口

每个故事写一个 `scene.py`，放在项目的工程目录里（素材在同目录的 `素材/`，路径写成相对 `scene.py` 的写法）。引擎负责逐帧输出、进度、时间映射、镜头号、配音轨、预览。

## 1 必须提供

```python
W, H, FPS, DUR = 1920, 1080, 24, 21.0
SHOTS = [(0, "S01 开场"), (3.0, "S02 画海"), ...]   # 镜头开始时间与名称，预览工作台据此出跳转按钮

def render(t):
    """返回第 t 秒（故事时间）的 BGR 画面，float 0–1 或 uint8。必须是 t 的纯函数。"""
```

## 2 建议提供

```python
def camera_matrix(t):
    """返回 (A, s)：场景坐标 → 屏幕的 2x3 矩阵与缩放。提供后预览工作台点击画面能取到场景坐标。"""
```

## 3 常用写法

```python
from nookanim import assets, core, draw, fx, geom, post

PLATE = assets.load(pathlib.Path(__file__).parent / "素材" / "desk.png")[:, :, :3]
CAM = geom.Camera((PLATE.shape[1], PLATE.shape[0]), (W, H))
PAGE = geom.Plane([(0, 330), (1440, 420), (1504, 835), (0, 760)], (1500, 500))   # 远左、远右、近右、近左
INK = draw.Marker(PAGE)

def camera_matrix(t):
    cx, cy, cw = core.keys(t, [(0, (1240, 640, 2250)), (3, (1240, 640, 2050))])
    return CAM.matrix(cx, cy, cw)

def render(t):
    A, s = camera_matrix(t)
    frame = CAM.render_plate(PLATE, A)
    cv = INK.begin()
    INK.line(cv, draw.partial(stroke, core.prog(t, 3.0, 4.6)), width=7)   # 逐笔画出
    frame = INK.composite(frame, A, cv)
    tq = core.q(t)                                                         # 角色按 12fps 定格
    anc, size = assets.bbox_anchor(BOY)
    frame = draw.shadow(frame, A, feet, 120)
    frame = draw.place(frame, A, BOY, anc, feet, 250 / size[1])
    frame = post.grain(post.vignette(frame), t)
    return post.fade(frame, t, DUR)
```

项目里场景多（例如一期视频配十几条 Broll 和标题）时，把共用的东西放到工程目录里的 `common.py`（色板、背景、卡片、角色、图标），每个场景文件 `from common import *`。引擎加载场景时会把场景所在的目录放进 `sys.path`，所以不用任何配置。样例见 `examples/tutorial_kit/`。

绘制顺序按离镜头远近：场景图 → 平面上的墨水 → 远处角色 → 近处物体 → 场景道具 → 特效 → 后期。

## 4 模块速查

| 模块 | 主要内容 |
|---|---|
| core | clamp、prog、lerp、ease 系列、spring、q（定格量化）、keys（关键帧）、warp_fn |
| geom | Plane（to_scene / from_scene / screen_h）、Camera（matrix / render_plate）、shake |
| assets | load、bbox_anchor、align、depth_variant、star_sprite、symbol_sprite、placeholder |
| draw | over、multiply、place、sprite_point、shadow、screen_lines、fill_poly、Marker、partial |
| fx | pop、speed_lines、drops、spiral、wind_lines、handwriting（支持同行混排字体）、flag |
| sketch | 手绘线稿：paper 纸纹、boil、resample、wobble、circle、Layer（stroke / fill / dot / ink / paint） |
| collage | 撕纸拼贴：Stage（设计空间摄像机）、sprite_matrix、cutout（带投影贴纸片、可加遮罩）、slap、jitter、torn_hole、bits |
| wash | 水墨水彩：xuan_paper 生宣纸纹、ink_diffusion_mask、water_ripples、InkCanvas |
| stick | 火柴人：Rig、fk、pose_keys / lerp_pose、walk、ik2 / reach、face、figure、Cam 与 line / poly / fill / disc |
| mg | 扁平动态图形：Beat、hexc、text、paste、pop / out、wipe、arc、count、rrect |
| post | vignette、grain、fade、label、to_uint8 |
| config | 机器相关设置（ComfyUI 地址、字体、ffmpeg、音乐工作流），全部可用环境变量覆盖 |
| audio | tone、sweep、noise、shaped、boing、ding、midi、Mixer、read_wav、write_wav、final_mix |
| music | analyze、cut_with_ending、snap_warp（命令行） |
| comfy | image / music 命令行 |
| render | stills / video / sheet 命令行 |
| preview | 预览工作台 |

完整样例：`examples/02_draw_direction/scene.py`（手绘线稿，完全基于引擎写成，推荐照它起步）；`examples/05_last_pizza/`、`examples/06_cat_day/`（纯代码，带音效脚本）。
