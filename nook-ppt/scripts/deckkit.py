"""页面小工具（公共）：真标题占位符放大成主角、眉题、副标题、页眉角标、圆角图片、大数字卡片行、左右对比。风格包的样片脚本共用。
用法：sys.path 里加入 <skill>/scripts 后  from deckkit import Kit, cli, variant
    from kit import Kit
    k = Kit(deck, label="PARA  ·  文件分类法", total=8)
    k.headline(s, ["一行", "两行**强调**"], (x, y, w, h), 56)
"""
import re

from slidekit import *            # noqa
from slidekit import _set_font    # noqa


class Kit:
    def __init__(self, deck, label, total, mx=80.0, light=False):
        self.d, self.t, self.label, self.total, self.mx = deck, deck.t, label, total, mx
        self.light = light                      # 浅色版：圆角图片不加边线（黑底图在浅底上本身就是卡片）
        self.cw = W - 2 * mx

    def headline(self, s, lines, rect, size, color=None, anim=("fade", "after", 0, 0.5), k=1.18, em=None):
        d, t = self.d, self.t
        ph = s.shapes.title
        x, y, w, h = rect
        ph.left, ph.top, ph.width, ph.height = (Emu(int(v * 12700)) for v in rect)
        tf = ph.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.text = ""
        for i, line in enumerate(lines):
            plain = re.sub(r"\*\*", "", line)
            if text_w(plain, size, True) > w:
                raise Overflow(f"标题行放不下 [{line}]：{size}pt 需要 {text_w(plain, size, True):.0f}pt，宽 {w:.0f}pt")
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.line_spacing = Pt(round(size * k, 1))
            for seg, b in parse_runs(line):
                r = p.add_run()
                r.text = seg
                _set_font(r, size, True, (em or t["em"]) if b else (color or t["ink"]))
        d.occupy(s, (x, y, w, len(lines) * size * k), "标题")
        d.report.append(("标题", lines[0][:12], size, len(lines)))
        if anim:
            d.A(s, ph.name, *anim)
        return ph

    def eyebrow(self, s, text, x, y, color="coral", anim=("fade", "after", 0, 0.4)):
        return self.d.text(s, (x, y, 480, 32), [dict(text=text, size=16, bold=True, color=self.t.get(color, color))], name="眉题", inset=0, anim=anim)

    def sub(self, s, rect, text, size=24, name="副标题", anim=("fade", "after", 0.1, 0.5), color="sub"):
        return self.d.text(s, rect, [dict(text=text, size=size, color=self.t.get(color, color))], name=name, inset=0, anim=anim)

    def corner(self, s, n, on_dark=False):
        d, t = self.d, self.t
        sub = "86868B" if on_dark else t["sub"]
        d.text(s, (self.mx, 30, 360, 22), [dict(text=self.label, size=14, bold=True, color=sub)], name="角标左", inset=0)
        d.text(s, (W - self.mx - 120, 30, 120, 22), [dict(text=f"{n:02d} / {self.total:02d}", size=14, bold=True, color=sub, align="right")], name="角标右", inset=0, align="right")

    def image(self, s, rect, path, alt, morph=None, anim=("fade", "after", 0, 0.6), focus=(0.5, 0.5), treat="rounded", z="front", name=None, frame="auto"):
        d = self.d
        p = d.slot(s, rect, path, kind="photo", treat=treat, focus=focus, alt=alt, name=name or pathlib.Path(path).stem, anim=None if morph else anim, z=z, frame=((None if self.light else ("line", 1.0)) if (frame == "auto" and treat == "rounded") else (None if frame == "auto" else frame)))
        if morph:
            p.name = d.mname(morph)
        return p

    # ------------------------------------------------------------ 页面零件
    def stat_row(self, s, items, y=170.0, h=270.0, num_size=112, name="数字卡"):
        """一排大数字卡：items = [(数字, 单位, 说明)]。第一张卡是一个讲点（点击），其余自动接着出现；数字带主题的渐变光。"""
        d, t = self.d, self.t
        n = len(items)
        cw = (self.cw - 16 * (n - 1)) / n
        for i, (num, unit, lab) in enumerate(items):
            x = self.mx + i * (cw + 16)
            d.card(s, (x, y, cw, h), None, None, fill="card", name=f"{name}{i + 1}", anim=("fade", "beat", 0, 0.45) if i == 0 else ("fade", "after", 0, 0.45))
            d.text(s, (x + 28, y + 26, cw - 56, 130), [dict(text=num, size=num_size, bold=True, color=t["ink"])], name=f"大数字{i + 1}", inset=0, anim=("zoom", "with", 0.05, 0.5), grad=t.get("num_grad"))
            d.text(s, (x + 28 + text_w(num, num_size, True) + 12, y + 84, 80, 48), [dict(text=unit, size=32, bold=True, color=t["coral"])], name=f"单位{i + 1}", inset=0, anim=("fade", "with", 0.15, 0.4))
            d.text(s, (x + 28, y + h - 68, cw - 56, 40), [dict(text=lab, size=20, color=t["sub"])], name=f"数字说明{i + 1}", inset=0, anim=("fade", "with", 0.2, 0.4))

    def compare(self, s, left, right, y=160.0, h=290.0):
        """左右对比两张卡：left / right = (小标题, [两行大字], 底部一句)；右卡用强调卡面。"""
        d, t = self.d, self.t
        cw2 = (self.cw - 16) / 2
        for k, (tag, lines, note) in enumerate((left, right)):
            x = self.mx + k * (cw2 + 16)
            d.card(s, (x, y, cw2, h), None, None, fill="card2" if k else "card", name="右卡" if k else "左卡", anim=("fade", "beat", 0, 0.45))
            d.text(s, (x + 28, y + 24, cw2 - 56, 30), [dict(text=tag, size=18, bold=True, color=t["coral"] if k else t["sub"])], name="右标" if k else "左标", inset=0, anim=("fade", "with", 0.05, 0.4))
            d.text(s, (x + 28, y + 60, cw2 - 56, 150), [dict(text=ln, size=32, bold=True) for ln in lines], name="右文" if k else "左文", inset=0, anim=("fade", "with", 0.1, 0.4))
            d.text(s, (x + 28, y + h - 68, cw2 - 56, 40), [dict(text=note, size=20, color=t["sub"])], name="右注" if k else "左注", inset=0, anim=("fade", "with", 0.15, 0.4))


def cli(default_out):
    """样片脚本的统一命令行：[输出目录] [--light] [--blue] [--read]。--read 是给别人看的版本（不加动效，切换朴素）。"""
    import sys
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    return dict(light="--light" in sys.argv, blue="--blue" in sys.argv, read="--read" in sys.argv,
                out=pathlib.Path(args[0]) if args else pathlib.Path(default_out))


def variant(o):
    """文件名里的版本标记：暗场 / 暗场蓝 / 浅色，阅读版再加后缀。"""
    return ("浅色" if o["light"] else ("暗场蓝" if o["blue"] else "暗场"))
