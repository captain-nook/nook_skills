"""共用的页面骨架：颜色映射（深色、船票）、船票外框、手绘红框和箭头、素材取用、CSS。页型本身在 render.py。"""
import html
import math
import pathlib
import random

from PIL import Image

import pages_core as P

import paths
CN2ID = {"相机": "camera", "叶子": "leaf_twig", "邮票": "stamp", "小人困惑": "char_confused", "小人思考": "char_thinking",
         "小人开心": "char_happy", "问号气泡": "bubble_question", "火箭": "rocket", "灯泡": "bulb", "星光": "sparkle"}
_MAN = None


def libfile(name):
    """按素材库 id（或旧中文名）取贴纸文件路径；id 不存在直接报错并提示可用 id。"""
    global _MAN
    if _MAN is None:
        import json
        _MAN = {m["id"]: m for m in json.loads((paths.LIB / "manifest.json").read_text(encoding="utf-8"))["items"]}
    iid = CN2ID.get(name, name)
    if iid not in _MAN:
        raise KeyError(f"素材库里没有 id={iid}。可用 id：{', '.join(sorted(_MAN))}")
    return paths.LIB / _MAN[iid]["file"]
W, H = 1242, 1656
INK, BLUE, ORANGE, RED = "#1B2540", "#2F5BEA", "#E55A14", "#E5412D"
uri = P.uri


DARK = False
THEME = "paper"      # paper / dark / ticket；dark 由 DARK 控制
ACCOUNT = ""         # 票根上的账号名（由 render.page_html 设置）
TICKET_NO = ""       # 票号（可选，meta.no）
HAS_LOGO = True
# 颜色映射：手账（浅色）是基准，深色和船票在它上面做字符串替换。每套的色值都要过 xhs.py check-themes 的对比度自检。
DARK_KEYS = ['#FBF7EC', '#F6E7C8', '#F3EAD7', '#FFFEF9', '#1B2540', '#2F5BEA', '#FFD46A', '#FFE9A8', '#E5412D', '#7D7560', '#D9CFB4', '#F7E1BC', '#F7E7C9', '#DDE8FF', '#8FB0F0', '#FFF1C9', '#6B6551', '#CFC4A6', '#8A8470']
DARK_VALUES = ['#2E2924', '#3A332B', '#342E27', '#383129', '#F2EBDD', '#A9C7F0', 'rgba(217,119,74,.42)', 'rgba(217,119,74,.35)', '#F28C74', '#A59C8B', '#51483C', '#43392F', '#43392F', '#4A4034', '#6A5B49', '#C86A40', '#CDC3B0', '#5A5043', '#6B5F4F']   # 暖夜纸：暖灰褐底、奶油字，是手账的夜间版


def dark_map():
    return list(zip(DARK_KEYS, DARK_VALUES)) + [("rgba(60,50,20,", "rgba(0,0,0,"), ("#EAD27A", "#EAD27A")]


TICKET_MAP = [("#FBF7EC", "#EAF3FF"), ("#F6E7C8", "#CFE3FF"), ("#F3EAD7", "#DCEBFF"), ("#FFFEF9", "#FFFFFF"), ("#1B2540", "#12306B"),
           ("#2F5BEA", "#1A5FD0"), ("#FFD46A", "#8CC0FF"), ("#FFE9A8", "rgba(140,192,255,.55)"), ("#7D7560", "#5A6F9C"),
           ("#D9CFB4", "#BCD1F0"), ("#F7E1BC", "#CFE3FF"), ("#F7E7C9", "#CFE3FF"), ("#FFF1C9", "#DCEBFF"), ("#6B6551", "#4A5E86"),
           ("#CFC4A6", "#A9C3EC"), ("#8A8470", "#6F86B3"), ("rgba(60,50,20,", "rgba(18,48,107,")]
# 船票的三个颜色（外底、票根底、票根字），在颜色映射之后再替换，不会被映射改掉
TICKET_COLORS = ("#C9DDF7", "#1F6FEB", "#FFFFFF")   # 外底、票根底、票根字（船票风：蓝白）
def dark_css():
    v = dict(zip(DARK_KEYS, DARK_VALUES))
    return (f".tagc{{background:{v['#FFFEF9']}!important;border-color:{v['#8FB0F0']}!important;color:{v['#1B2540']}!important}}.nt{{color:#1A2440!important}}"
            ".abs[src*='library']{filter:brightness(.9) saturate(.92)}svg{filter:saturate(.8)}")


BARS = [26, 14, 20, 40, 14, 26, 40, 14, 26, 14]
BAR_ORANGE = 2


def rough_box(x, y, w, h, color=RED, sw=7, seed=1):
    """手绘红框：四边略歪、首尾不闭合的一笔。"""
    r = random.Random(seed)
    j = lambda: r.uniform(-5, 5)
    pts = [(x + j(), y + j()), (x + w + j(), y + j()), (x + w + j(), y + h + j()), (x + j(), y + h + j()), (x + 4 + j(), y - 6 + j())]
    d = "M" + " L".join(f"{a:.0f},{b:.0f}" for a, b in pts)
    return (f'<svg class="abs" style="left:0;top:0" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><filter id="r{seed}"><feTurbulence baseFrequency="0.03" numOctaves="2" seed="{seed}"/><feDisplacementMap in="SourceGraphic" scale="5"/></filter></defs>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" filter="url(#r{seed})"/></svg>')


def arrow(p0, p1, p2, color=BLUE, sw=9, head=40, seed=1):
    pts = []
    for i in range(31):
        t = i / 30
        pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    ang = math.atan2(p2[1] - pts[-4][1], p2[0] - pts[-4][0])
    d = "M" + " L".join(f"{a:.0f},{b:.0f}" for a, b in pts)
    for da in (2.6, -2.6):
        d += f" M{p2[0]:.0f},{p2[1]:.0f} L{p2[0] + head * math.cos(ang + da):.0f},{p2[1] + head * math.sin(ang + da):.0f}"
    return (f'<svg class="abs" style="left:0;top:0" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def img(name, x, y, w, rot=0, extra=""):
    return f'<img class="abs" src="{uri(libfile(name))}" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg);{extra}">'


def hlw(text, color="#FFE9A8"):
    """淡黄荧光衬底的词。"""
    return f'<span class="hy" style="--hy:{color}">{html.escape(text)}</span>'


CSS = """
@font-face{font-family:'NSC';src:url('%(sans)s');font-weight:100 900}
@font-face{font-family:'KAI';src:url('%(kai)s')}
*{box-sizing:border-box;margin:0;padding:0}
body{width:1242px;height:1656px;background:#FBF7EC;font-family:'NSC','Microsoft YaHei',sans-serif;color:#1B2540;position:relative;overflow:hidden}
body:before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 520px 420px at 6%% 4%%,#F6E7C8 0,transparent 70%%),radial-gradient(ellipse 480px 380px at 96%% 98%%,#F3EAD7 0,transparent 70%%)}
.abs{position:absolute}
.hand{font-family:'KAI','NSC',serif;color:%(blue)s}
.kai{font-family:'KAI','NSC',serif}
.t{position:absolute;left:70px;right:70px;font-weight:900;line-height:1.2;white-space:nowrap}
.hy{white-space:nowrap;background:linear-gradient(transparent 14%%,var(--hy) 14%%,var(--hy) 90%%,transparent 90%%);padding:0 8px;border-radius:14px}
.hl{position:relative;display:inline-block;z-index:0;padding:0 10px}
.hl .brush{position:absolute;left:-16px;width:calc(100%% + 32px);top:8%%;height:90%%;z-index:-1}
.hlt{color:#1B2540}
.shot{position:absolute;border-radius:26px;box-shadow:0 0 0 6px #fff,0 18px 44px rgba(40,50,90,.22)}
.stick{position:absolute;background:#2F5BEC;color:#fff;font-weight:900;padding:14px 38px;border-radius:12px 40px 14px 36px;box-shadow:0 8px 0 rgba(47,91,234,.25)}
.wv{display:block}
"""


def barcode_svg(color, w=230, h=84):
    k = w / (sum(BARS) + 14 * (len(BARS) - 1))
    x, rects = 0.0, ""
    for i, bw in enumerate(BARS):
        rects += f'<rect x="{x:.1f}" y="0" width="{bw * k:.1f}" height="{h}" fill="{"#E55A14" if i == BAR_ORANGE else color}"/>'
        x += (bw + 14) * k
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{rects}</svg>'


TK_W, TK_H, TK_BODY, TK_X, TK_Y, TK_R, TK_N = 1172, 1586, 1400, 35, 35, 44, 28


def ticket_path():
    W_, H_, B, R, N = TK_W, TK_H, TK_BODY, TK_R, TK_N
    return (f"M{R},0 H{W_ - R} A{R} {R} 0 0 1 {W_},{R} V{B - N} A{N} {N} 0 0 0 {W_},{B + N} V{H_ - R} A{R} {R} 0 0 1 {W_ - R},{H_} "
            f"H{R} A{R} {R} 0 0 1 0,{H_ - R} V{B + N} A{N} {N} 0 0 0 0,{B - N} V{R} A{R} {R} 0 0 1 {R},0 Z")


def ticket_wrap(body):
    scale = min((TK_W - 60) / W, TK_BODY / H)
    left = (TK_W - W * scale) / 2
    stub_h = TK_H - TK_BODY
    logo = ""
    if HAS_LOGO:
        logo = (f'<div style="background:#fff;border-radius:18px;padding:10px 14px;margin-right:26px;display:flex;align-items:center;'
                f'box-shadow:0 0 0 3px rgba(255,255,255,.35)"><img src="{uri(P.BRAND / "logo_light.png")}" style="height:84px"></div>')
    no = f'<div class="tk-no">NO.{html.escape(TICKET_NO)}</div>' if TICKET_NO else ""
    return (f'<div class="tk-shadow"><div class="ticket">'
            f'<div class="tk-body"><div class="stage" style="left:{left:.1f}px;transform:scale({scale:.4f})">{body}</div></div>'
            f'<div class="tk-line"></div>'
            f'<div class="tk-stub" style="top:{TK_BODY}px;height:{stub_h}px">{logo}<div class="tk-name">{html.escape(ACCOUNT)}{no}</div>'
            f'<div class="tk-bar">{barcode_svg("#TKTXT")}</div></div></div></div>')


TICKET_CSS = (
    f".tkb{{background:#TKOUT}}.tkb:before{{display:none}}"
    f".tk-shadow{{position:absolute;left:{TK_X}px;top:{TK_Y}px;width:{TK_W}px;height:{TK_H}px;filter:drop-shadow(0 16px 28px rgba(8,12,24,.35))}}"
    f".ticket{{position:absolute;inset:0;background:#FBF7EC;clip-path:path('{ticket_path()}');overflow:hidden}}"
    f".ticket:before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 520px 420px at 6% 4%,#F6E7C8 0,transparent 70%),radial-gradient(ellipse 480px 380px at 96% {TK_BODY * 100 // TK_H}%,#F3EAD7 0,transparent 70%)}}"
    f".tk-body{{position:absolute;left:0;top:0;width:{TK_W}px;height:{TK_BODY}px;overflow:hidden}}"
    f".stage{{position:absolute;top:0;width:{W}px;height:{H}px;transform-origin:0 0}}"
    f".tk-line{{position:absolute;left:46px;right:46px;top:{TK_BODY - 1}px;border-top:4px dashed #TKTXT;opacity:.55}}"
    f".tk-stub{{position:absolute;left:0;width:{TK_W}px;background:#TKSTUB;display:flex;align-items:center;padding:0 64px;color:#TKTXT}}"
    f".tk-name{{flex:1;font-size:40px;font-weight:800;line-height:1.3}}.tk-no{{font-size:26px;font-weight:600;opacity:.7;letter-spacing:2px}}"
    f".tk-bar{{margin-left:20px}}"
)


def base(body, page_no, extra_css=""):
    css = CSS % dict(sans=uri(P.FONT_SANS), kai=uri(P.FONT_KAI), blue=BLUE)
    ticket = THEME == "ticket"
    inner = ticket_wrap(body) if ticket else body
    out = (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}{extra_css}{dark_css() if DARK else ""}{TICKET_CSS if ticket else ""}</style></head>'
           f'<body class="{"tkb" if ticket else ""}">{inner}</body></html>')
    if DARK:
        for a, b in dark_map():
            out = out.replace(a, b)
    elif THEME == "ticket":
        for a, b in TICKET_MAP:
            out = out.replace(a, b)
    if ticket:
        o, sb, tx = TICKET_COLORS
        out = out.replace("#TKOUT", o).replace("#TKSTUB", sb).replace("#TKTXT", tx)
    return out
























