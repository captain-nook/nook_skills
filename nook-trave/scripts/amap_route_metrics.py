#!/usr/bin/env python3
"""Fetch Amap driving metrics for a route skeleton."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

AMAP_DRIVING_URL = "https://restapi.amap.com/v3/direction/driving"

CITY_COORDS = {
    "成都": "104.066541,30.572269",
    "兰州": "103.834303,36.061089",
    "天水": "105.724947,34.580863",
    "张掖": "100.449818,38.925875",
    "嘉峪关": "98.289152,39.773130",
    "敦煌": "94.661967,40.142128",
    "哈密": "93.514916,42.818501",
    "吐鲁番": "89.189655,42.951384",
    "乌鲁木齐": "87.616824,43.825377",
    "赛里木湖": "81.184590,44.602001",
    "博乐": "82.072237,44.912870",
    "伊宁": "81.277715,43.908021",
    "昭苏": "81.130974,43.157293",
    "特克斯": "81.840058,43.214861",
    "那拉提": "83.258493,43.312347",
    "巴音布鲁克": "84.148993,43.032846",
    "库车": "82.962016,41.717906",
    "阿克苏": "80.265068,41.170712",
    "喀什": "75.989138,39.467664",
    "塔什库尔干": "75.228068,37.775437",
    "和田": "79.922211,37.114157",
    "民丰": "82.695862,37.064080",
    "且末": "85.529619,38.145749",
    "若羌": "88.168807,39.023807",
    "茫崖": "90.856429,38.247513",
    "花土沟": "90.858685,38.254424",
    "德令哈": "97.361528,37.369865",
    "青海湖": "100.170651,36.895671",
    "西宁": "101.778916,36.623178",
    "陇南": "104.921841,33.400684"
}


def pick_name(value: str) -> str | None:
    if not value or value == "机动":
        return None
    parts = value.split("/")
    return parts[0].strip()


def coord_for(value: str) -> str | None:
    name = pick_name(value)
    if not name:
        return None
    return CITY_COORDS.get(name)


def fetch_metric(origin: str, destination: str, key: str) -> dict:
    params = {
        "origin": origin,
        "destination": destination,
        "strategy": "0",
        "extensions": "base",
        "output": "JSON",
        "key": key,
    }
    url = AMAP_DRIVING_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("status") != "1":
        return {"status": "needs_recheck", "amap_status": payload.get("status"), "info": payload.get("info"), "infocode": payload.get("infocode")}
    route = payload.get("route", {})
    paths = route.get("paths") or []
    if not paths:
        return {"status": "needs_recheck", "info": "no paths returned"}
    path = paths[0]
    distance_m = int(path.get("distance", 0) or 0)
    duration_s = int(path.get("duration", 0) or 0)
    return {
        "status": "verified_by_amap",
        "distance_km": round(distance_m / 1000, 1),
        "duration_hours": round(duration_s / 3600, 1),
        "duration_text": f"{duration_s // 3600}h{(duration_s % 3600) // 60:02d}m",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Amap driving distance/duration for route days.")
    parser.add_argument("--route", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--key", default=os.environ.get("AMAP_WEB_SERVICE_KEY"))
    parser.add_argument("--limit", type=int, default=0, help="Optional number of drive days to process for smoke testing.")
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()
    if not args.key:
        raise SystemExit("Missing Amap key. Set AMAP_WEB_SERVICE_KEY or pass --key.")

    data = json.loads(args.route.read_text(encoding="utf-8-sig"))
    results = []
    processed = 0
    for day in data.get("days", []):
        start_coord = coord_for(day.get("start"))
        end_coord = coord_for(day.get("end"))
        result = {
            "day": day.get("day"),
            "date": day.get("date"),
            "start": day.get("start"),
            "end": day.get("end"),
            "theme": day.get("theme"),
        }
        if not start_coord or not end_coord or start_coord == end_coord:
            result.update({"status": "skipped", "reason": "rest day, flexible day, or unknown coordinate"})
        else:
            result.update(fetch_metric(start_coord, end_coord, args.key))
            processed += 1
            if args.limit and processed >= args.limit:
                results.append(result)
                break
            time.sleep(args.sleep)
        results.append(result)

    output = {
        "source_route": str(args.route),
        "provider": "amap_direction_driving",
        "verification": "distances and durations are API estimates; still recheck before departure",
        "days": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())