"""slidekit：用"零件 + 网格 + 量字"拼装可编辑 PPTX 的小引擎（原型 v0.1）。

原则
- Agent 只决定：用哪个零件、占网格的几列几行、放什么文字。坐标、字号档位、行距、内边距由代码算。
- 文字全部是真文字（标题走真占位符，正文/卡片/表格/图表/流程图都是原生对象），只有主标题、Logo、底图可以是 PNG。
- 每个文字容器先用同一款字体量字（中文禁则换行），放不下就报错并给出容量，不悄悄缩字、不裁字。
- 单位一律是 pt（一页 960×540），坐标只在这里出现一次。
"""
import copy
import math
import pathlib
import re

from lxml import etree
from PIL import ImageFont
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from pptx.util import Emu, Pt

__version__ = "2.0-alpha"
W, H = 960.0, 540.0
FONT = "微软雅黑"                     # 正文字体名
FONT_BOLD = None                      # 粗体字体名（静态粗体字重，如 Source Han Serif CN Heavy）；None 表示用 bold 标志
FONT_HAND = None                      # 批注手写体字体名
FONT_FILES = {False: "C:/Windows/Fonts/msyh.ttc", True: "C:/Windows/Fonts/msyhbd.ttc", "hand": None}   # 量字用的字体文件

# ---------------------------------------------------------------- 规格（Design Tokens）
T = dict(
    bg="F6F4EF", ink="1E2A44", sub="5B6478", line="D9D4C7", card="FFFFFF", card2="ECE8DD",
    coral="F0654B", teal="2A9D8F", sand="E9C46A", navy="1E2A44", white="FFFFFF", em="F0654B",
    card_alpha=1.0, glow=None, dark_text="1E2A44",
)
MARGIN_X, TITLE_Y, TITLE_H = 92.0, 38.0, 84.0                # 页边距 92：留出呼吸感（260930 起，原 76）
BODY_Y0, BODY_Y1 = 156.0, 466.0                 # 内容区上下沿
COLS, ROWS, GUT_X, GUT_Y = 12, 6, 24.0, 16.0
COL_W = (W - 2 * MARGIN_X - (COLS - 1) * GUT_X) / COLS
ROW_H = (BODY_Y1 - BODY_Y0 - (ROWS - 1) * GUT_Y) / ROWS
RADIUS = 10.0
SIZES = [40, 36, 32, 28, 24, 22, 20, 18, 16, 14]      # 字号档位，只在这里选，不逐个微调
LINE_K_HAND = 1.95                                     # 手写体（霞鹜文楷）字形比行高大，行距要放宽
LINE_K = 1.42                                          # 行距 = 字号 × 1.42，写成固定磅值
INSET = 10.0


def rgb(h):
    return RGBColor.from_string(h.upper())


def cell(col, row, cspan=1, rspan=1):
    """网格 → 矩形 (x, y, w, h)。col、row 从 0 起。"""
    x = MARGIN_X + col * (COL_W + GUT_X)
    y = BODY_Y0 + row * (ROW_H + GUT_Y)
    w = cspan * COL_W + (cspan - 1) * GUT_X
    h = rspan * ROW_H + (rspan - 1) * GUT_Y
    return (x, y, w, h)


# ---------------------------------------------------------------- 量字
_FONTS = {}


def _font(bold, size):
    key = (bold, round(size * 4))
    if key not in _FONTS:
        idx = 0
        _FONTS[key] = ImageFont.truetype(FONT_FILES[bold if bold in (False, True, "hand") else True], int(round(size * 4)), index=idx)
    return _FONTS[key]


def text_w(s, size, bold=False):
    return _font(bold, size).getlength(s) / 4.0


NO_START = set("，。、；：！？）》」』”’】〕…—,.;:!?)]}%")
NO_END = set("（《「『“‘【〔([{")
_TOKEN = re.compile(r"[A-Za-z0-9_.+\-/%:#@&']+|\s+|.", re.S)


def parse_runs(s):
    """把 **强调** 拆成 [(文字, 是否强调)]。"""
    out, bold = [], False
    for i, part in enumerate(s.split("**")):
        if part:
            out.append((part, i % 2 == 1))
    return out or [("", False)]


def wrap_lines(text, size, width, base_bold=False):
    """返回行数与每行文字。按 token 贪心换行，遵守标点禁则。"""
    toks = []
    for seg, b in parse_runs(text):
        for m in _TOKEN.finditer(seg):
            toks.append((m.group(0), "hand" if base_bold == "hand" else (b or base_bold)))
    lines, cur, cur_w = [], [], 0.0
    for tok, b in toks:
        w = text_w(tok, size, b)
        if cur and cur_w + w > width + 0.01 and not tok.isspace():
            # 行首不能是禁则标点：把上一 token 一起带下去
            if tok[0] in NO_START and len(cur) > 1:
                carry = cur.pop()
                lines.append(cur)
                cur, cur_w = [carry], text_w(carry[0], size, carry[1])
            else:
                lines.append(cur)
                cur, cur_w = [], 0.0
            if cur and cur[-1][0] in NO_END:
                pass
        if not cur and tok.isspace():
            continue
        cur.append((tok, b))
        cur_w += w
    if cur:
        lines.append(cur)
    return lines or [[]]


class Overflow(Exception):
    pass


def measure(paras, w, size_of):
    """paras: [{text, size, bold, bullet, after}]，返回总高度（pt）。"""
    tot = 0.0
    for p in paras:
        size = p["size"]
        ind = p.get("indent", 0)
        n = len(wrap_lines(p["text"], size, w - ind, p.get("kind", p.get("bold", False))))
        tot += n * size * (LINE_K_HAND if p.get("kind") == "hand" else LINE_K) + p.get("after", 0)
    return tot


# ---------------------------------------------------------------- 文本写入
def _set_font(run, size, bold=False, color=None, font=None):
    """font=None 时按主题选择：粗体优先用 FONT_BOLD（静态粗体字重，b 标志置 0，避免二次加粗）。"""
    if font is None:
        font = FONT_BOLD if (bold and FONT_BOLD) else FONT
        use_b = bold and not FONT_BOLD
    else:
        use_b = bold
    f = run.font
    f.size = Pt(size)
    f.bold = use_b
    f.name = font
    rPr = run._r.get_or_add_rPr()
    rPr.set("lang", "zh-CN")
    rPr.set("altLang", "en-US")
    for tag in ("a:ea", "a:cs"):
        for e in rPr.findall(qn(tag)):
            rPr.remove(e)
    for tag in ("a:ea", "a:cs"):
        el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", font)
    if color:
        f.color.rgb = rgb(color)


def _bullet(p, size, color, indent):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(indent * 12700)))
    pPr.set("indent", str(int(-indent * 12700)))
    for tag in ("a:buNone", "a:buChar", "a:buClr", "a:buFont", "a:buSzPct"):
        for e in pPr.findall(qn(tag)):
            pPr.remove(e)
    clr = etree.SubElement(pPr, qn("a:buClr"))
    etree.SubElement(clr, qn("a:srgbClr")).set("val", color.upper())
    etree.SubElement(pPr, qn("a:buSzPct")).set("val", "80000")
    etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
    etree.SubElement(pPr, qn("a:buChar")).set("char", "•")


def write_paras(tf, paras, inset=INSET, anchor="top", align="left", accent=None, em=None):
    """把段落写进文本框：固定行距、固定内边距、关闭自动缩放、显式换行。"""
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = Pt(inset)
    tf.margin_top = tf.margin_bottom = Pt(inset * 0.6)
    tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[anchor]
    accent = accent or T["coral"]
    for i, pd in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[pd.get("align", align)]
        size = pd["size"]
        p.line_spacing = Pt(round(size * (LINE_K_HAND if pd.get("kind") == "hand" else LINE_K), 1))
        p.space_before = Pt(0)
        p.space_after = Pt(pd.get("after", 0))
        _pp = p._p.get_or_add_pPr()
        _pp.set("eaLnBrk", "1")
        _pp.set("hangingPunct", "1")
        if pd.get("bullet"):
            _bullet(p, size, accent, pd.get("indent", size))
        for seg, b in parse_runs(pd["text"]):
            r = p.add_run()
            r.text = seg
            emph = b
            _set_font(r, size, bold=pd.get("bold", False) or b, color=(em or accent) if emph else pd.get("color", T["ink"]),
                      font=FONT_HAND if pd.get("kind") == "hand" else None)


def fit_paras(paras_in, w, h, sizes=None, inset=INSET, label=""):
    """给一组段落选字号：paras_in 每项的 size 是相对档位（"t" 标题、"b" 正文、"s" 小字），
    从大到小试整套缩放，选第一个放得下的。放不下抛 Overflow 并给出容量。"""
    inner_w = w - 2 * inset
    inner_h = h - 2 * inset * 0.6
    ladder = sizes or [1.0, 0.92, 0.85, 0.78]
    base = paras_in
    for k in ladder:
        paras = []
        for pd in base:
            q = dict(pd)
            q["size"] = max(12, round(pd["size"] * k))
            if q.get("bullet"):
                q["indent"] = q["size"]
            paras.append(q)
        need = measure(paras, inner_w, None)
        if need <= inner_h + 0.5:
            return paras, need
    cap = int(inner_w // max(12, base[-1]["size"]))
    raise Overflow(f"文字放不下 [{label}]：容器 {w:.0f}×{h:.0f}pt，最小字号仍需 {need:.0f}pt > {inner_h:.0f}pt；每行约 {cap} 字，请缩减文案")


# ---------------------------------------------------------------- 文档与母版
class Deck:
    def __init__(self, theme=None, mode="talk"):
        """mode = talk（上台讲：点击触发的讲点动效、平滑切换）/ read（给别人看：不加动效，切换朴素，导出 PDF 元素全在）。"""
        self.mode = mode
        self.prs = Presentation()
        self.prs.slide_width = Emu(int(W * 12700))
        self.prs.slide_height = Emu(int(H * 12700))
        global FONT, FONT_BOLD, FONT_HAND, RADIUS
        if theme:
            RADIUS = theme.get("radius", 10.0)        # 容器圆角（刊物风用小圆角）
            T.update(theme)            # 模块级默认色也随主题走（write_paras 的默认文字色用它）
            if theme.get("font"):
                FONT = theme["font"]
                FONT_FILES[False] = theme["font_file"]
            FONT_BOLD = theme.get("font_bold", FONT_BOLD)
            if theme.get("font_bold_file"):
                FONT_FILES[True] = theme["font_bold_file"]
            if theme.get("font_hand"):
                FONT_HAND = theme["font_hand"]
                FONT_FILES["hand"] = theme["font_hand_file"]
            _FONTS.clear()
        self.t = dict(T)
        self.report = []            # 每个容器的量字结果
        self.anim = []              # 零件自带的动效计划（保存时写成 .anim.json，由 animate_deck.ps1 执行）
        self.warnings = []          # 布局告警：装饰或人物压到内容、装饰过多
        self._occ = {}              # 每页已占用的内容区域
        self._names = {}
        self._deco_n = {}
        self.trans = {}             # 每页的切换方式：fade / morph（平滑）
        self._build_master()
        self.n_pages = 0

    def _idx(self, s):
        return list(self.prs.slides).index(s) + 1

    def uname(self, s, shape, base):
        """给形状起本页唯一的名字（动效按名字找形状）。"""
        k = (s.slide_id, base)
        n = self._names.get(k, 0)
        self._names[k] = n + 1
        shape.name = base if n == 0 else f"{base}#{n + 1}"
        return shape.name

    def mname(self, key):
        """平滑过渡的配对名：两页里叫同一个 !!名字 的对象，PowerPoint 会当作同一个东西。"""
        return f"!!{key}"

    def A(self, s, name, effect="fade", trigger="after", delay=0.0, dur=0.4, direction=None):
        """登记一条动效：effect = fade/zoom/wipe；trigger = beat（新讲点，现场点击一次）/ after（接在上一个之后自动）/ with（与上一个同时）。"""
        self.anim.append(dict(slide=self._idx(s), name=name, effect=effect, trigger=trigger, delay=round(delay, 3), dur=dur, dir=direction))

    def occupy(self, s, rect, kind="内容"):
        self._occ.setdefault(s.slide_id, []).append((rect, kind))

    def _overlap(self, s, rect, kind, allow=()):
        x, y, w, h = rect
        for (ox, oy, ow, oh), k in self._occ.get(s.slide_id, []):
            if k in allow:
                continue
            iw = min(x + w, ox + ow) - max(x, ox)
            ih = min(y + h, oy + oh) - max(y, oy)
            if iw > 4 and ih > 4:
                self.warnings.append(f"第 {self._idx(s)} 页：{kind} 压到了 {k}（重叠 {iw:.0f}×{ih:.0f}pt）")
                return True
        return False

    def on(self, hexcol):
        """在某个底色上用深字还是白字（按亮度）。"""
        h = hexcol.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))

        def lum(rgb_):
            f = lambda c: (c / 255) / 12.92 if c / 255 <= 0.03928 else (((c / 255) + 0.055) / 1.055) ** 2.4
            return 0.2126 * f(rgb_[0]) + 0.7152 * f(rgb_[1]) + 0.0722 * f(rgb_[2])
        lb = lum((r, g, b))
        dk = self.t["dark_text"]
        ld = lum(tuple(int(dk[i:i + 2], 16) for i in (0, 2, 4)))
        c_w = (1.05) / (lb + 0.05)
        c_d = (max(lb, ld) + 0.05) / (min(lb, ld) + 0.05)
        return "FFFFFF" if c_w >= c_d else dk          # 白字与深字里，选和底色对比度更高的那个

    def _skin(self, shape, ow=None, dist=None):
        """容器皮肤：主题里有 outline 就加墨线描边，有 hard_shadow 就换成硬投影。"""
        t = self.t
        if t.get("outline"):
            shape.line.color.rgb = rgb(t["outline"])
            shape.line.width = Pt(ow or t.get("outline_w", 2.0))
        if t.get("hard_shadow"):
            _hard_shadow(shape, dist or t.get("hard_shadow"), t.get("outline", "1E2A44"))

    # -- 母版与版式
    def _build_master(self):
        prs, t = self.prs, self.t
        m = prs.slide_master
        m.background.fill.solid()
        m.background.fill.fore_color.rgb = rgb(t["bg"])
        tx = m._element.find(qn("p:txStyles"))
        ts = tx.find(qn("p:titleStyle")).find(qn("a:lvl1pPr"))
        for e in list(ts):
            ts.remove(e)
        ts.set("algn", "l")
        ts.append(parse_xml(f'<a:lnSpc xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:spcPts val="{int(32*LINE_K*100)}"/></a:lnSpc>'))
        ts.append(parse_xml(f'<a:defRPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" sz="3200" b="{0 if FONT_BOLD else 1}"><a:solidFill><a:srgbClr val="{t["ink"]}"/></a:solidFill><a:latin typeface="{FONT_BOLD or FONT}"/><a:ea typeface="{FONT_BOLD or FONT}"/><a:cs typeface="{FONT_BOLD or FONT}"/></a:defRPr>'))
        for lvl in tx.find(qn("p:bodyStyle")):
            d = lvl.find(qn("a:defRPr"))
            if d is not None:
                for e in list(d):
                    d.remove(e)
                d.append(parse_xml(f'<a:solidFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:srgbClr val="{t["ink"]}"/></a:solidFill>'))
                d.append(parse_xml(f'<a:latin xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{FONT}"/>'))
                d.append(parse_xml(f'<a:ea xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{FONT}"/>'))
        # 只保留三个版式，并改名
        keep = {"Title Slide": "封面", "Section Header": "章节", "Title Only": "内容页"}
        for lay in list(prs.slide_layouts):
            if lay.name not in keep:
                prs.slide_layouts.remove(lay)
        self.layouts = {}
        for lay in prs.slide_layouts:
            self.layouts[keep[lay.name]] = lay
            lay._element.find(qn("p:cSld")).set("name", keep[lay.name])
        # 内容页：标题占位符
        lay = self.layouts["内容页"]
        for ph in lay.placeholders:
            if ph.placeholder_format.type is not None and "TITLE" in str(ph.placeholder_format.type):
                ph.left, ph.top, ph.width, ph.height = (Emu(int(v * 12700)) for v in (MARGIN_X, TITLE_Y, W - 2 * MARGIN_X, TITLE_H))
                ph.text_frame.vertical_anchor = MSO_ANCHOR.BOTTOM
            elif "DATE" in str(ph.placeholder_format.type) or "FOOTER" in str(ph.placeholder_format.type) or "SLIDE_NUMBER" in str(ph.placeholder_format.type):
                ph._element.getparent().remove(ph._element)
        # 封面：标题在页外（页面上的主标题用 PNG，占位符文字留给大纲视图），副标题占位符放在下方
        lay = self.layouts["封面"]
        for ph in list(lay.placeholders):
            ty = str(ph.placeholder_format.type)
            if "CENTER_TITLE" in ty or ty.endswith("TITLE (1)"):
                ph.left, ph.top, ph.width, ph.height = (Emu(int(v * 12700)) for v in (MARGIN_X, H + 20, 600, 60))
            elif "SUBTITLE" in ty:
                ph.left, ph.top, ph.width, ph.height = (Emu(int(v * 12700)) for v in (MARGIN_X, 372, 400, 90))
            else:
                ph._element.getparent().remove(ph._element)
        lay = self.layouts["章节"]
        for ph in list(lay.placeholders):
            ty = str(ph.placeholder_format.type)
            if "TITLE" in ty:
                ph.left, ph.top, ph.width, ph.height = (Emu(int(v * 12700)) for v in (MARGIN_X + 20, 200, 620, 110))
                ph.text_frame.vertical_anchor = MSO_ANCHOR.BOTTOM
            elif "BODY" in ty:
                ph.left, ph.top, ph.width, ph.height = (Emu(int(v * 12700)) for v in (MARGIN_X + 20, 322, 620, 80))
            else:
                ph._element.getparent().remove(ph._element)

    def layout_background(self, layout_name, image_path, alt="背景"):
        """把整页底图放进版式（不是放在页面上，避免误选误拖）。"""
        lay = self.layouts[layout_name]
        part = lay.part
        img_part, rId = part.get_or_add_image_part(str(image_path))
        emu = lambda v: int(v * 12700)
        pic = parse_xml(
            '<p:pic xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<p:nvPicPr><p:cNvPr id="90" name="底图" descr="{alt}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr userDrawn="1"/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rId}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{emu(W)}" cy="{emu(H)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
        tree = lay._element.find(qn("p:cSld")).find(qn("p:spTree"))
        tree.insert(2, pic)          # nvGrpSpPr、grpSpPr 之后，放在最底层

    # -- 页面
    def slide(self, layout="内容页", title=None, notes=None, transition="fade"):
        """transition="morph" 即 PowerPoint 的"平滑"：与上一页同名（"!!名字"）的对象，位置、大小、形状、图片会平滑过渡。"""
        s = self.prs.slides.add_slide(self.layouts[layout])
        self.trans[s.slide_id] = transition
        self.n_pages += 1
        s._kit_layout = layout
        if title is not None and s.shapes.title is not None:
            if layout == "内容页":
                self.fit_title(s, title)
            else:
                s.shapes.title.text_frame.text = title
                for p in s.shapes.title.text_frame.paragraphs:
                    for r in p.runs:
                        _set_font(r, 44, True, self.t["ink"])
        if notes:
            s.notes_slide.notes_text_frame.text = notes
        return s

    def fit_title(self, s, text):
        ph = s.shapes.title
        w = W - 2 * MARGIN_X
        for size in (32, 30, 28, 26, 24):
            lines = wrap_lines(text, size, w - 2 * 7.2, True)
            if len(lines) <= 2:
                break
        else:
            raise Overflow(f"标题太长 [{text}]：24pt 仍超过 2 行，请缩短（每行约 {int((w-14)//24)} 字）")
        tf = ph.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.text = ""
        p = tf.paragraphs[0]
        p.line_spacing = Pt(round(size * LINE_K, 1))
        for seg, b in parse_runs(text):
            r = p.add_run()
            r.text = seg
            _set_font(r, size, True, self.t["em"] if b else self.t["ink"])
        wmax = max(sum(text_w(t, size, True) for t, _ in ln) for ln in lines)
        self.occupy(s, (MARGIN_X, TITLE_Y + TITLE_H - len(lines) * size * LINE_K, wmax + 14, len(lines) * size * LINE_K), "标题")
        self.report.append(("标题", text[:14], size, len(lines)))
        self.A(s, ph.name, "wipe", "after", 0, 0.5, "left")
        if self.t.get("title_marker"):
            last = sum(text_w(t_, size, True) for t_, _ in lines[-1])
            base_y = TITLE_Y + TITLE_H - 4
            mk = self.marker(s, (MARGIN_X + 4, base_y - size * 0.34, min(last + 8, W - 2 * MARGIN_X), size * 0.28), color="sand", rot=-0.5, alpha=0.9, name="标题马克笔")
            tree = s.shapes._spTree
            tree.remove(mk._element)
            tree.insert(2, mk._element)                               # 放到最底层，压在标题文字下面
            self.A(s, mk.name, "wipe", "with", 0.1, 0.5, "left")

    # ---------------------------------------------------------------- 零件
    def _rect(self, rect):
        return tuple(Emu(int(v * 12700)) for v in rect)

    def text(self, s, rect, paras, anchor="top", name="文本", align="left", inset=0.0, label=None, anim=None, grad=None, occupy=True):
        x, y, w, h = rect
        paras, need = fit_paras(paras, w, h, inset=max(inset, 2), label=label or name)
        sh = s.shapes.add_textbox(*self._rect(rect))
        self.uname(s, sh, name)
        write_paras(sh.text_frame, paras, inset=max(inset, 2), anchor=anchor, align=align, accent=self.t["coral"], em=self.t["em"])
        if grad:                                   # 文字渐变光：[(位置%, 色, 不透明度%)]，上到下
            for p_ in sh.text_frame.paragraphs:
                for r_ in p_.runs:
                    rpr = r_._r.get_or_add_rPr()
                    for e in rpr.findall(qn("a:solidFill")):
                        rpr.remove(e)
                    rpr.insert(0, parse_xml(_grad([(a, b, c) for a, b, c in grad], 90)))
        if occupy:
            self.occupy(s, rect, name)
        if anim:
            self.A(s, sh.name, *anim)
        self.report.append((name, paras[0]["text"][:12], paras[0]["size"], round(need)))
        return sh

    def card(self, s, rect, title, body=None, accent="coral", bullets=None, fill="card", title_size=28, body_size=21, name="卡片", anchor="top", k=None, anim=("fade", "beat", 0, 0.45), rot=0.0, pad_left=None, fg=None, pad_right=0):
        """圆角卡片：文字写在形状里（拖动卡片文字跟着走），左侧一条强调色细条与卡片成组。"""
        x, y, w, h = rect
        paras = []
        if title:
            paras.append(dict(text=title, size=title_size, bold=True, after=6, **({"color": fg} if fg else {})))
        for line in ([body] if isinstance(body, str) else (body or [])):
            paras.append(dict(text=line, size=body_size, color=fg or self.t["sub"], after=4))
        for b in bullets or []:
            paras.append(dict(text=b, size=body_size, color=fg or self.t["ink"], bullet=True, after=4))
        inset = 16
        wfit = w - 8 - ((pad_left - inset) if pad_left else 0) - pad_right
        paras, need = fit_paras(paras, wfit, h, sizes=[k] if k else None, inset=inset, label=f"{name}:{title}")
        box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *self._rect(rect))
        box.adjustments[0] = min(0.5, RADIUS / min(w, h))
        box.fill.solid()
        box.fill.fore_color.rgb = rgb(self.t[fill] if fill in self.t else fill)
        box.line.color.rgb = rgb(self.t["line"])
        box.line.width = Pt(0.75)
        box.shadow.inherit = False
        if self.t["card_alpha"] < 1:
            _alpha_fill(box, self.t["card_alpha"])
        if self.t["glow"]:
            _glow(box, self.t["glow"])
        if self.t.get("shadow"):
            _soft_shadow(box)
        self._skin(box)
        extras = []
        if self.t.get("glass"):
            gl = self.t["glass"]
            _lit(box, gl, alt=(fill == "card2"))
            if gl.get("pool"):                     # 卡下光池：放在卡片之前（下层）
                pc, pa, ph_ = gl["pool"]
                pool = s.shapes.add_shape(MSO_SHAPE.OVAL, *self._rect((x + 14, y + h - 30, w - 28, ph_)))
                pool.fill.solid()
                pool.fill.fore_color.rgb = rgb(pc)
                pool.line.fill.background()
                _alpha_fill(pool, pa / 100.0)
                psp = pool._element.spPr
                for e in psp.findall(qn("a:effectLst")):
                    psp.remove(e)
                psp.append(parse_xml(f'<a:effectLst {_A_NS}><a:softEdge rad="{int(40 * 12700)}"/></a:effectLst>'))
                box._element.addprevious(pool._element)
                self.uname(s, pool, "光池")
                extras.append(pool)
            if gl.get("sheen"):                    # 卡面斜向反光：左上白、向右下渐隐
                sh_ = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *self._rect(rect))
                sh_.adjustments[0] = min(0.5, RADIUS / min(w, h))
                ssp = sh_._element.spPr
                for tag in ("a:solidFill", "a:noFill", "a:ln", "a:effectLst"):
                    for e in ssp.findall(qn(tag)):
                        ssp.remove(e)
                i0 = list(ssp).index(ssp.find(qn("a:prstGeom"))) + 1
                ssp.insert(i0, parse_xml(_grad(gl["sheen"], 40)))
                ssp.insert(i0 + 1, parse_xml(f'<a:ln {_A_NS}><a:noFill/></a:ln>'))
                self.uname(s, sh_, "高光层")
                extras.append(sh_)
        box.name = f"{name}·{title or ''}"
        tf = box.text_frame
        write_paras(tf, paras, inset=inset, anchor=anchor, accent=self.t[accent], em=self.t["em"])
        tf.margin_left = Pt(inset + 8)
        if pad_right:
            tf.margin_right = Pt(inset + pad_right)      # 给右侧插图留位置
        if self.t.get("accent_bar", True):
            bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, *self._rect((x + 1, y + 14, 4, h - 28)))
            bar.fill.solid()
            bar.fill.fore_color.rgb = rgb(self.t[accent])
            bar.line.fill.background()
            bar.shadow.inherit = False
            bar.name = "强调条"
            grp = s.shapes.add_group_shape([box, bar])
            self.uname(s, grp, f"{name}组·{title or ''}")
            node = grp
        else:
            tf.margin_left = Pt(pad_left or inset)
            self.uname(s, box, f"{name}·{title or ''}")
            node = box
        if rot:
            node.rotation = rot
        self.occupy(s, rect, f"卡片「{title}」")
        if anim:
            self.A(s, node.name, *anim)
            for ex in extras:                       # 光池、反光层跟着卡片一起出现
                self.A(s, ex.name, "fade", "with", 0, anim[3] if len(anim) > 3 else 0.45)
        self.report.append((name, (title or "")[:12], paras[0]["size"] if paras else 0, round(need)))
        return box

    def cards(self, s, specs, **common):
        """同一排的几张卡片共用一个字号档位：先各自量，取最小的那档，再一起写。specs=[(rect, title, kwargs)]"""
        ks = []
        for rect, title, kw in specs:
            kk = dict(common); kk.update(kw)
            paras = []
            ts, bs = kk.get("title_size", 28), kk.get("body_size", 21)
            if title:
                paras.append(dict(text=title, size=ts, bold=True, after=6))
            for line in ([kk.get("body")] if isinstance(kk.get("body"), str) else (kk.get("body") or [])):
                paras.append(dict(text=line, size=bs, after=4))
            for b in kk.get("bullets") or []:
                paras.append(dict(text=b, size=bs, bullet=True, after=4))
            for k in (1.0, 0.92, 0.85, 0.78):
                try:
                    fit_paras(paras, rect[2] - 8, rect[3], sizes=[k], inset=16)
                    ks.append(k)
                    break
                except Overflow:
                    continue
            else:
                ks.append(0.78)
        k = min(ks)
        out = []
        for i, (rect, title, kw) in enumerate(specs):
            extra = {} if i == 0 else {"anim": ("fade", "with", 0.15 * i, 0.45)}
            out.append(self.card(s, rect, title, k=k, **{**common, **kw, **extra}))
        return out

    def panel(self, s, rect, fill="navy", name="面板", r=None, anim=("fade", "after", 0, 0.4)):
        """大面板：放在一组内容后面的深色或彩色底，和纸面拉开对比。先创建它，再放里面的东西。"""
        x, y, w, h = rect
        sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *self._rect(rect))
        sh.adjustments[0] = min(0.5, (r or self.t.get("panel_radius", 14)) / min(w, h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(self.t.get(fill, fill))
        sh.shadow.inherit = False
        sh.line.fill.background()
        self._skin(sh)
        self.uname(s, sh, name)
        if anim:
            self.A(s, sh.name, *anim)
        return sh

    def sign(self, s, x, y, size=64, color="coral", name="警示牌"):
        """警示牌：橙色三角形加感叹号，墨线描边。"""
        sh = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, *self._rect((x, y, size, size * 0.88)))
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(self.t[color])
        sh.shadow.inherit = False
        self._skin(sh, ow=2.5, dist=3)
        write_paras(sh.text_frame, [dict(text="!", size=int(size * 0.5), bold=True, color=self.t["white"], align="center")], inset=0, anchor="bottom")
        self.uname(s, sh, name)
        return sh

    def _pill_pts(self, x, y, w, h, n=14):
        import math
        r = h / 2
        pts = [(x + r + (w - 2 * r) * k / 1.0, y) for k in (0,)]
        pts = [(x + r, y), (x + w - r, y)]
        pts += [(x + w - r + r * math.sin(math.pi * k / n), y + r - r * math.cos(math.pi * k / n)) for k in range(1, n)]
        pts += [(x + w - r, y + h), (x + r, y + h)]
        pts += [(x + r - r * math.sin(math.pi * k / n), y + r + r * math.cos(math.pi * k / n)) for k in range(1, n)]
        return pts

    def pill(self, s, rect, text, color="ink", fg="auto", size=16, name="标签", anim=None):
        x, y, w, h = rect
        if self.t.get("skin"):
            if text_w(text, size, True) > w - 24:
                raise Overflow(f"标签放不下 [{text}]：宽 {w:.0f}pt，需要 {text_w(text, size, True) + 24:.0f}pt")
            pic = self._poly(s, self._pill_pts(x, y, w, h), color, name=f"{name}·{text}", anim=anim)
            self.text(s, rect, [dict(text=text, size=size, bold=True, color=self._fg(color) if fg == "auto" else self.t.get(fg, fg), align="center")], anchor="middle", align="center", name=f"{name}字·{text}", inset=0, anim=anim and ("fade", "with", 0.05, 0.3))
            self.occupy(s, rect, f"标签「{text}」")
            return pic
        if text_w(text, size, True) > w - 24:
            raise Overflow(f"标签放不下 [{text}]：宽 {w:.0f}pt，需要 {text_w(text, size, True)+24:.0f}pt")
        sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *self._rect(rect))
        sh.adjustments[0] = self.t.get("pill_adj", 0.5)
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(self.t.get(color, color))
        sh.line.fill.background()
        sh.shadow.inherit = False
        if self.t.get("shadow"):
            _soft_shadow(sh, 6, 3, 0.2)
        self._skin(sh, ow=1.5, dist=3)
        sh.name = f"{name}·{text}"
        self.occupy(s, rect, f"标签「{text}」")
        if anim:
            self.A(s, sh.name, *anim)
        write_paras(sh.text_frame, [dict(text=text, size=size, bold=True, color=self.on(self.t.get(color, color)) if fg == "auto" else self.t.get(fg, fg), align="center")], inset=6, anchor="middle")
        return sh

    def stat(self, s, rect, number, label, color="coral", num_size=54, name="数字"):
        x, y, w, h = rect
        paras = [dict(text=number, size=num_size, bold=True, color=self.t[color], after=2), dict(text=label, size=16, color=self.t["sub"])]
        return self.text(s, rect, paras, name=name)

    def bar_accent(self, s, x, y, w=6, h=60, color="coral"):
        sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, *self._rect((x, y, w, h)))
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(self.t[color])
        sh.line.fill.background()
        sh.shadow.inherit = False
        self.uname(s, sh, "强调条")
        return sh

    def flow(self, s, rect, steps, colors=None, name="流程", title_size=24, desc_size=18, conn_color=None, rots=None, gap=40.0, anchor="middle", pad_top=None):
        """横向流程：方框（文字在框里）+ 粘在方框上的箭头连接线。steps=[(标题, 说明)]"""
        x, y, w, h = rect
        n = len(steps)
        bw = (w - gap * (n - 1)) / n
        boxes = []
        colors = colors or ["navy", "teal", "coral", "sand"]
        for i, (ttl, desc) in enumerate(steps):
            bx = x + i * (bw + gap)
            paras = [dict(text=ttl, size=title_size, bold=True, color=self.on(self.t[colors[i % len(colors)]]), after=6, align="center"),
                     dict(text=desc, size=desc_size, color=self.on(self.t[colors[i % len(colors)]]), align="center")]
            paras, need = fit_paras(paras, bw, h, inset=12, label=f"{name}:{ttl}")
            b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *self._rect((bx, y, bw, h)))
            b.adjustments[0] = RADIUS / min(bw, h)
            b.fill.solid()
            b.fill.fore_color.rgb = rgb(self.t[colors[i % len(colors)]])
            b.line.fill.background()
            b.shadow.inherit = False
            if self.t.get("shadow"):
                _soft_shadow(b)
            self._skin(b)
            b.name = f"{name}·{i+1}·{ttl}"
            if rots:
                b.rotation = rots[i % len(rots)]
            write_paras(b.text_frame, paras, inset=12, anchor=anchor, align="center")
            if pad_top is not None:
                b.text_frame.margin_top = Pt(pad_top)             # 标题统一从同一高度开始，方便对齐
            boxes.append(b)
            self.report.append((name, ttl[:10], paras[0]["size"], round(need)))
        self.occupy(s, rect, name)
        conns = []
        for a, b in zip(boxes, boxes[1:]):
            c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, 0, 0, 0, 0)
            c.begin_connect(a, 3)
            c.end_connect(b, 1)
            c.line.color.rgb = rgb(self.t.get(conn_color, conn_color) if conn_color else self.t["ink"])
            c.line.width = Pt(3)
            ln = c.line._get_or_add_ln()
            ln.append(parse_xml('<a:tailEnd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" type="triangle" w="med" len="med"/>'))
            self.uname(s, c, "连接线")
            conns.append(c)
        # 动效沿流程方向：方框 1 → 连接线 1 → 方框 2 → …
        for i, b in enumerate(boxes):
            self.A(s, b.name, "fade", "beat" if i == 0 else "after", 0, 0.35)
            if i < len(conns):
                self.A(s, conns[i].name, "wipe", "after", 0, 0.25, "left")
        return boxes

    def layers(self, s, rect, items, name="分层"):
        """纵向分层带：左侧标签块 + 右侧说明。items=[(标签, 标题, 说明, 颜色)]；动效自上而下。"""
        x, y, w, h = rect
        self.occupy(s, rect, name)
        n = len(items)
        gap = 12.0
        bh = (h - gap * (n - 1)) / n
        lw = 150.0
        for i, (tag, ttl, desc, col) in enumerate(items):
            by = y + i * (bh + gap)
            lab = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *self._rect((x, by, lw, bh)))
            lab.adjustments[0] = RADIUS / min(lw, bh)
            lab.fill.solid()
            lab.fill.fore_color.rgb = rgb(self.t[col])
            lab.line.fill.background()
            lab.shadow.inherit = False
            lab.name = f"{name}标签·{tag}"
            self.A(s, lab.name, "fade", "beat", 0, 0.3)
            write_paras(lab.text_frame, [dict(text=tag, size=22, bold=True, color=self.on(self.t[col]), align="center")], inset=8, anchor="middle")
            paras = [dict(text=ttl, size=24, bold=True, after=4), dict(text=desc, size=19, color=self.t["sub"])]
            paras, need = fit_paras(paras, w - lw - 12, bh, inset=12, label=f"{name}:{tag}")
            body = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *self._rect((x + lw + 12, by, w - lw - 12, bh)))
            body.adjustments[0] = RADIUS / min(w - lw - 12, bh)
            body.fill.solid()
            body.fill.fore_color.rgb = rgb(self.t["card"])
            body.line.color.rgb = rgb(self.t["line"])
            body.line.width = Pt(0.75)
            body.shadow.inherit = False
            if self.t["card_alpha"] < 1:
                _alpha_fill(body, self.t["card_alpha"])
            if self.t["glow"]:
                _glow(body, self.t["glow"])
            body.name = f"{name}内容·{tag}"
            self.A(s, body.name, "wipe", "with", 0.12, 0.4, "left")
            write_paras(body.text_frame, paras, inset=12, anchor="middle")
            self.report.append((name, tag, paras[0]["size"], round(need)))

    def timeline(self, s, rect, items, name="时间线", desc_size=22, stage_size=40, stage_color="coral"):
        """横向时间线：粗墨线 + 带墨边的圆点；上方是大号阶段名（时间），下方是一张纸片说明卡。items=[(阶段, 说明)]
        每个阶段是一个讲点：第一个跟着轴线擦出，其余每个点击一次。"""
        x, y, w, h = rect
        n = len(items)
        seg = w / n
        top_h = stage_size * 1.5
        cy = y + top_h + 18
        line = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, *self._rect((x, cy, 0, 0))[:2], Emu(int((x + w) * 12700)), Emu(int(cy * 12700)))
        line.line.color.rgb = rgb(self.t.get("outline") or self.t["line"])
        line.line.width = Pt(4.5)
        line.line._get_or_add_ln().append(parse_xml('<a:tailEnd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" type="triangle" w="lg" len="lg"/>'))
        self.uname(s, line, "时间线主轴")
        self.occupy(s, rect, name)
        self.A(s, line.name, "wipe", "beat", 0, 0.3 * n + 0.4, "left")
        cols = ["teal", "coral", "navy", "sand"]
        card_y = cy + 34
        for i, (ph, desc) in enumerate(items):
            cx = x + seg * i
            dot = s.shapes.add_shape(MSO_SHAPE.OVAL, *self._rect((cx + 6, cy - 16, 32, 32)))
            dot.fill.solid()
            dot.fill.fore_color.rgb = rgb(self.t[cols[i % 4]])
            dot.shadow.inherit = False
            self._skin(dot, ow=2.5, dist=2)
            dot.name = f"节点·{i+1}"
            self.A(s, dot.name, "zoom", "with" if i == 0 else "beat", 0, 0.3)
            self.text(s, (cx, y, seg - 12, top_h), [dict(text=ph, size=stage_size, bold=True, color=self.t[stage_color])], name=f"{name}阶段·{i+1}", anim=("fade", "with", 0.05, 0.35))
            self.card(s, (cx, card_y, seg - 16, y + h - card_y), desc, accent="coral", title_size=desc_size, anchor="top", name=f"{name}说明", rot=(-0.8, 0.7)[i % 2],
                      anim=("fade", "with", 0.2, 0.4))

    def table(self, s, rect, header, rows, ratios=None, name="表格", size=20, hsize=20):
        """原生表格：列宽按比例，行高按量字结果，单元格文字带内边距，不使用样式自带的斑马纹。"""
        x, y, w, h = rect
        nc = len(header)
        ratios = ratios or [1] * nc
        tot = sum(ratios)
        cw = [w * r / tot for r in ratios]
        pad = 10.0
        # 量每行需要的高度
        heights = []
        for r_i, row in enumerate([header] + rows):
            sz = hsize if r_i == 0 else size
            hh = 0
            for c_i, txt in enumerate(row):
                lines = len(wrap_lines(txt, sz, cw[c_i] - 2 * pad, r_i == 0))
                hh = max(hh, lines * sz * LINE_K + 2 * 7)
            heights.append(max(hh, 34))
        total = sum(heights)
        if total > h + 0.5:
            raise Overflow(f"表格放不下 [{name}]：需要 {total:.0f}pt > 区域 {h:.0f}pt，请减少行数或字数")
        gf = s.shapes.add_table(len(rows) + 1, nc, *self._rect((x, y, w, total)))
        self.uname(s, gf, name)
        self.occupy(s, (x, y, w, total), name)
        self.A(s, gf.name, "fade", "beat", 0, 0.5)
        tbl = gf.table
        tblPr = gf._element.graphic.graphicData.tbl.tblPr
        tblPr.set("firstRow", "0")
        tblPr.set("bandRow", "0")
        sid = tblPr.find(qn("a:tableStyleId"))
        if sid is not None:
            sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"          # 无样式、无网格
        for i, c in enumerate(tbl.columns):
            c.width = Emu(int(cw[i] * 12700))
        for i, r in enumerate(tbl.rows):
            r.height = Emu(int(heights[i] * 12700))
        for r_i, row in enumerate([header] + rows):
            for c_i, txt in enumerate(row):
                c = tbl.cell(r_i, c_i)
                c.margin_left = c.margin_right = Pt(pad)
                c.margin_top = c.margin_bottom = Pt(7)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                c.fill.solid()
                c.fill.fore_color.rgb = rgb(self.t["navy"] if r_i == 0 else (self.t["card"] if r_i % 2 else self.t["card2"]))
                tf = c.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                sz = hsize if r_i == 0 else size
                p.line_spacing = Pt(round(sz * LINE_K, 1))
                for seg, b in parse_runs(txt):
                    rr = p.add_run()
                    rr.text = seg
                    _set_font(rr, sz, bold=(r_i == 0) or b or c_i == 0, color=self.on(self.t["navy"]) if r_i == 0 else (self.t["em"] if b else self.t["ink"]))
                _cell_border(c, self.t["line"])
        self.report.append((name, f"{len(rows)+1}行×{nc}列", size, round(total)))
        return gf

    def chart(self, s, rect, categories, values, series_name="数量", name="图表", colors=None, kind="bar", unit=""):
        """原生图表（带数据，PowerPoint 里可直接改数据）。"""
        x, y, w, h = rect
        cd = CategoryChartData()
        cd.categories = categories
        cd.add_series(series_name, values)
        ct = XL_CHART_TYPE.BAR_CLUSTERED if kind == "bar" else XL_CHART_TYPE.COLUMN_CLUSTERED
        gf = s.shapes.add_chart(ct, *self._rect(rect), cd)
        self.uname(s, gf, name)
        self.occupy(s, rect, name)
        self.A(s, gf.name, "wipe", "beat", 0, 0.6, "left")
        ch = gf.chart
        ch.has_legend = False
        ch.has_title = False
        ch.font.size = Pt(16)
        ch.font.name = FONT
        ch.font.color.rgb = rgb(self.t["ink"])
        plot = ch.plots[0]
        plot.gap_width = 55
        plot.vary_by_categories = False
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.font.size = Pt(22)
        dl.font.bold = not FONT_BOLD
        dl.font.name = FONT_BOLD or FONT
        dl.font.color.rgb = rgb(self.t["ink"])
        dl.number_format = '0"' + unit + '"'
        dl.number_format_is_linked = False
        dl.position = XL_LABEL_POSITION.OUTSIDE_END
        ser = plot.series[0]
        cols = colors or ["navy", "teal", "coral", "sand"]
        for i in range(len(values)):
            pt = ser.points[i]
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = rgb(self.t[cols[i % len(cols)]])
        va, ca = ch.value_axis, ch.category_axis
        va.visible = False
        va.has_major_gridlines = False
        va.maximum_scale = max(values) * 1.25
        va.minimum_scale = 0
        ca.format.line.color.rgb = rgb(self.t["line"])
        ca.tick_labels.font.size = Pt(20)
        ca.tick_labels.font.color.rgb = rgb(self.t["ink"])
        ca.tick_labels.font.bold = not FONT_BOLD
        ca.tick_labels.font.name = FONT_BOLD or FONT
        ca.has_major_gridlines = False
        if kind == "bar":
            ca.reverse_order = True
        self.report.append((name, series_name, 16, len(values)))
        return gf

    def linechart(self, s, rect, categories, values, series_name="数值", name="折线图", color="coral", unit="%", vmax=None, label_size=18, tick_size=16, anim=("wipe", "beat", 0, 1.0, "left")):
        """原生折线图（带数据，PowerPoint 里可直接改数据）：平滑曲线、圆点标记、点上标数值、淡色横网格。"""
        from pptx.enum.chart import XL_MARKER_STYLE
        x, y, w, h = rect
        cd = CategoryChartData()
        cd.categories = categories
        cd.add_series(series_name, values)
        gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, *self._rect(rect), cd)
        self.uname(s, gf, name)
        self.occupy(s, rect, name)
        if anim:
            self.A(s, gf.name, *anim)
        ch = gf.chart
        ch.has_legend = False
        ch.has_title = False
        ch.font.size = Pt(tick_size)
        ch.font.name = FONT
        ch.font.color.rgb = rgb(self.t["sub"])
        plot = ch.plots[0]
        ser = plot.series[0]
        ser.smooth = True
        ser.format.line.color.rgb = rgb(self.t[color])
        ser.format.line.width = Pt(4)
        ser.marker.style = XL_MARKER_STYLE.CIRCLE
        ser.marker.size = 11
        ser.marker.format.fill.solid()
        ser.marker.format.fill.fore_color.rgb = rgb(self.t["white"])
        ser.marker.format.line.color.rgb = rgb(self.t[color])
        ser.marker.format.line.width = Pt(3)
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.font.size = Pt(label_size)
        dl.font.bold = not FONT_BOLD
        dl.font.name = FONT_BOLD or FONT
        dl.font.color.rgb = rgb(self.t["ink"])
        dl.number_format = '0"' + unit + '"'
        dl.number_format_is_linked = False
        dl.position = XL_LABEL_POSITION.ABOVE
        va, ca = ch.value_axis, ch.category_axis
        va.minimum_scale = 0
        va.maximum_scale = vmax or max(values) * 1.2
        va.visible = False
        va.has_major_gridlines = True
        va.major_gridlines.format.line.color.rgb = rgb(self.t["line"])
        va.major_gridlines.format.line.width = Pt(0.75)
        ca.format.line.color.rgb = rgb(self.t["line"])
        ca.tick_labels.font.size = Pt(tick_size)
        ca.tick_labels.font.color.rgb = rgb(self.t["sub"])
        ca.has_major_gridlines = False
        self.report.append((name, series_name, tick_size, len(values)))
        return gf

    def picture(self, s, rect, path, alt, name="图片", keep_ratio=True):
        x, y, w, h = rect
        pic = s.shapes.add_picture(str(path), *self._rect(rect))
        if keep_ratio:
            iw, ih = pic.image.size
            r = min(w / iw, h / ih)
            nw, nh = iw * r, ih * r
            pic.left, pic.top, pic.width, pic.height = (Emu(int(v * 12700)) for v in (x + (w - nw) / 2, y + (h - nh) / 2, nw, nh))
        pic._element.nvPicPr.cNvPr.set("descr", alt)
        pic.name = name
        return pic

    def footer(self, s, n, total, label="如何用元素方案优化PPT"):
        self.text(s, (MARGIN_X, H - 34, 500, 22), [dict(text=label, size=12, color=self.t["sub"])], name="页脚", inset=0)
        self.text(s, (W - MARGIN_X - 100, H - 34, 100, 22), [dict(text=f"{n} / {total}", size=12, color=self.t["sub"], align="right")], name="页码", inset=0)

    def tape(self, s, x, y, w=96, h=28, rot=-6.0, color="sand", name="胶带", anim=("fade", "with", 0.2, 0.3)):
        """胶带：半透明柠檬黄，贴在卡片的角上。"""
        sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, *self._rect((x, y, w, h)))
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(self.t.get(color, color))
        _alpha_fill(sh, 0.78)
        sh.line.fill.background()
        sh.shadow.inherit = False
        sh.rotation = rot
        self.uname(s, sh, name)
        if anim:
            self.A(s, sh.name, *anim)
        return sh

    def plus(self, s, x, y, size=16, color="coral", name="加号", anim=("fade", "with", 0.3, 0.3)):
        """小加号涂鸦（海报同款）。"""
        sh = s.shapes.add_shape(MSO_SHAPE.MATH_PLUS, *self._rect((x, y, size, size)))
        sh.adjustments[0] = 0.22
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(self.t.get(color, color))
        sh.line.fill.background()
        sh.shadow.inherit = False
        self.uname(s, sh, name)
        if anim:
            self.A(s, sh.name, *anim)
        return sh

    def corner_icon(self, s, card_rect, path, size=54, pos="br", pad=8, name="角标", anim=("fade", "with", 0.3, 0.3)):
        """给较空的卡片加一个小插画角标（放在右下、右上、左下或左上）。"""
        x, y, w, h = card_rect
        ix = x + w - size - pad if pos[1] == "r" else x + pad
        iy = y + h - size - pad if pos[0] == "b" else y + pad
        pic = self.picture(s, (ix, iy, size, size), path, "角标插画", name=name)
        self.uname(s, pic, name)
        if anim:
            self.A(s, pic.name, *anim)
        return pic

    def note(self, s, rect, text, size=26, rot=-2.0, color="coral", name="批注", anim=None):
        """手写批注（霞鹜文楷等手写体），可微旋转。"""
        sh = self.text(s, rect, [dict(text=text, size=size, color=self.t[color], kind="hand")], name=name, anim=anim)
        if rot:
            sh.rotation = rot
        return sh

    def marker(self, s, rect, color="sand", rot=-0.8, alpha=0.8, name="马克笔高亮", anim=None):
        """马克笔高亮条：半透明色块，压在文字下面（先创建它，再创建文字）。"""
        sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, *self._rect(rect))
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(self.t.get(color, color))
        _alpha_fill(sh, alpha)
        sh.line.fill.background()
        sh.shadow.inherit = False
        sh.rotation = rot
        self.uname(s, sh, name)
        if anim:
            self.A(s, sh.name, *anim)
        return sh

    def tip(self, s, rect, kind, text, size=26, name="提示卡", visible=0.75, max_h=170.0):
        """船长提示卡：卡片左侧是彩色标签章，右边一句话；船长贴纸从卡片后面探出头和肩。
        kind 取自主题里的 tips 字典：{kind: dict(sprite=图片路径, label=标签文字, color=颜色名)}。一页最多一个。
        visible 是船长露出卡片上沿的比例；卡片上方要留出 max_h*visible 的空间。"""
        x, y, w, h = rect
        spec = self.t["tips"][kind]
        from PIL import Image as _I
        iw, ih = _I.open(spec["sprite"]).size
        sh_ = min(max_h, h * 2.3)
        sw = sh_ * iw / ih
        cx = x + w - sw / 2 - 26
        foot = y + sh_ * (1 - visible)                          # 露出 visible 的部分，其余藏在卡片后面
        self.sticker(s, spec["sprite"], cx, foot, sh_, alt=f"Q 版船长，{spec['label']}", name=f"{name}·船长", anim=("zoom", "beat", 0, 0.45))
        chip_w = 118
        self.card(s, rect, text, accent=spec["color"], title_size=size, anchor="middle", name=name, anim=("fade", "with", 0.1, 0.4), pad_left=chip_w + 34)
        self.pill(s, (x + 18, y + (h - 38) / 2, chip_w, 38), spec["label"], color=spec["color"], size=20, name=f"{name}·标签", anim=("fade", "with", 0.2, 0.3))

    def footer_band(self, s, left, n, total):
        """页面底部一条很细的横幅：左边放讲次和课程名，右边放页码。不抢戏。
        主题 band_plain=True 时不铺底色，只留一条细线，页码用强调色（刊物风）。"""
        t = self.t
        plain = t.get("band_plain")
        if not plain:
            band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, *self._rect((0, H - 22, W, 22)))
            band.fill.solid()
            band.fill.fore_color.rgb = rgb(t.get("sky", t["card2"]))
            band.line.fill.background()
            band.shadow.inherit = False
            band.name = "页脚条"
        top = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, *self._rect((MARGIN_X if plain else 0, H - 22, (W - 2 * MARGIN_X) if plain else W, 0.75 if plain else 1.5)))
        top.fill.solid()
        top.fill.fore_color.rgb = rgb(t["line"] if plain else (t.get("outline") or t["ink"]))
        top.line.fill.background()
        top.shadow.inherit = False
        top.name = "页脚线"
        self.text(s, (MARGIN_X, H - 21, 600, 20), [dict(text=left, size=11, color=t["sub"])], name="页脚", inset=0, anchor="middle")
        self.text(s, (W - MARGIN_X - 100, H - 21, 100, 20), [dict(text=f"{n} / {total}", size=11, color=t["coral"] if plain else t["sub"], align="right")], name="页码", inset=0, anchor="middle")

    # ---------------------------------------------------------------- 260930 新增零件：不靠“卡片装文字”的版面语言
    def _shape(self, s, kind, rect, fill=None, line=None, lw=0.75, name="形状", radius=None):
        sh = s.shapes.add_shape(kind, *self._rect(rect))
        if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
            sh.adjustments[0] = min(0.5, radius / min(rect[2], rect[3]))
        if fill:
            sh.fill.solid()
            sh.fill.fore_color.rgb = rgb(self.t.get(fill, fill))
        else:
            sh.fill.background()
        if line:
            sh.line.color.rgb = rgb(self.t.get(line, line))
            sh.line.width = Pt(lw)
        else:
            sh.line.fill.background()
        sh.shadow.inherit = False
        self.uname(s, sh, name)
        return sh

    def hline(self, s, x, y, w, color="line", h=0.75, name="分隔线", anim=("wipe", "with", 0.1, 0.4, "left")):
        sh = self._shape(s, MSO_SHAPE.RECTANGLE, (x, y, w, h), fill=color, name=name)
        if anim:
            self.A(s, sh.name, *anim)
        return sh

    def badge(self, s, x, y, d, text, color="coral", fg="auto", size=None, name="序号", anim=("zoom", "with", 0.1, 0.3)):
        if self.t.get("skin"):
            import math
            pts = [(x + d / 2 + d / 2 * math.cos(2 * math.pi * k / 28), y + d / 2 + d / 2 * math.sin(2 * math.pi * k / 28)) for k in range(28)]
            pic = self._poly(s, pts, color, name=name, anim=anim)
            self.text(s, (x, y, d, d), [dict(text=text, size=size or max(18, int(d * 0.5)), bold=True, color=self._fg(color) if fg == "auto" else self.t.get(fg, fg), align="center")], anchor="middle", align="center", name=name + "字", inset=0, anim=anim and ("fade", "with", 0.1, 0.3))
            return pic
        """圆形序号章（也可放一个 ✓ 或一个字）。"""
        sh = self._shape(s, MSO_SHAPE.OVAL, (x, y, d, d), fill=color, name=f"{name}·{text}")
        write_paras(sh.text_frame, [dict(text=text, size=size or round(d * 0.46), bold=True, color=self.on(self.t.get(color, color)) if fg == "auto" else self.t.get(fg, fg), align="center")], inset=0, anchor="middle")
        self.occupy(s, (x, y, d, d), "序号章")
        if anim:
            self.A(s, sh.name, *anim)
        return sh

    def steps(self, s, rect, items, color="coral", title_size=22, desc_size=17, d=40, name="步骤"):
        """横向步骤：序号章串在一条细线上，标题和说明写在下面，没有卡片。items = [(标题, 说明), ...]"""
        x, y, w, h = rect
        n = len(items)
        colw = w / n
        self.hline(s, x + d, y + d / 2 - 0.75, w - d - 6, "line", 1.5, name + "连线", ("wipe", "beat", 0, 0.5, "left"))
        for i, (tt, dd) in enumerate(items):
            cx = x + i * colw
            self.badge(s, cx, y, d, str(i + 1), color, name=name + "章", anim=("zoom", "with", 0.1 * i, 0.3))
            paras = [dict(text=tt, size=title_size, bold=True, after=4)]
            if dd:
                paras.append(dict(text=dd, size=desc_size, color=self.t["sub"]))
            self.text(s, (cx, y + d + 14, colw - 18, h - d - 14), paras, name=f"{name}{i + 1}", inset=0, anim=("fade", "with", 0.1 * i + 0.1, 0.3))

    def chevrons(self, s, rect, items, colors=None, size=20, name="流程"):
        """箭头形流程：一排 chevron。容器走 _poly（风格材质，或原生多边形套主题的描边、硬投影、细线），文字是真文字。"""
        x, y, w, h = rect
        n = len(items)
        ov = h * 0.30
        gap = 10.0
        cw_ = (w - gap * (n - 1) + ov * (n - 1)) / n
        pal = colors or (["sky", "peach", "mint", "butter", "pink"] if "sky" in self.t else ["coral", "teal", "sand", "green", "navy"])
        for i, tt in enumerate(items):
            col = pal[i % len(pal)]
            x0 = x + i * (cw_ - ov + gap)
            pts = [(x0, y), (x0 + cw_ - ov, y), (x0 + cw_, y + h / 2), (x0 + cw_ - ov, y + h), (x0, y + h)]
            if i > 0:
                pts.append((x0 + ov, y + h / 2))
            self._poly(s, pts, col, name=f"{name}箭头", anim=("fade", "beat" if i == 0 else "with", 0.15 * i, 0.35))
            tx0 = x0 + (ov if i > 0 else 0) + 10
            self.text(s, (tx0, y, cw_ - ov - (ov if i > 0 else 0) - 20 + (ov if i == 0 else 0) * 0, h), [dict(text=tt, size=size, bold=True, color=self._fg(col), align="center")], anchor="middle", align="center", name=f"{name}字", inset=0, anim=("fade", "with", 0.15 * i + 0.05, 0.3))
        self.occupy(s, rect, "流程")

    def vs(self, s, cx, cy, d=54, text="VS", color="navy", name="对比章"):
        return self.badge(s, cx - d / 2, cy - d / 2, d, text, color, size=round(d * 0.34), name=name, anim=("zoom", "beat", 0, 0.3))

    def quote(self, s, rect, text, who=None, size=30, color="coral", name="引语"):
        """大引号加一段话，没有容器。"""
        x, y, w, h = rect
        self.text(s, (x, y - 16, 90, 120), [dict(text="“", size=96, bold=True, color=self.t.get(color, color))], name=name + "引号", inset=0, anim=("zoom", "beat", 0, 0.4))
        self.text(s, (x + 6, y + 64, w - 6, h - 64 - (34 if who else 0)), [dict(text=text, size=size, bold=True)], name=name, inset=0, anim=("fade", "with", 0.15, 0.4))
        if who:
            self.text(s, (x + 6, y + h - 30, w, 28), [dict(text="—— " + who, size=16, color=self.t["sub"])], name=name + "署名", inset=0, anim=("fade", "with", 0.3, 0.3))

    def checkrows(self, s, rect, items, size=22, row_h=54, color="green", name="清单", mark="✓", numbered=False):
        """清单行：✓ 章加一行字，行间一条细线，没有卡片。"""
        x, y, w, h = rect
        for i, tt in enumerate(items):
            yy = y + i * row_h
            self.badge(s, x, yy + (row_h - 30) / 2, 30, (str(i + 1) if numbered else mark), color, size=18, name=name + "章", anim=("zoom", "beat" if i == 0 else "with", 0.08 * i, 0.25))
            self.text(s, (x + 46, yy, w - 46, row_h), [dict(text=tt, size=size)], anchor="middle", name=f"{name}{i + 1}", inset=0, anim=("fade", "with", 0.08 * i + 0.05, 0.3))
            if i < len(items) - 1:
                self.hline(s, x + 46, yy + row_h - 0.5, w - 46, "line", 0.75, name + "线", ("wipe", "with", 0.08 * i, 0.3, "left"))

    def kv(self, s, rect, rows, key_w=150, size=20, row_h=56, name="键值"):
        """键值行：左边是键（粗体），右边是值，行间细线。"""
        x, y, w, h = rect
        for i, (k, v) in enumerate(rows):
            yy = y + i * row_h
            self.text(s, (x, yy, key_w, row_h), [dict(text=k, size=size, bold=True, color=self.t["coral"])], anchor="middle", name=f"{name}键{i + 1}", inset=0, anim=("fade", "beat" if i == 0 else "with", 0.08 * i, 0.3))
            self.text(s, (x + key_w + 16, yy, w - key_w - 16, row_h), [dict(text=v, size=size)], anchor="middle", name=f"{name}值{i + 1}", inset=0, anim=("fade", "with", 0.08 * i + 0.05, 0.3))
            self.hline(s, x, yy + row_h - 0.5, w, "line", 0.75, name + "线", ("wipe", "with", 0.08 * i, 0.3, "left"))

    def callout(self, s, rect, text, fill="butter", bar="coral", size=22, bold=True, name="要点条"):
        if self.t.get("skin"):
            x, y, w, h = rect
            pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            pic = self._poly(s, pts, fill, name=name, anim=("fade", "beat", 0, 0.4))
            self.text(s, (x + 22, y, w - 44, h), [dict(text=text, size=size, bold=bold, color=self._fg(fill))], anchor="middle", name=name + "字", inset=0, anim=("fade", "with", 0.05, 0.3))
            self.occupy(s, rect, "要点条")
            return pic
        """提示条：淡色底加左侧粗竖条，一句话。"""
        x, y, w, h = rect
        bg = self._shape(s, MSO_SHAPE.RECTANGLE, rect, fill=fill, name=name)
        self.A(s, bg.name, "fade", "beat", 0, 0.4)
        b = self._shape(s, MSO_SHAPE.RECTANGLE, (x, y, 6, h), fill=bar, name=name + "竖条")
        self.A(s, b.name, "wipe", "with", 0.05, 0.3, "up")
        self.text(s, (x + 26, y, w - 40, h), [dict(text=text, size=size, bold=bold)], anchor="middle", name=name + "字", inset=0, anim=("fade", "with", 0.15, 0.3))
        self.occupy(s, rect, "要点条")

    def tags(self, s, x, y, items, size=16, colors=None, gap=10, h=32, name="标签"):
        """一行标签（药丸），自动依次排开。"""
        cx = x
        for i, tt in enumerate(items):
            w = text_w(tt, size, True) + 30
            self.pill(s, (cx, y, w, h), tt, color=(colors or ["sky", "peach", "mint", "butter", "pink"])[i % 5], fg="ink", size=size, name=name, anim=("fade", "with", 0.08 * i, 0.3))
            cx += w + gap

    def cycle(self, s, center, r, items, size=20, name="循环"):
        """环形循环：一圈细线，节点药丸落在圆周上。"""
        import math
        cx, cy = center
        ring = self._shape(s, MSO_SHAPE.OVAL, (cx - r, cy - r, 2 * r, 2 * r), line="line", lw=2.0, name=name + "环")
        self.A(s, ring.name, "zoom", "beat", 0, 0.5)
        n = len(items)
        for i, tt in enumerate(items):
            a = -math.pi / 2 + 2 * math.pi * i / n
            w = text_w(tt, size, True) + 34
            px, py = cx + r * math.cos(a), cy + r * math.sin(a)
            self.pill(s, (px - w / 2, py - 19, w, 38), tt, color=["sky", "peach", "mint", "butter", "pink"][i % 5], fg="ink", size=size, name=name + "点", anim=("zoom", "with", 0.15 * i, 0.3))

    def window(self, s, rect, title, dark=False, name="窗口", anim=("fade", "beat", 0, 0.4)):
        """应用窗口线稿：标题栏加三个小圆点。dark=True 是深色终端。"""
        x, y, w, h = rect
        body = self.panel(s, rect, fill="navy" if dark else "card", name=name, anim=anim)
        if not dark:
            body.line.color.rgb = rgb(self.t["line"])
            body.line.width = Pt(1)
        bar = self._shape(s, MSO_SHAPE.RECTANGLE, (x, y, w, 26), fill="2A3A5E" if dark else "E3EAF4", name=name + "标题栏")
        self.A(s, bar.name, "fade", "with", 0.05, 0.3)
        for i, col in enumerate((self.t["coral"], self.t["sand"], "8FA0C4")):
            d_ = self._shape(s, MSO_SHAPE.OVAL, (x + 10 + i * 15, y + 8, 10, 10), fill=col, name=name + "圆点")
            self.A(s, d_.name, "fade", "with", 0.05, 0.3)
        self.text(s, (x + 62, y + 3, w - 80, 20), [dict(text=title, size=11, color="C9D3E8" if dark else self.t["sub"])], name=name + "标题", inset=0, anchor="middle", anim=("fade", "with", 0.1, 0.3))

    def sticker(self, s, path, x, foot_y, h, flip=False, alt="", name="人物", morph=None, anim=("zoom", "after", 0, 0.5), ground_shadow=False):
        """把带白边的透明 PNG 立在 (x, foot_y)，x 为中心，h 为高度。"""
        from PIL import Image
        iw, ih = Image.open(path).size
        w = h * iw / ih
        if ground_shadow:
            sw_ = w * 0.66
            gs = s.shapes.add_shape(MSO_SHAPE.OVAL, *self._rect((x - sw_ / 2, foot_y - 9, sw_, 18)))
            gs.fill.solid()
            gs.fill.fore_color.rgb = rgb(self.t.get("outline") or self.t["ink"])
            _alpha_fill(gs, 0.30)
            gs.line.fill.background()
            gs.shadow.inherit = False
            eff = gs._element.spPr.find(qn("a:effectLst"))
            etree.SubElement(eff, qn("a:softEdge")).set("rad", str(int(7 * 12700)))
            self.uname(s, gs, "接触阴影")
            if not (morph and self.trans.get(s.slide_id) == "morph"):
                self.A(s, gs.name, "fade", "after", 0, 0.4)
        pic = s.shapes.add_picture(str(path), *self._rect((x - w / 2, foot_y - h, w, h)))
        self._overlap(s, (x - w / 2 + 0.18 * w, foot_y - h + 0.06 * h, w * 0.64, h * 0.9), f"人物「{name}」", allow=("对话气泡",))
        if flip:
            pic._element.spPr.find(qn("a:xfrm")).set("flipH", "1")
        pic._element.nvPicPr.cNvPr.set("descr", alt or name)
        pic.name = self.mname(morph) if morph else name
        if not morph:
            self.uname(s, pic, name)
        self.occupy(s, (x - w / 2 + 0.18 * w, foot_y - h + 0.06 * h, w * 0.64, h * 0.9), f"人物「{name}」")
        if not (morph and self.trans.get(s.slide_id) == "morph"):      # 平滑过渡进来的人物不再播入场动画，由切换负责
            self.A(s, pic.name, *anim if not ground_shadow else ("zoom", "with", 0, 0.5))
        return pic

    def deco(self, s, path, size, anchor="tr", alt="装饰", name="装饰", margin=2.0, morph=None):
        """装饰图：靠页面边角放置（anchor = tr/tl/br/bl），size=(w, h)。压到内容，或一页装饰超过 1 处，记入告警。"""
        w, h = size
        x = W - w - margin if anchor[1] == "r" else margin
        y = margin if anchor[0] == "t" else H - h - margin
        n = self._deco_n.get(s.slide_id, 0) + 1
        self._deco_n[s.slide_id] = n
        if n > 1:
            self.warnings.append(f"第 {self._idx(s)} 页：装饰超过 1 处")
        self._overlap(s, (x, y, w, h), f"装饰「{name}」")
        pic = self.picture(s, (x, y, w, h), path, alt, name=name)
        if morph:
            pic.name = self.mname(morph)
        else:
            self.uname(s, pic, name)
        if not (morph and self.trans.get(s.slide_id) == "morph"):
            self.A(s, pic.name, "fade", "with", 0.3, 0.8)
        return pic

    def bubble(self, s, rect, text, tail=(-0.45, 0.75), size=20, color="card", name="对话气泡"):
        """对话气泡：原生圆角标注形状，文字在里面；tail = 尖角相对中心的偏移（占宽高的比例）。"""
        x, y, w, h = rect
        paras, need = fit_paras([dict(text=text, size=size, bold=True, align="center", color=self.t["dark_text"])], w, h, inset=10, label=name)
        sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT, *self._rect(rect))
        sh.adjustments[0], sh.adjustments[1], sh.adjustments[2] = tail[0], tail[1], 0.2
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb("FFFFFF")
        sh.line.fill.background()
        sh.shadow.inherit = False
        if self.t["glow"]:
            _glow(sh, self.t["glow"])
        self.uname(s, sh, name)
        self.occupy(s, rect, "对话气泡")
        self.A(s, sh.name, "zoom", "beat", 0, 0.35)
        write_paras(sh.text_frame, paras, inset=10, anchor="middle", align="center", accent=self.t["coral"], em=self.t["coral"])
        self.report.append((name, text[:10], paras[0]["size"], round(need)))
        return sh

    def slot(self, s, rect, path, kind="auto", treat=None, backing=None, focus=(0.5, 0.4), frame=None, z="front",
             alt="", name="素材", poster=None, pop=0.0, anim=None, allow=()):
        """素材槽位：放用户提供的照片、抠图、截图、Logo、视频。设计阶段就和用户约定好，落地时按约定做。

        kind    auto（按文件自动判断）/ photo（不透明照片，铺满并裁切）/ cutout（透明底抠图，完整显示不裁切）/
                screenshot（截图，完整显示带细边）/ logo（完整显示）/ video（视频，带封面图）
        treat   photo 和 screenshot 可用：rect / rounded / circle（圆形要求槽位接近正方形）。抠图不能再套形状。
        backing 抠图的底衬：("circle"|"rounded", 颜色名)，先画底衬，抠图站在它上面；pop 是抠图向上探出底衬的比例（0.15 = 高出 15%）。
        focus   照片裁切时保留的视觉重心 (x, y)，0–1。
        frame   (颜色名, 线宽pt) 的描边。
        z       front（默认，按创建顺序）/ back（放到本页最底层，当背景用）。
        allow   允许与哪些已有内容重叠（重叠检查白名单，如 ("卡片",)）。
        """
        from PIL import Image
        path = pathlib.Path(path)
        ext = path.suffix.lower()
        x, y, w, h = rect
        if kind == "auto":
            if ext in (".mp4", ".mov", ".m4v", ".wmv"):
                kind = "video"
            else:
                im = Image.open(path)
                a = im.convert("RGBA").getchannel("A")
                import numpy as _np
                kind = "cutout" if (_np.array(a) < 250).mean() > 0.02 else "photo"
        if treat and kind == "cutout":
            self.warnings.append(f"第 {self._idx(s)} 页：素材「{name}」是透明底抠图，不应再套 {treat} 形状，已忽略")
            treat = None
        if treat == "circle" and abs(w - h) > 0.15 * max(w, h):
            self.warnings.append(f"第 {self._idx(s)} 页：素材「{name}」要圆形，但槽位 {w:.0f}×{h:.0f} 不是正方形，会变成椭圆")
        if z != "back" and not self._overlap(s, rect, f"素材「{name}」", allow=tuple(allow) + ("素材",)):
            pass
        rx, ry, rw, rh = x, y, w, h
        if kind == "cutout" and backing:
            shp, col = backing
            bk = s.shapes.add_shape(MSO_SHAPE.OVAL if shp == "circle" else MSO_SHAPE.ROUNDED_RECTANGLE, *self._rect(rect))
            bk.fill.solid()
            bk.fill.fore_color.rgb = rgb(self.t.get(col, col))
            bk.line.fill.background()
            bk.shadow.inherit = False
            self.uname(s, bk, f"{name}·底衬")
            if z == "back":
                tree = s.shapes._spTree
                tree.remove(bk._element)
                tree.insert(2, bk._element)
        if kind == "video":
            import cv2
            cap = cv2.VideoCapture(str(path))
            ok, fr = cap.read()
            vw, vh = (fr.shape[1], fr.shape[0]) if ok else (16, 9)
            if poster is None and ok:
                poster = path.with_suffix(".poster.png")
                cv2.imencode(".png", fr)[1].tofile(str(poster))
            r = min(w / vw, h / vh)
            nw, nh = vw * r, vh * r
            rx, ry, rw, rh = x + (w - nw) / 2, y + (h - nh) / 2, nw, nh
            mime = {".mp4": "video/mp4", ".mov": "video/quicktime", ".m4v": "video/mp4", ".wmv": "video/x-ms-wmv"}[ext]
            pic = s.shapes.add_movie(str(path), *self._rect((rx, ry, rw, rh)), poster_frame_image=str(poster) if poster else None, mime_type=mime)
        else:
            iw, ih = Image.open(path).size
            if kind == "photo":
                pic = s.shapes.add_picture(str(path), *self._rect(rect))
                vis_x = min(1.0, (w / h) / (iw / ih))
                vis_y = min(1.0, (iw / ih) / (w / h))
                cx_, cy_ = (1 - vis_x), (1 - vis_y)
                pic.crop_left, pic.crop_right = cx_ * focus[0], cx_ * (1 - focus[0])
                pic.crop_top, pic.crop_bottom = cy_ * focus[1], cy_ * (1 - focus[1])
            else:
                box_h = h * (1 + pop) if kind == "cutout" else h
                r = min(w / iw, box_h / ih)
                nw, nh = iw * r, ih * r
                if kind == "cutout":
                    rx, ry, rw, rh = x + (w - nw) / 2, y + h - nh, nw, nh          # 站在槽位底边中间
                else:
                    rx, ry, rw, rh = x + (w - nw) / 2, y + (h - nh) / 2, nw, nh
                pic = s.shapes.add_picture(str(path), *self._rect((rx, ry, rw, rh)))
            if treat in ("circle", "rounded"):
                pic.auto_shape_type = MSO_SHAPE.OVAL if treat == "circle" else MSO_SHAPE.ROUNDED_RECTANGLE
            if kind == "screenshot" and not frame:
                frame = ("line", 1.0)
            gi = self.t.get("glass_img")
            if gi and treat == "rounded" and z != "back":
                _lit_pic(pic, gi, min(0.5, RADIUS / min(rw, rh)))      # 图片卡：细边线、轻投影、与卡片一致的圆角
                frame = None
            if frame:
                pic.line.color.rgb = rgb(self.t.get(frame[0], frame[0]))
                pic.line.width = Pt(frame[1])
        pic._element.xpath(".//p:cNvPr")[0].set("descr", alt or name)
        self.uname(s, pic, name)
        if z == "back":
            tree = s.shapes._spTree
            tree.remove(pic._element)
            tree.insert(2, pic._element)
        self.occupy(s, (rx, ry, rw, rh), "素材")
        if anim:
            self.A(s, pic.name, *anim)
        self.report.append(("素材槽位", f"{kind}:{name}", 0, 0))
        return pic


    # ------------------------------------------------------------ 图示零件（原生形状，跟随主题皮肤）
    # 循环、金字塔、漏斗、矩阵、阵列、韦恩、环形图：内容有"循环 / 层级 / 筛选 / 分类 / 重叠 / 占比"结构时用它们，不要全部排成一排卡片。
    def _col(self, c):
        return self.t.get(c, c)

    def _dark_bg(self):
        h = self.t["bg"].lstrip("#")
        return (0.299 * int(h[0:2], 16) + 0.587 * int(h[2:4], 16) + 0.114 * int(h[4:6], 16)) < 110

    def _fg(self, c):
        """图示里压在容器上的文字色：玻璃材质（半透明）用主题文字色，其余按容器颜色择优。"""
        sk = self.t.get("skin")
        if sk == "glass":
            return self.t["ink"]
        col = self._col(c).lstrip("#")
        if sk == "ink" and not self._dark_bg():                    # 水墨材质会把很浅的颜色调入墨灰，文字色要按调整后的颜色选
            r, g, b = (int(col[i:i + 2], 16) for i in (0, 2, 4))
            if (r + g + b) / 3 > 190:
                col = "%02X%02X%02X" % (int(r * 0.7 + 52 * 0.3), int(g * 0.7 + 60 * 0.3), int(b * 0.7 + 58 * 0.3))
        return self.on(col)

    def _poly(self, s, pts, fill, name="形状", line=None, lw=0.75, anim=None, alpha=1.0):
        """多边形容器。pts 单位 pt。主题有 skin（paper / ink / glass）时，渲染成该材质的 PNG 当容器（文字另放真文字）；
        否则是原生自由形状，填充与描边走主题皮肤（描边、硬投影、玻璃光影）。"""
        skin = self.t.get("skin")
        if skin:
            import zlib
            import diagram_skins as DS
            seed = zlib.crc32(f"{name}{pts[0]}".encode()) % 9973
            png, (bx, by, bw, bh) = DS.render(skin, pts, self._col(fill), seed=seed, alpha=alpha, dark=self._dark_bg())
            m = DS.MARGIN
            pic = s.shapes.add_picture(str(png), *self._rect((bx - m, by - m, bw + 2 * m, bh + 2 * m)))
            pic._element.xpath(".//p:cNvPr")[0].set("descr", f"{name}（材质容器）")
            self.uname(s, pic, name)
            if anim:
                self.A(s, pic.name, *anim)
            return pic
        e = lambda v: int(round(v * 12700))
        fb = s.shapes.build_freeform(e(pts[0][0]), e(pts[0][1]), scale=1.0)
        fb.add_line_segments([(e(x), e(y)) for x, y in pts[1:]], close=True)
        sh = fb.convert_to_shape()
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(self._col(fill))
        pl = self.t.get("poly_line")                             # 主题指定的多边形线条，如刊物·图纸的细墨线
        sh.line.color.rgb = rgb(self._col(pl[0] if pl else (line or "line")))
        sh.line.width = Pt(pl[1] if pl else lw)
        sh.shadow.inherit = False
        if self.t.get("shadow") and not pl:
            _soft_shadow(sh, 8, 3, 0.18)
        self._skin(sh)
        if self.t.get("glass"):
            _lit(sh, self.t["glass"])
        self.uname(s, sh, name)
        if anim:
            self.A(s, sh.name, *anim)
        return sh

    def pyramid(self, s, rect, levels, colors=None, size=22, desc_size=18, gap=6.0, name="金字塔", side=True):
        """金字塔：levels 从上到下 [(标题, 说明)]；说明放在右侧，用细线引出。动效：自下而上依次出现（下面是基础）。"""
        x, y, w, h = rect
        n = len(levels)
        pw = w * (0.56 if side else 1.0)
        cx = x + pw / 2
        lh = (h - (n - 1) * gap) / n
        cols = colors or ["coral", "sand", "teal", "navy", "green"]
        top = 0.30                                            # 顶层平顶宽度占底宽的比例，让顶层放得下字
        hw = lambda yy: (pw / 2) * (top + (1 - top) * ((yy - y) / h))
        for i in range(n - 1, -1, -1):                       # 自下而上创建，动效顺序就是自下而上
            tt, dd = levels[i]
            yt, yb = y + i * (lh + gap), y + i * (lh + gap) + lh
            pts = [(cx - hw(yt), yt), (cx + hw(yt), yt), (cx + hw(yb), yb), (cx - hw(yb), yb)]
            col = cols[i % len(cols)]
            first = (i == n - 1)
            self._poly(s, pts, col, name=f"{name}层{i + 1}", anim=("fade", "beat" if first else "after", 0, 0.45))
            self.text(s, (cx - hw(yt) + 4, yt, 2 * hw(yt) - 8, lh), [dict(text=tt, size=size, bold=True, color=self._fg(col), align="center")], anchor="middle", align="center", name=f"{name}字{i + 1}", inset=0, anim=("fade", "with", 0.05, 0.3))
            if side and dd:
                ymid = (yt + yb) / 2
                self.text(s, (x + pw + 40, yt, w - pw - 40, lh), [dict(text=dd, size=desc_size, color=self.t["sub"])], anchor="middle", name=f"{name}说明{i + 1}", inset=0, anim=("fade", "with", 0.1, 0.3))
                x0 = cx + hw(ymid) + 10
                self.hline(s, x0, ymid, x + pw + 30 - x0, color="line", name=f"{name}引线{i + 1}", anim=("wipe", "with", 0.1, 0.3, "left"))
        self.occupy(s, rect, "金字塔")

    def funnel(self, s, rect, stages, colors=None, size=22, desc_size=18, gap=6.0, narrow=0.42, name="漏斗"):
        """漏斗：stages 从上到下 [(标题, 说明)]；越往下越窄，说明在右侧。动效：自上而下依次出现。"""
        x, y, w, h = rect
        n = len(stages)
        fw = w * 0.56
        cx = x + fw / 2
        lh = (h - (n - 1) * gap) / n
        cols = colors or ["teal", "sky", "mint", "butter", "peach"]
        wid = lambda yy: fw * (1 - (1 - narrow) * ((yy - y) / h))
        for i, (tt, dd) in enumerate(stages):
            yt, yb = y + i * (lh + gap), y + i * (lh + gap) + lh
            pts = [(cx - wid(yt) / 2, yt), (cx + wid(yt) / 2, yt), (cx + wid(yb) / 2, yb), (cx - wid(yb) / 2, yb)]
            col = cols[i % len(cols)]
            self._poly(s, pts, col, name=f"{name}层{i + 1}", anim=("fade", "beat" if i == 0 else "after", 0, 0.45))
            self.text(s, (cx - wid(yb) / 2 + 8, yt, wid(yb) - 16, lh), [dict(text=tt, size=size, bold=True, color=self._fg(col), align="center")], anchor="middle", align="center", name=f"{name}字{i + 1}", inset=0, anim=("fade", "with", 0.05, 0.3))
            if dd:
                ymid = (yt + yb) / 2
                self.text(s, (x + fw + 40, yt, w - fw - 40, lh), [dict(text=dd, size=desc_size, color=self.t["sub"])], anchor="middle", name=f"{name}说明{i + 1}", inset=0, anim=("fade", "with", 0.1, 0.3))
                x0 = cx + wid(ymid) / 2 + 10
                self.hline(s, x0, ymid, x + fw + 30 - x0, color="line", name=f"{name}引线{i + 1}", anim=("wipe", "with", 0.1, 0.3, "left"))
        self.occupy(s, rect, "漏斗")

    def cycle_ring(self, s, center, rx, ry, items, node=(230, 92), centre_text=None, colors=None, title_size=24, body_size=18, name="循环图", card_fn=None):
        """环形循环图：节点卡片沿椭圆排布，顺时针，节点之间有指向下一个的箭头。items = [(标题, 说明)]。动效：节点和箭头沿循环方向依次出现。"""
        import math
        cx, cy = center
        n = len(items)
        nw, nh = node
        ring = s.shapes.add_shape(MSO_SHAPE.OVAL, *self._rect((cx - rx, cy - ry, 2 * rx, 2 * ry)))
        ring.fill.background()
        ring.line.color.rgb = rgb(self.t["line"])
        ring.line.width = Pt(3.0)
        ring.shadow.inherit = False
        self.uname(s, ring, name + "环")
        self.A(s, ring.name, "wipe", "beat", 0, 0.8, "left")
        cols = colors or ["coral", "teal", "sand", "green", "navy"]
        for i, (tt, dd) in enumerate(items):
            a = -math.pi / 2 + 2 * math.pi * i / n
            px, py = cx + rx * math.cos(a), cy + ry * math.sin(a)
            (card_fn or self.card)(s, (px - nw / 2, py - nh / 2, nw, nh), f"{i + 1}  {tt}", dd, accent=cols[i % len(cols)], title_size=title_size, body_size=body_size, name=f"{name}节点", anchor="middle", anim=("fade", "after", 0.0, 0.4))
            b = a + math.pi / n                       # 两个节点之间的中点
            ax, ay = cx + rx * math.cos(b), cy + ry * math.sin(b)
            tx, ty = -rx * math.sin(b), ry * math.cos(b)
            rot = math.degrees(math.atan2(tx, -ty))
            if self.t.get("skin"):
                th = math.atan2(ty, tx)
                base = [(-28, -9), (3, -9), (3, -22), (31, 0), (3, 22), (3, 9), (-28, 9)]
                apts = [(ax + px * math.cos(th) - py * math.sin(th), ay + px * math.sin(th) + py * math.cos(th)) for px, py in base]
                self._poly(s, apts, cols[i % len(cols)], name=name + "箭头", anim=("zoom", "after", 0.0, 0.25))
            else:
                tri = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, *self._rect((ax - 15, ay - 15, 30, 30)))
                tri.fill.solid()
                tri.fill.fore_color.rgb = rgb(self._col(cols[i % len(cols)]))
                tri.line.fill.background()
                tri.shadow.inherit = False
                tri.rotation = rot
                self.uname(s, tri, name + "箭头")
                self.A(s, tri.name, "zoom", "after", 0.0, 0.25)
        if centre_text:
            self.text(s, (cx - 120, cy - 34, 240, 68), [dict(text=centre_text, size=26, bold=True, color=self.t["ink"], align="center")], anchor="middle", align="center", name=name + "中心", inset=0, anim=("fade", "with", 0.2, 0.4))
        self.occupy(s, (cx - rx - nw / 2, cy - ry - nh / 2, 2 * rx + nw, 2 * ry + nh), "循环图")

    def matrix(self, s, rect, cells, rows=2, cols=2, col_labels=None, row_labels=None, x_axis=None, y_axis=None, colors=None, title_size=24, body_size=18, name="矩阵", card_fn=None):
        """矩阵 / 阵列：rows×cols 个格子，cells 按行排列 [(标题, 说明)]；可带列头、行头和两条坐标轴名（x_axis / y_axis，如 "紧急程度 →"）。"""
        x, y, w, h = rect
        lab_w = (78 if row_labels else 0) + (34 if y_axis else 0)
        lab_h = (34 if col_labels else 0)
        ax_w = 34 if y_axis else 0
        gx, gy = 14.0, 14.0
        cw = (w - lab_w - (cols - 1) * gx) / cols
        ch = (h - lab_h - (rows - 1) * gy) / rows
        cc = colors or ["coral", "teal", "sand", "green", "navy", "pink"]
        if col_labels:
            for j, lb in enumerate(col_labels):
                self.text(s, (x + lab_w + j * (cw + gx), y, cw, lab_h - 4), [dict(text=lb, size=18, bold=True, color=self.t["sub"], align="center")], anchor="middle", align="center", name=f"{name}列头", inset=0, anim=("fade", "after", 0, 0.3))
        if row_labels:
            for i, lb in enumerate(row_labels):
                self.text(s, (x + ax_w, y + lab_h + i * (ch + gy), lab_w - ax_w - 8, ch), [dict(text=lb, size=18, bold=True, color=self.t["sub"], align="center")], anchor="middle", align="center", name=f"{name}行头", inset=0, anim=("fade", "with", 0, 0.3))
        for k, (tt, dd) in enumerate(cells):
            i, j = divmod(k, cols)
            (card_fn or self.card)(s, (x + lab_w + j * (cw + gx), y + lab_h + i * (ch + gy), cw, ch), tt, dd, accent=cc[k % len(cc)], title_size=title_size, body_size=body_size, name=f"{name}格", anchor="middle", anim=("fade", "beat" if k == 0 else "with", 0.12 * k, 0.4))
        if x_axis:
            self.text(s, (x + lab_w, y + h + 6, w - lab_w, 30), [dict(text=x_axis, size=18, bold=True, color=self.t["coral"], align="center")], anchor="middle", align="center", name=name + "横轴", inset=0, anim=("fade", "with", 0.3, 0.3))
        if y_axis:
            sh = self.text(s, (x + 14 - h / 2, y + h / 2 - 15, h, 30), [dict(text=y_axis, size=18, bold=True, color=self.t["coral"], align="center")], anchor="middle", align="center", name=name + "纵轴", inset=0, anim=("fade", "with", 0.3, 0.3), occupy=False)
            sh.rotation = -90
        self.occupy(s, rect, "矩阵")

    def array_grid(self, s, rect, items, cols=4, colors=None, size=20, numbered=True, name="阵列", card_fn=None):
        """阵列：一组并列的小格子（周历、清单、选题池）。items = [标题] 或 [(标题, 说明)]；格子标题前带序号。"""
        x, y, w, h = rect
        n = len(items)
        rows = (n + cols - 1) // cols
        gx = gy = 12.0
        cw = (w - (cols - 1) * gx) / cols
        ch = (h - (rows - 1) * gy) / rows
        cc = colors or ["card"]
        for k, it in enumerate(items):
            tt, dd = (it, None) if isinstance(it, str) else it
            i, j = divmod(k, cols)
            (card_fn or self.card)(s, (x + j * (cw + gx), y + i * (ch + gy), cw, ch), (f"{k + 1}  " if numbered else "") + tt, dd, accent="coral", fill=cc[k % len(cc)], title_size=size, body_size=max(18, size - 2), name=f"{name}格", anchor="middle", anim=("fade", "beat" if k == 0 else "with", 0.06 * k, 0.35))
        self.occupy(s, rect, "阵列")

    def venn(self, s, center, r, labels, mid=None, colors=None, size=22, name="韦恩图"):
        """韦恩图：2 或 3 个半透明圆相交，labels 是各圆的名字，mid 是交集处的文字。动效：圆依次出现，最后出交集。"""
        import math
        cx, cy = center
        n = len(labels)
        cc = colors or ["coral", "teal", "sand"]
        d = r * (0.56 if n == 2 else 0.62)
        offs = [(-d, 0), (d, 0)] if n == 2 else [(0, -d * 0.62), (-d * 0.72, d * 0.5), (d * 0.72, d * 0.5)]
        for i, (lb, (ox, oy)) in enumerate(zip(labels, offs)):
            if self.t.get("skin") == "flat":
                if i == 0:                                            # 扁平：所有圆画成一张图，重叠处是计算出的亮色
                    import diagram_skins as DS
                    circles = [(cx + a_, cy + b_, r) for a_, b_ in offs]
                    png, (bx, by, bw, bh) = DS.render_circles(circles, [self._col(cc[k % len(cc)]) for k in range(n)])
                    m_ = DS.MARGIN
                    pic = s.shapes.add_picture(str(png), *self._rect((bx - m_, by - m_, bw + 2 * m_, bh + 2 * m_)))
                    pic._element.xpath(".//p:cNvPr")[0].set("descr", f"{name}（{n} 个圆相交，重叠处提亮）")
                    self.uname(s, pic, f"{name}圆组")
                    self.A(s, pic.name, "zoom", "beat", 0, 0.5)
            elif self.t.get("skin"):
                pts = [(cx + ox + r * math.cos(2 * math.pi * q / 72), cy + oy + r * math.sin(2 * math.pi * q / 72)) for q in range(72)]
                self._poly(s, pts, cc[i % len(cc)], name=f"{name}圆", alpha=0.80, anim=("zoom", "beat" if i == 0 else "with", 0.2 * i, 0.5))
            else:
                o = s.shapes.add_shape(MSO_SHAPE.OVAL, *self._rect((cx + ox - r, cy + oy - r, 2 * r, 2 * r)))
                o.fill.solid()
                o.fill.fore_color.rgb = rgb(self._col(cc[i % len(cc)]))
                _alpha_fill(o, 0.48)
                o.line.color.rgb = rgb(self._col(cc[i % len(cc)]))
                o.line.width = Pt(1.5)
                o.shadow.inherit = False
                self._skin(o)                                          # 主题的墨线描边、硬投影
                self.uname(s, o, f"{name}圆")
                self.A(s, o.name, "zoom", "beat" if i == 0 else "with", 0.2 * i, 0.5)
            ux, uy = (ox, oy) if (ox or oy) else (0, -1)
            norm = math.hypot(ux, uy) or 1
            tx, ty = cx + ox + ux / norm * r * (0.62 if n == 2 else 0.58), cy + oy + uy / norm * r * (0.62 if n == 2 else 0.58)
            self.text(s, (tx - 90, ty - 22, 180, 44), [dict(text=lb, size=size, bold=True, color=self.t["ink"], align="center")], anchor="middle", align="center", name=f"{name}字", inset=0, anim=("fade", "with", 0.3 + 0.2 * i, 0.35))
        if mid:
            self.text(s, (cx - 80, cy - 22 + (r * 0.08 if n == 3 else 0), 160, 44), [dict(text=mid, size=size - 4, bold=True, color=self.t["ink"], align="center")], anchor="middle", align="center", name=f"{name}交集", inset=0, anim=("fade", "after", 0.2, 0.4))
        self.occupy(s, (cx - r - d, cy - r - d * 0.7, 2 * (r + d), 2 * (r + d * 0.7)), "韦恩图")

    def _donut_skin(self, s, rect, parts, centre, colors, size, name):
        """有材质的环形图：每一段是一个材质容器（环扇形），中心字和图例是真文字。数据在 parts 里，改数据请改脚本。"""
        import math
        x, y, w, h = rect
        d = min(h, w * 0.5)
        cx, cy = x + d / 2, y + h / 2
        R, r = d / 2 - 2, d / 2 * 0.60
        total = float(sum(p[1] for p in parts))
        cc = colors or ["coral", "teal", "sand", "green", "navy"]
        a0 = -90.0
        gap = 1.6
        for i, (nm, v) in enumerate(parts):
            span = 360.0 * v / total
            s0, s1 = a0 + gap / 2, a0 + span - gap / 2
            n_ = max(6, int((s1 - s0) / 3))
            outer = [(cx + R * math.cos(math.radians(s0 + (s1 - s0) * k / n_)), cy + R * math.sin(math.radians(s0 + (s1 - s0) * k / n_))) for k in range(n_ + 1)]
            inner = [(cx + r * math.cos(math.radians(s1 - (s1 - s0) * k / n_)), cy + r * math.sin(math.radians(s1 - (s1 - s0) * k / n_))) for k in range(n_ + 1)]
            self._poly(s, outer + inner, cc[i % len(cc)], name=f"{name}段", anim=("wipe", "beat" if i == 0 else "after", 0, 0.4, "left"))
            a0 += span
        if centre:
            self.text(s, (cx - r * 0.8, cy - 34, r * 1.6, 68), [dict(text=centre, size=34, bold=True, color=self.t["ink"], align="center")], anchor="middle", align="center", name=name + "中心", inset=0, anim=("fade", "with", 0.3, 0.4))
        ly = y + (h - len(parts) * 52) / 2
        for i, (nm, v) in enumerate(parts):
            dot = s.shapes.add_shape(MSO_SHAPE.OVAL, *self._rect((x + d + 36, ly + i * 52 + 12, 18, 18)))
            dot.fill.solid()
            dot.fill.fore_color.rgb = rgb(self._col(cc[i % len(cc)]))
            dot.line.fill.background()
            dot.shadow.inherit = False
            self.uname(s, dot, name + "图例点")
            self.A(s, dot.name, "fade", "with", 0.2 * i, 0.3)
            self.text(s, (x + d + 64, ly + i * 52, w - d - 64, 40), [dict(text=nm, size=size, bold=True, color=self.t["ink"])], anchor="middle", name=name + "图例", inset=0, anim=("fade", "with", 0.2 * i + 0.05, 0.3))
        self.occupy(s, rect, "环形图")

    def donut(self, s, rect, parts, centre=None, colors=None, size=20, name="环形图"):
        """环形图（原生图表，带数据，PowerPoint 里可改）：parts = [(名称, 数值)]，右侧自动写图例。centre 是环中心的大字。"""
        x, y, w, h = rect
        d = min(h, w * 0.5)
        if self.t.get("skin"):
            return self._donut_skin(s, rect, parts, centre, colors, size, name)
        cd = CategoryChartData()
        cd.categories = [p[0] for p in parts]
        cd.add_series("占比", [p[1] for p in parts])
        gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, *self._rect((x, y + (h - d) / 2, d, d)), cd)
        self.uname(s, gf, name)
        self.A(s, gf.name, "wipe", "beat", 0, 0.8, "left")
        ch = gf.chart
        ch.has_legend = False
        ch.has_title = False
        plot = ch.plots[0]
        plot.vary_by_categories = True
        cc = colors or ["coral", "teal", "sand", "green", "navy"]
        for i in range(len(parts)):
            pt = plot.series[0].points[i]
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = rgb(self._col(cc[i % len(cc)]))
            pl = self.t.get("poly_line") or ((self.t["outline"], self.t.get("outline_w", 2.0)) if self.t.get("outline") else None)
            pt.format.line.color.rgb = rgb(self._col(pl[0])) if pl else rgb(self.t["bg"])
            pt.format.line.width = Pt(pl[1]) if pl else Pt(2)
        hs = plot._element.find(qn("c:holeSize"))
        if hs is None:
            hs = parse_xml('<c:holeSize xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" val="62"/>')
            plot._element.append(hs)
        else:
            hs.set("val", "62")
        if centre:
            self.text(s, (x + d * 0.2, y + h / 2 - 34, d * 0.6, 68), [dict(text=centre, size=34, bold=True, color=self.t["ink"], align="center")], anchor="middle", align="center", name=name + "中心", inset=0, anim=("fade", "with", 0.3, 0.4))
        ly = y + (h - len(parts) * 52) / 2
        for i, (nm, v) in enumerate(parts):
            dot = s.shapes.add_shape(MSO_SHAPE.OVAL, *self._rect((x + d + 36, ly + i * 52 + 12, 18, 18)))
            dot.fill.solid()
            dot.fill.fore_color.rgb = rgb(self._col(cc[i % len(cc)]))
            dot.line.fill.background()
            dot.shadow.inherit = False
            self.uname(s, dot, name + "图例点")
            self.A(s, dot.name, "fade", "with", 0.2 * i, 0.3)
            self.text(s, (x + d + 64, ly + i * 52, w - d - 64, 40), [dict(text=nm, size=size, bold=True, color=self.t["ink"])], anchor="middle", name=name + "图例", inset=0, anim=("fade", "with", 0.2 * i + 0.05, 0.3))
        self.occupy(s, rect, "环形图")

    def save(self, path):
        import json
        self.prs.save(str(path))
        plan = [] if self.mode == "read" else list(self.anim)
        for sl in self.prs.slides:
            plan.append(dict(slide=self._idx(sl), transition=self.trans.get(sl.slide_id, "fade"), dur=1.0 if self.trans.get(sl.slide_id) == "morph" else 0.6)) if self.mode == "talk" else plan.append(dict(slide=self._idx(sl), transition="fade", dur=0.4))
        pathlib.Path(str(path)).with_suffix(".anim.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf8")
        if self.mode == "talk":
            planned = {(a["slide"], a["name"]) for a in self.anim}
            for sl in self.prs.slides:
                idx = self._idx(sl)
                for sh in sl.shapes:
                    if sh.top is not None and (sh.top >= Emu(int(H * 12700)) or sh.top + sh.height <= 0):
                        continue                                       # 页外的真标题等
                    if (idx, sh.name) in planned or sh.name in ("页脚", "页码", "页脚条", "页脚线", "角标左", "角标右", "整页大图") or sh.name.startswith("光池") or sh.name.startswith("高光层") or sh.name.startswith("!!") or sh.name.startswith("口播底") or sh.name.startswith("Subtitle") or sh.name.startswith("Text Placeholder"):
                        continue
                    self.warnings.append(f"第 {idx} 页：「{sh.name}」没有动效，页面一开始就会出现")
        for w_ in self.warnings:
            print("[布局告警]", w_)


def _cell_border(c, color):
    tcPr = c._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for e in tcPr.findall(qn(tag)):
            tcPr.remove(e)
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = parse_xml(f'<{tag} xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" w="9525"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></{tag}>')
        tcPr.insert(0, ln) if False else tcPr.append(ln)
    # 边线需要在 solidFill 之前：把填充挪到最后
    for f in tcPr.findall(qn("a:solidFill")):
        tcPr.remove(f)
        tcPr.append(f)


def _hard_shadow(shape, dist=5.0, color="1E2A44", alpha=0.92):
    """硬投影（不虚化）：墨色，向右下偏移。让容器和纸面拉开对比，也是贴纸的质感。"""
    eff = shape._element.spPr.find(qn("a:effectLst"))
    if eff is None:
        eff = etree.SubElement(shape._element.spPr, qn("a:effectLst"))
    for c in list(eff):
        eff.remove(c)
    o = etree.SubElement(eff, qn("a:outerShdw"))
    o.set("blurRad", "0")
    o.set("dist", str(int(dist * 12700)))
    o.set("dir", "2700000")
    o.set("algn", "tl")
    o.set("rotWithShape", "0")
    c = etree.SubElement(o, qn("a:srgbClr"))
    c.set("val", color.upper())
    etree.SubElement(c, qn("a:alpha")).set("val", str(int(alpha * 100000)))


def _soft_shadow(shape, blur=10.0, dist=4.0, alpha=0.20):
    """纸片投影：原生外阴影，可以在 PowerPoint 里继续调。"""
    eff = shape._element.spPr.find(qn("a:effectLst"))
    if eff is None:
        eff = etree.SubElement(shape._element.spPr, qn("a:effectLst"))
    o = etree.SubElement(eff, qn("a:outerShdw"))
    o.set("blurRad", str(int(blur * 12700)))
    o.set("dist", str(int(dist * 12700)))
    o.set("dir", "2700000")
    o.set("algn", "tl")
    o.set("rotWithShape", "0")
    c = etree.SubElement(o, qn("a:srgbClr"))
    c.set("val", "3C2E14")
    etree.SubElement(c, qn("a:alpha")).set("val", str(int(alpha * 100000)))


def _alpha_fill(shape, a):
    sf = shape._element.spPr.find(qn("a:solidFill"))
    clr = sf[0]
    for e in clr.findall(qn("a:alpha")):
        clr.remove(e)
    etree.SubElement(clr, qn("a:alpha")).set("val", str(int(a * 100000)))


def _glow(shape, color, rad=7, a=0.45):
    eff = shape._element.spPr.find(qn("a:effectLst"))
    if eff is None:
        eff = etree.SubElement(shape._element.spPr, qn("a:effectLst"))
    g = etree.SubElement(eff, qn("a:glow"))
    g.set("rad", str(int(rad * 12700)))
    c = etree.SubElement(g, qn("a:srgbClr"))
    c.set("val", color.upper())
    etree.SubElement(c, qn("a:alpha")).set("val", str(int(a * 100000)))


# ---------------------------------------------------------------- 光影（玻璃质感）
_A_NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'


def _clr(hexc, alpha):
    return f'<a:srgbClr val="{hexc}"><a:alpha val="{int(alpha * 1000)}"/></a:srgbClr>'


def _grad(stops, angle, ns=True):
    gs = "".join(f'<a:gs pos="{int(p * 1000)}">{_clr(c, a)}</a:gs>' for p, c, a in stops)
    return f'<a:gradFill{(" " + _A_NS) if ns else ""} rotWithShape="1"><a:gsLst>{gs}</a:gsLst><a:lin ang="{int(angle * 60000)}" scaled="0"/></a:gradFill>'


def _lit(shape, g, alt=False, glow=None):
    """给形状加光影：渐变面（左上受光）、渐变边线（左上亮、右下暗）、带色调的大范围投影、顶部内侧高光。
    g = 主题里的 glass：dict(fill, fill2, rim, rim_w, angle, shadow=(色, 不透明度%, 模糊pt, 偏移pt), inner=(同)).
    纯 OOXML 效果，PowerPoint 里可直接编辑；alt=True 用 fill2（强调的那张卡）。"""
    E = lambda pt: int(pt * 12700)
    sp = shape._element.spPr
    for tag in ("a:solidFill", "a:gradFill", "a:noFill", "a:ln", "a:effectLst"):
        for e in sp.findall(qn(tag)):
            sp.remove(e)
    geom = sp.find(qn("a:prstGeom"))
    if geom is None:
        geom = sp.find(qn("a:custGeom"))
    idx = list(sp).index(geom) + 1
    ang = g.get("angle", 45)
    ln = parse_xml(f'<a:ln {_A_NS} w="{E(g.get("rim_w", 1.25))}">' + _grad(g["rim"], ang, ns=False) + "</a:ln>")
    fx = ""
    gl = glow or g.get("glow")
    if gl:                                   # 彩色光晕：沿形状外沿一圈柔光 (色, 不透明度%, 半径pt)
        fx += f'<a:glow rad="{E(gl[2])}">{_clr(gl[0], gl[1])}</a:glow>'
    if g.get("inner"):
        c, a, b, d = g["inner"]
        fx += f'<a:innerShdw blurRad="{E(b)}" dist="{E(d)}" dir="5400000">{_clr(c, a)}</a:innerShdw>'
    if g.get("shadow"):
        c, a, b, d = g["shadow"]
        fx += f'<a:outerShdw blurRad="{E(b)}" dist="{E(d)}" dir="5400000" algn="t" rotWithShape="0">{_clr(c, a)}</a:outerShdw>'
    els = [parse_xml(_grad(g["fill2"] if (alt and g.get("fill2")) else g["fill"], ang)), ln]
    if fx:
        els.append(parse_xml(f"<a:effectLst {_A_NS}>{fx}</a:effectLst>"))
    for k, e in enumerate(els):
        sp.insert(idx + k, e)


def _lit_pic(pic, g, adj):
    """图片圆角卡的克制光影：渐变细边线（顶边亮、下沿带光色）加一层很轻的投影；圆角与卡片统一。"""
    E = lambda pt: int(pt * 12700)
    sp = pic._element.spPr
    for tag in ("a:ln", "a:effectLst"):
        for e in sp.findall(qn(tag)):
            sp.remove(e)
    geom = sp.find(qn("a:prstGeom"))
    av = geom.find(qn("a:avLst"))
    for e in list(av):
        av.remove(e)
    av.append(parse_xml(f'<a:gd {_A_NS} name="adj" fmla="val {int(adj * 100000)}"/>'))
    idx = list(sp).index(geom) + 1
    ln = parse_xml(f'<a:ln {_A_NS} w="{E(g.get("rim_w", 1.0))}">' + _grad(g["rim"], 90, ns=False) + "</a:ln>")
    sp.insert(idx, ln)
    if g.get("shadow"):
        c, a, b, d = g["shadow"]
        sp.insert(idx + 1, parse_xml(f'<a:effectLst {_A_NS}><a:outerShdw blurRad="{E(b)}" dist="{E(d)}" dir="5400000" algn="t" rotWithShape="0">{_clr(c, a)}</a:outerShdw></a:effectLst>'))
