"""《画个方向》音效：全部代码合成。时间写故事时间，有 warp.json 时自动换算到视频时间。"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

import numpy as np

from nookanim.audio import Mixer, boing, ding, midi, noise, shaped, sweep, tone, write_wav
from nookanim.core import warp_fn

D = pathlib.Path(__file__).parent
DUR = 20.0
_, to_video = warp_fn(json.load(open(D / "warp.json")) if (D / "warp.json").exists() else None)
mx = Mixer(DUR, to_video)
rng = np.random.default_rng(12)


def scratch(t, dur, gain=0.12, lo=2200, hi=7500, rate=9, pan=0.0):
    """铅笔在纸上的沙沙声：带通噪声，按笔划节奏起伏。"""
    n = noise(dur, lo, hi)
    tt = np.arange(len(n)) / 44100
    mx.add(shaped(n * (0.45 + 0.55 * np.abs(np.sin(2 * np.pi * rate * tt))), 0.08, 0.2), t, gain, pan)


def clap(t, gain=0.4):
    n = noise(0.12, 800, 6000)
    mx.add(n * np.exp(-np.arange(len(n)) / 44100 / 0.03), t, gain)


# S01 开场：墨点、画小船长、眨眼、问号
mx.add(sweep(240, 90, 0.25, 0.08), 0.28, 0.45)
for i in range(8):
    scratch(0.6 + i * 0.2, 0.16, 0.10, rate=12, pan=-0.2 + 0.05 * i)
mx.add(sweep(1500, 2300, 0.05, 0.02), 2.28, 0.08)
mx.add(sweep(420, 640, 0.18, 0.1), 2.5, 0.18)

# S02 定方向：画箭头、铅笔蹦出、鞠躬
scratch(3.2, 1.0, 0.13, rate=6)
mx.add(boing(260, 0.35, 150), 4.4, 0.35)
mx.add(tone(midi(88), 0.4, 0.12, ((1, 1), (2.7, 0.3))), 4.75, 0.08, pan=0.4)

# S03 执行：一路画路 + 蹦跳 + 顺手画物件 + 音符
n = noise(6.0, 1800, 6500)
tt = np.arange(len(n)) / 44100
mx.add(shaped(n * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 6 * tt))), 0.03, 0.05), 5.0, 0.07, pan=0.2)
for i in range(int(6.0 * 6)):
    mx.add(tone(900 + 80 * (i % 2), 0.05, 0.02), 5.0 + i / 6, 0.035, pan=0.3)
for t0, d in ((7.2, 0.6), (8.2, 0.7), (9.5, 0.7)):
    scratch(t0, d, 0.11, rate=11, pan=-0.1)
for t0 in (7.9, 9.0):
    mx.add(tone(midi(84), 0.4, 0.15, ((1, 1), (2, 0.2))), t0, 0.06, pan=-0.3)

# S04 跑偏：越来越急、"！"、画边界、撞上、晕
n = noise(1.8, 2500, 8000)
tt = np.arange(len(n)) / 44100
mx.add(shaped(n * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * (8 + 10 * tt) * tt))), 0.05, 0.05), 11.0, 0.12, pan=0.3)
mx.add(sweep(700, 1300, 0.15, 0.08), 11.5, 0.18)
mx.add(shaped(noise(0.4, 1200, 7000), 0.1, 0.4), 12.2, 0.18, pan=-0.2)
mx.add(sweep(160, 70, 0.3, 0.12), 12.8, 0.45)
mx.add(boing(300, 0.5, 220, 11), 12.82, 0.3)
for i in range(4):
    mx.add(sweep(2600, 3400, 0.08, 0.04), 12.95 + i * 0.16, 0.05, pan=(-1) ** i * 0.5)

# S05 抵达：画山、画灯塔、灯光、击掌
scratch(13.7, 0.7, 0.10, rate=5)
for i in range(7):
    scratch(14.8 + i * 0.17, 0.14, 0.10, rate=14, pan=0.2)
for i, m in enumerate((79, 83, 86, 91)):
    mx.add(tone(midi(m), 0.9, 0.35, ((1, 1), (2.01, 0.25))), 16.0 + i * 0.05, 0.05, pan=0.3)
clap(16.62, 0.4)
mx.add(tone(midi(96), 0.5, 0.15), 16.64, 0.06, pan=0.3)

# S06 收尾：拉远、写字、叮
mx.add(shaped(noise(0.9, 300, 3000), 0.4, 0.5), 17.3, 0.12)
scratch(18.4, 0.9, 0.10, rate=10)
mx.add(ding(midi(96)), 19.05, 0.28, pan=0.3)

write_wav(D / "sfx.wav", mx.master(reverb=0.15, fade_in=0.2, fade_out=0.5))
print("sfx.wav ok")
