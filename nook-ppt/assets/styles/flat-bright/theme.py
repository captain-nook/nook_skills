"""风格包「明亮扁平」（可爱）的主题字典。扁平动态图形的语言：大圆角、糖果色块、无描边、柔和彩色投影、圆点与色块装饰，
Q 版船长贯穿。浅色底米白加圆点，深色底深蓝加圆点。字体用微软雅黑（干净圆润）。
用法：
    import sys; sys.path.insert(0, "<skill>/assets/styles/flat-bright")
    from theme import THEME, ST
    deck = Deck(theme=THEME, mode="talk")
    deck.layout_background("内容页", ST / "bg_light.png", "米白底加圆点")
    for lay in ("封面", "章节"): deck.layout_background(lay, ST / "bg_dark.png", "深蓝底加圆点")
背景图由 make_bg.py 生成。
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


_ensure_bg(['bg_light.png', 'bg_dark.png'])
WF = pathlib.Path("C:/Windows/Fonts")

THEME = dict(
    bg="FFF8EC", ink="1B2A4A", sub="55637F", line="F0E4CF", card="FFFFFF", card2="FFF1D6",
    coral="FF6B4A", teal="1E66D8", sand="FFC93C", navy="1B2A4A", white="FFFFFF", em="FF6B4A",
    sky="D6EBFF", peach="FFDCCF", mint="CDF3E4", butter="FFF0B8", green="1FBF8F", red="F0453A", pink="FFD3E6", lilac="E3DAFF",
    card_alpha=1.0, glow=None, shadow=True, accent_bar=False, dark_text="1B2A4A",
    outline=None, outline_w=1.0, hard_shadow=0, title_marker=False,
    radius=24.0, panel_radius=28.0, pill_adj=0.5, band_plain=True,
    font="Microsoft YaHei", font_file=str(WF / "msyh.ttc"),
    font_bold=None, font_bold_file=str(WF / "msyhbd.ttc"),
    font_hand="Microsoft YaHei", font_hand_file=str(WF / "msyh.ttc"),          # 手写批注字体在本风格里用雅黑；想用霞鹜文楷可改这两项
    tips={},
    skin="flat",                      # 图示容器的材质：实心糖果色、圆角、无描边、彩色软影（见 scripts/diagram_skins.py）
)
