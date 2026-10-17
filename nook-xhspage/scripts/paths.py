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
DEFAULT_BRAND = ASSETS / "brand" / "default"
HOME = pathlib.Path(os.environ.get("NOOK_XHS_HOME") or (pathlib.Path.home() / ".nook-xhspage"))
BRAND_CONFIG = HOME / "brand.json"
USER_BRAND = HOME / "brand"
OUT = pathlib.Path(os.environ.get("NOOK_XHS_OUT", pathlib.Path.cwd() / "output"))
# 渲染用的品牌文件夹：已设置自定义品牌用用户目录，否则用内置默认（船长）
BRAND_DIR = USER_BRAND if (BRAND_CONFIG.exists() and (USER_BRAND).exists()) else DEFAULT_BRAND
