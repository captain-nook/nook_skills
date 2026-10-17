"""图文下方的正文包检查：标题 3 个、标签 5 到 8 个、正文 400 到 800 字、无粗体无列表、去 AI 味、有删除测试记录。
文件格式见 nook-xhswrite/references/templates.md（五个二级标题：标题、标签、正文、删除测试记录、事实对照）。"""
import re

import lint

SECTIONS = ["标题", "标签", "正文", "删除测试记录", "事实对照"]


def parse(text):
    parts, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s*(.+?)\s*$", line)
        if m and m.group(1) in SECTIONS:
            cur = m.group(1)
            parts[cur] = []
        elif cur:
            parts[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in parts.items()}


def check(text):
    """返回 (errors, warnings)。"""
    errs, warns = [], []
    p = parse(text)
    for s in SECTIONS:
        if not p.get(s):
            errs.append(f"缺少「{s}」这一节（或为空）。五节固定：{'、'.join(SECTIONS)}，格式见 nook-xhswrite/references/templates.md")
    if errs:
        return errs, warns
    titles = []
    for ln in p["标题"].splitlines():
        if not ln.strip():
            continue
        t = re.sub(r"^[-*\d.、\s]+", "", ln).strip()
        t = re.sub(r"^[^：:]{1,4}[：:]\s*", "", t).strip()
        titles.append(t)
    if len(titles) != 3:
        errs.append(f"标题：要正好 3 个（搜索型、结果型、清单型），现在 {len(titles)} 个")
    for i, t in enumerate(titles, 1):
        n = len(re.sub(r"\s", "", t))
        if not 15 <= n <= 25:
            errs.append(f"标题 {i}：{n} 个字，要 15 到 25 字：{t[:20]}")
    tags = re.findall(r"#\s*([^\s#]+)", p["标签"])
    if not 5 <= len(tags) <= 8:
        errs.append(f"标签：要 5 到 8 个，现在 {len(tags)} 个（写成 #关键词 的形式，空格分隔）")
    body = p["正文"]
    n = len(re.sub(r"\s", "", body))
    short = bool(re.search(r"^篇幅：短", body, re.M))
    lo = 100 if short else 400
    if short:
        body = re.sub(r"^篇幅：短[^\n]*\n?", "", body, flags=re.M)
        n = len(re.sub(r"\s", "", body))
    if not lo <= n <= 800:
        errs.append(f"正文：{n} 个字，要 {lo} 到 800 字" + ("" if short else "；素材只有一两条事实时，正文第一行写“篇幅：短（素材只有 N 条事实）”，下限放宽到 100 字，不要用空话凑字数"))
    if "**" in body:
        errs.append("正文：不要用粗体 **")
    if re.search(r"^\s*([-*•]|\d+[.、])\s", body, re.M):
        errs.append("正文：不要用列表，写成自然段")
    if re.search(r"^(大家好|各位|今天|本文|在这篇)", body.strip()):
        errs.append("正文：第一句直接说内容，不写开场白")
    full = "\n".join([p["标题"], p["正文"]])
    for ln, w, name, hint in lint.lint_text(full):
        errs.append(f"AI 味表达：命中「{w}」（{name}），{hint}")
    for w in lint.warn_text(full):
        warns.append(w)
    rec = p["删除测试记录"]
    if not re.search(r"nook-alive|删除测试", rec):
        errs.append("删除测试记录：要写明已调用 nook-alive 做删除测试，并列出删掉了什么（没有命中就写“无命中”）")
    if len(re.sub(r"\s", "", rec)) < 8:
        errs.append("删除测试记录：内容太短，要写清做了什么、删了什么")
    return errs, warns
