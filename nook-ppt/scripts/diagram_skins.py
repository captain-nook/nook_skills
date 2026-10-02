"""图示的材质容器：给任意多边形（金字塔层、漏斗层、圆、箭头……）渲染出带风格材质的 PNG（透明底）。
文字不在图里：PNG 只是容器，文字由 slidekit 另放真文字，所以字可以改。

    path, (x, y, w, h) = render("paper"|"ink"|"glass", poly_pts, color_hex, seed=1, alpha=1.0, dark=True)

poly_pts 是 pt 单位的绝对坐标（相对页面）；返回 PNG 路径和多边形外接框（含不含边距由调用方用 MARGIN 处理）。
三种材质：
  paper  撕边纸片：边缘按法线抖动、纤维白边、纸纹、向右下的投影（纸片手作）
  ink    水墨：边缘飞白与洇开、墨色中间浅边缘深、纸面晕染（东方雅集）
  glass  磨砂玻璃：半透明渐变面、边缘亮线、外发光（发布会，dark=False 时是白玻璃加蓝影）
"""
import hashlib
import math
import pathlib

import cv2
import numpy as np
from PIL import Image

SC = 3                    # 每 pt 画多少像素
MARGIN = 14               # 外接框四周留的边距（pt），放投影、洇开、发光
CACHE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "_skin_cache"


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _edge_noise(n, rng, amp, smooth=20):
    low = np.convolve(rng.normal(0, 1, n + 2 * smooth), np.ones(smooth) / smooth, "same")[smooth:n + smooth] * amp * 2.2
    return low + rng.normal(0, 1, n) * amp * 0.45


def _outline(poly, rng, amp, step=6):
    """沿每条边按外法线方向抖动，返回像素坐标折线（已含边距偏移）。多边形需顺时针。"""
    minx, miny = min(p[0] for p in poly), min(p[1] for p in poly)
    pts = []
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0) or 1e-6
        k = max(2, int(L * SC / step))
        nx, ny = (y1 - y0) / L, -(x1 - x0) / L
        j = _edge_noise(k, rng, amp * SC)
        for t in range(k):
            u = t / k
            pts.append((MARGIN * SC + (x0 + (x1 - x0) * u - minx) * SC + nx * j[t], MARGIN * SC + (y0 + (y1 - y0) * u - miny) * SC + ny * j[t]))
    return pts


def _mask(poly, rng, amp):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    amp = amp * min(1.0, max(0.3, min(max(xs) - min(xs), max(ys) - min(ys)) / 70.0))      # 小图形（如箭头）毛边按比例缩小
    minx, maxx = min(p[0] for p in poly), max(p[0] for p in poly)
    miny, maxy = min(p[1] for p in poly), max(p[1] for p in poly)
    W, H = int((maxx - minx + 2 * MARGIN) * SC), int((maxy - miny + 2 * MARGIN) * SC)
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array(_outline(poly, rng, amp), np.int32)], 255)
    return m, W, H


def _paper(poly, color, seed, alpha, dark):
    rng = np.random.default_rng(seed)
    mask, W, H = _mask(poly, rng, 2.0)
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
    rim = 3.5
    inner = cv2.erode(mask, np.ones((int(rim * SC), int(rim * SC)), np.uint8))
    noise = cv2.GaussianBlur(rng.random((H, W)).astype(np.float32), (0, 0), 2.0)
    inner = (inner.astype(np.float32) * (0.75 + 0.5 * noise)).clip(0, 255).astype(np.uint8)
    base = np.array(_hex(color), np.float32)
    k = (inner.astype(np.float32) / 255.0)[..., None]
    rgb = np.array([250, 247, 240], np.float32) * (1 - k) + base * k
    grain = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2) * 5 + cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 14) * 9
    rgb = np.clip(rgb + grain[..., None], 0, 255)
    al = mask.astype(np.float32) * alpha
    sh = np.roll(np.roll(mask, int(5 * SC), 0), int(3 * SC), 1).astype(np.float32)
    sh = cv2.GaussianBlur(sh, (0, 0), 2 * SC) * 0.30
    return rgb, np.clip(al + sh * (1 - al / 255.0), 0, 255)


def _ink(poly, color, seed, alpha, dark):
    rng = np.random.default_rng(seed)
    mask, W, H = _mask(poly, rng, 3.2)                      # 边缘比纸片更不规则
    mask = cv2.GaussianBlur(mask, (0, 0), 1.6)
    m = mask.astype(np.float32) / 255.0
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5).astype(np.float32)
    pool = np.exp(-dist / (5.0 * SC))                       # 墨在边缘聚集：边缘深、中间浅
    blot = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 16 * SC / 3)
    blot = (blot - blot.mean()) / (blot.std() + 1e-6)
    streak = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.0)
    streak = cv2.GaussianBlur(streak, (0, 0), sigmaX=22 * SC / 3, sigmaY=1.2)   # 横向干笔飞白
    streak = streak / (streak.std() + 1e-6)
    base = np.array(_hex(color), np.float32)
    if base.mean() > 190 and not dark:                         # 很浅的颜色在宣纸上会淡到看不见：调入一点墨灰
        base = base * 0.70 + np.array([52, 60, 58], np.float32) * 0.30
    paper = np.array([244, 239, 227], np.float32) if not dark else np.array([20, 34, 33], np.float32)
    # 水墨浓淡：0 = 纸色，1 = 浓墨色。中间约 0.78，边缘到 1，被噪声和飞白扰动
    dens = np.clip(0.76 + 0.20 * pool + 0.05 * blot + 0.02 * streak, 0.55, 1.0)
    rgb = paper * (1 - dens[..., None]) + base * dens[..., None]
    # 干笔飞白：边缘处随机漏出纸色
    dry = np.clip((streak * 0.4 + 0.2) * pool * 0.45, 0, 0.35)
    rgb = rgb * (1 - dry[..., None]) + paper * dry[..., None]
    # 洇开：外圈一圈很淡的墨晕
    bleed = cv2.GaussianBlur(mask, (0, 0), 3.5 * SC).astype(np.float32) / 255.0 * 0.30
    al = np.clip(m * 255 * alpha + bleed * 255 * (1 - m), 0, 255)
    rgb = np.where((m > 0.02)[..., None], rgb, base * np.ones_like(rgb))
    return np.clip(rgb, 0, 255), al


def _glass(poly, color, seed, alpha, dark):
    rng = np.random.default_rng(seed)
    minx, maxx = min(p[0] for p in poly), max(p[0] for p in poly)
    miny, maxy = min(p[1] for p in poly), max(p[1] for p in poly)
    W, H = int((maxx - minx + 2 * MARGIN) * SC), int((maxy - miny + 2 * MARGIN) * SC)
    pts = np.array([(MARGIN * SC + (x - minx) * SC, MARGIN * SC + (y - miny) * SC) for x, y in poly], np.int32)
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    mask = cv2.GaussianBlur(mask, (0, 0), 0.8)
    m = mask.astype(np.float32) / 255.0
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32)
    xx = np.linspace(0, 1, W, dtype=np.float32)[None, :] * np.ones((H, 1), np.float32)
    base = np.array(_hex(color), np.float32)
    if dark:     # 深色底：深色磨砂玻璃，染一点主色；左上受光
        body = np.array([40, 44, 54], np.float32) * 0.6 + base * 0.40
        top = np.clip(body * 1.45 + 18, 0, 255)
        rgb = top * (1 - yy[..., None] * 0.9) + body * (yy[..., None] * 0.9)
        a_body = (0.58 - 0.16 * yy) * (0.9 + 0.2 * (1 - xx))
    else:        # 浅色底：白色玻璃，染一点主色，蓝灰投影
        body = np.array([255, 255, 255], np.float32) * 0.42 + base * 0.58
        rgb = body * np.ones((H, W, 3), np.float32)
        a_body = (0.92 - 0.14 * yy)
    grain = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.0) * 3
    rgb = np.clip(rgb + grain[..., None], 0, 255)
    # 边缘亮线：描边宽约 1.2pt，左上亮、右下暗
    er = cv2.erode(mask, np.ones((int(1.4 * SC) * 2 + 1,) * 2, np.uint8))
    edge = (mask.astype(np.float32) - er.astype(np.float32)) / 255.0
    lit = np.clip(1.0 - 0.75 * (xx * 0.5 + yy * 0.5), 0.25, 1.0)
    rimc = np.array([235, 245, 255], np.float32) if dark else np.array([150, 175, 225], np.float32)
    rgb = rgb * (1 - edge[..., None] * lit[..., None]) + rimc * (edge[..., None] * lit[..., None])
    a = m * a_body + edge * lit * 0.85 * (1 - m * a_body)
    # 顶部内侧高光
    hl = cv2.GaussianBlur(np.roll(er, int(1.6 * SC), 0).astype(np.float32), (0, 0), 1.2 * SC) / 255.0
    hl = np.clip(hl * (er.astype(np.float32) / 255.0) * (1 - yy) * 0.30, 0, 1)
    rgb = rgb * (1 - hl[..., None]) + 255 * hl[..., None]
    # 外发光 / 蓝影
    glow_c = base if dark else np.array([79, 123, 224], np.float32)
    glow = cv2.GaussianBlur(mask, (0, 0), 6 * SC / 2).astype(np.float32) / 255.0 * (0.30 if dark else 0.22)
    if not dark:
        glow = np.roll(glow, int(4 * SC), 0)
    a_all = np.clip(a + glow * (1 - a), 0, 1) * alpha if alpha < 1 else np.clip(a + glow * (1 - a), 0, 1)
    rgb = np.where((a > 0.02)[..., None], rgb, glow_c * np.ones_like(rgb))
    return np.clip(rgb, 0, 255), a_all * 255


def _flat(poly, color, seed, alpha, dark):
    """明亮扁平：实心糖果色、圆角、无描边、带颜色的软影。"""
    minx, maxx = min(p[0] for p in poly), max(p[0] for p in poly)
    miny, maxy = min(p[1] for p in poly), max(p[1] for p in poly)
    W, H = int((maxx - minx + 2 * MARGIN) * SC), int((maxy - miny + 2 * MARGIN) * SC)
    pts = np.array([(MARGIN * SC + (x - minx) * SC, MARGIN * SC + (y - miny) * SC) for x, y in poly], np.int32)
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    r = 7 * SC                                                    # 圆角半径：先糊再阈值，把尖角磨圆
    mask = cv2.GaussianBlur(mask, (0, 0), r * 0.55)
    mask = np.where(mask > 128, 255, 0).astype(np.uint8)
    mask = cv2.GaussianBlur(mask, (0, 0), 0.9)
    m = mask.astype(np.float32) / 255.0
    base = np.array(_hex(color), np.float32)
    rgb = base * np.ones((H, W, 3), np.float32)
    sh = np.roll(mask, int(5 * SC), 0).astype(np.float32)
    sh = cv2.GaussianBlur(sh, (0, 0), 6 * SC / 2) / 255.0 * 0.34
    shc = base * 0.55
    a = np.clip(m * alpha + sh * (1 - m * alpha), 0, 1)
    rgb = np.where((m > 0.02)[..., None], rgb, shc * np.ones_like(rgb))
    return np.clip(rgb, 0, 255), a * 255


_KINDS = {"paper": _paper, "ink": _ink, "glass": _glass, "flat": _flat}


def render_circles(circles, colors, alpha=0.92):
    """明亮扁平的韦恩：几个实心圆，重叠处是计算出的亮色（相交各圆颜色的平均再提亮），不是半透明混色。
    circles = [(cx, cy, r)]（pt，页面坐标）；colors = 十六进制颜色。返回 (PNG 路径, (x, y, w, h))。"""
    minx = min(cx - r for cx, cy, r in circles)
    maxx = max(cx + r for cx, cy, r in circles)
    miny = min(cy - r for cx, cy, r in circles)
    maxy = max(cy + r for cx, cy, r in circles)
    key = hashlib.md5(f"venn{[(round(a, 1), round(b, 1), round(c, 1)) for a, b, c in circles]}{colors}{alpha}".encode()).hexdigest()[:14]
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"flatvenn_{key}.png"
    if not out.exists():
        W, H = int((maxx - minx + 2 * MARGIN) * SC), int((maxy - miny + 2 * MARGIN) * SC)
        masks = []
        for cx, cy, r in circles:
            mk = np.zeros((H, W), np.uint8)
            cv2.circle(mk, (int((cx - minx + MARGIN) * SC), int((cy - miny + MARGIN) * SC)), int(r * SC), 255, -1, cv2.LINE_AA)
            masks.append(mk.astype(np.float32) / 255.0)
        cnt = sum(masks)
        acc = sum(mk[..., None] * np.array(_hex(c), np.float32) for mk, c in zip(masks, colors))
        rgb = acc / np.maximum(cnt, 1e-6)[..., None]
        k = np.clip(cnt - 1, 0, 1)[..., None]
        rgb = rgb + (255 - rgb) * 0.20 * k                          # 重叠处提亮
        union = np.clip(cnt, 0, 1)
        sh = cv2.GaussianBlur(np.roll((union * 255).astype(np.uint8), int(5 * SC), 0), (0, 0), 6 * SC / 2).astype(np.float32) / 255.0 * 0.30
        a = np.clip(union * alpha + sh * (1 - union * alpha), 0, 1)
        rgb = np.where((union > 0.02)[..., None], rgb, np.array(_hex(colors[0]), np.float32) * 0.55)
        Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), "RGBA").save(out)
    return out, (minx, miny, maxx - minx, maxy - miny)


def render(kind, poly, color, seed=1, alpha=1.0, dark=True):
    """返回 (PNG 路径, (x, y, w, h))；(x, y, w, h) 是多边形外接框（pt，页面坐标）。PNG 比外接框每边多 MARGIN。"""
    minx, maxx = min(p[0] for p in poly), max(p[0] for p in poly)
    miny, maxy = min(p[1] for p in poly), max(p[1] for p in poly)
    key = hashlib.md5(f"{kind}{[(round(x, 1), round(y, 1)) for x, y in poly]}{color}{seed}{alpha}{dark}".encode()).hexdigest()[:14]
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{kind}_{key}.png"
    if not out.exists():
        rgb, a = _KINDS[kind](poly, color, seed, alpha, dark)
        Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), "RGBA").save(out)
    return out, (minx, miny, maxx - minx, maxy - miny)
