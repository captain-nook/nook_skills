"""标题卡：title01_code（4 秒，带音效）。字来自千问 Image 2.1 出的透明底 PNG，动效全部由代码完成。"""
from titlekit import *

T = Title("title01_code", 4, "point", side="right", flip=False, hue=C["cyan"])
DUR = TITLE_DUR
SHOTS = [(0.0, "落字"), (1.05, "扫光"), (2.0, "停留")]


def render(t):
    return T.render(t)
