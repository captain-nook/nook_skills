"""水墨 / 水彩风格模块（风格卡 06）：生宣纸纹理、墨滴渗化晕染、书法枯笔飞白、写意水波与朱砂印章。

特性：
1. 生宣纸纹：长纤交织纤维、大尺度吸水斑驳、象牙/古纸微黄暖调。
2. 墨滴动态晕染（ink_bleed）：基于毛细渗化物理模拟的墨汁扩散，核心焦墨，外缘淡晕与纤维毛边。
3. 水墨书法飞白笔触（calligraphic_stroke）：提按顿挫、行笔枯笔拉丝与纸白透出。
4. 写意水面波纹（water_ripples）：正弦微波起伏。
5. 水墨图层（InkCanvas）：支持焦、浓、重、淡、清五色墨分与朱砂印泥正片叠底。
"""
import math
import cv2
import numpy as np
from .draw import multiply
from .geom import A3

# 传统国画墨色五分与朱砂
INK_BURNT  = np.array([0.08, 0.08, 0.08], np.float32)  # 焦墨（极浓黑）
INK_THICK  = np.array([0.16, 0.16, 0.16], np.float32)  # 浓墨
INK_HEAVY  = np.array([0.28, 0.28, 0.29], np.float32)  # 重墨
INK_LIGHT  = np.array([0.55, 0.55, 0.57], np.float32)  # 淡墨（远山、烟雾）
INK_PALE   = np.array([0.75, 0.76, 0.78], np.float32)  # 清墨（水汽、倒影）
SEAL_RED   = np.array([0.16, 0.18, 0.72], np.float32)  # 朱砂印泥（BGR）

# 纸张底色：特制温润生宣（米黄微象牙）
XUAN_ANTIQUE = (230, 240, 246)  # BGR 暖古白
XUAN_WARM    = (238, 245, 250)  # BGR 米宣白


def xuan_paper(w, h, seed=42, base=XUAN_ANTIQUE):
    """生宣纸纹理：横纵交织的韧皮植物纤维 + 吸水斑驳 + 微黄润色。返回 float32 [0, 1] BGR。"""
    rng = np.random.default_rng(seed)
    # 纵向长纤维
    fib_v = cv2.GaussianBlur(rng.random((h // 4 + 1, w // 4 + 1)).astype(np.float32), (0, 0), sigmaX=0.9, sigmaY=8.0)
    fib_v = cv2.resize(fib_v, (w, h), interpolation=cv2.INTER_LINEAR)
    fib_v = (fib_v - fib_v.min()) / (fib_v.max() - fib_v.min() + 1e-9)

    # 横向纤维交错
    fib_h = cv2.GaussianBlur(rng.random((h // 4 + 1, w // 4 + 1)).astype(np.float32), (0, 0), sigmaX=7.0, sigmaY=0.8)
    fib_h = cv2.resize(fib_h, (w, h), interpolation=cv2.INTER_LINEAR)
    fib_h = (fib_h - fib_h.min()) / (fib_h.max() - fib_h.min() + 1e-9)

    # 纸浆棉絮斑驳（大尺度）
    mott = cv2.GaussianBlur(rng.random((h // 48 + 2, w // 48 + 2)).astype(np.float32), (0, 0), 2.0)
    mott = cv2.resize(mott, (w, h), interpolation=cv2.INTER_CUBIC)
    mott = (mott - mott.min()) / (mott.max() - mott.min() + 1e-9)

    img = np.ones((h, w, 3), np.float32) * (np.array(base, np.float32) / 255.0)
    texture = (0.95 + 0.025 * fib_v[:, :, None] + 0.025 * fib_h[:, :, None]) * (0.97 + 0.03 * mott[:, :, None])
    return np.clip(img * texture, 0.0, 1.0)


def ink_diffusion_mask(h, w, center, radius, seed=101, roughness=0.35, blur_radius=7):
    """计算单个墨点沿生宣纤维毛细渗透晕染的遮罩 (float32, 0~1)。

    中心呈焦墨饱和，外圈随半径扩散衰减，边缘受微纤维毛细扰动产生不规则毛边。
    """
    if radius <= 0.5:
        return np.zeros((h, w), np.float32)

    cx, cy = center
    rng = np.random.default_rng(seed)

    # 局部范围以节省计算开销
    pad = int(radius * 1.8) + blur_radius * 2
    x0, x1 = max(0, int(cx - pad)), min(w, int(cx + pad))
    y0, y1 = max(0, int(cy - pad)), min(h, int(cy + pad))
    if x1 <= x0 or y1 <= y0:
        return np.zeros((h, w), np.float32)

    lw, lh = x1 - x0, y1 - y0
    yy, xx = np.ogrid[y0:y1, x0:x1]
    dx = xx - cx
    dy = yy - cy
    dist = np.sqrt(dx * dx + dy * dy)

    # 极坐标噪声扰动边缘
    angle = np.arctan2(dy, dx)
    # 多阶谐波模拟墨滴边缘星状渗化
    noise = (
        0.55 * np.sin(3 * angle + rng.uniform(0, 6.28)) +
        0.25 * np.sin(7 * angle + rng.uniform(0, 6.28)) +
        0.20 * np.sin(13 * angle + rng.uniform(0, 6.28))
    )
    dist_perturbed = dist / (1.0 + roughness * noise)

    # 径向衰减分布：中心平坦焦黑，边缘渗化
    core_r = radius * 0.45
    norm_d = np.clip((dist_perturbed - core_r) / max(1e-3, radius - core_r), 0.0, 1.0)
    density = np.clip(1.0 - norm_d ** 1.3, 0.0, 1.0)

    # 湿润边缘模糊渗出
    if blur_radius > 0:
        k = blur_radius * 2 + 1
        density = cv2.GaussianBlur(density, (k, k), blur_radius * 0.6)

    mask = np.zeros((h, w), np.float32)
    mask[y0:y1, x0:x1] = density
    return mask


def water_ripples(h, w, t, base_y=900, amp=12.0, n_waves=4, seed=303):
    """写意水墨水面波纹，返回波纹线条坐标点集列表。"""
    waves = []
    rng = np.random.default_rng(seed)
    for i in range(n_waves):
        y_center = base_y + i * 45
        freq = 0.0035 + i * 0.001
        speed = 1.2 - i * 0.15
        phase = rng.uniform(0, 6.28) + t * speed

        # 波纹分段留白：不是一条通栏死线，而是断续写意笔调
        x_start = int(rng.uniform(50, 250))
        x_end = int(w - rng.uniform(50, 250))
        xs = np.linspace(x_start, x_end, int((x_end - x_start) / 8))
        ys = y_center + amp * np.sin(xs * freq + phase) * (0.8 + 0.2 * np.sin(xs * 0.001))

        # 中断留白
        mask = (np.sin(xs * 0.008 + rng.uniform(0, 6.28)) > -0.2)
        if np.any(mask):
            pts = np.column_stack([xs[mask], ys[mask]])
            waves.append(pts)
    return waves


class InkCanvas:
    """水墨写意画布：负责分层墨汁叠加与正片叠底。"""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.mask_buffer = np.zeros((h, w), np.float32)

    def add_mask(self, mask, weight=1.0):
        """累加墨水密度。"""
        if mask is not None:
            self.mask_buffer = np.clip(self.mask_buffer + mask * weight, 0.0, 1.0)

    def draw_brush_stroke(self, pts, width=8.0, flying_white=True, seed=42):
        """书法枯笔飞白笔触：沿点集绘制，带有提按顿挫与飞白拉丝效果。"""
        if pts is None or len(pts) < 2:
            return
        pts = np.asarray(pts, dtype=np.float32)
        n = len(pts)

        # 临时单通道掩膜
        stroke_img = np.zeros((self.h, self.w), np.uint8)
        rng = np.random.default_rng(seed)

        # 沿路径按段绘制可变线宽
        for i in range(n - 1):
            f = i / max(1, n - 1)
            # 提按曲线：起笔稍重、行笔稍轻、收笔顿笔
            pressure = 0.8 + 0.4 * math.sin(f * math.pi)
            seg_w = max(1, int(width * pressure))

            p1 = (int(round(pts[i][0])), int(round(pts[i][1])))
            p2 = (int(round(pts[i + 1][0])), int(round(pts[i + 1][1])))
            cv2.line(stroke_img, p1, p2, 255, seg_w, cv2.LINE_AA)

        m = stroke_img.astype(np.float32) / 255.0

        # 枯笔飞白：在笔画较宽的内部产生细长平行拉丝孔隙
        if flying_white and width >= 4.0:
            noise_strip = rng.random((self.h // 2 + 1, self.w // 2 + 1)).astype(np.float32)
            noise_strip = cv2.GaussianBlur(noise_strip, (0, 0), sigmaX=8.0, sigmaY=0.6)
            noise_strip = cv2.resize(noise_strip, (self.w, self.h))
            white_mask = (noise_strip > 0.62).astype(np.float32)
            # 仅在较粗区域发生飞白，且边缘保留墨线
            inner_core = cv2.erode(m, np.ones((3, 3), np.uint8), iterations=1)
            m = np.clip(m - inner_core * white_mask * 0.45, 0.0, 1.0)

        # 边缘微渗化
        m = cv2.GaussianBlur(m, (3, 3), 0.8)
        self.mask_buffer = np.clip(self.mask_buffer + m, 0.0, 1.0)

    def render_to(self, base_paper, ink_color=INK_BURNT, alpha=1.0):
        """将当前墨色正片叠底应用到生宣纸上。"""
        m = self.mask_buffer * alpha
        return multiply(base_paper, m, np.array(ink_color, np.float32))
