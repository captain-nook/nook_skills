#!/usr/bin/env python3
"""Build Amap static map URLs and optionally download route overview/day images."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

AMAP_STATIC_MAP_URL = "https://restapi.amap.com/v3/staticmap"
DEFAULT_SIZE = "1024*768"
DEFAULT_ZOOM = "5"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_lnglat(location: str) -> tuple[float, float]:
    lng, lat = location.split(",", 1)
    return float(lng), float(lat)


def infer_center(points: list[dict]) -> str:
    lngs, lats = [], []
    for point in points:
        lng, lat = parse_lnglat(point["location"])
        lngs.append(lng)
        lats.append(lat)
    return f"{sum(lngs) / len(lngs):.6f},{sum(lats) / len(lats):.6f}"


def infer_zoom(points: list[dict]) -> str:
    if len(points) < 2:
        return DEFAULT_ZOOM
    coords = [parse_lnglat(point["location"]) for point in points]
    span = max(max(lng for lng, _ in coords) - min(lng for lng, _ in coords), max(lat for _, lat in coords) - min(lat for _, lat in coords))
    if span >= 12:
        return "4"
    if span >= 6:
        return "5"
    if span >= 3:
        return "6"
    if span >= 1:
        return "7"
    return "8"


def encode_markers(points: list[dict], limit: int = 6) -> str:
    markers = []
    for index, point in enumerate(points[:limit], start=1):
        location = point["location"]
        markers.append(f"mid,,{index}:{location}")
    return "|".join(markers)


def encode_paths(points: list[dict]) -> str:
    locations = ";".join(point["location"] for point in points)
    return f"5,0x2563EB,1,,:{locations}"


def data_from_points(points_text: str) -> dict:
    points = []
    for raw in points_text.split(";"):
        if not raw.strip():
            continue
        name, location = raw.split("=", 1)
        points.append({"name": name.strip(), "location": location.strip()})
    return {"points": points, "size": DEFAULT_SIZE}


def build_url(data: dict, key: str | None) -> str:
    points = data.get("points", [])
    if len(points) < 2:
        raise ValueError("At least two points are required")

    params = {
        "size": data.get("size", DEFAULT_SIZE),
        "zoom": str(data.get("zoom") or infer_zoom(points)),
        "location": data.get("center") or data.get("location") or infer_center(points),
        "paths": encode_paths(points),
        "markers": encode_markers(points, int(data.get("marker_limit", 6))),
    }
    if key:
        params["key"] = key
    return AMAP_STATIC_MAP_URL + "?" + urllib.parse.urlencode(params, safe=":,;|*")


def download(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=30) as response:
        content_type = response.headers.get("Content-Type", "")
        content = response.read()
    if b'"status"' in content[:200] and b'"info"' in content[:200]:
        raise RuntimeError(content.decode("utf-8", errors="replace"))
    out.write_bytes(content)
    print(f"Saved: {out}")
    if content_type:
        print(f"Content-Type: {content_type}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an Amap static map URL from route points.")
    parser.add_argument("--data", type=Path, help="Route JSON with point names and lng,lat locations.")
    parser.add_argument("--points", help="Inline route points, format: name=lng,lat;name=lng,lat")
    parser.add_argument("--out", type=Path, help="Optional image output path. Requires AMAP_WEB_SERVICE_KEY or --key.")
    parser.add_argument("--key", help="Amap Web Service API key. Defaults to AMAP_WEB_SERVICE_KEY env var.")
    parser.add_argument("--print-url", action="store_true", help="Print the static map URL.")
    args = parser.parse_args()

    if args.points:
        data = data_from_points(args.points)
    elif args.data:
        data = load_json(args.data)
    else:
        parser.error("Either --data or --points is required")

    key = args.key or os.environ.get("AMAP_WEB_SERVICE_KEY")
    url = build_url(data, key)

    if args.print_url or not args.out:
        print(url)

    if args.out:
        if not key:
            print("No Amap key found. Set AMAP_WEB_SERVICE_KEY or pass --key to download the map image.", file=sys.stderr)
            return 2
        download(url, args.out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())