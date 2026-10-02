"""生成「明亮扁平」两张底图：bg_light.png（米白加圆点加角落色块）、bg_dark.png（深蓝）。python make_bg.py"""
from PIL import Image, ImageDraw
import pathlib
HERE = pathlib.Path(__file__).parent
W, H = 1920, 1080


def make(bg, dot, blobs):
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    for y in range(30, H, 60):
        for x in range(30 + (30 if (y // 60) % 2 else 0), W, 60):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=dot)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for (cx, cy, r, col) in blobs:
        od.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    return im


make((255, 248, 236), (240, 226, 200), [(1880, 60, 190, (255, 201, 60, 70)), (60, 1040, 210, (255, 107, 74, 46)), (1700, 1080, 150, (47, 128, 237, 34))]).save(HERE / "bg_light.png")
make((27, 42, 74), (44, 62, 102), [(1880, 60, 200, (255, 201, 60, 40)), (60, 1040, 220, (255, 107, 74, 40)), (1700, 1080, 160, (47, 128, 237, 50))]).save(HERE / "bg_dark.png")
print("ok")
