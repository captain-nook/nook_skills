"""「发布会·暗场」风格样片一：费曼学习法（公认的方法，不绑定任何课程）。6 页。
python build_keynote_feynman.py [输出目录] [--light|--blue] [--read]   默认输出到 examples/output/
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SK = HERE.parents[1]                      # 以脚本自身位置定位 skill 根目录（examples/ 的上一级），不依赖任何外部目录结构
sys.path.insert(0, str(SK / "scripts"))
sys.path.insert(0, str(SK / "assets/styles/keynote-dark"))
from slidekit import *                           # noqa
from theme import THEME, THEME_LIGHT, THEME_BLUE, ST   # noqa
from kit import Kit, cli, variant                # noqa

O = cli(HERE.parent / "output")
LIGHT, BLUE, READ, OUT = O["light"], O["blue"], O["read"], O["out"]
OUT.mkdir(parents=True, exist_ok=True)
RAW = ST / "raw"
MX = 80.0
TOTAL = 5

deck = Deck(theme=THEME_LIGHT if LIGHT else (THEME_BLUE if BLUE else THEME), mode="read" if READ else "talk")
t = deck.t
deck.layout_background("内容页", ST / ("bg_mesh_cool.png" if LIGHT else "bg_dark_black.png"), "冷色弥散渐变底" if LIGHT else "纯黑底")
deck.layout_background("封面", ST / "bg_cover_voice.png", "玻璃对话气泡：讲给别人听")
deck.layout_background("章节", ST / "bg_section_voice.png", "对话气泡扩散的声波：讲出来")
K = Kit(deck, "FEYNMAN  ·  费曼学习法", TOTAL, MX, light=LIGHT)
CW_ = K.cw
DK_INK, DK_SUB, DK_EM = "F5F5F7", "A1A1A6", "5AB0FF"          # 深色页（封面、章节）上的字色

# ---------------------------------------------------------------- 1 封面
s = deck.slide("封面", title="费曼学习法", notes="开场：一个问题——你真的学会了吗？接着给出结论：能讲给外行听，才算学会。")
sp = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
sp.left, sp.top, sp.width, sp.height = (Emu(int(v * 12700)) for v in (MX, -90, 400, 40))
K.headline(s, ["费曼学习法"], (MX, 186, 560, 110), 84, color=DK_INK, anim=("fade", "after", 0, 0.7))
K.sub(s, (MX, 312, 480, 70), "用教会别人，检验自己学会了没有。", 24, color=DK_SUB)

# ---------------------------------------------------------------- 2 锚点：一句话 + 一张图
s = deck.slide("内容页", title=None, notes="先抛出判断：看懂、记住，都不等于学会。讲得出来，才是。", transition="morph")
K.corner(s, 2)
K.headline(s, ["学会，", "不等于**讲得出来**。"], (MX, 150, 490, 220), 56)
K.sub(s, (MX, 392, 420, 60), "看懂是输入，讲清楚才是输出。", 22)
K.image(s, (590, 110, 290, 330), RAW / "tile_jar.png", "密封的玻璃罐里困着一团光：知道，但出不来", morph="主视觉", name="主视觉")

# ---------------------------------------------------------------- 3 结构：四步循环
s = deck.slide("内容页", title=None, notes="四个动作：选概念、讲给外行、找卡点、简化类比。讲到哪一步点击一次。", transition="morph")
K.corner(s, 3)
K.headline(s, ["四步，**循环**一次。"], (MX, 84, 560, 64), 44)
K.image(s, (W - MX - 96, 92, 96, 96), RAW / "tile_loop.png", "三个箭头首尾相追的玻璃循环环", morph="主视觉", name="主视觉")
deck.cycle_ring(s, (W / 2, 322), 258, 108, [("选概念", "写下一个概念"), ("讲给外行", "讲给 12 岁孩子听"), ("找卡点", "讲不顺处就是缺口"), ("简化类比", "补上，再打个比方")], node=(236, 90))

# ---------------------------------------------------------------- 4 图为主：卡点
s = deck.slide("内容页", title=None, notes="讲不顺、要用术语糊过去的地方，就是还没懂的地方。回到材料，只补这一处。", transition="morph")
K.corner(s, 4)
K.image(s, (MX, 96, 420, 380), RAW / "tile_puzzle.png", "拼图缺了一块，缺口发光：缺口", anim=("fade", "after", 0, 0.7), focus=(0.5, 0.5), name="卡点图")
K.headline(s, ["讲不顺的地方，", "就是**缺口**。"], (540, 168, 340, 150), 40)
K.sub(s, (540, 336, 340, 100), "回到材料，只补这一处，再讲一遍。", 22)

# ---------------------------------------------------------------- 6 收尾
s = deck.slide("章节", title="讲出来，才算学会。", notes="收束：回到开头的问题。下次学完，先别急着收藏，找个人讲一遍。", transition="morph")
body = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
body._element.getparent().remove(body._element)
K.headline(s, ["讲出来，", "才算**学会**。"], (MX, 204, 600, 160), 60, color=DK_INK, em=DK_EM)
K.sub(s, (MX, 388, 520, 40), "下一次学完，先找个人讲一遍。", 22, color=DK_SUB)

out = OUT / f"风格样片_发布会{variant(O)}_费曼学习法{'_阅读版' if READ else ''}.pptx"
deck.save(out)
print("saved", out)
