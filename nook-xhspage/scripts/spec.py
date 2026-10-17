"""页型规格与校验。所有页型、字段、字数上限都在这里；校验报错统一写成"第 N 页（页型），字段 X：问题，怎么改"。
字数按字符计，上限是按样片估的软标准：超了就报错，让 agent 回去删文案，不悄悄缩字。"""
import json
import pathlib

import paths

THEMES = {"paper": "手账浅色", "dark": "深色", "ticket": "船票风（蓝白，页面是一张船票，底部票根印账号名和条码）"}
THEMES_READY = ("paper", "dark", "ticket")
POSES = ("a", "b", "c")
COVER_TYPES = ("cover_list", "cover_person", "cover_quote")
END_TYPES = ("closing", "back_cover")


class S:
    """字段规格。kind: str int num list obj asset path enum box arrow"""

    def __init__(self, kind, req=True, max=None, lo=None, hi=None, of=None, fields=None, values=None, hl=False, desc=""):
        self.kind, self.req, self.max, self.lo, self.hi = kind, req, max, lo, hi
        self.of, self.fields, self.values, self.hl, self.desc = of, fields, values, hl, desc


def st(max, req=True, hl=False, desc=""):
    return S("str", req, max=max, hl=hl, desc=desc)


def lst(of, lo, hi, req=True, desc=""):
    return S("list", req, lo=lo, hi=hi, of=of, desc=desc)


ASSET = lambda req=False: S("asset", req, desc="素材库 id（assets/library/manifest.json）")
ASSETS = lambda lo, hi: S("list", False, lo=lo, hi=hi, of=ASSET(True), desc="素材库 id 列表")
POSE = S("enum", False, values=POSES, desc="人物姿态 a 抱臂 / b 讲解 / c 邀请")

TYPES = {
    "cover_list": dict(cn="榜单清单封面", role="cover", use="N 个工具、N 条方法，收藏型内容", fields={
        "lead": st(12, desc="开头半句"), "number": S("int", lo=1, hi=99, desc="大数字"), "unit": st(6, hl=False, desc="数字后的词，自动高亮"),
        "items": lst(st(12), 3, 5, desc="清单项"), "footnote": st(10, False, desc="手写小注"), "pose": POSE, "sticker": ASSET()}),
    "cover_person": dict(cn="人物大字封面", role="cover", use="观点、反常识、结果承诺", fields={
        "line1": st(5), "line2": st(6, hl=True, desc="含高亮词，用 [[ ]]"), "sub1": st(12, desc="手写副标题第一行"), "sub2": st(12),
        "note": S("obj", False, desc="便签", fields={"title": st(8), "items": lst(st(8), 2, 3)}), "pose": POSE, "stickers": ASSETS(0, 2)}),
    "cover_quote": dict(cn="极简大字封面", role="cover", use="一句话观点、提示词、金句", fields={
        "lines": lst(st(5), 4, 4, desc="四行大字，最后一行含高亮"), "caption": st(12, False), "stickers": ASSETS(0, 1), "face": POSE}),
    "step": dict(cn="步骤教程页", role="inner", use="第 N 步加一张真实截图", fields={
        "step_no": S("int", lo=1, hi=9), "title": st(10), "subtitle": st(18, desc="可写 A → B → C"),
        "screenshot": S("path", desc="截图文件，相对方案文件的路径"), "red_box": S("box", False, desc="[x,y,w,h]，0 到 1 的截图相对位置"),
        "arrow": S("arrow", False, desc='{"from":[x,y],"to":[x,y]}，0 到 1'), "label": st(8, False, desc="便签贴字"), "stickers": ASSETS(0, 2)}),
    "prompt": dict(cn="提示词页", role="inner", use="一条能直接复制的指令", fields={
        "title": st(10, hl=True), "tag": st(4, False, desc="标签字，默认“提示词”"), "body": lst(st(24, hl=True), 2, 4, desc="指令正文，每句一条"),
        "storyboard": lst(S("obj", fields={"sticker": ASSET(True), "label": st(5)}), 3, 3, False, desc="小人分镜"), "sticker": ASSET()}),
    "idea": dict(cn="观点大字页", role="inner", use="一页一个判断", fields={
        "lines": lst(st(7), 3, 3, desc="三行大字，最后一行含高亮"), "caption": lst(st(10), 1, 3, False, desc="手写说明"), "stickers": ASSETS(0, 2)}),
    "list": dict(cn="清单页", role="inner", use="并列的几项", fields={
        "title": st(10, hl=True), "items": lst(S("obj", fields={"name": st(14, desc='名字，如 skill 名'), "desc": st(14)}), 3, 5), "footnote": st(12, False), "stickers": ASSETS(0, 2)}),
    "compare": dict(cn="对比页", role="inner", use="前后、新旧、A 对 B", fields={
        "title": st(8, hl=True), "left": S("obj", fields={"tag": st(3), "points": lst(st(10), 3, 3), "sticker": ASSET(True)}),
        "right": S("obj", fields={"tag": st(3), "points": lst(st(10), 3, 3), "sticker": ASSET(True)}), "footer": st(14, False)}),
    "result": dict(cn="成果页", role="inner", use="展示做出来的东西（用户提供的成品图）", fields={
        "title": st(10, hl=True), "images": lst(S("path"), 1, 2, desc="成品图，注意隐私"), "caption": st(12), "sticker": ASSET()}),
    "toc": dict(cn="目录页", role="inner", use="先列要点", fields={
        "title": st(8, hl=True), "items": lst(S("obj", fields={"name": st(10), "desc": st(14, False)}), 3, 6)}),
    "quote": dict(cn="金句页", role="inner", use="一句话大字，可当中间页", fields={
        "lines": lst(st(8), 2, 4, desc="最后一行含高亮"), "caption": st(14, False), "sticker": ASSET()}),
    "cycle": dict(cn="循环图", role="inner", use="首尾相接、反复进行", fields={
        "title": st(12, hl=True), "nodes": lst(S("obj", fields={"name": st(4), "desc": st(6), "sticker": ASSET(True)}), 3, 5), "footnote": st(14, False)}),
    "matrix": dict(cn="矩阵图", role="inner", use="两个维度交叉的分类", fields={
        "title": st(12, hl=True), "xlabel": st(4), "ylabel": st(4),
        "cells": lst(S("obj", fields={"tag": st(4), "desc": st(10), "sticker": ASSET(True)}), 4, 4, desc="顺序：左上、右上、左下、右下"),
        "highlight": S("int", False, lo=0, hi=3, desc="重点格序号，默认 0")}),
    "pyramid": dict(cn="金字塔图", role="inner", use="层级、基础与上层", fields={
        "title": st(12, hl=True), "layers": lst(S("obj", fields={"name": st(3), "desc": st(14)}), 3, 3, desc="从上到下"), "footnote": st(14, False)}),
    "bar": dict(cn="柱状图", role="inner", use="几项数据对比", fields={
        "title": st(12, hl=True), "items": lst(S("obj", fields={"label": st(5), "value": S("num"), "unit": st(3, False)}), 3, 5),
        "sticker": ASSET(), "note": st(20, False, desc="脚注，默认提示用真实数据替换")}),
    "line": dict(cn="折线图", role="inner", use="随时间的变化", fields={
        "title": st(12, hl=True), "points": lst(S("obj", fields={"label": st(5), "value": S("num")}), 3, 6), "axis": st(4, False, desc="纵轴名"),
        "sticker": ASSET(), "note": st(20, False)}),
    "funnel": dict(cn="漏斗图", role="inner", use="一层层筛选、转化", fields={
        "title": st(12, hl=True), "stages": lst(S("obj", fields={"name": st(3), "value": st(6), "sticker": ASSET(False)}), 3, 5), "footnote": st(16, False)}),
    "timeline": dict(cn="时间轴", role="inner", use="按时间排列的几个节点、阶段、版本", fields={
        "title": st(12, hl=True), "events": lst(S("obj", fields={"time": st(6), "name": st(8), "desc": st(14, False)}), 3, 5),
        "footnote": st(14, False), "sticker": ASSET()}),
    "stats": dict(cn="大数字页", role="inner", use="2 到 3 个关键数字，数字必须来自素材", fields={
        "title": st(12, hl=True), "items": lst(S("obj", fields={"number": st(6, desc="数字，带小数点或百分号都行"), "unit": st(3, False), "label": st(12)}), 2, 3),
        "note": st(20, False, desc="脚注，如数据来源")}),
    "shots": dict(cn="多截图页", role="inner", use="2 到 3 张用户提供的截图并排", fields={
        "title": st(12, hl=True), "shots": lst(S("path"), 2, 3, desc="截图，放进 inputs/"), "captions": lst(st(8), 2, 3, False, desc="每张的说明"),
        "label": st(8, False)}),
    "closing": dict(cn="收尾页", role="end", use="收藏、点赞、关注引导", fields={
        "line1": st(7), "line2": st(8, hl=True), "hint": st(12), "pose": POSE, "sticker": ASSET()}),
    "back_cover": dict(cn="封底页", role="end", use="一行大字：我是谁，保持关注。不放二维码、联系方式、导流话术", fields={
        "line1": st(10, desc="名字"), "line2": st(14, hl=True, desc="一句话"), "pose": POSE, "sticker": ASSET()}),
}


def manifest():
    return {m["id"]: m for m in json.loads((paths.LIB / "manifest.json").read_text(encoding="utf-8"))["items"]}


def hl_count(s):
    return s.count("[[")


def _check(val, sp, where, errs, base_dir, assets):
    """where：用于报错的字段路径。返回 None。"""
    k = sp.kind
    if k == "str":
        if not isinstance(val, str) or not val.strip():
            errs.append(f"字段 {where}：要填一段文字，现在是空的或不是文字")
            return
        n = len(val.replace("[[", "").replace("]]", ""))
        if n > sp.max:
            errs.append(f"字段 {where}：{n} 个字，超过上限 {sp.max}，删到 {sp.max} 字以内")
        c = hl_count(val)
        if c > 1:
            errs.append(f"字段 {where}：高亮 [[ ]] 只能有 1 处，现在有 {c} 处")
        elif c == 1 and (val.count("]]") != 1 or val.index("[[") > val.index("]]")):
            errs.append(f"字段 {where}：高亮写法是 [[词]]，括号没配对")
        elif c and not sp.hl and where.split(".")[-1] not in ("line2", "lines", "title", "body"):
            pass
    elif k in ("int", "num"):
        if isinstance(val, bool) or not isinstance(val, (int, float)) or (k == "int" and not float(val).is_integer()):
            errs.append(f"字段 {where}：要填{'整数' if k == 'int' else '数字'}")
            return
        if sp.lo is not None and val < sp.lo or sp.hi is not None and val > sp.hi:
            errs.append(f"字段 {where}：取值范围 {sp.lo} 到 {sp.hi}，现在是 {val}")
    elif k == "enum":
        if val not in sp.values:
            errs.append(f"字段 {where}：只能填 {' / '.join(sp.values)}，现在是 {val!r}")
    elif k == "asset":
        if not isinstance(val, str) or val not in assets:
            errs.append(f"字段 {where}：素材库里没有 id={val!r}，用 list-assets 查可用 id")
    elif k == "path":
        if not isinstance(val, str) or not (base_dir / val).is_file():
            errs.append(f"字段 {where}：找不到文件 {val!r}（路径相对方案文件所在目录）")
        elif not (base_dir / val).resolve().is_relative_to((base_dir / "inputs").resolve()):
            errs.append(f"字段 {where}：截图和成果图必须由用户提供，并放进方案文件旁边的 inputs/ 文件夹；{val!r} 不在里面。"
                        "agent 不要自己找图、不要用占位图或生成图，先向用户要")
    elif k == "box":
        if not (isinstance(val, list) and len(val) == 4 and all(isinstance(x, (int, float)) for x in val) and all(0 <= x <= 1 for x in val)):
            errs.append(f"字段 {where}：要写成 [x, y, w, h]，四个数都在 0 到 1 之间")
    elif k == "arrow":
        ok = isinstance(val, dict) and all(isinstance(val.get(p), list) and len(val[p]) == 2 and all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in val[p]) for p in ("from", "to"))
        if not ok:
            errs.append(f'字段 {where}：要写成 {{"from": [x, y], "to": [x, y]}}，数都在 0 到 1 之间')
    elif k == "list":
        if not isinstance(val, list):
            errs.append(f"字段 {where}：要写成列表")
            return
        if len(val) < sp.lo or len(val) > sp.hi:
            errs.append(f"字段 {where}：要 {sp.lo} 到 {sp.hi} 项，现在有 {len(val)} 项" if sp.lo != sp.hi else f"字段 {where}：要正好 {sp.lo} 项，现在有 {len(val)} 项")
        for i, v in enumerate(val[:sp.hi]):
            _check(v, sp.of, f"{where}[{i + 1}]", errs, base_dir, assets)
    elif k == "obj":
        if not isinstance(val, dict):
            errs.append(f"字段 {where}：要写成对象")
            return
        _fields(val, sp.fields, where, errs, base_dir, assets)


def _fields(obj, fields, where, errs, base_dir, assets):
    for name in obj:
        if name not in fields:
            errs.append(f"字段 {where + '.' if where else ''}{name}：这个页型没有这个字段，可用字段：{', '.join(fields)}")
    for name, sp in fields.items():
        if name not in obj or obj[name] in (None, ""):
            if sp.req:
                errs.append(f"字段 {where + '.' if where else ''}{name}：必填，没有写（{sp.desc or sp.kind}）")
            continue
        _check(obj[name], sp, f"{where + '.' if where else ''}{name}", errs, base_dir, assets)


def validate(plan, base_dir):
    """返回错误列表，空列表表示通过。"""
    errs = []
    if not isinstance(plan, dict) or "pages" not in plan:
        return ["方案文件顶层要有 meta 和 pages 两项"]
    meta = plan.get("meta", {})
    theme = meta.get("theme")
    if theme not in THEMES:
        errs.append(f"meta.theme：只能填 {' / '.join(THEMES)}，现在是 {theme!r}")
    elif theme not in THEMES_READY:
        errs.append(f"meta.theme：{theme} 款还没迁入，现在可用：{' / '.join(THEMES_READY)}")
    terms = meta.get("subject_terms")
    if not (isinstance(terms, list) and 1 <= len(terms) <= 4 and all(isinstance(x, str) and x.strip() for x in terms)):
        errs.append("meta.subject_terms：必填，写 1 到 4 个这篇图文的主题词（如 [\"skill\", \"小红书\"]），封面或第 2 页的文字里必须出现，读者才知道这是讲什么的")
    pages = plan["pages"]
    if not isinstance(pages, list) or not 3 <= len(pages) <= 9:
        errs.append(f"pages：要 3 到 9 页，现在有 {len(pages) if isinstance(pages, list) else '不是列表'}")
        if not isinstance(pages, list):
            return errs
    assets = manifest()
    kinds = []
    for i, pg in enumerate(pages, 1):
        t = pg.get("type") if isinstance(pg, dict) else None
        if t not in TYPES:
            errs.append(f"第 {i} 页：type 只能填 {' / '.join(TYPES)}，现在是 {t!r}")
            kinds.append(None)
            continue
        kinds.append(t)
        sub = []
        _fields(pg.get("fields", {}), TYPES[t]["fields"], "", sub, base_dir, assets)
        errs += [f"第 {i} 页（{t}），{e}" for e in sub]
    import brand
    b = brand.load()
    if b and not b["has_person"]:
        for i, k in enumerate(kinds, 1):
            if k == "cover_person":
                errs.append(f"第 {i} 页：当前品牌没有设置人物形象，cover_person 需要人物，换成 cover_quote 或 cover_list")
    ok = [k for k in kinds if k]
    if kinds and kinds[0] not in COVER_TYPES:
        errs.append(f"第 1 页：必须是封面类（{' / '.join(COVER_TYPES)}），现在是 {kinds[0]}")
    if kinds and kinds[-1] not in END_TYPES:
        errs.append(f"第 {len(kinds)} 页：最后一页必须是 {' 或 '.join(END_TYPES)}，现在是 {kinds[-1]}")
    for i in range(1, len(kinds)):
        if kinds[i] and kinds[i] == kinds[i - 1]:
            errs.append(f"第 {i} 页和第 {i + 1} 页：相邻两页都是 {kinds[i]}，换一种页型")
    for i, k in enumerate(kinds):
        if k in COVER_TYPES and i != 0:
            errs.append(f"第 {i + 1} 页：封面类页型只能放第 1 页")
        if k in END_TYPES and i != len(kinds) - 1:
            errs.append(f"第 {i + 1} 页：{k} 只能放最后一页")
    import lint
    errs += lint.lint_plan(plan)
    if isinstance(terms, list) and len(pages) >= 2:
        import lint as _l
        head = []
        for pg in pages[:2]:
            tx = []
            _l._walk(pg.get("fields", {}), "", tx, True)
            head += [x[1] for x in tx]
        blob = " ".join(head).replace("[[", "").replace("]]", "").lower()
        for w in terms:
            if isinstance(w, str) and w.strip() and w.strip().lower() not in blob:
                errs.append(f"封面和第 2 页：没有出现主题词「{w}」，读者看不出这是讲什么的。在封面或第 2 页的文字里点明（封面加第 2 页要回答：这是什么、给谁、得到什么）")
    if len(set(ok)) < 3 and len(ok) >= 3:
        errs.append(f"整篇只用了 {len(set(ok))} 种页型，至少用 3 种")
    return errs
