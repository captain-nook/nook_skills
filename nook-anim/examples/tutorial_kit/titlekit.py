"""章节标题套件：千问出的“纯文字 PNG”（透明底、封面同款霓虹立体字）+ 代码做全部动效和音效。4 秒。

时间线：
0.18–0.62  字从上方砸下来（下落时拉长，斜着）
0.62       落地：压扁 → 弹簧回弹、震屏、冲击环、星光和彩纸炸开
0.67–1.05  一道“波浪”从左到右滚过字（逐字弹跳的错落感，不用切开字形）
1.05–1.6   一道光从左到右扫过
0.95–1.35  下划线画出
0.55–1.1   船长跳出，落地压扁，然后呼吸
全程          背景光斑飘动、旋转光芒；结尾 0.3 秒淡出
"""
from common import *
from nookanim import audio as A

TITLE_DUR = 4.0
T_IMP = 0.62
_YY = {}


def load_title(name, max_w, max_h, shear=0.13):
    """读千问出的透明字，裁边，斜一点（封面是斜体），转预乘。返回 (spr, 原始宽高)。"""
    im = imread(TITLE_DIR / f"{name}.png")
    a = im[:, :, 3]
    ys, xs = np.where(a > 6)
    m = 8
    im = im[max(0, ys.min() - m):ys.max() + m, max(0, xs.min() - m):xs.max() + m]
    h, w = im.shape[:2]
    sc = min(max_w / (w + shear * h), max_h / h)
    im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    h, w = im.shape[:2]
    f = to_pm(im)
    M = np.float32([[1, -shear, shear * h], [0, 1, 0]])
    f = cv2.warpAffine(f, M, (int(w + shear * h), h), flags=cv2.INTER_LINEAR, borderValue=0)
    return f


def _grid(h, w):
    key = (h, w)
    if key not in _YY:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        _YY[key] = (xx, yy)
    return _YY[key]


_RAY_FALL = None


def rays(img, center, t, color, strength=0.10, n=14):
    """慢转的光芒，铺在字后面。"""
    global _RAY_FALL
    hh, ww = H // 2, W // 2
    if _RAY_FALL is None:
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        _RAY_FALL = np.clip(1 - np.hypot(xx - ww / 2, yy - hh / 2) / (ww * 0.62), 0, 1) ** 1.2
    layer = np.zeros((hh, ww), np.uint8)
    cx, cy = center[0] / 2, center[1] / 2
    for i in range(n):
        a0 = t * 0.18 + i * 2 * math.pi / n
        a1 = a0 + math.pi / n * 0.9
        pts = np.array([(cx, cy), (cx + math.cos(a0) * 1500, cy + math.sin(a0) * 1500), (cx + math.cos(a1) * 1500, cy + math.sin(a1) * 1500)], np.int32)
        cv2.fillPoly(layer, [pts], 255, cv2.LINE_AA)
    f = cv2.resize(cv2.GaussianBlur(layer, (0, 0), 3).astype(np.float32) / 255 * _RAY_FALL, (W, H), interpolation=cv2.INTER_LINEAR)
    return add_light(img, 0, 0, f, color, strength)


class Title:
    def __init__(self, name, nchars, pose, side="left", flip=False, hue=None, max_w=1780, max_h=470, y_center=350, char_h=420, pose2=None, t_pose2=1.25):
        self.name, self.n = name, nchars
        self.spr = load_title(name, max_w, max_h)
        self.h, self.w = self.spr.shape[:2]
        self.pose, self.pose2, self.t_pose2 = pose, pose2, t_pose2
        self.side, self.flip, self.hue = side, flip, hue or C["cyan"]
        self.cx = W / 2
        self.rest_bottom = y_center + self.h / 2
        self.char_h = char_h
        self.char_x = 470 if side == "left" else W - 470

    # ------------------------------------------------------------ 画面
    def render(self, t):
        img = new_frame(t)
        cx, cy_mid = self.cx, self.rest_bottom - self.h / 2
        glow(img, (cx, cy_mid), 760, self.hue, 0.34 * clamp(prog(t, 0.5, 0.9)))
        rays(img, (cx, cy_mid), t, self.hue, 0.10 * clamp(prog(t, 0.55, 1.0)))

        # ---- 标题字 ----
        spr = self.spr
        if T_IMP < t < T_IMP + 1.5:                       # 波浪：每列按位置延迟起跳
            w = spr.shape[1]
            xs = np.arange(w, dtype=np.float32)
            tw = T_IMP + 0.05 + (xs / w) * 0.38
            dt = t - tw
            dy = np.where(dt > 0, -30 * np.exp(-dt * 6.5) * np.sin(dt * 20), 0.0).astype(np.float32)
            mapx, _ = np.meshgrid(xs, np.arange(spr.shape[0], dtype=np.float32))
            mapy = np.arange(spr.shape[0], dtype=np.float32)[:, None] - dy[None, :]
            spr = cv2.remap(spr, mapx, mapy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        if 1.05 < t < 1.7:                                # 光扫过
            xx, yy = _grid(*spr.shape[:2])
            pos = lerp(-0.25, 1.25, ease_in_out(prog(t, 1.05, 1.7))) * spr.shape[1]
            band = np.exp(-(((xx - 0.45 * yy - pos) / (0.07 * spr.shape[1])) ** 2))
            spr = spr.copy()
            spr[:, :, :3] = np.clip(spr[:, :, :3] + band[..., None] * spr[:, :, 3:4] * 0.85, 0, 1)
        if t < T_IMP:
            u = clamp(prog(t, 0.18, T_IMP))
            yb = self.rest_bottom - 900 * (1 - u * u)
            sx, sy, rot, al = 1 - 0.10 * u, 1 + 0.22 * u, -9 * (1 - u), clamp(prog(t, 0.14, 0.26))
        else:
            sp = spring(t - T_IMP, 3.0, 6.0)
            yb = self.rest_bottom - (5 * math.sin((t - 1.7) * 3.2) * clamp(prog(t, 1.7, 2.1)) if t > 1.7 else 0)
            sx, sy, rot, al = 1 + 0.20 * sp, 1 - 0.26 * sp, 0.0, 1.0
        put(img, spr, (cx, yb), 1.0, al, rot, sx=sx, sy=sy, anchor=(0.5, 1.0))

        # ---- 下划线（封面里那道橙黄光）----
        k = clamp(prog(t, 0.95, 1.4))
        if k > 0:
            n = int(60 * k) + 2
            uw = min(640, 0.42 * self.w)
            pts = [(cx - uw + 2 * uw * i / 59, self.rest_bottom + 44 - 26 * math.sin(math.pi * i / 59) - 6 * (i / 59)) for i in range(n)]
            for wd, col, al in ((22, C["orange"], 0.25), (12, C["yellow"], 0.55), (5, C["white"], 0.95)):
                polyline(img, pts, col, wd, al * clamp(1.2 - 1.2 * prog(t, 3.4, 3.8)))

        # ---- 冲击环、星光、彩纸 ----
        if t >= T_IMP:
            d = t - T_IMP
            if d < 0.6:
                r = 80 + 900 * ease_out(d / 0.6)
                ov = img.copy()
                cv2.ellipse(ov, (int(cx), int(self.rest_bottom)), (int(r), int(r * 0.22)), 0, 0, 360, C["white"], 6, cv2.LINE_AA)
                cv2.addWeighted(ov, 0.7 * (1 - d / 0.6), img, 1 - 0.7 * (1 - d / 0.6), 0, img)
            rng = np.random.default_rng(11)
            cols = [C["cyan"], C["yellow"], C["pink"], C["white"], C["mint"]]
            for i in range(14):
                a = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
                sp_ = rng.uniform(380, 900)
                life = rng.uniform(0.7, 1.3)
                if d < life:
                    pos = (cx + math.cos(a) * sp_ * ease_out(d / life) * 0.9, self.rest_bottom - 30 + math.sin(a) * sp_ * ease_out(d / life) * 0.7 + 260 * d * d)
                    sparkle(img, pos, rng.uniform(14, 30) * (1 - d / life), cols[i % 5], rot=d * 200, alpha=1 - d / life)
            for i in range(20):                             # 彩纸
                x0 = rng.uniform(140, W - 140)
                fall = rng.uniform(0.9, 1.6)
                dd = d - rng.uniform(0.05, 0.4)
                if 0 < dd < fall * 2.2:
                    y = -40 + (self.rest_bottom + 260) * ease_in_out(dd / (fall * 2.2)) * 0.95
                    ang = dd * rng.uniform(-300, 300)
                    x = x0 + 30 * math.sin(dd * 4 + i)
                    ww_, hh_ = rng.uniform(10, 18), rng.uniform(18, 30)
                    pts = [(x + math.cos(math.radians(ang + o)) * r_, y + math.sin(math.radians(ang + o)) * r_) for o, r_ in ((0, ww_), (90, hh_), (180, ww_), (270, hh_))]
                    poly_fill(img, [(px, py) for px, py in pts], cols[i % 5], alpha=0.95 * clamp(1.4 - dd / (fall * 2.2)))

        # ---- 船长：从画面下方跳上来，落地压扁，然后呼吸；有第二姿势的话在 t_pose2 换成第二姿势再跳一下 ----
        pose = self.pose2 if (self.pose2 and t >= self.t_pose2) else self.pose
        if t >= 0.5:
            enter = 520 * (1 - ease_out(prog(t, 0.5, 0.85)))
            yo, sx_, sy_ = hop(t, 0.85, 0.55, 80)
            if self.pose2 and t >= self.t_pose2:
                yo, sx_, sy_ = hop(t, self.t_pose2, 0.5, 70)
            bsx, bsy = breathe(t)
            char(img, pose, (self.char_x, FOOT_Y + yo + enter), h=self.char_h, sx=sx_ * bsx, sy=sy_ * bsy, flip=self.flip)
        # ---- 震屏与淡入淡出 ----
        if T_IMP <= t < T_IMP + 0.28:
            k = 1 - (t - T_IMP) / 0.28
            dx, dy_ = 11 * k * math.sin((t - T_IMP) * 90), 8 * k * math.cos((t - T_IMP) * 75)
            img = cv2.warpAffine(img, np.float32([[1, 0, dx], [0, 1, dy_]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
        f = fade_io(t, TITLE_DUR, 0.12, 0.3)
        if f < 1:
            img = (img.astype(np.float32) * f + np.array(C["bg0"], np.float32) * (1 - f)).astype(np.uint8)
        return img

    # ------------------------------------------------------------ 音效
    def audio(self, path, root=72, scale=(0, 2, 4, 7, 9)):
        mx = A.Mixer(TITLE_DUR)
        mx.add(A.shaped(A.noise(0.42, 250, 5200), 0.85, 0.15), 0.02, 0.16)                 # 入场风声
        mx.add(A.sweep(2200, 260, 0.42, 0.3), 0.20, 0.13)                                  # 下落
        mx.add(A.sweep(170, 42, 0.32, 0.12), T_IMP, 0.55)                                  # 撞击低频
        mx.add(A.shaped(A.noise(0.16, 700, 7000), 0.02, 0.9), T_IMP, 0.25)                 # 撞击噪声
        mx.add(A.boing(190, 0.45, 150, 11), T_IMP + 0.03, 0.30)                            # 弹一下
        for i in range(self.n):                                                             # 波浪：逐字木琴音
            tw = T_IMP + 0.05 + (i + 0.5) / self.n * 0.38
            m = root + scale[i % len(scale)] + 12 * (i // len(scale))
            mx.add(A.tone(A.midi(m), 0.5, 0.16, ((1, 1), (2, 0.45), (3.9, 0.15))), tw + 0.02, 0.16, -0.5 + i / max(1, self.n - 1))
        mx.add(A.sweep(1300, 5600, 0.5, 0.35), 1.05, 0.10)                                 # 光扫
        mx.add(A.shaped(A.noise(0.45, 4000, 11000), 0.5, 0.5), 1.10, 0.05)
        for j, f in enumerate((2093, 2637, 3136)):                                          # 亮晶晶
            mx.add(A.ding(f, 0.9), 0.98 + j * 0.09, 0.07, 0.3 - 0.3 * j)
        mx.add(A.boing(330, 0.3, 160, 14), 0.62, 0.20, 0.3)                                # 船长跳出
        mx.add(A.sweep(300, 900, 0.14, 0.09), 0.55, 0.14, 0.4)
        mx.add(A.sweep(900, 300, 0.24, 0.12), 3.72, 0.08)                                  # 收尾
        wav = mx.master(reverb=0.14, fade_in=0.01, fade_out=0.25)
        A.write_wav(path, wav)
        return path
