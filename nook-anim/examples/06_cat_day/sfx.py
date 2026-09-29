"""《一只猫的一天》配乐 + 音效：全部代码合成，120 BPM，与 scene.py 的拍子对齐。

配乐：底鼓每拍、军鼓 2/4 拍、八分踩镲、贝斯 C-G-A-F 循环、拨弦点缀。
夜里跑酷段（第 21–25 拍）只留贝斯和踩镲；"理你 0 次"那一拍全部急停，开罐头（第 27 拍）一起回来。
"""
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import numpy as np

from nookanim.audio import SR, Mixer, boing, ding, midi, noise, shaped, sweep, tone, write_wav
from nookanim.mg import Beat

D = pathlib.Path(__file__).parent
DUR = 17.0
B = Beat(120)
mx = Mixer(DUR)

SILENT = (B(25.5), B(27))          # 急停区间


def on(t):
    return not (SILENT[0] <= t < SILENT[1])


def kick(t, g=0.5):
    mx.add(sweep(150, 45, 0.18, 0.08), t, g)


def snare(t, g=0.18):
    mx.add(shaped(noise(0.12, 1200, 7000), 0.02, 0.9), t, g)
    mx.add(tone(190, 0.1, 0.04), t, g * 0.6)


def hat(t, g=0.05, pan=0.2):
    mx.add(shaped(noise(0.03, 6000, 12000), 0.02, 0.9), t, g, pan)


def bass(t, m, dur=0.45, g=0.2):
    mx.add(shaped(tone(midi(m), dur, 0.3, ((1, 1), (2, 0.35), (3, 0.1))), 0.02, 0.3), t, g)


def pluck(t, m, g=0.07, pan=0.0):
    mx.add(tone(midi(m), 0.5, 0.18, ((1, 1), (2, 0.5), (3, 0.25), (4, 0.1))), t, g, pan)


def meow(t, g=0.18, up=1.0):
    n = int(0.55 * SR)
    tt = np.arange(n) / SR
    f = (520 + 380 * np.sin(np.pi * np.clip(tt / 0.4, 0, 1)) * up) * (1 + 0.015 * np.sin(2 * np.pi * 6 * tt))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    mx.add(shaped(sig, 0.15, 0.45), t, g)


ROOTS = [36, 43, 45, 41]   # C G A F
CHORD = {36: (60, 64, 67), 43: (59, 62, 67), 45: (60, 64, 69), 41: (60, 65, 69)}

# ---------------- 配乐 ----------------
for n in range(2, 34):
    t = B(n)
    if not on(t):
        continue
    night = 21 <= n < 25
    root = ROOTS[(n // 4) % 4]
    if not night:
        kick(t, 0.45)
        if n % 2 == 1:
            snare(t)
    elif n % 2 == 0:
        kick(t, 0.25)
    hat(t, 0.04)
    if on(t + B(0.5)):
        hat(t + B(0.5), 0.05)
    bass(t, root + (12 if n % 2 else 0), g=0.16 if night else 0.2)
    if not night and n >= 4 and n % 2 == 0:
        c = CHORD[root]
        pluck(t, c[(n // 2) % 3] + 12, 0.05, -0.3)
        pluck(t + B(0.5), c[(n // 2 + 1) % 3] + 12, 0.04, 0.3)
# 收尾和弦
for m in (48, 60, 64, 67, 72):
    mx.add(tone(midi(m), 2.0, 0.9, ((1, 1), (2, 0.3))), B(33.5), 0.06)

# ---------------- 音效 ----------------
mx.add(sweep(1800, 500, 0.5, 0.4), B(0), 0.10)          # 圆点落下的哨音
mx.add(boing(200, 0.35, 150, 12), B(1), 0.35)            # 弹一下
mx.add(sweep(300, 900, 0.15, 0.1), B(2), 0.15)           # 长成猫
meow(B(3.3), 0.16)
for b in (4, 6):
    mx.add(ding(1568, 0.5), B(b), 0.08)

# 每段：标签、数字、单位的"啵"
for b0 in (8, 13, 17, 21):
    for k, f in ((0, 900), (0.5, 600), (1, 1200)):
        mx.add(sweep(f, f * 1.6, 0.08, 0.05), B(b0 + k), 0.10)
# 数字滚动的哒哒声
for (b0, b1, n) in ((8.5, 10.5, 16), (13.5, 15.5, 24)):
    for i in range(n):
        u = (i / n) ** 0.5            # 与缓出同步：前密后疏
        mx.add(shaped(noise(0.012, 3000, 8000), 0.05, 0.9), B(b0) + (B(b1) - B(b0)) * u, 0.05)
# 睡觉的呼噜
for b in (9, 10, 11, 12):
    mx.add(shaped(noise(0.3, 150, 600), 0.4, 0.5), B(b), 0.10)
# 盯墙的"？"
mx.add(sweep(500, 800, 0.2, 0.15), B(15), 0.12)
# 推杯子：推、摔碎
for k in range(3):
    mx.add(shaped(noise(0.15, 300, 1500), 0.2, 0.6), B(17 + k + 0.45), 0.08)
    tb = B(17 + k + 0.85)
    mx.add(shaped(noise(0.25, 2000, 10000), 0.01, 0.9), tb, 0.3, 0.2)
    for j in range(4):
        mx.add(ding(3000 + 700 * j + 200 * k, 0.25), tb + 0.02 * j, 0.04, 0.4 - 0.25 * j)
# 跑酷：三次呼啸
for b, pan in ((21.5, 0.0), (22.5, 0.0), (23.5, 0.0)):
    mx.add(shaped(noise(0.35, 500, 4000), 0.3, 0.5), B(b), 0.18, pan)
mx.add(boing(260, 0.3, 120, 14), B(24), 0.2)
# 理你 0 次：急停 + 闷响
mx.add(sweep(700, 60, 0.35, 0.25), B(25.5) - 0.05, 0.25)           # 唱片急停
mx.add(sweep(90, 40, 0.3, 0.12), B(25.5), 0.5)
mx.add(shaped(noise(0.4, 1500, 5000), 0.1, 0.5), B(26.5), 0.10)    # 罐头"咔"
mx.add(shaped(noise(0.05, 2000, 9000), 0.02, 0.8), B(26.5) + 0.3, 0.2)
for i, m in enumerate((72, 76, 79, 84)):                              # 爱心眼 + ∞
    mx.add(ding(midi(m), 0.8), B(27) + 0.05 * i, 0.07)
meow(B(27.6), 0.2, up=1.4)
# 结尾
mx.add(sweep(400, 1000, 0.12, 0.08), B(30), 0.12)
mx.add(ding(2093, 1.0), B(33), 0.08)
meow(B(33.1), 0.12, up=0.8)

if __name__ == "__main__":
    write_wav(D / "sfx.wav", mx.master(reverb=0.1, fade_in=0.02, fade_out=0.5))
    print("sfx.wav ok")
