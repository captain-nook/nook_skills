"""生成发布会·暗场用到的底图。python make_bg.py
  bg_dark_black   内容页深色底（纯黑加颗粒）
  bg_mesh_cool    内容页浅色底（冷色弥散渐变，蓝青，无紫）
  bg_cover_*      封面：把 raw/ 里的主体图按"主体中心"摆到右侧（cubes 方块、curve 曲线、voice 对话气泡）
  bg_section_*    章节/收尾：q 问号、saw 锯齿光带、voice 声波，左侧压暗留给文字
改封面或章节底图：在 raw/ 里换图，再按主体中心调整 dx（dx = 目标中心 - 主体中心）。
"""
import pathlib

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).parent
W, H = 1920, 1080
rng = np.random.default_rng(7)
sc = H / 864


def grain(a, amt=1.6):
    return np.clip(a + rng.normal(0, amt, a.shape), 0, 255)


def save(a, name):
    Image.fromarray(grain(a).astype("uint8")).save(HERE / name)


def place(src, dx, dy, scale):
    """把 raw/ 里的图缩放后放到 1920×1080 的近黑画布上，左上角在 (dx, dy)。"""
    im = Image.open(HERE / "raw" / src).convert("RGB")
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    c = np.zeros((H, W, 3)) + 3
    x0, y0 = dx, dy
    c[max(0, y0):max(0, y0) + min(im.height, H - max(0, y0)), max(0, x0):max(0, x0) + min(im.width, W - max(0, x0))] = \
        np.asarray(im)[: min(im.height, H - max(0, y0)), : min(im.width, W - max(0, x0))]
    return c


def fade_full(src, dst, k=0.25):
    a = np.asarray(Image.open(HERE / "raw" / src).convert("RGB").resize((W, H), Image.LANCZOS), float)
    save(a * np.linspace(k, 1.0, W)[None, :, None], dst)


def mesh(base, blobs, name):
    a = np.zeros((H, W, 3)) + np.array(base, float)
    yy, xx = np.mgrid[0:H, 0:W]
    for (cx, cy, r, col, k) in blobs:
        w = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)) * 1.6)[..., None]
        a = a * (1 - w * k) + np.array(col, float) * (w * k)
    save(np.clip(a, 0, 255), name)


save(np.zeros((H, W, 3)) + np.array([4, 4, 6], float), "bg_dark_black.png")
mesh((246, 249, 253), [(260, 160, 760, (150, 192, 255), 0.70), (1560, 220, 700, (160, 215, 255), 0.60), (1100, 1050, 820, (150, 228, 255), 0.55)], "bg_mesh_cool.png")
save(place("hero_para.png", int(0.74 * W - 1536 * sc * 1.28 * 0.5), int(-H * 0.18), sc * 1.28), "bg_cover_cubes.png")   # 四个发光方块
save(place("hero_curve.png", int(W * 0.34), 0, sc), "bg_cover_curve.png")                                          # 衰减曲线
save(place("hero_voice.png", int(W * 0.115), 0, sc), "bg_cover_voice.png")                                         # 玻璃对话气泡
fade_full("hero_voice_end.png", "bg_section_voice.png")                                                            # 声波
fade_full("hero_question.png", "bg_section_q.png")                                                                 # 问号
save(place("hero_sawtooth.png", int(W * 0.36), 0, sc), "bg_section_saw.png")                                       # 锯齿光带
print("ok")
