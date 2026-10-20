"""统一路径：全部相对 skill 目录或用户目录，不含任何本机绝对路径。
输出目录：环境变量 NOOK_XHS_OUT，默认当前目录下的 output/。
品牌设置存在用户目录 ~/.nook-xhspage/（环境变量 NOOK_XHS_HOME 可改），设置一次后不再询问。"""
import os
import pathlib

SKILL = pathlib.Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"
FONTS = ASSETS / "fonts"
LIB = ASSETS / "library"
EXAMPLES = ASSETS / "examples"
DEFAULT_BRAND = ASSETS / "brand" / "default"      # 作者本人的船长款（--captain）
MINT_BRAND = ASSETS / "brand" / "mint"            # 通用款：薄荷（--default，任何人开箱即用）
THEME_DIR = ASSETS / "themes"
HOME = pathlib.Path(os.environ.get("NOOK_XHS_HOME") or (pathlib.Path.home() / ".nook-xhspage"))
BRAND_CONFIG = HOME / "brand.json"
USER_BRAND = HOME / "brand"
OUT = pathlib.Path(os.environ.get("NOOK_XHS_OUT", pathlib.Path.cwd() / "output"))


def _brand_dir():
    """渲染用的品牌文件夹：自定义用用户目录；mode=mint 或还没设置用通用款薄荷；mode=default（旧配置）和 captain 用船长款。"""
    import json
    if BRAND_CONFIG.exists():
        try:
            mode = json.loads(BRAND_CONFIG.read_text(encoding="utf-8")).get("mode")
        except ValueError:
            mode = None
        if mode == "custom" and USER_BRAND.exists():
            return USER_BRAND
        if mode in ("default", "captain"):
            return DEFAULT_BRAND
    return MINT_BRAND


BRAND_DIR = _brand_dir()
