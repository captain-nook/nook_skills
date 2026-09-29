"""火柴人 / 极简角色（风格卡 04）：代码骨骼、姿势插值、走路循环、两段反向动力学、几笔表情、镜头。

角度约定（一律是绝对角度，单位度）：
- 四肢：0 = 竖直向下，正值 = 朝角色面朝的方向转。大腿 30、小腿 -10 就是一条向前迈、膝盖微弯的腿。
- 躯干 lean：0 = 竖直向上，正值 = 向前倾，90 = 向前扑平。
- 面朝 facing：+1 朝右，-1 朝左。姿势按"朝右"写，朝左时自动镜像。
画在 uint8 BGR 画布上（cv2 的抗锯齿只对 8 位图生效），镜头 Cam 把世界坐标变到屏幕并同步缩放线宽。
"""
import math

import cv2
import numpy as np

from .core import clamp, ease, prog

BLACK = (30, 28, 28)
WHITE = (250, 250, 250)

POSE_KEYS = ("lean", "head", "lua", "lfa", "rua", "rfa", "lth", "lsh", "rth", "rsh")
STAND = dict(lean=0, head=0, lua=8, lfa=4, rua=-8, rfa=-4, lth=4, lsh=0, rth=-4, rsh=0)


class Rig:
    """骨长（世界像素）。l = 后侧（离镜头远）的肢体，r = 前侧。"""

    def __init__(self, head=38, neck=14, torso=130, ua=64, fa=58, th=72, sh=70, width=11):
        self.head, self.neck, self.torso = head, neck, torso
        self.ua, self.fa, self.th, self.sh = ua, fa, th, sh
        self.width = width

    @property
    def hip_h(self):
        """站直时胯到地面的高度。"""
        return self.th + self.sh


def _limb(a_deg, facing):
    a = math.radians(a_deg)
    return np.array([math.sin(a) * facing, math.cos(a)])


def fk(rig, hip, pose, facing=1):
    """正向运动学：胯的位置 + 姿势 → 各关节点。"""
    p = {**STAND, **pose}
    hip = np.array(hip, float)
    lean = math.radians(p["lean"])
    up = np.array([math.sin(lean) * facing, -math.cos(lean)])
    sho = hip + up * rig.torso
    neck = sho + up * rig.neck
    hl = math.radians(p["lean"] + p["head"])
    head_c = neck + np.array([math.sin(hl) * facing, -math.cos(hl)]) * rig.head
    J = dict(hip=hip, sho=sho, neck=neck, head=head_c)
    for s in "lr":
        J[s + "el"] = sho + _limb(p[s + "ua"], facing) * rig.ua
        J[s + "ha"] = J[s + "el"] + _limb(p[s + "fa"], facing) * rig.fa
        J[s + "kn"] = hip + _limb(p[s + "th"], facing) * rig.th
        J[s + "ft"] = J[s + "kn"] + _limb(p[s + "sh"], facing) * rig.sh
    J["up"] = up
    J["facing"] = facing
    J["head_ang"] = p["lean"] + p["head"]
    return J


def ik2(root, target, l1, l2, bend=1):
    """两段反向动力学：从 root 伸向 target，返回中间关节点。bend=±1 选择弯向哪一侧。"""
    root, target = np.array(root, float), np.array(target, float)
    d = target - root
    L = float(np.linalg.norm(d))
    L = clamp(L, abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3)
    base = math.atan2(d[1], d[0])
    a = math.acos(clamp((l1 * l1 + L * L - l2 * l2) / (2 * l1 * L), -1, 1))
    ang = base - bend * a
    return root + np.array([math.cos(ang), math.sin(ang)]) * l1


def reach(rig, J, side, target, bend=-1):
    """让某只手伸到 target（其余不动），就地改写关节点。"""
    sho = J["sho"]
    d = np.array(target, float) - sho
    L = np.linalg.norm(d)
    tgt = sho + d / max(L, 1e-6) * min(L, rig.ua + rig.fa - 1)
    J[side + "el"] = ik2(sho, tgt, rig.ua, rig.fa, bend * J["facing"])
    J[side + "ha"] = tgt
    return J


def lerp_pose(a, b, k):
    a, b = {**STAND, **a}, {**STAND, **b}
    return {n: a[n] + (b[n] - a[n]) * k for n in POSE_KEYS}


def pose_keys(t, pts, fn=ease):
    """姿势关键帧：pts = [(t0, pose0), (t1, pose1), ...]。"""
    if t <= pts[0][0]:
        return {**STAND, **pts[0][1]}
    for (ta, pa), (tb, pb) in zip(pts, pts[1:]):
        if t <= tb:
            return lerp_pose(pa, pb, fn(prog(t, ta, tb)))
    return {**STAND, **pts[-1][1]}


def walk(phase, amp=1.0):
    """走路循环：phase 以"步"为单位（每 1.0 迈一步），返回 (姿势, 胯的上下起伏)。"""
    s = math.sin(phase * math.pi)
    c = math.cos(phase * math.pi)
    pose = dict(
        lean=4 * amp,
        lth=26 * s * amp, rth=-26 * s * amp,
        lsh=(26 * s - 30 * max(0, -s)) * amp, rsh=(-26 * s - 30 * max(0, s)) * amp,
        lua=-22 * s * amp, rua=22 * s * amp,
        lfa=(-22 * s + 18) * amp, rfa=(22 * s + 18) * amp,
    )
    bob = -6 * abs(c) * amp
    return pose, bob


class Cam:
    """二维镜头：以世界点 (cx, cy) 为画面中心、放大 z 倍。"""

    def __init__(self, cx=960, cy=540, z=1.0, W=1920, H=1080):
        self.cx, self.cy, self.z, self.W, self.H = cx, cy, z, W, H

    def p(self, pt):
        return (int(round((pt[0] - self.cx) * self.z + self.W / 2)), int(round((pt[1] - self.cy) * self.z + self.H / 2)))

    def pts(self, arr):
        a = np.asarray(arr, float)
        return np.stack([(a[:, 0] - self.cx) * self.z + self.W / 2, (a[:, 1] - self.cy) * self.z + self.H / 2], 1).round().astype(np.int32)

    def w(self, width):
        return max(1, int(round(width * self.z)))


def line(img, cam, a, b, width, col=BLACK):
    cv2.line(img, cam.p(a), cam.p(b), col, cam.w(width), cv2.LINE_AA)


def poly(img, cam, pts, width, col=BLACK, closed=False):
    cv2.polylines(img, [cam.pts(pts)], closed, col, cam.w(width), cv2.LINE_AA)


def fill(img, cam, pts, col):
    cv2.fillPoly(img, [cam.pts(pts)], col, cv2.LINE_AA)


def disc(img, cam, c, r, col, outline=None, width=0):
    cv2.circle(img, cam.p(c), max(1, int(round(r * cam.z))), col, -1, cv2.LINE_AA)
    if outline is not None:
        cv2.circle(img, cam.p(c), max(1, int(round(r * cam.z))), outline, cam.w(width), cv2.LINE_AA)


def face(img, cam, rig, J, eyes="dot", mouth="none", brow=None, look=(0.0, 0.0), col=BLACK):
    """几笔表情。eyes: dot / wide / squint / x / closed / spiral；mouth: none / flat / smile / frown / o / chew；
    brow: None / angry / worried；look = 眼珠偏移（-1..1，按面朝方向）。"""
    f = J["facing"]
    hc = J["head"]
    r = rig.head
    ang = math.radians(J["head_ang"])
    fwd = np.array([math.cos(ang) * f, math.sin(ang) * f])       # 面朝方向（随头倾斜）
    upv = np.array([math.sin(ang) * f, -math.cos(ang)])
    base = hc + fwd * r * 0.38
    ex = [base - fwd * r * 0.30 + upv * r * 0.12, base + fwd * r * 0.22 + upv * r * 0.12]
    lk = fwd * look[0] * r * 0.10 + upv * (-look[1]) * r * 0.10
    lw = rig.width * 0.5
    for i, e in enumerate(ex):
        e = e + lk
        if eyes == "dot":
            disc(img, cam, e, r * 0.10, col)
        elif eyes == "wide":
            disc(img, cam, e, r * 0.20, WHITE, col, lw * 0.8)
            disc(img, cam, e + lk * 0.8, r * 0.08, col)
        elif eyes == "squint":
            line(img, cam, e - fwd * r * 0.12, e + fwd * r * 0.12, lw, col)
        elif eyes == "closed":
            arc = [e + fwd * r * 0.12 * math.cos(u) - upv * r * 0.06 * math.sin(u) for u in np.linspace(0, math.pi, 7)]
            poly(img, cam, arc, lw * 0.9, col)
        elif eyes == "x":
            d = r * 0.11
            line(img, cam, e - fwd * d - upv * d, e + fwd * d + upv * d, lw * 0.9, col)
            line(img, cam, e - fwd * d + upv * d, e + fwd * d - upv * d, lw * 0.9, col)
        elif eyes == "spiral":
            sp = [e + (fwd * math.cos(u) + upv * math.sin(u)) * r * 0.025 * u for u in np.linspace(0, 4 * math.pi, 30)]
            poly(img, cam, sp, lw * 0.6, col)
    if brow:
        for i, e in enumerate(ex):
            tilt = (1 if i == 1 else -1) * (0.10 if brow == "angry" else -0.08)
            c = e + upv * r * 0.30
            line(img, cam, c - fwd * r * 0.16 + upv * r * tilt, c + fwd * r * 0.16 - upv * r * tilt, lw, col)
    m = base - upv * r * 0.32 - fwd * r * 0.04
    if mouth == "flat":
        line(img, cam, m - fwd * r * 0.14, m + fwd * r * 0.14, lw, col)
    elif mouth in ("smile", "frown"):
        s = 1 if mouth == "smile" else -1
        arc = [m + fwd * r * 0.18 * math.cos(u) - upv * s * r * 0.10 * math.sin(u) for u in np.linspace(0, math.pi, 8)]
        poly(img, cam, arc, lw, col)
    elif mouth == "o":
        disc(img, cam, m, r * 0.11, col)
    elif mouth == "chew":
        line(img, cam, m - fwd * r * 0.12, m + fwd * r * 0.12 - upv * r * 0.05, lw, col)


def figure(img, cam, rig, J, col=BLACK, head_fill=WHITE, hands=True, fingers=None):
    """画一个火柴人：后侧肢体 → 躯干 → 前侧肢体 → 头。fingers = 手指张合 0..1（特写时用），None 不画。"""
    w = rig.width
    for s in "l":
        poly(img, cam, [J["hip"], J[s + "kn"], J[s + "ft"]], w, col)
        poly(img, cam, [J["sho"], J[s + "el"], J[s + "ha"]], w, col)
    line(img, cam, J["hip"], J["neck"], w, col)
    for s in "r":
        poly(img, cam, [J["hip"], J[s + "kn"], J[s + "ft"]], w, col)
        poly(img, cam, [J["sho"], J[s + "el"], J[s + "ha"]], w, col)
    for s in "lr":
        disc(img, cam, J[s + "ft"], w * 0.9, col)
        if hands:
            disc(img, cam, J[s + "ha"], w * 0.85, col)
    if fingers is not None:
        for s in "lr":
            h, e = J[s + "ha"], J[s + "el"]
            d = (h - e) / max(np.linalg.norm(h - e), 1e-6)
            n = np.array([-d[1], d[0]])
            for k in range(4):
                spread = (k - 1.5) * (0.35 + 0.45 * fingers[k] if hasattr(fingers, "__len__") else 0.5)
                tip = h + (d * math.cos(spread) + n * math.sin(spread)) * w * 2.0
                line(img, cam, h, tip, w * 0.45, col)
    disc(img, cam, J["head"], rig.head, head_fill, col, w * 0.9)
