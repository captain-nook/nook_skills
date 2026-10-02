"""lint_deck：质量清单里能自动判的项（读 PPTX、*.anim.json 和 PowerPoint 导出的逐页图片）。
python lint_deck.py <deck.pptx> [--png <check_deck 导出目录>] [--json]

判什么（talk = 上台讲，read = 给别人看；模式从 anim.json 里有没有动效推断）：
  否（必须改）：图片没有替代文字 / 页面没有标题文字 / 字号过小 / 字体家族超过 2 个 / 文字与底色对比度不够 /
               talk：某页讲点（点击）超过 5 次、某页没有备注
  提示（看情况）：talk：内容外框占页面超过 60% / 连续 3 页版式相同 / 强调色超过 5 种
退出码：有"否"返回 1，否则 0。
"""
import json
import pathlib
import re
import sys
from collections import Counter

from pptx import Presentation
from pptx.util import Emu

W, H = 960.0, 540.0
EXEMPT = {"角标左", "角标右", "数据来源", "试验标签", "页脚", "页码", "页脚条", "页脚线"}        # 页眉页脚类小字，不按最小字号判
MIN_FS = {"talk": 18.0, "read": 14.0}
ALLOW_EYEBROW = 16.0                                      # 眉题（小标签）放宽到 16pt


def lum(rgb):
    def f(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def sat(rgb):
    mx, mn = max(rgb), min(rgb)
    return 0 if mx == 0 else (mx - mn) / mx


def walk(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6:                     # 组合
            yield from walk(sh.shapes)


def runs_of(sh):
    """[(字号pt, 颜色hex或None, 是否渐变, 字体名)]"""
    out = []
    if not sh.has_text_frame:
        return out
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            if not r.text.strip():
                continue
            rpr = r._r.find("{http://schemas.openxmlformats.org/drawingml/2006/main}rPr")
            size = int(rpr.get("sz")) / 100.0 if rpr is not None and rpr.get("sz") else None
            col, grad, face = None, False, None
            if rpr is not None:
                ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
                sf = rpr.find(ns + "solidFill")
                if sf is not None and sf.find(ns + "srgbClr") is not None:
                    col = sf.find(ns + "srgbClr").get("val")
                grad = rpr.find(ns + "gradFill") is not None
                lt = rpr.find(ns + "latin")
                face = lt.get("typeface") if lt is not None else None
            out.append((size, col, grad, face))
    return out


def family(face):
    return re.sub(r"\s+(Semibold|Bold|Light|Medium|Heavy|Regular|Black)$", "", face or "")


def main():
    argv = sys.argv[1:]
    if not argv:
        raise SystemExit(__doc__)
    pptx = pathlib.Path(argv[0])
    png_dir = pathlib.Path(argv[argv.index("--png") + 1]) if "--png" in argv else None
    plan_path = pptx.with_suffix(".anim.json")
    plan = json.loads(plan_path.read_text(encoding="utf8")) if plan_path.exists() else []
    mode = "talk" if any("effect" in a for a in plan) else "read"
    prs = Presentation(str(pptx))
    finds = []        # (级别, 页, 说明)

    def add(level, idx, msg):
        finds.append((level, idx, msg))

    beats = Counter(a["slide"] for a in plan if a.get("trigger") == "beat")
    sigs = []
    faces, chroma = Counter(), Counter()
    try:
        import numpy as np
        from PIL import Image
    except Exception:
        np = None
    for idx, sl in enumerate(prs.slides, 1):
        top = list(sl.shapes)
        # 1 标题
        title = sl.shapes.title
        if title is None or not title.has_text_frame or not title.text_frame.text.strip():
            add("否", idx, "没有标题文字（标题要走真占位符）")
        # 2 替代文字
        for sh in walk(top):
            if sh.shape_type == 13:                 # 图片
                d = sh._element.xpath(".//p:cNvPr")[0].get("descr")
                if not d:
                    add("否", idx, f"图片「{sh.name}」没有替代文字")
        # 3 字号、字体、颜色
        for sh in walk(top):
            for size, col, grad, face in runs_of(sh):
                if face:
                    faces[family(face)] += 1
                if col and sat(hex2rgb(col)) > 0.25:
                    chroma[col.upper()] += 1
                if size is None or sh.name in EXEMPT:
                    continue
                floor = ALLOW_EYEBROW if sh.name.startswith("眉题") else MIN_FS[mode]
                if size < floor:
                    add("否", idx, f"「{sh.name}」字号 {size:g}pt，低于 {floor:g}pt")
        # 4 讲点与备注
        if mode == "talk":
            if beats.get(idx, 0) > 5:
                add("否", idx, f"讲点（点击）{beats[idx]} 次，超过 5 次")
            if not (sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip()):
                add("否", idx, "没有备注（讲稿）")
        # 5 版式签名
        names = sorted({re.sub(r"[#\d]+$", "", re.sub(r"·.*$", "", sh.name)) for sh in top if not sh.name.startswith("!!")})
        sigs.append(tuple(names))
        # 6 对比度、留白（需要导出图）
        img = None
        if png_dir and np is not None:
            p = png_dir / f"slide_{idx:02d}.png"
            if p.exists():
                img = np.asarray(Image.open(p).convert("RGB")).astype(int)
        if img is not None:
            sx, sy = img.shape[1] / W, img.shape[0] / H
            for sh in walk(top):
                rs = [r for r in runs_of(sh) if r[1] and not r[2]]
                if not rs or sh.left is None:
                    continue
                x0, y0 = int(Emu(sh.left).pt * sx), int(Emu(sh.top).pt * sy)
                x1, y1 = int((Emu(sh.left).pt + Emu(sh.width).pt) * sx), int((Emu(sh.top).pt + Emu(sh.height).pt) * sy)
                if x1 <= 0 or y1 <= 0 or x0 >= img.shape[1] or y0 >= img.shape[0]:
                    continue
                x0, y0, x1, y1 = max(0, x0), max(0, y0), min(img.shape[1], x1), min(img.shape[0], y1)
                if x1 - x0 < 12 or y1 - y0 < 12:
                    continue
                crop = img[y0:y1, x0:x1]
                flat = crop.reshape(-1, 3)
                for size, col, grad, face in rs:
                    # 底色：排除与文字色相近的像素（文字本身、同色描边）后取中位数；剩得太少就退回取边缘一圈
                    far = flat[np.linalg.norm(flat - np.array(hex2rgb(col)), axis=1) > 70]
                    if len(far) >= 0.15 * len(flat):
                        bg = tuple(int(v) for v in np.median(far, axis=0))
                    else:
                        ring = np.concatenate([crop[:3].reshape(-1, 3), crop[-3:].reshape(-1, 3), crop[:, :3].reshape(-1, 3), crop[:, -3:].reshape(-1, 3)])
                        bg = tuple(int(v) for v in np.median(ring, axis=0))
                    need = 3.0 if (size or 0) >= 24 else 4.5
                    cr = contrast(hex2rgb(col), bg)
                    if cr < need and not (sh.name in EXEMPT):
                        add("否", idx, f"「{sh.name}」文字与底色对比度 {cr:.1f}:1，低于 {need}:1")
                        break
            if mode == "talk":
                mask = np.zeros((54, 96), bool)
                for sh in top:
                    if sh.left is None or sh.name in ("整页大图", "整页底") or sh.name.startswith("光池") or sh.name.startswith("高光层") or sh.name in EXEMPT:
                        continue
                    a = (Emu(sh.left).pt, Emu(sh.top).pt, Emu(sh.width).pt, Emu(sh.height).pt)
                    if a[2] * a[3] > 0.8 * W * H or a[1] >= H or a[1] + a[3] <= 0:
                        continue
                    mask[int(max(0, a[1]) / 10): int(min(H, a[1] + a[3]) / 10 + 0.999), int(max(0, a[0]) / 10): int(min(W, a[0] + a[2]) / 10 + 0.999)] = True
                ratio = mask.mean()
                if ratio > 0.60:
                    add("提示", idx, f"内容外框约占页面 {ratio * 100:.0f}%（上台讲建议 ≤ 60%）")
    # 图示多样性：6 页以上的稿子，至少要用 3 种图示（循环、金字塔、漏斗、矩阵、阵列、韦恩、环形图、图表）；全是卡片就回头检查内容结构
    if mode == "talk" and len(prs.slides) >= 6:
        kinds = set()
        for sl in prs.slides:
            for sh in walk(list(sl.shapes)):
                for k in ("循环图", "金字塔", "漏斗", "矩阵", "阵列", "韦恩图", "环形图"):
                    if sh.name.startswith(k):
                        kinds.add(k)
                if getattr(sh, "has_chart", False) and sh.has_chart:
                    kinds.add("图表")
        if len(kinds) < 3:
            add("提示", 0, f"只用了 {len(kinds)} 种图示（{', '.join(sorted(kinds)) or '无'}）；内容有循环、层级、筛选、分类、重叠、占比结构时，请用对应图示，见 references/diagrams.md")
    # 套话：删掉对内容没有任何影响的框架话（口号式标题、标签式眉题、复述前文的结尾）。关键词只是线索，最终以"删了有没有影响"为准
    FILLER = ("TAKEAWAY", "小结", "记住它", "记住这", "一张图看懂", "一图看懂", "只做一件事", "这三件事", "核心只有", "总结一下", "划重点", "一句话总结", "值得注意", "不难发现", "综上所述", "先记住一句话")
    for idx, sl in enumerate(prs.slides, 1):
        for sh in walk(list(sl.shapes)):
            if sh.has_text_frame:
                for w_ in FILLER:
                    if w_ in sh.text_frame.text:
                        add("提示", idx, f"「{sh.text_frame.text.strip()[:20]}」像套话（含\"{w_}\"）：删掉对内容有影响吗？没有就删")
    if len(faces) > 2:
        add("否", 0, f"字体家族 {len(faces)} 个：{', '.join(faces)}（≤ 2）")
    if len(chroma) > 5:
        add("提示", 0, f"文字强调色 {len(chroma)} 种（建议 ≤ 5）")
    if mode == "talk":
        for i in range(2, len(sigs)):
            if sigs[i] == sigs[i - 1] == sigs[i - 2]:
                add("提示", i + 1, "连续 3 页版式相同")
    bad = [f for f in finds if f[0] == "否"]
    if "--json" in argv:
        print(json.dumps([dict(level=a, slide=b, msg=c) for a, b, c in finds], ensure_ascii=False, indent=1))
    else:
        print(f"[lint] {pptx.name}  模式={mode}  页={len(prs.slides)}  否={len(bad)}  提示={len(finds) - len(bad)}")
        for a, b, c in finds:
            print(f"  [{a}] {'全局' if b == 0 else f'第 {b} 页'}：{c}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
