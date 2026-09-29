"""B-roll 共用小部件：球、迷你画布、代码窗口、播放窗口、小标签。所有 B-roll 都在桌面舞台上，船长在桌上走。"""
from common import *

SKY = (hexbgr("#5FB4FF"), hexbgr("#BFE6FF"))
GROUND = (hexbgr("#3CC98A"), hexbgr("#1E8F63"))


def ball_pos(u):
    """球的弹跳路径，u∈[0,1] → 归一化画布坐标 (x, y)，y 向下。"""
    return 0.14 + 0.72 * u, 0.86 - 0.72 * abs(math.sin(math.pi * u * 2.4))


def draw_ball(img, cx, cy, r):
    circle(img, (cx + r * 0.06, cy + r * 0.16), r, (20, 20, 40), alpha=0.35)
    circle(img, (cx, cy), r, colors=(C["yellow"], C["orange"]), outline=C["ink"], ow=max(2, int(r * 0.14)))
    circle(img, (cx - r * 0.32, cy - r * 0.34), r * 0.24, C["white"], alpha=0.9)


def mini_canvas(img, x0, y0, x1, y1, u, ball_r=None):
    """一小块“画布”，里面有个球在 u 处。"""
    panel(img, x0, y0, x1, y1, r=10, fill=hexbgr("#0E1B45"), outline=C["cyan"], ow=3, shadow=False)
    w, h = x1 - x0, y1 - y0
    line(img, (x0 + 10, y0 + h * 0.90), (x1 - 10, y0 + h * 0.90), C["dim"], max(2, int(h * 0.03)))
    bx, by = ball_pos(u)
    draw_ball(img, x0 + bx * w, y0 + by * h - h * 0.08, ball_r or h * 0.11)


def frame_thumb(img, c, u, scale=1.0):
    if scale < 0.08:
        return img
    w, h = 104 * scale, 78 * scale
    mini_canvas(img, c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2, u, ball_r=h * 0.12)
    return img


def traffic(img, x, y, k=1.0):
    for i, col in enumerate((C["red"], C["yellow"], C["green"])):
        circle(img, (x + i * 26, y), 8 * k, col)


def code_window(img, box, t, t0, per_line=0.5, n=10, k=1.0, seed=5, title="</>"):
    """代码窗口：顶栏三个圆点 + 逐行敲出的彩色代码条。返回每行完成的时间列表。"""
    x0, y0, x1, y1 = box
    card(img, x0, y0, x1, y1, scale=k, glow_col=C["cyan"], r=26)
    if k < 0.9:
        return []
    traffic(img, x0 + 40, y0 + 34)
    label(img, title, ((x0 + x1) / 2, y0 + 34), size=32, fill=C["cyan"], stroke=0)
    line(img, (x0 + 14, y0 + 66), (x1 - 14, y0 + 66), hexbgr("#2E4A9A"), 2)
    rng = np.random.default_rng(seed)
    pal = [C["cyan"], C["pink"], C["yellow"], C["mint"], C["violet"], C["white"]]
    done = []
    row_h = (y1 - y0 - 100) / n
    for i in range(n):
        ind = (i % 3 == 1) * 34 + (i % 4 == 2) * 20
        maxw = x1 - x0 - 90 - ind
        segs = [(0.10 + 0.20 * rng.random()), (0.12 + 0.28 * rng.random()), (0.10 + 0.22 * rng.random())]
        ts = t0 + i * per_line
        p = clamp((t - ts) / (per_line * 0.9))
        done.append(ts + per_line * 0.9)
        cx = x0 + 44 + ind
        used = 0.0
        for j, sw in enumerate(segs):
            w_seg = maxw * sw
            vis = clamp((p * sum(segs) * maxw - used) / w_seg)
            if vis > 0.02:
                panel(img, cx, y0 + 92 + i * row_h, cx + w_seg * vis - 6, y0 + 92 + i * row_h + row_h * 0.42, r=7, fill=pal[(i + j * 2) % len(pal)], shadow=False)
            cx += w_seg
            used += w_seg
        if 0 < p < 1 and int(t * 4) % 2 == 0:
            panel(img, cx + 2, y0 + 88 + i * row_h, cx + 10, y0 + 96 + i * row_h + row_h * 0.42, r=2, fill=C["white"], shadow=False)
    return done


def player_window(img, box, k=1.0, glow_col=None):
    x0, y0, x1, y1 = box
    card(img, x0, y0, x1, y1, scale=k, glow_col=glow_col or C["pink"], r=26)
    return (x0 + 26, y0 + 26, x1 - 26, y1 - 84)          # 屏幕区域


def player_scene(img, screen, t, T_LV, t_play):
    """小画面：T_LV = 四层（天地、太阳、山、球）出现的时间；t_play>0 时开始播放（球弹跳、太阳光线转动）。"""
    sx0, sy0, sx1, sy1 = screen
    w, h = sx1 - sx0, sy1 - sy0
    panel(img, sx0, sy0, sx1, sy1, r=14, fill=hexbgr("#0E1B45"), outline=C["line"], ow=3, shadow=False)
    k1 = ease_out(clamp((t - T_LV[0]) / 0.6))
    if k1 <= 0:
        return
    panel(img, sx0 + 4, sy0 + 4, sx0 + 4 + (w - 8) * k1, sy1 - 4, r=12, colors=SKY, shadow=False)
    gy = sy0 + h * 0.72
    poly_fill(img, [(sx0 + 4, gy), (sx0 + 4 + (w - 8) * k1, gy), (sx0 + 4 + (w - 8) * k1, sy1 - 4), (sx0 + 4, sy1 - 4)], colors=GROUND)
    k = pop(t, T_LV[1], 0.5)                               # 太阳
    if k > 0:
        sxp, syp = sx0 + w * 0.78, sy0 + h * 0.24
        rot = t_play * 40 if t_play > 0 else 0
        for i in range(10):
            a = math.radians(rot + i * 36)
            line(img, (sxp + math.cos(a) * 44 * k, syp + math.sin(a) * 44 * k), (sxp + math.cos(a) * 66 * k, syp + math.sin(a) * 66 * k), C["yellow"], 6)
        circle(img, (sxp, syp), 34 * k, colors=(C["yellow"], C["orange"]), outline=C["ink"], ow=3, glow_col=C["yellow"])
    k = pop(t, T_LV[2], 0.5)                               # 山
    if k > 0:
        for cx_, hh_, ww_, col in ((0.28, 0.42, 0.34, hexbgr("#6B7BFF")), (0.52, 0.30, 0.26, hexbgr("#8F6BFF"))):
            tip = (sx0 + w * cx_, gy - h * hh_ * k)
            poly_fill(img, [(sx0 + w * (cx_ - ww_ / 2 * k), gy), tip, (sx0 + w * (cx_ + ww_ / 2 * k), gy)], color=col, outline=C["ink"], ow=3)
    k = pop(t, T_LV[3], 0.5)                               # 球
    if k > 0:
        u = ((t_play * 0.36) % 1.0) if t_play > 0 else 0.0
        bx = sx0 + w * (0.12 + 0.76 * u)
        lift = abs(math.sin(math.pi * u * 2.6)) * h * 0.30 if t_play > 0 else 0
        circle(img, (bx, gy - 2), 20 * k * (1 - 0.5 * lift / (h * 0.3)), (20, 20, 40), alpha=0.25)
        draw_ball(img, bx, gy - 26 * k - lift, 24 * k)


def play_bar(img, screen, prog_u):
    sx0, sy0, sx1, sy1 = screen
    y = sy1 + 44
    panel(img, sx0 + 4, y - 7, sx1 - 4, y + 7, r=7, fill=hexbgr("#24336E"), shadow=False)
    if prog_u > 0.005:
        panel(img, sx0 + 4, y - 7, sx0 + 4 + (sx1 - sx0 - 8) * prog_u, y + 7, r=7, colors=(C["cyan"], C["pink"]), angle=0, shadow=False)
        circle(img, (sx0 + 4 + (sx1 - sx0 - 8) * prog_u, y), 13, C["white"], outline=C["ink"], ow=3)


def fade_all(img, t, dur, fin=0.25, fout=0.3):
    k = fade_io(t, dur, fin, fout)
    if k < 1:
        img = (img.astype(np.float32) * k + np.array(C["bg0"], np.float32) * (1 - k)).astype(np.uint8)
    return img
