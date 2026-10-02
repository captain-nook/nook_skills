"""风格包「发布会·暗场」（正式·上台讲）的主题字典。参照：产品发布会的克制语言。
近黑底、大字、一个强调色（蓝）、圆角深灰容器、无描边无投影、3D 质感图片为主角，一页一个视觉重点。
字体：MiSans（常规 + Semibold）；没装时退回微软雅黑。
用法：
    import sys; sys.path.insert(0, "<skill>/assets/styles/keynote-dark")
    from theme import THEME, ST
    deck = Deck(theme=THEME, mode="talk")
    deck.layout_background("内容页", ST / "bg_dark_black.png", "纯黑底")
    deck.layout_background("封面", ST / "bg_cover_cubes.png", "封面：四个发光方块")
    deck.layout_background("章节", ST / "bg_section_q.png", "章节：问号")
底图由 make_bg.py 生成（图片素材在 raw/，出图任务见 jobs_hero.json）。
"""
import os
import pathlib

ST = pathlib.Path(__file__).parent


def _ensure_bg(names):
    """底图由 make_bg.py 用代码生成，发布包里不带；缺了就在第一次使用时生成（需要 numpy、Pillow）。"""
    if not all((ST / n).exists() for n in names):
        import subprocess
        import sys
        subprocess.run([sys.executable, str(ST / "make_bg.py")], check=True, cwd=str(ST))


_ensure_bg(['bg_dark_black.png', 'bg_mesh_cool.png', 'bg_cover_cubes.png', 'bg_cover_curve.png', 'bg_cover_voice.png', 'bg_section_voice.png', 'bg_section_q.png', 'bg_section_saw.png'])
WF = pathlib.Path("C:/Windows/Fonts")


def _find(name, fallback):
    for d in (pathlib.Path(os.environ.get("NOOKPPT_FONT_DIR", "")), pathlib.Path(os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts")), WF, ST.parents[1] / "fonts"):
        if (d / name).exists():
            return str(d / name)
    return str(fallback)


_HAS = (_find("MiSans.ttf", "") != "")
THEME = dict(
    bg="000000", ink="F5F5F7", sub="A1A1A6", line="2C2C2E", card="1C1C1E", card2="2C2C2E",
    coral="5AB0FF", teal="64D2FF", sand="FF9F0A", navy="0A0A0C", white="FFFFFF", em="5AB0FF",
    violet="BF5AF2", green="30D158", red="FF453A",
    sky="1C2B3D", peach="2F2521", mint="1C2F27", butter="2F2C1C", pink="2F2128", lilac="2A2538",
    card_alpha=1.0, glow=None, shadow=False, accent_bar=False, dark_text="1D1D1F",
    outline=None, outline_w=1.0, hard_shadow=0, title_marker=False,
    radius=22.0, panel_radius=28.0, pill_adj=0.5, band_plain=True,
    font="MiSans" if _HAS else "Microsoft YaHei",
    font_file=_find("MiSans.ttf", WF / "msyh.ttc"),
    font_bold="MiSans Semibold" if _HAS else None,
    font_bold_file=_find("MiSans Semibold.ttf", WF / "msyhbd.ttc"),
    font_hand=None, font_hand_file=None,
    tips={},
    skin="glass",                     # 图示容器的材质：磨砂玻璃（见 scripts/diagram_skins.py）
    # 光影（261002 定稿 K1）：色彩分工——卡面中性石墨色，光只在下沿亮边和卡下光池里（冰白），底是纯黑；见 slidekit._lit
    glass=dict(fill=[(0, "2E2E36", 100), (60, "18181D", 100), (100, "101014", 100)], fill2=[(0, "2E3440", 100), (60, "181C24", 100), (100, "10131A", 100)],
               rim=[(0, "FFFFFF", 70), (18, "FFFFFF", 14), (62, "D6ECFF", 16), (100, "D6ECFF", 95)], rim_w=1.5, angle=90,
               shadow=("D6ECFF", 32, 44, 20), inner=("FFFFFF", 26, 8, 2),
               pool=("D6ECFF", 14, 90), sheen=[(0, "FFFFFF", 20), (42, "FFFFFF", 4), (100, "FFFFFF", 0)]),
    num_grad=[(0, "FFFFFF", 100), (100, "CFE6FF", 100)],          # 大数字的渐变光
    # 图片圆角卡（克制）：细渐变边线 + 很轻的投影
    glass_img=dict(rim=[(0, "FFFFFF", 40), (28, "FFFFFF", 8), (100, "D6ECFF", 42)], rim_w=1.0, shadow=("D6ECFF", 10, 36, 14)),
)


# 浅色版：内容页浅灰白底、白色卡片，强调蓝换成更深的 0071E3；封面、章节、整页大图的页仍用深色底（图片本身是黑底 3D 图）
THEME_LIGHT = dict(
    THEME,
    bg="F5F5F7", ink="1D1D1F", sub="636366", line="D2D2D7", card="FFFFFF", card2="E8E8ED",
    coral="0066CC", teal="32ADE6", sand="FF9500", navy="1D1D1F", white="FFFFFF", em="0066CC",
    glass_img=dict(rim=[(0, "FFFFFF", 90), (50, "FFFFFF", 25), (100, "9DB6E8", 70)], rim_w=1.0, shadow=("4F7BE0", 18, 36, 16)),
    violet="AF52DE", green="248A3D", red="D70015",
    sky="DCE8FA", peach="FCE3D0", mint="DDEFD9", butter="FFF1B8", pink="FADBE4", lilac="E6E0F5", num_grad=[(0, "1D1D1F", 100), (100, "3F5A99", 100)],
    # 光影（浅色版，与深色同一思路：光从下方、色彩分工）：卡面中性白，不染色；顶边白高光，下沿一条淡蓝灰亮边；
    # 光只出现在下沿亮边、向下洒的冷灰蓝投影和卡下一片很淡的光池里；底是浅蓝青渐变（无紫）
    glass=dict(fill=[(0, "FFFFFF", 97), (100, "FFFFFF", 84)], fill2=[(0, "F2F7FF", 97), (100, "E8F0FF", 86)],
               rim=[(0, "FFFFFF", 100), (58, "FFFFFF", 45), (100, "9DB6E8", 90)], rim_w=1.25, angle=90,
               shadow=("4F7BE0", 20, 44, 20), inner=("FFFFFF", 95, 10, 3),
               pool=("7FA6FF", 14, 80), sheen=[(0, "FFFFFF", 60), (45, "FFFFFF", 8), (100, "FFFFFF", 0)]),
)


# 深色蓝色版：光换成蓝色，但压弱——下沿亮边更细更淡、光池更小更淡、投影更轻；底仍是纯黑
THEME_BLUE = dict(
    THEME,
    glass=dict(THEME["glass"],
               rim=[(0, "FFFFFF", 70), (18, "FFFFFF", 14), (70, "2F8CFF", 10), (100, "2F8CFF", 72)],
               shadow=("2F8CFF", 24, 36, 16), pool=("2F8CFF", 9, 60)),
    num_grad=[(0, "FFFFFF", 100), (100, "BBD6FF", 100)],
    glass_img=dict(rim=[(0, "FFFFFF", 40), (28, "FFFFFF", 8), (100, "2F8CFF", 55)], rim_w=1.0, shadow=("2F8CFF", 8, 36, 14)),
)


# 深色蓝色版：光换成蓝色，但压弱——下沿亮边更细更淡、光池更小更淡、投影更轻；底仍是纯黑
THEME_BLUE = dict(
    THEME,
    glass=dict(THEME["glass"],
               rim=[(0, "FFFFFF", 70), (18, "FFFFFF", 14), (70, "2F8CFF", 10), (100, "2F8CFF", 72)],
               shadow=("2F8CFF", 24, 36, 16), pool=("2F8CFF", 9, 60)),
    num_grad=[(0, "FFFFFF", 100), (100, "BBD6FF", 100)],
)
