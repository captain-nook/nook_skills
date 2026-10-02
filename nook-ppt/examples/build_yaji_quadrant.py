"""「东方雅集」风格样片：四象限时间管理（艾森豪威尔矩阵，公认的方法，不绑定任何课程）。8 页。
python build_yaji_quadrant.py [输出目录] [--dark] [--read]   默认输出到 examples/output/；默认宣纸浅色，--dark 为暗墨青金线版。
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SK = HERE.parents[1]                      # 以脚本自身位置定位 skill 根目录（examples/ 的上一级），不依赖任何外部目录结构
sys.path.insert(0, str(SK / "scripts"))
sys.path.insert(0, str(SK / "assets/styles/oriental-yaji"))
from slidekit import *                      # noqa
from theme import THEME, THEME_DARK, ST     # noqa
from deckkit import Kit, cli               # noqa（公共页面小工具）

O = cli(HERE.parent / "output")
DARK, READ, OUT = "--dark" in sys.argv, O["read"], O["out"]
OUT.mkdir(parents=True, exist_ok=True)
RAW = ST / "raw"
SUF = "d" if DARK else "l"
MX = 80.0
TOTAL = 7

deck = Deck(theme=THEME_DARK if DARK else THEME, mode="read" if READ else "talk")
t = deck.t
deck.layout_background("内容页", ST / ("bg_ink.png" if DARK else "bg_paper.png"), "暗墨青底" if DARK else "宣纸底")
deck.layout_background("封面", ST / f"bg_cover_{SUF}.png", "日晷与远山：时间")
deck.layout_background("章节", ST / f"bg_end_{SUF}.png", "登高望远：先看重要的")
K = Kit(deck, "四象限  ·  时间管理", TOTAL, MX, light=True)
CW_ = K.cw


def seal(s, x, y, ch="雅", size=54, anim=("zoom", "after", 0.2, 0.4)):
    """朱砂印章：圆角方块加一个字，微微倾斜（原生形状，可编辑）。"""
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, *deck._rect((x, y, size, size)))
    sh.adjustments[0] = 0.12
    sh.fill.solid()
    sh.fill.fore_color.rgb = rgb("B23A2F")
    sh.line.fill.background()
    sh.shadow.inherit = False
    sh.rotation = -4
    write_paras(sh.text_frame, [dict(text=ch, size=int(size * 0.56), bold=True, color="F7EFE0", align="center")], inset=0, anchor="middle")
    deck.uname(s, sh, "印章")
    if anim:
        deck.A(s, sh.name, *anim)


# ---------------------------------------------------------------- 1 封面
s = deck.slide("封面", title="四象限时间管理", notes="开场：事情永远做不完，怎么分先后？一张图。")
sp = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
sp.left, sp.top, sp.width, sp.height = (Emu(int(v * 12700)) for v in (MX, -90, 400, 40))
K.headline(s, ["四象限", "时间管理"], (MX, 184, 520, 190), 72, anim=("fade", "after", 0, 0.7))
K.sub(s, (MX, 392, 480, 40), "先分重要，再分紧急。", 24)
seal(s, MX, 446, "时")

# ---------------------------------------------------------------- 2 锚点
s = deck.slide("内容页", title=None, notes="先抛出判断：忙，和重要，是两回事。", transition="morph")
K.corner(s, 2)
K.headline(s, ["忙，", "不等于**重要**。"], (MX, 150, 490, 220), 56)
K.image(s, (590, 110, 290, 330), RAW / f"tile_scrolls_{SUF}.png", "案头堆满的卷轴：忙", morph="主视觉", name="主视觉")

# ---------------------------------------------------------------- 3 四象限
s = deck.slide("内容页", title=None, notes="四个象限：重要且紧急，立刻做；重要不紧急，计划做；紧急不重要，交给别人；都不是，少做或不做。", transition="morph")
K.corner(s, 3)
K.headline(s, ["四个象限，**四种做法**。"], (MX, 70, 760, 60), 40)
# 矩阵：纵向是"重要程度"，横向是"紧急程度"，每个格子是一个意象
LAB = 112                                     # 左侧留给坐标轴名和行头
gap = 14
gw = (CW_ - LAB - gap) / 2
gh = 138.0
gx0, gy0 = MX + LAB, 176.0
for j, lb in enumerate(("紧急", "不紧急")):
    deck.text(s, (gx0 + j * (gw + gap), 142, gw, 30), [dict(text=lb, size=20, bold=True, color=t["sub"], align="center")], name=f"列头{j + 1}", inset=0, align="center", anim=("fade", "after", 0, 0.3))
for i, lb in enumerate(("重要", "不重要")):
    deck.text(s, (MX + 36, gy0 + i * (gh + gap), LAB - 44, gh), [dict(text=lb, size=20, bold=True, color=t["sub"], align="center")], name=f"行头{i + 1}", inset=0, align="center", anchor="middle", anim=("fade", "with", 0, 0.3))
deck.text(s, (gx0, gy0 + 2 * gh + gap + 6, 2 * gw + gap, 28), [dict(text="紧急程度  →", size=18, bold=True, color=t["coral"], align="center")], name="横轴", inset=0, align="center", anim=("fade", "with", 0.3, 0.3))
ya = deck.text(s, (MX + 14 - (2 * gh + gap) / 2, gy0 + gh + gap / 2 - 15, 2 * gh + gap, 30), [dict(text="重要程度  →", size=18, bold=True, color=t["coral"], align="center")], name="纵轴", inset=0, align="center", anim=("fade", "with", 0.3, 0.3), occupy=False)
ya.rotation = -90
# 每张图是内容的意象：烽火（又重要又紧急）、磨刀（磨刀不误砍柴工）、驿使快马（紧急但可托人）、落叶随水（放手）
items = (("一", "重要 · 紧急", "立刻做", "beacon", "烽火台"), ("二", "重要 · 不紧急", "计划做", "whet", "磨刀"),
         ("三", "紧急 · 不重要", "交给别人", "courier", "驿使快马"), ("四", "不紧急 · 不重要", "少做，或不做", "leaf", "落叶随水"))
for i, (key, ti, de, img, alt) in enumerate(items):
    x = gx0 + (i % 2) * (gw + gap)
    y = gy0 + (i // 2) * (gh + gap)
    K.image(s, (x, y, gw, gh), RAW / f"bento_{img}_{SUF}.png", f"{alt}：{ti}，{de}", anim=("fade", "beat", 0, 0.5), name=f"象限{key}")
    deck.text(s, (x + 22, y + 14, 120, 54), [dict(text=key, size=40, bold=True, color=t["coral"])], name=f"序号{key}", inset=0, anim=("fade", "with", 0.1, 0.4))
    deck.text(s, (x + 22, y + 70, 220, 30), [dict(text=ti, size=20, bold=True)], name=f"名称{key}", inset=0, anim=("fade", "with", 0.15, 0.4))
    deck.text(s, (x + 22, y + 100, 220, 28), [dict(text=de, size=18, color=t["sub"])], name=f"说明{key}", inset=0, anim=("fade", "with", 0.2, 0.4))

# ---------------------------------------------------------------- 4 判断：两个问题
s = deck.slide("内容页", title=None, notes="拿到一件事，只问两个问题：重要吗？紧急吗？两个都不是，就少做。", transition="morph")
K.corner(s, 4)
K.headline(s, ["拿到一件事，", "只问**两个问题**。"], (MX, 84, 600, 110), 40)
rows = (("一", "这件事重要吗？", "对目标有没有贡献"), ("二", "这件事紧急吗？", "有没有人在等、有没有截止"), ("三", "两个都不是？", "少做，或者不做"))
y0, rh = 224, 66
for i, (key, q, a_) in enumerate(rows):
    y = y0 + i * rh
    deck.hline(s, MX, y, CW_, color="line", name=f"分隔线{i + 1}", anim=("wipe", "beat", 0, 0.4, "left"))
    deck.text(s, (MX, y + 8, 60, 50), [dict(text=key, size=34, bold=True, color=t["coral"])], name=f"序号{key}", inset=0, anim=("fade", "with", 0.1, 0.35))
    deck.text(s, (MX + 80, y + 14, 380, 40), [dict(text=q, size=26, bold=True)], name=f"问题{i + 1}", inset=0, anim=("fade", "with", 0.15, 0.35))
    deck.text(s, (W - MX - 330, y + 18, 330, 32), [dict(text=a_, size=20, color=t["sub"], align="right")], name=f"答案{i + 1}", inset=0, align="right", anim=("fade", "with", 0.25, 0.35))
deck.hline(s, MX, y0 + 3 * rh, CW_, color="line", name="分隔线4", anim=("wipe", "with", 0.3, 0.4, "left"))

# ---------------------------------------------------------------- 5 图为主
s = deck.slide("内容页", title=None, notes="真正拉开差距的，是重要但不紧急的事：学习、健康、关系、长期计划。", transition="morph")
K.corner(s, 5)
K.image(s, (MX, 96, 400, 380), RAW / f"bento_whet_{SUF}.png", "磨刀石与刀：磨刀不误砍柴工", anim=("fade", "after", 0, 0.7), focus=(0.86, 0.5), name="磨刀图")
K.headline(s, ["时间，留给", "**重要不紧急**。"], (540, 168, 340, 130), 40)
K.sub(s, (540, 322, 340, 100), "磨刀不误砍柴工：学习、健康、长期计划，都在这一格。", 22)

# ---------------------------------------------------------------- 6 对比
s = deck.slide("内容页", title=None, notes="救火式的忙，是被事情推着走；规划式的做，是自己决定先做什么。", transition="morph")
K.corner(s, 6)
K.headline(s, ["换一种**忙法**。"], (MX, 70, 700, 60), 40)
K.compare(s, ("救火", ["天天处理", "紧急的事。"], "忙了一天，目标没动。"), ("规划", ["先做重要的，", "再处理紧急的。"], "每周留出整块时间。"))

# ---------------------------------------------------------------- 8 收尾
s = deck.slide("章节", title="先问重要，再问紧急。", notes="收束：下次手上堆满事情，先停一下，问这两个问题。", transition="morph")
body = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
body._element.getparent().remove(body._element)
K.headline(s, ["先问重要，", "再问**紧急**。"], (MX, 204, 640, 160), 56)
seal(s, MX, 440, "雅")

out = OUT / f"风格样片_东方雅集{'暗墨' if DARK else '宣纸'}_四象限{'_阅读版' if READ else ''}.pptx"
deck.save(out)
print("saved", out)
