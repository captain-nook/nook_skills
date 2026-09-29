"""手绘线稿风格（风格卡 03）：程序纸纹、抖动线（boil）、屏幕空间墨线层。

线条每 1/fps 秒重抖一次（默认 8fps），形成手绘动画的颤动；抖动按时间段取种子，仍是 t 的纯函数。
合成顺序建议：纸 → 彩色墨线（路、箭头）→ 背景物件黑线 → 每个角色（纸白遮挡 → 彩色填充 → 黑色轮廓）→ 特效。
"""
import math

import cv2
import numpy as np

from .draw import multiply
from .geom import A3

INK_BLACK = np.array([0.13, 0.12, 0.12], np.float32)          # BGR
PAPER = (235, 241, 246)                                          # BGR 0–255，暖白纸


def paper(w, h, seed=1, base=PAPER):
    """暖白纸纹：纤维噪声 + 大尺度斑驳，float32 BGR。"""
    rng = np.random.default_rng(seed)
    fib = cv2.GaussianBlur(rng.random((h // 4 + 1, w // 4 + 1)).astype(np.float32), (0, 0), sigmaX=6, sigmaY=0.8)
    fib = cv2.resize(fib, (w, h), interpolation=cv2.INTER_LINEAR)
    fib = (fib - fib.min()) / (fib.max() - fib.min() + 1e-9)
    mott = cv2.GaussianBlur(rng.random((h // 64 + 2, w // 64 + 2)).astype(np.float32), (0, 0), 1.5)
    mott = cv2.resize((mott - mott.min()) / (mott.max() - mott.min() + 1e-9), (w, h), interpolation=cv2.INTER_CUBIC)
    img = np.ones((h, w, 3), np.float32) * (np.array(base, np.float32) / 255)
    return img * (0.965 + 0.035 * fib[:, :, None]) * (0.975 + 0.025 * mott[:, :, None])


def boil(t, fps=8):
    return int(math.floor(t * fps))


def resample(poly, step):
    """折线按固定间距重采样，抖动才会均匀（两点直线也要加密）。"""
    p = np.array(poly, float)
    if len(p) < 2:
        return p
    seg = np.hypot(*np.diff(p, axis=0).T)
    L = np.concatenate([[0], np.cumsum(seg)])
    if L[-1] < 1e-6:
        return p
    s = np.linspace(0, L[-1], max(2, int(L[-1] / step) + 1))
    return np.stack([np.interp(s, L, p[:, 0]), np.interp(s, L, p[:, 1])], 1)


def wobble(pts, amp, seed):
    """沿线的低频抖动。seed 取物件编号与 boil 段号的组合。"""
    rng = np.random.default_rng(seed & 0x7FFFFFFF)
    ph = rng.uniform(0, 6.28, 4)
    fr = rng.uniform(0.12, 0.35, 2)
    i = np.arange(len(pts))
    out = np.array(pts, float)
    out[:, 0] += amp * (0.6 * np.sin(i * fr[0] + ph[0]) + 0.4 * np.sin(i * fr[1] * 2.3 + ph[1]))
    out[:, 1] += amp * (0.6 * np.sin(i * fr[1] + ph[2]) + 0.4 * np.sin(i * fr[0] * 1.7 + ph[3]))
    return out


def circle(c, r, a0=0.0, a1=360.0, n=40, ry=None):
    a = np.radians(np.linspace(a0, a1, n))
    return [(c[0] + r * math.cos(x), c[1] + (ry or r) * math.sin(x)) for x in a]


class Layer:
    """一张屏幕空间的墨线/填充画布（2 倍超采样）。stroke/fill 用场景坐标，自动经摄像机矩阵 A 变换。"""

    SS = 2

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.cv = np.zeros((H * self.SS, W * self.SS), np.uint8)

    def _screen(self, A, pts):
        return (A3(A) @ np.vstack([np.array(pts, float).T, np.ones(len(pts))]))[:2].T * self.SS

    def stroke(self, A, poly, width, t, seed=0, amp=2.0, taper=True, boil_fps=8, step=6):
        if poly is None or len(poly) < 2:
            return
        pts = wobble(resample(poly, step), amp, seed * 7919 + boil(t, boil_fps))
        scr = self._screen(A, pts)
        s = A[0, 0]
        n = len(scr) - 1
        for i in range(n):
            f = i / max(1, n - 1)
            tp = max(0.4, min(1.0, 6 * f, 6 * (1 - f))) if taper else 1.0
            w = width * s * self.SS * tp * (0.85 + 0.15 * math.sin(i * 0.37 + seed))
            cv2.line(self.cv, tuple(map(int, scr[i])), tuple(map(int, scr[i + 1])), 255, max(1, int(round(w))), cv2.LINE_AA)

    def fill(self, A, poly, t=0.0, seed=0, amp=1.2, boil_fps=8):
        if poly is None or len(poly) < 3:
            return
        pts = wobble(resample(list(poly) + [poly[0]], 6), amp, seed * 7919 + boil(t, boil_fps))
        cv2.fillPoly(self.cv, [self._screen(A, pts).astype(np.int32)], 255, cv2.LINE_AA)

    def dot(self, A, c, r):
        p = self._screen(A, [c])[0]
        cv2.circle(self.cv, (int(p[0]), int(p[1])), max(1, int(r * A[0, 0] * self.SS)), 255, -1, cv2.LINE_AA)

    def mask(self):
        return cv2.resize(self.cv, (self.W, self.H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255

    def ink(self, frame, col=INK_BLACK, alpha=1.0):
        """正片叠底上墨（墨线）。"""
        return multiply(frame, self.mask() * alpha, np.array(col, np.float32))

    def paint(self, frame, col, alpha=1.0):
        """不透明上色（填充、纸白遮挡）。"""
        m = self.mask()[:, :, None] * alpha
        return frame * (1 - m) + np.array(col, np.float32) * m
