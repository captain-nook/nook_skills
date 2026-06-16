#!/usr/bin/env node

import { ProxyAgent, setGlobalDispatcher } from "undici";
import crypto from "node:crypto";
import fsSync from "node:fs";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const proxy = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
if (proxy) setGlobalDispatcher(new ProxyAgent(proxy));

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");

function loadEnvFile(envPath) {
  if (!fsSync.existsSync(envPath)) return;
  const envText = fsSync.readFileSync(envPath, "utf8");
  for (const line of envText.split(/\r?\n/)) {
    const trimmed = line.trim().replace(/^\uFEFF/, "");
    if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) continue;
    const index = trimmed.indexOf("=");
    const key = trimmed.slice(0, index).trim();
    const value = trimmed.slice(index + 1).trim().replace(/^["']|["']$/g, "");
    if (key && process.env[key] === undefined) process.env[key] = value;
  }
}

loadEnvFile(path.join(root, ".env"));
loadEnvFile(path.join(__dirname, ".env"));

function resolveOutputDir(value) {
  const raw = value || "output";
  return path.isAbsolute(raw) ? raw : path.resolve(root, raw);
}

const outputDir = resolveOutputDir(process.env.QWEN_IMAGE_OUTPUT_DIR);
const tasksDir = path.join(outputDir, ".tasks");
const DRY_RUN_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=";

const config = {
  baseUrl: (process.env.MS_API_BASE_URL || "https://api-inference.modelscope.cn").replace(/\/$/, ""),
  apiKey: process.env.MS_API_KEY || "",
  model: process.env.MS_IMAGE_MODEL || "Qwen/Qwen-Image",
  editModel: process.env.QWEN_IMAGE_EDIT_MODEL || "Qwen/Qwen-Image-Edit-2509",
  dryRun: (process.env.QWEN_IMAGE_DRY_RUN || "true").toLowerCase() !== "false",
  timeoutMs: Number(process.env.QWEN_IMAGE_TIMEOUT_MS || 600000),
};

const tasks = new Map();

function jsonText(payload) {
  return { content: [{ type: "text", text: JSON.stringify(payload, null, 2) }] };
}

function parseSize(size) {
  const match = String(size || "").match(/^\s*(\d{2,5})\s*[xX*]\s*(\d{2,5})\s*$/);
  if (!match) throw new Error("size must look like 1024x1024 or 720*1280");
  const width = Number(match[1]);
  const height = Number(match[2]);
  if (width < 128 || height < 128 || width > 4096 || height > 4096) {
    throw new Error("size width/height must be between 128 and 4096");
  }
  return { width, height, normalized: `${width}x${height}` };
}

function createTaskId() {
  const stamp = new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
  return `qwen_img_${stamp}_${crypto.randomBytes(4).toString("hex")}`;
}

function createEditTaskId() {
  const stamp = new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
  return `qwen_edit_${stamp}_${crypto.randomBytes(4).toString("hex")}`;
}

function taskFile(taskId) {
  return path.join(tasksDir, `${taskId}.json`);
}

async function persistTask(task) {
  await fs.mkdir(tasksDir, { recursive: true });
  await fs.writeFile(taskFile(task.task_id), JSON.stringify(task, null, 2), "utf8");
}

async function readPersistedTask(taskId) {
  try {
    const task = JSON.parse(await fs.readFile(taskFile(taskId), "utf8"));
    tasks.set(task.task_id, task);
    return task;
  } catch {
    return null;
  }
}

async function saveImageBuffer(taskId, buffer, index, contentType = "image/jpeg", overridePath) {
  if (overridePath) {
    const dir = path.dirname(overridePath);
    if (dir) await fs.mkdir(dir, { recursive: true });
    await fs.writeFile(overridePath, buffer);
    return overridePath;
  }
  await fs.mkdir(outputDir, { recursive: true });
  const suffix = index !== undefined ? `_${index}` : "";
  const ext = contentType.includes("png") ? ".png" : contentType.includes("webp") ? ".webp" : ".jpg";
  const imagePath = path.join(outputDir, `${taskId}${suffix}${ext}`);
  await fs.writeFile(imagePath, buffer);
  return imagePath;
}

function resolveExplicitOutputPath(raw) {
  if (!raw) return null;
  const expanded = raw.replace(/^~/, os.homedir());
  return path.isAbsolute(expanded) ? expanded : path.resolve(root, expanded);
}

async function resolveInputImage(raw) {
  if (!raw) throw new Error("input_image is required for an edit task");
  if (/^data:/i.test(raw)) return raw;
  if (/^https?:\/\//i.test(raw)) return raw;
  const expanded = raw.replace(/^~/, os.homedir());
  const abs = path.isAbsolute(expanded) ? expanded : path.resolve(root, expanded);
  if (!fsSync.existsSync(abs)) throw new Error(`input_image file not found: ${abs}`);
  const buf = await fs.readFile(abs);
  const ext = path.extname(abs).toLowerCase();
  const mime = ext === ".png" ? "image/png" : ext === ".webp" ? "image/webp" : ext === ".gif" ? "image/gif" : "image/jpeg";
  return `data:${mime};base64,${buf.toString("base64")}`;
}

async function runQwenImageTask(task) {
  task.status = "processing";
  task.updated_at = new Date().toISOString();
  await persistTask(task);

  try {
    if (config.dryRun) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      const imagePath = await saveImageBuffer(task.task_id, Buffer.from(DRY_RUN_PNG, "base64"), undefined, "image/png", task.output_path);
      task.status = "succeeded";
      task.image_path = imagePath;
      task.image_paths = [imagePath];
      task.note = "dry run only; no ModelScope API call was made";
      task.updated_at = new Date().toISOString();
      await persistTask(task);
      return;
    }

    if (!config.apiKey) throw new Error("MS_API_KEY is required when QWEN_IMAGE_DRY_RUN=false");

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.timeoutMs);
    const response = await fetch(`${config.baseUrl}/v1/images/generations`, {
      method: "POST",
      signal: controller.signal,
      headers: {
        "Authorization": `Bearer ${config.apiKey}`,
        "Content-Type": "application/json",
        "X-ModelScope-Async-Mode": "true",
      },
      body: JSON.stringify({
        model: config.model,
        prompt: task.prompt,
        size: `${task.width}x${task.height}`,
        width: task.width,
        height: task.height,
        parameters: {
          size: `${task.width}x${task.height}`,
          prompt_extend: true,
        },
      }),
    }).finally(() => clearTimeout(timeout));

    if (!response.ok) throw new Error(`ModelScope submit failed: HTTP ${response.status} ${(await response.text()).slice(0, 500)}`);
    const submitted = await response.json();
    const remoteTaskId = submitted.task_id;
    if (!remoteTaskId) throw new Error(`ModelScope response did not include task_id: ${JSON.stringify(submitted)}`);
    task.remote_task_id = remoteTaskId;
    task.updated_at = new Date().toISOString();
    await persistTask(task);

    const started = Date.now();
    while (Date.now() - started < config.timeoutMs) {
      await new Promise((resolve) => setTimeout(resolve, 3000));
      const poll = await fetch(`${config.baseUrl}/v1/tasks/${remoteTaskId}`, {
        headers: {
          "Authorization": `Bearer ${config.apiKey}`,
          "X-ModelScope-Task-Type": "image_generation",
        },
      });
      if (!poll.ok) throw new Error(`ModelScope poll failed: HTTP ${poll.status} ${(await poll.text()).slice(0, 500)}`);
      const data = await poll.json();
      if (data.task_status === "FAILED") throw new Error(data.message || "ModelScope task failed");
      if (data.task_status !== "SUCCEED") continue;

      const outputImages = Array.isArray(data.output_images) ? data.output_images : [];
      if (!outputImages.length) throw new Error("ModelScope task succeeded but output_images is empty");

      const paths = [];
      for (let i = 0; i < Math.min(outputImages.length, task.n); i++) {
        const url = typeof outputImages[i] === "string" ? outputImages[i] : outputImages[i]?.url;
        if (!url) continue;
        const imageResponse = await fetch(url);
        if (!imageResponse.ok) throw new Error(`image download failed: HTTP ${imageResponse.status}`);
        const contentType = imageResponse.headers.get("content-type") || "image/jpeg";
        const buffer = Buffer.from(await imageResponse.arrayBuffer());
        const explicit = task.output_path && task.n === 1 ? task.output_path : null;
        paths.push(await saveImageBuffer(task.task_id, buffer, task.n > 1 ? i : undefined, contentType, explicit));
      }
      if (!paths.length) throw new Error("No image URL could be saved");

      task.status = "succeeded";
      task.image_path = paths[0];
      task.image_paths = paths;
      task.updated_at = new Date().toISOString();
      await persistTask(task);
      return;
    }

    throw new Error(`timed out waiting for ModelScope task ${remoteTaskId}`);
  } catch (error) {
    task.status = "failed";
    task.error = error instanceof Error ? error.message : String(error);
    task.updated_at = new Date().toISOString();
    await persistTask(task);
  }
}

async function runQwenImageEditTask(task) {
  task.status = "processing";
  task.updated_at = new Date().toISOString();
  await persistTask(task);

  try {
    if (config.dryRun) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      const imagePath = await saveImageBuffer(task.task_id, Buffer.from(DRY_RUN_PNG, "base64"), undefined, "image/png", task.output_path);
      task.status = "succeeded";
      task.image_path = imagePath;
      task.image_paths = [imagePath];
      task.note = "dry run only; no ModelScope API call was made";
      task.updated_at = new Date().toISOString();
      await persistTask(task);
      return;
    }

    if (!config.apiKey) throw new Error("MS_API_KEY is required when QWEN_IMAGE_DRY_RUN=false");
    const imageUrl = await resolveInputImage(task.input_image);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.timeoutMs);
    const response = await fetch(`${config.baseUrl}/v1/images/generations`, {
      method: "POST",
      signal: controller.signal,
      headers: {
        "Authorization": `Bearer ${config.apiKey}`,
        "Content-Type": "application/json",
        "X-ModelScope-Async-Mode": "true",
      },
      body: JSON.stringify({
        model: config.editModel,
        prompt: task.prompt,
        image_url: imageUrl,
        size: task.size ? `${task.width}x${task.height}` : undefined,
        parameters: { size: `${task.width}x${task.height}` },
      }),
    }).finally(() => clearTimeout(timeout));

    if (!response.ok) throw new Error(`ModelScope submit failed: HTTP ${response.status} ${(await response.text()).slice(0, 500)}`);
    const submitted = await response.json();
    const remoteTaskId = submitted.task_id;
    if (!remoteTaskId) throw new Error(`ModelScope response did not include task_id: ${JSON.stringify(submitted)}`);
    task.remote_task_id = remoteTaskId;
    task.updated_at = new Date().toISOString();
    await persistTask(task);

    const started = Date.now();
    while (Date.now() - started < config.timeoutMs) {
      await new Promise((resolve) => setTimeout(resolve, 3000));
      const poll = await fetch(`${config.baseUrl}/v1/tasks/${remoteTaskId}`, {
        headers: {
          "Authorization": `Bearer ${config.apiKey}`,
          "X-ModelScope-Task-Type": "image_generation",
        },
      });
      if (!poll.ok) throw new Error(`ModelScope poll failed: HTTP ${poll.status} ${(await poll.text()).slice(0, 500)}`);
      const data = await poll.json();
      if (data.task_status === "FAILED") throw new Error(data.message || "ModelScope edit task failed");
      if (data.task_status !== "SUCCEED") continue;

      const outputImages = Array.isArray(data.output_images) ? data.output_images : [];
      if (!outputImages.length) throw new Error("ModelScope edit task succeeded but output_images is empty");
      const url = typeof outputImages[0] === "string" ? outputImages[0] : outputImages[0]?.url;
      if (!url) throw new Error("No image URL in edit response");

      const imageResponse = await fetch(url);
      if (!imageResponse.ok) throw new Error(`image download failed: HTTP ${imageResponse.status}`);
      const contentType = imageResponse.headers.get("content-type") || "image/jpeg";
      const buffer = Buffer.from(await imageResponse.arrayBuffer());
      const imagePath = await saveImageBuffer(task.task_id, buffer, undefined, contentType, task.output_path);

      task.status = "succeeded";
      task.image_path = imagePath;
      task.image_paths = [imagePath];
      task.updated_at = new Date().toISOString();
      await persistTask(task);
      return;
    }

    throw new Error(`timed out waiting for ModelScope edit task ${remoteTaskId}`);
  } catch (error) {
    task.status = "failed";
    task.error = error instanceof Error ? error.message : String(error);
    task.updated_at = new Date().toISOString();
    await persistTask(task);
  }
}

function publicTask(task) {
  return {
    task_id: task.task_id,
    kind: task.kind || "image",
    remote_task_id: task.remote_task_id || null,
    status: task.status,
    estimated_wait: task.status === "succeeded" || task.status === "failed" ? 0 : task.estimated_wait,
    image_path: task.image_path || null,
    image_paths: task.image_paths || null,
    output_path: task.output_path || null,
    input_image: task.input_image && !/^data:/i.test(task.input_image) ? task.input_image : null,
    error: task.error || null,
    note: task.note || null,
    updated_at: task.updated_at,
  };
}

const mcp = new McpServer({ name: "nook-qwen-image", version: "0.1.0" });

mcp.registerTool(
  "submit_qwen_image_task",
  {
    title: "Submit Qwen-Image task",
    description: "Generate a high-quality image with ModelScope Qwen-Image (best for Chinese posters, covers, typography-heavy editorial art, and printed material). Returns a local task_id immediately. Use for any image request that needs strong Chinese text rendering or higher quality than Z-Image-Turbo. For cheap fast drafts, batch tests, or low-stakes background images, prefer nook-zimage instead. Pass output_path to save the result to a user-specified absolute path; otherwise the image is written under output/ and shown inline via file:/// URL.",
    inputSchema: {
      prompt: z.string().min(1).describe("Text prompt. For Chinese text inside the image, write the exact characters in quotes inside the prompt."),
      size: z.string().default("1080x1440").describe("WxH in pixels, e.g. 1024x1024, 720x1280, 1080x1440. Min 128, max 4096."),
      n: z.number().int().min(1).max(1).default(1).describe("Number of images. Currently fixed at 1."),
      output_path: z.string().optional().describe("Optional absolute path (or path relative to the project root) for the final image, e.g. 'D:/images/cat.jpg' or '~/Pictures/cat.jpg'. If omitted, the image is saved under <project>/output/ and the absolute path is returned in image_path."),
    },
  },
  async ({ prompt, size, n, output_path }) => {
    const parsed = parseSize(size);
    const task = {
      task_id: createTaskId(),
      status: "queued",
      prompt,
      size: parsed.normalized,
      width: parsed.width,
      height: parsed.height,
      n,
      output_path: resolveExplicitOutputPath(output_path),
      estimated_wait: config.dryRun ? 1 : 60,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    tasks.set(task.task_id, task);
    await persistTask(task);
    setTimeout(() => runQwenImageTask(task), 0);
    return jsonText({ task_id: task.task_id, status: task.status, estimated_wait: task.estimated_wait, output_path: task.output_path });
  }
);

mcp.registerTool(
  "get_qwen_image_result",
  {
    title: "Get Qwen-Image result",
    description: "Check a previously submitted Qwen-Image task by its task_id. Poll every 5-10 seconds while status is queued or processing. When status becomes 'succeeded', the response contains image_path / image_paths; render the first one inline with a file:/// Markdown image tag.",
    inputSchema: { task_id: z.string().min(1).describe("The task_id returned by submit_qwen_image_task.") },
  },
  async ({ task_id }) => {
    const task = tasks.get(task_id) || await readPersistedTask(task_id);
    if (!task) return jsonText({ task_id, status: "not_found", error: "No task exists for this task_id" });
    return jsonText(publicTask(task));
  }
);

mcp.registerTool(
  "submit_qwen_image_edit_task",
  {
    title: "Submit Qwen-Image edit task",
    description: "Edit an existing image with ModelScope Qwen-Image-Edit (default: Qwen/Qwen-Image-Edit-2509). Use this to (a) re-style or re-render an image that nook-zimage or nook-qwen-image produced, (b) add or change Chinese text on top of an image, (c) change background while keeping the person, or (d) chain models: nook-zimage generates a draft, then this tool turns it into a polished cover with titles. Pass input_image as an absolute path (preferred, e.g. from a previous tool's image_path), an http(s) URL, or a data: URL. The instruction (prompt) is mandatory and should describe the edit in plain language, e.g. '把背景换成粉色樱花飘落的街道，保留人物。在顶部加上大字「春日穿搭」白色加粗。' Pass output_path to save the result to a user-specified absolute path; otherwise the image is written under output/ and shown inline via file:/// URL.",
    inputSchema: {
      input_image: z.string().min(1).describe("Absolute path, http(s) URL, or data: URL of the image to edit. Absolute file path is preferred (it gets base64-encoded automatically)."),
      prompt: z.string().min(1).describe("Edit instruction in Chinese or English. Be specific about what to keep, what to change, and what text (if any) to add."),
      size: z.string().default("1024x1024").describe("WxH in pixels, e.g. 1024x1024, 720x1280, 1024x1365. Min 128, max 4096."),
      output_path: z.string().optional().describe("Optional absolute path (or path relative to the project root) for the final image, e.g. 'D:/images/cover.jpg' or '~/Pictures/cover.jpg'."),
    },
  },
  async ({ input_image, prompt, size, output_path }) => {
    const parsed = parseSize(size);
    const task = {
      task_id: createEditTaskId(),
      kind: "edit",
      status: "queued",
      input_image,
      prompt,
      size: parsed.normalized,
      width: parsed.width,
      height: parsed.height,
      output_path: resolveExplicitOutputPath(output_path),
      estimated_wait: config.dryRun ? 1 : 90,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    tasks.set(task.task_id, task);
    await persistTask(task);
    setTimeout(() => runQwenImageEditTask(task), 0);
    return jsonText({ task_id: task.task_id, kind: task.kind, status: task.status, estimated_wait: task.estimated_wait, output_path: task.output_path });
  }
);

mcp.registerTool(
  "get_qwen_image_edit_result",
  {
    title: "Get Qwen-Image edit result",
    description: "Check a previously submitted Qwen-Image edit task by its task_id. Poll every 5-10 seconds while status is queued or processing. When status becomes 'succeeded', the response contains image_path; render it inline with a file:/// Markdown image tag.",
    inputSchema: { task_id: z.string().min(1).describe("The task_id returned by submit_qwen_image_edit_task.") },
  },
  async ({ task_id }) => {
    const task = tasks.get(task_id) || await readPersistedTask(task_id);
    if (!task) return jsonText({ task_id, status: "not_found", error: "No task exists for this task_id" });
    return jsonText(publicTask(task));
  }
);

const transport = new StdioServerTransport();
await mcp.connect(transport);
