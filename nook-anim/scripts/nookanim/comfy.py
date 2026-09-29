"""本地 ComfyUI 客户端：Qwen Image 2.1（加速通道，文生图/编辑/透明图）与 MiniMax Music3。

出图：python <S>/run.py comfy image jobs.json --out <目录>
  jobs.json: [{"name", "prompt", "refs": [参考图路径...], "w", "h", "seed", "alpha": true, "steps": 8, "lora", "cfg"}]
  "lora": null 走原始通道（没装加速 LoRA 的机器），默认 25 步、CFG 1（同官方模板）。
  有 refs 且未给 w/h 时是编辑模式，画布跟随第一张参考图。提示词只写要什么，不写否定句。
配乐：python <S>/run.py comfy music --caption cap.txt --lyrics "[Intro]\\n[Instrumental]\\n[Outro]" --max 30 --seeds 301,302 --out <目录>
  需设置 NOOKANIM_MUSIC_WORKFLOW 指向 MiniMax Music3 的 API 格式工作流。
"""
import argparse
import copy
import json
import pathlib
import time
import urllib.parse
import urllib.request
import uuid

from . import config

ALPHA = "This is an RGBA image with transparency. {} The image has alpha channel and the background is transparent."


def _http(path, data=None, headers=None, timeout=60):
    req = urllib.request.Request(config.COMFY_HOST + path, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


_UPLOADED = {}


def upload(path):
    """同一文件只上传一次：并发任务上传同名参考图会互相覆盖，LoadImage 读到残缺文件。"""
    path = str(path)
    if path in _UPLOADED:
        return _UPLOADED[path]
    p = pathlib.Path(path)
    bnd = uuid.uuid4().hex
    body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"nookanim_{p.stem}{p.suffix}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode() + p.read_bytes() + \
           f"\r\n--{bnd}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{bnd}--\r\n".encode()
    name = json.loads(_http("/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={bnd}"}))["name"]
    _UPLOADED[path] = name
    return name


def qwen_graph(job):
    prompt = ALPHA.format(job["prompt"]) if job.get("alpha") else job["prompt"]
    # "lora": null 走原始通道（没装加速 LoRA 的机器），默认 25 步、CFG 1，与官方模板一致
    lora = job.get("lora", "p_qwen_image_2.1_8step_v0.1.safetensors")
    steps = job.get("steps", 8 if lora else 25)
    cfg = job.get("cfg", 1.0)
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "5": {"class_type": "TextEncodeQwenImage21", "inputs": {"clip": ["3", 0], "prompt": prompt, "negative_prompt": "", "resolution": job.get("ref_res", 1024), "vae": ["4", 0]}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["2", 0], "positive": ["5", 0], "negative": ["5", 1], "seed": job.get("seed", 1),
                                                    "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["4", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"nookanim/{job['name']}"}},
    }
    if lora:
        g["2"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": lora, "strength_model": 1.0}}
    else:
        g["7"]["inputs"]["model"] = ["1", 0]
    refs = job.get("refs", [])
    for i, r in enumerate(refs, 1):
        g[f"r{i}"] = {"class_type": "LoadImage", "inputs": {"image": upload(r)}}
        g["5"]["inputs"][f"images.image_{i}"] = [f"r{i}", 0]
    if refs and not job.get("w"):
        g["7"]["inputs"]["latent_image"] = ["5", 2]
    else:
        g["6"] = {"class_type": "EmptyLatentImage", "inputs": {"width": job.get("w", 1024), "height": job.get("h", 1024), "batch_size": 1}}
        g["7"]["inputs"]["latent_image"] = ["6", 0]
    return g


def _wait(pid, poll=3):
    while True:
        time.sleep(poll)
        h = json.loads(_http(f"/history/{pid}"))
        if pid in h:
            return h[pid]


def _download(item, kind, dst):
    q = f"/view?filename={urllib.parse.quote(item['filename'])}&subfolder={urllib.parse.quote(item['subfolder'])}&type={item['type']}"
    dst.write_bytes(_http(q))


def run_images(jobs, out_dir):
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pending = {}
    for job in jobs:
        r = json.loads(_http("/prompt", json.dumps({"prompt": qwen_graph(job), "client_id": "nookanim"}).encode(), {"Content-Type": "application/json"}))
        if r.get("node_errors"):
            print("node_errors", job["name"], r["node_errors"])
            continue
        pending[r["prompt_id"]] = job["name"]
        print("queued", job["name"], flush=True)
    t0 = time.time()
    for pid, name in pending.items():
        h = _wait(pid)
        if h.get("status", {}).get("status_str") != "success":
            print("FAILED", name, json.dumps(h.get("status", {}).get("messages", []), ensure_ascii=False)[:600])
            continue
        for node in h["outputs"].values():
            for im in node.get("images", []):
                _download(im, "image", out_dir / f"{name}.png")
                print(f"done {name}  {time.time() - t0:.0f}s", flush=True)


def run_music(caption, lyrics, max_dur, seeds, out_dir, prefix="music"):
    """逐条提交、逐条等待（12G 卡上长任务不要连排）。"""
    if not config.MUSIC_WORKFLOW:
        raise SystemExit("请设置 NOOKANIM_MUSIC_WORKFLOW 指向 MiniMax Music3 的 API 格式工作流")
    base = json.loads(pathlib.Path(config.MUSIC_WORKFLOW).read_text(encoding="utf-8"))
    base = base.get("prompt", base)
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for sd in seeds:
        g = copy.deepcopy(base)       # 新 payload，不改原工作流文件
        for n in g.values():
            if n["class_type"] == "MiniMaxMusic3TextEncode":
                n["inputs"].update(caption=caption, lyrics=lyrics, max_duration=float(max_dur))
            elif n["class_type"] == "SeedNode":
                n["inputs"]["seed"] = sd
            elif n["class_type"] == "SaveAudioAdvanced":
                n["inputs"]["filename_prefix"] = f"audio/nookanim_{prefix}_s{sd}"
        pid = json.loads(_http("/prompt", json.dumps({"prompt": g}).encode(), {"Content-Type": "application/json"}))["prompt_id"]
        t0 = time.time()
        h = _wait(pid, 4)
        if h.get("status", {}).get("status_str") != "success":
            print(sd, "FAILED", json.dumps(h.get("status", {}).get("messages", []))[:600])
            continue
        for node in h["outputs"].values():
            for a in node.get("audio", []):
                _download(a, "audio", out_dir / f"{prefix}_s{sd}.mp3")
                print(f"{prefix}_s{sd}: done in {time.time() - t0:.0f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("image")
    a1.add_argument("jobs")
    a1.add_argument("--out", default="out")
    a2 = sub.add_parser("music")
    a2.add_argument("--caption", required=True, help="caption 文本文件（由官方 music-caption-rewriter 生成）")
    a2.add_argument("--lyrics", default="[Intro]\n[Instrumental]\n[Instrumental]\n[Outro]")
    a2.add_argument("--max", type=float, default=30)
    a2.add_argument("--seeds", default="301")
    a2.add_argument("--out", default="music")
    a2.add_argument("--prefix", default="music")
    a = ap.parse_args()
    if a.cmd == "image":
        run_images(json.loads(pathlib.Path(a.jobs).read_text(encoding="utf-8")), a.out)
    else:
        run_music(pathlib.Path(a.caption).read_text(encoding="utf-8"), a.lyrics.replace("\\n", "\n"), a.max,
                  [int(s) for s in a.seeds.split(",")], a.out, a.prefix)


if __name__ == "__main__":
    main()
