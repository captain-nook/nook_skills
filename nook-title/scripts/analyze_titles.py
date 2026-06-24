#!/usr/bin/env python3
"""Analyze Chinese AI-media title surface features.

Input: a UTF-8 text file with one title per line.
Output: JSON stats plus per-title feature rows.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

EN_RE = re.compile(r"[A-Za-z][A-Za-z0-9.+_-]*")
NUM_RE = re.compile(r"\d+(?:\.\d+)?%?|\d+\s*[万亿千百]?")


def display_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text.strip()))


def features(title: str) -> dict:
    return {
        "title": title,
        "length": display_len(title),
        "has_bang": "!" in title or "！" in title,
        "has_comma": "," in title or "，" in title,
        "has_question": "?" in title or "？" in title,
        "has_number": bool(NUM_RE.search(title)),
        "has_english": bool(EN_RE.search(title)),
        "english_terms": EN_RE.findall(title),
        "numbers": NUM_RE.findall(title),
    }


def pct(rows: list[dict], key: str) -> float:
    if not rows:
        return 0.0
    return round(sum(1 for row in rows if row[key]) / len(rows) * 100, 1)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, help="UTF-8 file with one title per line")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    titles = [
        line.strip().lstrip("\ufeff")
        for line in args.file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rows = [features(title) for title in titles]
    lengths = [row["length"] for row in rows]
    stats = {
        "count": len(rows),
        "median_length": statistics.median(lengths) if lengths else 0,
        "mean_length": round(statistics.mean(lengths), 1) if lengths else 0,
        "bang_rate": pct(rows, "has_bang"),
        "comma_rate": pct(rows, "has_comma"),
        "question_rate": pct(rows, "has_question"),
        "number_rate": pct(rows, "has_number"),
        "english_rate": pct(rows, "has_english"),
    }
    result = {"stats": stats, "titles": rows}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
