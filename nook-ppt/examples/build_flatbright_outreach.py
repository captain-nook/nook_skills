"""「明亮扁平」风格样片：获客与承接，把文章放到需求出现的地方（内容取自《公众号运营宝典》第 6、8 章，重点是呈现：流程、漏斗、三圆韦恩、矩阵、阵列、循环）。9 页，talk 模式。
python build_flatbright_outreach.py [输出目录]   默认输出到 examples/output/
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SK = HERE.parents[1]                      # 以脚本自身位置定位 skill 根目录（examples/ 的上一级），不依赖任何外部目录结构
sys.path.insert(0, str(SK / "scripts"))
sys.path.insert(0, str(SK / "assets/styles/flat-bright"))
from slidekit import *                    # noqa
from theme import THEME, ST               # noqa
from deckkit import cli                   # noqa

O = cli(HERE.parent / "output")
OUT = O["out"]
OUT.mkdir(parents=True, exist_ok=True)
CAP = SK / "assets/styles/captain-class"
DECO = ST / "deco"
CW_ = W - 2 * MARGIN_X
TOTAL = 9

deck = Deck(theme=THEME, mode="talk")
deck.layout_background("内容页", ST / "bg_light.png", "米白底加圆点")
for lay in ("封面", "章节"):
    deck.layout_background(lay, ST / "bg_dark.png", "深蓝底加圆点")
t = deck.t


def foot(s):
    deck.footer_band(s, "公众号运营  ·  获客与承接", len(deck.prs.slides), TOTAL)


def page(title, notes):
    return deck.slide(title=title, notes=notes, transition="morph" if len(deck.prs.slides) else "fade")


def icon(s, n, cx, foot_y, h, name="图标", i=0):
    deck.sticker(s, DECO / f"{n}.png", cx, foot_y, h, alt=f"{name}（扁平图标）", name=name, anim=("zoom", "with", 0.3 + 0.1 * i, 0.4))


# ---- 1 封面（深蓝）
s = deck.slide("封面", title="获客与承接", notes="文章写出来，还要放到读者需要它的地方。今天讲怎么承接、怎么触达、怎么让人愿意开口。")
sub = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
sub.left, sub.top, sub.width, sub.height = (Emu(int(v * 12700)) for v in (60, -90, 560, 60))
deck.text(s, (MARGIN_X, 128, 430, 100), [dict(text="获客与承接", size=60, bold=True, color="FFFFFF")], name="主标题", inset=0, anim=("zoom", "after", 0.1, 0.5))
deck.pill(s, (MARGIN_X, 262, 430, 52), "把文章放到需求出现的地方", color="coral", size=22, name="副标题", anim=("fade", "after", 0, 0.4))
deck.sticker(s, CAP / "char_present.png", 770, 490, 400, alt="Q 版船长，伸手介绍", name="船长·介绍", ground_shadow=True)
icon(s, "megaphone", 610, 130, 90, "喇叭", 1)
icon(s, "magnet", 600, 452, 100, "磁铁", 2)

# ---- 2 先从已有资料开始（流程）
s = page("先从已有资料开始", "优先服务已经看过教程、正在领取或使用资料的人。资料首页写“第一次使用从这里开始”，再说明常见卡点和对应的阅读入口。二维码旁写清文章解决什么。")
deck.chevrons(s, (MARGIN_X, 168, CW_, 112), ["第一次从这里开始", "常见卡点", "对应阅读入口"], colors=["coral", "sand", "green"], size=22)
deck.callout(s, (MARGIN_X, 330, CW_ - 120, 74), "二维码旁写清：这篇文章解决什么。", size=24)
icon(s, "gift", 870, 452, 96, "资料礼包", 0)
foot(s)

# ---- 3 触达漏斗
s = page("资料发出去之后", "资料发出之后，看每一步有没有人掉队：有没有打开，有没有用起来，卡在哪里，愿不愿意开口。记录原始人数与问题，不用十几个阅读推导精确转化率。")
deck.funnel(s, (MARGIN_X, 148, CW_, 316), [("发出资料", "交给正在需要的人"), ("被打开", "首页一句话讲清怎么开始"), ("真的用上", "第一次使用有起点"), ("遇到卡点", "没打开、看不懂、配置卡住"), ("愿意开口", "自愿说一个最近的例子")], colors=["coral", "sand", "green", "teal", "navy"], size=22, desc_size=20)
foot(s)

# ---- 4 三圆韦恩：完整回答
s = page("在讨论里，先完整回答", "回答至少包含三样：对问题的判断、一个具体动作、适用条件。文章链接是补充证据，不能代替回答。群规不允许分享时只回答问题，不群发，不私信轰炸。")
deck.venn(s, (W / 2 - 40, 304), 108, ["判断", "具体动作", "适用条件"], mid="当场能用", colors=["coral", "teal", "sand"], size=22)
deck.callout(s, (MARGIN_X + 520, 190, 256, 170), "文章链接是补充证据，不能代替回答。", fill="butter", bar="coral", size=24)
icon(s, "chat", 868, 452, 90, "对话", 0)
foot(s)

# ---- 5 反馈五类（阵列）
s = page("反馈，分成五类", "把反馈按没打开、看不懂、配置卡住、无法接到自己的流程、想要个性化帮助分类。出现同类问题，就写文章或改资料。")
deck.array_grid(s, (MARGIN_X, 150, CW_, 306), [("没打开", "改入口，写清理由"), ("看不懂", "改写资料首页"), ("配置卡住", "补步骤和截图"), ("接不到流程", "写成一篇文章"), ("要个性化", "小范围服务")], cols=3, colors=["peach", "sky", "mint", "butter", "pink"], size=26, numbered=True)
foot(s)

# ---- 6 诊断矩阵
s = page("每周复盘，对症检查", "没有曝光，先检查触达动作；有人打开却不继续阅读，检查标题兑现与开头；有人领资料却不用，检查起点和使用门槛。一次只调一个主要因素。")
deck.matrix(s, (MARGIN_X, 150, CW_, 270), [("没有曝光", None), ("触达动作", None), ("有人打开，不读", None), ("标题兑现与开头", None), ("领了资料，不用", None), ("起点和使用门槛", None)], rows=3, cols=2, col_labels=["看到什么", "先检查什么"], colors=["coral", "teal", "coral", "teal", "coral", "teal"], title_size=26, body_size=20)
icon(s, "magnifier", 868, 134, 74, "放大镜", 0)
foot(s)

# ---- 7 新读者三个入口（阵列 + 角标）
s = page("给新读者留三个入口", "为新读者保留三个入口：账号解决什么问题、从哪里开始、一个有代表性的实际案例。转赛道说明以使用指引为主。")
deck.array_grid(s, (MARGIN_X, 152, CW_, 240), [("解决什么问题", "一句话讲清"), ("从哪里开始", "第一篇读什么"), ("一个实际案例", "看到真实做法")], cols=3, colors=["sky", "mint", "butter"], size=26, numbered=True)
cw3 = (CW_ - 24) / 3
for k, ic_ in enumerate(("phone", "key", "star")):
    deck.corner_icon(s, (MARGIN_X + k * (cw3 + 12), 152, cw3, 240), DECO / f"{ic_}.png", size=64, pos="br", pad=12, name=f"入口图标{k + 1}")
foot(s)

# ---- 8 信任循环
s = page("信任，来自使用的过程", "资料发出后自愿邀请反馈：这份资料你准备先用哪一步？把反馈分类，同类问题就写文章或改资料，持续提供帮助，让信任来自使用过程。")
deck.cycle_ring(s, (W / 2, 314), 262, 112, [("发资料", "自愿邀请反馈"), ("收反馈", "分成五类"), ("改或写", "改资料、写文章"), ("继续帮助", "信任来自使用")], colors=["coral", "teal", "sand", "green"])
icon(s, "heart", 868, 134, 74, "爱心", 0)
foot(s)

# ---- 9 封底（深蓝）
s = deck.slide("章节", title="不群发，不轰炸", notes="收束：先完整回答，再放链接；邀请反馈，不强求。不群发，不私信轰炸。")
body = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
body._element.getparent().remove(body._element)
tt = s.shapes.title
tt.left, tt.top, tt.width, tt.height = (Emu(int(v * 12700)) for v in (MARGIN_X, 170, 700, 90))
for p_ in tt.text_frame.paragraphs:
    for r_ in p_.runs:
        r_.font.color.rgb = rgb("FFFFFF")
        r_.font.size = Pt(60)
deck.A(s, tt.name, "zoom", "after", 0, 0.5)
deck.text(s, (MARGIN_X, 290, 520, 50), [dict(text="先完整回答，再放链接。", size=30, color="FFD3C5")], name="副句", inset=0, anim=("fade", "after", 0, 0.4))
deck.sticker(s, CAP / "tips/tip_thumbsup.png", 790, 500, 340, alt="Q 版船长，点赞", name="船长·点赞", ground_shadow=False)
icon(s, "heart", 600, 210, 90, "爱心", 1)

out = OUT / "风格样片_明亮扁平_获客与承接.pptx"
deck.save(out)
print("saved", out)
