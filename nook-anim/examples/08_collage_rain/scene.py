"""《撕开下雨天》：撕纸拼贴风格（风格卡 02），Qwen Image 2.1 出图 + 代码合成，19 秒。

灰蒙蒙的雨天，黄雨衣小人撑着红伞发愁；他把伞往天上一抛，踮脚够住低垂的乌云，双手一撕——
云和灰天空被撕开一个洞，洞后是彩色的晴天。纸花一朵朵拍上来，红伞变成一只纸鸟飞走，
天上再贴一道撕纸彩虹；最后一行剪纸字拍在画面上。
"""
import math
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import cv2
import numpy as np

from nookanim import assets, collage, core, draw, post
from nookanim.core import clamp, ease, ease_back, ease_in, ease_in_out, ease_out, keys, prog, spring
from nookanim.collage import Stage, cutout, jitter, slap, sprite_matrix

W, H, FPS, DUR = 1920, 1080, 24, 19.0
SHOTS = [(0, "S01 雨天"), (4.4, "S02 抛伞"), (5.2, "S03 够云"), (6.2, "S04 撕开"), (7.6, "S05 晴天"),
         (9.4, "S06 变鸟"), (12.0, "S07 彩虹"), (15.0, "S08 落款")]
D = pathlib.Path(__file__).parent / "素材"


def ld(n):
    p = D / f"{n}.png"
    return assets.load(p) if p.exists() else None


S = {n: ld(n) for n in ("bg_gray", "bg_sunny", "man", "man_reach", "man_cheer", "man_wave", "umbrella", "bird_red", "cloud", "flowers", "rainbow", "title")}
STAGE = Stage(W, H)
FOOT = (780, 955)          # 小人脚底
MAN_H = 540.0
CLOUD_C = (790, 250)       # 乌云中心
HOLE_C = (790, 330)        # 撕口


def sc_of(name, h=MAN_H, ref="man"):
    _, size = assets.bbox_anchor(S[ref])
    return h / size[1]


K_MAN = sc_of("man")


def cam(t):
    zoom = keys(t, [(0, 1.0), (4.4, 1.06), (5.6, 1.16), (6.6, 1.2), (8.0, 1.05), (12.0, 1.0), (16, 1.03)], ease_in_out)
    pan = keys(t, [(0, (0, 0)), (5.6, (-30, -60)), (6.6, (-30, -90)), (8.4, (0, 0)), (16, (0, 0))], ease_in_out)
    sh = (0.0, 0.0)
    if 6.2 <= t < 6.7:
        n = int(t * 24)
        sh = (((n * 37) % 7 - 3) * 2.2, ((n * 53) % 5 - 2) * 2.2)
    return zoom, (pan[0] + sh[0], pan[1] + sh[1])


def M_of(t, f, anchor, at, sc, rot=0.0, jit=None, amp=1.0, sx=1.0, sy=1.0):
    if jit is not None:
        jx, jy, jr = jitter(t, jit, amp, 0.25 * amp)
        at = (at[0] + jx, at[1] + jy)
        rot += jr
    zoom, pan = cam(t)
    M = sprite_matrix(anchor, at, sc, rot)
    if sx != 1.0 or sy != 1.0:
        M = M @ np.array([[sx, 0, anchor[0] * (1 - sx)], [0, sy, anchor[1] * (1 - sy)], [0, 0, 1]])
    return STAGE.matrix(zoom, pan, f) @ M


def to_screen(t, f, p):
    zoom, pan = cam(t)
    q = STAGE.matrix(zoom, pan, f) @ np.array([p[0], p[1], 1.0])
    return q[:2]


def shadow(t, st=0.35, size=1.0):
    z = cam(t)[0]
    return (9 * z * size, 13 * z * size, 11 * z * size, st)


def center(spr):
    return (spr.shape[1] / 2, spr.shape[0] / 2)


def bg_M(t, f=0.3):
    spr = S["bg_gray"]
    s = 1.02 * W / spr.shape[1] * 1.04
    return M_of(t, f, center(spr), (W / 2, H / 2 + 20), s)


# ---------------- 时间线 ----------------
T_TOSS, T_REACH, T_TEAR, T_SUN, T_BIRD, T_RAINBOW, T_TITLE = 4.4, 5.2, 6.2, 7.6, 9.4, 12.0, 15.0


def hole_r(t):
    if t < T_TEAR:
        return 0.0
    return 24 + 2400 * ease_in_out(prog(t, T_TEAR + 0.25, T_TEAR + 2.5)) ** 1.5 if t > T_TEAR + 0.25 else 24 * prog(t, T_TEAR, T_TEAR + 0.25) + 3 * math.sin(t * 30)


def man_state(t):
    """(姿势, 脚底 y 偏移, sx, sy, 旋转)"""
    tq = core.q(t)
    if t < T_TOSS:
        b = 1 + 0.012 * math.sin(tq * 5)
        return "man", 0, 1.0, b, 0
    if t < T_REACH:
        d = t - T_TOSS
        return "man_reach", -70 * math.sin(math.pi * clamp(d / 0.8)) * 0.5, 1 + 0.04 * spring(d - 0.4, 4, 6), 1, 0
    if t < T_TEAR:
        d = t - T_REACH
        hop = -60 * abs(math.sin(min(d, 1.0) * math.pi * 2.0)) * (1 if d < 1.0 else 0)
        return "man_reach", hop, 1, 1 + 0.03 * math.sin(tq * 9), 0
    if t < T_TEAR + 1.5:
        d = t - T_TEAR
        return "man_reach", -20 * math.sin(math.pi * clamp(d / 0.6)), 1, 1, 0
    if t < 11.2:
        d = t - (T_TEAR + 1.5)
        hop = -34 * abs(math.sin(d * 5.2)) * (1 if d < 1.6 else 0.0)
        return "man_cheer", hop, 1, 1, 2 * math.sin(tq * 6)
    return "man_wave", 0, 1, 1 + 0.01 * math.sin(tq * 5), 0


# ---------------- 雨 ----------------
def rain(frame, t, strength):
    if strength <= 0.02:
        return frame
    tq = core.q(t, 12)
    rng = np.random.default_rng(3)
    n = 130
    xs = rng.uniform(-200, W + 100, n)
    ph = rng.uniform(0, 1, n)
    ln = rng.uniform(34, 70, n)
    ov = frame.copy()
    for i in range(n):
        y = ((tq * 1.1 + ph[i]) % 1.0) * (H + 200) - 100
        x = xs[i] + y * 0.14
        cv2.line(ov, (int(x), int(y)), (int(x - ln[i] * 0.14), int(y - ln[i])), (0.92, 0.80, 0.68), 3, cv2.LINE_AA)
    a = 0.55 * strength
    return cv2.addWeighted(ov, a, frame, 1 - a, 0)


# ---------------- 渲染 ----------------
def render(t):
    zoom, pan = cam(t)
    frame = np.zeros((H, W, 3), np.float32)
    r = hole_r(t)
    c_hole = to_screen(t, 0.3, HOLE_C)
    # 晴天在下、灰天在上（灰天被撕开）
    sunny = S["bg_sunny"]
    frame = cutout(frame, sunny, bg_M(t), shadow=None)
    gray = S["bg_gray"]
    if r <= 0:
        frame = cutout(frame, gray, bg_M(t), shadow=None)
    elif r < 2390:
        paper_m, fiber, inner = collage.torn_hole(W, H, c_hole, max(r, 0.5), seed=7)
        frame *= (1 - 0.35 * inner)[:, :, None]
        frame = cutout(frame, gray, bg_M(t), shadow=None, mask=paper_m)
        fr = fiber[:, :, None]
        frame = frame * (1 - 0.9 * fr) + 0.93 * fr
    # 晴天的太阳自带；雨只在灰天里
    rain_k = 1.0 if r <= 0 else clamp(1 - r / 500.0)
    if t < 4.4 + 0.1 or r < 2300:
        frame = rain(frame, t, rain_k)

    # 花（晴天后从地面拍上来）
    if t >= 8.0:
        spr = S["flowers"]
        for i, (x, y, sc, flip) in enumerate(((420, 990, 0.9, False), (1010, 1000, 0.8, True), (1340, 985, 1.0, False), (250, 1010, 0.7, True), (1650, 1005, 0.85, False), (1830, 990, 0.7, True))):
            t0 = 8.0 + i * 0.22
            if t >= t0:
                s_, dy, vis, shs = slap(t, t0, drop=90, overshoot=0.12)
                img = spr[:, ::-1] if flip else spr
                anc, size = assets.bbox_anchor(img)
                k = sc * 330.0 / size[1]
                frame = cutout(frame, img, M_of(t, 1.0, anc, (x, y + dy), k * s_, jit=100 + i, amp=0.8), alpha=vis, shadow=shadow(t, 0.3, shs))

    # 彩虹
    if t >= T_RAINBOW and S["rainbow"] is not None:
        spr = S["rainbow"]
        anc, size = assets.bbox_anchor(spr, 0.5, 1.0)
        s_, dy, vis, shs = slap(t, T_RAINBOW, drop=140, overshoot=0.06, dur=0.4)
        k = 1150.0 / size[0]
        frame = cutout(frame, spr, M_of(t, 0.6, anc, (1380, 700 + dy), k * s_, jit=120, amp=0.6), alpha=vis, shadow=shadow(t, 0.3, shs))

    # 乌云（够到之前挂在头顶，撕开时被扯走）
    if S["cloud"] is not None and T_REACH - 0.6 <= t < T_TEAR + 1.4:
        spr = S["cloud"]
        k = 1.2 * 760.0 / assets.bbox_anchor(spr)[1][0]
        vis = ease_out(prog(t, T_REACH - 0.6, T_REACH)) * (1 - ease_in(prog(t, T_TEAR + 0.5, T_TEAR + 1.3)))
        off = np.array([-700, -420]) * ease_in(prog(t, T_TEAR + 0.2, T_TEAR + 1.3))
        at = (CLOUD_C[0] + off[0], CLOUD_C[1] + 40 + off[1] + 10 * math.sin(t * 2))
        frame = cutout(frame, spr, M_of(t, 0.8, center(spr), at, k, rot=off[0] * -0.01, jit=130, amp=1.0), alpha=vis, shadow=shadow(t, 0.4))

    # 小人
    name, dy, sx, sy, rot = man_state(t)
    spr = S[name]
    anc, size = assets.bbox_anchor(spr)
    k = K_MAN
    if name == "man_wave" or name == "man_cheer" or name == "man_reach":
        pass
    frame = cutout(frame, spr, M_of(t, 1.0, anc, (FOOT[0], FOOT[1] + dy), k, rot=rot, jit=31, amp=0.9, sx=sx, sy=sy), shadow=shadow(t, 0.38))

    # 红伞：抛出去 → 躺在地上 → 变成纸鸟
    ux, uy, urot, ushow = umbrella_state(t)
    if t >= T_TOSS and t < T_BIRD + 0.3 and ushow:
        spr = S["umbrella"]
        anc, size = assets.bbox_anchor(spr)
        k = 0.78 * MAN_H * 1.05 / size[0]
        frame = cutout(frame, spr, M_of(t, 1.0, center(spr), (ux, uy), k, rot=urot, jit=150, amp=0.8), shadow=shadow(t, 0.35))
    bx, by, brot, bk, bflap = bird_state(t)
    if bk > 0.01 and S["bird_red"] is not None:
        spr = S["bird_red"]
        anc, size = assets.bbox_anchor(spr)
        k = bk * 520.0 / size[0]
        frame = cutout(frame, spr, M_of(t, 1.0, center(spr), (bx, by), k, rot=brot, jit=160, amp=0.8, sy=bflap), shadow=shadow(t, 0.3, 1.5))

    # 撕开的纸屑
    for x, y, rot_, size, vis in collage.bits(t, T_TEAR + 0.25, c_hole, n=30, seed=4, life=1.4):
        pts = [(x + size * math.cos(math.radians(rot_ + a)), y + size * 0.6 * math.sin(math.radians(rot_ + a))) for a in (0, 110, 200, 290)]
        frame = draw.fill_poly(frame, np.eye(3)[:2], pts, np.array([0.55, 0.50, 0.45], np.float32), vis)
    # 晴天的彩纸屑
    for x, y, rot_, size, vis in collage.bits(t, T_SUN + 0.1, to_screen(t, 1.0, (960, 320)), n=44, seed=11, life=2.0, speed=(200, 800), gravity=700):
        col = [(0.35, 0.78, 1.0), (0.45, 0.9, 0.55), (0.95, 0.65, 0.35), (0.6, 0.45, 0.95)][int(x + y) % 4]
        pts = [(x + size * math.cos(math.radians(rot_ + a)), y + size * 0.6 * math.sin(math.radians(rot_ + a))) for a in (0, 110, 200, 290)]
        frame = draw.fill_poly(frame, np.eye(3)[:2], pts, np.array(col, np.float32), vis)

    # 落款
    if S["title"] is not None and t >= T_TITLE:
        spr = S["title"]
        anc, size = assets.bbox_anchor(spr)
        s_, dy, vis, shs = slap(t, T_TITLE, drop=120, overshoot=0.14, dur=0.4)
        k = 1150.0 / size[0]
        frame = cutout(frame, spr, M_of(t, 1.0, center(spr), (700, 140 + dy), k * s_, rot=-2, jit=170, amp=0.6), alpha=vis, shadow=shadow(t, 0.4, shs))

    frame = post.grain(post.vignette(frame, 0.22), t, amount=0.008)
    return post.fade(frame, t, DUR, 0.5, 0.7)


def umbrella_state(t):
    """(x, y, 旋转, 是否显示)：抛上去，落到右边地上，躺着。"""
    if t < T_TOSS:
        return 0, 0, 0, False
    d = t - T_TOSS
    if d < 0.9:
        u = d / 0.9
        x = FOOT[0] - 40 + 820 * ease_out(u)
        y = FOOT[1] - 250 + (-450 * math.sin(math.pi * u)) + 260 * u
        return x, y, 720 * u, True
    dd = t - (T_TOSS + 0.9)
    y = FOOT[1] - 40 + (-30 * abs(math.sin(dd * 8)) * math.exp(-dd * 3))
    return FOOT[0] + 780, y, 68 + 4 * math.exp(-dd * 3) * math.sin(dd * 9), t < T_BIRD


def bird_state(t):
    """纸鸟：从伞变来，绕小人盘旋，再飞出画面。返回 (x, y, 旋转, 缩放, 扇翅)"""
    if t < T_BIRD:
        return 0, 0, 0, 0.0, 1.0
    d = t - T_BIRD
    k = ease_back(prog(t, T_BIRD, T_BIRD + 0.35), 2.2)
    flap = 1.0 if int(core.q(t, 12) * 12) % 2 == 0 else 0.7
    if d < 1.6:
        a = d / 1.6 * 2 * math.pi
        x = 1300 + 380 * math.cos(a) - 250 * (1 - math.cos(a)) * 0.0
        y = 400 - 120 * math.sin(a)
        return FOOT[0] + 780 - (FOOT[0] + 780 - x) * ease_out(prog(d, 0, 0.5)), FOOT[1] - 40 + (y - FOOT[1] + 40) * ease_out(prog(d, 0, 0.5)), 12 * math.cos(a), 0.9 * k + 0.1, flap
    u = prog(t, T_BIRD + 1.6, T_BIRD + 3.2)
    x = 1680 + 500 * ease_in(u)
    y = 400 - 420 * ease_in(u)
    return x, y, -15 * u, 0.9 * (1 - 0.3 * u), flap


def camera_matrix(t):
    zoom, pan = cam(t)
    return STAGE.matrix(zoom, pan, 1.0)[:2], zoom
