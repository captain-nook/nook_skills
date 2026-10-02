"""「刊物·图纸」风格样片：选题方法（内容取自《公众号运营宝典》第 3 章，重点是呈现：对照矩阵、四象来源、循环、阵列、漏斗、金字塔）。9 页，talk 模式。
python build_editorial_topic.py [输出目录]   默认输出到 examples/output/
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SK = HERE.parents[1]                      # 以脚本自身位置定位 skill 根目录（examples/ 的上一级），不依赖任何外部目录结构
sys.path.insert(0, str(SK / "scripts"))
sys.path.insert(0, str(SK / "assets/styles/editorial-blueprint"))
from slidekit import *                    # noqa
from slidekit import _set_font            # noqa
from theme import THEME, ST               # noqa
from deckkit import cli                   # noqa

O = cli(HERE.parent / "output")
OUT = O["out"]
OUT.mkdir(parents=True, exist_ok=True)
ICN = SK / "assets/library/editorial_icons"
CW_ = W - 2 * MARGIN_X
TOTAL = 9

deck = Deck(theme=THEME, mode="talk")
deck.layout_background("内容页", ST / "paper_bg.png", "米白纸底，淡网格线")
for lay in ("封面", "章节"):
    deck.layout_background(lay, ST / "ink_bg.png", "深墨蓝图纸网格底")
T = deck.t
ORANGE = T["coral"]


def rule(s, x, y, w, color=None, h=3, name="分隔线", anim=("wipe", "with", 0.1, 0.4, "left")):
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, *deck._rect((x, y, w, h)))
    r.fill.solid()
    r.fill.fore_color.rgb = rgb(color or ORANGE)
    r.line.fill.background()
    r.shadow.inherit = False
    deck.uname(s, r, name)
    if anim:
        deck.A(s, r.name, *anim)
    return r


def foot(s):
    deck.footer_band(s, "公众号运营宝典  ·  选题篇", len(deck.prs.slides), TOTAL)


def page(title, notes):
    s = deck.slide(title=title, notes=notes, transition="morph" if len(deck.prs.slides) else "fade")
    rule(s, MARGIN_X, 128, 44, ORANGE, 3, "标题短线", ("wipe", "after", 0.2, 0.4, "left"))
    return s


def icon(s, n, x, y, sz, name="插图", i=0):
    pic = deck.picture(s, (x, y, sz, sz), ICN / f"f_{n}.png", f"{name}（线稿插图）", name=name)
    deck.A(s, pic.name, "fade", "with", 0.3 + 0.1 * i, 0.3)


# ---- 1 封面（深墨蓝）
s = deck.slide("封面", title="选题方法", notes="选题不是想题目，是先确认读者的问题。这一篇讲怎么从素材走到一个能写的题。")
sub = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
sub.left, sub.top, sub.width, sub.height = (Emu(int(v * 12700)) for v in (60, -90, 560, 60))
deck.text(s, (MARGIN_X, 94, 520, 34), [dict(text="公众号运营宝典  ·  第 3 篇", size=18, bold=True, color=ORANGE)], name="眉题", inset=0, anim=("fade", "after", 0, 0.4))
deck.text(s, (MARGIN_X, 134, 560, 100), [dict(text="选题方法", size=72, bold=True, color="FFFFFF")], name="主标题", inset=0, anim=("wipe", "after", 0.1, 0.5, "left"))
deck.text(s, (MARGIN_X, 236, 600, 60), [dict(text="先确认读者的问题，再决定写什么", size=32, bold=True, color="FFFFFF")], name="副题", inset=0, anim=("wipe", "with", 0.2, 0.5, "left"))
rule(s, MARGIN_X + 4, 330, 96, ORANGE, 4, "封面短线", ("wipe", "after", 0, 0.4, "left"))
pn = deck.panel(s, (664, 120, 220, 250), fill="sky", name="插图板", anim=("fade", "with", 0.2, 0.4))
pic = deck.picture(s, (688, 150, 172, 172), ICN / "f_checklist.png", "选题卡清单线稿插图", name="插图板图")
deck.A(s, pic.name, "fade", "with", 0.3, 0.3)

# ---- 2 素材主题 ≠ 读者问题
s = page("素材主题，不等于读者问题", "分类法是素材主题；这篇材料放哪才方便下次写稿找到，才是读者问题。每个题写出：谁在做什么时遇到什么困难。")
deck.matrix(s, (MARGIN_X, 150, CW_, 316), [("PARA 分类法", None), ("这篇材料放哪，才方便下次写稿找到", None), ("AI 总爱说“不是……而是……”", None), ("改了提示词稿子仍空泛，下一轮该改哪里", None), ("Agent 做 PPT", None), ("生成后还要改字换图，怎样避免整份重做", None)],
            rows=3, cols=2, col_labels=["素材主题", "读者问题"], colors=["teal", "coral", "teal", "coral", "teal", "coral"], title_size=22, body_size=19)
foot(s)

# ---- 3 四个稳定来源
s = page("选题的四个稳定来源", "自己的生产现场、读者的使用障碍、已有内容的下一步、外部问题与案例。能解释原因与办法的记录，优先进入选题池。")
cells = [("生产现场", "找不到材料、稿子跑偏、返工记录"), ("读者障碍", "评论私信里的“卡在哪一步”"), ("旧内容的下一步", "教程教建库，文章讲怎么用"), ("外部案例", "同行评论区，低粉高互动作品")]
deck.matrix(s, (MARGIN_X, 150, CW_, 306), cells, colors=["coral", "teal", "coral", "teal"], title_size=26, body_size=19)
cwm, chm = (CW_ - 14) / 2, (306 - 14) / 2
for k, ic_ in enumerate(("laptop", "chat", "signpost", "globe")):
    i, j = divmod(k, 2)
    icon(s, ic_, MARGIN_X + j * (cwm + 14) + cwm - 74, 150 + i * (chm + 14) + chm - 74, 58, f"来源插图{k + 1}", k)
foot(s)

# ---- 4 循环：一个项目四个角度
s = page("一个项目，拆出四个角度", "每个项目至少检查四个角度：开始前容易误判什么，过程里哪一步最易失败，为什么选这条流程，完成后怎样复用。不同证据、不同读者动作，才值得分篇。")
deck.cycle_ring(s, (W / 2, 316), 262, 112, [("开始前误判", "新手入口"), ("过程里失败", "分类取舍"), ("为何这条流程", "素材变选题"), ("完成后复用", "来源追溯")], centre_text="一个项目", colors=["coral", "teal", "coral", "teal"])
foot(s)

# ---- 5 选题卡：阵列
s = page("写之前，先填一张选题卡", "选题卡十项：读者、问题、信号、判断、证据、带走的动作、文章任务、分发位置、制作成本、与旧文的差异。直接放进选题笔记。")
deck.array_grid(s, (MARGIN_X, 150, CW_, 306), [("读者", "做什么"), ("问题", "卡住的动作"), ("信号", "记录或反馈"), ("判断", "一句话"), ("证据", "稿件截图"), ("带走的动作", "读者能做的"), ("文章任务", "拉新或信任"), ("分发位置", "哪里承接"), ("制作成本", "缺什么材料"), ("新旧差异", "新增了什么")], cols=5, size=20, numbered=False)
foot(s)

# ---- 6 漏斗：先写哪个题
s = page("先写哪个题？五道筛子", "优先写读者能立即识别、自己已经做过、有现成证据、无需大规模补拍，并且知道发给谁的题。")
deck.funnel(s, (MARGIN_X, 148, CW_, 316), [("全部想法", "四个来源攒下的题"), ("读者能识别", "一看标题就知道是谁的事"), ("自己做过", "有真实经历可讲"), ("有现成证据", "稿件、截图、前后对比"), ("知道发给谁", "有明确的分发位置")], colors=["teal", "sky", "mint", "butter", "peach"], size=22, desc_size=20)
foot(s)

# ---- 7 金字塔：三档分类
s = page("三档分类，每周只从前两档选", "把选题分为可以写、补一项材料即可写、需要独立项目。每周从前两类选，需要全新系统或大量测试的题进项目计划，不挤占本周常规文章。")
deck.pyramid(s, (MARGIN_X, 150, CW_, 306), [("独立项目", "需要全新系统或大量测试，进项目计划"), ("补材料", "先补一个案例或截图，再写"), ("可以写", "材料齐备，每周从这里选")], colors=["coral", "sand", "teal"], size=24, desc_size=20)
foot(s)

# ---- 8 标题写法：对照
s = page("标题：写困境，不写承诺", "标题写读者的困境、工具与结果、或一个具体判断。数字、耗时和效果必须能由案例支撑，不用未经记录的承诺。")
hw = (CW_ - 24) / 2
deck.card(s, (MARGIN_X, 156, hw, 280), "这样写", bullets=["素材存进 Obsidian 后，怎么变成下周的选题", "AI 改稿越改越空？先删这三类段落"], accent="teal", title_size=28, body_size=22, name="好标题", anim=("fade", "beat", 0, 0.45))
deck.card(s, (MARGIN_X + hw + 24, 156, hw, 280), "不要写", bullets=["三天搭完", "一万条不乱", "每天只用一小时"], accent="coral", title_size=28, body_size=22, name="差标题", anim=("fade", "beat", 0, 0.45), fill="peach")
foot(s)

# ---- 9 收尾（深墨蓝）
s = deck.slide("章节", title="写出这一句", notes="每个题都写出一句话：谁在做什么时遇到什么困难，我用什么案例帮助他完成什么动作。写不具体，就先缩小范围。")
body = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
body._element.getparent().remove(body._element)
tt = s.shapes.title
tt.left, tt.top, tt.width, tt.height = (Emu(int(v * 12700)) for v in (MARGIN_X, 120, 700, 70))
tt.text_frame.text = ""
r = tt.text_frame.paragraphs[0].add_run()
r.text = "写出这一句"
_set_font(r, 54, True, "FFFFFF")
r._r.get_or_add_rPr().set("cap", "none")
deck.A(s, tt.name, "wipe", "after", 0, 0.5, "left")
rule(s, MARGIN_X + 4, 214, 96, ORANGE, 4, "封面短线", ("wipe", "after", 0, 0.4, "left"))
for i, ln in enumerate(("谁，在做什么时，", "遇到什么困难；", "我用什么案例，", "帮他完成什么动作。")):
    deck.text(s, (MARGIN_X, 244 + i * 52, 700, 48), [dict(text=ln, size=34, bold=(i % 2 == 1), color="FFFFFF")], name=f"句{i + 1}", inset=0, anim=("fade", "beat" if i == 0 else "with", 0.25 * i, 0.45))
deck.text(s, (MARGIN_X, 466, 600, 34), [dict(text="写不具体，就先缩小范围。", size=20, color="D8DEEA")], name="脚注", inset=0, anim=("fade", "after", 0, 0.4))

out = OUT / "风格样片_刊物图纸_选题方法.pptx"
deck.save(out)
print("saved", out)
