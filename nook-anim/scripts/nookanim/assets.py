"""素材：读图、锚点、对齐、虚化变体、代码生成的小贴图（星光、符号、占位剪影）。
图像约定：float32，BGRA，直通 alpha（非预乘），取值 0–1。"""
import math
import pathlib

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import config


def imread(path, flags=cv2.IMREAD_UNCHANGED):
    """中文路径安全的读图（cv2.imread 在 Windows 上读不了非 ASCII 路径，会静默返回 None）。"""
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
    except OSError:
        return None
    return cv2.imdecode(data, flags) if data.size else None


def imwrite(path, img, params=None):
    """中文路径安全的写图。"""
    ext = pathlib.Path(path).suffix or ".png"
    ok, buf = cv2.imencode(ext, img, params or [])
    if not ok:
        raise IOError(f"encode failed: {path}")
    buf.tofile(str(path))


def load(path):
    im = imread(path)
    if im is None:
        raise FileNotFoundError(path)
    im = im.astype(np.float32) / 255
    if im.ndim == 2:
        im = np.dstack([im] * 3)
    if im.shape[2] == 3:
        im = np.dstack([im, np.ones(im.shape[:2], np.float32)])
    return im


def bbox_anchor(spr, fx=0.5, fy=1.0, thr=0.1):
    """不透明区域外接框里 (fx, fy) 处的点，以及外接框宽高。fy=1 即脚底/底边。"""
    ys, xs = np.where(spr[:, :, 3] > thr)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    return (x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)), (x1 - x0, y1 - y0)


def align(img, ref, rows=None):
    """用 alpha 的相位相关把 img 平移对齐到 ref。rows 指定参与比对的行（例如头部或船身）。
    同一母版编辑出的多张图先对齐，再共用母版的锚点和缩放。"""
    sl = rows if rows is not None else slice(None)
    (dx, dy), _ = cv2.phaseCorrelate(ref[sl, :, 3], img[sl, :, 3])
    h, w = img.shape[:2]
    return cv2.warpAffine(img, np.float32([[1, 0, -dx], [0, 1, -dy]]), (w, h), borderValue=0), (dx, dy)


def depth_variant(spr, blur_plate_px, height_plate_px, dark=1.0):
    """场景道具的景深变体：按"在场景里的像素"指定虚化量，换算到素材像素。"""
    _, size = bbox_anchor(spr)
    out = cv2.GaussianBlur(spr, (0, 0), max(0.1, blur_plate_px * size[1] / height_plate_px))
    out[:, :, :3] *= dark
    return out


def _from_pil(img):
    a = np.asarray(img).astype(np.float32) / 255
    return np.dstack([a[:, :, [2, 1, 0]], a[:, :, 3]])


def star_sprite(size=256, tint=(0.45, 0.85, 1.0)):
    """四角星光，带柔光。tint 为 BGR。"""
    img = np.zeros((size, size, 4), np.float32)
    c = size / 2
    g = np.exp(-(((np.mgrid[0:size, 0:size] - c) ** 2).sum(0)) / (2 * (size * 0.16) ** 2))
    img[:, :, 3] = g * 0.5
    img[:, :, :3] = g[:, :, None] * 0.5 * np.array(tint)
    pts = [[c + (size * 0.46 if i % 2 == 0 else size * 0.07) * math.cos(i * math.pi / 4 - math.pi / 2),
            c + (size * 0.46 if i % 2 == 0 else size * 0.07) * math.sin(i * math.pi / 4 - math.pi / 2)] for i in range(8)]
    m = np.zeros((size * 4, size * 4), np.uint8)
    cv2.fillPoly(m, [(np.array(pts) * 4).astype(np.int32)], 255, cv2.LINE_AA)
    m = cv2.resize(m, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32)[:, :, None] / 255
    return img * (1 - m) + m * np.array([0.6, 0.95, 1, 1], np.float32)


def symbol_sprite(ch="?", color=(30, 91, 216), stroke=(255, 255, 255), size=230, font=None):
    """弹出符号（？！♪ 等），color/stroke 为 RGB。锚点建议取 (宽/2, 高)。"""
    img = Image.new("RGBA", (int(size * 0.9), int(size * 1.2)), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((img.width / 2, img.height / 2), ch, font=ImageFont.truetype(font or config.FONT_UI, size),
                             fill=color + (255,), anchor="mm", stroke_width=max(2, size // 19), stroke_fill=stroke + (255,))
    return _from_pil(img)


def placeholder(base, label):
    """灰色剪影占位：用 base 的轮廓，中间写姿势编号。动态分镜里素材未到位时用。"""
    a = base[:, :, 3]
    edge = cv2.morphologyEx((a > 0.5).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((7, 7), np.uint8)).astype(np.float32)
    rgb = np.dstack([np.full_like(a, 0.62)] * 3) * (1 - edge[:, :, None]) + 0.35 * edge[:, :, None]
    img = Image.fromarray((np.dstack([rgb, a]) * 255).astype(np.uint8), "RGBA")
    ImageDraw.Draw(img).text((img.width / 2, img.height / 2), label, font=ImageFont.truetype(config.FONT_UI, max(24, img.width // 16)),
                             fill=(255, 255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(60, 60, 60, 255))
    return np.asarray(img).astype(np.float32) / 255
