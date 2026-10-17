"""贴纸"放不放"的判断逻辑：任何 agent 照着这几步走，都能得到同样的答案。贴纸不是必填，也不是越多越好。
  1 页型没有贴纸位 → 不放
  2 页型自带贴纸（对比、循环、矩阵）→ 不再加
  3 页面主体是用户的截图、成果图或数据图（step、result、bar、line、funnel）→ 不放
  4 内容严肃或负面（风险、事故、损失、违规、隐私、健康、金融、法律）→ 不放
  5 页面已经满（文字超过 70 字，或清单条目 ≥ 4）→ 不放
  6 在素材库里按页面文字里的词（素材标签）找不到贴切的 → 不放，宁缺毋滥
  7 都通过，才放：每页最多 2 个（封面 2、其余 1 到 2），同一个贴纸全篇不重复，全篇有贴纸的页不超过 60%"""
import re

import lint
import spec

SLOTS = {"timeline": 1, "cover_list": 1, "cover_person": 2, "cover_quote": 1, "step": 2, "prompt": 1, "idea": 2, "list": 2, "result": 1, "quote": 1,
         "bar": 1, "line": 1, "closing": 1, "back_cover": 1}
NO_SLOT = {"toc", "pyramid", "stats", "shots"}
BUILT_IN = {"compare", "cycle", "matrix"}
DATA_LED = {"step", "result", "bar", "line", "funnel", "shots", "stats"}
SENSITIVE = ["风险", "事故", "损失", "违规", "违法", "封号", "封禁", "警告", "隐私", "泄露", "死亡", "疾病", "癌", "亏损", "诈骗", "犯罪", "投资", "理财", "医疗", "维权"]
ALIAS = {"agent": "智能体", "ai": "ai", "提示词": "提示", "工作流": "流程", "封面": "拍照", "截图": "拍照", "素材": "资料", "脚本": "代码", "出图": "拍照"}
CAT_ORDER = {"object": 0, "tool": 1, "symbol": 2, "nature": 3, "character": 4}
MAX_RATIO = 0.6


def page_text(pg):
    out = []
    lint._walk(pg.get("fields", {}), "", out)
    return " ".join(x[1] for x in out).replace("[[", "").replace("]]", "")


def _count_items(f):
    n = 0
    for k in ("items", "layers", "stages", "points", "nodes", "cells", "body"):
        if isinstance(f.get(k), list):
            n = max(n, len(f[k]))
    return n


def _candidates(text, used):
    t = text.lower()
    for k, v in ALIAS.items():
        if k in t:
            t += " " + v
    scored = []
    for m in spec.manifest().values():
        hits = sum(1 for w in m["tags"] + [m["cn"]] if w and w.lower() in t)
        if hits and m["id"] not in used:
            scored.append((-hits, CAT_ORDER.get(m["category"], 9), m["id"], m["cn"]))
    scored.sort()
    return [(i, cn, -h) for h, _, i, cn in scored]


def decide(pg, used=()):
    """返回 (放/不放, 原因, 候选列表)。"""
    t, f = pg.get("type"), pg.get("fields", {})
    if t in NO_SLOT:
        return "不放", "这个页型没有贴纸位", []
    if t in BUILT_IN:
        return "不放", "页型自带贴纸，不再加", []
    if t in DATA_LED:
        return "不放", "页面主体是用户的截图、成果图或数据图", []
    text = page_text(pg)
    hit = [w for w in SENSITIVE if w in text]
    if hit:
        return "不放", f"内容严肃或负面（含「{hit[0]}」）", []
    if len(re.sub(r"\s", "", text)) > 70 or _count_items(f) >= 4:
        return "不放", "页面已经满（文字超过 70 字或条目 ≥ 4）", []
    cands = _candidates(text, set(used))
    if not cands:
        return "不放", "素材库里没有贴切的（按页面文字里的词匹配素材标签）", []
    return "放", f"页面里有可画的内容：{'、'.join(c[1] for c in cands[:3])}", cands[:3]


def suggest(plan):
    """返回逐页建议，并按全篇上限 60% 收紧。"""
    pages = plan["pages"]
    used, res = [], []
    for i, pg in enumerate(pages):
        d, why, c = decide(pg, used)
        if d == "放":
            used += [x[0] for x in c[:SLOTS.get(pg["type"], 1)]]
        res.append([d, why, c])
    n = len(pages)
    keep = int(n * MAX_RATIO)
    yes = [(i, max((x[2] for x in r[2]), default=0)) for i, r in enumerate(res) if r[0] == "放"]
    if len(yes) > keep:
        yes.sort(key=lambda x: (-(x[0] == 0), -x[1], x[0]))   # 封面优先，其余按匹配度
        drop = {i for i, _ in yes[keep:]}
        for i in drop:
            res[i] = ["不放", f"全篇有贴纸的页不超过 {int(MAX_RATIO * 100)}%，这页让位", []]
    return res


def warnings(plan):
    """校验通过后的提醒（不拦截）：用了贴纸，但按判断逻辑这一页不该放。"""
    out = []
    pages = plan["pages"]
    seen = {}
    with_st = 0
    for i, pg in enumerate(pages, 1):
        f = pg.get("fields", {})
        ids = list(f.get("stickers") or []) + ([f["sticker"]] if f.get("sticker") else [])
        if ids and pg["type"] not in BUILT_IN:
            with_st += 1
            d, why, _ = decide(pg)
            if d == "不放" and "素材库里没有贴切" not in why and "让位" not in why:
                out.append(f"第 {i} 页（{pg['type']}）：放了贴纸，但按判断逻辑这一页不建议放：{why}")
            for x in ids:
                if x in seen:
                    out.append(f"第 {i} 页：贴纸 {x} 和第 {seen[x]} 页重复，换一个")
                seen[x] = i
    if pages and with_st > len(pages) * MAX_RATIO:
        out.append(f"全篇 {with_st} 页放了贴纸，超过 {int(MAX_RATIO * 100)}%，去掉几个让页面有留白")
    return out
