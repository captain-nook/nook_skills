"""页面小工具已提到公共位置 scripts/deckkit.py，这里保留一个转发，旧脚本仍可 from kit import Kit。"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "scripts"))
from deckkit import *       # noqa
from deckkit import Kit, cli, variant   # noqa
