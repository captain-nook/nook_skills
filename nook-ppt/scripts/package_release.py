"""package_release：生成发布目录（本地的 skill 目录原样保留，不删任何文件）。
python package_release.py <目标目录> [--full]

带上：
  代码、文档、examples、references、scripts
  每个风格包的 .py / .md / .json（主题、小工具、出图任务、提示词）
  风格包的素材（deco/ 图标、tips/ 船长表情、raw/ 出好的图、底图）：图标和表情缩小到够用的尺寸（图标长边 640px，船长表情 900px）
  素材库 assets/library/：icons_ink、icons_blue、editorial_icons、captain_poses、deco（可复用的图标、船长姿势、装饰）
  raw/ 里的图：只带样片用到的和 make_bg.py 需要的输入（清单 assets/release_manifest.json）；--full 时带全部
不带：
  字体文件（只带 assets/fonts/README.md，用户自行下载安装）
  由 make_bg.py 生成的底图（首次使用时由主题自动生成）
  课程标题字 library/titles、故事素材 library/story_*、课程图标和品牌图 captain-class/brand、来源清单
  缓存（_cache、_skin_cache）、__pycache__、examples/output
参数：
  --full      raw/ 里的图全部带上（默认只带用到的）
"""
import json
import pathlib
import re
import shutil
import sys

from PIL import Image

SK = pathlib.Path(__file__).resolve().parents[1]
IMG = {".png", ".jpg", ".jpeg", ".webp"}
LIB_KEEP = {"icons_ink", "icons_blue", "editorial_icons", "captain_poses", "deco"}
SIZE_BY_DIR = {"captain_poses": 1000, "tips": 900, "deco": 640, "icons_ink": 640, "icons_blue": 640, "editorial_icons": 640}
EXCLUDE_DIRS = {"__pycache__", "_cache", "_skin_cache", ".git"}


def generated_bg(style_dir):
    """主题里 _ensure_bg([...]) 列出的底图是 make_bg.py 生成的，发布包不带。"""
    t = style_dir / "theme.py"
    if not t.exists():
        return set()
    m = re.search(r"_ensure_bg\((\[.*?\])\)", t.read_text(encoding="utf8"), re.S)
    return set(eval(m.group(1))) if m else set()


def lite_keep():
    m = json.loads((SK / "assets/release_manifest.json").read_text(encoding="utf8"))
    keep = {x.lower() for x in m["used"]}
    for mk in (SK / "assets/styles").glob("*/make_bg.py"):             # make_bg.py 读取的 raw 输入
        for name in re.findall(r'"([\w\-]+(?:\.png)?)"', mk.read_text(encoding="utf8")):
            for cand in (name, name + ".png"):
                p = mk.parent / "raw" / cand
                if p.is_file():
                    keep.add(p.relative_to(SK / "assets").as_posix().lower())
    return keep


def copy_img(src, dst, max_side):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    im.save(dst, optimize=True)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    dest = pathlib.Path(sys.argv[1])
    lite = "--full" not in sys.argv
    if dest.exists():
        shutil.rmtree(dest)
    keep = lite_keep() if lite else None
    n = 0
    for p in sorted(SK.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(SK)
        parts = rel.parts
        if any(x in EXCLUDE_DIRS for x in parts) or p.suffix == ".pyc":
            continue
        if parts[0] == "examples" and len(parts) > 1 and parts[1] == "output":
            continue
        out = dest / rel
        if parts[0] == "assets" and len(parts) > 1:
            sub = parts[1]
            if sub == "fonts":
                if p.suffix.lower() in (".ttf", ".otf"):                     # 字体不随库提供
                    continue
            elif sub == "library":
                lib = parts[2] if len(parts) > 2 else ""
                if len(parts) == 3:                                   # library 根下的文件：只带 README
                    if p.name != "README.md":
                        continue
                elif lib not in LIB_KEEP or p.suffix.lower() not in IMG:
                    continue
                else:
                    copy_img(p, out, SIZE_BY_DIR.get(lib, 640))
                    n += 1
                    continue
            elif sub == "styles":
                if "brand" in parts:                                  # 课程标题字和课程图标，不属于通用素材
                    continue
                if p.suffix.lower() in IMG and len(parts) == 4 and p.name in generated_bg(SK / "assets/styles" / parts[2]):
                    continue                                              # 代码生成的底图
                if p.suffix.lower() in IMG:
                    sd = next((d for d in parts[:-1] if d in SIZE_BY_DIR), None)
                    if sd:
                        copy_img(p, out, SIZE_BY_DIR[sd])
                        n += 1
                        continue
                    if lite and rel.relative_to("assets").as_posix().lower() not in keep:
                        continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, out)
        n += 1
    tot = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
    print(f"发布目录：{dest}  文件 {n} 个  共 {tot / 1e6:.0f} MB" + ("（raw/ 只带用到的）" if lite else "（含全部 raw/）") + "（不含字体）")


if __name__ == "__main__":
    main()
