#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nook-topic 采集脚本的共用小工具。

这个文件存在的唯一原因：让 bili_breakout.py / youtube_breakout.py 能独立运行，
不依赖任何账号基础设施（数据库、浏览器自动化、私有 vault 路径）。
"""
from __future__ import annotations

import os
import sys
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any

# Windows 控制台默认 GBK，中文和 emoji 会 UnicodeEncodeError 崩掉整个脚本。
for _s in (sys.stdout, sys.stderr):
    if _s and _s.encoding and _s.encoding.lower() not in {"utf-8", "utf8"}:
        _s.reconfigure(encoding="utf-8")

DESKTOP_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def http_get(url: str, headers: dict[str, str] | None = None,
             jar: CookieJar | None = None, timeout: int = 30) -> str:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar or CookieJar()))
    req = urllib.request.Request(url, headers={"User-Agent": DESKTOP_UA, **(headers or {})})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def item_skeleton(**kw: Any) -> dict[str, Any]:
    """统一的条目结构。所有通道输出同一个 schema，下游才好合并。"""
    base = {
        "source_id": "", "url": "", "title": "", "author": "", "published_at": None,
        "text": "", "tags": [], "metrics": {}, "comments": [], "asset_paths": [],
        "platform_extra": {},
    }
    base.update(kw)
    return base


def load_key(env_var: str, env_file: str = ".env") -> str:
    """读 API key。优先级：环境变量 > 脚本同级目录的 .env 文件。

    用 utf-8-sig 而不是 utf-8：Windows PowerShell 的 `>` / Out-File 默认写 UTF-8 **带 BOM**，
    BOM 会粘在第一个键名上变成 '\\ufeffYOUTUBE_API_KEY'，导致 key 读不到却报"缺 key"。
    utf-8-sig 读无 BOM 的文件同样正确，所以无脑用它。
    """
    if os.environ.get(env_var):
        return os.environ[env_var].strip()
    path = Path(__file__).resolve().parent / env_file
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == env_var:
                    return v.strip()
    return ""
