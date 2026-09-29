"""《最后一块披萨》：火柴人风格（风格卡 04），纯代码，16 秒。

两个火柴人同时走向桌上最后一块披萨，四目相对，画面切成西部对决：牛仔帽落下、风滚草滚过、
眼神特写、手指抽动；两人同时扑出，空中定格——一只鸽子飞进来叼走披萨；两人头撞头倒地，
鸽子落在吊灯上慢慢吃完，打了个嗝。两人坐起来，一起抬头看它。

世界坐标 = 1920×1080 的屏幕，地面 FLOOR=900，桌子居中。镜头用 stick.Cam，特写是硬切放大。
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

from nookanim import assets, config, draw, fx, post, stick
from nookanim.core import clamp, ease, ease_in, ease_in_out, ease_out, keys, lerp, prog, spring
from nookanim.stick import Cam, disc, fill, fk, line, poly

W, H, FPS, DUR = 1920, 1080, 24, 16.0
SHOTS = [
    (0.0, "S01 入场"),
    (2.3, "S02 发现"),
    (4.2, "S03 对决"),
    (6.2, "S04 眼神"),
    (8.5, "S05 扑"),
    (10.9, "S06 鸽子"),
]

FLOOR = 900
TABLE = dict(x0=800, x1=1120, top=745)
SLICE_AT = (960.0, 734.0)
LAMP = (960.0, 300.0)       # 灯罩顶面中心
RIG = stick.Rig()

# 颜色（BGR）
BG = (238, 243, 247)
FLOOR_COL = (214, 224, 232)
WOOD = (70, 110, 160)
CHEESE = (70, 200, 250)
CRUST = (60, 130, 200)
PEPPER = (50, 60, 200)
HAT_COL = (40, 85, 140)
HAT_BAND = (25, 45, 70)
PIGEON = (160, 150, 150)
PIGEON_D = (110, 100, 100)
STAR_COL = (60, 210, 255)

BANG = assets.symbol_sprite("!", color=(216, 91, 30))
BURP = assets.symbol_sprite("嗝", color=(90, 90, 90), size=150)
_rng = np.random.default_rng(3)
TUMBLE = [(_rng.uniform(0, 6.28), _rng.uniform(0, 6.28)) for _ in range(26)]


# ---------------------------------------------------------------- 时间轴

T_STOP = 2.2
T_WEST0, T_WEST1 = 4.2, 10.0
T_CROUCH, T_LUNGE, T_FREEZE0, T_FREEZE1 = 8.5, 9.0, 9.35, 9.9
T_BONK = 10.0
T_GRAB = 9.62
T_LAND = 11.4
BITES = (12.0, 12.45, 12.9, 13.35)
T_BURP = 13.8
T_SIT = 14.2


def pose_A(t):
    """左边的火柴人（面朝右）。返回 (关节点, 表情参数)。B 是 A 的镜像加一点时间差。"""
    ex = dict(eyes="dot", mouth="none", brow=None, look=(0, 0))
    grounded = True
    if t < T_STOP:
        x = -120 + 730 * prog(t, 0, T_STOP)
        pose, bob = stick.walk(x / 85.0)
        hip = (x, 0)
        ex["mouth"] = "smile"
    elif t < T_CROUCH:
        x = 610
        settle = spring(t - T_STOP, 2.5, 7) * 6
        base = dict(lean=settle)
        if t >= 2.4:
            base = stick.pose_keys(t, [(2.4, {}), (2.7, dict(head=22)), (3.1, dict(head=22)), (3.3, dict(head=0))])
            ex["look"] = (0.6, -0.8) if t < 3.2 else (1, 0)
            ex["mouth"] = "o" if 2.7 < t < 3.2 else "flat"
        if t >= 3.4:
            ex["eyes"] = "wide" if t < 3.9 else "squint"
            ex["brow"] = None if t < 3.9 else "angry"
        if t >= T_WEST0:
            # 对决站姿：腿岔开，手悬在胯边
            base = stick.pose_keys(t, [(T_WEST0, {}), (T_WEST0 + 0.3, dict(lth=16, lsh=12, rth=-16, rsh=-12, lua=-24, lfa=-10, rua=24, rfa=12))])
            ex.update(eyes="squint", brow="angry", mouth="flat")
        pose, bob, hip = base, 0, (x, 0)
    elif t < T_LUNGE:
        k = ease_out(prog(t, T_CROUCH, T_CROUCH + 0.35))
        pose = stick.lerp_pose(dict(lth=16, lsh=12, rth=-16, rsh=-12, lua=-24, lfa=-10, rua=24, rfa=12),
                               dict(lean=38, head=-30, lth=80, lsh=-18, rth=58, rsh=-38, lua=-80, lfa=-50, rua=-65, rfa=-35), k)
        pose["lean"] += 2 * math.sin(t * 40) * (t > T_CROUCH + 0.35)   # 蓄力时微微发抖
        hip, bob = (610 - 25 * k, 0), 0
        ex.update(eyes="squint", brow="angry", mouth="flat")
    else:
        grounded = False
        LUNGE = dict(lean=86, head=-70, lua=95, lfa=90, rua=85, rfa=80, lth=-72, lsh=-86, rth=-98, rsh=-104)
        FALL = dict(lean=-130, head=25, lth=70, lsh=30, rth=110, rsh=80, lua=160, lfa=200, rua=-150, rfa=-190)
        LIE = dict(lean=-90, head=-8, lth=90, lsh=92, rth=84, rsh=100, lua=-115, lfa=-100, rua=-70, rfa=-60)
        SIT = dict(lean=-12, head=-40, lth=88, lsh=92, rth=80, rsh=84, lua=-35, lfa=-40, rua=-30, rfa=-35)
        if t < T_FREEZE0:
            k = ease_out(prog(t, T_LUNGE, T_FREEZE0))
            pose = stick.lerp_pose(dict(lean=38, head=-30, lth=80, lsh=-18, rth=58, rsh=-38, lua=-80, lfa=-50, rua=-65, rfa=-35), LUNGE, k)
            hip = (lerp(585, 690, k), lerp(FLOOR - 120, 650, k))
            ex.update(eyes="wide", brow="angry", mouth="o")
        elif t < T_FREEZE1:                           # 空中定格
            pose, hip = LUNGE, (690, 650)
            ex.update(eyes="wide", brow="angry", mouth="o", look=(0, 0))
            if t > T_GRAB - 0.1:
                ex["look"] = (0.2, 1)                  # 眼珠跟着鸽子往下看
        elif t < T_BONK:
            k = ease_in(prog(t, T_FREEZE1, T_BONK))
            pose, hip = LUNGE, (lerp(690, 758, k), 650)
            ex.update(eyes="wide", mouth="o")
        elif t < 10.9:
            u = prog(t, T_BONK, 10.75)
            pose = stick.lerp_pose(LUNGE, FALL, ease_out(prog(t, T_BONK, 10.3))) if t < 10.45 else stick.lerp_pose(FALL, LIE, ease(prog(t, 10.45, 10.8)))
            y = 650 + (FLOOR - 14 - 650) * (u ** 2) - 60 * math.sin(math.pi * min(1, u * 1.3))
            hip = (lerp(758, 690, ease_out(u)), min(FLOOR - 14, y))
            ex.update(eyes="x", mouth="o")
        else:
            k = ease_out(prog(t, T_SIT, T_SIT + 0.45))
            pose = stick.lerp_pose(LIE, SIT, k)
            hip = (690, FLOOR - 14 + spring(t - 10.8, 3, 6) * -8)
            ex.update(eyes="spiral" if t < T_SIT else "dot", mouth="flat" if t >= T_SIT else "none",
                      look=(0.4, 1) if t >= T_SIT else (0, 0))
        bob = 0
    J = fk(RIG, (hip[0], hip[1] + bob), pose, 1)
    if grounded:
        low = max(J["lft"][1], J["rft"][1]) + RIG.width * 0.9
        for n in list(J):
            if isinstance(J[n], np.ndarray) and J[n].shape == (2,) and n != "up":
                J[n] = J[n] + np.array([0, FLOOR - low])
    if T_LUNGE + 0.12 < t < T_BONK:                   # 双手伸向披萨
        for s, off in (("r", 0), ("l", -14)):
            J = stick.reach(RIG, J, s, (SLICE_AT[0] - 14 + off, SLICE_AT[1] - 16), bend=1)
    return J, ex


def mirror(J):
    out = {}
    for n, v in J.items():
        if isinstance(v, np.ndarray) and v.shape == (2,) and n != "up":
            out[n] = np.array([W - v[0], v[1]])
        else:
            out[n] = v
    out["facing"] = -J["facing"]
    return out


def pose_B(t):
    # B 比 A 晚一点点反应，动作不完全对称，看起来更像两个人
    lag = 0.08 if t < T_LUNGE else 0.0
    J, ex = pose_A(max(0.0, t - lag))
    return mirror(J), ex


# ---------------------------------------------------------------- 道具

def draw_bg(img, cam, t):
    west = 0.0
    if T_WEST0 <= t < T_WEST1:
        west = 1.0
    if west:
        # 夕阳：上橙下黄的渐变 + 大太阳
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        top, bot = np.array([60, 130, 235], np.float32), np.array([140, 215, 250], np.float32)
        img[:] = (top * (1 - yy) + bot * yy).astype(np.uint8)
        disc(img, cam, (960, 560), 330, (170, 230, 255))
        cv2.rectangle(img, (0, cam.p((0, FLOOR))[1]), (W, H), (95, 160, 210), -1)
    else:
        img[:] = BG
        cv2.rectangle(img, (0, cam.p((0, FLOOR))[1]), (W, H), FLOOR_COL, -1)
    line(img, cam, (-2000, FLOOR), (4000, FLOOR), 6, stick.BLACK)
    return west


def draw_table(img, cam):
    x0, x1, top = TABLE["x0"], TABLE["x1"], TABLE["top"]
    fill(img, cam, [(x0, top), (x1, top), (x1, top + 18), (x0, top + 18)], WOOD)
    poly(img, cam, [(x0, top), (x1, top), (x1, top + 18), (x0, top + 18)], 5, closed=True)
    for lx in (x0 + 40, x1 - 40):
        line(img, cam, (lx, top + 18), (lx, FLOOR), 9)
    # 盘子
    cv2.ellipse(img, cam.p((960, top - 4)), (int(92 * cam.z), int(13 * cam.z)), 0, 0, 360, (250, 250, 250), -1, cv2.LINE_AA)
    cv2.ellipse(img, cam.p((960, top - 4)), (int(92 * cam.z), int(13 * cam.z)), 0, 0, 360, stick.BLACK, cam.w(4), cv2.LINE_AA)


def slice_poly(L=110.0, bite=0.0):
    """披萨片（局部坐标：尖在原点，饼边在 x=L），bite 为被吃掉的比例（从尖开始）。"""
    b = L * bite
    w0 = 26 * bite
    return [(b, -w0 * 0.55), (L, -26), (L + 6, 0), (L, 14), (b, w0 * 0.3)]


def draw_slice(img, cam, at, rot=0.0, sc=1.0, bite=0.0, flip=1):
    if bite >= 0.98:
        return
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def tf(p):
        x, y = p[0] * flip * sc, p[1] * sc
        return (at[0] + c * x - s * y, at[1] + s * x + c * y)

    P = [tf(p) for p in slice_poly(bite=bite)]
    fill(img, cam, P, CHEESE)
    for px, py in ((45, -5), (75, -12), (85, 6)):
        if px > 110 * bite + 8:
            cv2.ellipse(img, cam.p(tf((px, py))), (max(1, int(8 * sc * cam.z)), max(1, int(5 * sc * cam.z))), rot, 0, 360, PEPPER, -1, cv2.LINE_AA)
    poly(img, cam, [tf((110, -26)), tf((116, 0)), tf((110, 14))], 12 * sc, CRUST)
    poly(img, cam, P, 3.5 * sc, closed=True)


def draw_lamp(img, cam, t, swing=0.0):
    top = (960, -50)
    a = math.radians(swing)
    rot = lambda p: (top[0] + (p[0] - top[0]) * math.cos(a) - (p[1] - top[1]) * math.sin(a),
                     top[1] + (p[0] - top[0]) * math.sin(a) + (p[1] - top[1]) * math.cos(a))
    line(img, cam, top, rot(LAMP), 4)
    shade = [rot(p) for p in [(900, 300), (1020, 300), (1060, 350), (860, 350)]]
    fill(img, cam, shade, (80, 120, 60))
    poly(img, cam, shade, 5, closed=True)
    disc(img, cam, rot((960, 356)), 13, (180, 240, 255))
    return rot


def draw_hat(img, cam, anchor, rot=0.0, sc=1.0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    tf = lambda p: (anchor[0] + (c * p[0] - s * p[1]) * sc, anchor[1] + (s * p[0] + c * p[1]) * sc)
    brim = [tf((70 * math.cos(u), -8 + 12 * math.sin(u) - 10 * abs(math.cos(u)) ** 3)) for u in np.linspace(0, 2 * math.pi, 28)]
    crown = [tf(p) for p in [(-36, -10), (-30, -58), (-10, -64), (0, -54), (10, -64), (30, -58), (36, -10)]]
    fill(img, cam, brim, HAT_COL)
    fill(img, cam, crown, HAT_COL)
    poly(img, cam, [tf((-34, -18)), tf((34, -18))], 8 * sc, HAT_BAND)
    poly(img, cam, brim, 4 * sc, closed=True)
    poly(img, cam, crown, 4 * sc)


def hat_anchor(J):
    """帽子按头的朝向戴在头顶（扑出时身体是平的，头是抬着的）。"""
    a = math.radians(J["head_ang"])
    return J["head"] + np.array([math.sin(a) * J["facing"], -math.cos(a)]) * RIG.head * 0.62


def draw_hair_B(img, cam, J):
    """B 头顶三根翘毛，用来区分两个人。"""
    hc = J["head"]
    for k in (-0.35, 0.0, 0.35):
        ang = math.radians(J["head_ang"]) + k
        base = hc + np.array([math.sin(ang), -math.cos(ang)]) * RIG.head
        tip = hc + np.array([math.sin(ang + 0.15), -math.cos(ang + 0.15)]) * (RIG.head + 20)
        line(img, cam, base, tip, 5)


def draw_curl_A(img, cam, J):
    """A 头顶一个小卷。"""
    hc = J["head"]
    ang = math.radians(J["head_ang"])
    base = hc + np.array([math.sin(ang), -math.cos(ang)]) * RIG.head
    pts = [base + np.array([math.sin(ang), -math.cos(ang)]) * (8 * u) + np.array([math.cos(u * 4), math.sin(u * 4)]) * 7 * u
           for u in np.linspace(0, 1.6, 14)]
    poly(img, cam, pts, 4.5)


def draw_tumbleweed(img, cam, t):
    p = prog(t, 4.6, 6.4)
    if not 0 < p < 1:
        return
    x = lerp(2150, -250, p)
    r = 46
    y = FLOOR - r - 30 * abs(math.sin(p * 9))
    ang = -(x / r)
    c = np.array([x, y])
    for a0, a1 in TUMBLE:
        u = np.linspace(a0, a0 + 2.2, 10)
        pts = [c + np.array([math.cos(v + ang), math.sin(v + ang)]) * r * (0.55 + 0.45 * math.sin(v * 1.7 + a1)) for v in u]
        poly(img, cam, pts, 3, (60, 100, 140))


def draw_pigeon(img, cam, at, facing=-1, flap=None, t=0.0, peck=0.0, eye="dot", sc=1.35):
    """鸽子：灰身、深色翅膀、彩色颈、橙眼、粉脚。flap=None 表示停着（翅膀收起），否则 0..1 为扑扇相位。"""
    f = facing
    X = lambda p: (at[0] + p[0] * f * sc, at[1] + p[1] * sc)
    body = [X((42 * math.cos(u), -34 + 26 * math.sin(u))) for u in np.linspace(0, 2 * math.pi, 26)]
    tail = [X(p) for p in [(-30, -40), (-78, -52), (-80, -36), (-30, -26)]]
    fill(img, cam, tail, PIGEON_D)
    poly(img, cam, tail, 4, closed=True)
    if flap is not None:
        a = math.sin(flap * 2 * math.pi)
        wing_b = [X(p) for p in [(-5, -50), (-40, -50 - 70 * a), (-70, -45 - 60 * a), (10, -46)]]
        fill(img, cam, wing_b, PIGEON_D)
        poly(img, cam, wing_b, 4, closed=True)
    fill(img, cam, body, PIGEON)
    poly(img, cam, body, 4.5, closed=True)
    hx, hy = 34, -64 + 10 * peck
    neck = [X(p) for p in [(18, -52), (hx - 6, hy + 4), (hx + 10, hy + 10), (32, -40)]]
    fill(img, cam, neck, (130, 110, 120))
    fill(img, cam, [X(p) for p in [(20, -48), (hx - 2, hy + 8), (30, -40)]], (120, 150, 80))
    disc(img, cam, X((hx, hy)), 17, PIGEON, stick.BLACK, 4.5)
    fill(img, cam, [X(p) for p in [(hx + 14, hy - 2), (hx + 30, hy + 3 + 4 * peck), (hx + 14, hy + 6)]], (120, 160, 230))
    if eye == "closed":
        line(img, cam, X((hx + 3, hy - 3)), X((hx + 11, hy - 3)), 3)
    else:
        disc(img, cam, X((hx + 6, hy - 4)), 6, (60, 150, 250))
        disc(img, cam, X((hx + 7, hy - 4)), 3, stick.BLACK)
    if flap is None:
        wing = [X(p) for p in [(-28, -48), (18, -52), (26, -36), (-24, -26)]]
        fill(img, cam, wing, PIGEON_D)
        poly(img, cam, wing, 4, closed=True)
        for dx in (-8, 8):
            line(img, cam, X((dx, -10)), X((dx, 0)), 4, (150, 150, 235))
    else:
        a = math.sin(flap * 2 * math.pi)
        wing = [X(p) for p in [(-10, -48), (-30, -48 - 80 * a), (-60, -40 - 70 * a), (15, -42)]]
        fill(img, cam, wing, PIGEON)
        poly(img, cam, wing, 4, closed=True)
    return X((hx + 26, hy + 5))     # 嘴尖


def pigeon_state(t):
    """鸽子的位置、朝向、扑扇相位、啄食。"""
    if t < 9.42:
        return None
    if t < T_GRAB:
        p = ease_in(prog(t, 9.42, T_GRAB))
        return dict(at=(lerp(1500, 1000, p), lerp(160, 770, p)), f=-1, flap=t * 6, peck=0.8)
    if t < 10.05:
        p = ease_out(prog(t, T_GRAB, 10.05))
        return dict(at=(lerp(1000, 380, p), lerp(770, 120, p)), f=-1, flap=t * 6, peck=0)
    if t < 10.9:
        return None
    if t < T_LAND:
        p = ease_out(prog(t, 10.9, T_LAND))
        return dict(at=(lerp(-150, LAMP[0], p), lerp(80, LAMP[1], p) - 40 * math.sin(math.pi * p)), f=1, flap=t * 6, peck=0)
    peck = 0.0
    for b in BITES:
        peck = max(peck, max(0.0, 1 - abs(t - b) / 0.12))
    return dict(at=LAMP, f=-1, flap=None, peck=peck)


def slice_bite(t):
    return sum(0.22 for b in BITES if t >= b + 0.05)


def draw_stars(img, cam, center, t, n=3, r=(55, 18)):
    for i in range(n):
        a = t * 5 + i * 2 * math.pi / n
        c = (center[0] + r[0] * math.cos(a), center[1] + r[1] * math.sin(a))
        pts = [(c[0] + (13 if j % 2 == 0 else 5) * math.cos(j * math.pi / 5 - math.pi / 2),
                c[1] + (13 if j % 2 == 0 else 5) * math.sin(j * math.pi / 5 - math.pi / 2)) for j in range(10)]
        fill(img, cam, pts, STAR_COL)
        poly(img, cam, pts, 2.5, closed=True)


def draw_speed(img, cam, J, back=1):
    f = J["facing"]
    for j, dy in enumerate((-40, -10, 20, 50)):
        y = J["hip"][1] + dy
        x = J["hip"][0] - f * (70 + 30 * (j % 2))
        line(img, cam, (x, y), (x - f * 150, y), 5, (120, 120, 120))


def draw_crumbs(img, cam, t):
    for i, b in enumerate(BITES):
        for k in range(3):
            dt = t - b - 0.05
            if dt < 0:
                continue
            x = LAMP[0] - 40 + 12 * k - 8 * i
            y = min(TABLE["top"] - 4, LAMP[1] - 40 + 0.5 * 1800 * dt * dt)
            disc(img, cam, (x, y), 4, CRUST)


# ---------------------------------------------------------------- 镜头

def camera(t):
    if 6.2 <= t < 6.9:              # A 的眼神特写
        J, _ = pose_A(t)
        return Cam(J["head"][0] + 10, J["head"][1] + 4, 4.2)
    if 6.9 <= t < 7.6:              # B 的眼神特写
        J, _ = pose_B(t)
        return Cam(J["head"][0] - 10, J["head"][1] + 4, 4.2)
    if 7.6 <= t < 8.05:             # A 的手
        J, _ = pose_A(t)
        return Cam(J["rha"][0], J["rha"][1] - 10, 4.0)
    if 8.05 <= t < 8.5:             # B 的手
        J, _ = pose_B(t)
        return Cam(J["rha"][0], J["rha"][1] - 10, 4.0)
    if T_FREEZE0 <= t < T_FREEZE1:  # 定格时轻推近
        z = 1.25 + 0.3 * ease_out(prog(t, T_FREEZE0, T_FREEZE0 + 0.15))
        return Cam(960, 660, z)
    if 2.3 <= t < 4.2:
        z = 1.25 + 0.15 * ease_in_out(prog(t, 2.3, 3.4))
        return Cam(960, 665, z)
    return Cam(960, 650, 1.25)


def camera_matrix(t):
    c = camera(t)
    return np.array([[c.z, 0, W / 2 - c.cx * c.z], [0, c.z, H / 2 - c.cy * c.z]], np.float32), c.z


# ---------------------------------------------------------------- 主渲染

def _fingers(t, seed):
    r = np.random.default_rng(seed + int(t * 24))
    return r.random(4)


def render(t):
    cam = camera(t)
    img = np.zeros((H, W, 3), np.uint8)
    west = draw_bg(img, cam, t)
    rot = draw_lamp(img, cam, t, swing=3.0 * spring(t - T_LAND, 1.2, 1.5) if t > T_LAND else 0.0)
    draw_table(img, cam)
    draw_crumbs(img, cam, t)

    ps = pigeon_state(t)
    # 披萨：盘子上 → 鸽子嘴里
    if t < T_GRAB:
        draw_slice(img, cam, (SLICE_AT[0] - 58, SLICE_AT[1]), rot=0)
        if t < T_WEST0:
            for k in range(3):   # 热气
                x = 930 + 30 * k
                pts = [(x + 8 * math.sin(u * 3 + t * 4 + k), 715 - 60 * u) for u in np.linspace(0, 1, 10)]
                poly(img, cam, pts, 3, (190, 190, 190))

    JA, exA = pose_A(t)
    JB, exB = pose_B(t)
    fingers = (7.6 <= t < 8.5)
    for J, ex, who in ((JA, exA, "A"), (JB, exB, "B")):
        if T_LUNGE < t < T_FREEZE0:
            draw_speed(img, cam, J)
        stick.figure(img, cam, RIG, J, fingers=_fingers(t, 1 if who == "A" else 2) if fingers else None)
        (draw_curl_A if who == "A" else draw_hair_B)(img, cam, J)
        stick.face(img, cam, RIG, J, **ex)
        # 牛仔帽：落下 → 戴着 → 撞头时飞走
        t_drop = T_WEST0 + (0.1 if who == "A" else 0.25)
        if t >= t_drop:
            anc = hat_anchor(J)
            if t < T_BONK:
                k = prog(t, t_drop, t_drop + 0.25)
                off = -500 * (1 - ease_in(k)) + (spring(t - t_drop - 0.25, 3, 6) * 10 if k >= 1 else 0)
                draw_hat(img, cam, (anc[0], anc[1] + off), rot=J["head_ang"] * J["facing"])
            else:
                dt = t - T_BONK
                s = -1 if who == "A" else 1
                pos = (anc[0] + s * 380 * dt, anc[1] - 700 * dt + 0.5 * 2200 * dt * dt)
                if pos[1] < H + 200:
                    draw_hat(img, cam, pos, rot=s * 400 * dt)
        if t >= T_BONK:
            draw_stars(img, cam, J["head"] + np.array([0, -RIG.head - 20]), t)

    if ps is not None:
        beak = draw_pigeon(img, cam, ps["at"], ps["f"], ps["flap"], t, ps["peck"],
                           eye="closed" if abs(t - T_BURP) < 0.25 or t > 15.0 else "dot")
        if t >= T_GRAB:
            draw_slice(img, cam, beak, rot=15 * ps["f"], sc=0.6, bite=slice_bite(t), flip=ps["f"])

    # 撞头：一圈冲击线
    if T_BONK <= t < T_BONK + 0.25:
        c = (960, 600)
        k = prog(t, T_BONK, T_BONK + 0.25)
        for i in range(10):
            a = i * math.pi / 5
            line(img, cam, (c[0] + math.cos(a) * (40 + 90 * k), c[1] + math.sin(a) * (40 + 90 * k)),
                 (c[0] + math.cos(a) * (70 + 120 * k), c[1] + math.sin(a) * (70 + 120 * k)), 7, (60, 200, 255))

    draw_tumbleweed(img, cam, t)

    frame = img.astype(np.float32) / 255
    A, _ = camera_matrix(t)
    for J in (JA, JB):
        frame = fx.pop(frame, A, BANG, (BANG.shape[1] / 2, BANG.shape[0]), J["head"] + np.array([0, -RIG.head - 18]), t, 3.4, 0.45, life=0.9)
    if ps is not None and t > T_LAND:
        frame = fx.pop(frame, A, BURP, (BURP.shape[1] / 2, BURP.shape[0]), (LAMP[0] - 90, LAMP[1] - 120), t, T_BURP, 0.75, life=1.0)

    # 西部段：上下电影黑边
    if west:
        bar = int(110 * min(ease_out(prog(t, T_WEST0, T_WEST0 + 0.3)), 1 - ease_in(prog(t, T_WEST1 - 0.3, T_WEST1))))
        frame[:bar] = 0.05
        frame[H - bar:] = 0.05
    # 定格：画面轻微去色，时间停了只有鸽子在动
    if T_FREEZE0 <= t < T_FREEZE1:
        g = frame.mean(2, keepdims=True)
        frame = frame * 0.6 + g * 0.4

    if t > 14.9:
        frame = draw_caption(frame, t)
    frame = post.grain(frame, t, amount=0.006)
    return post.fade(frame, t, DUR, 0.25, 0.6)


_CAP = None


def draw_caption(frame, t):
    global _CAP
    if _CAP is None:
        img = Image.new("L", (360, 60), 0)
        ImageDraw.Draw(img).text((360, 30), "船长的角落", font=ImageFont.truetype(config.FONT_UI, 34), fill=255, anchor="rm")
        _CAP = np.asarray(img).astype(np.float32) / 255
    a = _CAP * 0.7 * prog(t, 14.9, 15.3)
    h, w = a.shape
    y, x = H - 90, W - 60 - w
    frame[y:y + h, x:x + w] *= (1 - a[:, :, None] * 0.8)
    return frame
