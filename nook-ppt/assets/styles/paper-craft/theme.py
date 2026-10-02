"""风格包「纸片手作」（可爱）的主题字典。桌面上的手工纸片：撕边纸片、胶带、回形针、纸片剪出的小图标，小船长当贴纸。
浅色底是牛皮纸桌面，深色底是夜间台灯下的桌面。纸片由 parts.py 现画（撕边、纤维白边、纸纹、投影），图标由千问出图。
用法：
    import sys; sys.path.insert(0, "<skill>/assets/styles/paper-craft")
    from theme import THEME, ST
    from parts import paper_card
    deck = Deck(theme=THEME, mode="talk")
    deck.layout_background("内容页", ST / "bg_light.png", "牛皮纸桌面")
    for lay in ("封面", "章节"): deck.layout_background(lay, ST / "bg_dark.png", "夜间台灯下的桌面")
"""
import os
import pathlib

ST = pathlib.Path(__file__).parent
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
    bg="F3E7D3", ink="3B2F2F", sub="5E4F3E", line="D9C7A6", card="FFFDF7", card2="F6EBD3",
    coral="E4572E", teal="2A9D8F", sand="F4C95D", navy="2B3A55", white="FFFFFF", em="E4572E",
    sky="C9DDF0", peach="F9CDB8", mint="C5E3CF", butter="FFE9A8", green="4E9F6B", red="D64545", pink="F4B6C6", lilac="D3C4EC",
    card_alpha=1.0, glow=None, shadow=True, accent_bar=False, dark_text="3B2F2F",
    outline=None, outline_w=1.0, hard_shadow=0, title_marker=True,
    radius=14.0, panel_radius=16.0, pill_adj=0.5, band_plain=True,
    font=("LXGW WenKai Light" if _LX else "Microsoft YaHei"), font_file=(str(UF / "LXGWWenKai-Light.ttf") if _LX else str(_WF / "msyh.ttc")),
    font_bold=("Source Han Serif CN Heavy" if _SH else None), font_bold_file=(str(UF / "SourceHanSerifCN-Heavy-4.otf") if _SH else str(_WF / "msyhbd.ttc")),
    font_hand=("LXGW WenKai Light" if _LX else "Microsoft YaHei"), font_hand_file=(str(UF / "LXGWWenKai-Light.ttf") if _LX else str(_WF / "msyh.ttc")),
    tips={},
    skin="paper",                     # 图示容器的材质：撕边纸片（见 scripts/diagram_skins.py）
)
