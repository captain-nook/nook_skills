#!/usr/bin/env python

from __future__ import annotations

import argparse
import base64
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def render_one(cases_file: Path, case_id: str, out_dir: Path, save_html: bool) -> Path:
    script = ROOT / "scripts" / "render-xhs-poster-v04.cjs"
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
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / payload["output_name"]
    png_path.write_bytes(base64.b64decode(payload["png_base64"]))
    if save_html:
        html_dir = out_dir / "html"
        html_dir.mkdir(parents=True, exist_ok=True)
        html = base64.b64decode(payload["html_base64"]).decode("utf-8")
        (html_dir / payload["html_name"]).write_text(html, encoding="utf-8")
    return png_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases_file", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--case-id")
    parser.add_argument("--no-html", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.cases_file.read_text(encoding="utf-8"))
    ids = [args.case_id] if args.case_id else [item["id"] for item in data["cases"]]
    for case_id in ids:
        png_path = render_one(args.cases_file, case_id, args.output_dir, save_html=not args.no_html)
        print(f"{case_id}: PNG={png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
