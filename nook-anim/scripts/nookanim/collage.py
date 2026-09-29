"""撕纸拼贴风格（风格卡 02）：纸片投影、"啪"地贴上、定格颤动、撕开的洞。

约定：设计空间 = 输出画面坐标（例如 1920×1080），每一层有视差系数 f（0 最远、1 与前景同步）。
Stage 负责"设计空间 → 屏幕"的摄像机（推拉 zoom、平移 pan），cutout 负责"素材 → 设计空间"的摆放。
"""
import math

import cv2
import numpy as np

from .core import clamp, ease_back, prog, spring
from .draw import over


def jitter(t, seed, amp=1.2, rot=0.25, fps=8):
    """定格颤动：每 1/fps 秒换一次的微小位移与旋转（确定性）。"""
    rng = np.random.default_rng((seed * 9973 + int(math.floor(t * fps))) & 0x7FFFFFFF)
    return rng.uniform(-amp, amp), rng.uniform(-amp, amp), rng.uniform(-rot, rot)


def slap(t, t0, drop=60, overshoot=0.12, dur=0.3):
    """纸片"啪"地贴上：返回 (缩放倍数, 竖直偏移, 可见度, 投影放大)。t<t0 时不可见。"""
    if t < t0:
        return 0.0, 0.0, 0.0, 1.0
    k = prog(t, t0, t0 + dur)
    sc = 1 + overshoot * (1 - k) ** 2 + 0.03 * spring(t - t0 - dur, 3.5, 7)
    return sc, -drop * (1 - k) ** 2, min(1.0, k * 3), 1 + 1.5 * (1 - k)


class Stage:
    """设计空间的摄像机：绕画面中心推拉 zoom，平移 pan；视差系数 f 控制每层跟随程度。"""

    def __init__(self, W, H):
        self.W, self.H = W, H

    def matrix(self, zoom, pan, f):
        z = zoom ** f
        cx, cy = self.W / 2, self.H / 2
        return np.array([[z, 0, (1 - z) * cx - pan[0] * f], [0, z, (1 - z) * cy - pan[1] * f], [0, 0, 1]], np.float64)


def sprite_matrix(anchor, at, sc, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    M = np.array([[c * sc, -s * sc, 0], [s * sc, c * sc, 0], [0, 0, 1]], np.float64)
    M[:2, 2] = np.array(at, float) - M[:2, :2] @ np.array(anchor, float)
    return M


def cutout(frame, spr, M, alpha=1.0, shadow=(10, 14, 12, 0.35), mask=None):
    """把纸片按 3x3 矩阵 M（素材→屏幕）贴到画面，先在身后投下柔和阴影。
    shadow = (dx, dy, 模糊, 强度)，单位为屏幕像素；None 关闭。mask 为可选的屏幕空间遮罩（撕洞用）。"""
    H, W = frame.shape[:2]
    lay = cv2.warpAffine(spr, M[:2].astype(np.float32), (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    if mask is not None:
        lay[:, :, 3] *= mask
    if alpha < 1:
        lay[:, :, 3] *= alpha
    if shadow is not None and shadow[3] > 0:
        dx, dy, blur, st = shadow
        a = cv2.GaussianBlur(np.roll(np.roll(lay[:, :, 3], int(dy), 0), int(dx), 1), (0, 0), max(0.5, blur))
        frame = frame * (1 - st * a[:, :, None])
    return over(frame, lay)


def torn_hole(W, H, center, radius, seed=7, rough=0.07, rim=0.035):
    """撕开的洞：返回 (纸剩余部分的遮罩, 白色纤维边遮罩, 洞内侧阴影遮罩)，都是屏幕空间 float。"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - center[0], yy - center[1]
    ang = np.arctan2(dy, dx)
    rng = np.random.default_rng(seed)
    wob = np.zeros_like(ang)
    for k, amp in ((3, 1.0), (7, 0.55), (13, 0.35), (29, 0.2), (61, 0.12)):
        wob += amp * np.sin(k * ang + rng.uniform(0, 6.28))
    r_edge = radius * (1 + rough * wob / 2.2)
    d = np.hypot(dx, dy)
    paper = np.clip((d - r_edge) / 2.0, 0, 1)                                   # 洞外为纸
    fiber = np.clip((d - r_edge) / 2.0, 0, 1) * np.clip((r_edge * (1 + rim) - d) / 3.0, 0, 1)
    fiber *= 0.75 + 0.25 * np.sin(ang * 140 + rng.uniform(0, 6.28))              # 纤维疏密
    inner = np.clip(1 - (r_edge - d) / (radius * 0.05 + 8), 0, 1) * (d < r_edge)  # 洞内侧靠边的阴影
    return paper, fiber, inner


def bits(t, t0, center, n=24, seed=5, life=1.2, speed=(250, 700), gravity=900):
    """撕开时飞出的纸屑：返回 [(x, y, 旋转, 大小, 可见度), ...]。"""
    dt = t - t0
    if not (0 < dt < life):
        return []
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        sp = rng.uniform(*speed)
        x = center[0] + math.cos(a) * sp * dt
        y = center[1] + math.sin(a) * sp * dt + gravity * dt * dt
        out.append((x, y, rng.uniform(0, 360) + dt * rng.uniform(-400, 400), rng.uniform(10, 26), 1 - dt / life))
    return out
