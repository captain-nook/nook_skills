#!/usr/bin/env python

from __future__ import annotations

import argparse
import base64
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def export_sample(brief: Path, output_dir: Path) -> tuple[Path, Path]:
    script = ROOT / "scripts" / "render-xhs-route-sample.cjs"
    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["node", str(script), str(brief.resolve()), "--stdout-base64"],
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    payload = json.loads(result.stdout)
    html_path = output_dir / "index.html"
    png_path = output_dir / "cover.png"
    html_path.write_text(base64.b64decode(payload["html_base64"]).decode("utf-8"), encoding="utf-8")
    png_path.write_bytes(base64.b64decode(payload["png_base64"]))
    return html_path, png_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("brief", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
      html_path, png_path = export_sample(args.brief, args.output_dir)
      print(f"HTML={html_path}")
      print(f"PNG={png_path}")
      return 0
    except Exception as exc:
      print(f"ERROR={exc}")
      return 1


if __name__ == "__main__":
    raise SystemExit(main())
