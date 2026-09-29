"""通用启动器：python <skill>/scripts/run.py <模块> [参数...]
例：python run.py render <scene.py> sheet --every 1.5
    python run.py music <音乐.mp3> --dur 20 --end-by 19.3 --anchors 3,6
    python run.py comfy image jobs.json --out 素材
自动把本脚本所在目录加入 sys.path，另一台电脑上同样可用。
"""
import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
mod = sys.argv[1]
sys.argv = [f"nookanim.{mod}"] + sys.argv[2:]
runpy.run_module(f"nookanim.{mod}", run_name="__main__")
