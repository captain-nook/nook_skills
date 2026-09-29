"""终混：Music3 配乐（截取并对拍后的 music_final.wav）+ 代码合成的音效 → final_mix.wav"""
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import json

import numpy as np

from nookanim.audio import SR, final_mix, read_wav, write_wav

D = pathlib.Path(__file__).parent
wj = json.load(open(D / "warp.json"))
V = lambda ts: float(np.interp(ts, wj["story"], wj["video"]))
# 配乐音量：空盘子的惊叫和惨叫前后压低一点，让音效出得来
DUCK = [(V(12.0) - 0.1, V(12.0) + 0.05, 0.55), (V(14.5), V(14.6) + 0.1, 0.5)]


def gain(t):
    g = 1.0
    for a, b, v in DUCK:
        if a <= t <= b + 0.9:
            g = min(g, v + (1 - v) * max(0.0, (t - b) / 0.9))
    return g


music, sfx = read_wav(D / "music_final.wav"), read_wav(D / "sfx.wav")
write_wav(D / "final_mix.wav", final_mix(music, sfx, gain, music_gain=0.85, sfx_gain=0.75))
print("final_mix.wav ok")
