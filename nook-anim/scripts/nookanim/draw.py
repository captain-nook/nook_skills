"""绘制：合成、贴图、阴影、正片叠底、屏幕线条、马克笔墨线。frame 为 float32 BGR（0–1）。"""
import math

import cv2
import numpy as np

from .geom import A3

INK_BLUE = np.array([216, 91, 30], np.float32) / 255      # BGR，品牌蓝 #1E5BD8
INK_DARK = np.array([120, 50, 20], np.float32) / 255


def over(dst, lay):
    """把 BGRA 图层叠到 BGR 画面上。"""
    a = lay[:, :, 3:4]
    return lay[:, :, :3] * a + dst * (1 - a)


def multiply(frame, a, col=INK_BLUE):
    """正片叠底：墨水、阴影这类"染在纸上"的东西用它，纸纹会透出来。"""
    return frame * (1 - a[:, :, None] + a[:, :, None] * col)


def place(frame, A, spr, anchor, at, sc, rot=0.0, alpha=1.0, flip=False):
    """把素材的 anchor 点放到场景坐标 at，缩放 sc（场景像素/素材像素），旋转 rot 度。"""
    H, W = frame.shape[:2]
    if flip:
        spr = spr[:, ::-1]
        anchor = (spr.shape[1] - 1 - anchor[0], anchor[1])
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    Msp = np.array([[c * sc, -s * sc, 0], [s * sc, c * sc, 0], [0, 0, 1]])
    Msp[:2, 2] = np.array(at) - Msp[:2, :2] @ np.array(anchor)
    M = (A3(A) @ Msp)[:2]
    lay = cv2.warpAffine(spr, M.astype(np.float32), (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    if alpha < 1:
        lay = lay * alpha
    return over(frame, lay)


def sprite_point(pt, anchor, at, sc, rot=0.0):
    """素材坐标里的某个点（笔尖、帆尖、眼睛）在 place 之后落到场景的哪里。"""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    d = (np.array(pt, float) - np.array(anchor, float)) * sc
    return np.array(at, float) + np.array([c * d[0] - s * d[1], s * d[0] + c * d[1]])


def shadow(frame, A, at, w, strength=0.4, h_ratio=0.12):
    """接触阴影：场景坐标 at 处宽 w 的柔和椭圆，正片叠底压暗。"""
    H, W = frame.shape[:2]
    p = A3(A) @ np.array([at[0], at[1], 1])
    s = A[0, 0]
    m = np.zeros((H, W), np.float32)
    cv2.ellipse(m, (int(p[0]), int(p[1])), (max(2, int(w * s / 2)), max(2, int(w * s * h_ratio))), 0, 0, 360, strength, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), max(1, 8 * s))
    return frame * (1 - m[:, :, None])


def screen_lines(frame, A, polylines, width, col=None, alpha=1.0):
    """在场景坐标里画折线（自动换算到屏幕）。col=None 时按墨水正片叠底，否则按颜色覆盖。"""
    if alpha <= 0:
        return frame
    H, W = frame.shape[:2]
    m = np.zeros((H, W), np.uint8)
    s = A[0, 0]
    for pl in polylines:
        pts = (A3(A) @ np.vstack([np.array(pl, float).T, np.ones(len(pl))]))[:2].T
        cv2.polylines(m, [pts.astype(np.int32)], False, 255, max(1, int(width * s)), cv2.LINE_AA)
    a = m.astype(np.float32) / 255 * alpha
    if col is None:
        return multiply(frame, a)
    return frame * (1 - a[:, :, None]) + np.array(col, np.float32) * a[:, :, None]


def fill_poly(frame, A, poly, col, alpha=1.0):
    """场景坐标的实心多边形（如小旗）。"""
    H, W = frame.shape[:2]
    pts = (A3(A) @ np.vstack([np.array(poly, float).T, np.ones(len(poly))]))[:2].T
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [pts.astype(np.int32)], 255, cv2.LINE_AA)
    a = m.astype(np.float32)[:, :, None] / 255 * alpha
    return frame * (1 - a) + a * np.array(col, np.float32)


# ---------------- 马克笔墨线 ----------------
class Marker:
    """一个平面上的马克笔墨水层。先 begin() 取空画布，用 line() 画若干笔，再 composite() 贴到画面。
    纹理固定在平面坐标里，墨迹跟着纸走；笔画两头收细、宽窄起伏，边缘积墨。"""

    SS = 2  # 超采样

    def __init__(self, plane, seed=42):
        self.plane = plane
        rng = np.random.default_rng(seed)
        tex = cv2.GaussianBlur(rng.random((plane.h * self.SS, plane.w * self.SS)).astype(np.float32), (0, 0), sigmaX=14, sigmaY=1.2)
        self.tex = (tex - tex.min()) / (tex.max() - tex.min())

    def begin(self):
        return np.zeros((self.plane.h * self.SS, self.plane.w * self.SS), np.uint8)

    def line(self, canvas, pts_uv, width, seed=0):
        """pts_uv 为平面坐标折线，width 为平面坐标下的笔宽。"""
        pts = np.array(pts_uv, float) * self.SS
        n = len(pts) - 1
        for i in range(n):
            f = i / max(1, n - 1)
            taper = max(0.45, min(1.0, 5 * f, 5 * (1 - f)))
            w = width * self.SS * taper * (0.86 + 0.14 * math.sin(i * 0.55 + seed * 1.7))
            cv2.line(canvas, tuple(map(int, pts[i])), tuple(map(int, pts[i + 1])), 255, max(1, int(round(w))), cv2.LINE_AA)

    def composite(self, frame, A, canvas, col=INK_BLUE, fade=1.0, wash=None):
        """wash：可选的平面坐标浅色底（float，同画布尺寸），先铺底再上线。"""
        H, W = frame.shape[:2]
        Hs = self.plane.screen_h(A, self.SS)
        if wash is not None:
            frame = multiply(frame, cv2.warpPerspective(wash, Hs, (W, H)), col)
        m = canvas.astype(np.float32) / 255 * fade
        inner = cv2.erode(m, np.ones((5, 5), np.uint8))
        edge = np.clip(m - inner, 0, 1)
        body = m * (0.70 + 0.22 * self.tex)
        core = np.maximum(np.maximum(body, edge * 0.97), cv2.GaussianBlur(m, (0, 0), 4) * 0.28)
        return multiply(frame, cv2.warpPerspective(core, Hs, (W, H)), col)


def partial(poly, k):
    """折线按长度画到比例 k 的部分——"逐笔画出"的基础。"""
    if k >= 1:
        return list(poly)
    seg = [math.dist(poly[i], poly[i + 1]) for i in range(len(poly) - 1)]
    L, out = sum(seg) * max(0.0, k), [poly[0]]
    for i, d in enumerate(seg):
        if L <= d:
            f = L / d if d else 0
            out.append((poly[i][0] + (poly[i + 1][0] - poly[i][0]) * f, poly[i][1] + (poly[i + 1][1] - poly[i][1]) * f))
            return out
        out.append(poly[i + 1])
        L -= d
    return out
