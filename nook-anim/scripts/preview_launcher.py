"""预览工作台启动器：自动把本脚本所在目录加入 sys.path，任何电脑上都不用手动设 PYTHONPATH。
python <skill>/scripts/preview_launcher.py <scene.py> [--port 8765]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from nookanim.preview import main  # noqa: E402

main()
