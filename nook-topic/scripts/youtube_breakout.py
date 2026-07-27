#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""YouTube 低粉爆款筛选器 —— B站版的对照通道，判据相同（播粉比）。

为什么必须走官方 Data API 而不是 yt-dlp：
  yt-dlp --flat-playlist  → 有 view_count，但**没有订阅数**，算不出播粉比
  yt-dlp 完整模式          → 有 channel_follower_count，但被 "Sign in to confirm
                             you're not a bot" 挡死（2026-07 实测）
Data API v3 免费额度 10,000 units/天，够用：
  search.list   100 units/次  ← 大头，一次搜索
  videos.list     1 unit/次   ← 批量取统计（一次最多 50 个 id）
  channels.list   1 unit/次   ← 批量取订阅数（一次最多 50 个 id）
即约 95 次搜索/天。批量接口是省额度的关键，别改成逐个查。

key 来源：环境变量 YOUTUBE_API_KEY，或 scripts/.env 文件。免费额度 10000 units/天。
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from typing import Any

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import load_key, item_skeleton  # noqa: E402

# Windows 控制台默认 GBK，中文和 emoji 会 UnicodeEncodeError 崩掉整个脚本。
# AGENT_SCHEMA §1.1 要求显式 UTF-8。260727 由 validate_skills.py 批量补齐。
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    if _s and _s.encoding and _s.encoding.lower() not in {"utf-8", "utf8"}:
        _s.reconfigure(encoding="utf-8")

API = "https://www.googleapis.com/youtube/v3"

DEFAULT_MAX_SUBS = 50_000
DEFAULT_MIN_VIEWS = 50_000
DEFAULT_MIN_RATIO = 3.0
# 见 bili_breakout 同名常量的说明：刚发布的视频数据未稳定，会变成伪反面证据；
# 太老的靠时间堆播放量，不反映当下供给格局。
DEFAULT_MIN_AGE_DAYS = 3
DEFAULT_MAX_AGE_DAYS = 180


def _get(endpoint: str, params: dict[str, str]) -> dict[str, Any]:
    url = f"{API}/{endpoint}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _chunked(seq: list[str], size: int = 50):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def find_breakouts(query: str, *, api_key: str, max_results: int = 50,
                   max_subs: int = DEFAULT_MAX_SUBS, min_views: int = DEFAULT_MIN_VIEWS,
                   min_ratio: float = DEFAULT_MIN_RATIO, min_likes: int = 0,
                   min_comments: int = 0, region: str = "",
                   min_age_days: float = DEFAULT_MIN_AGE_DAYS,
                   max_age_days: float = DEFAULT_MAX_AGE_DAYS,
                   ) -> tuple[list[dict[str, Any]], list[str]]:
    import datetime as _dt
    errors: list[str] = []
    now = _dt.datetime.now(_dt.timezone.utc)
    params = {
        "part": "snippet", "q": query, "type": "video",
        "maxResults": str(min(max_results, 50)), "key": api_key,
        # 时间窗直接下推给 API，省额度也省得捞回来再扔
        "publishedAfter": (now - _dt.timedelta(days=max_age_days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "publishedBefore": (now - _dt.timedelta(days=min_age_days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if region:
        params["regionCode"] = region
    try:
        found = _get("search", params)
    except Exception as exc:  # noqa: BLE001
        return [], [f"youtube search failed: {exc}"]

    vids = [it["id"]["videoId"] for it in found.get("items", []) if it.get("id", {}).get("videoId")]
    if not vids:
        return [], ["no videos returned"]

    # 批量取视频统计
    stats: dict[str, dict[str, Any]] = {}
    for chunk in _chunked(vids):
        try:
            data = _get("videos", {"part": "statistics,snippet,contentDetails",
                                   "id": ",".join(chunk), "key": api_key})
        except Exception as exc:  # noqa: BLE001
            errors.append(f"videos.list failed: {exc}")
            continue
        for it in data.get("items", []):
            stats[it["id"]] = it

    # 批量取频道订阅数（先去重，同一频道常有多条视频）
    ch_ids = list({v["snippet"]["channelId"] for v in stats.values() if v.get("snippet")})
    subs: dict[str, int] = {}
    for chunk in _chunked(ch_ids):
        try:
            data = _get("channels", {"part": "statistics", "id": ",".join(chunk), "key": api_key})
        except Exception as exc:  # noqa: BLE001
            errors.append(f"channels.list failed: {exc}")
            continue
        for it in data.get("items", []):
            raw = it.get("statistics", {}).get("subscriberCount")
            if raw is not None:
                subs[it["id"]] = int(raw)

    hits: list[dict[str, Any]] = []
    for vid, v in stats.items():
        st, sn = v.get("statistics", {}), v.get("snippet", {})
        views = int(st.get("viewCount") or 0)
        likes = int(st.get("likeCount") or 0)
        comments = int(st.get("commentCount") or 0)
        if views < min_views or likes < min_likes or comments < min_comments:
            continue
        # 订阅数隐藏的频道（YouTube 允许）拿不到分母，无法判断是否低粉，跳过而不是当 0
        sub = subs.get(sn.get("channelId", ""))
        if sub is None or sub > max_subs:
            continue
        pub = sn.get("publishedAt")
        if not pub:
            continue
        age = (now - _dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))).total_seconds() / 86400
        if age < min_age_days or age > max_age_days:
            continue
        ratio = views / max(sub, 1)
        if ratio < min_ratio:
            continue
        hits.append(item_skeleton(
            source_id=vid,
            url=f"https://www.youtube.com/watch?v={vid}",
            title=sn.get("title", ""),
            author=sn.get("channelTitle", ""),
            published_at=sn.get("publishedAt"),
            text=(sn.get("description") or "")[:500],
            tags=sn.get("tags", []) or [],
            metrics={
                "views": views, "likes": likes, "comments": comments,
                "follower": sub, "breakout_ratio": round(ratio, 2),
                "age_days": round(age, 1),
                "views_per_day": round(views / max(age, 1)),
            },
            platform_extra={
                "channel_id": sn.get("channelId"),
                "duration": v.get("contentDetails", {}).get("duration"),
            },
        ))

    hits.sort(key=lambda i: i["metrics"]["breakout_ratio"], reverse=True)
    return hits, errors


def main() -> int:
    p = argparse.ArgumentParser(description="YouTube 低粉爆款筛选器（播粉比排序）")
    p.add_argument("--query", required=True)
    p.add_argument("--max-results", type=int, default=50)
    p.add_argument("--max-subs", type=int, default=DEFAULT_MAX_SUBS)
    p.add_argument("--min-views", type=int, default=DEFAULT_MIN_VIEWS)
    p.add_argument("--min-ratio", type=float, default=DEFAULT_MIN_RATIO)
    p.add_argument("--min-likes", type=int, default=0)
    p.add_argument("--min-comments", type=int, default=0)
    p.add_argument("--region", default="", help="regionCode，如 US / JP，留空=不限")
    a = p.parse_args()

    key = load_key("YOUTUBE_API_KEY")
    if not key:
        print("缺 YOUTUBE_API_KEY。设环境变量，或在 scripts/.env 写入：YOUTUBE_API_KEY=你的key",
              file=sys.stderr)
        return 2

    hits, errors = find_breakouts(
        a.query, api_key=key, max_results=a.max_results, max_subs=a.max_subs,
        min_views=a.min_views, min_ratio=a.min_ratio, min_likes=a.min_likes,
        min_comments=a.min_comments, region=a.region,
    )
    if errors:
        print("警告：" + "; ".join(errors), file=sys.stderr)
    if not hits:
        print(f"没找到低粉爆款（订阅≤{a.max_subs} 播放≥{a.min_views} 播粉比≥{a.min_ratio}）")
        return 0
    print(f"「{a.query}」YouTube 低粉爆款 {len(hits)} 条（按播粉比降序）\n")
    for i, it in enumerate(hits, 1):
        m = it["metrics"]
        print(f"{i}. {it['title']}")
        print(f"   {it['author']}  订阅 {m['follower']:,}  播放 {m['views']:,}  "
              f"赞 {m['likes']:,}  评论 {m['comments']:,}")
        print(f"   播粉比 {m['breakout_ratio']}x   {it['url']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
