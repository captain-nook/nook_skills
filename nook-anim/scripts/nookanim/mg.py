"""扁平动态图形（风格卡 05）：节拍网格、文字贴片、弹入缩放、圆形擦除转场、弧形进度、数字滚动。

画布用 uint8 BGR（cv2 抗锯齿只对 8 位图生效）；文字用 PIL 渲染成 RGBA 贴片并缓存，按中心点贴。
时间轴按拍写：B = Beat(120)，B(8) 就是第 8 拍的秒数，剪辑点都落在拍上。
"""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import config
from .core import clamp, ease_back, ease_in_out, ease_out, prog


class Beat:
    def __init__(self, bpm=120.0, offset=0.0):
        self.spb = 60.0 / bpm
        self.offset = offset

    def __call__(self, n):
        """第 n 拍（可以是小数）的秒数。"""
        return self.offset + n * self.spb

    def index(self, t):
        return (t - self.offset) / self.spb


def hexc(h):
    """'#FF8A3D' → BGR 元组。"""
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b, g, r)


@functools.lru_cache(maxsize=256)
def text(s, size, color=(43, 45, 66), font=None, stroke=0, stroke_color=(255, 255, 255)):
    """文字贴片（float32 BGRA，预乘前的颜色）。color 为 BGR。"""
    f = ImageFont.truetype(font or config.FONT_UI, size)
    l, t, r, b = f.getbbox(s, stroke_width=stroke)
    pad = 8 + stroke
    img = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((pad - l, pad - t), s, font=f, fill=color[::-1] + (255,),
                             stroke_width=stroke, stroke_fill=stroke_color[::-1] + (255,))
    a = np.asarray(img).astype(np.float32) / 255
    return np.ascontiguousarray(np.dstack([a[:, :, 2], a[:, :, 1], a[:, :, 0], a[:, :, 3]]))


def paste(img, spr, center, scale=1.0, alpha=1.0, rot=0.0, anchor=(0.5, 0.5)):
    """把 BGRA 贴片按 anchor（比例）对到 center，缩放、旋转后叠到 uint8 画布上。"""
    if scale <= 0.01 or alpha <= 0.01:
        return img
    h, w = spr.shape[:2]
    H, W = img.shape[:2]
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    ax, ay = anchor[0] * w, anchor[1] * h
    M = np.array([[c * scale, -s * scale, 0], [s * scale, c * scale, 0]], np.float32)
    M[:, 2] = np.array(center, np.float32) - M[:, :2] @ np.array([ax, ay], np.float32)
    corners = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], np.float32) @ M.T
    x0, y0 = np.floor(corners.min(0)).astype(int)
    x1, y1 = np.ceil(corners.max(0)).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return img
    M[:, 2] -= (x0, y0)
    lay = cv2.warpAffine(spr, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderValue=0)
    a = lay[:, :, 3:4] * alpha
    roi = img[y0:y1, x0:x1].astype(np.float32) / 255
    img[y0:y1, x0:x1] = (np.clip(lay[:, :, :3] * a + roi * (1 - a), 0, 1) * 255).astype(np.uint8)
    return img


def pop(t, t0, dur=0.3, s=2.2):
    """弹入缩放：0 → 略超 1 → 1。t0 之前为 0。"""
    if t < t0:
        return 0.0
    return ease_back(prog(t, t0, t0 + dur), s)


def out(t, t0, dur=0.2):
    """缩出：t0 之后从 1 缩到 0。"""
    return 1.0 - ease_out(prog(t, t0, t0 + dur)) if t >= t0 else 1.0


def wipe(img, t, t0, color, center=(960, 540), dur=0.35):
    """圆形擦除转场：从 center 扩出一个填满全屏的色圆。返回是否已铺满。"""
    if t < t0:
        return False
    H, W = img.shape[:2]
    rmax = math.hypot(max(center[0], W - center[0]), max(center[1], H - center[1]))
    r = rmax * ease_in_out(prog(t, t0, t0 + dur))
    cv2.circle(img, (int(center[0]), int(center[1])), int(r) + 1, color, -1, cv2.LINE_AA)
    return r >= rmax


def arc(img, center, r, a0, a1, color, width):
    """弧形进度（角度，0 = 正上方，顺时针）。"""
    if a1 - a0 < 0.5:
        return
    cv2.ellipse(img, (int(center[0]), int(center[1])), (int(r), int(r)), -90, a0, a1, color, int(width), cv2.LINE_AA)


def count(t, t0, t1, v0, v1):
    """数字滚动（整数），缓出。"""
    return int(round(v0 + (v1 - v0) * ease_out(prog(t, t0, t1))))


def rrect(img, x0, y0, x1, y1, r, color, thickness=-1):
    """圆角矩形。"""
    x0, y0, x1, y1, r = int(x0), int(y0), int(x1), int(y1), int(r)
    if thickness < 0:
        cv2.rectangle(img, (x0 + r, y0), (x1 - r, y1), color, -1, cv2.LINE_AA)
        cv2.rectangle(img, (x0, y0 + r), (x1, y1 - r), color, -1, cv2.LINE_AA)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
            cv2.circle(img, (cx, cy), r, color, -1, cv2.LINE_AA)
    else:
        for (a, b), (c, d) in (((x0 + r, y0), (x1 - r, y0)), ((x0 + r, y1), (x1 - r, y1)), ((x0, y0 + r), (x0, y1 - r)), ((x1, y0 + r), (x1, y1 - r))):
            cv2.line(img, (a, b), (c, d), color, thickness, cv2.LINE_AA)
        for (cx, cy), ang in (((x0 + r, y0 + r), 180), ((x1 - r, y0 + r), 270), ((x0 + r, y1 - r), 90), ((x1 - r, y1 - r), 0)):
            cv2.ellipse(img, (cx, cy), (r, r), ang, 0, 90, color, thickness, cv2.LINE_AA)
