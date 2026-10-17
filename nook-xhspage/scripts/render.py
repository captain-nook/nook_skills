"""渲染：把校验通过的方案 JSON 画成 PNG。每个页型一个函数，读 fields，不含任何写死的文案。"""
import html
import math
import pathlib
import re

from PIL import Image

import pages_core as P
import pages_hand as D
import pages_diagram as G
from pages_hand import uri, img, base, INK, BLUE, ORANGE, rough_box, arrow, libfile
from pages_diagram import rough, rrect_pts, svg, arrowhead, txt, jitter_poly

W, H = 1242, 1656
OR, BLU, TE, YE, DK = G.OR, G.BL, G.TE, G.YE, G.DK
BASE_DIR = pathlib.Path(".")


# ---------- 文字工具 ----------
def esc(s):
    return html.escape(str(s))


def T(text, seed=1, color="#FFD46A"):
    """含 [[词]] 的文字 -> 高亮词带毛笔衬底；不含则原样。"""
    text = str(text)
    m = re.search(r"\[\[(.+?)\]\]", text)
    if not m:
        return esc(text)
    a, w, b = text[:m.start()], m.group(1), text[m.end():]
    return f'{esc(a)}<span class="hl"><span class="hlt">{esc(w)}</span>{P.brush_svg(seed, color)}</span>{esc(b)}'


def plain(text):
    return re.sub(r"\[\[(.+?)\]\]", r"\1", str(text))


def title(text, seed=1, top=130, size=104):
    return f'<div class="t" style="top:{top}px;font-size:{size}px">{T(text, seed)}</div>'


def note(text, x=70, y=1560, size=58):
    return f'<div class="abs kai" style="left:{x}px;top:{y}px;font-size:{size}px;color:#2F5BEA">{esc(text)}</div>'


def wave(x, y, w, seed=1, color=ORANGE, sw=9):
    pts = " ".join(f"{'M' if i == 0 else 'L'}{i * 6},{14 + 7 * math.sin(i * 0.5 + seed):.1f}" for i in range(int(w / 6)))
    return f'<svg class="abs" style="left:{x}px;top:{y}px" width="{w}" height="28"><path d="{pts}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def stickers(ids, slots):
    out = ""
    for iid, (x, y, w, rot) in zip(ids or [], slots):
        out += img(iid, x, y, w, rot)
    return out


def _brand():
    import brand
    return brand.load() or dict(account=brand.DEFAULT_ACCOUNT, has_person=True, has_logo=True)


def pose_img(pose, **style):
    if not _brand()["has_person"]:
        return ""
    st = ";".join(f"{k.replace('_', '-')}:{v}" for k, v in style.items())
    return f'<img class="abs" src="{uri(P.POSE[pose])}" style="{st}">'


def logo():
    if D.THEME == "ticket" or not _brand()["has_logo"]:
        return ""
    name = "logo_dark.png" if D.DARK else "logo_light.png"
    return f'<img class="abs" src="{uri(P.BRAND / name)}" style="left:70px;bottom:56px;width:120px">'


def tagline(text):
    if D.THEME == "ticket":
        return ""      # 账号名已经印在票根上
    return (f'<div class="abs tagc" style="left:70px;top:70px;display:flex;align-items:center;gap:12px;font-size:36px;font-weight:800;color:#1A2440;'
            f'background:#FEFEFE;border:4px solid #1A2440;border-radius:40px 14px 40px 14px;padding:8px 28px;transform:rotate(-2deg)">'
            f'<i style="width:20px;height:20px;border-radius:50%;background:{ORANGE};display:inline-block"></i>{esc(text)}</div>')




def hlw_line(x):
    """荧光黄衬底的高亮（提示词页用淡色，不用毛笔）。"""
    m = re.search(r"\[\[(.+?)\]\]", x)
    if not m:
        return esc(x)
    return esc(x[:m.start()]) + D.hlw(m.group(1)) + esc(x[m.end():])


# ---------- 封面 ----------
def cover_list(f, n, N):
    items = f["items"]
    rows = "".join(
        f'<div class="r"><span class="hand n">{i + 1}</span><span class="nm">{esc(t)}</span>'
        f'<svg width="62" height="62" viewBox="0 0 84 84"><rect x="6" y="8" width="70" height="68" rx="12" fill="none" stroke="{INK}" stroke-width="7"/>'
        f'<path d="M18,44 L36,64 L88,6" fill="none" stroke="{ORANGE}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
        for i, t in enumerate(items))
    rh = int(610 / len(items))
    css = (f".r{{display:flex;align-items:center;gap:26px;height:{rh}px;border-bottom:4px dashed #D9CFB4}}.r .n{{font-size:84px;width:70px;text-align:center;font-weight:700}}"
           ".r .nm{flex:1;font-size:54px;font-weight:900;white-space:nowrap}.cardA{position:absolute;left:70px;top:700px;width:760px;background:#FFFEF9;border:5px solid #1B2540;border-radius:34px;padding:20px 40px;transform:rotate(-1deg);box-shadow:0 14px 34px rgba(60,50,20,.16)}")
    num = str(f["number"])
    ux = 60 + 250 * len(num) + 60
    circle = (f'<svg class="abs" style="left:50px;top:320px" width="320" height="400" viewBox="0 0 320 400"><path d="M200,28 C300,30 316,150 296,260 C280,360 120,390 50,330" fill="none" stroke="#E5412D" stroke-width="9" stroke-linecap="round" transform="rotate(-6 160 200)"/></svg>'
              if len(num) == 1 else "")
    body = (tagline(_brand()["account"]) + f'<div class="t" style="top:190px;font-size:100px">{esc(f["lead"])}</div>'
            + f'<div class="abs" style="left:60px;top:300px;font-size:430px;font-weight:900;line-height:1;color:{ORANGE}">{esc(num)}</div>' + circle
            + f'<div class="t" style="left:{ux}px;top:450px;font-size:136px">{T("[[" + f["unit"] + "]]", 3)}</div>'
            + f'<div class="cardA">{rows}</div>' + stickers([f["sticker"]] if f.get("sticker") else [], [(930, 120, 270, 8)])
            + pose_img(f.get("pose", "c"), right="-30px", bottom="-130px", width="470px")
            + (f'<div class="abs kai" style="left:230px;top:1560px;font-size:56px;color:{BLUE}">{esc(f["footnote"])}</div>' if f.get("footnote") else "") + logo())
    return base(body, n, css)


def cover_person(f, n, N):
    nt = f.get("note")
    sticky = ""
    if nt:
        lines = "<br>".join("✓ " + esc(x) for x in nt["items"])
        sticky = (f'<div class="abs nt" style="left:70px;top:1090px;width:420px;color:#1A2440;background:#FFF0AE;border:4px solid #EAD27A;padding:30px 36px;font-size:50px;font-weight:700;line-height:1.6;transform:rotate(-4deg);box-shadow:0 12px 28px rgba(60,50,20,.2)">'
                  f'<div class="kai" style="font-size:46px;margin-bottom:6px;color:#1A2440">{esc(nt["title"])}：</div>{lines}</div>')
    body = (tagline(_brand()["account"])
            + '<div class="abs" style="right:-160px;bottom:-120px;width:760px;height:760px;border-radius:50%;background:#F7E1BC"></div>'
            + pose_img(f.get("pose", "a"), right="-40px", bottom="-175px", width="525px")
            + f'<div class="t" style="top:190px;font-size:210px;line-height:1.12">{esc(f["line1"])}<br>{T(f["line2"], 5)}</div>'
            + '<svg class="abs" style="left:70px;top:640px" width="760" height="30"><path d="M6,16 C70,2 130,30 200,14 S330,2 400,16 S530,30 610,12 S720,6 754,14" fill="none" stroke="#E5412D" stroke-width="12" stroke-linecap="round"/></svg>'
            + f'<div class="abs kai" style="left:70px;top:740px;font-size:74px;color:{BLUE};line-height:1.5">{esc(f["sub1"])}<br>{esc(f["sub2"])}</div>'
            + sticky + stickers(f.get("stickers"), [(870, 130, 260, 10), (1050, 70, 150, 0)]) + logo())
    return base(body, n)


def cover_quote(f, n, N):
    ln = f["lines"]
    inner = "".join(f"<br>{T(x, 8)}" if i else T(x, 8) for i, x in enumerate(ln))
    face = ""
    body = (tagline(_brand()["account"])
            + f'<svg class="abs" style="left:70px;top:210px" width="190" height="200" viewBox="0 0 190 200"><polygon points="10,10 80,10 62,120 18,120" fill="{ORANGE}"/><polygon points="108,10 178,10 160,120 116,120" fill="{ORANGE}"/></svg>'
            + f'<div class="t" style="top:430px;font-size:206px;line-height:1.1">{inner}</div>'
            + wave(70, 1388, 700, 3)
            + (f'<div class="abs kai" style="left:230px;top:1500px;font-size:58px;color:{BLUE}">{esc(f["caption"])}</div>' if f.get("caption") else "")
            + (f'<div class="abs" style="right:70px;bottom:60px;width:290px;height:290px;border-radius:50%;background:#F7E1BC;border:9px solid #fff;box-shadow:0 10px 28px rgba(60,50,20,.2);overflow:hidden">'
               f'<img src="{uri(P.POSE[f.get("face", "a")])}" style="position:absolute;left:-60px;top:-20px;width:420px"></div>' if _brand()["has_person"] else "")
            + stickers(f.get("stickers"), [(960, 200, 220, 8)]) + logo())
    return base(body, n)


# ---------- 内页（手账） ----------
def step(f, n, N):
    shot = BASE_DIR / f["screenshot"]
    iw, ih = Image.open(shot).size
    sy = 690
    sw = int(min(1102, (1450 - sy) * iw / ih))
    sh = int(ih * sw / iw)
    sx = (W - sw) // 2
    inner = ""
    if f.get("red_box"):
        x, y, w, h = f["red_box"]
        inner += rough_box(sx + x * sw, sy + y * sh, w * sw, h * sh, seed=3)
    if f.get("arrow"):
        a, b = f["arrow"]["from"], f["arrow"]["to"]
        p0, p2 = (sx + a[0] * sw, sy + a[1] * sh), (sx + b[0] * sw, sy + b[1] * sh)
        mid = ((p0[0] + p2[0]) / 2 - 40, (p0[1] + p2[1]) / 2 - 60)
        inner += arrow(p0, mid, p2, color=BLUE, seed=1)
    lab = f'<div class="stick" style="right:70px;top:610px;font-size:50px;transform:rotate(-6deg)">{esc(f["label"])}</div>' if f.get("label") else ""
    body = (f'<div class="abs hand" style="left:64px;top:78px;font-size:230px;line-height:1;font-weight:700;transform:rotate(-4deg)">Step {f["step_no"]}</div>'
            f'<svg class="abs" style="left:70px;top:300px" width="560" height="40" viewBox="0 0 560 40"><path d="M6,26 C120,8 300,36 552,14" fill="none" stroke="{BLUE}" stroke-width="12" stroke-linecap="round" opacity=".55"/></svg>'
            f'<div class="t" style="top:352px;font-size:104px">{esc(f["title"])}</div>'
            f'<div class="abs" style="left:70px;top:520px;display:flex;align-items:center;gap:22px;font-size:46px;font-weight:700">'
            f'<span style="width:74px;height:74px;border-radius:50%;background:#2F5BEC;display:flex;align-items:center;justify-content:center;color:#fff;font-size:46px">✓</span>{esc(f["subtitle"])}</div>'
            f'<img class="shot" src="{uri(shot)}" style="left:{sx}px;top:{sy}px;width:{sw}px;transform:rotate(-1deg)">' + inner + lab
            + stickers(f.get("stickers"), [(40, 1380, 250, -6), (1000, 1400, 230, 8)]))
    return base(body, n)


def prompt(f, n, N):
    lines = "".join(f'<div style="margin-bottom:26px">{hlw_line(x)}</div>' for x in f["body"])
    sb = f.get("storyboard")
    box_h = 640 if sb else 1000
    story = ""
    if sb:
        cells = ""
        for i, c in enumerate(sb):
            cells += (f'<div style="text-align:center;position:relative"><img src="{uri(libfile(c["sticker"]))}" width="300"><div class="pill2">{esc(c["label"])}</div></div>')
            if i < 2:
                cells += f'<div class="hand" style="font-size:80px;margin-bottom:110px">→</div>'
        story = f'<div class="abs" style="left:60px;top:1030px;display:flex;align-items:flex-end;gap:6px">{cells}</div>'
    css = ".pill2{display:inline-block;margin-top:-6px;background:#DDE8FF;border:4px solid #8FB0F0;border-radius:40px;padding:6px 34px;font-size:48px;font-weight:900}"
    body = (f'<div class="t" style="top:120px;font-size:128px">{T(f["title"], 4)}</div>'
            f'<div class="abs" style="left:70px;top:340px;width:1102px;height:{box_h}px;border:5px solid {INK};border-radius:36px;background:#FFFEF9"></div>'
            f'<div class="abs" style="left:100px;top:300px;background:#FFF1C9;border:5px solid {INK};border-radius:22px;padding:8px 30px;font-size:54px;font-weight:900;display:flex;gap:14px;align-items:center">'
            f'<span style="font-size:50px">💡</span>{esc(f.get("tag", "提示词"))}</div>'
            f'<div class="abs fit" style="left:120px;top:420px;width:790px;height:{box_h - 120}px;overflow:hidden;font-size:58px;font-weight:800;line-height:1.5">{lines}</div>'
            + (img(f["sticker"], 880, 760, 320, 4) if f.get("sticker") else "") + story)
    return base(body, n, css)


def idea(f, n, N):
    ln = f["lines"]
    big = "<br>".join(T(x, 7) for x in ln)
    cap = "<br>".join(esc(x) for x in f.get("caption", []))
    off = 0 if (cap or f.get("stickers")) else 190
    body = (f'<div class="t" style="top:{170 + off}px;font-size:150px;line-height:1.28">{big}</div>' + wave(70, 880 + off, 640, 2, sw=10)
            + (f'<div class="abs kai" style="left:70px;top:960px;font-size:70px;color:{BLUE};line-height:1.5">{cap}</div>' if cap else "")
            + stickers(f.get("stickers"), [(840, 120, 330, 8), (700, 1130, 480, -3)]))
    return base(body, n)


def list_page(f, n, N):
    items = f["items"]
    rh = 1060 // len(items)
    rows = ""
    for i, it in enumerate(items):
        rows += (f'<div class="row" style="height:{rh}px"><div class="hand no">{i + 1}</div><div class="rt"><div class="a">{esc(it["name"])}</div><div class="b kai">{esc(it["desc"])}</div></div>'
                 f'<svg class="ck" width="84" height="84" viewBox="0 0 84 84"><rect x="6" y="8" width="70" height="68" rx="12" fill="none" stroke="{INK}" stroke-width="6"/>'
                 f'<path d="M18,44 L36,64 L88,6" fill="none" stroke="{ORANGE}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')
    css = (".row{display:flex;align-items:center;gap:34px;border-bottom:4px dashed #D9CFB4}.no{font-size:132px;width:110px;text-align:center;font-weight:700}"
           ".rt{flex:1}.a{font-size:80px;font-weight:900;white-space:nowrap}.b{font-size:50px;color:#6B6551;margin-top:6px;white-space:nowrap}.ck{flex:none}")
    body = (title(f["title"], 12, 120, 128) + f'<div class="abs" style="left:70px;top:340px;width:1102px">{rows}</div>'
            + stickers(f.get("stickers"), [(980, 1440, 190, 12), (60, 1450, 190, -3)])
            + (f'<div class="abs kai" style="left:290px;top:1520px;font-size:58px;color:{BLUE}">{esc(f["footnote"])}</div>' if f.get("footnote") else ""))
    return base(body, n, css)


def compare(f, n, N):
    def col(x, side, mark, color):
        li = "".join(f'<div class="li">{esc(t)}</div>' for t in side["points"])
        return (f'<div class="abs" style="left:{x}px;top:380px;width:520px"><div class="tg" style="background:{color}">{esc(side["tag"])}</div>'
                f'<img src="{uri(libfile(side["sticker"]))}" width="470" style="display:block;margin:10px auto 0"><div class="ls">{li}</div></div>'
                f'<div class="abs hand" style="left:{x + 400}px;top:360px;font-size:150px;color:{D.RED if mark == "✕" else ORANGE};transform:rotate(8deg)">{mark}</div>')
    css = (".tg{display:inline-block;color:#fff;font-size:54px;font-weight:900;padding:10px 44px;border-radius:14px 40px 16px 38px;transform:rotate(-3deg)}"
           ".ls{margin-top:10px}.li{font-size:52px;font-weight:800;line-height:1.35;margin-bottom:34px;white-space:nowrap}")
    body = (title(f["title"], 15, 120, 128) + col(60, f["left"], "✕", "#8A8470") + col(660, f["right"], "✓", "#2F5BEC")
            + '<svg class="abs" style="left:600px;top:380px" width="20" height="900"><path d="M10,0 C2,150 18,300 8,450 S16,750 10,900" fill="none" stroke="#CFC4A6" stroke-width="6" stroke-dasharray="4 18" stroke-linecap="round"/></svg>'
            + (f'<div class="abs kai" style="left:70px;top:1490px;font-size:68px;color:{BLUE}">{esc(f["footer"])}</div>' + wave(70, 1580, 560, 4) if f.get("footer") else ""))
    return base(body, n, css)


def result(f, n, N):
    css = (".ph{position:absolute;background:#fff;padding:18px;box-shadow:0 14px 36px rgba(60,50,20,.25)}.ph img{display:block;width:100%}"
           ".tp{position:absolute;width:190px;height:58px;background:rgba(255,226,140,.78);}")
    imgs = f["images"]
    body = title(f["title"], 17, 120, 128)
    if len(imgs) == 1:
        body += (f'<div class="ph" style="left:250px;top:430px;width:740px;transform:rotate(-2deg)"><img src="{uri(BASE_DIR / imgs[0])}"></div>'
                 '<div class="tp" style="left:470px;top:400px;transform:rotate(-6deg)"></div>')
    else:
        body += (f'<div class="ph" style="left:70px;top:420px;width:1010px;transform:rotate(-2.5deg)"><img src="{uri(BASE_DIR / imgs[0])}"></div>'
                 '<div class="tp" style="left:420px;top:392px;transform:rotate(-6deg)"></div>'
                 f'<div class="ph" style="left:520px;top:930px;width:600px;transform:rotate(3deg)"><img src="{uri(BASE_DIR / imgs[1])}"></div>'
                 '<div class="tp" style="left:760px;top:900px;transform:rotate(5deg)"></div>')
    body += (f'<div class="abs kai" style="left:70px;top:{1000 if len(imgs) > 1 else 1420}px;width:{430 if len(imgs) > 1 else 1100}px;font-size:64px;color:{BLUE};line-height:1.5;transform:rotate(-3deg)">{esc(f["caption"])}</div>'
             + (img(f["sticker"], 40, 1300, 300, -4) if f.get("sticker") else ""))
    return base(body, n, css)


def toc(f, n, N):
    items = f["items"]
    rh = min(190, 1000 // len(items))
    rows = ""
    for i, it in enumerate(items):
        d = f'<div class="b kai">{esc(it["desc"])}</div>' if it.get("desc") else ""
        rows += f'<div class="row" style="height:{rh}px"><div class="hand no">{i + 1:02d}</div><div class="rt"><div class="a">{esc(it["name"])}</div>{d}</div></div>'
    css = (".row{display:flex;align-items:center;gap:34px;border-bottom:4px dashed #D9CFB4}.no{font-size:110px;width:150px;color:#2F5BEA;font-weight:700}"
           ".rt{flex:1}.a{font-size:72px;font-weight:900;white-space:nowrap}.b{font-size:46px;color:#6B6551;white-space:nowrap}")
    body = title(f["title"], 21, 120, 128) + f'<div class="abs" style="left:70px;top:360px;width:1102px">{rows}</div>'
    return base(body, n, css)


def quote(f, n, N):
    big = "<br>".join(T(x, 23) for x in f["lines"])
    body = (f'<svg class="abs" style="left:70px;top:210px" width="190" height="200" viewBox="0 0 190 200"><polygon points="10,10 80,10 62,120 18,120" fill="{ORANGE}"/><polygon points="108,10 178,10 160,120 116,120" fill="{ORANGE}"/></svg>'
            f'<div class="t" style="top:470px;font-size:160px;line-height:1.3">{big}</div>' + wave(70, 1330, 620, 5, sw=10)
            + (f'<div class="abs kai" style="left:70px;top:1420px;font-size:62px;color:{BLUE}">{esc(f["caption"])}</div>' if f.get("caption") else "")
            + (img(f["sticker"], 880, 1180, 300, 6) if f.get("sticker") else ""))
    return base(body, n)


def _halo():
    return ('<div class="abs" style="right:-160px;bottom:-200px;width:900px;height:900px;border-radius:50%;background:#F7E7C9"></div>'
            if _brand()["has_person"] else "")


def closing(f, n, N):
    body = (_halo()
            + pose_img(f.get("pose", "c"), right="-30px", bottom="-60px", width="600px")
            + f'<div class="t" style="top:170px;font-size:128px;line-height:1.25">{esc(f["line1"])}<br>{T(f["line2"], 9)}</div>'
            + f'<div class="abs kai" style="left:70px;top:700px;font-size:72px;color:{BLUE}">{esc(f["hint"])}</div>' + wave(70, 790, 480, 6)
            + '<div class="abs" style="left:70px;top:900px;display:flex;flex-direction:column;gap:26px;font-size:56px;font-weight:900">'
              '<div>☆ 收藏　<span style="color:#9A927C;font-weight:600;font-size:44px">下次直接用</span></div>'
              '<div>♡ 点赞　<span style="color:#9A927C;font-weight:600;font-size:44px">让更多人看到</span></div><div>＋ 关注</div></div>'
            + (img(f["sticker"], 40, 1260, 330, -4) if f.get("sticker") else (img("char_celebrate", 700, 1000, 460, 4) if not _brand()["has_person"] else "")))
    return base(body, n)


def back_cover(f, n, N):
    body = (_halo()
            + pose_img(f.get("pose", "c"), right="-30px", bottom="-60px", width="600px")
            + f'<div class="t" style="top:520px;font-size:130px;line-height:1.25">{esc(f["line1"])}<br><span style="font-size:84px">{T(f["line2"], 31)}</span></div>'
            + wave(70, 900, 560, 7) + (img(f["sticker"], 60, 1200, 300, -4) if f.get("sticker") else "")
            + ("" if _brand()["has_person"] else img("sparkle", 760, 1000, 380, 8)
               + f'<div class="abs kai" style="left:70px;top:1500px;font-size:56px;color:{BLUE}">{esc(_brand()["account"])}</div>')
            + logo())
    return base(body, n)


# ---------- 时间轴、大数字、多截图 ----------
def timeline(f, n, N):
    ev = f["events"]
    k = len(ev)
    top, hgt = 400, 1000
    step_h = hgt / k
    inner, over = f'<path d="M150,{top - 20} L150,{top + hgt}" stroke="{INK}" stroke-width="8" stroke-linecap="round" stroke-dasharray="2 18"/>', ""
    cols = [OR, BLU, TE, YE, "#8A5CD6", OR]
    for i, e in enumerate(ev):
        y = top + i * step_h + step_h / 2 - 20
        inner += f'<circle cx="150" cy="{y:.0f}" r="34" fill="{cols[i]}" stroke="{INK}" stroke-width="8"/>'
        over += txt(232, y - 78, esc(e["time"]), 54, 700, 800, BLUE, "left", True)
        over += txt(232, y - 14, esc(e["name"]), 92, 900, 900, INK, "left")
        if e.get("desc"):
            over += txt(232, y + 96, esc(e["desc"]), 54, 900, 600, "#6B6551", "left", True)
    body = (title(f["title"], 19, 130, 104) + svg(inner) + over + (note(f["footnote"], 70, 1540) if f.get("footnote") else "")
            + (img(f["sticker"], 930, 150, 240, 8) if f.get("sticker") else ""))
    return base(body, n)


def stats(f, n, N):
    it = f["items"]
    k = len(it)
    rows = ""
    rh = 1060 // k
    for i, x in enumerate(it):
        big = 230 if k == 2 else 190
        rows += (f'<div class="card" style="height:{rh - 30}px;display:flex;flex-direction:column;justify-content:center;gap:18px;padding:0 60px;margin-bottom:30px">'
                 f'<div style="font-size:{big}px;font-weight:900;color:{ORANGE};line-height:1;white-space:nowrap">'
                 f'{esc(x["number"])}<small style="font-size:84px;color:{INK};margin-left:14px">{esc(x.get("unit", ""))}</small></div>'
                 f'<div style="font-size:60px;font-weight:700;line-height:1.3">{esc(x["label"])}</div></div>')
    css = ".card{background:#FFFEF9;border:3px solid #D9CFB4;border-radius:30px;box-shadow:0 10px 28px rgba(60,50,20,.10)}"
    body = (title(f["title"], 22, 130, 104) + f'<div class="abs" style="left:70px;top:340px;width:1102px">{rows}</div>'
            + (txt(70, 1560, esc(f["note"]), 40, 1100, 600, "#7D7560", "left", True) if f.get("note") else ""))
    return base(body, n, css)


def shots(f, n, N):
    sh = f["shots"]
    cap = f.get("captions", [])
    css = (".ph{position:absolute;background:#fff;padding:16px;box-shadow:0 14px 36px rgba(60,50,20,.25)}.ph img{display:block;width:100%}"
           ".tp{position:absolute;width:170px;height:52px;background:rgba(255,226,140,.78)}")
    body = title(f["title"], 24, 120, 112)
    sizes = [Image.open(BASE_DIR / p).size for p in sh]
    hh = lambda i, w: int(w * sizes[i][1] / sizes[i][0]) + 32
    if len(sh) == 2:
        w0, w1 = 1000, 1000
        pos = [(80, 420, w0, -1.5)]
        y1 = 420 + hh(0, w0) + 120
        pos.append((160, y1, w1, 1.5))
    else:
        pos = [(60, 400, 520, -2), (640, 470, 520, 2)]
        y2 = max(400 + hh(0, 520), 470 + hh(1, 520)) + 120
        w3 = int(min(940, (1400 - y2) * sizes[2][0] / sizes[2][1])) if y2 < 1300 else 400
        pos.append(((W - w3) // 2, y2, w3, -1))
    for i, (p, (x, y, w, r_)) in enumerate(zip(sh, pos)):
        h = hh(i, w)
        body += (f'<div class="ph" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({r_}deg)"><img src="{uri(BASE_DIR / p)}"></div>'
                 f'<div class="tp" style="left:{x + w // 2 - 80}px;top:{y - 26}px;transform:rotate({-r_ * 2}deg)"></div>')
        if i < len(cap) and cap[i]:
            body += f'<div class="abs kai" style="left:{x}px;top:{y + h + 14}px;width:{w}px;font-size:50px;color:{BLUE};text-align:center">{esc(cap[i])}</div>'
    if f.get("label"):
        body += f'<div class="stick" style="right:70px;top:300px;font-size:46px;transform:rotate(-5deg)">{esc(f["label"])}</div>'
    return base(body, n, css)


# ---------- 图示页 ----------
def cycle(f, n, N):
    nodes = f["nodes"]
    k = len(nodes)
    cx, cy, rx, ry = 621, 900, 330, 380
    ang = [-90 + 360 * i / k for i in range(k)]
    cols = [BLU, OR, TE, YE, "#8A5CD6"]
    parts, boxes = "", ""
    off = 26 if k < 5 else 18
    for i in range(k):
        t0, t1 = math.radians(ang[i] + off), math.radians(ang[i] + 360 / k - off)
        pts = jitter_poly([(cx + rx * math.cos(t0 + (t1 - t0) * j / 18), cy + ry * math.sin(t0 + (t1 - t0) * j / 18)) for j in range(19)], 20 + i, 3)
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
        parts += f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round" filter="url(#ro{i})"/>' + arrowhead(pts[-3], pts[-1])
    bw, bh = (430, 230) if k < 5 else (390, 200)
    for i, nd in enumerate(nodes):
        px, py = cx + rx * math.cos(math.radians(ang[i])), cy + ry * math.sin(math.radians(ang[i]))
        x, y = px - bw / 2, py - bh / 2
        col = cols[i]
        parts += rough(rrect_pts(x, y, bw, bh), col, 40 + i)
        tc = DK if col == YE else "#FFFFFF"
        boxes += txt(x + 130, y + 44, esc(nd["name"]), 74, bw - 140, color=tc, align="left") + txt(x + 130, y + 132, esc(nd["desc"]), 48, bw - 140, 600, tc, "left", True)
        boxes += img(nd["sticker"], x + 8, y + 62, 118)
    body = (title(f["title"], 3, 130, 104) + svg(parts) + boxes + img("arrow_cycle", cx - 130, cy - 130, 260)
            + (note(f["footnote"], 150, 1540) if f.get("footnote") else ""))
    return base(body, n)


def matrix(f, n, N):
    x0, y0, cw, ch, g = 190, 430, 470, 450, 24
    cols = [OR, BLU, TE, YE]
    hi = f.get("highlight", 0)
    inner, over = "", ""
    for i, c in enumerate(f["cells"]):
        cc, rr = i % 2, i // 2
        x, y = x0 + cc * (cw + g), y0 + rr * (ch + g)
        hot = i == hi
        inner += rough(rrect_pts(x, y, cw, ch, 30), "#FFFEF9", 60 + i, 9 if hot else 6, OR if hot else INK)
        inner += rough(rrect_pts(x + 24, y + 24, 250, 80, 34), cols[i], 70 + i, 5)
        tc = DK if cols[i] == YE else "#FFFFFF"
        over += txt(x + 24, y + 42, esc(c["tag"]), 52, 250, color=tc) + txt(x + 30, y + 140, esc(c["desc"]), 56, cw - 60, 800, INK, "left") + img(c["sticker"], x + cw - 240, y + ch - 250, 220)
    ax = (f'<path d="M{x0 - 50},{y0 + 2 * ch + g} L{x0 - 50},{y0 - 20}" stroke="{INK}" stroke-width="9" fill="none" stroke-linecap="round"/>' + arrowhead((x0 - 50, y0 + 60), (x0 - 50, y0 - 20))
          + f'<path d="M{x0 - 50},{y0 + 2 * ch + g + 50} L{x0 + 2 * cw + g + 10},{y0 + 2 * ch + g + 50}" stroke="{INK}" stroke-width="9" fill="none" stroke-linecap="round"/>'
          + arrowhead((x0 + 2 * cw - 40, y0 + 2 * ch + g + 50), (x0 + 2 * cw + g + 10, y0 + 2 * ch + g + 50)))
    yl = "<br>".join(esc(c) for c in f["ylabel"])
    labs = txt(30, y0 + 300, yl, 54, 100, 800, INK, "center", True) + txt(x0 + 380, y0 + 2 * ch + g + 70, esc(f["xlabel"]) + " →", 50, 300, 800, INK, "center", True)
    return base(title(f["title"], 5, 130, 104) + svg(inner + ax) + over + labs, n)


def pyramid(f, n, N):
    cx, top, hgt, base_w, gap = 400, 440, 960, 680, 16
    lh = (hgt - 2 * gap) / 3
    cols = [OR, BLU, TE]
    wd = lambda y: 120 + (base_w - 120) * y / hgt
    inner, over = "", ""
    for i, ly in enumerate(f["layers"]):
        y0 = i * (lh + gap)
        y1 = y0 + lh
        pts = [(cx - wd(y0) / 2, top + y0), (cx + wd(y0) / 2, top + y0), (cx + wd(y1) / 2, top + y1), (cx - wd(y1) / 2, top + y1)]
        inner += rough(pts, cols[i], 80 + i, 8)
        ym = top + (y0 + y1) / 2
        inner += f'<path d="M{cx + wd((y0 + y1) / 2) / 2 + 14:.0f},{ym:.0f} L760,{ym:.0f}" stroke="{INK}" stroke-width="5" stroke-dasharray="3 14" stroke-linecap="round"/>'
        over += txt(cx - 150, ym - 40, esc(ly["name"]), 74, 300) + txt(780, ym - 60, esc(ly["desc"]), 50, 400, 800, INK, "left")
    return base(title(f["title"], 7, 130, 104) + svg(inner) + over + img("flag", 320, 280, 150) + (note(f["footnote"], 70, 1500) if f.get("footnote") else ""), n)


def _axes(ox, oy, ph):
    s = f'<path d="M{ox},{oy - ph - 30} L{ox},{oy} L1160,{oy}" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>' + arrowhead((ox, oy - ph + 20), (ox, oy - ph - 30))
    for g in (1, 2, 3):
        yy = oy - ph * g / 3.4
        s += f'<path d="M{ox + 10},{yy:.0f} L1150,{yy:.0f}" stroke="#CFC4A6" stroke-width="4" stroke-dasharray="4 16" stroke-linecap="round"/>'
    return s


def bar(f, n, N):
    items = f["items"]
    k = len(items)
    ox, oy, ph = 170, 1380, 700
    mx = max(i["value"] for i in items) or 1
    cols = [OR, BLU, TE, YE, "#8A5CD6"]
    slot = 980 / k
    bw = int(slot * 0.76)
    inner, over = _axes(ox, oy, ph), ""
    for i, it in enumerate(items):
        x = ox + 40 + i * slot
        h = max(ph * 0.88 * it["value"] / mx, 30)
        inner += rough(rrect_pts(x, oy - h, bw, h, 14), cols[i], 90 + i, 7)
        over += txt(x - 30, oy - h - 90, f'{it["value"]:g}{esc(it.get("unit", ""))}', 52, bw + 60, 900, INK) + txt(x - 30, oy + 24, esc(it["label"]), 44, bw + 60, 800, INK, "center", True)
    body = (title(f["title"], 9, 130, 104) + svg(inner) + over + (img(f["sticker"], 780, 430, 300, 8) if f.get("sticker") else "")
            + txt(70, 1560, esc(f.get("note", "示例数据，用你自己的真实数据替换")), 40, 1100, 600, "#9A927C", "left", True))
    return base(body, n)


def line(f, n, N):
    pts_in = f["points"]
    k = len(pts_in)
    ox, oy, ph, pw = 170, 1380, 760, 900
    mx = max(p["value"] for p in pts_in) or 1
    inner, over = _axes(ox, oy, ph), ""
    pts = [(ox + 100 + i * pw / (k - 0.2 if k > 1 else 1), oy - ph * 0.88 * p["value"] / mx) for i, p in enumerate(pts_in)]
    q = jitter_poly(pts, 99, 3)
    inner += '<path d="M' + " L".join(f"{x:.0f},{y:.0f}" for x, y in q) + f'" fill="none" stroke="{OR}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round" filter="url(#ro2)"/>'
    for (x, y), p in zip(q, pts_in):
        inner += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="22" fill="#FFFEF9" stroke="{INK}" stroke-width="8"/>'
        over += txt(x - 100, y - 100, f'{p["value"]:g}', 56, 200, 900, INK) + txt(x - 100, oy + 24, esc(p["label"]), 44, 200, 800, INK, "center", True)
    body = (title(f["title"], 11, 130, 104) + svg(inner) + over + (img(f["sticker"], 940, 380, 250) if f.get("sticker") else "")
            + (txt(430, 430, esc(f["axis"]), 50, 200, 800, INK, "left", True) if f.get("axis") else "")
            + txt(70, 1560, esc(f.get("note", "示例数据，用你自己的真实数据替换")), 40, 1100, 600, "#9A927C", "left", True))
    return base(body, n)


def funnel(f, n, N):
    st = f["stages"]
    k = len(st)
    cx, top, gap = 460, 430, 16
    lh = int((1000 - gap * (k - 1)) / k)
    cols = [OR, BLU, TE, YE, "#8A5CD6"]
    widths = [860 - (860 - 240) * i / k for i in range(k + 1)]
    inner, over = "", ""
    for i, s in enumerate(st):
        y = top + i * (lh + gap)
        w0, w1 = widths[i], widths[i + 1]
        inner += rough([(cx - w0 / 2, y), (cx + w0 / 2, y), (cx + w1 / 2, y + lh), (cx - w1 / 2, y + lh)], cols[i], 110 + i, 8)
        tc = DK if cols[i] == YE else "#FFFFFF"
        over += txt(cx - 220, y + lh / 2 - 38, f'{esc(s["name"])}  {esc(s["value"])}', 64, 440, color=tc)
        if s.get("sticker"):
            over += img(s["sticker"], cx + w1 / 2 + 60, y + (lh - 190) / 2, 190)
    return base(title(f["title"], 13, 130, 104) + svg(inner) + over + (note(f["footnote"], 70, 1500) if f.get("footnote") else ""), n)


RENDERERS = {"timeline": timeline, "stats": stats, "shots": shots, "cover_list": cover_list, "cover_person": cover_person, "cover_quote": cover_quote, "step": step, "prompt": prompt, "idea": idea,
             "list": list_page, "compare": compare, "result": result, "toc": toc, "quote": quote, "cycle": cycle, "matrix": matrix,
             "pyramid": pyramid, "bar": bar, "line": line, "funnel": funnel, "closing": closing, "back_cover": back_cover}

COVER_LIMIT = {"default": 0.34, "step": 0.52, "result": 0.46, "cover_person": 0.46, "cover_list": 0.46, "cover_quote": 0.40}

CHECK_JS = """() => {
  const out = [];
  document.querySelectorAll('.t').forEach(e => { if (e.scrollWidth > e.clientWidth + 2) out.push('标题或大字过长：' + e.textContent.trim().slice(0, 16)); });
  document.querySelectorAll('.fit').forEach(e => { if (e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2) out.push('文字放不下：' + e.textContent.trim().slice(0, 16)); });
  const stk = [...document.querySelectorAll('img')].filter(i => (i.getAttribute('src') || '').includes('library')).map(i => i.getBoundingClientRect());
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let nd;
  while ((nd = w.nextNode())) {
    const t = nd.textContent.trim();
    if (!t || nd.parentElement.closest('style,script')) continue;
    if (t.length <= 2 && nd.parentElement.closest('.hand')) continue;   // ✕ ✓ 这类标记本来就压在贴纸上
    const r = document.createRange(); r.selectNodeContents(nd);
    for (const tb of r.getClientRects()) {
      if (tb.width < 20 || tb.height < 14) continue;
      for (const s of stk) {
        const ix = Math.max(0, Math.min(tb.right, s.right) - Math.max(tb.left, s.left)), iy = Math.max(0, Math.min(tb.bottom, s.bottom) - Math.max(tb.top, s.top));
        if (ix * iy > 0.25 * tb.width * tb.height) { out.push('贴纸压住了文字：' + t.slice(0, 12)); break; }
      }
    }
  }
  return [...new Set(out)];
}"""


def page_html(plan, idx, base_dir):
    global BASE_DIR
    BASE_DIR = pathlib.Path(base_dir)
    D.DARK = plan["meta"]["theme"] == "dark"
    D.THEME = plan["meta"]["theme"]
    b = _brand()
    D.ACCOUNT = b["account"]
    D.HAS_LOGO = b["has_logo"]
    D.TICKET_NO = str(plan["meta"].get("no", ""))
    D.TOTAL = len(plan["pages"])
    pg = plan["pages"][idx]
    return RENDERERS[pg["type"]](pg["fields"], idx + 1, len(plan["pages"]))


def render_pages(plan, base_dir, out_dir, only=None):
    """返回 (生成的文件列表, 版面问题列表)。"""
    from playwright.sync_api import sync_playwright
    out_dir = pathlib.Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_tmp"
    tmp.mkdir(exist_ok=True)
    files, problems = [], []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for i, pg in enumerate(plan["pages"]):
            if only and i + 1 != only:
                continue
            h = tmp / f"p{i + 1}.html"
            h.write_text(page_html(plan, i, base_dir), encoding="utf-8")
            page = br.new_page(viewport={"width": W, "height": H})
            page.goto(h.as_uri())
            page.wait_for_timeout(300)
            for msg in page.evaluate(CHECK_JS):
                problems.append(f"第 {i + 1} 页（{pg['type']}）：{msg}，回去删文案或换页型")
            f = out_dir / f"{i + 1:02d}_{pg['type']}.png"
            f.write_bytes(page.screenshot(clip=dict(x=0, y=0, width=W, height=H)))
            import quality
            cov = quality.coverage(f, ticket=(D.THEME == "ticket"))
            lim = COVER_LIMIT.get(pg["type"], COVER_LIMIT["default"])
            if cov > lim:
                problems.append(f"第 {i + 1} 页（{pg['type']}）：留白不足，内容占页面 {cov:.0%}，上限 {lim:.0%}，删条目或缩短文字，让页面有呼吸感")
            page.close()
            files.append(f)
        br.close()
    for f in tmp.glob("*.html"):
        f.unlink()
    tmp.rmdir()
    return files, problems
