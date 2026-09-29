"""整批渲染：8 条 B-roll（10 秒，静音）+ 8 条标题（4 秒，带音效）。用法：python build_all.py [broll|titles|all]"""
import pathlib, subprocess, sys, time, importlib
D = pathlib.Path(__file__).parent
RUN = D.parents[3] / "82_Skills" / "nook-skills" / "skills" / "nook-anim" / "scripts" / "run.py"
OUT_B, OUT_T = D.parent / "成片" / "Broll", D.parent / "成片" / "标题"
BROLL = [("broll_01_code", "broll-01_本质就是代码"), ("broll_02_tiers", "broll-02_三档"), ("broll_03_steps", "broll-03_画原型截图拼接"),
         ("broll_04_puppet", "broll-04_皮影戏"), ("broll_05_styles", "broll-05_六种风格"), ("broll_06_beats", "broll-06_画面对音乐"),
         ("broll_07_flow", "broll-07_skill流程"), ("broll_08_judgment", "broll-08_判断自己做")]
TITLES = [("title00_main", "title-00_主标题"), ("title01_code", "title-01_代码动画"), ("title02_imgcode", "title-02_图加代码动画"),
          ("title03_deploy", "title-03_部署环境"), ("title04_skill", "title-04_视频skill"), ("title05_music", "title-05_音乐音效"),
          ("title06_case", "title-06_真实案例"), ("title07_end", "title-07_结尾")]


def run(scene, out, audio=None):
    cmd = [sys.executable, str(RUN), "render", f"{scene}.py", "video", "--out", str(out)]
    if audio:
        cmd += ["--audio", audio]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=D, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    print(("OK  " if r.returncode == 0 else "FAIL"), scene, round(time.time() - t0), "s", flush=True)
    if r.returncode:
        print((r.stdout[-800:] + r.stderr[-800:]).encode("ascii", "replace").decode(), flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    OUT_B.mkdir(parents=True, exist_ok=True); OUT_T.mkdir(parents=True, exist_ok=True); (D / "audio").mkdir(exist_ok=True)
    if what in ("titles", "all") or what.startswith("titles:"):
        sys.path.insert(0, str(D))
        only = what.split(":", 1)[1].split(",") if what.startswith("titles:") else None
        for scene, name in TITLES:
            if only and scene not in only:
                continue
            mod = importlib.import_module(scene)
            mod.T.audio(D / "audio" / f"{scene}.wav", root=[72, 72, 74, 69, 76, 71, 74, 76][[s for s, _ in TITLES].index(scene)])
            run(scene, OUT_T / f"{name}.mp4", f"audio/{scene}.wav")
    if what in ("broll", "all"):
        for scene, name in BROLL:
            run(scene, OUT_B / f"{name}.mp4")
