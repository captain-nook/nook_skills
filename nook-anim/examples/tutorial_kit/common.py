"""教程 Broll 与标题的共用件。

整期一个风格，来自封面：深蓝科技底 + 霓虹渐变（青 → 蓝 → 紫 → 粉）+ 亮黄橙强调 + Q 版船长。
画布用 uint8 BGR；精灵一律是预乘 alpha 的 BGRA float32（0–1），贴图前不会有黑边。
"""
import functools
import math
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from nookanim.core import clamp, ease, ease_back, ease_in, ease_in_out, ease_out, lerp, prog, spring

W, H, FPS = 1920, 1080, 24
PROJ = pathlib.Path(__file__).resolve().parent            # 素材/角色、素材/标题字 放在这个目录下（不随库提供）
CHAR_DIR = PROJ / "素材" / "角色"
TITLE_DIR = PROJ / "素材" / "标题字"
FONT_B = "C:/Windows/Fonts/msyhbd.ttc"
FONT_HUPO = "C:/Windows/Fonts/STHUPO.TTF"


def hexbgr(h):
    h = h.lstrip("#")
    return (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))


C = dict(
    bg0=hexbgr("#0A1330"), bg1=hexbgr("#1A3373"), card0=hexbgr("#22397D"), card1=hexbgr("#142655"),
    line=hexbgr("#6A93FF"), cyan=hexbgr("#35D0FF"), blue=hexbgr("#4C7DFF"), violet=hexbgr("#9A5CFF"),
    pink=hexbgr("#FF5FA8"), yellow=hexbgr("#FFC83D"), orange=hexbgr("#FF8A1F"), mint=hexbgr("#45F0B5"),
    white=(255, 255, 255), ink=hexbgr("#0B1330"), red=hexbgr("#FF5A5F"), dim=hexbgr("#93A9DE"), green=hexbgr("#3DDC84"),
)
NEON = [C["cyan"], C["blue"], C["violet"], C["pink"]]     # 封面标题字的渐变
WARM = [C["yellow"], C["orange"]]                          # 封面横幅的渐变


# ---------------------------------------------------------------- 基础工具

@functools.lru_cache(maxsize=64)
def lingrad(w, h, colors, angle=90.0):
    """线性渐变，float32 BGR 0–255。angle 90 = 自上而下，0 = 自左而右。"""
    a = math.radians(angle)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = (xx - w / 2) * math.cos(a) + (yy - h / 2) * math.sin(a)
    half = (abs(w * math.cos(a)) + abs(h * math.sin(a))) / 2 + 1e-6
    u = np.clip(d / (2 * half) + 0.5, 0, 1)
    cols = np.array(colors, np.float32)
    pos = np.linspace(0, 1, len(cols))
    return np.stack([np.interp(u, pos, cols[:, k]) for k in range(3)], -1).astype(np.float32)


def to_pm(bgra_u8):
    """uint8 BGRA → 预乘 float32。"""
    f = bgra_u8.astype(np.float32) / 255
    f[:, :, :3] *= f[:, :, 3:4]
    return f


def imread(path):
    return cv2.imdecode(np.fromfile(str(path), np.uint8), cv2.IMREAD_UNCHANGED)


def paste2(img, spr, at, anchor, sx=1.0, sy=1.0, rot=0.0, alpha=1.0, flip=False):
    """预乘精灵按锚点放到 at，可非等比缩放（压扁拉长）、旋转、翻转。"""
    if alpha <= 0.004 or sx == 0 or sy == 0:
        return img
    h, w = spr.shape[:2]
    ax, ay = anchor
    if flip:
        spr = spr[:, ::-1]
        ax = w - 1 - ax
    r = math.radians(rot)
    c, s = math.cos(r), math.sin(r)
    M2 = np.array([[c * sx, -s * sy], [s * sx, c * sy]], np.float32)
    t = np.array(at, np.float32) - M2 @ np.array([ax, ay], np.float32)
    M = np.hstack([M2, t[:, None]]).astype(np.float32)
    corners = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], np.float32) @ M.T
    x0, y0 = np.floor(corners.min(0)).astype(int)
    x1, y1 = np.ceil(corners.max(0)).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return img
    Ml = M.copy()
    Ml[:, 2] -= (x0, y0)
    lay = cv2.warpAffine(spr, Ml, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderValue=0)
    a = lay[:, :, 3:4] * alpha
    roi = img[y0:y1, x0:x1].astype(np.float32)
    img[y0:y1, x0:x1] = np.clip(roi * (1 - a) + lay[:, :, :3] * 255 * alpha, 0, 255).astype(np.uint8)
    return img


def put(img, spr, center, scale=1.0, alpha=1.0, rot=0.0, sx=None, sy=None, anchor=(0.5, 0.5)):
    """把精灵的比例锚点放到 center。"""
    h, w = spr.shape[:2]
    return paste2(img, spr, center, (anchor[0] * w, anchor[1] * h),
                  (sx if sx is not None else scale), (sy if sy is not None else scale), rot, alpha)


def add_light(img, x0, y0, layer, color, strength=1.0):
    """屏幕混合发光：layer 是 0–1 的强度图，放到 (x0, y0)。"""
    h, w = layer.shape[:2]
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return img
    sub = layer[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None] * strength
    roi = img[Y0:Y1, X0:X1].astype(np.float32)
    col = np.array(color, np.float32)
    img[Y0:Y1, X0:X1] = np.clip(roi + (255 - roi) * sub * (col / 255.0) * 1.0 + col * sub * 0.25, 0, 255).astype(np.uint8)
    return img


@functools.lru_cache(maxsize=32)
def _radial(size):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    d = np.hypot(xx - size / 2, yy - size / 2) / (size / 2)
    return np.clip(1 - d, 0, 1) ** 2


def glow(img, center, radius, color, strength=0.6):
    r = int(radius)
    if r < 4:
        return img
    size = max(8, int(r * 2))
    layer = cv2.resize(_radial(256), (size, size), interpolation=cv2.INTER_LINEAR)
    return add_light(img, int(center[0] - r), int(center[1] - r), layer, color, strength)


# ---------------------------------------------------------------- 背景

def _build_bg():
    g = lingrad(W, H, (C["bg0"], C["bg1"]), 90).copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for (cx, cy, rad, col, k) in ((1500, 260, 900, C["blue"], 0.30), (240, 900, 800, C["violet"], 0.22), (980, 1180, 900, C["cyan"], 0.10)):
        d = np.clip(1 - np.hypot(xx - cx, yy - cy) / rad, 0, 1) ** 2 * k
        g += d[..., None] * np.array(col, np.float32)
    # 点阵
    dots = np.zeros((H, W), np.float32)
    for y in range(36, H, 54):
        for x in range(36, W, 54):
            cv2.circle(dots, (x, y), 2, 1.0, -1, cv2.LINE_AA)
    g += dots[..., None] * 24
    # 封面同款的胶片带轮廓，很淡，放右上
    film = np.zeros((H, W), np.float32)
    pts_a = np.array([(1180 + 18 * i, 210 - 130 * math.sin(i / 21 * 2.2) + 8 * i) for i in range(0, 42)], np.float32)
    pts_b = pts_a + np.array([40, 92], np.float32)
    cv2.polylines(film, [pts_a.astype(np.int32)], False, 1.0, 3, cv2.LINE_AA)
    cv2.polylines(film, [pts_b.astype(np.int32)], False, 1.0, 3, cv2.LINE_AA)
    for k in range(1, 41, 2):
        a, b = pts_a[k], pts_b[k]
        cv2.line(film, tuple(map(int, a)), tuple(map(int, b)), 0.7, 2, cv2.LINE_AA)
    g += film[..., None] * 30
    vig = 1 - 0.38 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.78)) ** 2)
    g *= np.clip(vig, 0.4, 1)[..., None]
    return np.clip(g, 0, 255).astype(np.uint8)


BG = _build_bg()

# ---- 桌面舞台（千问出的虚化工作室 + 胡桃木桌面），整期共用；文件不存在时退回上面的渐变底 ----
STAGE_FILE = PROJ / "素材" / "场景" / "bg_desk_41.png"
STAGE_SHIFT = 130          # 整张图往下挪，桌面变成底部的台面，上面留出放信息面板的空间
FOOT_Y = 968               # 船长脚底所在的桌面线


def _build_stage():
    if not STAGE_FILE.exists():
        return None
    im = cv2.resize(imread(STAGE_FILE)[:, :, :3], (W, H), interpolation=cv2.INTER_AREA)
    top = cv2.GaussianBlur(cv2.resize(im[:24], (W, STAGE_SHIFT), interpolation=cv2.INTER_LINEAR), (0, 0), 30)
    out = np.vstack([top, im[:H - STAGE_SHIFT]])
    out = cv2.GaussianBlur(out[:400], (0, 0), 0.1) if False else out
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.30 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.85)) ** 2)
    out = np.clip(out.astype(np.float32) * np.clip(vig, 0.5, 1)[..., None] * 1.05, 0, 255).astype(np.uint8)
    return out


STAGE = _build_stage()
_BOKEH = [(1500, 240, 260, C["cyan"], 0.30, 0.9), (300, 820, 300, C["violet"], 0.26, 0.6), (1750, 880, 230, C["pink"], 0.20, 0.7),
          (620, 200, 200, C["blue"], 0.22, 1.1)]


def new_frame(t=0.0, bokeh=True, stage=True):
    img = (STAGE if (stage and STAGE is not None) else BG).copy()
    if bokeh:
        for i, (x, y, r, col, k, sp) in enumerate(_BOKEH):
            glow(img, (x + 26 * math.sin(t * sp + i), y + 18 * math.cos(t * sp * 0.8 + i * 2)), r, col, k)
    return img


# ---------------------------------------------------------------- 文字

@functools.lru_cache(maxsize=256)
def gtext(s, size, colors=None, fill=None, stroke=0, stroke_col=None, font=None, shadow=None, gangle=90.0):
    """文字精灵（预乘 BGRA）。colors 给渐变，fill 给纯色；stroke 为描边宽度。"""
    f = ImageFont.truetype(font or FONT_B, size)
    l, t, r, b = f.getbbox(s, stroke_width=stroke)
    pad = stroke + 6 + (shadow[0] if shadow else 0)
    w, h = r - l + 2 * pad, b - t + 2 * pad
    ox, oy = pad - l, pad - t
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((ox, oy), s, font=f, fill=255)
    out = np.zeros((h, w, 4), np.float32)
    m_fill = np.asarray(mask).astype(np.float32) / 255
    if stroke:
        ms = Image.new("L", (w, h), 0)
        ImageDraw.Draw(ms).text((ox, oy), s, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
        m_str = np.asarray(ms).astype(np.float32) / 255
    else:
        m_str = m_fill
    if shadow:
        dx, dy = shadow[0], shadow[1]
        sh = np.roll(np.roll(m_str, dy, 0), dx, 1)
        out[:, :, :3] = np.array(C["ink"], np.float32) / 255 * sh[..., None] * 0.9
        out[:, :, 3] = sh * 0.9
    sc = np.array(stroke_col or C["ink"], np.float32) / 255
    a = m_str[..., None]
    out[:, :, :3] = out[:, :, :3] * (1 - a) + sc * a
    out[:, :, 3] = out[:, :, 3] * (1 - m_str) + m_str
    col = (lingrad(w, h, tuple(colors), gangle) / 255) if colors else (np.array(fill or C["white"], np.float32) / 255)
    a2 = m_fill[..., None]
    out[:, :, :3] = out[:, :, :3] * (1 - a2) + col * a2
    out[:, :, 3] = np.maximum(out[:, :, 3], m_fill)
    return out          # 各层都是按 over 算子叠出来的，rgb 已经是预乘


def label(img, s, center, size=48, scale=1.0, alpha=1.0, colors=None, fill=None, stroke=7, rot=0.0):
    spr = gtext(s, size, tuple(colors) if colors else None, fill or C["white"], stroke, C["ink"])
    return put(img, spr, center, scale, alpha, rot)


# ---------------------------------------------------------------- 形状

def _rr_mask(w, h, r, ss=2):
    """圆角矩形遮罩（float 0–1），超采样抗锯齿。"""
    m = np.zeros((h * ss, w * ss), np.uint8)
    R = int(r * ss)
    cv2.rectangle(m, (R, 0), (w * ss - 1 - R, h * ss - 1), 255, -1)
    cv2.rectangle(m, (0, R), (w * ss - 1, h * ss - 1 - R), 255, -1)
    for cx, cy in ((R, R), (w * ss - 1 - R, R), (R, h * ss - 1 - R), (w * ss - 1 - R, h * ss - 1 - R)):
        cv2.circle(m, (cx, cy), R, 255, -1)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def panel(img, x0, y0, x1, y1, r=30, fill=None, colors=None, outline=None, ow=4, glow_col=None, glow_a=0.5, shadow=True, alpha=1.0, angle=90.0):
    """玻璃卡片 / 药丸 / 色块。colors 渐变，fill 纯色；outline 描边色；glow_col 外发光；shadow 硬阴影。"""
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    w, h = x1 - x0, y1 - y0
    if w < 4 or h < 4 or alpha <= 0.004:
        return img
    m = 46 if glow_col else 22
    X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(W, x1 + m + 14), min(H, y1 + m + 16)
    if X1 <= X0 or Y1 <= Y0:
        return img
    roi = img[Y0:Y1, X0:X1].astype(np.float32)

    def place(mask, ex=0):
        full = np.zeros(roi.shape[:2], np.float32)
        ox, oy = x0 - ex - X0, y0 - ex - Y0
        hh, ww = mask.shape
        ys0, xs0 = max(0, oy), max(0, ox)
        ys1, xs1 = min(full.shape[0], oy + hh), min(full.shape[1], ox + ww)
        if ys1 > ys0 and xs1 > xs0:
            full[ys0:ys1, xs0:xs1] = mask[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
        return full

    mk = place(_rr_mask(w, h, r))
    mo = place(_rr_mask(w + 2 * ow, h + 2 * ow, r + ow), ow) if outline is not None else mk
    if shadow:
        sh = np.roll(np.roll(mo, 9, 0), 7, 1)
        roi *= (1 - sh[..., None] * 0.42 * alpha)
    if glow_col is not None:
        gb = cv2.GaussianBlur(mo, (0, 0), 12) * glow_a * alpha
        roi = roi + (255 - roi) * gb[..., None] * (np.array(glow_col, np.float32) / 255) + np.array(glow_col, np.float32) * gb[..., None] * 0.25
    if outline is not None:
        roi = roi * (1 - mo[..., None] * alpha) + np.array(outline, np.float32) * mo[..., None] * alpha
    if colors is not None:
        g = np.zeros(roi.shape, np.float32)
        gg = lingrad(w, h, tuple(colors), angle)
        gy0, gx0 = y0 - Y0, x0 - X0
        ys0, xs0 = max(0, gy0), max(0, gx0)
        ys1, xs1 = min(roi.shape[0], gy0 + h), min(roi.shape[1], gx0 + w)
        if ys1 > ys0 and xs1 > xs0:            # 面板整个在画面外、只有阴影边距落在画面里时，不用铺渐变
            g[ys0:ys1, xs0:xs1] = gg[ys0 - gy0:ys1 - gy0, xs0 - gx0:xs1 - gx0]
    else:
        g = np.zeros(roi.shape, np.float32) + np.array(fill or C["card1"], np.float32)
    roi = roi * (1 - mk[..., None] * alpha) + g * mk[..., None] * alpha
    img[Y0:Y1, X0:X1] = np.clip(roi, 0, 255).astype(np.uint8)
    return img


def card(img, x0, y0, x1, y1, scale=1.0, alpha=1.0, glow_col=None, r=30, outline=None, colors=None):
    """玻璃卡片，可按中心缩放（用于弹入）。"""
    if scale <= 0.02:
        return img
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hh = (x1 - x0) / 2 * scale, (y1 - y0) / 2 * scale
    return panel(img, cx - hw, cy - hh, cx + hw, cy + hh, r=r * min(1, scale + 0.2), colors=colors or (C["card0"], C["card1"]),
                 outline=outline or C["line"], ow=4, glow_col=glow_col or C["blue"], glow_a=0.45, alpha=alpha)


def poly_fill(img, pts, color=None, colors=None, alpha=1.0, outline=None, ow=0, angle=90.0):
    pts = np.array(pts, np.float32)
    x0, y0 = np.floor(pts.min(0)).astype(int) - 3
    x1, y1 = np.ceil(pts.max(0)).astype(int) + 3
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if X1 <= X0 or Y1 <= Y0:
        return img
    ss = 3
    m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
    cv2.fillPoly(m, [((pts - [x0, y0]) * ss).astype(np.int32)], 255, cv2.LINE_AA)
    m = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    roi = img[Y0:Y1, X0:X1].astype(np.float32)
    mm = m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    if outline is not None and ow > 0:
        mo = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
        cv2.polylines(mo, [((pts - [x0, y0]) * ss).astype(np.int32)], True, 255, ow * ss, cv2.LINE_AA)
        mo = cv2.resize(mo, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        mo = np.maximum(mo[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0], 0)
    if colors is not None:
        col = lingrad(x1 - x0, y1 - y0, tuple(colors), angle)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    else:
        col = np.array(color or C["white"], np.float32)
    roi = roi * (1 - mm[..., None] * alpha) + col * mm[..., None] * alpha
    if outline is not None and ow > 0:
        roi = roi * (1 - mo[..., None] * alpha) + np.array(outline, np.float32) * mo[..., None] * alpha
    img[Y0:Y1, X0:X1] = np.clip(roi, 0, 255).astype(np.uint8)
    return img


def circle(img, c, r, color=None, colors=None, outline=None, ow=0, alpha=1.0, glow_col=None):
    r = float(r)
    if r < 1:
        return img
    if glow_col is not None:
        glow(img, c, r * 2.2, glow_col, 0.5 * alpha)
    n = 40
    pts = [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return poly_fill(img, pts, color, colors, alpha, outline, ow)


def line(img, a, b, color, width=6, alpha=1.0):
    if alpha >= 0.99:
        cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), color, int(width), cv2.LINE_AA)
        return img
    ov = img.copy()
    cv2.line(ov, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), color, int(width), cv2.LINE_AA)
    return cv2.addWeighted(ov, alpha, img, 1 - alpha, 0, img)


def polyline(img, pts, color, width=6, alpha=1.0):
    p = np.array(pts, np.float32).round().astype(np.int32)
    if alpha >= 0.99:
        cv2.polylines(img, [p], False, color, int(width), cv2.LINE_AA)
        return img
    ov = img.copy()
    cv2.polylines(ov, [p], False, color, int(width), cv2.LINE_AA)
    return cv2.addWeighted(ov, alpha, img, 1 - alpha, 0, img)


def sparkle(img, c, size, color=None, rot=0.0, alpha=1.0):
    """四角星光。"""
    color = color or C["white"]
    pts = []
    for i in range(8):
        rr = size if i % 2 == 0 else size * 0.22
        a = math.radians(rot) + i * math.pi / 4 - math.pi / 2
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    glow(img, c, size * 1.8, color, 0.5 * alpha)
    return poly_fill(img, pts, color, alpha=alpha)


def slashes(img, c, r0, r1, angles, color, width=7, k=1.0):
    """封面里的霓虹放射短线。k 为出现进度 0–1。"""
    for a in angles:
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        p0 = (c[0] + ca * (r0 + (r1 - r0) * 0.0), c[1] + sa * r0)
        p1 = (c[0] + ca * (r0 + (r1 - r0) * k), c[1] + sa * (r0 + (r1 - r0) * k))
        line(img, p0, p1, color, width)
    return img


# ---------------------------------------------------------------- Q 版船长

_POSES = {"idle": "idle_crossed_arms.png", "win": "win_v_sign.png", "point": "pose_point.png", "think": "pose_think.png",
          "present": "pose_present.png", "wow": "pose_wow.png", "shrug": "pose_shrug.png",
          "walk": "pose_walk.png", "walk_b": "pose_walk_b.png"}
_POSE_FIX = {"win": 844 / 896}        # 原型截图两张尺寸不同，统一到 idle 的像素比例
_STAND_H = None


@functools.lru_cache(maxsize=64)
def pose_sprite(name, h):
    """返回 (预乘精灵, 脚底锚点)。h = 站立（idle）时整个人的像素高度；带白色贴纸描边，深色底上也分得开。"""
    im = imread(CHAR_DIR / _POSES[name])
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    ys, xs = np.where(im[:, :, 3] > 40)
    idle = imread(CHAR_DIR / _POSES["idle"])
    iy = np.where(idle[:, :, 3] > 40)[0]
    idle_h = iy.max() - iy.min()
    sc = h / idle_h * _POSE_FIX.get(name, 1.0)
    im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    ys, xs = np.where(im[:, :, 3] > 40)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    k = max(3, int(round(h / 150)))
    pad = k * 2 + 4
    im = cv2.copyMakeBorder(im[y0:y1 + 1, x0:x1 + 1], pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    a = im[:, :, 3].astype(np.float32) / 255
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))
    ring = cv2.GaussianBlur(cv2.dilate(a, ker), (0, 0), 0.9)
    f = im.astype(np.float32) / 255
    rgb = f[:, :, :3] * f[:, :, 3:4] + np.array([1, 1, 1], np.float32) * (ring - a * 0)[..., None] * (1 - f[:, :, 3:4])
    alpha = np.maximum(ring, a)
    spr = np.dstack([rgb, alpha]).astype(np.float32)
    # 锚点：y 取最低的脚底；x 静态姿势取脚底中心，走路姿势（两脚一前一后）取躯干中心
    bys = np.where(alpha > 0.5)[0]
    yb = bys.max()
    if name.startswith("walk"):
        top = bys.min()
        rows = slice(int(top + 0.30 * (yb - top)), int(top + 0.55 * (yb - top)))
        cols = np.where(alpha[rows].max(0) > 0.5)[0]
        xc = (cols.min() + cols.max()) / 2
    else:
        rows = slice(int(yb - 0.06 * (yb - bys.min())), yb)
        cols = np.where(alpha[rows].max(0) > 0.5)[0]
        xc = cols.mean()
    return spr, (float(xc), float(yb - k))


def char(img, pose, foot, h=620, sx=1.0, sy=1.0, rot=0.0, alpha=1.0, flip=False, shadow=True):
    """画船长。foot = 脚底中心；squash 用 sx、sy（锚点在脚底，压扁不会离地）。"""
    spr, anc = pose_sprite(pose, int(round(h / 8) * 8))
    if shadow and alpha > 0.05:
        wsh = int(0.30 * h * (0.5 + 0.5 * sx))
        bw, bh = wsh * 2 + 80, int(0.045 * h) * 2 + 80
        X0, Y0 = int(foot[0] - bw / 2), int(foot[1] - bh / 2)
        ell = np.zeros((bh, bw), np.float32)
        cv2.ellipse(ell, (bw // 2, bh // 2), (wsh, int(0.045 * h)), 0, 0, 360, 0.55 * alpha, -1, cv2.LINE_AA)
        ell = cv2.GaussianBlur(ell, (0, 0), 10)
        xa, ya, xb, yb = max(0, X0), max(0, Y0), min(W, X0 + bw), min(H, Y0 + bh)
        if xb > xa and yb > ya:
            roi = img[ya:yb, xa:xb].astype(np.float32)
            img[ya:yb, xa:xb] = np.clip(roi * (1 - ell[ya - Y0:yb - Y0, xa - X0:xb - X0, None]), 0, 255).astype(np.uint8)
    return paste2(img, spr, foot, anc, sx, sy, rot, alpha, flip)


def hop(t, t0, dur=0.55, height=90):
    """一次跳跃：返回 (y 偏移, sx, sy)。落地带压扁回弹。"""
    if t < t0:
        return 0.0, 1.0, 1.0
    u = (t - t0) / dur
    if u < 1:
        pre = 0.12
        if u < pre:                                  # 起跳前蹲一下
            k = u / pre
            return 0.0, 1 + 0.10 * k, 1 - 0.14 * k
        v = (u - pre) / (1 - pre)
        return -height * 4 * v * (1 - v), 1 - 0.06 * math.sin(math.pi * v), 1 + 0.10 * math.sin(math.pi * v)
    sp = spring(t - t0 - dur, 3.4, 7.5)
    return 0.0, 1 + 0.14 * sp, 1 - 0.18 * sp


def breathe(t, amp=0.012, f=1.6):
    s = math.sin(t * f * 2 * math.pi)
    return 1 - amp * s * 0.6, 1 + amp * s


# ---------------------------------------------------------------- 图标

def icon_code(img, c, size, color=None, alpha=1.0, scale=1.0):
    spr = gtext("</>", int(size * scale), None, color or C["cyan"], 0, None, FONT_B)
    return put(img, spr, c, 1.0, alpha)


def icon_play(img, c, r, color=None, alpha=1.0):
    color = color or C["white"]
    pts = [(c[0] - r * 0.55, c[1] - r * 0.8), (c[0] - r * 0.55, c[1] + r * 0.8), (c[0] + r * 0.85, c[1])]
    return poly_fill(img, pts, color, alpha=alpha)


def icon_check(img, c, r, color=None, width=None, alpha=1.0):
    color = color or C["mint"]
    width = width or max(4, int(r * 0.32))
    return polyline(img, [(c[0] - r * 0.7, c[1]), (c[0] - r * 0.2, c[1] + r * 0.55), (c[0] + r * 0.8, c[1] - r * 0.6)], color, width, alpha)


def icon_camera(img, c, r, color=None, flash=0.0):
    color = color or C["white"]
    panel(img, c[0] - r, c[1] - r * 0.62, c[0] + r, c[1] + r * 0.72, r=r * 0.2, fill=color, outline=C["ink"], ow=4, shadow=False)
    panel(img, c[0] - r * 0.42, c[1] - r * 0.86, c[0] + r * 0.05, c[1] - r * 0.55, r=r * 0.08, fill=color, outline=C["ink"], ow=3, shadow=False)
    circle(img, (c[0], c[1] + r * 0.05), r * 0.42, C["ink"])
    circle(img, (c[0], c[1] + r * 0.05), r * 0.3, C["blue"])
    circle(img, (c[0] - r * 0.1, c[1] - r * 0.05), r * 0.09, C["white"])
    if flash > 0:
        glow(img, (c[0] + r * 0.55, c[1] - r * 0.35), r * 1.5 * flash, C["white"], 0.7 * flash)
    return img


def icon_film(img, x0, y0, x1, y1, color=None, hole=None, alpha=1.0, n=None):
    """一段胶片：深色底、两侧齿孔。"""
    color = color or C["ink"]
    hole = hole or C["dim"]
    panel(img, x0, y0, x1, y1, r=8, fill=color, outline=C["dim"], ow=3, shadow=False, alpha=alpha)
    hh = y1 - y0
    step = max(14, int(hh * 0.30))
    n = n or int((x1 - x0) / step)
    for i in range(n):
        x = x0 + step * (i + 0.5)
        panel(img, x - step * 0.22, y0 + hh * 0.07, x + step * 0.22, y0 + hh * 0.07 + hh * 0.11, r=3, fill=hole, shadow=False, alpha=alpha)
        panel(img, x - step * 0.22, y1 - hh * 0.07 - hh * 0.11, x + step * 0.22, y1 - hh * 0.07, r=3, fill=hole, shadow=False, alpha=alpha)
    return img


def icon_gear(img, c, r, color=None, rot=0.0, teeth=8):
    color = color or C["dim"]
    pts = []
    for i in range(teeth * 4):
        a = math.radians(rot) + i * 2 * math.pi / (teeth * 4)
        rr = r if (i % 4) in (0, 1) else r * 0.78
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    poly_fill(img, pts, color, outline=C["ink"], ow=3)
    circle(img, c, r * 0.36, C["card1"], outline=C["ink"], ow=3)
    return img


def icon_eye(img, c, r, look=(0, 0), blink=0.0, color=None):
    color = color or C["white"]
    hh = r * 0.62 * (1 - blink)
    if hh < 2:
        return line(img, (c[0] - r, c[1]), (c[0] + r, c[1]), C["ink"], 5)
    pts = [(c[0] + r * math.cos(a), c[1] - hh * math.sin(a) * (1 if True else 0)) for a in np.linspace(0, math.pi, 20)]
    pts += [(c[0] + r * math.cos(a), c[1] + hh * math.sin(a)) for a in np.linspace(math.pi, 2 * math.pi, 20)]
    poly_fill(img, pts, color, outline=C["ink"], ow=4)
    circle(img, (c[0] + look[0] * r * 0.3, c[1] + look[1] * r * 0.2), min(hh, r) * 0.62, C["blue"])
    circle(img, (c[0] + look[0] * r * 0.3, c[1] + look[1] * r * 0.2), min(hh, r) * 0.3, C["ink"])
    return img


def arrow(img, a, b, color, width=8, head=26, alpha=1.0):
    d = np.array(b, float) - np.array(a, float)
    L = np.linalg.norm(d)
    if L < 2:
        return img
    u = d / L
    n = np.array([-u[1], u[0]])
    line(img, a, np.array(b) - u * head * 0.7, color, width, alpha)
    tip = np.array(b, float)
    poly_fill(img, [tip, tip - u * head + n * head * 0.62, tip - u * head - n * head * 0.62], color, alpha=alpha)
    return img


def pop(t, t0, dur=0.32, s=2.4):
    """弹入缩放：0 → 过冲 → 1。"""
    if t < t0:
        return 0.0
    return ease_back(prog(t, t0, t0 + dur), s)


def fade_io(t, dur, fin=0.25, fout=0.3):
    return clamp(t / fin) * clamp((dur - t) / fout)


def char_walk(img, x, t, h=400, facing=1, moving=True, foot_y=None, rate=4.6, alpha=1.0):
    """走路：两帧交替 + 起伏 + 轻摇。facing=1 朝右，-1 朝左。不在走时用站立姿势。"""
    fy = foot_y if foot_y is not None else FOOT_Y
    if not moving:
        return char(img, "idle", (x, fy), h=h, flip=(facing < 0), alpha=alpha, sx=breathe(t)[0], sy=breathe(t)[1])
    ph = t * rate
    pose = "walk" if int(ph) % 2 == 0 else "walk_b"
    bob = -abs(math.sin(math.pi * ph)) * 13
    sway = 2.2 * math.sin(math.pi * ph) * facing
    return char(img, pose, (x, fy + bob), h=h, rot=sway, flip=(facing < 0), alpha=alpha)
