#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B站低粉爆款筛选器 —— 找"粉丝不多但这条炸了"的视频。

为什么是 B站/YouTube 而不是小红书/抖音：低粉爆款筛选需要"粉丝数 + 互动数"两个字段
同时可筛。小红书/抖音只有第三方付费数据平台能给（自采=被风控），而 B站 有公开 API、
零登录、零风险。中视频基本盘正好在 B站，所以这条通道服务的是主力选题源。

核心判据是**播粉比 = 播放量 / 粉丝数**，不是绝对阈值。
一条 100k 播放：来自 18k 粉的 UP 是爆款（5.6x），来自 400k 粉的 UP 是日常（0.25x）。
绝对阈值会把大号的日常视频当爆款捞回来，播粉比不会。

数据来源（都是公开接口，无需登录）：
  搜索  api.bilibili.com/x/web-interface/search/all/v2  → play/like/review/mid
  粉丝  api.bilibili.com/x/relation/stat?vmid=<mid>     → follower

风控自觉：B站 对高频请求返回 -412。每个 UP 的粉丝数要单独查一次，所以这里做了
mid 级缓存 + 请求间隔，别把间隔调到 0。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
from http.cookiejar import CookieJar
from typing import Any

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import http_get, item_skeleton  # noqa: E402

SEARCH_API = "https://api.bilibili.com/x/web-interface/search/all/v2"
RELATION_API = "https://api.bilibili.com/x/relation/stat"
REFERER = {"Referer": "https://www.bilibili.com/"}

# 默认粉丝上限 = 1 万。判据是"普通人能不能复制"：
# 大号火了你拍不一定火（他有账号权重），1 万粉以下的人火了，才说明是**内容本身**在起作用。
# 想放宽用 --max-followers（B站 粉丝基数量级比小红书大，放到 5 万仍算低粉）。
DEFAULT_MAX_FOLLOWERS = 10_000
DEFAULT_MIN_PLAY = 50_000
DEFAULT_MIN_RATIO = 3.0
REQUEST_GAP_SEC = 0.7

# 时间维度（260726 补，此前完全没做，是个真 bug）：
# 刚发半小时的视频数据必然难看，混进来会被当成"这个角度不行"——是伪反面证据。
# 反过来，三年前的常青视频靠时间堆出来的播放量也不代表当下时机。所以要双向卡：
DEFAULT_MIN_AGE_DAYS = 3     # 成熟度地板：不足 3 天的数据还没稳定
DEFAULT_MAX_AGE_DAYS = 180   # 时效天花板：太老的不反映当下供给格局

# 噪声地板（260726 补）：**播粉比是发现器，不是判断器。**
# 实测「AI 写作」召回的前两名是「AI一辈子做不出来的自然波动」(362粉/50万播放/1392x)
# 和「AI味的成人V?」(2894粉/48万播放/167x) —— 极小号 + 单条病毒式猎奇 = 播粉比爆表。
# 规律：粉丝基数越小，分母越不可靠，一条偶然的推荐流就能把比值顶上天。
# 所以要有粉丝数地板；剩余的语义噪声（猎奇/擦边）由上层 AI 判断层剔除，脚本不硬编词表。
DEFAULT_MIN_FOLLOWERS = 1000


def _search_page(query: str, page: int, jar: CookieJar) -> list[dict[str, Any]]:
    url = f"{SEARCH_API}?keyword={urllib.parse.quote(query)}&page={page}"
    data = json.loads(http_get(url, headers=REFERER, jar=jar))
    if data.get("code") != 0:
        raise RuntimeError(f"bilibili search code={data.get('code')} msg={data.get('message')}")
    for block in data.get("data", {}).get("result", []):
        if block.get("result_type") == "video":
            return block.get("data", []) or []
    return []


def _follower_count(mid: int, jar: CookieJar, cache: dict[int, int]) -> int | None:
    """粉丝数按 mid 缓存 —— 同一个 UP 在搜索结果里常出现多条，不缓存就是成倍的请求。"""
    if mid in cache:
        return cache[mid]
    try:
        raw = http_get(f"{RELATION_API}?vmid={mid}", headers=REFERER, jar=jar)
        payload = json.loads(raw)
    except Exception:  # noqa: BLE001
        return None
    if payload.get("code") != 0:
        return None
    follower = payload.get("data", {}).get("follower")
    if isinstance(follower, int):
        cache[mid] = follower
        time.sleep(REQUEST_GAP_SEC)
        return follower
    return None


def find_breakouts(query: str, *, pages: int = 2, max_followers: int = DEFAULT_MAX_FOLLOWERS,
                   min_play: int = DEFAULT_MIN_PLAY, min_ratio: float = DEFAULT_MIN_RATIO,
                   min_like: int = 0, min_review: int = 0,
                   min_age_days: float = DEFAULT_MIN_AGE_DAYS,
                   max_age_days: float = DEFAULT_MAX_AGE_DAYS,
                   min_followers: int = DEFAULT_MIN_FOLLOWERS,
                   ) -> tuple[list[dict[str, Any]], list[str]]:
    jar = CookieJar()
    errors: list[str] = []
    try:
        http_get("https://www.bilibili.com/", jar=jar)  # 先拿 buvid cookie，否则搜索易 -412
    except Exception as exc:  # noqa: BLE001
        return [], [f"bilibili warmup failed: {exc}"]

    raw_videos: list[dict[str, Any]] = []
    for page in range(1, pages + 1):
        try:
            raw_videos.extend(_search_page(query, page, jar))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"page {page}: {exc}")
            break
        time.sleep(REQUEST_GAP_SEC)

    now_ts = time.time()

    def age_days(v: dict[str, Any]) -> float | None:
        pub = v.get("pubdate")
        return (now_ts - float(pub)) / 86400 if pub else None

    # 先按播放量+时间窗粗筛，再查粉丝数 —— 顺序反了会白查几十次 API。
    candidates = []
    for v in raw_videos:
        if int(v.get("play") or 0) < min_play:
            continue
        a = age_days(v)
        if a is None or a < min_age_days or a > max_age_days:
            continue
        candidates.append(v)
    cache: dict[int, int] = {}
    hits: list[dict[str, Any]] = []

    for v in candidates:
        mid = v.get("mid")
        if not isinstance(mid, int):
            continue
        play = int(v.get("play") or 0)
        like = int(v.get("like") or 0)
        review = int(v.get("review") or 0)
        if like < min_like or review < min_review:
            continue
        follower = _follower_count(mid, jar, cache)
        if follower is None or follower > max_followers:
            continue
        if follower < min_followers:      # 分母太小，播粉比不可信（见 DEFAULT_MIN_FOLLOWERS 注释）
            continue
        ratio = play / max(follower, 1)
        if ratio < min_ratio:
            continue
        hits.append(item_skeleton(
            source_id=v.get("bvid", ""),
            url=f"https://www.bilibili.com/video/{v.get('bvid','')}",
            title=__import__("re").sub(r"</?em[^>]*>", "", str(v.get("title", ""))),
            author=v.get("author", ""),
            published_at=v.get("pubdate"),
            text=str(v.get("description") or ""),
            tags=[t for t in str(v.get("tag") or "").split(",") if t],
            metrics={
                "views": play, "likes": like, "comments": review,
                "favorites": int(v.get("favorites") or 0),
                "danmaku": int(v.get("danmaku") or 0),
                "follower": follower,
                "breakout_ratio": round(ratio, 2),
                "age_days": round(age_days(v) or 0, 1),
                # 日均播放：区分"3 天冲到 10 万"和"两年积累 10 万"，前者才是当下热度
                "views_per_day": round(play / max(age_days(v) or 1, 1)),
            },
            platform_extra={
                "mid": mid, "duration": v.get("duration"), "typename": v.get("typename"),
            },
        ))

    hits.sort(key=lambda i: i["metrics"]["breakout_ratio"], reverse=True)
    return hits, errors


def main() -> int:
    p = argparse.ArgumentParser(description="B站低粉爆款筛选器（播粉比排序）")
    p.add_argument("--query", required=True)
    p.add_argument("--pages", type=int, default=2, help="搜索页数，每页约 20 条")
    p.add_argument("--max-followers", type=int, default=DEFAULT_MAX_FOLLOWERS)
    p.add_argument("--min-play", type=int, default=DEFAULT_MIN_PLAY)
    p.add_argument("--min-ratio", type=float, default=DEFAULT_MIN_RATIO)
    p.add_argument("--min-like", type=int, default=0)
    p.add_argument("--min-review", type=int, default=0)
    p.add_argument("--json", action="store_true", help="输出标准 JSON（供 collect.py 消费）")
    a = p.parse_args()

    hits, errors = find_breakouts(
        a.query, pages=a.pages, max_followers=a.max_followers, min_play=a.min_play,
        min_ratio=a.min_ratio, min_like=a.min_like, min_review=a.min_review,
    )
    if a.json:
        print(json.dumps({"items": hits, "errors": errors}, ensure_ascii=False))
        return 0

    if errors:
        print("警告：" + "; ".join(errors), file=sys.stderr)
    if not hits:
        print(f"没找到低粉爆款（粉丝≤{a.max_followers} 播放≥{a.min_play} 播粉比≥{a.min_ratio}）")
        print("建议：放宽 --max-followers 或降低 --min-ratio，或换关键词。")
        return 0
    print(f"「{a.query}」低粉爆款 {len(hits)} 条（按播粉比降序）\n")
    for i, it in enumerate(hits, 1):
        m = it["metrics"]
        print(f"{i}. {it['title']}")
        print(f"   {it['author']}  粉丝 {m['follower']:,}  播放 {m['views']:,}  "
              f"赞 {m['likes']:,}  评论 {m['comments']:,}")
        print(f"   播粉比 {m['breakout_ratio']}x   {it['url']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
