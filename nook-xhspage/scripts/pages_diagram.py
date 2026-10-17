"""手绘形状工具（抖边多边形、圆角矩形、箭头头、SVG 外壳、素材引用），图示页型在 render.py 里用。"""
import html
import json
import math
import pathlib
import random

import pages_core as P
import pages_hand as D
from pages_hand import uri, base, INK, ORANGE

import paths
LIB = paths.LIB
MAN = {m["id"]: m for m in json.loads((LIB / "manifest.json").read_text(encoding="utf-8"))["items"]}
OR, BL, TE, YE, DK = "#E55A14", "#2F5BEC", "#1FA38A", "#F5B82E", "#1A2440"   # 平涂色（深色款映射表里不动它们）
W, H = 1242, 1656


def asset(iid):
    if iid not in MAN:
        raise KeyError(f"素材库里没有 id={iid}，可用 id 见 manifest.json")
    return uri(LIB / MAN[iid]["file"])


def st(iid, x, y, w, rot=0):
    return f'<img class="abs" src="{asset(iid)}" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg)">'


def jitter_poly(pts, seed, amp=4):
    r = random.Random(seed)
    return [(x + r.uniform(-amp, amp), y + r.uniform(-amp, amp)) for x, y in pts]


def rough(pts, fill, seed, sw=7, stroke=INK, closed=True):
    q = jitter_poly(pts, seed)
    d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in q) + (" Z" if closed else "")
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" filter="url(#ro{seed % 7})"/>')


def rrect_pts(x, y, w, h, r=26, n=5):
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def svg(inner, h=H):
    defs = "".join(f'<filter id="ro{i}"><feTurbulence baseFrequency="0.028" numOctaves="2" seed="{i + 3}"/><feDisplacementMap in="SourceGraphic" scale="6"/></filter>' for i in range(7))
    return f'<svg class="abs" style="left:0;top:0" width="{W}" height="{h}" xmlns="http://www.w3.org/2000/svg"><defs>{defs}</defs>{inner}</svg>'


def arrowhead(p, q, size=34, color=INK, sw=9):
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    a = (q[0] + size * math.cos(ang + 2.6), q[1] + size * math.sin(ang + 2.6))
    b = (q[0] + size * math.cos(ang - 2.6), q[1] + size * math.sin(ang - 2.6))
    return f'<path d="M{a[0]:.0f},{a[1]:.0f} L{q[0]:.0f},{q[1]:.0f} L{b[0]:.0f},{b[1]:.0f}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'






def txt(x, y, text, size, w=900, weight=900, color="#FFFFFF", align="center", kai=False, extra=""):
    ff = "font-family:KAI,NSC,serif;" if kai else ""
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;text-align:{align};font-size:{size}px;font-weight:{weight};color:{color};line-height:1.2;{ff}{extra}">{text}</div>')















