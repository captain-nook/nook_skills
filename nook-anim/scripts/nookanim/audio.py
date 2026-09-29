"""音效合成与混音。音效全部由代码合成；时间点写故事时间，经映射表换算到视频时间。"""
import math
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter

SR = 44100
_rng = np.random.default_rng(9)


def env(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = int(a * SR)
    if na:
        e[:na] *= np.linspace(0, 1, na)
    return e


def tone(f, dur, d, partials=((1, 1.0),), a=0.002):
    """带泛音的衰减音，partials = ((倍频, 音量), ...)。钢片琴、马林巴、铃声都用它。"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    return sum(w * np.sin(2 * np.pi * f * k * t) * np.exp(-t / (d / max(1, k ** 0.5))) for k, w in partials) * env(n, a, 1e9)


def sweep(f0, f1, dur, d, a=0.003):
    """滑音：上扬（弹出、起飞）或下滑（惊慌、落地）。"""
    n = int(dur * SR)
    f = f0 * (f1 / f0) ** (np.arange(n) / n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, a, d)


def noise(dur, lo, hi):
    """带通噪声：沙沙声、呼啸、水声、风声的原料。"""
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], btype="band")
    return lfilter(b, a, _rng.standard_normal(int(dur * SR)))


def shaped(sig, attack=0.3, release=0.3):
    n = len(sig)
    e = np.ones(n)
    na, nr = int(attack * n), int(release * n)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] = np.linspace(1, 0, nr)
    return sig * e


def boing(f=220, dur=0.25, depth=120, rate=14):
    """弹簧回弹声。"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f + depth * np.exp(-t * 12) * np.cos(2 * np.pi * rate * t)) / SR) * np.exp(-t / 0.08)


def ding(f=2093.0, dur=1.6):
    """"叮"：主音加非谐泛音的铃声。"""
    return tone(f, dur, 0.7, ((1, 1.0), (2.0, 0.35), (2.76, 0.28), (5.4, 0.12)))


midi = lambda m: 440 * 2 ** ((m - 69) / 12)


class Mixer:
    """立体声混音台。add() 的时间是故事时间，warp 为 core.warp_fn 返回的"故事→视频"函数。"""

    def __init__(self, dur, to_video=None):
        self.dur = dur
        self.N = int(SR * dur)
        self.buf = np.zeros((self.N, 2))
        self.V = to_video or (lambda t: t)

    def add(self, sig, t, gain=1.0, pan=0.0):
        i = int(self.V(t) * SR)
        if i >= self.N or i < 0:
            return
        sig = sig[: self.N - i]
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        self.buf[i:i + len(sig), 0] += sig * gain * l * 1.414
        self.buf[i:i + len(sig), 1] += sig * gain * r * 1.414

    def master(self, reverb=0.18, fade_in=0.5, fade_out=0.6, peak=0.89):
        out = self.buf
        if reverb > 0:
            ir_n = int(0.8 * SR)
            ir = _rng.standard_normal((ir_n, 2)) * np.exp(-np.arange(ir_n) / SR / 0.22)[:, None]
            ir[: int(0.01 * SR)] = 0
            wet = np.stack([fftconvolve(out[:, c], ir[:, c])[: self.N] for c in range(2)], 1)
            out = out + wet / (np.abs(wet).max() + 1e-9) * np.abs(out).max() * reverb
        out = np.tanh(out / (np.abs(out).max() + 1e-9) * 1.2)
        fi, fo = int(fade_in * SR), int(fade_out * SR)
        if fi:
            out[:fi] *= np.linspace(0, 1, fi)[:, None]
        if fo:
            out[-fo:] *= np.linspace(1, 0, fo)[:, None]
        return out / (np.abs(out).max() + 1e-9) * peak


def read_wav(path):
    w = wave.open(str(path))
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a.reshape(-1, w.getnchannels())


def write_wav(path, stereo):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes())


def final_mix(music, sfx, gain_curve=None, music_gain=0.85, sfx_gain=0.55):
    """配乐 + 音效终混。gain_curve(t_video) 返回配乐音量（用于危机段压低、高潮推起）。"""
    n = min(len(music), len(sfx))
    music, sfx = music[:n], sfx[:n]
    g = np.ones(n) if gain_curve is None else np.array([gain_curve(i / SR) for i in range(0, n, 441)]).repeat(441)[:n]
    mix = music * g[:, None] * music_gain + sfx * sfx_gain
    mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.1)
    return mix / (np.abs(mix).max() + 1e-9) * 0.89
