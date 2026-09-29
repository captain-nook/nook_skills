"""渲染命令行。场景文件约定：定义 W, H, FPS, DUR, SHOTS=[(开始秒, "镜头名"), ...]，以及 render(t) → BGR 画面
（float 0–1 或 uint8）。render(t) 必须是时间的纯函数：任何一帧都能单独算出。

静帧：  python <S>/run.py render scene.py stills 3.5 7.9 [--labels]
整片：  python <S>/run.py render scene.py video --out film.mp4 [--audio mix.wav] [--warp warp.json] [--labels]
抽帧拼图：python <S>/run.py render scene.py sheet --every 1.5
渲染时在场景目录写 progress.json 与 latest.jpg，预览工作台据此显示进度。
"""
import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys
import time

import cv2
import numpy as np

from . import config
from .core import warp_fn
from .assets import imwrite
from .post import label


def load_scene(path):
    path = pathlib.Path(path).resolve()
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("scene", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.__dir__ = path.parent
    return mod


def shot_name(scene, t):
    names = [n for s, n in getattr(scene, "SHOTS", [(0, "")]) if t >= s]
    return names[-1] if names else ""


def frame_at(scene, t, labels=False, display_t=None):
    fr = scene.render(t)
    if fr.dtype != np.uint8:
        fr = (np.clip(fr, 0, 1) * 255).astype(np.uint8)
    if labels:
        f = fr.astype(np.float32) / 255
        f = label(f, f"{shot_name(scene, t)}   {display_t if display_t is not None else t:05.2f}s")
        fr = (np.clip(f, 0, 1) * 255).astype(np.uint8)
    return fr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("mode", choices=["stills", "video", "sheet"])
    ap.add_argument("times", nargs="*", type=float)
    ap.add_argument("--out", default="film.mp4")
    ap.add_argument("--audio")
    ap.add_argument("--warp")
    ap.add_argument("--labels", action="store_true")
    ap.add_argument("--every", type=float, default=1.5)
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()
    scene = load_scene(a.scene)
    D = scene.__dir__
    W, H, FPS, DUR = scene.W, scene.H, scene.FPS, scene.DUR
    to_story, _ = warp_fn(json.load(open(a.warp)) if a.warp else None)

    if a.mode == "stills":
        for t in a.times:
            imwrite(D / f"still_{t:05.2f}.png", frame_at(scene, t, a.labels))
            print("still", t, flush=True)
        return
    if a.mode == "sheet":
        ts = list(np.arange(0.5, DUR, a.every))
        tiles = [cv2.resize(frame_at(scene, t, True), (480, int(480 * H / W))) for t in ts]
        while len(tiles) % 4:
            tiles.append(np.zeros_like(tiles[0]))
        imwrite(D / "sheet.png", np.vstack([np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]))
        print("sheet.png", len(ts), "frames")
        return

    out = D / a.out
    cmd = [config.ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if a.audio:
        cmd += ["-i", str(D / a.audio), "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total, t0 = int(round(FPS * DUR)), time.time()
    for i in range(total):
        tv = i / FPS
        fr = frame_at(scene, to_story(tv), a.labels, display_t=tv)
        ff.stdin.write(fr.tobytes())
        try:      # 进度文件只是给预览看的；同一目录里并行渲多条片子时会互相占用，写不进去就跳过，别让渲染中断
            if i % 6 == 0 or i == total - 1:
                el = time.time() - t0
                json.dump({"out": out.name, "frame": i + 1, "total": total, "elapsed": round(el, 1),
                           "eta": round(el / (i + 1) * (total - i - 1), 1), "t": round(tv, 2)}, open(D / "progress.json", "w"))
            if i % 12 == 0:
                imwrite(D / "latest.jpg", cv2.resize(fr, (960, int(960 * H / W))), [cv2.IMWRITE_JPEG_QUALITY, 80])
        except OSError:
            pass
        if i % (FPS * 2) == 0:
            print(f"frame {i}/{total}  {time.time() - t0:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", out, ff.returncode)


if __name__ == "__main__":
    main()
