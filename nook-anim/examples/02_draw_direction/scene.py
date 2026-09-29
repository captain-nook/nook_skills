"""《画个方向》：手绘线稿风格，纯代码，20 秒。
小船长画出方向，铅笔把路画出来；铅笔跑偏冲向纸边，船长画边界把它弹回；一起抵达山顶灯塔。
世界坐标：场景图 5600×3150（桌面），纸 x 200–5400、y 1000–2500，地面线 GY=2000。
"""
import math

import numpy as np

from nookanim import assets, config, core, draw, fx, geom, post, sketch
from nookanim.core import clamp, ease, ease_back, ease_out, keys, lerp, prog, spring
from nookanim.sketch import Layer, circle

W, H, FPS, DUR = 1920, 1080, 24, 20.0
SHOTS = [(0, "S01 开场"), (3.0, "S02 定方向"), (6.5, "S03 执行"), (11.0, "S04 跑偏"), (14.0, "S05 抵达"), (17.3, "S06 收尾")]

# ---------------- 场景 ----------------
PW, PH = 5600, 3150
PX0, PX1, PY0, PY1 = 200, 5400, 1000, 2500
GY = 2000                      # 船长站的地面
RY = GY + 25                   # 路面（比人略靠近镜头）


def _plate():
    desk = np.ones((PH, PW, 3), np.float32) * np.array([62, 88, 112], np.float32) / 255   # 暖灰木桌
    yy, xx = np.mgrid[0:PH, 0:PW]
    desk *= (0.9 + 0.1 * np.sin(yy / 37.0 + np.sin(xx / 900.0) * 3))[:, :, None].astype(np.float32)   # 木纹
    sh = np.zeros((PH, PW), np.float32)
    sh[PY0 + 18:PY1 + 18, PX0 + 14:PX1 + 14] = 1
    import cv2
    sh = cv2.GaussianBlur(sh, (0, 0), 18)
    desk *= (1 - 0.45 * sh)[:, :, None]
    desk[PY0:PY1, PX0:PX1] = sketch.paper(PX1 - PX0, PY1 - PY0)
    return desk


PLATE = _plate()
CAM = geom.Camera((PW, PH), (W, H))
PAPER_COL = np.array(sketch.PAPER, np.float32) / 255
BLUE = np.array([216, 91, 30], np.float32) / 255
YELLOW = np.array([63, 210, 255], np.float32) / 255
PINK = np.array([180, 160, 245], np.float32) / 255
WOOD = np.array([150, 200, 238], np.float32) / 255
GRAPH = np.array([60, 58, 58], np.float32) / 255
SHIRT = np.array([55, 52, 50], np.float32) / 255
HAT = np.array([150, 70, 25], np.float32) / 255
METAL = np.array([170, 170, 165], np.float32) / 255
QMARK = assets.symbol_sprite("?")
BANG = assets.symbol_sprite("!")
NOTE = assets.symbol_sprite("♪", color=(30, 91, 216), font=str(config._FONTS / "seguisym.ttf"))   # 雅黑里没有 ♪
STAR = assets.star_sprite()


# ---------------- 路：铅笔笔尖的轨迹 ----------------
def hill_y(x):
    if 3900 <= x <= 4700:
        return GY - 260 * (0.5 - 0.5 * math.cos(2 * math.pi * (x - 3900) / 800))
    return GY


def _road():
    pts = []
    for x in np.arange(1180, 3150, 10):                     # 正路：轻微起伏，过桥处拱起
        y = RY + 8 * math.sin(x / 90)
        if 2030 <= x <= 2270:
            y -= 38 * math.sin(math.pi * (x - 2030) / 240)
        pts.append((x, y))
    seg1 = len(pts)
    for u in np.linspace(0, 1, 90)[1:]:                     # 跑偏：绕圈斜冲向纸的上缘
        x = 3150 + 330 * u + 70 * math.sin(4 * math.pi * u)
        y = RY - 760 * u + 80 * (math.cos(4 * math.pi * u) - 1)
        pts.append((x, y))
    hit = pts[-1]
    seg2 = len(pts)
    for u in np.linspace(0, 1, 50)[1:]:                     # 撞上边界弹回地面
        pts.append((lerp(hit[0], 3820, u), lerp(hit[1], RY, ease(u)) - 90 * math.sin(math.pi * u)))
    seg3 = len(pts)
    for x in np.arange(3830, 4301, 10):                     # 上山到山顶
        pts.append((x, hill_y(x) + 25))
    return np.array(pts), [seg1, seg2, seg3, len(pts)]


ROAD, SEGS = _road()
_L = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(ROAD, axis=0).T))])
SEG_S = [_L[i - 1] for i in SEGS]                           # 各段终点的弧长
BOUND_Y = ROAD[SEGS[1] - 1][1] - 6                          # 边界线高度（撞击点上方）


def road_s(t):
    """铅笔沿路走过的弧长。"""
    return keys(t, [(5.0, 0.0), (11.0, SEG_S[0]), (12.8, SEG_S[1]), (13.6, SEG_S[2]), (14.6, SEG_S[3])], fn=lambda x: x)


def road_point(s):
    return np.array([np.interp(s, _L, ROAD[:, 0]), np.interp(s, _L, ROAD[:, 1])])


def road_upto(s):
    n = int(np.searchsorted(_L, s))
    return [tuple(p) for p in ROAD[:n]] + [tuple(road_point(s))]


# ---------------- 角色：线稿小船长 ----------------
def captain(layers, A, t, x, y, facing=1, arms=(0, 0, 0, 0), walk=None, eyes="open", mouth="smile", look=0, k=1.0, bob=0.0):
    """arms=(左上臂, 左前臂, 右上臂, 右前臂) 角度，0 为自然下垂，正值向前抬。walk 为步态相位（None 为站立）。
    k 为逐笔画出进度（开场用）。layers = (纸白遮挡, 衬衫, 帽子, 黑线)。"""
    occ, shirt, hat, ink = layers
    f = facing
    hc = (x + 2 * f, y - 150 + bob)
    strokes, fills = [], []

    head = circle(hc, 32)
    strokes.append(("head", head, 3.2))
    hair = []
    for i, a in enumerate(np.linspace(185, 355, 13)):
        r = 32 if i % 2 == 0 else 45
        hair.append((hc[0] + r * math.cos(math.radians(a)), hc[1] + r * math.sin(math.radians(a))))
    strokes.append(("hair", hair, 3.0))
    crown = [(hc[0] - 24, hc[1] - 33), (hc[0] + 24, hc[1] - 33), (hc[0] + 18, hc[1] - 56), (hc[0] - 18, hc[1] - 56)]
    brim = [(hc[0] - 30 * f + 2, hc[1] - 31), (hc[0] + 36 * f, hc[1] - 28)]
    strokes += [("hat", crown + [crown[0]], 2.8), ("brim", brim, 3.2)]

    ex = [hc[0] - 11 + look * 4 + 3 * f, hc[0] + 11 + look * 4 + 3 * f]
    ey = hc[1] - 2
    if eyes == "open":
        eye_dots = [(ex[0], ey), (ex[1], ey)]
    else:
        eye_dots = [(ex[0], ey)] if eyes == "wink" else []
        if eyes == "closed":
            strokes.append(("eyeL", [(ex[0] - 5, ey), (ex[0] + 5, ey)], 2.4))
        strokes.append(("eyeR", [(ex[1] - 6, ey + 2), (ex[1], ey - 4), (ex[1] + 6, ey + 2)], 2.4))
    if mouth == "open":
        strokes.append(("mouth", circle((hc[0] + 4 * f, hc[1] + 13), 6, n=16), 2.4))
    else:
        strokes.append(("mouth", circle((hc[0] + 4 * f, hc[1] + 8), 9, 20, 160, 12), 2.4))

    neck, hip = (x, y - 118 + bob), (x, y - 62 + bob * 0.5)
    torso = [(neck[0] - 15, neck[1]), (neck[0] + 15, neck[1]), (hip[0] + 18, hip[1]), (hip[0] - 18, hip[1])]
    strokes.append(("torso", torso + [torso[0]], 3.0))

    def limb(root, a1, a2, l1, l2):
        d1 = (math.sin(math.radians(a1)) * f, math.cos(math.radians(a1)))
        j = (root[0] + d1[0] * l1, root[1] + d1[1] * l1)
        d2 = (math.sin(math.radians(a1 + a2)) * f, math.cos(math.radians(a1 + a2)))
        return [root, j, (j[0] + d2[0] * l2, j[1] + d2[1] * l2)]

    if walk is not None:
        sw = math.sin(walk * 2 * math.pi)
        arms = (arms[0] + 28 * sw, arms[1] + 20, arms[2] - 28 * sw, arms[3] + 20)
        legs = ((22 * sw, max(0, -30 * sw)), (-22 * sw, max(0, 30 * sw)))
    else:
        legs = ((6, 0), (-6, 0))
    armL = limb((neck[0] - 12 * f, neck[1] + 8), arms[0], arms[1], 27, 24)
    armR = limb((neck[0] + 12 * f, neck[1] + 8), arms[2], arms[3], 27, 24)
    legL = limb((hip[0] - 8, hip[1]), legs[0][0], legs[0][1], 30, 30)
    legR = limb((hip[0] + 8, hip[1]), legs[1][0], legs[1][1], 30, 30)
    strokes += [("armL", armL, 3.0), ("armR", armR, 3.0), ("legL", legL, 3.2), ("legR", legR, 3.2)]
    for lg in (legL, legR):
        strokes.append(("foot", circle((lg[-1][0] + 5 * f, lg[-1][1] - 2), 9, n=16, ry=4), 2.6))

    # 逐笔画出：k 按笔画顺序分配
    n = len(strokes)
    for i, (name, poly, w) in enumerate(strokes):
        ki = clamp(k * n - i)
        if ki <= 0:
            continue
        ink.stroke(A, draw.partial(poly, ki), w, t, seed=hash(name) % 997)
    if k >= 0.35:
        occ.fill(A, head, t, 1)
        for d in eye_dots:
            ink.dot(A, d, 4.2)
    if k >= 0.6:
        shirt.fill(A, torso, t, 2)
        hat.fill(A, crown, t, 3)
    return {"hand_R": np.array(armR[-1]), "head": np.array(hc)}


# ---------------- 角色：铅笔 ----------------
def pencil(layers, A, t, tip, tilt=0.0, sc=1.0, face=True):
    """竖立的铅笔，笔尖 tip 在下；tilt 为倾角（度）。layers = (纸白遮挡, 黄, 粉, 木, 石墨, 金属, 黑线)。"""
    occ, yel, pink, wood, graph, metal, ink = layers
    c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))

    def T(pts):
        return [(tip[0] + (x * c - y * s) * sc, tip[1] + (x * s + y * c) * sc) for x, y in pts]

    body = T([(-15, -34), (15, -34), (15, -104), (-15, -104)])
    cone = T([(0, 0), (15, -34), (-15, -34)])
    lead = T([(0, 0), (4.5, -10), (-4.5, -10)])
    band = T([(-15, -104), (15, -104), (15, -113), (-15, -113)])
    eraser = T([(-15, -113), (15, -113)] + [(15 * math.cos(a), -113 - 12 * math.sin(a)) for a in np.linspace(0, math.pi, 12)])
    yel.fill(A, body, t, 11)
    wood.fill(A, cone, t, 12)
    graph.fill(A, lead, t, 13)
    metal.fill(A, band, t, 14)
    pink.fill(A, eraser, t, 15)
    for nm, p in (("pb", body), ("pc", cone), ("pn", band), ("pe", eraser)):
        ink.stroke(A, p + [p[0]], 2.6 * sc, t, seed=hash(nm) % 997, taper=False)
    if face:
        e1, e2 = T([(-6, -76)])[0], T([(6, -76)])[0]
        ink.dot(A, e1, 3.4 * sc)
        ink.dot(A, e2, 3.4 * sc)
        ink.stroke(A, T([(-7, -64), (0, -59), (7, -64)]), 2.2 * sc, t, seed=77)
    return {"top": np.array(T([(0, -125)])[0])}


# ---------------- 沿路的物件（铅笔顺手画的） ----------------
def tree(x):
    b = (x, GY - 5)
    return [[(b[0] - 7, b[1]), (b[0] - 5, b[1] - 70)], [(b[0] + 7, b[1]), (b[0] + 5, b[1] - 70)],
            circle((b[0], b[1] - 110), 48, 120, 470, 60, ry=42)]


def bridge(x0, x1):
    river = [[(x0 + 30 + 18 * math.sin(i / 3), GY - 110 + i * 14) for i in range(18)],
             [(x1 - 30 + 18 * math.sin(i / 3 + 1), GY - 110 + i * 14) for i in range(18)]]
    arch = [(x, RY - 38 * math.sin(math.pi * (x - x0) / (x1 - x0)) + 22) for x in np.linspace(x0, x1, 30)]
    rail = [(x, RY - 38 * math.sin(math.pi * (x - x0) / (x1 - x0)) - 32) for x in np.linspace(x0, x1, 30)]
    posts = [[(x, RY - 38 * math.sin(math.pi * (x - x0) / (x1 - x0)) - 32), (x, RY - 38 * math.sin(math.pi * (x - x0) / (x1 - x0)))]
             for x in np.linspace(x0 + 20, x1 - 20, 6)]
    return river + [arch, rail] + posts


def house(x):
    b = GY - 5
    return [[(x - 70, b), (x - 70, b - 110), (x + 70, b - 110), (x + 70, b), (x - 70, b)],
            [(x - 90, b - 105), (x, b - 190), (x + 90, b - 105)],
            [(x - 18, b), (x - 18, b - 55), (x + 18, b - 55), (x + 18, b)],
            [(x + 32, b - 85), (x + 58, b - 85), (x + 58, b - 60), (x + 32, b - 60), (x + 32, b - 85)]]


LX = 4300


def lighthouse():
    b = hill_y(LX) - 2
    return [[(LX - 48, b), (LX - 30, b - 270), (LX + 30, b - 270), (LX + 48, b), (LX - 48, b)],
            [(LX - 43, b - 70), (LX + 43, b - 70)], [(LX - 38, b - 140), (LX + 38, b - 140)], [(LX - 34, b - 205), (LX + 34, b - 205)],
            [(LX - 36, b - 270), (LX - 36, b - 320), (LX + 36, b - 320), (LX + 36, b - 270)],
            [(LX - 48, b - 320), (LX, b - 365), (LX + 48, b - 320), (LX - 48, b - 320)],
            [(LX - 14, b), (LX - 14, b - 40), (LX + 14, b - 40), (LX + 14, b)]]


def hill():
    return [[(x, hill_y(x)) for x in np.arange(3880, 4721, 10)]]


PROPS = [(tree(1650), 7.2, 7.8), (bridge(2030, 2270), 8.2, 8.9), (house(2750), 9.5, 10.2), (hill(), 13.7, 14.4), (lighthouse(), 14.8, 16.0)]


def draw_strokes(layer, A, t, strokes, t0, t1, w=3.0, seed=0):
    """一组笔画在 [t0, t1] 内依次画出。"""
    n = len(strokes)
    k = prog(t, t0, t1) * n
    for i, st in enumerate(strokes):
        if k - i > 0:
            layer.stroke(A, draw.partial(st, clamp(k - i)), w, t, seed=seed + i)


# ---------------- 位置与姿态 ----------------
def bot_state(t):
    """铅笔：笔尖位置、倾角、缩放。"""
    tip0 = np.array(ROAD[0])
    if t < 4.4:
        return None
    if t < 5.0:
        pop = ease_back(prog(t, 4.4, 4.7), 2.5)
        return tip0, -18 * (1 - prog(t, 4.6, 4.95)) + 8 * spring(t - 4.7, 3, 6), max(pop, 0.01)
    if t < 14.6:
        tq = core.q(t)
        s = road_s(tq)
        p = road_point(s)
        ahead = road_point(min(s + 20, _L[-1]))
        lean = math.degrees(math.atan2(ahead[1] - p[1], ahead[0] - p[0] + 1e-6))
        hop = 10 * (1 if int(tq * 12) % 2 else -1)
        tilt = 0.35 * lean + hop
        if 12.8 <= t < 13.6:                             # 撞上边界：弹回、打晃
            tilt += 25 * spring(t - 12.8, 2.5, 3)
        return p, tilt, 1.0
    rest = np.array([4500.0, hill_y(4500) + 2])
    top = road_point(SEG_S[3])
    k = ease(prog(t, 14.6, 14.8))
    p = top + (rest - top) * k + np.array([0, -60 * 4 * k * (1 - k)])
    tilt = 10 * math.sin(core.q(t) * 12 * math.pi / 2) if 14.8 <= t < 16.0 else 0   # 画灯塔时摇笔
    if 16.45 <= t < 16.9:
        tilt = -22 * math.sin(math.pi * prog(t, 16.45, 16.9))                          # 击掌
    return p, tilt, 1.0


def cap_state(t):
    """船长：位置、朝向与姿势。"""
    tq = core.q(t)
    if t < 3.0:
        look = 0 if t < 2.4 else (-1 if int(t * 3) % 2 else 1)
        return dict(x=800, y=GY, k=prog(t, 0.6, 2.2), eyes="closed" if 2.25 <= t < 2.35 else "open", look=look, bob=1.5 * math.sin(tq * 5))
    if t < 5.0:
        a = 60 * ease(prog(t, 3.1, 3.3)) * (1 - ease(prog(t, 4.3, 4.6)))
        return dict(x=800, y=GY, arms=(0, 0, a, 25 * (a > 1)), mouth="open" if 4.4 <= t < 5.0 else "smile")
    if t < 11.6:
        s = road_s(tq)
        bx = road_point(s)[0]
        x = max(800, min(bx - 260, 800 + (tq - 5.0) * 420))
        walking = x > 801
        return dict(x=x, y=GY, walk=(tq * 1.6) % 1 if walking else None)
    if t < 13.4:
        x = min(3050, road_point(road_s(11.6))[0] - 260)
        up = ease(prog(t, 12.1, 12.25)) * (1 - ease(prog(t, 12.7, 12.9)))
        return dict(x=x, y=GY, arms=(0, 0, 150 * up, 0), eyes="open", mouth="open", look=1)
    x0 = min(3050, road_point(road_s(11.6))[0] - 260)
    x = lerp(x0, 4400, ease(prog(t, 13.4, 16.3)))   # 走过灯塔前方，停在右侧
    walking = t < 16.3
    arms = (0, 0, 0, 0)
    if 16.45 <= t < 16.9:
        arms = (0, 0, 160 * math.sin(math.pi * prog(t, 16.45, 16.9)), 0)
    eyes = "wink" if 19.0 <= t < 19.6 else "open"
    return dict(x=x, y=hill_y(x), walk=(tq * 1.6) % 1 if walking else None, arms=arms, eyes=eyes)


# ---------------- 摄像机 ----------------
def camera_matrix(t):
    if t < 3.0:
        v = keys(t, [(0, (800, 1850, 1150)), (3.0, (820, 1860, 1250))])
    elif t < 6.5:
        v = keys(t, [(3.0, (820, 1860, 1250)), (4.6, (950, 1880, 1400)), (6.5, (1350, 1870, 1700))])
    elif t < 11.0:
        bx = road_point(road_s(t))[0]
        v = (bx - 150, 1850, 1800)
    elif t < 14.0:
        v = keys(t, [(11.0, (3200, 1700, 2000)), (11.8, (3350, 1560, 2200)), (14.0, (3550, 1620, 2200))])
    elif t < 17.3:
        v = keys(t, [(14.0, (3900, 1780, 1900)), (15.2, (4250, 1720, 1600)), (17.3, (4250, 1740, 1650))])
    else:
        v = keys(t, [(17.3, (4250, 1740, 1650)), (18.1, (2800, 1575, 5600)), (18.6, (2800, 1575, 5600)), (19.4, (4250, 1950, 2300))])
    shake = geom.shake(t, 2.0) if 12.8 <= t < 13.1 else (0, 0)
    return CAM.matrix(*v, shake=shake)


TEXT_PLANE = geom.Plane([(3620, 2130), (5020, 2130), (5020, 2440), (3620, 2440)], (1400, 310))


# ---------------- 渲染 ----------------
def render(t):
    A, s = camera_matrix(t)
    frame = CAM.render_plate(PLATE, A)
    tq = core.q(t)

    # 蓝：箭头与路
    blue = Layer(W, H)
    arrow = [[(860, RY + 5), (1175, RY + 5)], [(1130, RY - 25), (1180, RY + 5), (1130, RY + 35)]]
    draw_strokes(blue, A, t, arrow, 3.2, 4.2, w=9, seed=40)
    if t >= 5.0:
        blue.stroke(A, road_upto(road_s(tq)), 8, t, seed=41, taper=False, step=8)
    frame = blue.ink(frame, BLUE)

    # 黄：边界线（船长画的）
    if t >= 12.2:
        yel = Layer(W, H)
        k = ease_out(prog(t, 12.2, 12.6))
        x0, x1 = 3180, 3900
        yel.stroke(A, [(x0, BOUND_Y), (lerp(x0, x1, k), BOUND_Y)], 14, t, seed=50, taper=False)
        frame = yel.paint(frame, YELLOW, 0.95)

    # 黑：背景物件
    bg = Layer(W, H)
    for i, (strokes, t0, t1) in enumerate(PROPS):
        draw_strokes(bg, A, t, strokes, t0, t1, w=3.2, seed=100 + 20 * i)
    frame = bg.ink(frame)

    # 灯塔光束
    if t >= 16.0:
        ang = (t - 16.0) * 2.2
        c = np.array([LX, hill_y(LX) - 295])
        beam = [tuple(c)] + [tuple(c + 700 * np.array([math.cos(ang + d), math.sin(ang + d) * 0.35])) for d in (-0.12, 0.12)]
        frame = draw.fill_poly(frame, A, beam, YELLOW, 0.35 * prog(t, 16.0, 16.4))

    # 铅笔
    b = bot_state(t)
    if b is not None:
        L = [Layer(W, H) for _ in range(7)]
        pencil(L, A, t, b[0], b[1], b[2])
        for lay, col in zip(L[:6], (PAPER_COL, YELLOW, PINK, WOOD, GRAPH, METAL)):
            frame = lay.paint(frame, col)
        frame = L[6].ink(frame)

    # 船长
    st = cap_state(t)
    if t >= 0.6:
        L = [Layer(W, H) for _ in range(4)]
        info = captain(L, A, t, st["x"], st["y"], arms=st.get("arms", (0, 0, 0, 0)), walk=st.get("walk"), eyes=st.get("eyes", "open"),
                       mouth=st.get("mouth", "smile"), look=st.get("look", 0), k=st.get("k", 1.0), bob=st.get("bob", 0.0))
        frame = L[0].paint(frame, PAPER_COL)
        frame = L[1].paint(frame, SHIRT)
        frame = L[2].paint(frame, HAT)
        frame = L[3].ink(frame)
        head = info["head"]
        frame = fx.pop(frame, A, QMARK, (QMARK.shape[1] / 2, QMARK.shape[0]), head + [40, -80], t, 2.5, 0.28, life=0.7)
        frame = fx.pop(frame, A, BANG, (BANG.shape[1] / 2, BANG.shape[0]), head + [40, -80], t, 11.5, 0.3, life=0.9)
        for tn, dx in ((7.9, 30), (9.0, 55)):
            frame = fx.pop(frame, A, NOTE, (NOTE.shape[1] / 2, NOTE.shape[0]), head + [dx, -70], t, tn, 0.22, life=0.8)
        if 19.05 <= t < 19.9:                                  # 眨眼星光
            frame = fx.pop(frame, A, STAR, (128, 128), head + [30, -30], t, 19.05, 0.35, life=0.85, rise=15)

    # 开场墨点
    if 0.25 <= t < 0.9:
        k = ease_out(prog(t, 0.25, 0.6))
        dot = Layer(W, H)
        dot.dot(A, (802, GY - 150), 6 + 30 * k)
        frame = dot.ink(frame, alpha=1 - prog(t, 0.6, 0.9))

    # 撞边界：晕眩星
    if 12.8 <= t < 13.8 and b is not None:
        top = b[0] + np.array([0, -135])
        for j in range(3):
            a = (t - 12.8) * 7 + j * 2.1
            p = top + np.array([34 * math.cos(a), 10 * math.sin(a)])
            frame = draw.place(frame, A, STAR, (128, 128), p, 0.13, a * 40, alpha=1 - prog(t, 13.4, 13.8))
    # 击掌火花
    frame = fx.pop(frame, A, STAR, (128, 128), np.array([4455.0, hill_y(4455) - 175]), t, 16.62, 0.5, life=0.6, rise=0)

    # 手写字
    frame = fx.handwriting(frame, A, TEXT_PLANE, [([("人定方向，", config.FONT_HAND_ZH, 170), ("AI ", config.FONT_HAND_EN, 120), ("执行", config.FONT_HAND_ZH, 170)], (40, 0)),
                                                  ("船长的角落", config.FONT_HAND_ZH, 90, (860, 200))], t, 18.4, 19.3, col=draw.INK_DARK)

    frame = post.grain(post.vignette(frame, 0.18), t, amount=0.008)
    return post.fade(frame, t, DUR, 0.4, 0.5)
