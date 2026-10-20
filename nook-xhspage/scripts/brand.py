"""品牌设置：第一次使用时必须设置一次（用默认船长，或设置自己的账号名、IP 人物和 Logo），之后不再询问。
设置存在 ~/.nook-xhspage/brand.json，素材复制到 ~/.nook-xhspage/brand/。"""
import json
import shutil

import paths

DEFAULT_ACCOUNT = "船长的角落 · AI 提效"      # 船长款的账号名
MINT_ACCOUNT = "我的 AI 笔记"                  # 通用款的占位账号名，建议用 --name 改成自己的
ASK = """品牌还没有设置。第一次使用要先问用户这四件事，答完运行一次 setup，之后不会再问：
  1. 有没有自己的 IP 人物形象？（透明底 PNG，最好有抱臂、讲解、邀请三个姿态；没有也可以不用人物）
  2. 有没有自己的 Logo？（浅色底和深色底各一张最好；没有也可以不用）
  3. 账号名叫什么？（船票风印在票根上，其他风格画在封面左上角的小标签里，如“某某的角落 · AI 提效”）
  4. 默认用哪种视觉风格？有四套：mint 薄荷（明亮清爽的薄荷色，通用款默认）、paper 手账（奶油纸底）、dark 深色、ticket 船票风（蓝白，每页是一张船票，底部票根印账号名和条码）。每篇图文还可以按内容另选，这里问的是没有特别理由时用哪套。
如果用户暂时都没有，或想先试试，就用内置的通用款（IP 人物「薄荷」+ 薄荷风格，任何人开箱即用，账号名可以只改名字）：
  python xhs.py setup --default [--name "你的账号名"]
设置自己的：
  python xhs.py setup --name "账号名" --pose-a 人物a.png [--pose-b 人物b.png --pose-c 人物c.png] [--logo-light 浅底logo.png --logo-dark 深底logo.png] [--theme mint|paper|dark|ticket]
没有人物就加 --no-person，没有 Logo 就加 --no-logo。
"""


def configured():
    return paths.BRAND_CONFIG.exists()


def load():
    """返回品牌信息；未设置时返回 None。"""
    if not configured():
        return None
    cfg = json.loads(paths.BRAND_CONFIG.read_text(encoding="utf-8"))
    if cfg.get("mode") in ("default", "captain"):
        d = paths.DEFAULT_BRAND
        return dict(account=cfg.get("account") or DEFAULT_ACCOUNT, has_person=True, has_logo=True, dir=d, mode="captain", default_theme=cfg.get("default_theme", "ticket"))
    if cfg.get("mode") == "mint":
        return dict(account=cfg.get("account") or MINT_ACCOUNT, has_person=True, has_logo=True, dir=paths.MINT_BRAND, mode="mint", default_theme=cfg.get("default_theme", "mint"))
    d = paths.USER_BRAND
    return dict(account=cfg["account"], has_person=cfg["has_person"], has_logo=cfg["has_logo"], dir=d, mode="custom", default_theme=cfg.get("default_theme", "ticket"))


def status_text():
    b = load()
    if not b:
        return "品牌：未设置"
    return (f"品牌：已设置（{ {'captain': '船长款', 'mint': '通用款薄荷'}.get(b['mode'], '自定义') }），账号名「{b['account']}」，"
            f"人物{'有' if b['has_person'] else '无'}，Logo{'有' if b['has_logo'] else '无'}，默认风格 {b['default_theme']}。")


def setup(a):
    paths.HOME.mkdir(parents=True, exist_ok=True)
    if a.default:
        cfg = {"mode": "mint", "account": a.name or MINT_ACCOUNT, "default_theme": a.theme or "mint"}
        paths.BRAND_CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
        return f"已设置为通用款（IP 人物薄荷，薄荷风格），账号名「{cfg['account']}」。想换成自己的名字：python xhs.py setup --default --name \"你的账号名\"。之后不会再问。"
    if a.captain:
        cfg = {"mode": "captain", "account": a.name or DEFAULT_ACCOUNT, "default_theme": a.theme or "ticket"}
        paths.BRAND_CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
        return "已设置为船长款（作者本人的品牌）。之后不会再问。"
    if not a.name:
        raise SystemExit("缺少账号名：加 --name \"账号名\"；或用 --default 使用默认品牌。")
    if not a.no_person and not a.pose_a:
        raise SystemExit("没有给人物图：加 --pose-a 人物.png；没有人物就加 --no-person。")
    if not a.no_logo and not a.logo_light:
        raise SystemExit("没有给 Logo：加 --logo-light 浅底logo.png（深色底版 --logo-dark 可选）；没有 Logo 就加 --no-logo。")
    d = paths.USER_BRAND
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)

    def cp(src, name):
        p = __import__("pathlib").Path(src)
        if not p.is_file():
            raise SystemExit(f"找不到文件：{src}")
        shutil.copy(p, d / name)
    if not a.no_person:
        cp(a.pose_a, "pose_a.png")
        cp(a.pose_b or a.pose_a, "pose_b.png")
        cp(a.pose_c or a.pose_b or a.pose_a, "pose_c.png")
    if not a.no_logo:
        cp(a.logo_light, "logo_light.png")
        cp(a.logo_dark or a.logo_light, "logo_dark.png")
    cfg = {"mode": "custom", "account": a.name, "has_person": not a.no_person, "has_logo": not a.no_logo, "default_theme": a.theme or "ticket"}
    paths.BRAND_CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    return f"已设置自定义品牌「{a.name}」。之后不会再问。"
