"""几何：场景里的平面（纸面、便利贴、屏幕……）与虚拟摄像机。

坐标系三层：
- 平面坐标 (u, v)：某个平面自己的平直坐标，画墨线、手写字都在这里画；
- 场景坐标 (x, y)：大场景图（plate）上的像素；
- 屏幕坐标：输出画面像素，由摄像机矩阵 A（2x3）从场景坐标变换而来。
"""
import cv2
import numpy as np


def A3(A):
    return np.vstack([A, [0, 0, 1]])


class Plane:
    """场景图上的一个透视平面。quad 为四个角的场景坐标：远左、远右、近右、近左。"""

    def __init__(self, quad, size):
        self.w, self.h = size
        self.quad = np.float32(quad)
        self.H = cv2.getPerspectiveTransform(np.float32([[0, 0], [self.w, 0], [self.w, self.h], [0, self.h]]), self.quad)
        self.Hinv = np.linalg.inv(self.H)

    def to_scene(self, u, v):
        p = self.H @ np.array([u, v, 1.0])
        return p[:2] / p[2]

    def from_scene(self, x, y):
        p = self.Hinv @ np.array([x, y, 1.0])
        return p[:2] / p[2]

    def screen_h(self, A, supersample=1):
        """平面画布（supersample 倍）→ 屏幕 的单应矩阵，配合 cv2.warpPerspective 使用。"""
        return A3(A) @ self.H @ np.diag([1 / supersample, 1 / supersample, 1])


class Camera:
    """在一张大场景图上取景的虚拟摄像机：中心 (cx, cy)、取景宽度 cw，画幅比例跟随输出。"""

    def __init__(self, plate_size, out_size):
        self.pw, self.ph = plate_size
        self.W, self.H = out_size

    def matrix(self, cx, cy, cw, shake=(0.0, 0.0)):
        ch = cw * self.H / self.W
        cx = min(max(cx, cw / 2), self.pw - cw / 2)
        cy = min(max(cy, ch / 2), self.ph - ch / 2)
        s = self.W / cw
        A = np.array([[s, 0, -(cx - cw / 2) * s + shake[0]], [0, s, -(cy - ch / 2) * s + shake[1]]], np.float64)
        return A, s

    @staticmethod
    def center_x(A, s, W):
        return (W / 2 - A[0, 2]) / s

    def render_plate(self, plate, A):
        return cv2.warpAffine(plate, A.astype(np.float32), (self.W, self.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def shake(t, amount=1.5, fps=12):
    """定格节奏的镜头抖动偏移（确定性，不用随机状态）。"""
    n = int(t * fps)
    return ((n * 37) % 7 - 3) * amount, ((n * 53) % 5 - 2) * amount
