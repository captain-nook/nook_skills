"""风格包「船长课堂」（明亮纸张版）的主题字典。用法：
    import sys; sys.path.insert(0, "<skill>/assets/styles/captain-class")
    from theme import THEME, ST
    deck = Deck(theme=THEME, mode="talk")
    for lay in ("封面", "内容页", "章节"):
        deck.layout_background(lay, ST / "paper_bg.png", "暖白纸张底，淡蓝方格线")
字体默认取当前用户的字体目录（思源宋体、霞鹜文楷 Light，需自行安装，见 assets/fonts/README.md），可用环境变量 NOOKPPT_FONT_DIR 改；没装时退回微软雅黑。
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

TIPS = {
    "notice": dict(sprite=str(ST / "tips/tip_serious.png"), label="注意", color="coral"),
    "ask": dict(sprite=str(ST / "tips/tip_confused.png"), label="想一想", color="teal"),
    "trick": dict(sprite=str(ST / "tips/tip_clever.png"), label="有窍门", color="green"),
    "shock": dict(sprite=str(ST / "tips/tip_surprised.png"), label="反常识", color="coral"),
    "pain": dict(sprite=str(ST / "tips/tip_cry.png"), label="痛点", color="teal"),
    "donot": dict(sprite=str(ST / "tips/tip_angry.png"), label="别这样", color="red"),
    "good": dict(sprite=str(ST / "tips/tip_thumbsup.png"), label="做得好", color="green"),
    "news": dict(sprite=str(ST / "tips/tip_cheer.png"), label="好消息", color="sand"),
    "think": dict(sprite=str(ST / "tips/tip_thinking.png"), label="分析中", color="teal"),
    "hello": dict(sprite=str(ST / "tips/tip_wave.png"), label="开场", color="teal"),
    "thanks": dict(sprite=str(ST / "tips/tip_love.png"), label="谢谢", color="pink"),
    "egg": dict(sprite=str(ST / "tips/tip_laugh.png"), label="彩蛋", color="sand"),
}

THEME = dict(
    bg="FBF7EE", ink="1E2A44", sub="5B6477", line="DDD2BA", card="FFFFFF", card2="F0EAD8",
    coral="F26B21", teal="2F6FDE", sand="FFD93D", navy="1E2A44", white="FFFFFF", em="F26B21",
    sky="DCE8FA", peach="FCE3D0", mint="DDEFD9", butter="FFF1B8", green="1D7A4E", red="D9382B", pink="E8547A",
    card_alpha=1.0, glow=None, shadow=False, accent_bar=False, dark_text="1E2A44",
    outline="1E2A44", outline_w=2.25, hard_shadow=4.5, title_marker=True,          # 容器：墨线描边 + 硬投影，和纸面拉开对比
    font=("Source Han Serif CN Medium" if _SM else "Microsoft YaHei"), font_file=(str(UF / "SourceHanSerifCN-Medium-6.otf") if _SM else str(_WF / "msyh.ttc")),
    font_bold=("Source Han Serif CN Heavy" if _SH else None), font_bold_file=(str(UF / "SourceHanSerifCN-Heavy-4.otf") if _SH else str(_WF / "msyhbd.ttc")),
    font_hand=("LXGW WenKai Light" if _LX else "Microsoft YaHei"), font_hand_file=(str(UF / "LXGWWenKai-Light.ttf") if _LX else str(_WF / "msyh.ttc")),
    tips=TIPS,
)
