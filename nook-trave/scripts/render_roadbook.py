#!/usr/bin/env python3
"""Render a vertical mobile-first travel roadbook HTML from JSON data."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def esc(value) -> str:
    return html.escape(str(value or ""), quote=True)


def p(text: str) -> str:
    return f"<p>{esc(text)}</p>" if text else ""


def render_cover(data: dict) -> str:
    trip = data.get("trip", {})
    stats = trip.get("stats", [])
    stats_html = "".join(
        f"<div class=\"stat\"><b>{esc(item.get('value'))}</b><span>{esc(item.get('label'))}</span></div>"
        for item in stats[:4]
    )
    return f"""
    <section class="page cover">
      <img src="{esc(trip.get('cover_image', 'assets/cover.jpg'))}" alt="{esc(trip.get('cover_alt', 'roadbook cover'))}" />
      <div class="cover-content">
        <header class="masthead"><div class="brand">{esc(trip.get('brand', 'Nook Trave'))}</div><div class="issue">{esc(trip.get('issue', 'Roadbook')).replace(chr(10), '<br />')}</div></header>
        <div><div class="kicker">{esc(trip.get('kicker'))}</div><h1>{esc(trip.get('title')).replace(chr(10), '<br />')}</h1><div class="subtitle">{esc(trip.get('subtitle'))}</div></div>
        <div class="cover-stats">{stats_html}</div>
      </div>
    </section>
    """


def render_overview(data: dict) -> str:
    overview = data.get("overview", {})
    metrics = "".join(
        f"<div class=\"info\"><span>{esc(item.get('label'))}</span><b>{esc(item.get('value'))}</b>{p(item.get('note', ''))}</div>"
        for item in overview.get("metrics", [])
    )
    route_items = "".join(
        f"<div class=\"list-item\"><div class=\"num\">{idx:02d}</div><div><b>{esc(item.get('title'))}</b><br />{esc(item.get('text'))}</div></div>"
        for idx, item in enumerate(overview.get("route_spine", []), 1)
    )
    map_html = ""
    if overview.get("map_image"):
        map_html = f"<img class=\"photo\" style=\"height:360px;border:1px solid var(--line);margin:14px 0 0\" src=\"{esc(overview.get('map_image'))}\" alt=\"{esc(overview.get('map_alt', 'route overview map'))}\" />"
    return f"""
    <section class="page"><div class="content">
      <div class="head"><div><div class="label">Overview</div><h2>{esc(overview.get('title', '整体行程'))}</h2></div><div class="folio">01</div></div>
      <p class="lead">{esc(overview.get('lead'))}</p>
      <div class="grid2">{metrics}</div>
      <div class="list" style="margin-top:16px">{route_items}</div>
      {map_html}
      <p class="map-note">{esc(overview.get('map_note', '路线图和公里数必须通过地图工具核验。'))}</p>
    </div></section>
    """


def render_day(day: dict, index: int) -> str:
    chips = "".join(f"<span class=\"chip\">{esc(chip)}</span>" for chip in day.get("chips", []))
    facts = "".join(
        f"<div class=\"fact\"><b>{esc(item.get('value'))}</b><span>{esc(item.get('label'))}</span></div>"
        for item in day.get("facts", [])[:4]
    )
    timeline = "".join(
        f"<div class=\"time-row\"><div class=\"time\">{esc(item.get('time'))}</div><div><b>{esc(item.get('title'))}</b><br />{esc(item.get('text'))}</div></div>"
        for item in day.get("timeline", [])
    )
    day_map_html = ""
    if day.get("map_image"):
        day_map_html = f"<div class=\"content\" style=\"padding-top:16px;padding-bottom:0\"><img class=\"photo\" style=\"height:300px;border:1px solid var(--line)\" src=\"{esc(day.get('map_image'))}\" alt=\"{esc(day.get('map_alt', 'daily route map'))}\" /><p class=\"map-note\">{esc(day.get('map_note', '高德静态路线图，正式导航以高德 App 为准。'))}</p></div>"
    hotel = day.get("hotel", {})
    note = ""
    if hotel:
        note = f"<div class=\"note\"><h4>住宿候选</h4><p>{esc(hotel.get('text'))}</p></div>"
    return f"""
    <section class="page">
      <img class="photo" src="{esc(day.get('image', 'assets/day-placeholder.jpg'))}" alt="{esc(day.get('image_alt', day.get('title', 'day image')))}" />
      <div class="caption">Day {esc(day.get('day_no', index))} · {esc(day.get('caption', 'Daily Plan'))}</div>
      <div class="day-title"><div class="label">Day {esc(day.get('day_no', index))}</div><h3>{esc(day.get('title'))}</h3><p>{esc(day.get('summary'))}</p><div class="chips">{chips}</div></div>
      <div class="facts">{facts}</div>
      {day_map_html}
      <div class="timeline">{timeline}</div>
      {note}
    </section>
    """


def render_appendix(data: dict) -> str:
    appendix = data.get("appendix", {})
    items = "".join(
        f"<div class=\"list-item\"><div class=\"num\">{esc(item.get('label'))}</div><div>{esc(item.get('text'))}</div></div>"
        for item in appendix.get("items", [])
    )
    return f"""
    <section class="page"><div class="content">
      <div class="head"><div><div class="label">Appendix</div><h2>{esc(appendix.get('title', '出发前清单'))}</h2></div><div class="folio">{esc(appendix.get('folio', '99'))}</div></div>
      <div class="list">{items}</div>
    </div><div class="footer">{esc(appendix.get('footer', '真实出行前必须重新核验路线、天气、酒店、电话和路况。'))}</div></section>
    """


def render(data: dict, template: str) -> str:
    days = "".join(render_day(day, idx) for idx, day in enumerate(data.get("days", []), 1))
    return (
        template.replace("{{TITLE}}", esc(data.get("trip", {}).get("title", "旅行路书")))
        .replace("{{COVER}}", render_cover(data))
        .replace("{{OVERVIEW}}", render_overview(data))
        .replace("{{DAYS}}", days)
        .replace("{{APPENDIX}}", render_appendix(data))
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Nook Trave vertical roadbook HTML.")
    parser.add_argument("--data", required=True, help="Path to roadbook JSON data")
    parser.add_argument("--template", required=True, help="Path to template.html")
    parser.add_argument("--out", required=True, help="Output HTML path")
    args = parser.parse_args()

    data_path = Path(args.data)
    template_path = Path(args.template)
    out_path = Path(args.out)
    data = json.loads(data_path.read_text(encoding="utf-8-sig"))
    template = template_path.read_text(encoding="utf-8")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(data, template), encoding="utf-8")
    print(f"Rendered {out_path}")


if __name__ == "__main__":
    main()

