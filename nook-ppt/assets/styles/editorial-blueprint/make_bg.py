"""生成「刊物·图纸」的两张底图：paper_bg.png（内容页）、ink_bg.png（封面/章节）。python make_bg.py"""
from PIL import Image, ImageDraw
import pathlib
HERE = pathlib.Path(__file__).parent
W, H, U = 1920, 1080, 24            # 每格 24px，每 5 格一条稍深的线


def grid(bg, minor, major, mark):
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    for i, x in enumerate(range(0, W + 1, U)):
        d.line([(x, 0), (x, H)], fill=major if i % 5 == 0 else minor, width=1)
    for i, y in enumerate(range(0, H + 1, U)):
        d.line([(0, y), (W, y)], fill=major if i % 5 == 0 else minor, width=1)
    m, L = 40, 34                     # 四角套准线
    for cx, cy, sx, sy in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        d.line([(cx, cy), (cx + sx * L, cy)], fill=mark, width=3)
        d.line([(cx, cy), (cx, cy + sy * L)], fill=mark, width=3)
    return im


grid((244, 241, 234), (233, 229, 217), (222, 216, 200), (232, 89, 12)).save(HERE / "paper_bg.png")
grid((20, 30, 54), (29, 41, 70), (40, 56, 92), (232, 89, 12)).save(HERE / "ink_bg.png")
print("ok")
