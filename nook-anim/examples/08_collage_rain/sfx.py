"""《撕开下雨天》音效：全部代码合成，时间点写故事时间，经 warp.json 换算到视频时间。配乐是 MiniMax Music3，见 mix.py。"""
import json
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import numpy as np

from nookanim.audio import SR, Mixer, boing, ding, midi, noise, shaped, sweep, tone, write_wav
from nookanim.core import warp_fn

D = pathlib.Path(__file__).parent
_, to_video = warp_fn(json.load(open(D / "warp.json")) if (D / "warp.json").exists() else None)

DUR = 19.0
mx = Mixer(DUR, to_video)


def slap(t, g=0.28, pan=0.0):
    mx.add(shaped(noise(0.07, 150, 1500), 0.05, 0.6), t, g, pan)
    mx.add(sweep(220, 70, 0.1, 0.05), t, g * 0.7, pan)


def rip(t0, t1, g=0.16):
    t = t0
    rng = np.random.default_rng(3)
    while t < t1:
        mx.add(shaped(noise(rng.uniform(0.03, 0.09), 1800, 7000), 0.1, 0.5), t, g * rng.uniform(0.5, 1.0), rng.uniform(-0.4, 0.4))
        t += rng.uniform(0.03, 0.08)


# S01 雨：低沉的雨声，撕开后消失
mx.add(shaped(noise(6.0, 2500, 9000), 0.25, 0.4), 0.0, 0.10, 0.0)
mx.add(shaped(noise(6.0, 400, 1400), 0.25, 0.4), 0.0, 0.05, 0.0)
mx.add(shaped(sweep(140, 90, 0.5, 0.2), 0.05, 0.3), 0.7, 0.14, 0.0)         # 小人叹气
slap(0.55, 0.22)
# S02 抛伞
mx.add(sweep(300, 900, 0.5, 0.2), 4.4, 0.16, 0.2)
slap(5.3, 0.2, 0.6)
# S03 够云：踮脚的弹簧声、抓住
mx.add(boing(260, 0.3, 120), 5.25, 0.14, -0.2)
mx.add(shaped(noise(0.25, 200, 900), 0.2, 0.5), 5.9, 0.18, 0.0)
# S04 撕开
rip(6.2, 7.9, 0.22)
mx.add(sweep(60, 30, 0.5, 0.3), 6.25, 0.3, 0.0)
# S05 晴天：亮闪闪的琶音，彩纸屑
for i, m in enumerate((72, 76, 79, 84, 88)):
    mx.add(ding(midi(m), 0.9), 7.6 + i * 0.07, 0.10, -0.3 + i * 0.15)
mx.add(shaped(noise(0.6, 4000, 9000), 0.1, 0.8), 7.65, 0.10, 0.0)
# 花：一朵一朵拍上来
for i in range(6):
    slap(8.0 + i * 0.22, 0.16, -0.6 + i * 0.25)
    mx.add(tone(midi(84 + (i % 3) * 2), 0.3, 8), 8.02 + i * 0.22, 0.06, 0.0)
# S06 变鸟：扑棱
mx.add(sweep(400, 1200, 0.3, 0.1), 9.4, 0.14, 0.3)
t = 9.5
while t < 12.6:
    mx.add(shaped(noise(0.05, 300, 2500), 0.1, 0.9), t, 0.10, 0.4 * np.sin(t * 2))
    t += 1 / 6
# S07 彩虹
for i, m in enumerate((60, 64, 67, 72, 76, 79, 84)):
    mx.add(tone(midi(m), 0.5, 5, ((1, 1.0), (2, 0.4))), 12.0 + i * 0.06, 0.10, -0.4 + i * 0.13)
slap(12.0, 0.22)
# S08 落款
slap(15.0, 0.3)
mx.add(ding(2093, 1.6), 15.35, 0.10, 0.0)
write_wav(D / "sfx.wav", mx.master(reverb=0.12, fade_in=0.03, fade_out=0.7))
print("sfx.wav ok")
