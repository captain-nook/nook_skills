"""「发布会·暗场」风格样片二：用 PARA 文件分类法做内容（公认的方法，不绑定任何课程）。talk 模式，8 页。
python build_keynote_para.py [输出目录] [--light|--blue] [--read]   默认输出到 examples/output/
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
deck.layout_background("封面", ST / "bg_cover_cubes.png", "封面：四个发光方块")
deck.layout_background("章节", ST / "bg_section_q.png", "玻璃问号：它现在有什么用")
K = Kit(deck, "PARA  ·  文件分类法", TOTAL, MX, light=LIGHT)
CW_ = K.cw
COL_DK = dict(P="FF9F0A", A="5AB0FF", R="30D158", X="D6ECFF")       # 压在深色图上的字母颜色
COL = dict(P="9A4300", A="005BB8", R="17702F", X="4A5560") if LIGHT else COL_DK
DK_INK, DK_SUB, DK_EM = "F5F5F7", "A1A1A6", "5AB0FF"                 # 深色页（封面、章节、整页大图）上的字色

# ---------------------------------------------------------------- 1 封面
s = deck.slide("封面", title="PARA 文件分类法", notes="开场：你的文件夹是不是越建越多？PARA 只用四个抽屉。")
sp = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
sp.left, sp.top, sp.width, sp.height = (Emu(int(v * 12700)) for v in (MX, -90, 400, 40))
K.headline(s, ["PARA", "文件分类法"], (MX, 184, 520, 190), 72, color=DK_INK, anim=("fade", "after", 0, 0.7))
K.sub(s, (MX, 392, 480, 40), "按“能不能行动”来分，不按主题。", 24, color=DK_SUB)

# ---------------------------------------------------------------- 2 整页大图 + 一句话
s = deck.slide("内容页", title=None, notes="先说痛点：文件越存越多，找的时候却想不起来放哪了。", transition="morph")
K.image(s, (0, 0, W, H), RAW / "hero_pile.png", "乱堆溢出的玻璃文件：存得越多，找得越乱", treat=None, z="back", anim=None, name="整页大图")
K.corner(s, 2, on_dark=True)
K.headline(s, ["存得越多，", "**找得越慢**。"], (MX, 62, 600, 140), 56, color=DK_INK, em=DK_EM)

# ---------------------------------------------------------------- 3 结构：四个抽屉（图片网格）
s = deck.slide("内容页", title=None, notes="四个抽屉：项目、领域、资源、归档。每讲一个点击一次。", transition="morph")
K.corner(s, 3)
K.headline(s, ["四个**抽屉**。"], (MX, 70, 700, 60), 40)
gap = 16
gw = (CW_ - gap) / 2
gh = 158.0
items = (("P", "Projects  项目", "有目标、有截止日期", "bento_p"), ("A", "Areas  领域", "长期要维护的责任", "bento_a"),
         ("R", "Resources  资源", "将来可能有用的主题", "bento_r"), ("X", "Archive  归档", "已完成、不再活跃", "bento_x"))
for i, (key, ti, de, img) in enumerate(items):
    x = MX + (i % 2) * (gw + gap)
    y = 142 + (i // 2) * (gh + gap)
    K.image(s, (x, y, gw, gh), RAW / f"{img}.png", ti, anim=("fade", "beat", 0, 0.5), name=f"抽屉{key}")
    deck.text(s, (x + 26, y + 20, 200, 60), [dict(text=key, size=48, bold=True, color=COL_DK[key])], name=f"字母{key}", inset=0, anim=("fade", "with", 0.1, 0.4))
    deck.text(s, (x + 26, y + 84, 250, 32), [dict(text=ti, size=22, bold=True, color=DK_INK)], name=f"名称{key}", inset=0, anim=("fade", "with", 0.15, 0.4))
    deck.text(s, (x + 26, y + 116, 250, 30), [dict(text=de, size=18, color=DK_SUB)], name=f"说明{key}", inset=0, anim=("fade", "with", 0.2, 0.4))

# ---------------------------------------------------------------- 4 判断规则：四个问题
s = deck.slide("内容页", title=None, notes="四个问题，按顺序问：有截止日期吗？是长期责任吗？将来会用吗？都不是就归档。", transition="morph")
K.corner(s, 4)
K.headline(s, ["拿到一份资料，", "只问**四个问题**。"], (MX, 84, 600, 110), 40)
rows = (("P", "它有截止日期吗？", "放进 项目"), ("A", "它是长期要维护的吗？", "放进 领域"), ("R", "它将来可能有用吗？", "放进 资源"), ("X", "都不是？", "放进 归档"))
y0, rh = 214, 62
for i, (key, q, a_) in enumerate(rows):
    y = y0 + i * rh
    deck.hline(s, MX, y, CW_, color="line", name=f"分隔线{i + 1}", anim=("wipe", "beat", 0, 0.4, "left"))
    deck.text(s, (MX, y + 8, 60, 48), [dict(text=key, size=36, bold=True, color=COL[key])], name=f"字母{key}", inset=0, anim=("fade", "with", 0.1, 0.35))
    deck.text(s, (MX + 80, y + 14, 420, 36), [dict(text=q, size=26, bold=True)], name=f"问题{i + 1}", inset=0, anim=("fade", "with", 0.15, 0.35))
    deck.text(s, (W - MX - 240, y + 16, 240, 32), [dict(text=a_, size=22, color=COL[key], align="right", bold=True)], name=f"答案{i + 1}", inset=0, align="right", anim=("fade", "with", 0.25, 0.35))
deck.hline(s, MX, y0 + 4 * rh, CW_, color="line", name="分隔线5", anim=("wipe", "with", 0.3, 0.4, "left"))

# ---------------------------------------------------------------- 5 图为主：归档
s = deck.slide("内容页", title=None, notes="归档不是删除。只是让它离开眼前，需要时仍然找得到。", transition="morph")
K.corner(s, 5)
K.image(s, (MX, 96, 400, 380), RAW / "para_x.png", "拉丝钛金属盒，青色细光线", anim=("fade", "after", 0, 0.7), focus=(0.5, 0.5), name="归档图")
K.headline(s, ["归档，", "不是**删除**。"], (540, 168, 340, 130), 44)
K.sub(s, (540, 322, 340, 100), "离开眼前，需要时仍然找得到。", 22)

# ---------------------------------------------------------------- 6 对比
s = deck.slide("内容页", title=None, notes="旧办法按主题分，一份资料能放进好几个文件夹；新办法按行动分，放哪里只有一个答案。", transition="morph")
K.corner(s, 6)
K.headline(s, ["换一个**分法**。"], (MX, 70, 700, 60), 40)
K.compare(s, ("按主题分", ["摄影、写作、", "财务、旅行……"], "一份资料能放进好几个地方。"), ("按行动分", ["项目、领域、", "资源、归档。"], "放哪里，只有一个答案。"))

# ---------------------------------------------------------------- 8 收尾
s = deck.slide("章节", title="先问：它现在有什么用？", notes="收束：下次存东西前，先问一句——它现在有什么用？", transition="morph")
body = [p for p in s.placeholders if p.placeholder_format.idx == 1][0]
body._element.getparent().remove(body._element)
K.headline(s, ["先问：", "它现在有**什么用**？"], (MX, 204, 640, 160), 56, color=DK_INK, em=DK_EM)

out = OUT / f"风格样片_发布会{variant(O)}_PARA{'_阅读版' if READ else ''}.pptx"
deck.save(out)
print("saved", out)
