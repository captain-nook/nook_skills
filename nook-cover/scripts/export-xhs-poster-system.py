#!/usr/bin/env python

from __future__ import annotations

import argparse
import base64
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def render_one(cases_file: Path, case_id: str, out_dir: Path) -> tuple[Path, Path]:
    script = ROOT / "scripts" / "render-xhs-poster-system.cjs"
    result = subprocess.run(
        ["node", str(script), str(cases_file.resolve()), case_id],
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    payload = json.loads(result.stdout)
    item_dir = out_dir / payload["id"]
    item_dir.mkdir(parents=True, exist_ok=True)
    html = base64.b64decode(payload["html_base64"]).decode("utf-8")
    png = base64.b64decode(payload["png_base64"])
    html_path = item_dir / "index.html"
    png_path = item_dir / "cover.png"
    html_path.write_text(html, encoding="utf-8")
    png_path.write_bytes(png)
    return html_path, png_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases_file", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--case-id")
    args = parser.parse_args()
    data = json.loads(args.cases_file.read_text(encoding="utf-8"))
    ids = [args.case_id] if args.case_id else [item["id"] for item in data["cases"]]
    for case_id in ids:
        html_path, png_path = render_one(args.cases_file, case_id, args.output_dir)
        print(f"{case_id}: HTML={html_path}")
        print(f"{case_id}: PNG={png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
