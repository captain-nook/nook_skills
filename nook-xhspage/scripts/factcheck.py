"""事实追溯（提醒级）：图上出现的数字，要能在 meta.facts 里找到。
meta.facts 是一份列表，每条 {"id": "f1", "text": "素材里的原话或数据", "source": "原文位置"}，由 nook-xhswrite 的关卡 1 产生。
不拦截，只提醒：没写 facts 会提醒一次；图上的数字在 facts 里找不到会逐条提醒。"""
import re

import lint

NUM = re.compile(r"\d+(?:\.\d+)?")
IGNORE_KEYS = {"step_no", "number", "no", "value"}


def check(plan):
    out = []
    facts = plan.get("meta", {}).get("facts")
    pages = plan.get("pages", [])
    blob = ""
    if isinstance(facts, list):
        blob = " ".join(str(f.get("text", "")) for f in facts if isinstance(f, dict))
    has_num = False
    for i, pg in enumerate(pages, 1):
        f = pg.get("fields", {})
        texts = []
        lint._walk(f, "", texts)
        for where, t in texts:
            if where.endswith("label") and pg.get("type") in ("step", "prompt"):
                continue
            for m in NUM.finditer(t):
                has_num = True
                if blob and m.group(0) not in blob:
                    out.append(f"第 {i} 页（{pg.get('type')}），字段 {where}：数字 {m.group(0)} 在 meta.facts 里找不到出处，确认素材里有这个数字")
        for k in ("number",):
            pass
        if pg.get("type") == "stats":
            for j, it in enumerate(f.get("items", []), 1):
                n = str(it.get("number", ""))
                if blob and n and n not in blob:
                    out.append(f"第 {i} 页（stats），items[{j}].number：{n} 在 meta.facts 里找不到出处")
        if pg.get("type") in ("bar", "line"):
            key = "items" if pg["type"] == "bar" else "points"
            for j, it in enumerate(f.get(key, []), 1):
                v = it.get("value")
                if blob and v is not None and str(v).rstrip("0").rstrip(".") not in blob.replace(",", ""):
                    out.append(f"第 {i} 页（{pg['type']}），{key}[{j}].value：{v} 在 meta.facts 里找不到出处；图表的数据必须来自素材，否则只能写“示例数据”")
    if not isinstance(facts, list) and has_num:
        out.append("meta.facts：图上有数字但没有写事实清单 facts，无法核对出处；按 nook-xhswrite 关卡 1 把事实清单写进 meta.facts")
    return out


# ---------------- 强制版（方案不在 skill 自带目录里时，validate / render / deliver 都执行）----------------
CN = {"一": "1", "二": "2", "两": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}
BANNED = ("真相", "内幕", "揭秘", "实锤")


def _fact_texts(facts):
    out = []
    for f in facts or []:
        out.append(str(f.get("text", "")) if isinstance(f, dict) else str(f))
    return out


def _tokens(facts):
    blob = " ".join(_fact_texts(facts))
    for k, v in CN.items():
        blob = blob.replace(k, v)
    return set(NUM.findall(blob))


def errors(plan):
    """返回错误列表。图上的数字、日期必须逐个出现在 meta.facts 里；不能写“真相”这类定论词。"""
    errs = []
    facts = plan.get("meta", {}).get("facts")
    if not isinstance(facts, list) or not [t for t in _fact_texts(facts) if len(t.strip()) >= 4]:
        errs.append("meta.facts：没有事实清单。先按 nook-xhswrite 关卡 1 写 facts.md，再把每条事实原样写进 meta.facts（每条写明素材里的原句）")
        return errs
    toks = _tokens(facts)
    for i, pg in enumerate(plan.get("pages", []), 1):
        f = pg.get("fields", {})
        nums = []
        texts = []
        lint._walk(f, "", texts)
        for where, t in texts:
            if where.endswith("label") and pg.get("type") in ("step", "prompt"):
                continue
            for m in NUM.finditer(t):
                nums.append((where, m.group(0)))
            for w in BANNED:
                if w in t:
                    errs.append(f"第 {i} 页（{pg.get('type')}），字段 {where}：出现「{w}」，素材里没有这种定论就不能写，改成素材里的原话或加“可能”")
        for j, it in enumerate(f.get("items", []) if pg.get("type") == "stats" else [], 1):
            nums.append((f"items[{j}].number", str(it.get("number", ""))))
        if pg.get("type") in ("bar", "line"):
            key = "items" if pg["type"] == "bar" else "points"
            for j, it in enumerate(f.get(key, []), 1):
                if it.get("value") is not None:
                    nums.append((f"{key}[{j}].value", str(it.get("value"))))
        for where, n in nums:
            for tok in NUM.findall(n):
                if tok not in toks:
                    errs.append(f"第 {i} 页（{pg.get('type')}），字段 {where}：数字 {tok} 在 meta.facts 里找不到。素材里没有的数字和日期不能写；"
                                f"版面放不下时只能缩短文字，不能换成别的数字")
    return errs

