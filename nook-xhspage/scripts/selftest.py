"""自检：改完代码后运行，确认词表、素材、示例、检查、出图都正常。python xhs.py selftest
所有检查通过退出码 0。用临时的品牌设置目录，不动用户自己的设置。"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import paths

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = []


def ok(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("通过  " if cond else "失败  ") + name + (f"  {detail}" if detail and not cond else ""))


def run(args, env, timeout=600):
    return subprocess.run([sys.executable, str(HERE / "xhs.py")] + args, capture_output=True, text=True, encoding="utf-8", env=env, timeout=timeout, cwd=str(HERE))


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="xhs_selftest_"))
    env = dict(os.environ, NOOK_XHS_HOME=str(tmp / "home"), NOOK_XHS_OUT=str(tmp / "out"), PYTHONIOENCODING="utf-8")
    ex = paths.SKILL / "examples"
    try:
        # 1 品牌设置的强制关卡
        r = run(["validate", str(ex / "demo_paper.json")], env)
        ok("未设置品牌时拒绝执行（退出码 3）", r.returncode == 3, r.stdout[-200:])
        r = run(["setup", "--default"], env)
        ok("默认品牌可设置", r.returncode == 0, r.stdout + r.stderr)
        # 2 词表和渲染函数一致
        import render
        import spec
        missing = [t for t in spec.TYPES if t not in render.RENDERERS]
        ok("每个页型都有渲染函数", not missing, str(missing))
        # 3 素材库
        man = json.loads((paths.LIB / "manifest.json").read_text(encoding="utf-8"))["items"]
        bad = [m["id"] for m in man if not (paths.LIB / m["file"]).is_file()]
        ok(f"素材库 {len(man)} 个条目的文件都在", not bad, str(bad[:5]))
        ids = [m["id"] for m in man]
        ok("素材 id 没有重复", len(ids) == len(set(ids)))
        # 4 主题对比度
        r = run(["check-themes"], env)
        ok("三套主题对比度全部达标", r.returncode == 0, r.stdout[-300:])
        # 5 示例方案通过，错误方案被拦
        for f in sorted(ex.glob("demo*.json")) + sorted((paths.SKILL.parent / "nook-xhswrite" / "references" / "plans").glob("*.json") if (paths.SKILL.parent / "nook-xhswrite").exists() else []):
            r = run(["validate", str(f)], env)
            ok(f"校验通过 {f.name}", r.returncode == 0, (r.stdout + r.stderr)[-200:])
        r = run(["validate", str(ex / "bad_plan.json")], env)
        n = len(re.findall(r"^\s+- ", r.stdout, re.M))
        ok("错误方案被拦下且报出多处问题", r.returncode == 1 and n >= 8, f"退出码 {r.returncode}，{n} 处")
        # 5b 强制检查：自带目录之外的方案，编造日期、数字、定论词必须被拦
        work = tmp / "work"
        work.mkdir()
        shutil.copy(ex / "bad_glm_plan.json", work / "plan.json")
        r = run(["validate", str(work / "plan.json")], env)
        ok("编造日期和数字的方案被强制拦下", r.returncode == 1 and "找不到" in r.stdout and "真相" in r.stdout, r.stdout[-300:])
        shutil.copytree(ex / "inputs", work / "inputs")
        shutil.copy(ex / "demo_paper.json", work / "nofacts.json")
        r = run(["validate", str(work / "nofacts.json")], env)
        ok("没有事实清单的方案被拦下", r.returncode == 1 and "meta.facts" in r.stdout, r.stdout[-300:])
        r = run(["render", str(work / "plan.json")], env)
        ok("缺关卡文件时不出图", r.returncode == 1, r.stdout[-200:])
        r = run(["deliver", str(ex / "demo_paper.json"), str(ex / "demo_post.md")], env)
        ok("自带示例不能当成交付", r.returncode != 0)
        # 6 每套风格出一份图，没有版面问题
        for name in ("demo_paper.json", "demo_dark.json", "demo_ticket.json", "demo_new_types.json"):
            r = run(["render", str(ex / name), "--out", str(tmp / "out" / name)], env)
            ok(f"出图无版面问题 {name}", r.returncode == 0, (r.stdout + r.stderr)[-300:])
        # 7 正文检查
        good = ex / "demo_post.md"
        r = run(["check-post", str(good)], env)
        ok("示例正文包通过检查", r.returncode == 0, r.stdout[-300:])
        badp = tmp / "bad_post.md"
        badp.write_text("## 标题\n- 搜索型：太短\n## 标签\n#a\n## 正文\n**值得注意的是**，这不是工具而是能力。\n## 删除测试记录\n无\n## 事实对照\n无\n", encoding="utf-8")
        r = run(["check-post", str(badp)], env)
        ok("错误正文包被拦下", r.returncode == 1)
        # 8 没有本机路径和个人信息
        pat = re.compile(r"[A-Za-z]:\\|[A-Za-z]:/Users|wanlly|nook_vault|moosa")
        hits = []
        for f in paths.SKILL.rglob("*"):
            if f.is_file() and f.suffix in (".py", ".md", ".json", ".bat", ".txt") and "__pycache__" not in f.parts and "publish-checklist" not in f.name and f.name != "selftest.py":
                t = f.read_text(encoding="utf-8", errors="ignore")
                if pat.search(t):
                    hits.append(str(f.relative_to(paths.SKILL)))
        ok("skill 目录里没有本机路径和个人信息", not hits, str(hits[:5]))
        # 9 字体许可文件
        ok("字体许可文件在位", (paths.FONTS / "LICENSE-fonts.txt").is_file())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [n for n, c, _ in RESULTS if not c]
    print(f"\n共 {len(RESULTS)} 项，通过 {len(RESULTS) - len(bad)} 项" + (f"，失败 {len(bad)} 项" if bad else "，全部通过"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
