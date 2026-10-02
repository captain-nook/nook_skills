"""「船长课堂」风格样片：公众号运营的底层逻辑（内容取自《公众号运营宝典》，重点是呈现：循环、金字塔、矩阵、流程、韦恩、清单）。9 页，talk 模式。
python build_captain_wechat.py [输出目录]   默认输出到 examples/output/
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SK = HERE.parents[1]                      # 以脚本自身位置定位 skill 根目录（examples/ 的上一级），不依赖任何外部目录结构
sys.path.insert(0, str(SK / "scripts"))
sys.path.insert(0, str(SK / "assets/styles/captain-class"))
from slidekit import *                    # noqa
from theme import THEME, ST               # noqa
from deckkit import cli                   # noqa

O = cli(HERE.parent / "output")
OUT = O["out"]
OUT.mkdir(parents=True, exist_ok=True)
TIPS = ST / "tips"
CW_ = W - 2 * MARGIN_X
TOTAL = 9

deck = Deck(theme=THEME, mode="talk")
for lay in ("封面", "内容页", "章节"):
    deck.layout_background(lay, ST / "paper_bg.png", "暖白纸张底，淡蓝方格线")
t = deck.t


def foot(s):
    deck.footer_band(s, "公众号运营  ·  船长课堂", len(deck.prs.slides), TOTAL)


def page(title, notes):
    return deck.slide(title=title, notes=notes, transition="morph" if len(deck.prs.slides) else "fade")


def mascot(s, kind, cx, foot_y, h, name="船长"):
    deck.sticker(s, TIPS / f"tip_{kind}.png", cx, foot_y, h, alt=f"Q 版船长（{kind}）", name=name, anim=("zoom", "after", 0, 0.5))


# ---- 1 封面
s = deck.slide("封面", title="公众号运营", notes="开场：做公众号，不是每天更新，而是让对的人持续看见、持续用上。今天用一张图讲清它怎么转起来。")
sub = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
sub.left, sub.top, sub.width, sub.height = (Emu(int(v * 12700)) for v in (60, -90, 560, 60))
deck.marker(s, (MARGIN_X + 4, 238, 470, 18), color="sand", rot=-0.6, alpha=0.9, anim=("wipe", "after", 0, 0.45, "left"))
deck.text(s, (MARGIN_X, 140, 560, 110), [dict(text="公众号运营", size=76, bold=True)], name="主标题", inset=0, anim=("wipe", "with", 0.1, 0.5, "left"))
deck.card(s, (MARGIN_X + 6, 300, 430, 56), "从定位到变现", accent="coral", title_size=24, fill="teal", fg="FFFFFF", anchor="middle", name="副标题条", rot=-0.8, anim=("fade", "after", 0, 0.4))
deck.tape(s, MARGIN_X + 340, 286, 92, 26, rot=-5)
mascot(s, "wave", 748, 486, 330, "船长·挥手")
deck.plus(s, 600, 96, 18, "coral")
deck.plus(s, 70, 390, 14, "teal")

# ---- 2 帮谁，解决什么
s = page("先说清楚：帮谁，解决什么问题", "定位只有一句话：帮已经开始做内容、却被重复劳动拖慢的创作者。读者要能认出自己的工作。")
cw3 = (CW_ - 32) / 3
specs = [((MARGIN_X + i * (cw3 + 16), 152, cw3, 138), ti, dict(body=bd, fill=cl, rot=r)) for i, (ti, bd, cl, r) in enumerate((
    ("每周不知道写什么", "选题没有固定来源", "peach", -0.8), ("存过的材料找不到", "写稿时想不起放哪", "sky", 0.6), ("AI 初稿反复重写", "改了几轮还是空泛", "mint", -0.5)))]
deck.cards(s, specs, title_size=24, body_size=19, anchor="middle")
deck.tip(s, (MARGIN_X, 388, CW_, 80), "trick", "写不具体，就先缩小范围。", size=26, max_h=130)
foot(s)

# ---- 3 增长循环
s = page("文章怎么越转越准？", "主动分发让对的人看见，持续交付建立信任，反馈又回到下一篇选题。这是一个循环，不是一条直线。")
deck.cycle_ring(s, (W / 2, 312), 262, 112, [("写文章", "解决一个具体问题"), ("主动分发", "放到需求出现处"), ("收反馈", "读者卡在哪一步"), ("定选题", "回到下一篇")], centre_text="增长循环", colors=["coral", "teal", "green", "sand"])
foot(s)

# ---- 4 金字塔
s = page("收入从哪里长出来？", "免费内容给出完整可用的方法，是信任的底座；往上才是小服务和课程。先验证一个范围清楚的小服务，再开课。")
deck.pyramid(s, (MARGIN_X, 150, CW_, 306), [("个性化支持", "适配你的流程、陪你执行"), ("课程", "围绕采集→选题→写作主线"), ("小服务", "梳理流程、一套模板、诊断中断"), ("免费文章与资料", "完整、可用，先建立信任")], colors=["coral", "sand", "green", "teal"], size=22, desc_size=20)
foot(s)

# ---- 5 选题矩阵
s = page("选题从哪里来？四个稳定来源", "四个来源：自己的生产现场、读者的使用障碍、已有内容的下一步、外部问题与案例。写不具体就缩小范围。")
deck.matrix(s, (MARGIN_X, 150, CW_, 306), [("生产现场", "找不到材料、稿子跑偏、返工记录"), ("读者障碍", "评论、私信里的“卡在哪一步”"), ("旧内容的下一步", "教程教建库，文章讲怎么用"), ("外部案例", "同行评论区、低粉高互动作品")], colors=["coral", "teal", "green", "sand"], title_size=26, body_size=20)
foot(s)

# ---- 6 一篇文章的结构
s = page("一篇文章，只解决一个问题", "开头给熟悉的场景，再讲问题出在哪，用真实案例说明判断，最后给可以照做的动作。")
deck.chevrons(s, (MARGIN_X, 168, CW_, 104), ["熟悉场景", "问题在哪", "真实案例", "可做动作"], size=20)
deck.callout(s, (MARGIN_X, 316, CW_, 70), "每讲一个方法，说清为什么这样做，以及什么情况要换做法。", size=24)
mascot(s, "clever", 806, 492, 96, "船长·有窍门")
foot(s)

# ---- 7 分工韦恩
s = page("Agent 与人，各管什么？", "Agent 归纳素材、查案例、提结构、检查重复；人定问题、选论据、补经历、确认判断。重叠的部分，就是必须确认的节点。")
deck.venn(s, (W / 2, 300), 124, ["Agent", "人"], mid="确认节点", colors=["sky", "peach"], size=24)
deck.text(s, (MARGIN_X, 214, 190, 150), [dict(text="归纳素材", size=20), dict(text="查已有案例", size=20), dict(text="提结构候选", size=20), dict(text="检查重复", size=20)], name="Agent职责", inset=0, anim=("fade", "with", 0.4, 0.4))
deck.text(s, (W - MARGIN_X - 190, 214, 190, 150), [dict(text="定问题", size=20, align="right"), dict(text="选论据", size=20, align="right"), dict(text="补真实经历", size=20, align="right"), dict(text="确认判断", size=20, align="right")], name="人职责", inset=0, align="right", anim=("fade", "with", 0.5, 0.4))
foot(s)

# ---- 8 发布前检查
s = page("发布前，检查这五件事", "标题承诺兑现了吗，案例真不真实，工具说明还适用吗，图片链接能打开吗，读者知道下一步做什么吗。结尾只安排一个动作。")
deck.checkrows(s, (MARGIN_X, 160, 470, 280), ["标题承诺兑现了吗", "案例是真实的吗", "工具说明仍然适用吗", "图片、链接能打开吗", "读者知道下一步做什么吗"], size=22, row_h=56)
deck.card(s, (600, 170, 268, 236), "结尾只放一个动作", "尝试方法 / 读延伸文章 / 领资料 / 回答一个问题", accent="coral", title_size=26, body_size=20, fill="butter", anchor="middle", name="结尾动作卡", rot=0.8, anim=("fade", "beat", 0, 0.45))
deck.tape(s, 700, 156, 70, 22, rot=-4)
foot(s)

# ---- 9 收尾
s = page("写第一张选题卡", "把最近一次卡住的地方，写成一张选题卡。先确定读者，再写第一句判断。")
deck.text(s, (MARGIN_X, 170, CW_, 70), [dict(text="把最近一次卡住的地方，写成一张选题卡", size=34, bold=True)], name="观点", inset=0, anchor="middle", anim=("fade", "beat", 0, 0.4))
deck.marker(s, (MARGIN_X + 4, 220, 640, 16), color="sand", rot=-0.5, alpha=0.9, anim=("wipe", "with", 0.1, 0.45, "left"))
deck.tip(s, (MARGIN_X, 340, CW_, 90), "trick", "先确定读者，再写第一句判断。", size=28, max_h=150)
foot(s)

out = OUT / "风格样片_船长课堂_公众号运营.pptx"
deck.save(out)
print("saved", out)
