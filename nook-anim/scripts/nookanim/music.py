"""配乐：测节拍与调性、截取并补同调收尾和弦、生成画面对拍的时间映射表。

MiniMax Music3 的时长和速度都不听提示词（文件长度等于 max_duration，在上限处硬切；写的 BPM 不遵守）。
所以做法是：生成比片长更长的音乐 → 测真实节拍 → 在半小节处截取并补收尾 → 让画面去对音乐。

命令行：python <S>/run.py music <音乐文件> --dur 21 --end-by 20.4 --anchors 3,6,7.9,... --out-dir <目录>
"""
import argparse
import json
import math
import pathlib
import subprocess

import numpy as np

from . import config
from .audio import SR, write_wav

NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def load_stereo(path):
    raw = subprocess.run([config.ffmpeg(), "-loglevel", "error", "-i", str(path), "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32).reshape(-1, 2) / 32768


def analyze(st):
    """返回 bpm、拍点、小节第一拍、半小节点、调性。频谱通量起音 + 自相关 + 梳状相位。"""
    mono = st.mean(1)
    n, hop = 2048, 512
    frames = np.lib.stride_tricks.sliding_window_view(mono, n)[::hop] * np.hanning(n)
    spec = np.abs(np.fft.rfft(frames, axis=1))
    flux = np.concatenate([[0], np.maximum(np.diff(np.log1p(spec * 10), axis=0), 0).sum(1)])
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    fps = SR / hop
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    ac /= ac[0]
    bpms = np.arange(70, 181)
    score = np.array([ac[int(round(fps * 60 / b))] for b in bpms]) * np.where((bpms >= 80) & (bpms <= 140), 1.0, 0.85)
    bpm = float(bpms[np.argmax(score)])
    fine = np.arange(bpm - 1.5, bpm + 1.5, 0.1)
    bpm = float(fine[int(np.argmax([np.interp(fps * 60 / b, np.arange(len(ac)), ac) for b in fine]))])
    period = 60 / bpm
    t_axis = np.arange(len(flux)) / fps
    best, ph0 = -1e9, 0.0
    for ph in np.arange(0, period, 0.01):
        v = np.interp(np.arange(ph, t_axis[-1], period), t_axis, flux).sum()
        if v > best:
            best, ph0 = v, ph
    beats = np.arange(ph0, len(mono) / SR, period)
    bar_off = int(np.argmax([np.interp(beats[k::4], t_axis, flux).sum() for k in range(4)]))
    # 调性：音级能量与 Krumhansl 大小调模板比对
    freqs = np.fft.rfftfreq(n, 1 / SR)
    chroma = np.zeros(12)
    for f, a in zip(freqs, spec.mean(0)):
        if 60 < f < 4000:
            chroma[int(round(12 * math.log2(f / 440) + 69)) % 12] += a
    maj = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    mnr = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    _, tonic, mode = max([(np.corrcoef(chroma, np.roll(maj, k))[0, 1], k, "major") for k in range(12)] +
                         [(np.corrcoef(chroma, np.roll(mnr, k))[0, 1], k, "minor") for k in range(12)])
    return {"bpm": bpm, "period": period, "beats": beats.tolist(), "downbeats": beats[bar_off::4].tolist(),
            "halfbars": beats[bar_off::2].tolist(), "tonic": int(tonic), "mode": mode, "key": f"{NAMES[tonic]} {mode}"}


def cut_with_ending(st, info, dur, end_by):
    """从头截取 dur 秒：在 end_by 之前最后一个半小节点淡出原曲，叠同调收尾和弦。返回 (音频, 收尾时间)。"""
    hb = np.array(info["halfbars"])
    cut = float(hb[hb <= end_by][-1])
    out = st[: int(dur * SR)].copy()
    if len(out) < int(dur * SR):
        out = np.vstack([out, np.zeros((int(dur * SR) - len(out), 2), np.float32)])
    i0, i1 = int(cut * SR), int((cut + 0.35) * SR)
    fade = np.ones(len(out))
    fade[i0:i1] = np.linspace(1, 0, i1 - i0)
    fade[i1:] = 0
    out *= fade[:, None]
    third = 4 if info["mode"] == "major" else 3
    t0 = info["tonic"]
    nch = len(out) - i0
    tt = np.arange(nch) / SR
    chord = np.zeros(nch)
    for j, m in enumerate([60 + t0, 60 + t0 + third, 67 + t0, 72 + t0]):
        f0 = 440 * 2 ** ((m - 69) / 12)
        dly = int(j * 0.03 * SR)
        tn = (np.sin(2 * np.pi * f0 * tt) + 0.35 * np.sin(4 * np.pi * f0 * tt) + 0.12 * np.sin(8 * np.pi * f0 * tt)) * np.exp(-tt / 0.9)
        chord[dly:] += tn[: nch - dly] * 0.18
    chord *= np.clip(np.linspace(1.4, 0, nch) * 2, 0, 1)
    level = np.sqrt(np.mean(st[max(0, i0 - 2 * SR):i0] ** 2))
    chord *= level / (np.sqrt(np.mean(chord[: int(0.5 * SR)] ** 2)) + 1e-9) * 0.9
    out[i0:] += chord[:, None]
    tail = int(0.05 * SR)
    out[-tail:] *= np.linspace(1, 0, tail)[:, None]
    return out / (np.abs(out).max() + 1e-9) * 0.9, cut


def snap_warp(anchors, beats, dur, cut=None, max_shift_ratio=0.45, min_gap=0.25):
    """关键时间点（故事时间）吸附到最近拍点，得到分段线性映射表 {"video", "story"}。单点挪动不超过半拍。"""
    beats = np.array(beats)
    period = float(np.median(np.diff(beats)))
    story, video = [0.0], [0.0]
    for a in sorted(anchors + ([cut] if cut else [])):
        b = float(beats[np.argmin(np.abs(beats - a))])
        v = cut if (cut is not None and a == cut) else (b if abs(b - a) <= period * max_shift_ratio else a)
        if v - video[-1] > min_gap and a - story[-1] > min_gap:
            story.append(float(a))
            video.append(float(v))
    story.append(dur)
    video.append(dur)
    return {"video": video, "story": story}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--end-by", type=float, required=True, help="收尾点不晚于此时间")
    ap.add_argument("--anchors", default="", help="需要对拍的故事时间点，逗号分隔")
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()
    out_dir = pathlib.Path(a.out_dir)
    st = load_stereo(a.src)
    info = analyze(st)
    audio, cut = cut_with_ending(st, info, a.dur, a.end_by)
    write_wav(out_dir / "music_final.wav", audio)
    anchors = [float(x) for x in a.anchors.split(",") if x.strip()]
    warp = snap_warp(anchors, info["beats"], a.dur, cut)
    json.dump(warp, open(out_dir / "warp.json", "w"))
    json.dump({**info, "cut": cut}, open(out_dir / "beats.json", "w"))
    print(f"速度 {info['bpm']:.1f} BPM | 调性 {info['key']} | 收尾 {cut:.2f}s")
    print("对拍：", [(round(s, 2), round(v, 2)) for s, v in zip(warp["story"], warp["video"])])


if __name__ == "__main__":
    main()
