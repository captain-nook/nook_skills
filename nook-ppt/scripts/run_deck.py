"""run_deck：一键 生成 → PowerPoint 核验 → 自动检查 → 加动效 → 总览图。**默认只输出一份动效版**，中间文件自动清理。
python run_deck.py <build_script.py> [构建脚本的参数...]

构建脚本需要在最后打印一行  saved <pptx 路径>（slidekit 的样片脚本都是这样）。
流程（talk，有动效计划，默认）：
  构建（静态稿 + *.anim.json）→ check_deck（导出图、查溢出）→ lint_deck → animate_deck 写出动效版，
  **替换原文件**（交付物就是 <名字>.pptx，带动效）→ 删除 *.anim.json
read（无动效计划，仅在明确要"给别人看"的版本时用）：构建 → animate_deck 只加朴素淡入（原地）→ check_deck → lint_deck。
环境变量：
  NOOKPPT_KEEP=1        保留 *.anim.json 和静态稿（调试用）
  NOOKPPT_PDF=1         read 模式额外导出 PDF（默认不导出）
  NOOKPPT_CHECK_DIR     保留逐页 PNG、check.json、总览.jpg 的目录（不设置则用完即删）
构建或核验偶发"文件被占用"时自动重试。需要 Windows + PowerPoint。
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def run(cmd, retries=3, wait=3.0):
    out = ""
    for k in range(retries):
        r = subprocess.run(cmd, capture_output=True, env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        out = (r.stdout + r.stderr).decode("utf-8", "replace")
        if r.returncode == 0:
            return out, 0
        time.sleep(wait)
    return out, 1


def ps(script, *args):
    return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HERE / script), *args]


def safe_replace(src, dst, tries=6, wait=2.0):
    """用 src 覆盖 dst。Windows 上 shutil.move 在目标已存在或刚被 PowerPoint 释放时不稳，所以用 os.replace 加重试。"""
    import os
    for k in range(tries):
        try:
            os.replace(str(src), str(dst))
            return
        except OSError:
            time.sleep(wait)
    raise SystemExit(f"替换失败：{dst} 可能正被 PowerPoint 打开，请关闭后把 {src} 改名为它")


def sheet(png_dir, dst):
    from PIL import Image
    files = sorted(png_dir.glob("slide_*.png"))
    if not files:
        return
    cols = 3
    tw, th = 640, 360
    rows = (len(files) + cols - 1) // cols
    im = Image.new("RGB", (cols * (tw + 6), rows * (th + 6)), (60, 60, 60))
    for i, f in enumerate(files):
        im.paste(Image.open(f).convert("RGB").resize((tw, th)), ((i % cols) * (tw + 6), (i // cols) * (th + 6)))
    im.save(dst, quality=88)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    script, extra = sys.argv[1], sys.argv[2:]
    out, bad = run([sys.executable, script, *extra])
    m = re.findall(r"^saved (.+)$", out, flags=re.M)
    if bad or not m:
        sys.stdout.buffer.write(out[-1500:].encode("utf-8", "replace"))
        raise SystemExit("构建失败")
    pptx = pathlib.Path(m[-1].strip()).resolve()          # PowerPoint / PowerShell 需要绝对路径
    for line in out.splitlines():
        if line.startswith("[布局告警]"):
            print(line)
    import os
    keep = os.environ.get("NOOKPPT_KEEP") == "1"
    plan = pptx.with_suffix(".anim.json")
    talk = any("effect" in x for x in json.loads(plan.read_text(encoding="utf8")))
    import tempfile
    keep_check = bool(os.environ.get("NOOKPPT_CHECK_DIR"))
    chk = (pathlib.Path(os.environ["NOOKPPT_CHECK_DIR"]) / pptx.stem if keep_check else pathlib.Path(tempfile.mkdtemp(prefix="nookppt_check_"))).resolve()
    chk.mkdir(parents=True, exist_ok=True)
    pdf = ""
    if not talk:                                                     # read：先加淡入切换（原地）
        tmp = pptx.with_name(pptx.stem + ".__tmp.pptx")
        o, b = run(ps("animate_deck.ps1", "-In", str(pptx), "-Out", str(tmp), "-Plan", str(plan)))
        if not b and tmp.exists():
            safe_replace(tmp, pptx)
        if os.environ.get("NOOKPPT_PDF") == "1":
            pdf = str(pptx.with_suffix(".pdf"))
    args = ["-Pptx", str(pptx), "-OutDir", str(chk)] + (["-Pdf", pdf] if pdf else [])
    o, b = run(ps("check_deck.ps1", *args))
    ov = re.search(r"overflow=(\d+)", o)
    sm = re.search(r"slides=\d+ shapes=\d+", o)
    print(f"[核验] {pptx.name}: {sm.group(0) if sm else '?'}  overflow={ov.group(1) if ov else '?'}" + (f"  PDF={pathlib.Path(pdf).name}" if pdf else ""))
    sheet(chk, chk / "总览.jpg")
    lo, lb = run([sys.executable, str(HERE / "lint_deck.py"), str(pptx), "--png", str(chk)], retries=1)
    print(lo.strip())
    if talk:                                                          # 动效版替换原文件，交付物只有这一份
        tmp = pptx.with_name(pptx.stem + ".__anim.pptx")
        o, b = run(ps("animate_deck.ps1", "-In", str(pptx), "-Out", str(tmp), "-Plan", str(plan)))
        if b or not tmp.exists():
            raise SystemExit("加动效失败：" + o.strip()[-300:])
        if keep:
            shutil.copy(str(pptx), str(pptx.with_name(pptx.stem + "_静态稿.pptx")))
        safe_replace(tmp, pptx)
        print(f"[动效] {pptx.name}: " + ("; ".join(re.findall(r"slide \d+: effects=\d+", o)) or "ok"))
    if not keep:
        plan.unlink(missing_ok=True)
    print(f"[交付] {pptx}")
    if keep_check:
        print(f"[总览] {chk / '总览.jpg'}")
    else:
        shutil.rmtree(chk, ignore_errors=True)                        # 逐页截图、总览图是过程文件，默认用完就删


if __name__ == "__main__":
    main()
