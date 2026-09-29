"""《最后一块披萨》音效：全部代码合成。西部口哨、风声、风滚草、手指抽动、扑出呼啸、
定格静音、鸽子扑翅与咕咕、撞头、倒地、啄食、打嗝。时间点与 scene.py 的时间轴一致。"""
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import numpy as np

from nookanim.audio import SR, Mixer, boing, ding, midi, noise, shaped, sweep, tone, write_wav

D = pathlib.Path(__file__).parent
DUR = 16.0
mx = Mixer(DUR)


def step(t, pan):
    mx.add(sweep(170, 70, 0.07, 0.03), t, 0.22, pan)
    mx.add(shaped(noise(0.03, 800, 3000), 0.05, 0.8), t, 0.05, pan)


def whistle(t, notes, gain=0.16):
    """西部口哨：正弦 + 慢颤音 + 滑入。notes = [(相对时间, midi, 时长), ...]"""
    for dt, m, dur in notes:
        n = int(dur * SR)
        tt = np.arange(n) / SR
        f0 = midi(m)
        f = f0 * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * tt) * np.clip(tt / 0.2, 0, 1)) * (1 - 0.04 * np.exp(-tt / 0.04))
        sig = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.12 * np.sin(4 * np.pi * np.cumsum(f) / SR)
        mx.add(shaped(sig, 0.08, 0.35), t + dt, gain, -0.2)


def flaps(t0, t1, rate=9, gain=0.12, pan=0.0):
    t = t0
    while t < t1:
        mx.add(shaped(noise(0.05, 300, 2500), 0.1, 0.9), t, gain, pan)
        t += 1 / rate


def coo(t, gain=0.14, pan=0.2):
    n = int(0.45 * SR)
    tt = np.arange(n) / SR
    f = 330 + 60 * np.sin(np.pi * tt / 0.45) - 40 * tt
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * tt))
    mx.add(shaped(sig, 0.2, 0.4), t, gain, pan)


# S01 入场：脚步
for k in range(9):
    t = (k * 85 + 120) / 730 * 2.2
    if t < 2.2:
        step(t, -0.5)
        step(t + 0.08, 0.5)
mx.add(ding(1760, 0.8), 2.85, 0.06, 0.0)            # 披萨"闪一下"

# S02 发现
mx.add(ding(1568, 0.5), 3.4, 0.12, -0.4)
mx.add(ding(1568, 0.5), 3.48, 0.12, 0.4)

# S03 对决：甩鞭 + 口哨 + 风
mx.add(sweep(300, 1400, 0.18, 0.1), 4.2, 0.2)
mx.add(tone(midi(40), 1.8, 0.8, ((1, 1), (2, 0.5), (3, 0.3), (4, 0.2))), 4.2, 0.22)   # 低音弦
for t in (4.3, 4.45):
    mx.add(sweep(140, 60, 0.12, 0.05), t + 0.25, 0.25)                                 # 帽子落在头上
whistle(4.5, [(0.0, 81, 0.35), (0.38, 86, 0.35), (0.76, 81, 0.35), (1.14, 86, 0.35), (1.52, 81, 0.9)])
wind = noise(4.3, 150, 900)
tt = np.arange(len(wind)) / SR
mx.add(shaped(wind * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * tt)), 0.2, 0.2), 4.2, 0.10)
mx.add(shaped(noise(1.8, 1500, 6000), 0.2, 0.3), 4.6, 0.05, 0.6)                        # 风滚草沙沙

# S04 眼神：两下"锵"，手指抽动的哒哒声
for t in (6.2, 6.9):
    mx.add(tone(midi(88), 0.6, 0.25, ((1, 1), (2.7, 0.4))), t, 0.10)
    mx.add(sweep(90, 60, 0.5, 0.3), t, 0.18)
rng = np.random.default_rng(4)
for t in np.arange(7.6, 8.5, 0.09):
    mx.add(shaped(noise(0.015, 2000, 7000), 0.05, 0.9), t + rng.uniform(0, 0.03), 0.08, -0.3 if t < 8.05 else 0.3)

# S05 扑：蓄力 → 呼啸 → 定格静音（只有鸽子）→ 撞头
mx.add(sweep(120, 260, 0.5, 0.4), 8.5, 0.12)
mx.add(shaped(noise(0.35, 400, 5000), 0.2, 0.6), 9.0, 0.25)
mx.add(sweep(900, 300, 0.25, 0.2), 9.35, 0.12)                                        # 定格"唰"
flaps(9.42, 10.05, gain=0.14, pan=0.3)
coo(9.62, 0.12)
mx.add(boing(160, 0.5, 140, 12), 10.0, 0.5)
mx.add(sweep(110, 45, 0.25, 0.1), 10.0, 0.45)
for i, t in enumerate(np.arange(10.1, 10.9, 0.18)):
    mx.add(ding(2600 + 300 * (i % 3), 0.4), t, 0.05, (-1) ** i * 0.5)                   # 晕眩星星
mx.add(sweep(100, 50, 0.18, 0.07), 10.72, 0.4, -0.4)
mx.add(sweep(100, 50, 0.18, 0.07), 10.76, 0.4, 0.4)

# S06 鸽子
flaps(10.9, 11.4, gain=0.12, pan=-0.2)
mx.add(sweep(160, 90, 0.1, 0.05), 11.4, 0.15)
for t in (12.0, 12.45, 12.9, 13.35):
    mx.add(shaped(noise(0.07, 1500, 6000), 0.05, 0.7), t, 0.13)                        # 咔嚓
n = int(0.4 * SR)
tt = np.arange(n) / SR
burp = np.sin(2 * np.pi * np.cumsum(120 - 50 * tt) / SR) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 34 * tt)))
mx.add(shaped(burp, 0.05, 0.4), 13.8, 0.35)
mx.add(shaped(noise(0.25, 200, 800), 0.1, 0.5), 14.25, 0.08)                            # 坐起来的窸窣
coo(14.9, 0.14, 0.0)
mx.add(ding(2093, 1.2), 15.0, 0.07)

if __name__ == "__main__":
    write_wav(D / "sfx.wav", mx.master(reverb=0.12, fade_in=0.05, fade_out=0.6))
    print("sfx.wav ok")
