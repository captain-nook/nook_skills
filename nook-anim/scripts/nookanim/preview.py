"""预览工作台：浏览器里拖时间轴当场渲染任意一帧、跳镜头、重载场景代码、看整片渲染进度、点击取坐标。
python <S>/preview_launcher.py scene.py [--port 8765]  → http://127.0.0.1:8765

点击画面会显示该点的"场景坐标"（依赖场景提供 camera_matrix(t) → (A, s)），用于标注平面四角、锚点、落点。
"""
import argparse
import importlib
import json
import pathlib
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
import numpy as np

from .render import frame_at, load_scene

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>nookanim 预览</title>
<style>
:root{--bg:#16181c;--panel:#22252b;--fg:#e8e6e1;--mut:#9aa0a8;--acc:#1e5bd8;--acc2:#ffd23f}
body{margin:0;background:var(--bg);color:var(--fg);font:14px "Microsoft YaHei",system-ui,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:16px}
#v{width:100%;aspect-ratio:16/9;background:#000;display:block;border-radius:8px;cursor:crosshair}
.row{display:flex;gap:8px;align-items:center;margin-top:12px;flex-wrap:wrap}
button{background:var(--panel);color:var(--fg);border:1px solid #3a3e46;border-radius:6px;padding:6px 12px;cursor:pointer;font:inherit}
button.on{background:var(--acc);border-color:var(--acc)}
input[type=range]{flex:1;accent-color:var(--acc2);min-width:200px}
.t{font-variant-numeric:tabular-nums;min-width:110px}.mut{color:var(--mut);font-size:12px}
h3{margin:20px 0 6px;font-size:15px}
.bar{flex:1;background:#2c3038;border-radius:6px;height:14px;overflow:hidden}.bar div{height:100%;width:0;background:var(--acc2)}
</style></head><body><div class="wrap">
<img id="v" alt="当前帧">
<div class="row"><button id="play">▶ 播放</button><input id="s" type="range" min="0" max="__MAX__" step="__STEP__" value="0">
<span class="t" id="tt">00.00s</span><span class="mut" id="ms"></span></div>
<div class="row" id="shots"></div>
<div class="row"><button id="rl">重载代码</button><span class="mut" id="pick">点击画面取场景坐标</span></div>
<h3>渲染进度</h3>
<div class="row"><div class="bar"><div id="pbar"></div></div><span class="t" id="ptxt" style="min-width:260px">未在渲染</span></div>
<img id="latest" alt="正在渲染的最新一帧" style="margin-top:8px;max-width:480px">
</div><script>
const shots=__SHOTS__;
const v=document.getElementById('v'),s=document.getElementById('s'),tt=document.getElementById('tt'),ms=document.getElementById('ms'),pb=document.getElementById('play');
let playing=false,busy=false,want=null,ver=0;
function show(t){want=t;tt.textContent=(+t).toFixed(2).padStart(5,'0')+'s';if(!busy)load();}
function load(){if(want===null)return;const t=want;want=null;busy=true;const t0=performance.now();
 v.onload=()=>{busy=false;ms.textContent='渲染 '+Math.round(performance.now()-t0)+' ms';
   if(playing&&want===null){let n=+s.value+1/12;if(n>+s.max)n=0;s.value=n;show(n);}else load();};
 v.src='/frame?t='+(+t).toFixed(4)+'&v='+ver;}
s.oninput=()=>show(s.value);
pb.onclick=()=>{playing=!playing;pb.textContent=playing?'❚❚ 暂停':'▶ 播放';pb.classList.toggle('on',playing);if(playing)show(s.value);};
for(const [t,n] of shots){const b=document.createElement('button');b.textContent=n;b.onclick=()=>{s.value=t+0.3;show(s.value)};document.getElementById('shots').appendChild(b);}
document.getElementById('rl').onclick=async()=>{await fetch('/reload');ver++;show(s.value);};
v.onclick=async(e)=>{const r=v.getBoundingClientRect();const x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;
 const p=await (await fetch(`/pick?t=${(+s.value).toFixed(4)}&x=${x}&y=${y}`)).json();
 document.getElementById('pick').textContent=p.scene?`场景坐标 (${p.scene[0]}, ${p.scene[1]})　屏幕 (${p.screen[0]}, ${p.screen[1]})`:`屏幕 (${p.screen[0]}, ${p.screen[1]})（场景未提供 camera_matrix）`;
 navigator.clipboard&&p.scene&&navigator.clipboard.writeText(`(${p.scene[0]}, ${p.scene[1]})`);};
async function poll(){try{const r=await fetch('/progress');if(r.ok){const p=await r.json();
 const pct=Math.round(p.frame/p.total*100);document.getElementById('pbar').style.width=pct+'%';
 document.getElementById('ptxt').textContent=p.frame>=p.total?`${p.out} 已完成（${p.total} 帧，用时 ${p.elapsed}s）`:`${p.out}：${p.frame}/${p.total} 帧（${pct}%），已用 ${p.elapsed}s，剩余约 ${p.eta}s`;
 document.getElementById('latest').src='/latest?'+Date.now();}}catch(e){} setTimeout(poll,2000);}
show(0);poll();
</script></body></html>"""


def serve(scene_path, port):
    state = {"scene": load_scene(scene_path), "cache": {}}
    lock = threading.Lock()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, body, ctype, code=200):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            sc = state["scene"]
            u = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(u.query)
            if u.path == "/":
                page = PAGE.replace("__SHOTS__", json.dumps([[s, n] for s, n in getattr(sc, "SHOTS", [])], ensure_ascii=False))
                page = page.replace("__MAX__", f"{sc.DUR - 1 / sc.FPS:.4f}").replace("__STEP__", f"{1 / sc.FPS:.5f}")
                return self.send(page.encode("utf-8"), "text/html; charset=utf-8")
            if u.path == "/reload":
                with lock:
                    state["scene"] = load_scene(scene_path)
                    state["cache"].clear()
                return self.send(b"ok", "text/plain")
            if u.path == "/frame":
                t = round(float(q["t"][0]) * sc.FPS) / sc.FPS
                with lock:
                    if t not in state["cache"]:
                        fr = cv2.resize(frame_at(sc, t, True), (960, int(960 * sc.H / sc.W)), interpolation=cv2.INTER_AREA)
                        state["cache"][t] = cv2.imencode(".jpg", fr, [cv2.IMWRITE_JPEG_QUALITY, 88])[1].tobytes()
                return self.send(state["cache"][t], "image/jpeg")
            if u.path == "/pick":
                t, x, y = float(q["t"][0]), float(q["x"][0]) * sc.W, float(q["y"][0]) * sc.H
                res = {"screen": [round(x), round(y)]}
                if hasattr(sc, "camera_matrix"):
                    A, _ = sc.camera_matrix(t)
                    p = np.linalg.inv(np.vstack([A, [0, 0, 1]])) @ np.array([x, y, 1.0])
                    res["scene"] = [round(p[0]), round(p[1])]
                return self.send(json.dumps(res).encode(), "application/json")
            if u.path in ("/progress", "/latest"):
                f = sc.__dir__ / ("progress.json" if u.path == "/progress" else "latest.jpg")
                if not f.exists():
                    return self.send(b"", "text/plain", 404)
                return self.send(f.read_bytes(), "application/json" if u.path == "/progress" else "image/jpeg")
            self.send(b"", "text/plain", 404)

    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    srv.daemon_threads = True
    print(f"preview on http://127.0.0.1:{port}", flush=True)
    srv.serve_forever()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    serve(a.scene, a.port)


if __name__ == "__main__":
    main()
