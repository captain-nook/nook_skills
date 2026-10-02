"""「发布会·暗场」风格样片三：艾宾浩斯遗忘曲线（公认的记忆规律，不绑定任何课程）。talk 模式，7 页，含原生折线图。
python build_keynote_ebbinghaus.py [输出目录] [--light|--blue] [--read]   默认输出到 examples/output/
数据：艾宾浩斯 1885 年记忆实验的常见引用值（节省率 %）：20 分钟 58、1 小时 44、9 小时 36、1 天 34、2 天 28、6 天 25、31 天 21。
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SK = HERE.parents[1]                      # 以脚本自身位置定位 skill 根目录（examples/ 的上一级），不依赖任何外部目录结构
sys.path.insert(0, str(SK / "scripts"))
sys.path.insert(0, str(SK / "assets/styles/keynote-dark"))
from slidekit import *            # noqa
from theme import THEME, THEME_LIGHT, THEME_BLUE, ST       # noqa
from kit import Kit, cli, variant  # noqa

O = cli(HERE.parent / "output")
LIGHT, BLUE, READ, OUT = O["light"], O["blue"], O["read"], O["out"]
OUT.mkdir(parents=True, exist_ok=True)
RAW = ST / "raw"
MX = 80.0
TOTAL = 7

deck = Deck(theme=THEME_LIGHT if LIGHT else (THEME_BLUE if BLUE else THEME), mode="read" if READ else "talk")
t = deck.t
deck.layout_background("内容页", ST / ("bg_mesh_cool.png" if LIGHT else "bg_dark_black.png"), "冷色弥散渐变底" if LIGHT else "纯黑底")
deck.layout_background("封面", ST / "bg_cover_curve.png", "封面：衰减曲线")
deck.layout_background("章节", ST / "bg_section_saw.png", "一次次托起的光带：复习把曲线拉回来")
K = Kit(deck, "遗忘曲线  ·  记忆的规律", TOTAL, MX, light=LIGHT)
DK_INK, DK_SUB, DK_EM = "F5F5F7", "A1A1A6", "5AB0FF"                 # 深色页（封面、章节）上的字色
CW_ = K.cw

# ---------------------------------------------------------------- 1 封面
s = deck.slide("封面", title="艾宾浩斯遗忘曲线", notes="开场：学过的东西，是怎么一点点消失的？")
sp = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
sp.left, sp.top, sp.width, sp.height = (Emu(int(v * 12700)) for v in (MX, -90, 400, 40))
K.headline(s, ["艾宾浩斯", "遗忘曲线"], (MX, 184, 520, 190), 72, color=DK_INK, anim=("fade", "after", 0, 0.7))

# ---------------------------------------------------------------- 2 大数字 + 图
s = deck.slide("内容页", title=None, notes="一天之后，保留约三分之一，也就是忘掉了大约三分之二。", transition="morph")
K.corner(s, 2)
K.headline(s, ["学完一天，", "忘掉**大半**。"], (MX, 84, 520, 120), 44)
deck.text(s, (MX, 236, 420, 170), [dict(text="66%", size=150, bold=True, color=t["coral"])], name="大数字", inset=0, anim=("zoom", "beat", 0, 0.6))
deck.text(s, (MX, 410, 420, 36), [dict(text="一天之后，忘掉的比例。", size=22, color=t["sub"])], name="数字说明", inset=0, anim=("fade", "with", 0.2, 0.4))
K.image(s, (600, 110, 280, 340), RAW / "tile_hourglass.png", "发光的蓝色沙漏", anim=("fade", "after", 0, 0.7), name="沙漏")

# ---------------------------------------------------------------- 3 折线图
s = deck.slide("内容页", title=None, notes="曲线先陡后缓：前一天掉得最快，之后越来越慢。所以第一次复习要早。", transition="morph")
K.corner(s, 3)
K.headline(s, ["遗忘，**先快后慢**。"], (MX, 66, 700, 56), 40)
deck.linechart(s, (MX - 10, 140, CW_ + 20, 320), ["20分钟", "1小时", "9小时", "1天", "2天", "6天", "31天"], [58, 44, 36, 34, 28, 25, 21], series_name="记忆保持率", unit="%", vmax=70, label_size=20, tick_size=18, name="遗忘曲线")
deck.text(s, (MX, 474, CW_, 22), [dict(text="数据：艾宾浩斯 1885 年记忆实验的常见引用值（节省率）。", size=14, color=t["sub"])], name="数据来源", inset=0, anim=("fade", "after", 0, 0.4))

# ---------------------------------------------------------------- 4 时间线：五次复习
s = deck.slide("内容页", title=None, notes="复习要踩在遗忘之前：当天、第 1 天、第 3 天、第 7 天、第 30 天。每次间隔拉长。", transition="morph")
K.corner(s, 4)
K.headline(s, ["复习，踩在**遗忘之前**。"], (MX, 66, 760, 56), 40)
pts = (("当天", "趁热回忆"), ("1 天后", "第一次复习"), ("3 天后", "巩固"), ("7 天后", "拉长间隔"), ("30 天后", "进入长期记忆"))
ly = 262
deck.hline(s, MX + 22, ly + 21, CW_ - 44, color="coral", h=3, name="时间轴", anim=("wipe", "beat", 0, 1.6, "left"))
step = (CW_ - 44) / 4
for i, (lab, cap) in enumerate(pts):
    cx = MX + 22 + i * step
    d_ = 44
    deck.badge(s, cx - d_ / 2, ly, d_, str(i + 1), color="coral", name=f"节点{i + 1}", anim=("zoom", "with", 0.32 * i, 0.3))
    deck.text(s, (cx - 80, ly + 70, 160, 40), [dict(text=lab, size=28, bold=True, align="center")], name=f"时间{i + 1}", inset=0, align="center", anim=("fade", "with", 0.32 * i + 0.1, 0.35))
    deck.text(s, (cx - 80, ly + 118, 160, 56), [dict(text=cap, size=20, color=t["sub"], align="center")], name=f"说明{i + 1}", inset=0, align="center", anim=("fade", "with", 0.32 * i + 0.15, 0.35))

# ---------------------------------------------------------------- 5 图为主
s = deck.slide("内容页", title=None, notes="合上书，自己回想一遍。想不起来的地方，就是该复习的地方。", transition="morph")
K.corner(s, 5)
K.image(s, (MX, 96, 400, 380), RAW / "tile_book.png", "合上的玻璃书，书页边缘透光：合上书", anim=("fade", "after", 0, 0.7), name="回忆图")
K.headline(s, ["合上书，", "**回忆**一遍。"], (540, 168, 340, 130), 44)
K.sub(s, (540, 322, 340, 100), "主动回想，比反复重读更牢。", 22)

# ---------------------------------------------------------------- 6 对比
s = deck.slide("内容页", title=None, notes="重读会产生熟悉感，容易误以为记住了；回忆会暴露真正没记住的地方。", transition="morph")
K.corner(s, 6)
K.headline(s, ["别重读，要**回忆**。"], (MX, 70, 700, 60), 40)
K.compare(s, ("重读", ["看着很熟，", "以为记住了。"], "熟悉感，不等于记得。"), ("回忆", ["想不起来的地方，", "就是该补的地方。"], "只补缺的，不重来。"))

# ---------------------------------------------------------------- 7 收尾
s = deck.slide("章节", title="忘记很正常，复习才是办法。", notes="收束：忘是常态，把复习排进日程。", transition="morph")
body = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
body._element.getparent().remove(body._element)
K.headline(s, ["忘记很正常，", "**复习**才是办法。"], (MX, 204, 700, 160), 56, color=DK_INK, em=DK_EM)
K.sub(s, (MX, 388, 520, 40), "把第一次复习，排在明天。", 22, color=DK_SUB)

out = OUT / f"风格样片_发布会{variant(O)}_遗忘曲线{'_阅读版' if READ else ''}.pptx"
deck.save(out)
print("saved", out)
