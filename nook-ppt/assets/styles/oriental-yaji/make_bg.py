"""生成东方雅集底图：bg_paper（宣纸）、bg_ink（暗墨青）、bg_cover_*（封面：日晷）、bg_end_*（收尾：登高望远）、bg_mist_*（通用远山，内容与山水有关时用）。python make_bg.py"""
import pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = pathlib.Path(__file__).parent
W, H = 1920, 1080
rng = np.random.default_rng(11)


def noise(sigma, amp):
    n = rng.normal(0, 1, (H, W))
    img = Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(sigma))
    a = np.asarray(img, float)
    return (a - a.mean()) / (a.std() + 1e-6) * amp


def fibers(color, alpha, count):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(count):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        L, ang = rng.uniform(20, 90), rng.uniform(0, np.pi)
        d.line((x, y, x + L * np.cos(ang), y + L * np.sin(ang)), fill=color + (int(alpha * rng.uniform(0.4, 1)),), width=1)
    return np.asarray(im.filter(ImageFilter.GaussianBlur(0.5)), float)


def vignette(strength):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return (np.clip(d - 0.55, 0, 1) ** 1.6 * strength)[..., None]


# 宣纸：暖白底 + 大尺度云纹 + 细颗粒 + 纤维 + 四周微暗
a = np.zeros((H, W, 3)) + np.array([244, 239, 227], float)
a += (noise(60, 2.2) + noise(2, 1.2))[..., None] * np.array([1.0, 1.0, 1.1])
f = fibers((150, 135, 110), 38, 900)
a = a * (1 - f[..., 3:4] / 255) + f[..., :3] * (f[..., 3:4] / 255)
a -= vignette(10) * np.array([1.0, 1.1, 1.4])
Image.fromarray(np.clip(a, 0, 255).astype("uint8")).save(HERE / "bg_paper.png")

# 暗墨青：深青黑底，左上一团淡青雾，细颗粒
a = np.zeros((H, W, 3)) + np.array([13, 24, 23], float)
yy, xx = np.mgrid[0:H, 0:W]
a += (np.exp(-(((xx - 500) / 900) ** 2 + ((yy - 250) / 520) ** 2) * 1.6) * 14)[..., None] * np.array([0.6, 1.0, 0.95])
a += (noise(50, 1.4) + noise(2, 0.9))[..., None]
a -= vignette(8)
Image.fromarray(np.clip(a, 0, 255).astype("uint8")).save(HERE / "bg_ink.png")

# 封面/章节：水墨远山、金线山水，直接用出图结果放大到 1920×1080
for src, dst in (("hero_dial_l", "bg_cover_l"), ("hero_dial_d", "bg_cover_d"), ("hero_summit_l", "bg_end_l"), ("hero_summit_d", "bg_end_d"),
                 ("hero_l", "bg_mist_l"), ("hero_d", "bg_mist_d")):
    p = HERE / "raw" / f"{src}.png"
    if p.exists():
        Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS).save(HERE / f"{dst}.png")
print("ok")
