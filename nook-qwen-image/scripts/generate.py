#!/usr/bin/env python
"""nook-qwen-image CLI: ModelScope Qwen-Image text-to-image."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip().lstrip("\ufeff")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def parse_size(value: str) -> Tuple[int, int]:
    match = re.fullmatch(r"\s*(\d{2,5})\s*[xX*]\s*(\d{2,5})\s*", value or "")
    if not match:
        raise ValueError("size must look like 1024x1024 or 720*1280")
    width, height = int(match.group(1)), int(match.group(2))
    if width < 128 or height < 128 or width > 4096 or height > 4096:
        raise ValueError("size width/height must be between 128 and 4096")
    return width, height


def http_json(url: str, method: str, headers: dict, payload: Optional[dict] = None, timeout: int = 60) -> dict:
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body[:500]}") from exc
    except URLError as exc:
        raise RuntimeError(f"request failed: {exc}") from exc


def download(url: str, output: Path, timeout: int = 60) -> None:
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=timeout) as resp:
            output.write_bytes(resp.read())
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"image download HTTP {exc.code}: {body[:300]}") from exc
    except URLError as exc:
        raise RuntimeError(f"image download failed: {exc}") from exc


def write_dry_run_png(output: Path) -> None:
    png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    output.write_bytes(base64.b64decode(png))


def generate_image(prompt: str, size: str, output_file: Optional[str] = None, timeout: int = 600) -> str:
    load_env(ROOT / ".env")

    width, height = parse_size(size)
    output_dir = Path(os.getenv("QWEN_IMAGE_OUTPUT_DIR", str(ROOT / "output")))
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if output_file:
        output = Path(output_file)
        if not output.is_absolute():
            output = Path.cwd() / output
    else:
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        output = output_dir / f"qwen_image_{stamp}.jpg"
    output.parent.mkdir(parents=True, exist_ok=True)

    if os.getenv("QWEN_IMAGE_DRY_RUN", "").lower() == "true":
        write_dry_run_png(output.with_suffix(".png"))
        return str(output.with_suffix(".png"))

    api_key = os.getenv("MS_API_KEY", "")
    if not api_key:
        raise RuntimeError("MS_API_KEY is required. Run node setup.js or create .env.")

    base_url = os.getenv("MS_API_BASE_URL", "https://api-inference.modelscope.cn").rstrip("/")
    model = os.getenv("MS_IMAGE_MODEL", "Qwen/Qwen-Image")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-ModelScope-Async-Mode": "true",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "size": f"{width}x{height}",
        "width": width,
        "height": height,
        "parameters": {
            "size": f"{width}x{height}",
            "prompt_extend": True,
        },
    }

    print(f"nook-qwen-image: submitting {width}x{height} image task")
    submitted = http_json(f"{base_url}/v1/images/generations", "POST", headers, payload)
    task_id = submitted.get("task_id")
    if not task_id:
        raise RuntimeError(f"ModelScope response did not include task_id: {submitted}")

    started = time.time()
    poll_headers = {
        "Authorization": f"Bearer {api_key}",
        "X-ModelScope-Task-Type": "image_generation",
    }
    while True:
        if time.time() - started > timeout:
            raise RuntimeError(f"timed out waiting for task {task_id}")
        data = http_json(f"{base_url}/v1/tasks/{task_id}", "GET", poll_headers)
        status = data.get("task_status")
        if status == "SUCCEED":
            images = data.get("output_images") or []
            if not images:
                raise RuntimeError(f"task succeeded but output_images is empty: {data}")
            image_url = images[0].get("url") if isinstance(images[0], dict) else images[0]
            if not image_url:
                raise RuntimeError(f"task output did not include image URL: {data}")
            download(image_url, output)
            return str(output)
        if status == "FAILED":
            raise RuntimeError(data.get("message") or f"task {task_id} failed")
        time.sleep(3)


def main() -> int:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Generate an image with ModelScope Qwen-Image.")
    parser.add_argument("prompt", help="Text prompt")
    parser.add_argument("--size", default="1080x1440", help="Image size, e.g. 1024x1024 or 720*1280")
    parser.add_argument("--output", default=None, help="Output image path")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout seconds")
    args = parser.parse_args()

    try:
        path = generate_image(args.prompt, args.size, args.output, args.timeout)
        print(f"OUTPUT_PATH={path}")
        return 0
    except Exception as exc:
        print(f"ERROR={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
