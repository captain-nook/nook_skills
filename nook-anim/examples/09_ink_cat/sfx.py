"""《墨猫与月亮》音效：全部代码合成，时间点写故事时间，经 warp.json 换算到视频时间。配乐是 MiniMax Music3，见 mix.py。"""
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


def drip(t, f=520, g=0.22, pan=0.0):
    mx.add(sweep(f, f * 0.45, 0.18, 0.06), t, g, pan)
    mx.add(tone(f * 2, 0.25, 12), t, g * 0.2, pan)


def paw(t, g=0.05):
    mx.add(shaped(noise(0.03, 500, 3000), 0.1, 0.6), t, g, 0.0)


# S01 墨滴落下、砸在纸上
mx.add(sweep(1800, 500, 0.45, 0.4), 0.9, 0.05, 0.3)
drip(1.35, 420, 0.30, 0.3)
mx.add(sweep(90, 45, 0.7, 0.3), 1.4, 0.22, 0.0)
# S02 墨在纸上洇开：低沉的沙沙声
mx.add(shaped(noise(3.3, 200, 1400), 0.4, 0.4), 1.9, 0.10, 0.0)
# S03 月亮留白出来：一声轻轻的钟
mx.add(ding(880, 2.6), 3.2, 0.16, 0.3)
mx.add(ding(1320, 2.2), 3.35, 0.08, 0.4)
# S04 猫来：轻轻的喵
n = int(0.5 * SR); tt = np.arange(n) / SR
f = 560 + 240 * np.sin(np.pi * tt / 0.5)
mx.add(shaped(np.sin(2 * np.pi * np.cumsum(f) / SR), 0.15, 0.6), 4.7, 0.10, -0.4)
# S05 够月亮：伸直
mx.add(sweep(300, 600, 0.6, 0.3), 6.0, 0.06, -0.3)
# S06 追：小碎步
t = 7.25
while t < 8.5:
    paw(t, 0.06); t += 0.09
mx.add(shaped(noise(0.4, 500, 3500), 0.2, 0.6), 7.2, 0.05, 0.0)
# S07 蹲下
mx.add(shaped(noise(0.15, 200, 900), 0.3, 0.6), 8.6, 0.08, 0.0)
# S08 水里出现月亮和猫：水滴一样的音
for i, m in enumerate((79, 83, 86)):
    mx.add(ding(midi(m), 1.6), 9.0 + i * 0.25, 0.10, 0.4)
# S09 一拨：爪子划过、水花、涟漪
mx.add(sweep(1800, 400, 0.22, 0.1), 10.85, 0.16, 0.3)
mx.add(shaped(noise(0.5, 300, 6000), 0.03, 0.9), 11.05, 0.28, 0.4)
for k in range(9):
    drip(11.1 + k * 0.11, 500 + 70 * (k % 4), 0.10, -0.3 + 0.1 * k)
for k in range(4):
    mx.add(ding(midi(72 + 2 * k), 1.8), 11.4 + k * 0.5, 0.06, 0.4)
# S10 月圆：又一声钟
mx.add(ding(880, 2.6), 13.0, 0.12, 0.3)
# S11 题款、印章
mx.add(shaped(noise(1.5, 300, 4000), 0.4, 0.5), 15.2, 0.05, 0.3)
mx.add(sweep(140, 55, 0.3, 0.14), 17.1, 0.30, 0.0)
mx.add(shaped(noise(0.06, 200, 1000), 0.05, 0.6), 17.1, 0.20, 0.0)
write_wav(D / "sfx.wav", mx.master(reverb=0.16, fade_in=0.03, fade_out=0.8))
print("sfx.wav ok")
