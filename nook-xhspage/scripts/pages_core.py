"""共用的小工具：毛笔衬底、手写波浪线、高亮词、字体和品牌路径。"""
import html
import math
import pathlib
import random

from PIL import Image

import paths
BRAND = paths.BRAND_DIR
FONT_SANS = paths.FONTS / "NotoSansSC-VF.ttf"
FONT_KAI = paths.FONTS / "LXGWWenKai-Regular.ttf"
POSE = {k: BRAND / f"pose_{k}.png" for k in "abc"}

W, H = 1242, 1656



def uri(p):
    return pathlib.Path(p).as_uri()


def brush_svg(seed=1, color="var(--brush)"):
    """毛笔笔画衬底：两端收尖的一笔，边缘用位移滤镜做出毛边。"""
    rng = random.Random(seed)
    n = 22
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        x = 6 + 288 * t
        taper = min(1.0, t * 6, (1 - t) * 6)
        inset = (1 - taper) * 26
        top.append((x, 6 + inset + rng.uniform(-1.5, 1.5)))
        bot.append((x, 54 - inset + rng.uniform(-1.5, 1.5)))
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in top + bot[::-1])
    streaks = "".join(
        f'<line x1="{rng.uniform(20, 120):.0f}" y1="{rng.uniform(16, 44):.0f}" x2="{rng.uniform(150, 280):.0f}" '
        f'y2="{rng.uniform(16, 44):.0f}" stroke="var(--bg)" stroke-opacity=".35" stroke-width="2"/>' for _ in range(5))
    return (f'<svg class="brush" viewBox="0 0 300 60" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><filter id="rough{seed}"><feTurbulence baseFrequency="0.035 0.08" numOctaves="2" seed="{seed}"/>'
            f'<feDisplacementMap in="SourceGraphic" scale="9"/></filter></defs>'
            f'<g filter="url(#rough{seed})"><polygon points="{pts}" fill="{color}"/>{streaks}</g></svg>')


def wave_svg(width=360, amp=7, period=40, seed=1, stroke=7, color="var(--accent)"):
    rng = random.Random(seed)
    pts = [(x, 12 + amp * math.sin(x / period * 2 * math.pi) + rng.uniform(-0.8, 0.8)) for x in range(0, width, 5)]
    d = "M" + " L".join(f"{x},{y:.1f}" for x, y in pts)
    return (f'<svg class="wave" width="{width}" height="26" viewBox="0 0 {width} 26" xmlns="http://www.w3.org/2000/svg">'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def hl(text, seed=1):
    """高亮词：毛笔衬底 + 高亮字色。"""
    return f'<span class="hl"><span class="hlt">{html.escape(text)}</span>{brush_svg(seed)}</span>'

























