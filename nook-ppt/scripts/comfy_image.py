"""comfy_image：按 jobs_*.json 批量调用本地 ComfyUI（Qwen Image 2.1）出图，不依赖其他 skill。
python comfy_image.py <jobs.json> --out <目录>

jobs.json 是一个列表，每项：{"name", "prompt", "w", "h", "seed", "alpha": true（透明底）, "lora": null（走原始通道）, "refs": [参考图路径...]}。
前提：本机 ComfyUI 已启动（默认 http://127.0.0.1:8188，可用环境变量 NOOKPPT_COMFY 改），并装有 Qwen Image 2.1 的模型
  qwen_image_2.1_int8_convrot、qwen3vl_8b_int8_convrot、qwen_image_2.1_vae_bf16，加速通道还需要 LoRA p_qwen_image_2.1_8step_v0.1。
没有 ComfyUI、或想用别的模型：把 jobs 里的 prompt 原样发给任意图像 API，按 name 存成同名 PNG（透明底要求透明 PNG）放回对应目录即可。
提示词只写要什么，不写否定句（否定句会把被否定的东西带进画面）。
"""
import argparse
import json
import os
import pathlib
import time
import urllib.parse
import urllib.request
import uuid

COMFY_HOST = os.environ.get("NOOKPPT_COMFY", "http://127.0.0.1:8188")


class config:                      # 与原来的写法保持一致，便于对照
    COMFY_HOST = COMFY_HOST


ALPHA = "This is an RGBA image with transparency. {} The image has alpha channel and the background is transparent."


def _http(path, data=None, headers=None, timeout=60):
    req = urllib.request.Request(COMFY_HOST + path, data=data, headers=headers or {})
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
    body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"nookppt_{p.stem}{p.suffix}\"\r\n"
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
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"nookppt/{job['name']}"}},
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
        r = json.loads(_http("/prompt", json.dumps({"prompt": qwen_graph(job), "client_id": "nookppt"}).encode(), {"Content-Type": "application/json"}))
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




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    run_images(json.loads(pathlib.Path(a.jobs).read_text(encoding="utf8")), a.out)


if __name__ == "__main__":
    main()
