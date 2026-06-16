#!/usr/bin/env python
"""Small HTTP wrapper for sharing nook-zimage with trusted users."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import threading
import time
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
GENERATE = ROOT / "scripts" / "generate.py"

spec = importlib.util.spec_from_file_location("nook_zimage_generate", GENERATE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {GENERATE}")
generate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_module)

tasks: dict[str, dict] = {}
tasks_lock = threading.Lock()


def json_response(handler: BaseHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def html_response(handler: BaseHTTPRequestHandler, body: str, status: int = 200) -> None:
    raw = body.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def text_response(handler: BaseHTTPRequestHandler, text: str, status: int = 200) -> None:
    raw = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def page() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>nook-zimage</title>
  <style>
    body { margin: 0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Microsoft YaHei", sans-serif; background: #eef3ee; color: #151515; }
    main { max-width: 860px; margin: 0 auto; padding: 40px 20px 64px; }
    h1 { font-size: 34px; margin: 0 0 18px; }
    form { display: grid; gap: 14px; background: white; border: 1px solid #dbe5dc; border-radius: 14px; padding: 20px; }
    label { display: grid; gap: 8px; font-weight: 700; }
    textarea, input, select, button { font: inherit; border-radius: 10px; border: 1px solid #cbd8cc; padding: 12px 14px; }
    textarea { min-height: 150px; resize: vertical; }
    button { border: 0; background: #0f8f7f; color: white; font-weight: 800; cursor: pointer; }
    img { max-width: 100%; border-radius: 14px; margin-top: 20px; box-shadow: 0 16px 48px rgba(0,0,0,.12); }
    pre { white-space: pre-wrap; background: #111; color: #fff; padding: 16px; border-radius: 12px; }
  </style>
</head>
<body>
  <main>
    <h1>nook-zimage</h1>
    <form id="form">
      <label>Prompt
        <textarea name="prompt" required>clean poster background, soft light, no text, no logo, no watermark</textarea>
      </label>
      <label>Size
        <select name="size">
          <option>1024x1024</option>
          <option>1080x1440</option>
          <option>720x1280</option>
          <option>1280x720</option>
        </select>
      </label>
      <label>Token
        <input name="token" type="password" placeholder="如果服务端设置了 token，请填写" />
      </label>
      <button>快速生成</button>
    </form>
    <pre id="status"></pre>
    <div id="result"></div>
  </main>
  <script>
    const form = document.querySelector("#form");
    const statusEl = document.querySelector("#status");
    const resultEl = document.querySelector("#result");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      resultEl.innerHTML = "";
      statusEl.textContent = "提交中...";
      const payload = Object.fromEntries(new FormData(form).entries());
      const submitted = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).then(r => r.json());
      if (submitted.error) {
        statusEl.textContent = submitted.error;
        return;
      }
      statusEl.textContent = JSON.stringify(submitted, null, 2);
      const started = Date.now();
      while (Date.now() - started < 360000) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        const data = await fetch(`/api/tasks/${submitted.task_id}?token=${encodeURIComponent(payload.token || "")}`).then(r => r.json());
        statusEl.textContent = JSON.stringify(data, null, 2);
        if (data.status === "succeeded") {
          resultEl.innerHTML = `<img src="${data.image_url}" alt="generated image" />`;
          return;
        }
        if (data.status === "failed") return;
      }
    });
  </script>
</body>
</html>"""


def authorized(handler: BaseHTTPRequestHandler, token_value: str) -> bool:
    if not token_value:
        return True
    parsed = urlparse(handler.path)
    query_token = parse_qs(parsed.query).get("token", [""])[0]
    header_token = handler.headers.get("X-Zimage-Token", "")
    return query_token == token_value or header_token == token_value


def task_worker(task_id: str, prompt: str, size: str) -> None:
    with tasks_lock:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["updated_at"] = time.time()
    try:
        output = ROOT / "output" / "share" / f"{task_id}.jpg"
        image_path = generate_module.generate_image(prompt, size, str(output), timeout=300)
        with tasks_lock:
            tasks[task_id].update(status="succeeded", image_path=image_path, updated_at=time.time())
    except Exception as exc:
        with tasks_lock:
            tasks[task_id].update(status="failed", error=str(exc), updated_at=time.time())


def make_handler(token_value: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                html_response(self, page())
                return
            if parsed.path.startswith("/api/tasks/"):
                if not authorized(self, token_value):
                    json_response(self, {"error": "unauthorized"}, HTTPStatus.UNAUTHORIZED)
                    return
                task_id = parsed.path.rsplit("/", 1)[-1]
                with tasks_lock:
                    task = dict(tasks.get(task_id, {}))
                if not task:
                    json_response(self, {"task_id": task_id, "status": "not_found"}, HTTPStatus.NOT_FOUND)
                    return
                if task.get("image_path"):
                    task["image_url"] = f"/images/{Path(task['image_path']).name}"
                json_response(self, task)
                return
            if parsed.path.startswith("/images/"):
                name = Path(parsed.path).name
                image_path = ROOT / "output" / "share" / name
                if not image_path.exists():
                    text_response(self, "not found", HTTPStatus.NOT_FOUND)
                    return
                body = image_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(str(image_path))[0] or "application/octet-stream")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            text_response(self, "not found", HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/api/generate":
                text_response(self, "not found", HTTPStatus.NOT_FOUND)
                return
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except Exception:
                json_response(self, {"error": "invalid json"}, HTTPStatus.BAD_REQUEST)
                return
            if token_value and payload.get("token") != token_value:
                json_response(self, {"error": "unauthorized"}, HTTPStatus.UNAUTHORIZED)
                return
            prompt = str(payload.get("prompt", "")).strip()
            size = str(payload.get("size", "1024x1024")).strip()
            if not prompt:
                json_response(self, {"error": "prompt is required"}, HTTPStatus.BAD_REQUEST)
                return
            task_id = f"zshare_{int(time.time())}_{os.urandom(3).hex()}"
            with tasks_lock:
                tasks[task_id] = {
                    "task_id": task_id,
                    "status": "queued",
                    "prompt": prompt,
                    "size": size,
                    "created_at": time.time(),
                    "updated_at": time.time(),
                }
            threading.Thread(target=task_worker, args=(task_id, prompt, size), daemon=True).start()
            json_response(self, {"task_id": task_id, "status": "queued", "estimated_wait": 20})

        def log_message(self, fmt: str, *args) -> None:
            print(f"{self.address_string()} - {html.escape(fmt % args)}")

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description="Share nook-zimage through a small HTTP server.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Use 0.0.0.0 only on trusted networks.")
    parser.add_argument("--port", type=int, default=7860, help="Bind port")
    parser.add_argument("--token", default=os.getenv("ZIMAGE_SHARE_TOKEN", ""), help="Optional shared access token")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), make_handler(args.token))
    print(f"nook-zimage share server: http://{args.host}:{args.port}")
    if args.token:
        print("Access token is enabled.")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
