"""后期：暗角、胶片颗粒、淡入淡出、镜头号标签。"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import config

_VIG = {}


def vignette(frame, strength=0.25):
    H, W = frame.shape[:2]
    key = (H, W, strength)
    if key not in _VIG:
        yy, xx = np.mgrid[0:H, 0:W]
        _VIG[key] = (1 - strength * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2))[:, :, None].astype(np.float32)
    return frame * _VIG[key]


def grain(frame, t, fps=24, amount=0.01):
    """每帧不同但确定的颗粒（种子取帧号）。"""
    H, W = frame.shape[:2]
    return frame + np.random.default_rng(int(round(t * fps))).normal(0, amount, (H, W))[:, :, None].astype(np.float32)


def fade(frame, t, dur, fade_in=0.6, fade_out=0.6):
    k = min(1.0, t / fade_in if fade_in else 1.0) * min(1.0, (dur - t) / fade_out if fade_out else 1.0)
    return frame * max(0.0, k)


def label(frame, text, xy=(24, 24)):
    """左上角镜头号/时间码。正片关掉。"""
    img = Image.new("RGBA", (420, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, 419, 59), 10, fill=(0, 0, 0, 140))
    d.text((16, 30), text, font=ImageFont.truetype(config.FONT_UI, 30), fill=(255, 255, 255, 255), anchor="lm")
    a = np.asarray(img).astype(np.float32) / 255
    x, y = xy
    frame[y:y + 60, x:x + 420] = a[:, :, [2, 1, 0]] * a[:, :, 3:4] + frame[y:y + 60, x:x + 420] * (1 - a[:, :, 3:4])
    return frame


def to_uint8(frame):
    return (np.clip(frame, 0, 1) * 255).astype(np.uint8)
