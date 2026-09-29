"""通用特效。每个故事常会需要新特效：先在场景文件里写，好用的再收进这里。"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import config
from .core import clamp, ease_back, prog
from .draw import multiply, place, screen_lines, INK_DARK
from .geom import A3

import cv2


def pop(frame, A, spr, anchor, at, t, t0, scale, life=0.8, rise=25, wobble=8):
    """弹出贴图（星光、问号）：回弹放大、上浮、到期淡出。"""
    dt = t - t0
    if dt <= 0 or dt > life:
        return frame
    k = ease_back(prog(dt, 0, 0.18), 3) * (1 - prog(dt, life * 0.6, life))
    p = (at[0], at[1] - rise * prog(dt, 0, life))
    return place(frame, A, spr, anchor, p, scale * k + 1e-3, wobble * math.sin(dt * 9))


def speed_lines(frame, A, p, n=5, length=80, gap=30, back=180, col=(0.95, 0.95, 0.95), alpha=0.7):
    """运动物体身后的速度线（向左拖尾；需要其它方向时在场景里旋转坐标）。"""
    segs = [[(p[0] - back - length - 40 * (j % 2), p[1] - gap * (n - 1) / 2 + j * gap), (p[0] - back, p[1] - gap * (n - 1) / 2 + j * gap)]
            for j in range(n)]
    return screen_lines(frame, A, segs, 4, col, alpha)


def drops(frame, A, center, dt, life=0.6, n=14, seed=3, speed=(120, 260), gravity=600, width=7):
    """墨滴/水花飞溅：以 center 为中心向上半圆抛出，受重力下落。"""
    if not (0 < dt < life):
        return frame
    rng = np.random.default_rng(seed)
    segs = []
    for _ in range(n):
        ang = rng.uniform(-math.pi, 0)
        sp = rng.uniform(*speed)
        x = center[0] + math.cos(ang) * sp * dt
        y = center[1] - 10 + math.sin(ang) * sp * dt + gravity * dt * dt
        segs.append([(x, y), (x + 1, y + 3)])
    return screen_lines(frame, A, segs, width, None, 0.9 * (1 - dt / life))


def spiral(center, k, turns_pts=120, rot=0.0, squash=0.6, r0=8, dr=0.9):
    """逐笔画出的漩涡路径（场景坐标），k 为画出进度 0–1。"""
    n = int(turns_pts * clamp(k)) + 2
    return [(center[0] + (r0 + i * dr) * math.cos(i * 0.16 + rot), center[1] + (r0 + i * dr) * squash * math.sin(i * 0.16 + rot)) for i in range(n)]


def wind_lines(center, g, n=4, gap=28, length=12, travel=220):
    """从 center 向右吹出的风线，g 为推进进度。"""
    out = []
    for j in range(n):
        y0 = center[1] - 40 + j * gap
        x0 = center[0] + 40 + travel * g
        out.append([(x0 + i * length, y0 + 6 * math.sin(i * 0.5 + j)) for i in range(12)])
    return out


def handwriting(frame, A, plane, lines, t, t0, t1, col=INK_DARK, alpha=0.9):
    """在平面上逐行"写出"文字，按行依次从左到右擦出。
    lines 每项为 (文字, 字体路径, 字号, (u, v))；同一行要混用字体（中文行楷 + 英文手写）时，
    写成 ([(文字, 字体, 字号), ...], (u, v))，各段依次排开、底部对齐。"""
    if t < t0:
        return frame
    H, W = frame.shape[:2]
    img = Image.new("L", (plane.w, plane.h), 0)
    d = ImageDraw.Draw(img)
    ys = []
    for item in lines:
        if len(item) == 2:
            runs, (x, y) = item
            fonts = [ImageFont.truetype(f, sz) for _, f, sz in runs]
            base = y + max(f.getbbox("国")[3] for f in fonts)
            for (text, _, _), fnt in zip(runs, fonts):
                d.text((x, base), text, font=fnt, fill=255, anchor="ls")
                x += fnt.getlength(text)
        else:
            text, font, size, (x, y) = item
            d.text((x, y), text, font=ImageFont.truetype(font, size), fill=255)
        ys.append(y)
    m = np.asarray(img).astype(np.float32) / 255
    k = prog(t, t0, t1) * len(lines)
    wipe = np.zeros_like(m)
    bounds = ys + [plane.h]
    for i in range(len(lines)):
        y0, y1 = int(max(0, bounds[i] - 10)), int(bounds[i + 1] - 10) if i + 1 < len(lines) else plane.h
        wipe[y0:y1, : int(plane.w * clamp(k - i))] = 1
    a = cv2.warpPerspective(m * wipe * alpha, A3(A) @ plane.H, (W, H))
    return multiply(frame, a, col)


def flag(frame, A, t, base, top, t0, col, length=72, height=30, direction=-1):
    """代码画的小旗：旗杆从 base 长到 top，旗面挂在杆顶，向 direction（-1 向左）飘。
    旗子应该朝运动的反方向飘。"""
    from .draw import fill_poly
    if t < t0:
        return frame
    g = ease_back(prog(t, t0, t0 + 0.3))
    base, top = np.array(base, float), np.array(top, float)
    pole_top = base + (top - base) * clamp(g * 1.2)
    frame = screen_lines(frame, A, [[tuple(base), tuple(pole_top)]], 4, (0.55, 0.72, 0.85), 1.0)
    L, Hf = length * g, height * g
    up, down = [], []
    for i in range(12):
        w = 4 * math.sin(i * 0.8 + t * 12) * i / 11
        x = pole_top[0] + direction * L * i / 11
        up.append((x, pole_top[1] + w + 4 * g * i / 11))
        down.append((x, pole_top[1] + Hf + w - 4 * g * i / 11))
    return fill_poly(frame, A, up + down[::-1], col)
