"""零件陈列页：把一个风格里所有图示和常用零件放在几页里，逐个对照风格检查（改引擎或主题后用它回归）。
python gallery_parts.py <风格包目录名> [输出目录]
风格包：captain-class / editorial-blueprint / oriental-yaji / paper-craft / flat-bright / keynote-dark
"""
import importlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SK = HERE.parents[1]                      # 以脚本自身位置定位 skill 根目录（examples/ 的上一级），不依赖任何外部目录结构
STYLE = sys.argv[1]
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "output"
sys.path.insert(0, str(SK / "scripts"))
sys.path.insert(0, str(SK / "assets/styles" / STYLE))
from slidekit import *            # noqa
import theme                      # noqa

BG = dict(
    **{"captain-class": ("paper_bg.png",), "editorial-blueprint": ("paper_bg.png",), "oriental-yaji": ("bg_paper.png",),
       "paper-craft": ("bg_light.png",), "flat-bright": ("bg_light.png",), "keynote-dark": ("bg_dark_black.png",)})[STYLE][0]
deck = Deck(theme=theme.THEME, mode="talk")
ST = theme.ST
deck.layout_background("内容页", ST / BG, "底")
t = deck.t
W_ = W - 2 * MARGIN_X
PAL = ["coral", "teal", "sand", "green"] if "sky" not in t else None
CARD = None
if STYLE == "paper-craft":
    from parts import paper_card
    _n = [0]

    def CARD(s, rect, title, body=None, accent="coral", fill=None, title_size=24, body_size=19, name="卡片", anchor="middle", anim=None, **kw):
        _n[0] += 1
        col = fill if fill not in (None, "card") else {"coral": "peach", "teal": "sky", "sand": "butter", "green": "mint", "navy": "sky", "pink": "pink"}.get(accent, "card")
        return paper_card(deck, s, rect, title, body, None, col, (-1.2, 0.8, -0.6, 1.0)[_n[0] % 4], title_size, body_size, name, anchor, anim=anim)


def page(title):
    return deck.slide(title=title, notes="陈列页")


# 1 流程、提示、清单、标签
s = page("流程 · 提示 · 清单 · 标签")
deck.chevrons(s, (MARGIN_X, 150, W_, 90), ["第一步", "第二步", "第三步", "第四步"], colors=PAL, size=22)
deck.callout(s, (MARGIN_X, 268, W_, 56), "提示条：一句要点放在这里。", size=22)
deck.checkrows(s, (MARGIN_X, 346, 360, 130), ["清单第一项", "清单第二项", "清单第三项"], size=20, row_h=42)
deck.pill(s, (500, 352, 140, 38), "标签", color="coral", size=20)
deck.pill(s, (656, 352, 140, 38), "标签", color="teal", size=20)
deck.badge(s, 520, 412, 44, "1", color="coral")
deck.badge(s, 576, 412, 44, "2", color="teal")

# 2 漏斗、金字塔
s = page("漏斗 · 金字塔")
deck.funnel(s, (MARGIN_X, 146, W_ / 2 - 10, 310), [("第一层", "说明"), ("第二层", "说明"), ("第三层", "说明")], colors=PAL, size=20, desc_size=18)
deck.pyramid(s, (MARGIN_X + W_ / 2 + 10, 146, W_ / 2 - 10, 310), [("顶层", "说明"), ("中层", "说明"), ("底层", "说明")], colors=PAL, size=20, desc_size=18)

# 3 韦恩、循环
s = page("韦恩 · 循环")
deck.venn(s, (MARGIN_X + 150, 300), 92, ["甲", "乙"], mid="交集", colors=PAL[:2] if PAL else None, size=20)
deck.cycle_ring(s, (MARGIN_X + 500, 306), 200, 100, [("节点一", "说明"), ("节点二", "说明"), ("节点三", "说明"), ("节点四", "说明")], node=(170, 74), title_size=20, body_size=18, colors=PAL, card_fn=CARD)

# 4 矩阵、阵列、环形图
s = page("矩阵 · 阵列 · 环形图")
deck.matrix(s, (MARGIN_X, 146, 330, 150), [("甲", None), ("乙", None), ("丙", None), ("丁", None)], colors=PAL, title_size=20, body_size=18, card_fn=CARD)
deck.array_grid(s, (MARGIN_X + 360, 146, 416, 150), [("周一", "说明"), ("周二", "说明"), ("周三", "说明"), ("周四", "说明")], cols=4, size=20, card_fn=CARD)
deck.donut(s, (MARGIN_X, 320, W_, 150), [("一", 30), ("二", 90), ("三", 30)], centre="3", colors=PAL, size=20)

OUT.mkdir(parents=True, exist_ok=True)
out = OUT / f"陈列页_{STYLE}.pptx"
deck.save(out)
print("saved", out)
