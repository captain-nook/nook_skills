"""《墨猫与月亮》：水墨写意风格（风格卡 06），Qwen Image 2.1 出图 + 代码水墨合成，19 秒。

一滴墨落在生宣上，晕开成夜空，中心那块没被墨染到的纸白，就成了月亮。岸边的小猫仰头看月亮，
伸直了够、跑着追，够不着，蹲在水边低头，看见水里也有一只猫抱着月亮。它伸爪一拨，涟漪把月亮和那只猫全打散了，
溅起一串墨点；等水面慢慢静下来，月亮又拼了回来。竖排题款与印章收尾。
"""
import math
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from nookanim import assets, config, wash
from nookanim.core import clamp, ease_in_out, ease_out, prog, spring

W, H, FPS, DUR = 1920, 1080, 24, 19.0
SHOTS = [(0, "S01 墨落宣纸"), (1.4, "S02 墨化夜空"), (3.6, "S03 月出"), (4.4, "S04 猫来"), (6.0, "S05 够月亮"),
         (7.2, "S06 追"), (8.6, "S07 水边"), (9.6, "S08 水里的猫"), (10.8, "S09 拨"), (12.6, "S10 月圆"), (15.0, "S11 题款")]
D = pathlib.Path(__file__).parent / "素材"

HORIZON = 520                  # 水平线：以上是山和夜空，以下是水
DROP = (1420.0, 175.0)         # 墨滴落点 = 月亮的位置
MOON_R = 118
SURFACE_Y = 905                # 岸边小猫脚底线


def ld(name):
    p = D / f"{name}.png"
    return assets.load(p) if p.exists() else None


PAPER = wash.xuan_paper(W, H, seed=888, base=wash.XUAN_ANTIQUE)
CAT = {n: ld(n) for n in ("cat_sit", "cat_reach", "cat_run", "cat_crouch", "cat_swat")}
HILLS = ld("hills")
BANK = ld("bank")
TITLE = ld("title")


def vmult(frame, m, col=wash.INK_HEAVY):
    return frame * (1 - m[:, :, None] * (1 - col))


def ink(frame, spr, M, alpha=1.0, mask=None):
    """水墨素材正片叠底：墨色压暗纸面，纸纹透出。mask：屏幕空间遮罩。"""
    if spr is None or alpha <= 0.002:
        return frame
    h, w = spr.shape[:2]
    corners = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], np.float32) @ M.T
    x0, y0 = np.floor(corners.min(0)).astype(int)
    x1, y1 = np.ceil(corners.max(0)).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return frame
    Ml = M.copy()
    Ml[:, 2] -= (x0, y0)
    lay = cv2.warpAffine(spr, Ml, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderValue=0)
    a = np.clip(lay[:, :, 3:4] * alpha, 0, 1)
    if mask is not None:
        a = a * mask[y0:y1, x0:x1, None]
    roi = frame[y0:y1, x0:x1]
    frame[y0:y1, x0:x1] = roi * (1.0 - a * (1.0 - lay[:, :, :3]))
    return frame


def affine(anchor, at, sx, sy=None, rot=0.0):
    sy = sx if sy is None else sy
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    R = np.array([[c * sx, -s * sy], [s * sx, c * sy]], np.float32)
    t = np.array(at, np.float32) - R @ np.array(anchor, np.float32)
    return np.hstack([R, t[:, None]]).astype(np.float32)


def _vn(shape, cell, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((shape[0] // cell + 3, shape[1] // cell + 3)).astype(np.float32)
    return cv2.resize(g, (shape[1] + 2 * cell, shape[0] + 2 * cell), interpolation=cv2.INTER_CUBIC)[cell:cell + shape[0], cell:cell + shape[1]]


FIBER = 0.55 * _vn((H, W), 6, 11) + 0.30 * _vn((H, W), 22, 12) + 0.15 * _vn((H, W), 90, 13)
FIBER = (FIBER - FIBER.min()) / (FIBER.max() - FIBER.min())
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
BANK_MASK = np.clip((1440.0 - _xx) / 240.0, 0, 1).astype(np.float32)      # 岸在 x≈1100 处渐隐，右边是开阔水面
_ANG = np.arctan2(_yy - DROP[1], _xx - DROP[0])
_DIST = np.hypot(_xx - DROP[0], _yy - DROP[1])
_rng = np.random.default_rng(5)
_harm = 1.6 * sum(_rng.normal(0, 1.0 / k) * np.cos(k * _ANG + _rng.uniform(0, 6.28)) for k in range(2, 9))
_DIST_N = _DIST / (1.0 + 0.16 * _harm) + (cv2.GaussianBlur(FIBER, (0, 0), 3.0) - 0.5) * 45.0


def blot(r):
    """墨滴晕开：焦墨芯 + 淡墨晕 + 晕边一圈水渍深边。"""
    core = np.clip((0.45 * r - _DIST_N) / (0.18 * r + 4), 0, 1) ** 0.8
    halo = np.clip((r - _DIST_N) / (0.06 * r + 4), 0, 1)
    fall = np.clip(1.0 - _DIST_N / max(r, 1.0), 0, 1) ** 0.7
    wash_ = halo * (0.12 + 0.30 * fall) * (0.7 + 0.6 * FIBER)
    rim = np.exp(-((_DIST_N - r * 0.96) / (0.035 * r + 2)) ** 2) * halo * 0.6
    dens = cv2.GaussianBlur(np.clip(0.9 * core + wash_, 0, 1), (0, 0), 1.6)
    return dens, cv2.GaussianBlur(rim, (0, 0), 1.5)


def spread(r, soft=220.0):
    """墨沿纸纤维向外渗开的遮罩。"""
    return np.clip((r - _DIST_N) / soft, 0, 1)


# ---------------------------------------------------------------- 运动排期
T_DROP, T_HIT = 0.9, 1.35
T_MOON = 3.2            # 月亮中心从墨里"留白"出来的时刻
T_SWAT = 11.05
T_TITLE = 15.2


def blot_r(t):
    if t < T_HIT:
        return 0.0
    if t < 1.9:
        return 95.0 * ease_out(prog(t, T_HIT, 1.9))
    return 95.0 + 1700.0 * ease_in_out(prog(t, 1.9, 5.2))


def moon_glow(t):
    return ease_out(prog(t, T_MOON, 4.2)) * (1 + 0.12 * prog(t, 13.0, 15.0))


# ---------------------------------------------------------------- 小猫
def cat_pose(t):
    """(姿势, 脚底 x, 脚底 y, 旋转, sx, sy, alpha)"""
    if t < 4.4:
        return None
    a = ease_out(prog(t, 4.4, 5.3))
    if t < 6.0:
        return "cat_sit", 480, SURFACE_Y, 0, 1, 1, a
    if t < 7.0:                                       # 伸直了够
        u = prog(t, 6.0, 6.5)
        rise = spring(t - 6.5, 3.5, 5) * 0.03
        return "cat_reach", 480, SURFACE_Y, 0, 1 + rise, 1 + 0.04 * u, 1
    if t < 7.2:
        return "cat_sit", 480, SURFACE_Y, 0, 1, 1, 1
    if t < 8.5:                                       # 跑着追
        u = ease_in_out(prog(t, 7.2, 8.5))
        return "cat_run", 480 + 700 * u, SURFACE_Y - 40 * math.sin(math.pi * min(u * 1.2, 1)) - 20 * math.sin(t * 22) ** 2, -3 * math.sin(math.pi * u), 1, 1, 1
    if t < 10.3:                                      # 蹲在水边
        return "cat_crouch", 1180, SURFACE_Y, 0, 1 + 0.03 * spring(t - 9.0, 3, 6), 1, 1
    if t < 12.9:                                      # 伸爪一拨
        u = prog(t, 10.3, 11.05)
        return "cat_swat", 1180 + 25 * ease_out(u), SURFACE_Y, 0, 1, 1, 1
    return "cat_sit", 1205, SURFACE_Y, 0, 1 + 0.01 * math.sin(t * 2), 1, 1


CAT_K = 330.0 / assets.bbox_anchor(CAT["cat_sit"])[1][1]


def draw_cat(frame, t):
    st = cat_pose(t)
    if st is None:
        return frame
    name, x, y, rot, sx, sy, a = st
    spr = CAT[name]
    anc, _ = assets.bbox_anchor(spr)
    M = affine(anc, (x, y), CAT_K * sx, CAT_K * sy, rot)
    return ink(frame, spr, M, a)


# ---------------------------------------------------------------- 水面与倒影
RIP = []
_r = np.random.default_rng(77)
for _ in range(160):
    depth = _r.random() ** 1.5
    RIP.append(dict(x=_r.uniform(-100, 2000), y=HORIZON + 24 + depth * (H - HORIZON - 40), L=30 + 150 * depth * _r.uniform(0.5, 1.2),
                    w=1 + int(2 * depth + _r.random()), a=_r.uniform(0.15, 0.4) * (0.5 + 0.5 * depth), ph=_r.uniform(0, 6.28), amp=1.5 + 3 * depth))


def draw_water_lines(frame, t, k):
    if k <= 0.01:
        return frame
    m = np.zeros((H, W), np.float32)
    for rp in RIP:
        x = rp["x"] + 12 * math.sin(t * 0.6 + rp["ph"])
        a = rp["a"] * (0.6 + 0.4 * math.sin(t * 1.2 + rp["ph"] * 2)) * k
        n = 8
        xs = x + np.linspace(-rp["L"] / 2, rp["L"] / 2, n)
        ys = rp["y"] + rp["amp"] * np.sin(np.linspace(0, math.pi * 1.4, n) + rp["ph"] + t)
        cv2.polylines(m, [np.stack([xs, ys], 1).astype(np.int32)], False, float(a), rp["w"], cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (3, 3), 0.7) * (0.75 + 0.5 * FIBER)
    return vmult(frame, m)


REFL_C = (DROP[0], 2 * HORIZON - DROP[1])          # 月亮倒影的中心


def refl_alpha(t):
    """倒影的可见度：先浮出来，被一拨就散，静下来后又拼回来。"""
    a = ease_out(prog(t, 8.9, 10.0))
    if t >= T_SWAT:
        a = a * (1 - ease_out(prog(t, T_SWAT, T_SWAT + 0.4)))
        a = max(a, ease_out(prog(t, 12.4, 15.0)))
    return clamp(a)


def swat_wobble(t):
    if t < T_SWAT:
        return 2.0 * math.sin(t * 2)
    return 2.0 + 34.0 * math.exp(-(t - T_SWAT) * 0.75)


def draw_reflection(frame, t):
    k = refl_alpha(t)
    if k < 0.01:
        return frame
    cx, cy = REFL_C
    m = np.zeros((H, W), np.float32)
    cv2.circle(m, (int(cx), int(cy)), MOON_R, 0.55, 5, cv2.LINE_AA)
    cv2.circle(m, (int(cx), int(cy)), MOON_R + 14, 0.22, 10, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 2.0)
    tmp = vmult(frame.copy(), m)
    spr = CAT["cat_sit"][::-1]                                   # 水里倒挂的小猫，抱着月亮
    anc, size = assets.bbox_anchor(spr, 0.5, 0.5)
    scale = 175.0 / size[1]
    tmp = ink(tmp, spr, affine(anc, (cx - 6, cy + 4), scale), 0.6)
    amp = swat_wobble(t)
    ys = np.arange(H, dtype=np.float32)[:, None]
    dx = amp * np.sin(ys * 0.11 + t * 6.0) * np.exp(-((ys - cy) / 220.0) ** 2)
    out = cv2.remap(tmp, (_xx - dx).astype(np.float32), _yy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    y0, y1, x0, x1 = int(cy - 260), int(cy + 260), int(cx - 340), int(cx + 340)
    res = frame.copy()
    res[y0:y1, x0:x1] = out[y0:y1, x0:x1] * k + frame[y0:y1, x0:x1] * (1 - k)
    return res


def draw_rings(frame, t):
    dt = t - T_SWAT
    if not 0 < dt < 3.4:
        return frame
    m = np.zeros((H, W), np.float32)
    cx, cy = REFL_C[0] - 40, REFL_C[1] + 6
    for i in range(4):
        d = dt - i * 0.28
        if d <= 0:
            continue
        r = 30 + 330 * ease_out(prog(d, 0, 2.6))
        a = 0.5 * (1 - prog(d, 0.3, 2.8))
        cv2.ellipse(m, (int(cx), int(cy)), (int(r), int(r * 0.26)), 0, 0, 360, float(a), 2, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (3, 3), 0.8) * (0.7 + 0.5 * FIBER)
    return vmult(frame, m)


def draw_splash(frame, t):
    dt = t - T_SWAT
    if not 0 < dt < 1.1:
        return frame
    rng = np.random.default_rng(21)
    m = np.zeros((H, W), np.float32)
    for _ in range(26):
        a = rng.uniform(-math.pi * 0.9, -math.pi * 0.1)
        sp = rng.uniform(180, 560)
        x = REFL_C[0] - 40 + math.cos(a) * sp * dt
        y = REFL_C[1] + math.sin(a) * sp * dt + 900 * dt * dt
        r = rng.uniform(3, 9) * (1 - dt / 1.2)
        cv2.circle(m, (int(x), int(y)), max(1, int(r)), 0.9, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (3, 3), 0.9) * (1 - prog(dt, 0.7, 1.1))
    return vmult(frame, m, wash.INK_BURNT)


# ---------------------------------------------------------------- 题款与印章
def make_seal(chars="墨猫", size=96):
    big = size * 4
    img = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(img)
    pad = int(big * 0.04)
    d.rectangle((pad, pad, big - pad, big - pad), fill=255)
    font = ImageFont.truetype(str(pathlib.Path(config.FONT_UI).parent / "STLITI.TTF"), int(big * 0.42))
    for ch, (fx, fy) in zip(chars, ((0.5, 0.29), (0.5, 0.71))):
        d.text((big * fx, big * fy), ch, font=font, fill=0, anchor="mm")
    m = np.asarray(img.resize((size, size), Image.LANCZOS)).astype(np.float32) / 255
    rng = np.random.default_rng(9)
    n = cv2.GaussianBlur(rng.random((size, size)).astype(np.float32), (0, 0), 1.2)
    n = (n - n.min()) / (n.max() - n.min())
    m *= np.clip((n - 0.18) * 4, 0, 1)
    yy, xx = np.mgrid[0:size, 0:size]
    edge = np.minimum.reduce([xx, yy, size - 1 - xx, size - 1 - yy]).astype(np.float32)
    m *= np.clip((edge + 3 * (n - 0.5) * 3) / 3, 0, 1)
    return m * 0.93


SEAL = make_seal()
SEAL_RED = np.array([0.20, 0.22, 0.78], np.float32)


def draw_title(frame, t):
    if TITLE is None or t < T_TITLE:
        return frame
    p = prog(t, T_TITLE, T_TITLE + 1.6)
    h0, w0 = TITLE.shape[:2]
    sc = 700.0 / h0
    x0, y0 = 1560, 90
    yy = (_yy - y0) / (h0 * sc)
    wipe = np.clip((p * 1.25 - yy) / 0.22, 0, 1).astype(np.float32)
    frame = ink(frame, TITLE, affine((0, 0), (x0, y0), sc), 1.0, mask=wipe)
    if t >= T_TITLE + 1.9:
        k = ease_out(prog(t, T_TITLE + 1.9, T_TITLE + 2.05))
        s = SEAL.shape[0]
        M2 = affine((s / 2, s / 2), (x0 + 130, y0 + 730), 1.0 + 0.5 * (1 - k))
        seal = cv2.warpAffine(SEAL, M2, (W, H), flags=cv2.INTER_LINEAR)
        a = np.clip(seal * k, 0, 1)
        frame = frame * (1 - a[:, :, None] * (1 - SEAL_RED))
    return frame


# ---------------------------------------------------------------- 渲染
def render(t):
    frame = PAPER.copy()
    r = blot_r(t)
    if T_DROP <= t < T_HIT:                                       # 墨滴下落
        u = prog(t, T_DROP, T_HIT)
        y = -40 + (DROP[1] + 40) * u * u
        cv2.ellipse(frame, (int(DROP[0]), int(y)), (7, int(11 + 10 * u)), 0, 0, 360, tuple(float(v) for v in wash.INK_BURNT), -1, cv2.LINE_AA)
    if r > 0:
        dens, rim = blot(min(r, 95.0 + 380.0 * clamp((r - 95) / 600.0)))
        # 夜空：墨沿纸纤维向外渗开，越靠上越浓，水平线以下不染
        sky = spread(r) * np.clip(1.15 - _yy / HORIZON * 0.75, 0.2, 1.0) * np.clip((HORIZON + 22 - _yy + 26 * (FIBER - 0.5)) / 46.0, 0, 1)
        sky = cv2.GaussianBlur((sky * (0.62 + 0.38 * FIBER)).astype(np.float32), (0, 0), 2.0)
        ink_only = np.clip(np.maximum(dens * (1 - prog(t, 2.2, T_MOON + 0.6)), sky * 0.78), 0, 1)
        hole = np.clip((MOON_R - _DIST - 2.5 * (FIBER - 0.5)) / 3.0, 0, 1) * ease_out(prog(t, T_MOON, T_MOON + 0.7))
        frame = vmult(frame, ink_only * (1 - hole))
        frame = vmult(frame, rim * (1 - prog(t, 2.2, 3.4)), wash.INK_BURNT)
        if t >= T_MOON:                                           # 月亮的淡墨晕边
            ring = np.exp(-((_DIST - MOON_R - 4) / 3.5) ** 2) * 0.38 * moon_glow(t)
            frame = vmult(frame, ring.astype(np.float32), wash.INK_LIGHT)
    if HILLS is not None and t >= 2.6:                            # 山从墨里渗出
        mask = spread(r, 300.0)
        k = ease_out(prog(t, 2.6, 5.0))
        for sc_, x_ in ((1.0, 380), (0.95, 1500)):
            frame = ink(frame, HILLS, affine((HILLS.shape[1] / 2, HILLS.shape[0]), (x_, HORIZON + 26), sc_ * 0.95), 0.85 * k, mask=mask)
    frame = draw_water_lines(frame, t, ease_out(prog(t, 4.0, 6.0)))
    frame = draw_reflection(frame, t)
    frame = draw_rings(frame, t)
    if BANK is not None and t >= 3.6:
        frame = ink(frame, BANK, affine((BANK.shape[1] / 2, BANK.shape[0]), (700, H - 60), 0.85), ease_out(prog(t, 3.6, 5.2)), mask=BANK_MASK)
    frame = draw_cat(frame, t)
    frame = draw_splash(frame, t)
    frame = draw_title(frame, t)
    fade = min(1.0, t / 0.4) * min(1.0, (DUR - t) / 0.8)
    return frame * fade + PAPER * (1 - fade)


def camera_matrix(t):
    return np.array([[1, 0, 0], [0, 1, 0]], np.float64), 1.0
