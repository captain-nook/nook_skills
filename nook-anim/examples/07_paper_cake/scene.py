"""《蛋糕保卫战》：纸片定格风格，Qwen Image 2.1 出图 + 代码合成，18.5 秒。
纸片小厨师端着生日蛋糕走过厨房桌面，一只纸片小老鼠一路偷偷跟着。厨师放下蛋糕回头一看，老鼠当场定住；
他一走，老鼠爬上盘子把蛋糕啃得只剩盘子。厨师带着火柴回来，看见空盘子和盘子上站得笔直的"蜡烛"，
点着了火柴——
角色 12fps 定格并带纸片的微颤，镜头与特效 24fps。
"""
import math
import pathlib

import cv2
import numpy as np

from nookanim import assets, config, core, draw, fx, geom, post
from nookanim.core import clamp, ease, ease_back, ease_in, ease_in_out, ease_out, keys, prog, spring

W, H, FPS, DUR = 1920, 1080, 24, 18.5
SHOTS = [(0, "S01 端蛋糕"), (3.7, "S02 放下"), (5.0, "S03 回头"), (6.6, "S04 走开"), (8.0, "S05 偷吃"),
         (10.8, "S06 回来"), (12.0, "S07 空盘子"), (13.2, "S08 点蜡烛"), (14.6, "S09 惨叫"), (15.8, "S10 落款")]
D = pathlib.Path(__file__).parent / "素材"

S = {p.stem: assets.load(p) for p in D.glob("*.png")}
PLATE = S["table"][:, :, :3]
CAM = geom.Camera((PLATE.shape[1], PLATE.shape[0]), (W, H))
FOOT_Y = 965                 # 桌面上角色脚底线（底图坐标）
PLATE_C = (1590, 806)        # 盘面中心
MX = 1420                    # 站成蜡烛的老鼠的位置
CHEF_H = 640                 # 厨师母版高度（底图像素）
MOUSE_H = 300

_a, _sz = assets.bbox_anchor(S["chef"])
K_CHEF = CHEF_H / _sz[1]
_a, _sz = assets.bbox_anchor(S["mouse"])
K_MOUSE = MOUSE_H / _sz[1]
_a, _sz = assets.bbox_anchor(S["cake"])
CAKE_W = 250
K_CAKE = CAKE_W / _sz[0]

INK = np.array([40, 35, 30], np.float32) / 255


# ---------------- 摄像机 ----------------
def camera_matrix(t):
    cx = keys(t, [(0, 1180), (3.7, 1330), (8.0, 1420), (10.8, 1560), (14.4, 1590), (18.5, 1590)], ease_in_out)
    cw = keys(t, [(0, 2250), (3.7, 2200), (5.0, 2100), (6.6, 2200), (8.0, 1950), (10.4, 1950), (12.0, 2150),
                  (13.2, 1750), (14.6, 1700), (15.5, 2200), (18.5, 2200)], ease_in_out)
    sh = (0.0, 0.0)
    if 12.0 <= t < 12.5:                                     # 厨师大叫时震一下
        sh = geom.shake(t, 4.0)
    if 14.6 <= t < 15.0:
        sh = geom.shake(t, 5.0)
    return CAM.matrix(cx, 610, cw, sh)


# ---------------- 纸片木偶 ----------------
def put(frame, A, spr, at, k, anchor=None, sx=1.0, sy=1.0, rot=0.0, flip=False, alpha=1.0):
    """按脚底中点摆放；sx、sy 做挤压拉伸，rot 绕脚底旋转。"""
    if anchor is None:
        anchor, _ = assets.bbox_anchor(spr)
    if flip:
        spr = spr[:, ::-1]
        anchor = (spr.shape[1] - 1 - anchor[0], anchor[1])
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    M = np.array([[c * k * sx, -s * k * sy, 0], [s * k * sx, c * k * sy, 0], [0, 0, 1]])
    M[:2, 2] = np.array(at) - M[:2, :2] @ np.array(anchor)
    Hh, Ww = frame.shape[:2]
    lay = cv2.warpAffine(spr, (geom.A3(A) @ M)[:2].astype(np.float32),
                         (Ww, Hh), flags=cv2.INTER_LINEAR, borderValue=0)
    if alpha < 1:
        lay = lay * alpha
    return draw.over(frame, lay)


def wobble(t):
    """纸片定格的微颤：每格换一次角度和位置。"""
    n = int(t * 12)
    return (((n * 37) % 5) - 2) * 0.55, (((n * 53) % 3) - 1) * 1.2


def bounce(tq, rate, amp):
    return -amp * abs(math.sin(tq * math.pi * rate))


def shadow_at(frame, A, x, w, st=0.42, y=FOOT_Y):
    return draw.shadow(frame, A, (x, y + 6), w, st, 0.16)


# ---------------- 角色状态 ----------------
def chef_state(t):
    """(姿势, x, y偏移, 旋转, sx, sy, 朝左) 或 None"""
    tq = core.q(t)
    if t < 3.7:                                              # 端着蛋糕走进来
        x = -160 + (1000 + 160) * (t / 3.7)
        return "chef_carry", x, bounce(tq, 4.4, 26), 2.2 * math.sin(tq * math.pi * 4.4), 1, 1, False
    if t < 4.0:                                              # 站住
        u = (t - 3.7) / 0.3
        return "chef_carry", 1000, 0, 0, 1 + 0.05 * u, 1 - 0.04 * u, False
    if t < 5.0:                                              # 张开双臂"哒哒"
        d = t - 4.0
        return "chef_ta", 1000, -34 * ease_out(prog(d, 0, 0.16)) * (1 - ease_in(prog(d, 0.16, 0.34))), 0, 1 + 0.05 * spring(d - 0.34, 4, 6), 1 - 0.05 * spring(d - 0.34, 4, 6), False
    if t < 6.6:                                              # 回头怀疑
        d = t - 5.0
        return "chef_look", 1000, 0, 1.5 * math.sin(tq * 3), 1, 1, False
    if t < 8.0:                                              # 一步一回头地走开（朝右）
        u = prog(t, 6.6, 8.0)
        return "chef_look", 1000 + 1500 * ease_in(u), bounce(tq, 4, 20), 2.5 * math.sin(tq * math.pi * 4), 1, 1, True
    if t < 10.8:
        return None
    if t < 12.0:                                             # 拿着火柴回来
        u = prog(t, 10.8, 12.0)
        return "chef_match", 2800 - 900 * ease_out(u), bounce(tq, 4.6, 24) * (1 - u ** 3), 2 * math.sin(tq * math.pi * 4.6), 1, 1, False
    if t < 13.2:                                             # 发现盘子空了
        d = t - 12.0
        return "chef_shock", 1900, -30 * ease_out(prog(d, 0, 0.12)) * (1 - ease_in(prog(d, 0.12, 0.28))), 0, 1 + 0.06 * spring(d - 0.28, 4, 6), 1 - 0.06 * spring(d - 0.28, 4, 6), False
    if t < 14.6:                                             # 举着火柴走向"蜡烛"
        u = prog(t, 13.2, 14.4)
        return "chef_match", 1900 - 250 * ease_in_out(u), bounce(tq, 4, 14) * (u < 1), 1.5 * math.sin(tq * math.pi * 4), 1, 1, False
    if t < 15.6:
        d = t - 14.6
        return "chef_shock", 1650, -30 * ease_out(prog(d, 0, 0.12)) * (1 - ease_in(prog(d, 0.12, 0.28))), 0, 1, 1, False
    d = t - 15.6
    return "chef_ta", 1650, -20 * abs(math.sin(min(d, 1.6) * 5)) * (d < 1.6), 0, 1, 1, False


def mouse_state(t):
    """(姿势, x, y, 旋转, sx, sy, 朝左, 层) y 是脚底的底图 y。"""
    tq = core.q(t)
    if t < 1.6:
        return None
    if t < 5.0:                                              # 蹑手蹑脚跟着
        u = prog(t, 1.6, 5.0)
        return "mouse_sneak", -120 + 850 * u, FOOT_Y + bounce(tq, 3.0, 12), 0, 1, 1, False, 0
    if t < 7.0:                                              # 被发现：定住
        d = t - 5.0
        return "mouse_freeze", 730, FOOT_Y, 0, 1, 1, False, 0
    if t < 8.0:                                              # 继续偷偷靠近盘子
        u = prog(t, 7.0, 8.0)
        return "mouse_sneak", 730 + 560 * u, FOOT_Y + bounce(tq, 3.6, 12), 0, 1, 1, False, 0
    if t < 8.5:                                              # 跳上盘子
        u = prog(t, 8.0, 8.5)
        x = 1290 + 130 * u
        y = FOOT_Y + (PLATE_C[1] + 6 - FOOT_Y) * ease_in_out(u) - 150 * math.sin(math.pi * u)
        return "mouse_sneak", x, y, -12 * math.sin(math.pi * u), 1, 1, False, 1
    if t < 10.3:                                             # 啃蛋糕
        d = t - 8.5
        chew = 1 + 0.05 * math.sin(tq * 30)
        return "mouse_sneak", 1425 + 18 * (d / 1.8), PLATE_C[1] + 6, 6, chew, 1 / chew, False, 1
    if t < 10.9:                                             # 吃饱了
        d = t - 10.3
        return "mouse_full", 1500, PLATE_C[1] + 8, 0, 1 + 0.06 * spring(d, 4, 6), 1 - 0.06 * spring(d, 4, 6), False, 1
    if t < 11.7:
        return "mouse_full", 1500, PLATE_C[1] + 8, 0, 1, 1, False, 1
    if t < 14.6:                                             # 立刻站成一根"蜡烛"
        d = t - 11.7
        return "mouse_freeze", MX, PLATE_C[1] + 8, 0, 1, 1, False, 1
    # 惨叫着飞出画面
    u = prog(t, 14.6, 16.0)
    x, y = fly_xy(u)
    return "mouse_yelp", x, y, -18 * math.sin(u * 9), 1, 1, False, 1


def fly_xy(u):
    """被烫到的老鼠：先蹿起，再一路往左边逃出画面。"""
    x = MX - 1700 * ease_in(u) - 60 * u
    y = PLATE_C[1] + 8 - 520 * math.sin(math.pi * min(u * 1.6, 1)) ** 0.9 + 300 * max(0, u - 0.6)
    return x, y


# ---------------- 小部件 ----------------
def _flame_sprite():
    n = 256
    img = np.zeros((n, n, 4), np.float32)
    pts = np.array([[128, 10], [190, 120], [200, 180], [128, 246], [56, 180], [66, 120]], np.int32)
    cv2.fillPoly(img, [pts], (0.10, 0.45, 1.0, 1.0), cv2.LINE_AA)            # BGR 橙红
    cv2.fillPoly(img, [((pts - 128) * 0.62 + [128, 158]).astype(np.int32)], (0.25, 0.85, 1.0, 1.0), cv2.LINE_AA)   # 黄
    cv2.fillPoly(img, [((pts - 128) * 0.30 + [128, 190]).astype(np.int32)], (0.85, 0.98, 1.0, 1.0), cv2.LINE_AA)   # 淡黄芯
    cv2.polylines(img, [pts], True, (0.05, 0.10, 0.35, 1.0), 6, cv2.LINE_AA)
    img[:, :, :3] *= img[:, :, 3:4]
    return img


FLAME = _flame_sprite()
QMARK = assets.symbol_sprite("?", color=(40, 60, 210), stroke=(255, 255, 255))
BANG = assets.symbol_sprite("!", color=(40, 60, 210), stroke=(255, 255, 255))
STAR = assets.star_sprite()

BITES = [(0.02, 0.62, 0.26), (0.20, 0.32, 0.27), (0.34, 0.62, 0.28), (0.55, 0.45, 0.30), (0.56, 0.10, 0.32), (0.85, 0.5, 0.55)]
BITE_T = [8.9, 9.25, 9.6, 9.95, 10.2, 10.3]


def cake_sprite(t):
    """按已经咬过的口数，把蛋糕的透明通道挖掉几个圆口（底板不挖）。"""
    spr = S["cake"].copy()
    anc, size = assets.bbox_anchor(spr, 0, 0)
    x0, y0 = anc
    w, h = size
    board = y0 + h * 0.84
    m = np.ones(spr.shape[:2], np.float32)
    for (bx, by, br), bt in zip(BITES, BITE_T):
        if t >= bt:
            cx, cy, r = x0 + bx * w, y0 + by * h, br * w * 0.5
            cv2.circle(m, (int(cx), int(cy)), int(r), 0.0, -1, cv2.LINE_AA)
    m2 = np.ones_like(m)
    m2[int(board):, :] = 1.0
    keep = m.copy()
    keep[int(board):, :] = 1.0
    spr[:, :, 3] *= keep
    spr[:, :, :3] *= keep[:, :, None]
    return spr


def crumbs(frame, A, t, t0, origin, n=9, seed=1):
    dt = t - t0
    if not 0 < dt < 0.7:
        return frame
    rng = np.random.default_rng(seed)
    ov = frame.copy()
    for _ in range(n):
        a = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
        sp = rng.uniform(120, 300)
        x = origin[0] + math.cos(a) * sp * dt
        y = origin[1] + math.sin(a) * sp * dt + 800 * dt * dt
        p = geom.A3(A) @ np.array([x, y, 1.0])
        cv2.circle(ov, (int(p[0]), int(p[1])), int(rng.uniform(4, 8) * A[0, 0] * 1.4), (0.35, 0.72, 0.93) if rng.random() < 0.6 else (0.55, 0.45, 0.95), -1, cv2.LINE_AA)
    a_ = 1 - dt / 0.7
    return cv2.addWeighted(ov, a_, frame, 1 - a_, 0)


def sparkle(frame, A, spr, at, t, t0, sc, life=0.7):
    return fx.pop(frame, A, spr, (spr.shape[1] / 2, spr.shape[0] / 2), at, t, t0, sc, life)


def cherry(frame, A, t):
    return frame


# ---------------- 渲染 ----------------
def render(t):
    A, s = camera_matrix(t)
    frame = CAM.render_plate(PLATE, A)
    wx, wy = wobble(t)

    # ---- 蛋糕（放下后出现，被咬到没有）----
    cake_on = t >= 4.05
    cake_x = PLATE_C[0]
    if cake_on and t < 10.4:
        d = t - 4.05
        drop = 90 * (1 - ease_out(prog(d, 0, 0.16)))
        sq = 1 + 0.10 * spring(d - 0.16, 4, 6)
        spr = cake_sprite(t)
        anc, _ = assets.bbox_anchor(spr)
        frame = shadow_at(frame, A, cake_x, 230, 0.35, PLATE_C[1] + 14)
        frame = put(frame, A, spr, (cake_x, PLATE_C[1] + 12 - drop), K_CAKE, anchor=anc, sx=sq if d < 0.6 else 1, sy=(2 - sq) if d < 0.6 else 1)
    # 只剩银色底板
    if t >= 10.4:
        spr = S["cake"].copy()
        anc, size = assets.bbox_anchor(spr, 0, 0)
        keep = np.zeros(spr.shape[:2], np.float32)
        keep[int(anc[1] + size[1] * 0.84):, :] = 1
        spr[:, :, 3] *= keep
        spr[:, :, :3] *= keep[:, :, None]
        anc2, _ = assets.bbox_anchor(S["cake"])
        frame = put(frame, A, spr, (cake_x, PLATE_C[1] + 12), K_CAKE, anchor=anc2)

    # ---- 角色 ----
    ms = mouse_state(t)
    cs = chef_state(t)

    def draw_mouse(frame):
        if ms is None:
            return frame
        name, x, y, rot, sx, sy, flip, layer = ms
        spr = S[name]
        if layer == 0:
            frame = shadow_at(frame, A, x, 120, 0.40, y)
        anc, _ = assets.bbox_anchor(spr)
        return put(frame, A, spr, (x + wx * 0.6, y), K_MOUSE, anchor=anc, sx=sx, sy=sy, rot=rot + wx * 0.5, flip=flip)

    def draw_chef(frame):
        if cs is None:
            return frame
        name, x, dy, rot, sx, sy, flip = cs
        spr = S[name]
        frame = shadow_at(frame, A, x, 230, 0.42, FOOT_Y)
        anc, _ = assets.bbox_anchor(spr)
        return put(frame, A, spr, (x + wx, FOOT_Y + dy + wy), K_CHEF, anchor=anc, sx=sx, sy=sy, rot=rot + wx * 0.6, flip=flip)

    # 老鼠在盘子上时先画（在厨师后面）；地面上的老鼠和厨师按脚底 y 排序，同一条线上老鼠在前
    frame = draw_chef(frame)
    frame = draw_mouse(frame)

    # ---- 特效 ----
    star_anc = (STAR.shape[1] / 2, STAR.shape[0] / 2)
    # ta-da 星光
    if 4.0 <= t < 5.0:
        for i, (dx, dy) in enumerate(((-210, -560), (200, -600), (-60, -690))):
            frame = fx.pop(frame, A, STAR, star_anc, (1000 + dx, FOOT_Y + dy), t, 4.06 + i * 0.07, 0.8, 0.7, 30)
    # 回头的问号
    frame = fx.pop(frame, A, QMARK, (QMARK.shape[1] / 2, QMARK.shape[0] / 2), (1030, FOOT_Y - 700), t, 5.15, 0.55, 1.2, 25)
    # 老鼠被发现：冷汗
    if 5.0 <= t < 6.5:
        d = t - 5.0
        p = (760, FOOT_Y - 300 + 60 * d)
        frame = draw.fill_poly(frame, A, [(p[0], p[1] - 34), (p[0] + 18, p[1] + 10), (p[0], p[1] + 26), (p[0] - 18, p[1] + 10)], (0.95, 0.6, 0.25), 0.9 * (1 - prog(d, 1.0, 1.5)))
    # 啃食：碎屑与哼哧
    for i, bt in enumerate(BITE_T[:5]):
        frame = crumbs(frame, A, t, bt, (PLATE_C[0] - 120 + i * 60, PLATE_C[1] - 120), 8, seed=10 + i)
    # 厨师震惊线
    if 12.0 <= t < 12.9:
        d = t - 12.0
        frame = fx.pop(frame, A, BANG, (BANG.shape[1] / 2, BANG.shape[0] / 2), (1930, FOOT_Y - 760), t, 12.0, 0.7, 0.9, 20)
        frame = fx.pop(frame, A, BANG, (BANG.shape[1] / 2, BANG.shape[0] / 2), (2080, FOOT_Y - 700), t, 12.12, 0.5, 0.9, 20)
    # 火柴上的火焰：跟着厨师的手
    if 12.9 <= t < 14.65 or (14.6 <= t < 15.4):
        base = (1750, FOOT_Y)
        if cs is not None and cs[0] in ("chef_match", "chef_shock"):
            spr = S["chef_match"]
            anc, size = assets.bbox_anchor(spr)
            tip = draw.sprite_point((anc[0] - size[0] * 0.5 + size[0] * 0.03, anc[1] - size[1] * 0.60), anc, (cs[1] + wx, FOOT_Y + cs[2] + wy), K_CHEF)
            if cs[0] == "chef_match" and t >= 12.9:
                grow = ease_back(prog(t, 12.9, 13.2), 2.0)
                fl = 1 + 0.12 * math.sin(core.q(t, 24) * 40)
                fw = 100 * grow * fl
                frame = draw.place(frame, A, FLAME, (128, 246), (tip[0], tip[1] + 6), fw / 256, rot=5 * math.sin(t * 30))
    # 点着"蜡烛"：火苗跳到老鼠头上
    if 14.3 <= t < 14.9:
        u = prog(t, 14.3, 14.6)
        frame = draw.place(frame, A, FLAME, (128, 246), (MX, PLATE_C[1] - 290 + 40 * (1 - u)), 0.5 * ease_back(u, 2.0) + 0.02, rot=5 * math.sin(t * 30))
    if 14.6 <= t < 16.4:                                     # 屁股冒火的拖尾
        for i in range(6):
            tt = t - i * 0.07
            if tt >= 14.6:
                x, y = fly_xy(prog(tt, 14.6, 16.0))
                frame = draw.place(frame, A, FLAME, (128, 246), (x + 60, y - 60), 0.4 * (1 - i / 7), rot=10 * math.sin(t * 25 + i))
    # 惨叫
    if 14.6 <= t < 15.6:
        frame = fx.pop(frame, A, BANG, (BANG.shape[1] / 2, BANG.shape[0] / 2), (1650, 330), t, 14.62, 0.9, 1.0, 40)

    # ---- 落款：千问出的纸片剪字 ----
    if t >= 16.0 and "title" in S:
        spr = S["title"]
        anc, size = assets.bbox_anchor(spr, 0.5, 0.5)
        drop = 130 * (1 - ease_out(prog(t, 16.0, 16.35)))
        k = ease_back(prog(t, 16.0, 16.4), 2.2)
        M = np.array([[1300.0 / size[0] * k, 0, 0], [0, 1300.0 / size[0] * k, 0], [0, 0, 1]])
        M[:2, 2] = np.array([960, 200 + drop + 5 * math.sin(core.q(t) * 5)]) - M[:2, :2] @ np.array(anc)
        Hh, Ww = frame.shape[:2]
        lay = cv2.warpAffine(spr, M[:2].astype(np.float32), (Ww, Hh), flags=cv2.INTER_LINEAR, borderValue=0)
        sh = cv2.GaussianBlur(np.roll(np.roll(lay[:, :, 3], 12, 0), 6, 1), (0, 0), 10)
        frame = frame * (1 - 0.4 * sh[:, :, None])
        frame = draw.over(frame, lay)
    frame = post.grain(post.vignette(frame, 0.28), t, amount=0.010)
    return post.fade(frame, t, DUR, 0.5, 0.7)


def _unused_letter(frame, spr, at, sc, rot):
    anc = (spr.shape[1] / 2, spr.shape[0] / 2)
    return draw.place(frame, np.array([[1, 0, 0], [0, 1, 0]], np.float64), spr, anc, at, sc, rot)
