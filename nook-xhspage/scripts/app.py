"""本地界面：给不用 agent 的人用。读写同一份方案 JSON，所见即所得。
python xhs.py ui   或双击 ui.bat → 浏览器打开 http://127.0.0.1:8770
工作文件夹默认在 ~/.nook-xhspage/work/，截图放进里面的 inputs/。只监听本机，只读写工作文件夹。"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

import brand
import paths

HERE = pathlib.Path(__file__).resolve().parent
WORK = paths.HOME / "work"
PORT = 8770

PAGE = r"""<!doctype html><html lang="zh"><meta charset="utf-8"><title>小红书图文</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;font:15px/1.6 "Microsoft YaHei",sans-serif;color:#1B2540;background:#F8F4EA}
.wrap{display:grid;grid-template-columns:minmax(380px,520px) 1fr;gap:22px;max-width:1500px;margin:0 auto;padding:20px}
h1{font-size:22px;margin:0 0 4px}.sub{color:#6B7385;font-size:13px;margin:0 0 12px}
textarea{width:100%;height:520px;border:1.5px solid #D9CFB4;border-radius:10px;padding:10px;font:13px/1.5 Consolas,monospace;background:#fff}
button{background:#1F6FEB;color:#fff;border:0;border-radius:10px;padding:10px 20px;font:700 15px "Microsoft YaHei";cursor:pointer;margin:8px 8px 8px 0}
button.g{background:#fff;color:#1B2540;border:1.5px solid #D9CFB4}button:disabled{opacity:.5}
pre{background:#fff;border:1.5px solid #D9CFB4;border-radius:10px;padding:10px;white-space:pre-wrap;font-size:13px;max-height:260px;overflow:auto}
.imgs{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}.imgs img{width:100%;border-radius:10px;border:1.5px solid #D9CFB4;background:#fff}
.tag{display:inline-block;background:#fff;border:1.5px solid #D9CFB4;border-radius:20px;padding:2px 12px;font-size:13px;margin:0 6px 6px 0}
</style>
<div class="wrap"><div>
<h1>小红书图文</h1><p class="sub" id="st"></p>
<textarea id="plan" spellcheck="false"></textarea>
<div><button id="v">校验</button><button id="r">出图</button><button class="g" id="ex">载入示例</button></div>
<p class="sub">截图放进工作文件夹的 inputs/ 里：<span id="wd"></span></p>
<pre id="msg">先点“载入示例”，改成自己的内容，再点校验和出图。</pre>
</div><div><div class="imgs" id="imgs"></div></div></div>
<script>
const $=id=>document.getElementById(id);
async function post(p,b){return await (await fetch(p,{method:'POST',body:JSON.stringify(b||{})})).json()}
async function init(){const s=await (await fetch('/api/status')).json();$('wd').textContent=s.work;
 $('st').innerHTML=s.brand_ok?'<span class="tag">'+s.brand+'</span>':'<span class="tag" style="border-color:#E55A14">品牌未设置</span> <button class="g" id="sb">用默认品牌</button>';
 if(!s.brand_ok)$('sb').onclick=async()=>{await post('/api/setup',{});init()};
 $('plan').value=s.plan||''}
$('ex').onclick=async()=>{const r=await (await fetch('/api/example')).json();$('plan').value=r.plan}
async function run(kind){$('msg').textContent='处理中……';$('v').disabled=$('r').disabled=true;
 const r=await post('/api/'+kind,{plan:$('plan').value});
 $('msg').textContent=r.text||'';$('imgs').innerHTML=(r.images||[]).map(u=>'<a href="'+u+'" target="_blank"><img src="'+u+'?t='+Date.now()+'"></a>').join('');
 $('v').disabled=$('r').disabled=false}
$('v').onclick=()=>run('validate');$('r').onclick=()=>run('render');
init();
</script></html>"""


def cli(args):
    r = subprocess.run([sys.executable, str(HERE / "xhs.py")] + args, capture_output=True, text=True, encoding="utf-8", cwd=str(WORK),
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return (r.stdout + r.stderr).strip(), r.returncode


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = unquote(urlparse(self.path).path)
        if p == "/":
            return self._send(200, PAGE, "text/html; charset=utf-8")
        if p == "/api/status":
            f = WORK / "plan.json"
            return self._send(200, json.dumps({"brand_ok": brand.configured(), "brand": brand.status_text(), "work": str(WORK),
                                               "plan": f.read_text(encoding="utf-8") if f.exists() else ""}, ensure_ascii=False))
        if p == "/api/example":
            ex = paths.SKILL / "examples" / "demo_paper.json"
            (WORK / "inputs").mkdir(parents=True, exist_ok=True)
            for f in (paths.SKILL / "examples" / "inputs").glob("*.png"):     # 示例要用的截图一起放进工作文件夹
                shutil.copy(f, WORK / "inputs" / f.name)
            return self._send(200, json.dumps({"plan": ex.read_text(encoding="utf-8")}, ensure_ascii=False))
        if p.startswith("/out/"):
            f = (WORK / "output" / p[5:]).resolve()
            if (WORK / "output").resolve() in f.parents and f.is_file():
                return self._send(200, f.read_bytes(), "image/png")
        self._send(404, "not found", "text/plain")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(n) or b"{}")
        try:
            if self.path == "/api/setup":
                return self._send(200, json.dumps({"text": cli(["setup", "--default"])[0]}, ensure_ascii=False))
            if self.path in ("/api/validate", "/api/render"):
                WORK.mkdir(parents=True, exist_ok=True)
                (WORK / "inputs").mkdir(exist_ok=True)
                try:
                    json.loads(data.get("plan", ""))
                except json.JSONDecodeError as e:
                    return self._send(200, json.dumps({"text": f"方案不是合法 JSON：第 {e.lineno} 行第 {e.colno} 列，{e.msg}"}, ensure_ascii=False))
                (WORK / "plan.json").write_text(data["plan"], encoding="utf-8")
                if self.path == "/api/validate":
                    return self._send(200, json.dumps({"text": cli(["validate", "plan.json"])[0]}, ensure_ascii=False))
                out, code = cli(["render", "plan.json", "--out", "output"])
                imgs = sorted((WORK / "output").glob("[0-9][0-9]_*.png")) if code in (0, 2) else []
                return self._send(200, json.dumps({"text": out, "images": ["/out/" + i.name for i in imgs]}, ensure_ascii=False))
        except Exception as e:  # noqa
            return self._send(200, json.dumps({"text": f"出错：{type(e).__name__}: {e}"}, ensure_ascii=False))
        self._send(404, "{}")


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "inputs").mkdir(exist_ok=True)
    srv = None
    for port in range(PORT, PORT + 10):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port), H)
            break
        except OSError:
            continue
    if srv is None:
        raise SystemExit("找不到可用端口，请关掉之前打开的窗口再试。")
    url = f"http://127.0.0.1:{port}"
    print("小红书图文界面已启动：", url, "（使用期间不要关这个窗口）")
    if not os.environ.get("NOOK_NO_BROWSER"):
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
