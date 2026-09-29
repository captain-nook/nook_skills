"""机器相关设置。全部可用环境变量覆盖，代码里不写个人路径。"""
import os
import pathlib

COMFY_HOST = os.environ.get("NOOKANIM_COMFY", "http://127.0.0.1:8188")

_FONTS = pathlib.Path(os.environ.get("NOOKANIM_FONT_DIR", "C:/Windows/Fonts"))
FONT_UI = os.environ.get("NOOKANIM_FONT_UI", str(_FONTS / "msyhbd.ttc"))          # 界面/符号：微软雅黑粗体
FONT_HAND_EN = os.environ.get("NOOKANIM_FONT_HAND_EN", str(_FONTS / "segoeprb.ttf"))  # 英文手写：Segoe Print Bold
FONT_HAND_ZH = os.environ.get("NOOKANIM_FONT_HAND_ZH", str(_FONTS / "STXINGKA.TTF"))  # 中文手写：华文行楷

# MiniMax Music3 的 API 格式 ComfyUI 工作流 JSON 路径，可覆盖
MUSIC_WORKFLOW = os.environ.get("NOOKANIM_MUSIC_WORKFLOW", "")


def ffmpeg():
    exe = os.environ.get("NOOKANIM_FFMPEG")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()
