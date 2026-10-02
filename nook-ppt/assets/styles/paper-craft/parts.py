"""「纸片手作」的专用零件：撕边纸片（现画 PNG：撕边、纤维白边、纸纹、投影）和纸片卡。
    paper_card(deck, s, rect, title, body=None, bullets=None, color="card", rot=0.0, tape=None, ...)
纸片 PNG 缓存在 ST/_cache/，同尺寸同颜色同种子只画一次。
"""
import hashlib
import pathlib

import cv2
import numpy as np
from PIL import Image

from theme import ST, THEME

CACHE = ST / "_cache"
SC = 3            # 每 pt 画多少像素


def _hex(c):
    c = THEME.get(c, c).lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _edge(n, rng, amp):
    """一条边的抖动：低频起伏加高频毛刺。"""
    low = np.convolve(rng.normal(0, 1, n + 40), np.ones(20) / 20, "same")[20:n + 20] * amp * 2.2
    high = rng.normal(0, 1, n) * amp * 0.45
    return low + high


def torn_paper(w, h, color="card", seed=1, margin=14, amp=2.2, rim=4.0):
    """返回一张撕边纸片 PNG 的路径，尺寸 (w+2*margin, h+2*margin) pt。"""
    key = hashlib.md5(f"{w:.0f}{h:.0f}{color}{seed}{margin}{amp}{rim}".encode()).hexdigest()[:12]
    CACHE.mkdir(exist_ok=True)
    out = CACHE / f"paper_{key}.png"
    if out.exists():
        return out
    rng = np.random.default_rng(seed)
    W, H, m = int((w + 2 * margin) * SC), int((h + 2 * margin) * SC), int(margin * SC)
    x0, y0, x1, y1 = m, m, W - m, H - m
    a = amp * SC
    pts = []
    for x in range(x0, x1, 6):
        pts.append((x, y0))
    n_top = len(pts)
    top = _edge(n_top, rng, a)
    pts = [(px, y0 + top[i]) for i, (px, _) in enumerate(pts)]
    right_y = list(range(y0, y1, 6))
    rt = _edge(len(right_y), rng, a)
    pts += [(x1 + rt[i], py) for i, py in enumerate(right_y)]
    bot_x = list(range(x1, x0, -6))
    bt = _edge(len(bot_x), rng, a)
    pts += [(px, y1 + bt[i]) for i, px in enumerate(bot_x)]
    left_y = list(range(y1, y0, -6))
    lt = _edge(len(left_y), rng, a)
    pts += [(x0 + lt[i], py) for i, py in enumerate(left_y)]
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, [np.array(pts, np.int32)], 255)
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
    # 纤维白边：外圈比纸色更浅，边缘不规则
    inner = cv2.erode(mask, np.ones((int(rim * SC), int(rim * SC)), np.uint8))
    noise = cv2.GaussianBlur(rng.random((H, W)).astype(np.float32), (0, 0), 2.0)
    inner = (inner.astype(np.float32) * (0.75 + 0.5 * noise)).clip(0, 255).astype(np.uint8)
    base = np.array(_hex(color), np.float32)
    rim_col = np.array([250, 247, 240], np.float32)
    k = (inner.astype(np.float32) / 255.0)[..., None]
    rgb = rim_col * (1 - k) + base * k
    # 纸纹
    grain = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2) * 5 + cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 14) * 9
    rgb = np.clip(rgb + grain[..., None], 0, 255)
    # 投影：向右下偏移的柔和阴影
    sh = np.roll(np.roll(mask, int(5 * SC), 0), int(3 * SC), 1).astype(np.float32)
    sh = cv2.GaussianBlur(sh, (0, 0), 6 * SC / 3) * 0.32
    al = mask.astype(np.float32)
    out_a = np.clip(al + sh * (1 - al / 255.0), 0, 255)
    col = (rgb * (al / 255.0)[..., None] + np.zeros_like(rgb) * (1 - al / 255.0)[..., None])
    Image.fromarray(np.dstack([col, out_a]).astype(np.uint8), "RGBA").save(out)
    return out


def paper_card(deck, s, rect, title, body=None, bullets=None, color="card", rot=0.0, title_size=28, body_size=21, name="纸片", anchor="top",
               seed=None, tape=None, anim=("fade", "beat", 0, 0.45), pad=22):
    """一张撕边纸片卡：纸片 PNG 加文字，成组后可整体微旋转。tape=颜色名时在上沿贴一条胶带。"""
    from slidekit import MSO_SHAPE  # noqa
    x, y, w, h = rect
    seed = seed if seed is not None else (abs(hash((title, round(w), round(h)))) % 9973)
    png = torn_paper(w, h, color, seed)
    m = 14
    pic = deck.picture(s, (x - m, y - m, w + 2 * m, h + 2 * m), png, f"纸片 {title}", name=name + "纸")
    paras = []
    if title:
        paras.append(dict(text=title, size=title_size, bold=True, after=6))
    for line in ([body] if isinstance(body, str) else (body or [])):
        paras.append(dict(text=line, size=body_size, color=deck.t["sub"], after=4))
    for b in bullets or []:
        paras.append(dict(text=b, size=body_size, color=deck.t["ink"], bullet=True, after=4))
    py = pad if h >= 120 else 8
    members = [pic]
    if paras:
        tx = deck.text(s, (x + pad, y + py - 4, w - 2 * pad, h - 2 * py + 4), paras, anchor=anchor, name=name + "字", inset=0, anim=None)
        members.append(tx)
    grp = s.shapes.add_group_shape(members)
    deck.uname(s, grp, f"{name}组·{title or ''}")
    if rot:
        grp.rotation = rot
    deck.occupy(s, rect, f"纸片「{title}」")
    if anim:
        deck.A(s, grp.name, *anim)
    return grp
