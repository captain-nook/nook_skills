"""时间与缓动工具。所有画面都写成时间 t 的纯函数，这里的函数都不保存状态。"""
import math

import numpy as np


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, a, b):
    """t 在 [a, b] 区间里的进度，0–1。"""
    return clamp((t - a) / (b - a))


def lerp(a, b, k):
    return a + (b - a) * k


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_back(x, s=1.7):
    """带回弹的缓出，s 越大回弹越明显。"""
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def spring(dt, f=3.0, d=6.0):
    """从 1 开始衰减振荡的弹簧，用于落地挤压、晃动。"""
    return 0.0 if dt < 0 else math.exp(-d * dt) * math.cos(2 * math.pi * f * dt)


def q(t, fps=12):
    """定格量化：把时间落到 fps 的格子上（角色、船等实物用 12fps）。"""
    return math.floor(t * fps) / fps


def keys(t, pts, fn=ease):
    """关键帧插值。pts = [(t0, v0), (t1, v1), ...]，v 可以是数或元组；段内用 fn 缓动。"""
    if t <= pts[0][0]:
        return pts[0][1]
    for (ta, va), (tb, vb) in zip(pts, pts[1:]):
        if t <= tb:
            k = fn(prog(t, ta, tb))
            if isinstance(va, (tuple, list, np.ndarray)):
                return tuple(lerp(a, b, k) for a, b in zip(va, vb))
            return lerp(va, vb, k)
    return pts[-1][1]


def warp_fn(warp):
    """时间映射表 {"video": [...], "story": [...]} → (视频→故事, 故事→视频) 两个函数。"""
    if not warp:
        return (lambda t: t), (lambda t: t)
    v, s = warp["video"], warp["story"]
    return (lambda tv: float(np.interp(tv, v, s))), (lambda ts: float(np.interp(ts, s, v)))
