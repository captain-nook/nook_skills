#!/usr/bin/env python3
"""Create deterministic technical-QC evidence for one H3 video output."""

from __future__ import annotations

import argparse
import json
import math
import wave
from pathlib import Path

try:
    import av
    import numpy as np
    from PIL import Image, ImageDraw, ImageOps
except ImportError as exc:  # pragma: no cover - environment-specific
    raise SystemExit(
        "prepare_h3_qc.py requires PyAV, NumPy, and Pillow in the selected Python environment"
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--expected-duration", type=float, default=0.0)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=9)
    return parser.parse_args()


def mean_difference(first: Image.Image, second: Image.Image, crop: tuple[int, int, int, int]) -> float:
    a = np.asarray(first.crop(crop).resize((320, 180))).astype(np.float32)
    b = np.asarray(second.crop(crop).resize((320, 180))).astype(np.float32)
    return float(np.mean(np.abs(a - b)))


def extract_audio_wav(video_path: Path, output_path: Path) -> bool:
    container = av.open(str(video_path))
    if not container.streams.audio:
        container.close()
        return False
    resampler = av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=16000)
    chunks: list[bytes] = []
    for frame in container.decode(audio=0):
        outputs = resampler.resample(frame)
        if outputs is None:
            continue
        if not isinstance(outputs, list):
            outputs = [outputs]
        for output in outputs:
            chunks.append(bytes(output.planes[0]))
    container.close()
    if not chunks:
        return False
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"".join(chunks))
    return True


def main() -> None:
    args = parse_args()
    video_path = args.video.resolve(strict=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    container = av.open(str(video_path))
    video_stream = container.streams.video[0]
    frames = [frame.to_image().convert("RGB") for frame in container.decode(video=0)]
    fps = float(video_stream.average_rate) if video_stream.average_rate else 0.0
    duration = len(frames) / fps if fps else 0.0
    container.close()
    if not frames:
        raise SystemExit("video contains no decodable frames")

    sample_count = max(2, min(args.samples, len(frames)))
    indices = sorted(
        {round(i * (len(frames) - 1) / (sample_count - 1)) for i in range(sample_count)}
    )
    selected = [frames[index] for index in indices]
    thumbs: list[Image.Image] = []
    for index, frame in zip(indices, selected):
        thumb = ImageOps.fit(frame, (480, 270), method=Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(thumb)
        draw.rectangle((0, 0, 130, 25), fill=(0, 0, 0))
        draw.text((6, 5), f"frame {index}", fill=(255, 255, 255))
        thumbs.append(thumb)

    columns = 3
    rows = math.ceil(len(thumbs) / columns)
    contact = Image.new("RGB", (columns * 480, rows * 270), (20, 20, 20))
    for position, thumb in enumerate(thumbs):
        contact.paste(thumb, ((position % columns) * 480, (position // columns) * 270))
    contact_path = args.output_dir / "contact_sheet.jpg"
    contact.save(contact_path, quality=92)

    width, height = selected[0].size
    full_diffs: list[float] = []
    top_diffs: list[float] = []
    bottom_diffs: list[float] = []
    for first, second in zip(selected, selected[1:]):
        full_diffs.append(mean_difference(first, second, (0, 0, width, height)))
        top_diffs.append(mean_difference(first, second, (0, 0, width, height // 2)))
        bottom_diffs.append(mean_difference(first, second, (0, height // 2, width, height)))

    container = av.open(str(video_path))
    audio_streams = list(container.streams.audio)
    audio_rms: list[float] = []
    if audio_streams:
        for audio_frame in container.decode(audio=0):
            samples = audio_frame.to_ndarray().astype(np.float32)
            if samples.size:
                audio_rms.append(float(np.sqrt(np.mean(samples * samples))))
    container.close()

    audio_path = args.output_dir / "audio.wav"
    audio_exported = extract_audio_wav(video_path, audio_path)

    duration_tolerance = max(0.75, args.expected_duration * 0.15)
    duration_pass = (
        args.expected_duration <= 0
        or abs(duration - args.expected_duration) <= duration_tolerance
    )
    aspect_ratio = video_stream.width / video_stream.height
    report = {
        "shot_id": args.shot_id,
        "video": str(video_path),
        "bytes": video_path.stat().st_size,
        "width": video_stream.width,
        "height": video_stream.height,
        "aspect_ratio": aspect_ratio,
        "aspect_16_9_pass": abs(aspect_ratio - 16 / 9) < 0.04,
        "fps": fps,
        "decoded_frames": len(frames),
        "duration_seconds": duration,
        "expected_duration_seconds": args.expected_duration,
        "duration_pass": duration_pass,
        "audio_streams": len(audio_streams),
        "audio_rms_mean": float(np.mean(audio_rms)) if audio_rms else 0.0,
        "audio_wav": str(audio_path) if audio_exported else None,
        "sample_indices": indices,
        "sample_full_diff_mean": float(np.mean(full_diffs)),
        "sample_top_diff_mean": float(np.mean(top_diffs)),
        "sample_bottom_diff_mean": float(np.mean(bottom_diffs)),
        "contact_sheet": str(contact_path),
        "technical_pass": bool(duration_pass and abs(aspect_ratio - 16 / 9) < 0.04),
        "semantic_qc_required": True,
    }
    report_path = args.output_dir / "technical_qc.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
