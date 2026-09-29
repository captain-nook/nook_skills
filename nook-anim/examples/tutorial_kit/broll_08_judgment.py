"""broll-08：判断自己做（“大模型是永远不能帮你审美的”）。10 秒。

桌上一个代码画的小机器人，一手举着方案 A（灰蒙蒙）一手举着方案 B（鲜亮），头顶冒“？”，肩一耸——它选不出来。
船长走进来，托腮看了看，指向 B：B 的画框镀金、星光炸开，一枚“定”字印章盖下；机器人拍手。最后船长比 V。
"""
from bkit import *

DUR = 10.0
SHOTS = [(0.0, "机器人犯难"), (2.6, "船长来了"), (5.6, "选 B"), (7.6, "庆祝")]
ROBOT_X = 430
FRAME_A = (620, 150, 990, 470)          # 方案 A 画框
FRAME_B = (1080, 150, 1450, 470)        # 方案 B 画框
T_PICK = 5.6


def draw_pic(img, box, good, t, gold=0.0):
    x0, y0, x1, y1 = box
    panel(img, x0 - 16, y0 - 16, x1 + 16, y1 + 16, r=14, colors=((C["yellow"], C["orange"]) if gold > 0.5 else (hexbgr("#5A6690"), hexbgr("#3B4670"))),
          outline=C["ink"], ow=5, glow_col=C["yellow"] if gold > 0.5 else None, glow_a=0.7)
    w, h = x1 - x0, y1 - y0
    if good:
        panel(img, x0, y0, x1, y1, r=8, colors=(hexbgr("#FF8AC0"), hexbgr("#FFD86B")), shadow=False)
        circle(img, (x0 + w * 0.72, y0 + h * 0.32), 46, colors=(C["yellow"], C["orange"]), outline=C["ink"], ow=3, glow_col=C["yellow"])
        poly_fill(img, [(x0, y1), (x0 + w * 0.38, y0 + h * 0.42), (x0 + w * 0.7, y1)], colors=(hexbgr("#6B7BFF"), hexbgr("#8F6BFF")), outline=C["ink"], ow=3)
        poly_fill(img, [(x0 + w * 0.35, y1), (x0 + w * 0.7, y0 + h * 0.55), (x1, y1)], colors=(hexbgr("#3CC98A"), hexbgr("#1E8F63")), outline=C["ink"], ow=3)
    else:
        panel(img, x0, y0, x1, y1, r=8, fill=hexbgr("#7C849A"), shadow=False)
        circle(img, (x0 + w * 0.72, y0 + h * 0.32), 40, hexbgr("#B9BFCC"), outline=hexbgr("#5A6172"), ow=3)
        poly_fill(img, [(x0, y1), (x0 + w * 0.38, y0 + h * 0.5), (x0 + w * 0.7, y1)], color=hexbgr("#5C6478"))
        poly_fill(img, [(x0 + w * 0.35, y1), (x0 + w * 0.7, y0 + h * 0.6), (x1, y1)], color=hexbgr("#6A7286"))
    label(img, "B" if good else "A", ((x0 + x1) / 2, y1 + 56), size=64, fill=C["white"], stroke=8)


def draw_robot(img, x, foot, t, arms_up=0.0, shrug=0.0, mood="?", clap=0.0):
    """代码画的小机器人。arms_up：双臂举起的程度；shrug：耸肩；clap：拍手。"""
    bob = 3 * math.sin(t * 3)
    y = foot - 12 + bob
    # 腿
    for dx in (-30, 30):
        panel(img, x + dx - 14, foot - 44, x + dx + 14, foot, r=8, fill=hexbgr("#7AA3E6"), outline=C["ink"], ow=4, shadow=False)
    # 身体
    panel(img, x - 78, y - 214, x + 78, y - 44, r=26, colors=(hexbgr("#8DB4F5"), hexbgr("#5A82D0")), outline=C["ink"], ow=5, shadow=False)
    panel(img, x - 42, y - 176, x + 42, y - 108, r=14, fill=hexbgr("#0E1B45"), outline=C["ink"], ow=4, shadow=False)
    for i, col in enumerate((C["cyan"], C["yellow"], C["pink"])):
        circle(img, (x - 20 + i * 20, y - 142), 6, col)
    # 头
    panel(img, x - 70, y - 330, x + 70, y - 216, r=30, colors=(hexbgr("#A7C6FA"), hexbgr("#6F96E0")), outline=C["ink"], ow=5, shadow=False)
    line(img, (x, y - 330), (x, y - 360), C["ink"], 5)
    circle(img, (x, y - 368), 10, C["red"], outline=C["ink"], ow=3)
    for dx in (-30, 30):
        circle(img, (x + dx, y - 276), 20, C["white"], outline=C["ink"], ow=4)
        if mood == "?":
            circle(img, (x + dx + 5 * math.sin(t * 2.6), y - 276 + 3 * math.cos(t * 2.6)), 9, C["ink"])
        elif mood == "ok":
            circle(img, (x + dx, y - 276), 9, C["ink"])
    if mood == "?":
        line(img, (x - 22, y - 236), (x + 22, y - 232), C["ink"], 5)
    else:
        polyline(img, [(x - 22 + 44 * i / 10, y - 240 + 10 * math.sin(math.pi * i / 10)) for i in range(11)], C["ink"], 5)
    # 手臂（肩在身体两侧）
    for sgn in (-1, 1):
        sh = (x + sgn * 78, y - 180 + 8 * shrug * -1)
        up = arms_up
        hand = (x + sgn * (150 + 30 * up - 40 * clap * (0.5 + 0.5 * math.sin(t * 16))), y - 160 - 190 * up - 30 * shrug)
        line(img, sh, hand, hexbgr("#6F96E0"), 22)
        line(img, sh, hand, C["ink"], 4)
        circle(img, hand, 20, hexbgr("#A7C6FA"), outline=C["ink"], ow=4)
    if mood == "?":
        k = pop(t, 0.8, 0.4)
        if k > 0.02 and (t < T_PICK):
            bubble = (x + 90, y - 460)
            panel(img, bubble[0] - 46 * k, bubble[1] - 46 * k, bubble[0] + 46 * k, bubble[1] + 46 * k, r=26 * k, fill=C["white"], outline=C["ink"], ow=4, shadow=False)
            label(img, "?", bubble, size=64, scale=k, fill=C["red"], stroke=6, rot=8 * math.sin(t * 4))


def render(t):
    img = new_frame(t)
    # ---- 两幅方案 ----
    ka, kb = pop(t, 0.3, 0.4), pop(t, 0.6, 0.4)
    gold = 1.0 if t >= T_PICK + 0.3 else 0.0
    if ka > 0.02:
        b = FRAME_A
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        hw, hh = (b[2] - b[0]) / 2 * ka, (b[3] - b[1]) / 2 * ka
        draw_pic(img, (cx - hw, cy - hh, cx + hw, cy + hh), False, t)
    if kb > 0.02:
        b = FRAME_B
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        s_ = kb * (1 + 0.08 * spring(t - T_PICK - 0.3, 3, 6) if t > T_PICK + 0.3 else 1)
        hw, hh = (b[2] - b[0]) / 2 * s_, (b[3] - b[1]) / 2 * s_
        draw_pic(img, (cx - hw, cy - hh, cx + hw, cy + hh), True, t, gold)
    # ---- 机器人 ----
    if t < T_PICK:
        arms, shrug = 0.0, 0.5 + 0.5 * math.sin(t * 3.4)
        mood, clap = "?", 0.0
    else:
        arms, shrug, mood = 0.35, 0.0, "ok"
        clap = 1.0 if t > T_PICK + 0.5 else 0.0
    draw_robot(img, ROBOT_X, FOOT_Y - 6, t, arms_up=arms, shrug=shrug, mood=mood, clap=clap)
    # ---- 印章 “定” ----
    if t >= T_PICK + 0.55:
        k = ease_out(clamp((t - T_PICK - 0.55) / 0.16))
        sc = 1.9 - 0.9 * k
        c = ((FRAME_B[0] + FRAME_B[2]) / 2 + 60, (FRAME_B[1] + FRAME_B[3]) / 2 + 30)
        rot = -12
        if k > 0.05:
            seal = gtext("定", 150, None, C["white"], 0, None, FONT_HUPO)
            panel_c = gtext("定", 150, None, C["white"], 0, None, FONT_HUPO)
            r_ = 92 * sc
            circle(img, c, r_, colors=(hexbgr("#FF6B5B"), hexbgr("#D9342B")), outline=C["ink"], ow=5, alpha=min(1, k * 1.5), glow_col=C["red"])
            put(img, seal, c, sc, min(1, k * 1.5), rot)
        if t - (T_PICK + 0.55) < 0.5:                                    # 落印冲击波
            d = (t - T_PICK - 0.55) / 0.5
            ov = img.copy()
            cv2.circle(ov, (int(c[0]), int(c[1])), int(80 + 200 * ease_out(d)), C["white"], 6, cv2.LINE_AA)
            a = 0.8 * (1 - d)
            cv2.addWeighted(ov, a, img, 1 - a, 0, img)
    if t >= T_PICK + 0.3 and t < T_PICK + 1.6:                            # 星光炸开
        for i in range(8):
            a = i * math.pi / 4 + 0.3
            d = ease_out((t - T_PICK - 0.3) / 1.0)
            sparkle(img, ((FRAME_B[0] + FRAME_B[2]) / 2 + math.cos(a) * (240 * d), (FRAME_B[1] + FRAME_B[3]) / 2 + math.sin(a) * (200 * d)),
                    22 * (1 - d * 0.6), [C["yellow"], C["cyan"], C["pink"], C["white"]][i % 4], rot=t * 100, alpha=1 - d * 0.8)
    # ---- 船长：走进来 → 托腮 → 指向 B → 庆祝 ----
    x_stop = 1700
    if t < 2.6:
        pass
    elif t < 4.4:
        u = (t - 2.6) / 1.8
        x = 2140 + (x_stop - 2140) * 0.0 - 2140 * 0.0
        xw = 2140 - (2140 - 1250) * ease_in_out(u)                     # 从右边走进来，停在方案 B 右侧
        char_walk(img, xw, t, h=400, facing=-1, moving=u < 0.98)
    elif t < T_PICK:
        char(img, "think", (1250, FOOT_Y), h=400, sx=breathe(t)[0], sy=breathe(t)[1], flip=True)
    elif t < 7.6:
        yo, sx, sy = hop(t, T_PICK - 0.02, 0.4, 40)
        char(img, "point", (1250, FOOT_Y + yo), h=400, sx=sx, sy=sy, flip=False)
    else:
        yo, sx, sy = hop(t, 7.65, 0.5, 70)
        char(img, "win", (1250, FOOT_Y + yo), h=400, sx=sx, sy=sy)
        for i, (dx, dy) in enumerate(((-140, -430), (150, -450), (40, -520))):
            sparkle(img, (1250 + dx, FOOT_Y + dy), 26 * pop(t, 7.7 + i * 0.1, 0.3), [C["yellow"], C["cyan"], C["pink"]][i], rot=t * 60)
    return fade_all(img, t, DUR)
