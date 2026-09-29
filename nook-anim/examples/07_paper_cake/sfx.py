"""《蛋糕保卫战》音效：全部代码合成，时间点写故事时间，经 warp.json 换算到视频时间。
脚步、放下蛋糕的"叮"、问号、啃食、火柴划燃、惨叫。配乐是 MiniMax Music3 生成的，见 mix.py。"""
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import json

import numpy as np

from nookanim.core import warp_fn
from nookanim.audio import SR, Mixer, boing, ding, midi, noise, shaped, sweep, tone, write_wav

D = pathlib.Path(__file__).parent
DUR = 18.5
_, to_video = warp_fn(json.load(open(D / "warp.json")) if (D / "warp.json").exists() else None)
mx = Mixer(DUR, to_video)


def step(t, pan=0.0, g=0.2):
    mx.add(sweep(180, 80, 0.06, 0.03), t, g, pan)
    mx.add(shaped(noise(0.03, 900, 3200), 0.05, 0.8), t, g * 0.3, pan)


def pluck(t, m, g=0.16, pan=0.0, dur=0.28):
    mx.add(tone(midi(m), dur, 9, ((1, 1.0), (2, 0.35), (3, 0.12))), t, g, pan)


def marimba(t, m, g=0.14, pan=0.0):
    mx.add(tone(midi(m), 0.4, 7, ((1, 1.0), (4, 0.25))), t, g, pan)


def chomp(t, g=0.28):
    mx.add(shaped(noise(0.09, 300, 2400), 0.06, 0.7), t, g, 0.1)
    mx.add(sweep(240, 90, 0.09, 0.04), t, g * 0.8, 0.1)


# ---- S01 端蛋糕：脚步 ----
t = 0.15
while t < 3.6:
    step(t, -0.3); step(t + 0.11, 0.3); t += 0.42
t = 1.7
while t < 4.9:
    step(t, 0.35, 0.09); t += 0.5
# ---- S02 放下 ----
mx.add(shaped(noise(0.06, 200, 1200), 0.05, 0.6), 4.05, 0.3)
mx.add(ding(1568, 0.8), 4.1, 0.12)
for i, m in enumerate((84, 88, 91)):
    marimba(4.15 + i * 0.08, m, 0.10)
# ---- S03 回头：问号（上滑的短音）和老鼠定格 ----
mx.add(sweep(500, 900, 0.18, 0.06), 5.15, 0.14, 0.0)
mx.add(boing(300, 0.2, 100), 5.0, 0.18, -0.5)
# ---- S04 走开：厨师脚步 ----
t = 6.65
while t < 8.0:
    step(t, 0.2, 0.2); t += 0.34
# ---- S05 偷吃 ----
for k in range(6):
    step(7.05 + k * 0.17, -0.1, 0.06)
mx.add(sweep(200, 400, 0.4, 0.1), 8.0, 0.12, 0.0)                      # 跳
mx.add(shaped(noise(0.05, 200, 1500), 0.05, 0.6), 8.5, 0.16, 0.0)
for bt in (8.9, 9.25, 9.6, 9.95, 10.2, 10.3):
    chomp(bt)
mx.add(boing(160, 0.4, 60), 10.3, 0.18, 0.0)                            # 吃饱
mx.add(tone(midi(46), 0.3, 6), 10.55, 0.2, 0.0)                         # 打嗝
# ---- S06 回来 ----
t = 10.9
while t < 12.0:
    step(t, 0.4, 0.2); t += 0.32
# ---- S07 空盘子：惊叫 ----
mx.add(sweep(1200, 500, 0.35, 0.15), 12.0, 0.2, 0.3)
mx.add(shaped(noise(0.2, 200, 800), 0.05, 0.9), 12.0, 0.15, 0.3)
mx.add(ding(1760, 0.6), 12.05, 0.08, 0.4)
# ---- S08 点蜡烛：划火柴、火苗、脚步 ----
mx.add(shaped(noise(0.35, 1200, 6000), 0.5, 0.2), 12.85, 0.16, -0.2)    # 嗤
mx.add(shaped(noise(0.7, 400, 2000), 0.2, 0.6), 13.05, 0.05, -0.2)      # 火苗
t = 13.3
while t < 14.4:
    step(t, -0.2, 0.15); t += 0.36
mx.add(shaped(noise(0.3, 500, 4000), 0.3, 0.3), 14.3, 0.14, -0.4)        # 点着
# ---- S09 惨叫 ----
mx.add(sweep(500, 2000, 0.25, 0.08), 14.6, 0.22, -0.2)
mx.add(sweep(2000, 700, 0.9, 0.5), 14.85, 0.16, -0.5)
mx.add(shaped(noise(1.2, 300, 3000), 0.1, 0.9), 14.7, 0.08, -0.6)
mx.add(boing(220, 0.5, 200), 14.9, 0.15, -0.3)
# ---- S10 落款：逐字敲木鱼 ----
for i, m in enumerate((72, 74, 76, 79, 84)):
    marimba(16.0 + i * 0.16, m, 0.14)
mx.add(ding(2093, 1.6), 16.9, 0.10, 0.0)

write_wav(D / "sfx.wav", mx.master(reverb=0.12, fade_in=0.03, fade_out=0.7))
print("sfx.wav ok")
