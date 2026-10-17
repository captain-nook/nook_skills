"""质量自检：主题对比度（check-themes）和页面留白（render 后自动做）。"""
import numpy as np
from PIL import Image

import pages_hand as D

# (名称, 前景基色, 背景基色, 最低对比度)；基色是手账款的色值，深色和船票款按映射表换算
PAIRS = [("主要文字对底色", "#1B2540", "#FBF7EC", 7.0), ("次要文字对底色", "#6B6551", "#FBF7EC", 4.5),
         ("手写蓝字对底色", "#2F5BEA", "#FBF7EC", 4.5), ("注释灰字对底色", "#7D7560", "#FBF7EC", 3.5),
         ("主要文字对卡片", "#1B2540", "#FFFEF9", 7.0), ("次要文字对卡片", "#6B6551", "#FFFEF9", 4.5),
         ("红色对底色", "#E5412D", "#FBF7EC", 3.0), ("橙色强调对底色", "#E55A14", "#FBF7EC", 3.0)]


def _lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mapped(hexc, theme):
    m = {"dark": D.dark_map(), "ticket": D.TICKET_MAP}.get(theme, [])
    for a, b in m:
        if hexc.lower() == a.lower() and b.startswith("#"):
            return b
    return hexc


def check_themes():
    """返回 (表格文本, 是否全部通过)。"""
    lines, ok = [], True
    for th in ("paper", "dark", "ticket"):
        for name, fg, bg, need in PAIRS:
            f, b = mapped(fg, th), mapped(bg, th)
            c = contrast(f, b)
            good = c >= need
            ok = ok and good
            lines.append(f"{th:<6}{name:<12}{f} 对 {b}  对比度 {c:4.1f}（要求 ≥ {need}）{'' if good else '  ← 不达标'}")
    return "\n".join(lines), ok


def coverage(png, ticket=True):
    """页面墨迹占比：与底色明显不同的像素比例。船票款只量票身内容区。"""
    im = Image.open(png).convert("RGB")
    if ticket:
        im = im.crop((D.TK_X + 20, D.TK_Y + 20, D.TK_X + D.TK_W - 20, D.TK_Y + D.TK_BODY - 10))
    a = np.asarray(im).astype(int)
    flat = a.reshape(-1, 3)
    vals, counts = np.unique((flat // 8), axis=0, return_counts=True)
    bg = vals[counts.argmax()] * 8 + 4
    diff = np.abs(a - bg).sum(axis=2)
    return float((diff > 60).mean())
