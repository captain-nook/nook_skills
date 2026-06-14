#!/usr/bin/env node

import { ProxyAgent, setGlobalDispatcher } from "undici";
import crypto from "node:crypto";
import fsSync from "node:fs";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const proxy = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
if (proxy) {
  setGlobalDispatcher(new ProxyAgent(proxy));
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const serverRoot = path.resolve(__dirname, "..");
const envPath = path.join(serverRoot, ".env");

if (fsSync.existsSync(envPath)) {
  const envText = fsSync.readFileSync(envPath, "utf8");
  for (const line of envText.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) continue;
    const index = trimmed.indexOf("=");
    const key = trimmed.slice(0, index).trim();
    const value = trimmed.slice(index + 1).trim().replace(/^["']|["']$/g, "");
    if (key && process.env[key] === undefined) process.env[key] = value;
  }
}

const outputDir = path.resolve(serverRoot, process.env.IMAGE_OUTPUT_DIR || "output");

const tasks = new Map();

const config = {
  baseUrl: (process.env.IMAGE_API_BASE_URL || "https://sub.jarodfund.xyz/v1").replace(/\/$/, ""),
  apiKey: process.env.IMAGE_API_KEY || "",
  model: process.env.IMAGE_MODEL || "gpt-image-2",
  responseFormat: process.env.IMAGE_RESPONSE_FORMAT || "b64_json",
  dryRun: (process.env.IMAGE_DRY_RUN || "true").toLowerCase() !== "false"
};

function jsonText(payload) {
  return {
    content: [{ type: "text", text: JSON.stringify(payload, null, 2) }]
  };
}

function createTaskId() {
  const stamp = new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
  return `img_${stamp}_${crypto.randomBytes(4).toString("hex")}`;
}

async function saveBase64Png(taskId, b64Json, index) {
  await fs.mkdir(outputDir, { recursive: true });
  const suffix = index !== undefined ? `_${index}` : "";
  const imagePath = path.join(outputDir, `${taskId}${suffix}.png`);
  await fs.writeFile(imagePath, Buffer.from(b64Json, "base64"));
  return imagePath;
}

function getImageMimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  return "image/png";
}

async function runImageTask(task) {
  task.status = "processing";
  task.updated_at = new Date().toISOString();

  try {
    if (config.dryRun) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      task.status = "succeeded";
      task.image_paths = [path.join(outputDir, `${task.task_id}.dry-run.png`)];
      task.note = "dry run only; no API call was made";
      task.updated_at = new Date().toISOString();
      return;
    }

    if (!config.apiKey) {
      throw new Error("IMAGE_API_KEY is required when IMAGE_DRY_RUN=false");
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 300000);

    let response;
    if (task.mode === "image_to_image") {
      if (!task.input_image_path) {
        throw new Error("input_image_path is required for image_to_image mode");
      }
      const imageBytes = await fs.readFile(task.input_image_path);
      const form = new FormData();
      form.append("model", config.model);
      form.append("prompt", task.prompt);
      form.append("size", task.size);
      form.append("response_format", config.responseFormat);
      form.append("n", String(task.n));
      form.append("image[]", new Blob([imageBytes], { type: getImageMimeType(task.input_image_path) }), path.basename(task.input_image_path));
      response = await fetch(`${config.baseUrl}/images/edits`, {
        method: "POST",
        signal: controller.signal,
        headers: { "Authorization": `Bearer ${config.apiKey}` },
        body: form
      }).finally(() => clearTimeout(timeout));
    } else {
      response = await fetch(`${config.baseUrl}/images/generations`, {
        method: "POST",
        signal: controller.signal,
        headers: { "Authorization": `Bearer ${config.apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          model: config.model,
          prompt: task.prompt,
          size: task.size,
          response_format: config.responseFormat,
          n: task.n
        })
      }).finally(() => clearTimeout(timeout));
    }

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`image API failed: HTTP ${response.status} ${body.slice(0, 500)}`);
    }

    const data = await response.json();
    const items = data?.data;
    if (!Array.isArray(items) || items.length === 0) {
      throw new Error("image API response did not include data[]");
    }

    const savedPaths = [];
    const saveErrors = [];
    for (let i = 0; i < items.length; i++) {
      const b64Json = items[i]?.b64_json;
      if (!b64Json) { saveErrors.push(`image ${i}: no b64_json`); continue; }
      try {
        const savedPath = await saveBase64Png(task.task_id, b64Json, items.length > 1 ? i : undefined);
        savedPaths.push(savedPath);
      } catch (e) {
        saveErrors.push(`image ${i}: ${e.message}`);
      }
    }

    task.image_paths = savedPaths;
    if (savedPaths.length > 0) task.image_path = savedPaths[0];
    task.status = savedPaths.length > 0 ? "succeeded" : "failed";
    if (saveErrors.length > 0) task.error = saveErrors.join("; ");
    task.updated_at = new Date().toISOString();
  } catch (error) {
    task.status = "failed";
    task.error = error instanceof Error ? error.message : String(error);
    task.updated_at = new Date().toISOString();
  }
}

const mcp = new McpServer({
  name: "nook-image-gpt",
  version: "0.1.0"
});

mcp.registerTool(
  "submit_image_task",
  {
    title: "Submit image task",
    description: "Create a local image task and return immediately with a task_id. Supports text-to-image and image-to-image.",
    inputSchema: {
      prompt: z.string().min(1),
      size: z.enum(["1024x1024", "2048x2048", "2048x1152", "3840x2160", "2160x3840"]).default("1024x1024"),
      n: z.number().int().min(1).max(4).default(1),
      mode: z.enum(["text_to_image", "image_to_image"]).default("text_to_image"),
      input_image_path: z.string().optional()
    }
  },
  async ({ prompt, size, n, mode, input_image_path }) => {
    const task = {
      task_id: createTaskId(),
      status: "queued",
      mode,
      prompt,
      size,
      n,
      input_image_path: input_image_path || null,
      estimated_wait: config.dryRun ? 1 : 60,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    tasks.set(task.task_id, task);
    setTimeout(() => runImageTask(task), 0);
    return jsonText({
      task_id: task.task_id,
      status: task.status,
      estimated_wait: task.estimated_wait
    });
  }
);

mcp.registerTool(
  "get_image_result",
  {
    title: "Get image result",
    description: "Check local image task status by task_id.",
    inputSchema: {
      task_id: z.string().min(1)
    }
  },
  async ({ task_id }) => {
    const task = tasks.get(task_id);
    if (!task) {
      return jsonText({
        task_id,
        status: "not_found",
        error: "No task exists for this task_id in the current server process"
      });
    }
    return jsonText({
      task_id: task.task_id,
      status: task.status,
      estimated_wait: task.status === "succeeded" || task.status === "failed" ? 0 : task.estimated_wait,
      image_path: task.image_path || null,
      image_paths: task.image_paths || null,
      error: task.error || null,
      note: task.note || null,
      updated_at: task.updated_at
    });
  }
);

const transport = new StdioServerTransport();
await mcp.connect(transport);
