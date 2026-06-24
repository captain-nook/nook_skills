#!/usr/bin/env python3
"""Score candidate Chinese AI-media titles for surface strength.

This script checks title-form features only. It cannot verify factual truth.
Input: UTF-8 text file with one candidate title per line.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EN_RE = re.compile(r"[A-Za-z][A-Za-z0-9.+_-]*")
NUM_RE = re.compile(r"\d+(?:\.\d+)?%?|\d+\s*[万亿千百]?")
HYPE_RE = re.compile(r"炸|逆天|碾压|吊打|暴锤|狂飙|打骨折|成精|变天|封神|登顶")
BOUNDARY_RE = re.compile(r"传言|被曝|内测|疑似|或将|可能|据称|爆料|论文称|官方称")
RISK_RE = re.compile(r"彻底|全网|所有|没人|完美|必然|颠覆一切|取代人类|人类多余")


def display_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text.strip()))


def score(title: str) -> dict:
    length = display_len(title)
    numbers = NUM_RE.findall(title)
    english = EN_RE.findall(title)
    has_bang = "!" in title or "！" in title
    has_comma = "," in title or "，" in title
    has_hype = bool(HYPE_RE.search(title))
    has_boundary = bool(BOUNDARY_RE.search(title))
    risks = RISK_RE.findall(title)

    points = 0
    notes: list[str] = []

    if 28 <= length <= 42:
        points += 2
    elif 20 <= length < 28 or 42 < length <= 52:
        points += 1
    else:
        notes.append("length_outside_preferred_range")

    if english:
        points += 2
    else:
        notes.append("no_english_entity")

    if numbers:
        points += 2
    else:
        notes.append("no_numeric_hook")

    if has_bang:
        points += 1
    if has_comma:
        points += 1
    if has_hype:
        points += 1
    if has_boundary:
        points += 1
    if risks:
        points -= 2
        notes.append("overclaim_risk:" + ",".join(sorted(set(risks))))
    if has_hype and not numbers and not english:
        points -= 2
        notes.append("hype_without_concrete_anchor")

    return {
        "title": title,
        "score": max(points, 0),
        "length": length,
        "numbers": numbers,
        "english_terms": english,
        "has_bang": has_bang,
        "has_comma": has_comma,
        "has_boundary": has_boundary,
        "notes": notes,
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, help="UTF-8 file with one title per line")
    args = parser.parse_args()

    titles = [
        line.strip().lstrip("\ufeff")
        for line in args.file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rows = sorted((score(title) for title in titles), key=lambda row: row["score"], reverse=True)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
