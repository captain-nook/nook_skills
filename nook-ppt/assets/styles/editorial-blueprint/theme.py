"""风格包「刊物·图纸」（正式，浅色内容页 + 深墨蓝封面/章节页）的主题字典。用法：
    import sys; sys.path.insert(0, "<skill>/assets/styles/editorial-blueprint")
    from theme import THEME, ST
    deck = Deck(theme=THEME, mode="talk")
    deck.layout_background("内容页", ST / "paper_bg.png", "米白纸底，淡网格")
    for lay in ("封面", "章节"):
        deck.layout_background(lay, ST / "ink_bg.png", "深墨蓝图纸网格底")
气质：编辑刊物加工程图纸。克制、有秩序、留白多；直角小圆角、细线、无投影、无旋转、无人物；
一个强调色（工程橙）加一个辅助蓝，编号和细线承担装饰。字体同为思源宋，靠结构与「船长课堂」区分。
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


_ensure_bg(['paper_bg.png', 'ink_bg.png'])
def _font_dir():
    """字体目录：环境变量 NOOKPPT_FONT_DIR → 当前用户字体目录（有思源宋就用）→ skill 自带的 assets/fonts。"""
    env = os.environ.get("NOOKPPT_FONT_DIR")
    if env:
        return pathlib.Path(env)
    u = pathlib.Path(os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"))
    return u if (u / "SourceHanSerifCN-Medium-6.otf").exists() else pathlib.Path(__file__).resolve().parents[2] / "fonts"


UF = _font_dir()
_WF = pathlib.Path("C:/Windows/Fonts")
# 字体文件不随库提供：在就用，不在就退回系统自带的微软雅黑（量字和显示保持一致）。安装方法见仓库 README 的"字体"一节。
_SM = (UF / "SourceHanSerifCN-Medium-6.otf").exists()
_SH = (UF / "SourceHanSerifCN-Heavy-4.otf").exists()
_LX = (UF / "LXGWWenKai-Light.ttf").exists()

THEME = dict(
    bg="F4F1EA", ink="141E36", sub="55607A", line="D6CFBD", card="FFFFFF", card2="ECE7DA",
    coral="E8590C", teal="1F4E8C", sand="F2C14E", navy="141E36", white="FFFFFF", em="E8590C",
    sky="E3EAF4", peach="F8E5D6", mint="E2EEE3", butter="F5EDCF", green="2C7A4B", red="C0392B", pink="B94E77",
    card_alpha=1.0, glow=None, shadow=False, accent_bar=True, dark_text="141E36",
    outline=None, outline_w=1.0, hard_shadow=0, title_marker=False,
    radius=3.0, panel_radius=3.0, pill_adj=0.2, band_plain=True,
    font=("Source Han Serif CN Medium" if _SM else "Microsoft YaHei"), font_file=(str(UF / "SourceHanSerifCN-Medium-6.otf") if _SM else str(_WF / "msyh.ttc")),
    font_bold=("Source Han Serif CN Heavy" if _SH else None), font_bold_file=(str(UF / "SourceHanSerifCN-Heavy-4.otf") if _SH else str(_WF / "msyhbd.ttc")),
    font_hand=("Source Han Serif CN Medium" if _SM else "Microsoft YaHei"), font_hand_file=(str(UF / "SourceHanSerifCN-Medium-6.otf") if _SM else str(_WF / "msyh.ttc")),
    tips={},
    poly_line=("navy", 1.25),         # 图示多边形用细墨线勾边（刊物·图纸的线条语言），无投影
)
