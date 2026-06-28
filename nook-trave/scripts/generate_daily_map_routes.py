#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def pick(value: str | None) -> str | None:
    if not value or value == "机动":
        return None
    return value.split("/")[0].strip()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", required=True, type=Path)
    parser.add_argument("--coords", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    route = json.loads(args.route.read_text(encoding="utf-8-sig"))
    coords = json.loads(args.coords.read_text(encoding="utf-8-sig"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    skipped = []
    for day in route.get("days", []):
        start = pick(day.get("start"))
        end = pick(day.get("end"))
        if not start or not end or start == end or start not in coords or end not in coords:
            skipped.append({"day": day.get("day"), "start": day.get("start"), "end": day.get("end")})
            continue
        points = [{"name": start, "location": coords[start]}]
        for via in day.get("via", []) or []:
            if via in coords:
                points.append({"name": via, "location": coords[via]})
        points.append({"name": end, "location": coords[end]})
        data = {"title": f"Day {day.get('day'):02d} {start} to {end}", "size": "1024*768", "points": points}
        (args.out_dir / f"day-{day.get('day'):02d}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        count += 1
    print(f"generated={count} skipped={len(skipped)}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())