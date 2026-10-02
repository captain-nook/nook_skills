"""风格包「东方雅集」（正式）的主题字典：宣纸底、墨色字、朱砂一点红、淡金细线、水墨山水与花木。
两个主题：THEME（宣纸浅色，默认）、THEME_DARK（暗墨青底，金线）。字体用思源宋（随库 assets/fonts）。
用法：
    import sys; sys.path.insert(0, "<skill>/assets/styles/oriental-yaji")
    from theme import THEME, THEME_DARK, ST
    deck = Deck(theme=THEME, mode="talk")
    deck.layout_background("内容页", ST / "bg_paper.png", "宣纸底")
    deck.layout_background("封面", ST / "bg_cover_l.png", "封面：水墨远山")
底图由 make_bg.py 生成（图片素材在 raw/，出图任务见 jobs_yaji.json）。
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


_ensure_bg(['bg_paper.png', 'bg_ink.png', 'bg_cover_l.png', 'bg_cover_d.png', 'bg_end_l.png', 'bg_end_d.png', 'bg_mist_l.png', 'bg_mist_d.png'])


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
    bg="F4EFE3", ink="26211C", sub="5C5349", line="D9CFB9", card="FBF8F0", card2="EFE7D6",
    coral="B23A2F", teal="3E5C5A", sand="B08D57", navy="26211C", white="FFFFFF", em="B23A2F",
    green="4A6B52", red="B23A2F",
    sky="D9E3E0", peach="F1DAD0", mint="DDE6D8", butter="EFE3C2", pink="F0D8D4", lilac="E4DDE0",     # 浅色系：淡青、淡朱、淡石绿、淡金
    card_alpha=1.0, glow=None, shadow=False, accent_bar=False, dark_text="26211C",
    outline=None, outline_w=1.0, hard_shadow=0, title_marker=False,
    radius=8.0, panel_radius=10.0, pill_adj=0.3, band_plain=True,
    font=("Source Han Serif CN Medium" if _SM else "Microsoft YaHei"), font_file=(str(UF / "SourceHanSerifCN-Medium-6.otf") if _SM else str(_WF / "msyh.ttc")),
    font_bold=("Source Han Serif CN Heavy" if _SH else None), font_bold_file=(str(UF / "SourceHanSerifCN-Heavy-4.otf") if _SH else str(_WF / "msyhbd.ttc")),
    font_hand=("Source Han Serif CN Medium" if _SM else "Microsoft YaHei"), font_hand_file=(str(UF / "SourceHanSerifCN-Medium-6.otf") if _SM else str(_WF / "msyh.ttc")),
    tips={},
    skin="ink",                       # 图示容器的材质：水墨（见 scripts/diagram_skins.py）
    # 光影：宣纸卡面（暖白微渐变）、淡金细边、很淡的暖褐投影（墨晕）；不用光池和反光
    glass=dict(fill=[(0, "FCF9F2", 100), (100, "F1EADB", 100)], fill2=[(0, "F7ECDF", 100), (100, "EBDCC6", 100)],
               rim=[(0, "FFFFFF", 90), (50, "D9CFB9", 85), (100, "B08D57", 75)], rim_w=1.0, angle=90,
               shadow=("5A4630", 14, 30, 12), inner=("FFFFFF", 80, 6, 2)),
    glass_img=dict(rim=[(0, "FFFFFF", 80), (50, "D9CFB9", 70), (100, "B08D57", 80)], rim_w=1.0, shadow=("5A4630", 14, 30, 12)),
    num_grad=[(0, "26211C", 100), (100, "7A3B2E", 100)],
)

# 暗墨青版：底暗墨青，字宣纸白，强调用淡金（朱砂在暗底上对比不够，只留给印章），卡面深青渐变加金线边
THEME_DARK = dict(
    THEME,
    bg="0E1A19", ink="EFE8D8", sub="C4BCAA", line="2A3A38", card="16262A", card2="1D2F31",
    coral="D9B873", teal="7FB5A8", sand="D9B873", navy="0E1A19", em="D9B873", green="8FBF9F",
    dark_text="0E1A19",
    sky="1F3A3A", peach="3A2B27", mint="23372C", butter="3A3524", pink="3A2B2B", lilac="2E2B33",
    glass=dict(fill=[(0, "1E3234", 100), (100, "101D1F", 100)], fill2=[(0, "2A3B33", 100), (100, "16241F", 100)],
               rim=[(0, "E8D49A", 55), (40, "E8D49A", 12), (100, "E8D49A", 40)], rim_w=1.0, angle=90,
               shadow=("000000", 50, 30, 12), inner=("FFFFFF", 10, 6, 2)),
    glass_img=dict(rim=[(0, "E8D49A", 50), (40, "E8D49A", 10), (100, "E8D49A", 45)], rim_w=1.0, shadow=("000000", 40, 30, 12)),
    num_grad=[(0, "F6EFDD", 100), (100, "D9B873", 100)],
)
