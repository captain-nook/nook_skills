"""《一只猫的一天》：扁平动态图形（风格卡 05），纯代码，17 秒，120 BPM，每拍一变。

一个橙色圆点落下弹成一只猫，然后用信息图讲它的一天：睡 16 小时、盯着墙 47 分钟、
把杯子推下桌 3 次、凌晨三点跑酷 1 次（每晚）、理你 0 次——除非你开罐头，变成 ∞。

布局统一：左边是图形，右边是标签 + 大数字 + 单位。每个数据一种底色，圆形擦除转场，剪辑点都在拍上。
"""
import math
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import cv2
import numpy as np

from nookanim import mg, post
from nookanim.core import clamp, ease_in, ease_in_out, ease_out, lerp, prog, spring
from nookanim.mg import hexc, paste, pop, text

W, H, FPS, DUR = 1920, 1080, 24, 17.0
B = mg.Beat(120)
SHOTS = [
    (B(0), "S01 开场"),
    (B(8), "S02 睡觉"),
    (B(13), "S03 盯墙"),
    (B(17), "S04 推杯子"),
    (B(21), "S05 跑酷"),
    (B(25), "S06 理你"),
    (B(30), "S07 收尾"),
]

CREAM, TEAL, PINK, YELLOW, NAVY, ORANGE = map(hexc, ("#FFF4E0", "#2EC4B6", "#FF6B8B", "#FFD23F", "#1B1F3B", "#FF8A3D"))
INK, WHITE = hexc("#2B2D42"), (255, 255, 255)
CAT, STRIPE, EAR, NOSE = hexc("#FF8A3D"), hexc("#D9622B"), hexc("#FFB3C1"), hexc("#FF6B8B")
CUP = hexc("#4D96FF")

GX, GY = 600, 560        # 左侧图形中心
TX = 1180                # 右侧文字左边线


# ---------------------------------------------------------------- 猫

def _P(c, s, p):
    return (int(round(c[0] + p[0] * s)), int(round(c[1] + p[1] * s)))


def cat(img, c, s=1.0, eyes="open", look=(0, 0), tail=0.0, squash=0.0, back=False):
    """几何猫。eyes: open / wide / closed / happy / heart / wink / blink；squash 0..1 趴成一团（睡觉）；back=True 背对。"""
    P = lambda p: _P(c, s, p)
    R = lambda r: max(1, int(round(r * s)))
    hy = 60 * squash                                     # 趴下时头往下沉
    # 尾巴
    pts = [P((110 + 70 * math.sin(u * 2.2) * (0.6 + 0.4 * math.sin(tail)) + 40 * u, 200 - 150 * u + 30 * math.sin(tail + u * 3)))
           for u in np.linspace(0, 1, 16)]
    cv2.polylines(img, [np.array(pts, np.int32)], False, CAT, R(34), cv2.LINE_AA)
    cv2.circle(img, pts[-1], R(17), STRIPE, -1, cv2.LINE_AA)
    # 身体
    cv2.ellipse(img, P((0, 170 + 20 * squash)), (R(125 + 70 * squash), R(115 - 45 * squash)), 0, 0, 360, CAT, -1, cv2.LINE_AA)
    if not back:
        cv2.ellipse(img, P((0, 190 + 15 * squash)), (R(60 + 30 * squash), R(70 - 30 * squash)), 0, 0, 360, hexc("#FFE3C8"), -1, cv2.LINE_AA)
        for dx in (-50, 50):
            cv2.ellipse(img, P((dx, 275 - 30 * squash)), (R(34), R(20)), 0, 0, 360, WHITE, -1, cv2.LINE_AA)
    # 头与耳朵
    for sx in (-1, 1):
        ear = [P((sx * 100, -40 + hy)), P((sx * 85, -160 + hy)), P((sx * 20, -100 + hy))]
        cv2.fillPoly(img, [np.array(ear, np.int32)], CAT, cv2.LINE_AA)
        if not back:
            inner = [P((sx * 82, -60 + hy)), P((sx * 78, -130 + hy)), P((sx * 38, -95 + hy))]
            cv2.fillPoly(img, [np.array(inner, np.int32)], EAR, cv2.LINE_AA)
    cv2.circle(img, P((0, hy)), R(115), CAT, -1, cv2.LINE_AA)
    for dx in (-26, 0, 26):
        cv2.line(img, P((dx, -110 + hy)), P((dx * 0.8, -78 + hy)), STRIPE, R(10), cv2.LINE_AA)
    if back:
        return
    # 脸
    lx, ly = look[0] * 10, look[1] * 10
    for i, sx in enumerate((-1, 1)):
        e = (sx * 45, -5 + hy)
        kind = eyes
        if eyes == "wink":
            kind = "happy" if sx > 0 else "open"
        if kind == "open":
            cv2.ellipse(img, P((e[0] + lx, e[1] + ly)), (R(15), R(22)), 0, 0, 360, INK, -1, cv2.LINE_AA)
            cv2.circle(img, P((e[0] + lx + 5, e[1] + ly - 8)), R(5), WHITE, -1, cv2.LINE_AA)
        elif kind == "wide":
            cv2.circle(img, P(e), R(34), WHITE, -1, cv2.LINE_AA)
            cv2.circle(img, P((e[0] + lx * 1.5, e[1] + ly * 1.5)), R(20), INK, -1, cv2.LINE_AA)
            cv2.circle(img, P((e[0] + lx * 1.5 + 6, e[1] + ly * 1.5 - 7)), R(6), WHITE, -1, cv2.LINE_AA)
        elif kind in ("closed", "blink"):
            cv2.ellipse(img, P(e), (R(18), R(10)), 0, 0, 180, INK, R(7), cv2.LINE_AA)
        elif kind == "happy":
            cv2.ellipse(img, P((e[0], e[1] + 8)), (R(18), R(14)), 0, 180, 360, INK, R(7), cv2.LINE_AA)
        elif kind == "heart":
            heart(img, P(e), 26 * s, NOSE)
    cv2.fillPoly(img, [np.array([P((-12, 30 + hy)), P((12, 30 + hy)), P((0, 42 + hy))], np.int32)], NOSE, cv2.LINE_AA)
    for sx in (-1, 1):
        cv2.ellipse(img, P((sx * 12, 48 + hy)), (R(12), R(10)), 0, 0, 180, INK, R(5), cv2.LINE_AA)
        for k in (-1, 0, 1):
            cv2.line(img, P((sx * 60, 35 + hy + k * 14)), P((sx * 135, 28 + hy + k * 26)), INK, R(4), cv2.LINE_AA)


def heart(img, c, r, col):
    t = np.linspace(0, 2 * math.pi, 40)
    x = 16 * np.sin(t) ** 3
    y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    pts = np.stack([c[0] + x * r / 16, c[1] + y * r / 16], 1).astype(np.int32)
    cv2.fillPoly(img, [pts], col, cv2.LINE_AA)


def cup(img, c, s=1.0, rot=0.0):
    a = math.radians(rot)
    R = lambda p: (int(c[0] + (p[0] * math.cos(a) - p[1] * math.sin(a)) * s), int(c[1] + (p[0] * math.sin(a) + p[1] * math.cos(a)) * s))
    body = [R(p) for p in [(-45, -90), (45, -90), (38, 0), (-38, 0)]]
    cv2.fillPoly(img, [np.array(body, np.int32)], CUP, cv2.LINE_AA)
    cv2.ellipse(img, R((52, -48)), (int(24 * s), int(28 * s)), rot, -90, 90, CUP, int(12 * s), cv2.LINE_AA)
    cv2.line(img, R((-40, -70)), R((40, -70)), WHITE, max(1, int(7 * s)), cv2.LINE_AA)


def paw(img, c, s=1.0):
    cv2.ellipse(img, c, (int(110 * s), int(60 * s)), 0, 0, 360, CAT, -1, cv2.LINE_AA)
    cv2.circle(img, (int(c[0] - 70 * s), c[1]), int(38 * s), WHITE, -1, cv2.LINE_AA)
    for dy in (-28, 0, 28):
        cv2.circle(img, (int(c[0] - 98 * s), int(c[1] + dy * s)), int(9 * s), NOSE, -1, cv2.LINE_AA)
    cv2.circle(img, (int(c[0] - 68 * s), c[1]), int(16 * s), NOSE, -1, cv2.LINE_AA)


def can(img, c, s=1.0):
    x, y = c
    mg.rrect(img, x - 70 * s, y - 60 * s, x + 70 * s, y + 60 * s, 14 * s, hexc("#C0C5D1"))
    mg.rrect(img, x - 70 * s, y - 30 * s, x + 70 * s, y + 30 * s, 6 * s, hexc("#4D96FF"))
    paste(img, text("罐头", int(36 * s), WHITE), (x, y), 1.0)
    cv2.ellipse(img, (int(x), int(y - 60 * s)), (int(70 * s), int(16 * s)), 0, 0, 360, hexc("#E5E8EF"), -1, cv2.LINE_AA)


# ---------------------------------------------------------------- 右侧数据块

def stat(img, t, b0, label, value, unit, col, extra=None, vscale=1.0):
    """右侧：标签（第 b0 拍）→ 大数字（b0+0.5）→ 单位（b0+1）。value 可以是字符串。"""
    k = pop(t, B(b0))
    paste(img, text(label, 64, col), (TX, 330), k, anchor=(0, 0.5))
    k2 = pop(t, B(b0 + 0.5), 0.3, 3.0) * vscale
    v = text(str(value), 300, col)
    paste(img, v, (TX, 560), k2, anchor=(0, 0.5))
    ku = pop(t, B(b0 + 1))
    paste(img, text(unit, 72, col), (TX + v.shape[1] * k2 + 10, 640), ku, anchor=(0, 0.5))
    if extra:
        paste(img, text(extra[0], 44, col), (TX, 790), pop(t, B(extra[1])), anchor=(0, 0.5))


# ---------------------------------------------------------------- 各段

def intro(img, t):
    img[:] = CREAM
    c = (960, 470)
    if t < B(2):
        # 圆点落下、弹一下
        y = lerp(-80, c[1] + 60, ease_in(prog(t, B(0), B(1))))
        sq = spring(t - B(1), 3, 6) * 0.35 if t > B(1) else 0.0
        r = 70
        cv2.ellipse(img, (c[0], int(y + r * sq)), (int(r * (1 + sq)), int(r * (1 - sq))), 0, 0, 360, CAT, -1, cv2.LINE_AA)
        return
    # 圆点长成猫
    s = 0.25 + 0.95 * ease_out(prog(t, B(2), B(2.6))) + 0.04 * spring(t - B(2.6), 3, 5)
    eyes = "closed" if B(3) <= t < B(3.25) else "open"
    cat(img, c, s * 0.9, eyes=eyes, tail=t * 3, look=(0.3 * math.sin(t * 2), 0))
    paste(img, text("一只猫的一天", 110, INK), (960, 880), pop(t, B(4)))
    paste(img, text("（数据来源：我家猫，仅供参考）", 40, hexc("#8D8FA3")), (960, 975), pop(t, B(6)))


def s_sleep(img, t):
    img[:] = TEAL
    k = pop(t, B(8))
    track = tuple(int(0.8 * v + 0.2 * 255) for v in TEAL)
    cv2.circle(img, (GX, GY), int(250 * k), track, int(40 * k) + 1, cv2.LINE_AA)
    mg.arc(img, (GX, GY), 250, 0, 240 * ease_in_out(prog(t, B(8.5), B(10.5))), WHITE, 40)
    cat(img, (GX, GY - 60), 0.75 * k, eyes="closed", squash=1.0, tail=t * 1.5)
    for i, b in enumerate((9, 10, 11, 12)):
        dt = t - B(b)
        if 0 <= dt < 1.2:
            paste(img, text("Z", 70 + 15 * i, WHITE), (GX + 150 + 30 * dt * 60 / 60, GY - 180 - 120 * dt), pop(t, B(b)) * (1 - prog(dt, 0.8, 1.2)), rot=-15)
    stat(img, t, 8, "睡觉", mg.count(t, B(8.5), B(10.5), 0, 16), "小时", WHITE, ("= 一天的三分之二", 11))


def s_wall(img, t):
    img[:] = PINK
    k = pop(t, B(13))
    if k > 0:
        mg.rrect(img, GX - 300 * k, GY - 330 * k, GX + 300 * k, GY + 120 * k, 24, WHITE)
    look = (0.6 * math.sin(t * 9) * (t > B(15)), -1)
    cat(img, (GX, GY + 260), 0.62 * k, eyes="wide", look=look, tail=t * 5)
    q = pop(t, B(15))
    paste(img, text("?", 200, PINK), (GX, GY - 110), q, rot=10 * math.sin(t * 6))
    stat(img, t, 13, "盯着墙", mg.count(t, B(13.5), B(15.5), 0, 47), "分钟", WHITE, ("墙上什么都没有", 16))


def s_cups(img, t):
    img[:] = YELLOW
    top = GY + 80
    cv2.rectangle(img, (0, top), (GX + 160, top + 28), hexc("#8B5E3C"), -1, cv2.LINE_AA)
    n = 0
    for k in range(3):
        b = 17 + k
        appear, push, fall = B(b), B(b + 0.45), B(b + 0.55)
        if t < appear or t > B(b + 1.4):
            continue
        s = pop(t, appear)
        x, y, rot = GX + 60, top, 0.0
        if t > push:
            x += 100 * ease_out(prog(t, push, fall))
        if t > fall:
            dt = t - fall
            x += 250 * dt
            y += 0.5 * 5000 * dt * dt
            rot = 400 * dt
        cup(img, (x, y), 1.1 * s, rot)
        # 猫爪从左边伸进来推
        pk = prog(t, B(b + 0.2), push) - prog(t, fall, B(b + 0.8))
        if pk > 0:
            paw(img, (int(GX - 240 + 230 * ease_out(pk)), int(top - 50)), 1.0)
    for k in range(3):
        if t >= B(17 + k + 0.6):
            n = k + 1
        tb = B(17 + k + 0.85)
        if tb <= t < tb + 0.4:                 # 摔碎："啪！"
            paste(img, text("啪！", 120, INK), (GX + 300 + 60 * k, 930), pop(t, tb, 0.15, 3.0) * mg.out(t, tb + 0.28, 0.12), rot=-8 + 8 * k)
    vs = 1.0 + 0.25 * max(0.0, spring(t - B(17 + max(n - 1, 0) + 0.6), 3, 7)) if n else 1.0
    stat(img, t, 17, "把杯子推下桌", n, "次", INK, ("而且看着你推", 20), vscale=vs)


def s_parkour(img, t):
    img[:] = NAVY
    # 星星
    rng = np.random.default_rng(7)
    for _ in range(40):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.7)
        a = 0.5 + 0.5 * math.sin(t * 3 + x)
        cv2.circle(img, (int(x), int(y)), 2 + int(2 * a), (200, 200, 230), -1, cv2.LINE_AA)
    colon = ":" if int(t * 2) % 2 == 0 else " "
    paste(img, text(f"03{colon}00", 110, YELLOW), (GX, 220), pop(t, B(21)))
    floor = 900
    cv2.line(img, (0, floor), (W, floor), (80, 80, 120), 6, cv2.LINE_AA)
    # 猫在屋里来回冲：左→右、右→左、跳起、落地
    segs = [(B(21.5), B(22.1), (-200, floor - 110), (2100, floor - 110)),
            (B(22.5), B(23.1), (2100, floor - 110), (-200, floor - 110)),
            (B(23.5), B(24.0), (-200, floor - 110), (GX, floor - 110))]
    for t0, t1, p0, p1 in segs:
        if t0 <= t <= t1 + 0.2:
            for g in range(5):                    # 残影
                u = clamp(prog(t - g * 0.03, t0, t1))
                x = lerp(p0[0], p1[0], u if t1 != B(24.0) else ease_out(u))
                y = p0[1] - (260 * math.sin(math.pi * u) if t0 == B(23.5) else 0)
                ghost = img.copy()
                cat(ghost, (x, y), 0.45, eyes="wide", tail=t * 12)
                a = 1.0 if g == 0 else 0.25 / g
                cv2.addWeighted(ghost, a, img, 1 - a, 0, img)
    if t > B(24.0) + 0.2:
        cat(img, (GX, floor - 110), 0.45, eyes="wide", tail=t * 8, look=(math.sin(t * 20), 0))
    stat(img, t, 21, "凌晨三点跑酷", 1, "次", WHITE, ("每晚", 24))


def s_ignore(img, t):
    img[:] = CREAM
    turned = t >= B(27)
    k = pop(t, B(25))
    if not turned:
        cat(img, (GX, GY - 40), 0.9 * k, back=True, tail=t * 4)
    else:
        s = 0.9 * (1 + 0.08 * spring(t - B(27), 3, 6))
        cat(img, (GX, GY - 40), s, eyes="heart", tail=t * 10)
    cp = pop(t, B(26.5))
    if cp > 0:
        can(img, (GX + 250, GY + 240), 0.9 * cp)
    # 数字：0 砸下来；开罐头后翻成 ∞
    if not turned:
        vs = 1 + 2.0 * (1 - ease_out(prog(t, B(25.5), B(25.5) + 0.18))) if t >= B(25.5) else 0
        paste(img, text("理你", 64, INK), (TX, 330), pop(t, B(25)), anchor=(0, 0.5))
        paste(img, text("0", 300, INK), (TX, 560), vs, anchor=(0, 0.5))
        paste(img, text("次", 72, INK), (TX + 200, 640), pop(t, B(26)), anchor=(0, 0.5))
    else:
        fl = abs(math.cos(math.pi * clamp(prog(t, B(27), B(27.35)) * 0.5 + 0.5))) if t < B(27.35) else 1.0
        paste(img, text("理你", 64, INK), (TX, 330), 1.0, anchor=(0, 0.5))
        spr = text("∞", 300, PINK)
        sq = cv2.resize(spr, (spr.shape[1], max(1, int(spr.shape[0] * fl))))
        paste(img, sq, (TX, 560), 1.0, anchor=(0, 0.5))
        paste(img, text("次", 72, INK), (TX + spr.shape[1] + 10, 640), 1.0, anchor=(0, 0.5))
        paste(img, text("除非你开罐头", 44, INK), (TX, 790), pop(t, B(27.25)), anchor=(0, 0.5))


def ending(img, t):
    img[:] = TEAL
    eyes = "open"
    if B(32) <= t < B(32.25):
        eyes = "blink"
    if t >= B(33):
        eyes = "wink"
    k = pop(t, B(30))
    cat(img, (960, 420), 0.95 * k, eyes=eyes, tail=t * 3)
    paste(img, text("一只猫的一天", 110, WHITE), (960, 830), pop(t, B(30.5)))
    paste(img, text("船长的角落", 44, hexc("#E6FFFB")), (960, 935), pop(t, B(31.5)))


SEGMENTS = [(B(0), intro, None), (B(8), s_sleep, (TEAL, (960, 470))), (B(13), s_wall, (PINK, (W, 540))),
            (B(17), s_cups, (YELLOW, (0, 540))), (B(21), s_parkour, None), (B(25), s_ignore, (CREAM, (GX, 540))),
            (B(30), ending, (TEAL, (GX + 250, GY + 240)))]
WIPE = 0.5    # 转场提前半拍开始


def render(t):
    img = np.zeros((H, W, 3), np.uint8)
    idx = max(i for i, (t0, _, _) in enumerate(SEGMENTS) if t >= t0)
    SEGMENTS[idx][1](img, t)
    # 下一段的圆形擦除：在切点前半拍开始扩出
    if idx + 1 < len(SEGMENTS):
        t_next, _, wp = SEGMENTS[idx + 1]
        if wp and t >= t_next - WIPE:
            mg.wipe(img, t, t_next - WIPE, wp[0], wp[1], dur=WIPE)
        if SEGMENTS[idx + 1][1] is s_parkour and t >= t_next - 0.06:
            img[:] = 255     # 硬切到夜里：先白闪一下
    frame = img.astype(np.float32) / 255
    return post.fade(frame, t, DUR, 0.05, 0.5)
