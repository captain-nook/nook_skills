"""nook-xhspage 命令行入口。
  python xhs.py setup --status                    看品牌是否已设置；第一次使用必须先 setup
  python xhs.py setup --default | --name ...      设置品牌（一次即可）
  python xhs.py ui                                本地界面（给不用 agent 的人）
  python xhs.py selftest                          自检：词表、素材、示例、检查、出图
  python xhs.py check-themes                      三套主题的对比度自检
  python xhs.py suggest-assets plan.json          逐页判断贴纸该放还是不放，并给候选 id
  python xhs.py list-types                        列出全部页型和字段
  python xhs.py list-assets [--tag 想法] [--cat object]   列出素材库
  python xhs.py validate plan.json                只校验（含去 AI 味表达检查和 inputs/ 检查）
  python xhs.py check-post post.md                检查标题、标签、正文、删除测试记录
  python xhs.py deliver plan.json post.md         交付：方案校验、正文检查、出图，三项都过才算完成
  python xhs.py lint-text 正文.md                 检查标题、正文里的 AI 味表达
  python xhs.py preview plan.json --page 2        只出第 2 页
  python xhs.py render plan.json [--out 目录]      全量出图并拼总览图
退出码：0 通过，1 校验失败，2 出图时发现版面问题或出错，3 品牌未设置（要先问用户再 setup）。"""
import argparse
import json
import pathlib
import os
import sys

import brand
import paths
import spec

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def load(plan_path):
    p = pathlib.Path(plan_path)
    try:
        return json.loads(p.read_text(encoding="utf-8")), p.resolve().parent
    except FileNotFoundError:
        sys.exit(f"找不到方案文件：{plan_path}")
    except json.JSONDecodeError as e:
        print(f"方案文件不是合法 JSON：第 {e.lineno} 行第 {e.colno} 列，{e.msg}")
        sys.exit(1)


def cmd_list_types(a):
    print("主题：" + "；".join(f"{k} = {v}" for k, v in spec.THEMES.items()))
    print("规则：3 到 9 页；第 1 页封面类；最后一页 closing 或 back_cover；相邻两页不同型；至少 3 种页型；高亮词用 [[词]]，一个字段最多一处。\n")

    def show(fields, ind):
        for k, sp in fields.items():
            kind = {"str": f"文字≤{sp.max}字", "int": f"整数{sp.lo}~{sp.hi}", "num": "数字", "enum": "/".join(sp.values or []) if sp.values else "", "asset": "素材id",
                    "path": "文件路径", "box": "[x,y,w,h]", "arrow": "{from,to}", "list": f"列表{sp.lo}~{sp.hi}项", "obj": "对象"}[sp.kind]
            print(f"{ind}{k}{'' if sp.req else '（可省）'}：{kind}" + (f" — {sp.desc}" if sp.desc else ""))
            if sp.kind == "obj":
                show(sp.fields, ind + "    ")
            if sp.kind == "list" and sp.of.kind == "obj":
                show(sp.of.fields, ind + "    每项.")
    for t, d in spec.TYPES.items():
        print(f"## {t}  {d['cn']}（{d['role']}）用于：{d['use']}")
        show(d["fields"], "  ")
        print()


def cmd_ui(a):
    import app
    app.main()


def cmd_selftest(a):
    import selftest
    sys.exit(selftest.main())


def cmd_check_themes(a):
    import quality
    text, ok = quality.check_themes()
    print(text)
    print("全部达标" if ok else "有不达标项，调 pages_hand.py 里的颜色映射")
    sys.exit(0 if ok else 1)


def cmd_list_assets(a):
    n = 0
    for m in spec.manifest().values():
        if a.cat and m["category"] != a.cat:
            continue
        if a.tag and not any(a.tag in t for t in m["tags"] + [m["cn"]]):
            continue
        print(f'{m["id"]:<18}{m["category"]:<10}{m["cn"]:<10}{" ".join(m["tags"])}')
        n += 1
    print(f"共 {n} 个")


def need_brand():
    if not brand.configured():
        print(brand.ASK)
        sys.exit(3)


def cmd_setup(a):
    if a.status:
        print(brand.status_text())
        return
    print(brand.setup(a))


def is_demo(plan_path):
    """放在 skill 自带目录里的示例方案只做提醒级检查，其余一律强制。"""
    try:
        pathlib.Path(plan_path).resolve().relative_to(paths.SKILL.parent)
        return True
    except ValueError:
        return False


GATE_FILES = {"preview": ["facts.md", "outline.md"], "render": ["facts.md", "outline.md", "needs.md", "covers.md"]}


def gates(plan_path, level):
    """关卡文件必须和方案放在同一个文件夹里，缺一个就不出图。"""
    d = pathlib.Path(plan_path).resolve().parent
    miss = [f for f in GATE_FILES[level] if not (d / f).is_file()]
    if miss:
        print("缺少关卡文件：" + "、".join(miss))
        print("按 nook-xhswrite 的关卡顺序先做完这些文件（facts、outline、needs、covers），和 plan.json 放在同一个文件夹，再出图。不要自己补空文件。")
        sys.exit(1)


def check(plan_path):
    need_brand()
    plan, base = load(plan_path)
    errs = spec.validate(plan, base)
    if not errs and not is_demo(plan_path):
        import factcheck
        errs = factcheck.errors(plan)
    if errs:
        print(f"校验未通过，共 {len(errs)} 处：")
        for e in errs:
            print("  - " + e)
        sys.exit(1)
    return plan, base


def cmd_validate(a):
    plan, _ = check(a.plan)
    print(f"校验通过：{len(plan['pages'])} 页，主题 {plan['meta']['theme']}。")
    import decor
    import lint
    import factcheck as tr
    for w in decor.warnings(plan) + lint.warn_plan(plan) + (tr.check(plan) if is_demo(a.plan) else []):
        print("提醒：" + w)


def cmd_suggest(a):
    plan, _ = check(a.plan)
    import decor
    for i, (pg, (d, why, c)) in enumerate(zip(plan["pages"], decor.suggest(plan)), 1):
        extra = "  候选：" + "、".join(f"{x[0]}（{x[1]}）" for x in c) if c else ""
        print(f"第 {i} 页（{pg['type']}）：{d}。{why}{extra}")


def cmd_check_post(a):
    import post
    try:
        text = pathlib.Path(a.file).read_text(encoding="utf-8")
    except FileNotFoundError:
        sys.exit(f"找不到文件：{a.file}")
    errs, warns = post.check(text)
    for e in errs:
        print("  - " + e)
    for w in warns:
        print("提醒：" + w)
    if errs:
        print(f"正文包未通过，共 {len(errs)} 处")
        sys.exit(1)
    print("正文包通过。")


def cmd_deliver(a):
    plan, base = check(a.plan)
    if is_demo(a.plan):
        sys.exit("这是 skill 自带的示例方案，不能交付。把方案和关卡文件放到你自己的工作文件夹里再运行 deliver。")
    gates(a.plan, "render")
    import post
    import decor
    import factcheck as tr
    import lint
    errs, warns = post.check(pathlib.Path(a.post).read_text(encoding="utf-8"))
    if errs:
        print("正文包未通过：")
        for e in errs:
            print("  - " + e)
        sys.exit(1)
    for w in decor.warnings(plan) + lint.warn_plan(plan) + tr.check(plan) + warns:
        print("提醒：" + w)
    a.out = a.out
    cmd_render(a)
    print("交付完成：方案校验、正文检查、出图都已通过。把 post.md 的标题、标签、正文发布到平台（发布全人工）。")


def cmd_lint_text(a):
    import lint
    try:
        text = pathlib.Path(a.file).read_text(encoding="utf-8")
    except FileNotFoundError:
        sys.exit(f"找不到文件：{a.file}")
    hits = lint.lint_text(text)
    for n, w, name, hint in hits:
        print(f"第 {n} 行：命中「{w}」（{name}），{hint}")
    print(f"共 {len(hits)} 处" if hits else "未发现表面表达问题（这只查表面，仍要按自检清单读一遍）")
    sys.exit(1 if hits else 0)


def cmd_render(a, only=None):
    plan, base = check(a.plan)
    if not is_demo(a.plan):
        gates(a.plan, "preview" if only else "render")
    import render
    if a.out:
        out = pathlib.Path(a.out)
    elif os.environ.get("NOOK_XHS_OUT"):
        out = paths.OUT / (plan["meta"].get("title") or "plan")
    else:
        out = pathlib.Path(a.plan).resolve().parent / ("_preview" if only else "out")
    try:
        files, problems = render.render_pages(plan, base, out, only)
    except Exception as e:  # noqa
        print(f"出图失败：{type(e).__name__}: {e}")
        sys.exit(2)
    if not only:
        from PIL import Image
        w = 330
        h = int(1656 * w / 1242)
        cols = min(5, len(files))
        rows = -(-len(files) // cols)
        sh = Image.new("RGB", (cols * (w + 10) + 10, rows * (h + 10) + 10), (255, 255, 255))
        for i, f in enumerate(files):
            sh.paste(Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS), (10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 10)))
        sh.save(out / "overview.png")
    print(f"已生成 {len(files)} 张到 {out}")
    if problems:
        print("版面问题：")
        for p in problems:
            print("  - " + p)
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser(prog="xhs", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("setup")
    p.add_argument("--status", action="store_true")
    p.add_argument("--default", action="store_true", help="通用款（薄荷）")
    p.add_argument("--captain", action="store_true", help="船长款（作者本人的品牌）")
    p.add_argument("--name")
    for k in ("pose-a", "pose-b", "pose-c", "logo-light", "logo-dark"):
        p.add_argument("--" + k)
    p.add_argument("--theme", choices=["mint", "ticket", "paper", "dark"])
    p.add_argument("--no-person", action="store_true")
    p.add_argument("--no-logo", action="store_true")
    p.set_defaults(f=cmd_setup)
    p = sp.add_parser("suggest-assets")
    p.add_argument("plan")
    p.set_defaults(f=cmd_suggest)
    sp.add_parser("ui").set_defaults(f=cmd_ui)
    sp.add_parser("selftest").set_defaults(f=cmd_selftest)
    sp.add_parser("check-themes").set_defaults(f=cmd_check_themes)
    sp.add_parser("list-types").set_defaults(f=cmd_list_types)
    p = sp.add_parser("list-assets")
    p.add_argument("--tag")
    p.add_argument("--cat")
    p.set_defaults(f=cmd_list_assets)
    p = sp.add_parser("validate")
    p.add_argument("plan")
    p.set_defaults(f=cmd_validate)
    p = sp.add_parser("check-post")
    p.add_argument("file")
    p.set_defaults(f=cmd_check_post)
    p = sp.add_parser("deliver")
    p.add_argument("plan")
    p.add_argument("post")
    p.add_argument("--out")
    p.set_defaults(f=cmd_deliver)
    p = sp.add_parser("lint-text")
    p.add_argument("file")
    p.set_defaults(f=cmd_lint_text)
    p = sp.add_parser("preview")
    p.add_argument("plan")
    p.add_argument("--page", type=int, required=True)
    p.add_argument("--out")
    p.set_defaults(f=lambda a: cmd_render(a, only=a.page))
    p = sp.add_parser("render")
    p.add_argument("plan")
    p.add_argument("--out")
    p.set_defaults(f=cmd_render)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
