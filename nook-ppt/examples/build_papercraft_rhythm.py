"""「纸片手作」风格样片：发布节奏，一篇保底一篇补充（内容取自《公众号运营宝典》第 5 章，重点是呈现：周历阵列、韦恩、环形图、金字塔、矩阵排期、循环）。9 页，talk 模式。
python build_papercraft_rhythm.py [输出目录]   默认输出到 examples/output/
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SK = HERE.parents[1]                      # 以脚本自身位置定位 skill 根目录（examples/ 的上一级），不依赖任何外部目录结构
sys.path.insert(0, str(SK / "scripts"))
sys.path.insert(0, str(SK / "assets/styles/paper-craft"))
from slidekit import *                    # noqa
from theme import THEME, ST               # noqa
from parts import paper_card              # noqa
from deckkit import cli                   # noqa

O = cli(HERE.parent / "output")
OUT = O["out"]
OUT.mkdir(parents=True, exist_ok=True)
CAP = SK / "assets/styles/captain-class"
CW_ = W - 2 * MARGIN_X
TOTAL = 9

deck = Deck(theme=THEME, mode="talk")
deck.layout_background("内容页", ST / "bg_light.png", "牛皮纸桌面")
for lay in ("封面", "章节"):
    deck.layout_background(lay, ST / "bg_dark.png", "夜间台灯下的桌面")
t = deck.t
_N = [0]
ROT = (-1.2, 0.8, -0.6, 1.0, -0.9, 0.6)
PCOL = dict(coral="peach", teal="sky", sand="butter", green="mint", navy="sky", pink="pink")


def pcard(s, rect, title, body=None, accent="coral", fill=None, title_size=24, body_size=19, name="卡片", anchor="middle", anim=None, **kw):
    """纸片卡适配器：让 matrix / array_grid / cycle_ring 用撕边纸片当格子。"""
    _N[0] += 1
    col = fill if fill not in (None, "card") else PCOL.get(accent, "card")
    return paper_card(deck, s, rect, title, body, None, col, ROT[_N[0] % len(ROT)], title_size, body_size, name, anchor, anim=anim)


def icon(s, n, cx, foot_y, h, name="图标", i=0):
    deck.sticker(s, ST / "deco" / f"{n}.png", cx, foot_y, h, alt=f"{name}（纸片图标）", name=name, anim=("zoom", "with", 0.3 + 0.1 * i, 0.4))


def foot(s):
    deck.footer_band(s, "公众号运营  ·  发布节奏", len(deck.prs.slides), TOTAL)


def page(title, notes):
    return deck.slide(title=title, notes=notes, transition="morph" if len(deck.prs.slides) else "fade")


# ---- 1 封面（夜间桌面）
s = deck.slide("封面", title="发布节奏", notes="更新的关键不是多，而是稳。一篇保底，一篇补充，留出做视频的完整时段。")
sub = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
sub.left, sub.top, sub.width, sub.height = (Emu(int(v * 12700)) for v in (60, -90, 560, 60))
paper_card(deck, s, (MARGIN_X, 112, 520, 150), "发布节奏", None, None, "card", -1.5, 64, 21, "标题纸", "middle")
paper_card(deck, s, (MARGIN_X + 20, 296, 470, 66), "一篇保底，一篇补充", None, None, "mint", 1.2, 26, 21, "副标题纸", "middle", tape="sand")
deck.sticker(s, CAP / "tips/tip_cheer.png", 790, 500, 340, alt="Q 版船长，欢呼", name="船长·欢呼", ground_shadow=False)
icon(s, "calendar", 660, 170, 110, "日历", 1)
icon(s, "stopwatch", 640, 470, 110, "秒表", 2)

# ---- 2 一周日历（阵列）
s = page("一周怎么排？", "周一确定两张选题卡，周二整理案例并完成保底稿，周三发布主文章并分发，周四收反馈，周五写补充稿，周六有成熟稿就发，周日用二十分钟复盘。周三、周六只是便于执行的固定安排，不是平台流量规律。")
deck.array_grid(s, (MARGIN_X, 152, CW_, 300), [("周一", "定两张选题卡"), ("周二", "整理案例，写保底稿"), ("周三", "发布主文章，分发"), ("周四", "收集反馈"), ("周五", "完成补充稿"), ("周六", "有成熟稿就发"), ("周日", "复盘 20 分钟")], cols=4, colors=["peach", "sky", "mint", "butter"], size=24, numbered=False, card_fn=pcard)
icon(s, "calendar", 868, 134, 74, "日历", 0)
foot(s)

# ---- 3 两篇怎么搭配（韦恩）
s = page("两篇文章，怎么搭配？", "主文章解决一个容易被识别的具体问题，兼顾陌生读者的进入门槛；补充文章深入一个真实案例，或回答主文章引出的障碍。两篇围绕同一条主线。")
deck.venn(s, (W / 2, 306), 120, ["主文章", "补充文章"], mid="同一主线", colors=["peach", "sky"], size=24)
deck.text(s, (MARGIN_X - 4, 220, 210, 150), [dict(text="解决容易识别的问题", size=20), dict(text="照顾陌生读者", size=20)], name="主文章说明", inset=0, anim=("fade", "with", 0.4, 0.4))
deck.text(s, (W - MARGIN_X - 206, 220, 210, 150), [dict(text="深入一个真实案例", size=20, align="right"), dict(text="回答引出的障碍", size=20, align="right")], name="补充说明", inset=0, align="right", anim=("fade", "with", 0.5, 0.4))
foot(s)

# ---- 4 三小时（环形图）
s = page("一篇，三个小时", "已有素材的常规文章，三小时起步：三十分钟定问题与证据，九十分钟写作修改，三十分钟发布检查，三十分钟分发与记录。三小时是时间管理建议，超出时先查是不是混进了多个问题。")
deck.donut(s, (MARGIN_X, 150, CW_, 300), [("定问题与证据  30 分", 30), ("写作修改  90 分", 90), ("发布检查  30 分", 30), ("分发与记录  30 分", 30)], centre="3 小时", colors=["coral", "teal", "sand", "green"], size=22)
icon(s, "stopwatch", 868, 134, 74, "秒表", 0)
foot(s)

# ---- 5 忙碌周（金字塔：保护顺序）
s = page("忙碌周，先砍什么？", "做重型视频的时候，保留一篇从已有材料提炼的保底文章，取消补充篇，减少新增测试和装饰性配图。不用临时拼凑的文章补更新数量。")
deck.pyramid(s, (MARGIN_X, 150, CW_, 300), [("新增测试", "先砍：装饰性配图也一起省"), ("补充篇", "忙碌周取消"), ("保底篇", "保留：从已有材料提炼")], colors=["coral", "sand", "green"], size=24, desc_size=20)
icon(s, "flag", 868, 134, 74, "旗子", 0)
foot(s)

# ---- 6 库存
s = page("常备两篇轻稿", "常备两篇已完成主要材料与结构的轻稿：真实问答、单段改稿、一次具体取舍。保持稳定供给，同时为视频制作留下完整工作时段。")
deck.array_grid(s, (MARGIN_X, 160, CW_, 150), [("真实问答", "材料与结构已备好"), ("单段改稿", "删了什么，为什么"), ("具体取舍", "一个选择和理由")], cols=3, colors=["sky", "mint", "butter"], size=24, numbered=False, card_fn=pcard)
deck.text(s, (MARGIN_X, 340, 560, 60), [dict(text="为视频留出完整的制作时段。", size=28, bold=True)], name="观点", inset=0, anchor="middle", anim=("fade", "beat", 0, 0.4))
deck.marker(s, (MARGIN_X + 4, 380, 480, 14), color="sand", rot=-0.5, alpha=0.9, anim=("wipe", "with", 0.1, 0.45, "left"))
icon(s, "box", 800, 464, 130, "库存箱", 0)
foot(s)

# ---- 7 四周排期（矩阵）
s = page("首月四周，这样排", "第一周建好库后从哪里开始，加素材怎么变成选题；第二周真实稿件做减法，加找回论据；第三周教程转文章，加一期视频拆三篇；第四周封面图字分工，加保留确认节点。补充篇服从当周精力与证据准备。")
deck.matrix(s, (MARGIN_X, 150, CW_, 306), [("建好库后从哪里开始", None), ("素材怎么变成选题", None), ("真实稿件做减法", None), ("写稿时找回论据", None), ("教程转文章", None), ("一期视频拆三篇", None), ("封面图字分工", None), ("保留确认节点", None)],
            rows=4, cols=2, col_labels=["保底篇", "补充篇"], row_labels=["第一周", "第二周", "第三周", "第四周"], colors=["coral", "teal"], title_size=22, body_size=19, card_fn=pcard)
foot(s)

# ---- 8 周复盘循环
s = page("每周复盘，转一圈", "周末看三个问题：哪篇吸引了目标读者，哪个入口带来可确认的反馈，哪个障碍值得再写一篇。一次只调一个主要因素，连续观察同类题。")
deck.cycle_ring(s, (W / 2, 314), 262, 112, [("记录数据", "标题、耗时、阅读"), ("看三个问题", "谁来、哪个入口"), ("只调一个因素", "触达、开头或起点"), ("连续观察", "同类题多看几篇")], colors=["coral", "teal", "sand", "green"], node=(236, 96), card_fn=pcard)
icon(s, "magnifier", 868, 134, 74, "放大镜", 0)
foot(s)

# ---- 9 封底（夜间桌面）
s = deck.slide("章节", title="稳定供给", notes="收束：稳定比频繁重要。一篇保底，一篇补充，给视频留出完整时段。")
body = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
body._element.getparent().remove(body._element)
paper_card(deck, s, (MARGIN_X - 10, 100, 560, 250), None, None, None, "butter", -1.2, 28, 21, "封底纸", "middle")
deck.text(s, (MARGIN_X + 20, 124, 500, 100), [dict(text="稳定供给，", size=52, bold=True)], name="封底大字一", inset=0, anim=("zoom", "after", 0, 0.5))
deck.text(s, (MARGIN_X + 20, 214, 500, 90), [dict(text="留出完整制作时段", size=34, bold=True, color=t["coral"])], name="封底大字二", inset=0, anim=("fade", "with", 0.2, 0.4))
tt = s.shapes.title
s.shapes._spTree.remove(tt._element)
s.shapes._spTree.append(tt._element)                 # 标题占位符放到最上层
tt.left, tt.top, tt.width, tt.height = (Emu(int(v * 12700)) for v in (MARGIN_X + 20, H + 10, 400, 70))      # 真标题放在页外，页面上的大字已经写了同样的话
for p_ in tt.text_frame.paragraphs:
    for r_ in p_.runs:
        r_.font.color.rgb = rgb("F3E7D3")                 # 夜间桌面上用浅色字
deck.sticker(s, CAP / "tips/tip_thumbsup.png", 790, 500, 330, alt="Q 版船长，点赞", name="船长·点赞", ground_shadow=False)
icon(s, "stopwatch", 640, 440, 96, "秒表", 1)

out = OUT / "风格样片_纸片手作_发布节奏.pptx"
deck.save(out)
print("saved", out)
