#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "fs/promises";
import path from "path";

const API_KEY = process.env.IMAGE_API_KEY;
if (!API_KEY) {
  console.error("IMAGE_API_KEY environment variable is required");
  process.exit(1);
}

const API_BASE = process.env.IMAGE_API_BASE || "https://sub.jarodfund.xyz";
const GENERATIONS_API_URL = `${API_BASE}/v1/images/generations`;
const EDITS_API_URL = `${API_BASE}/v1/images/edits`;
const MODEL = "gpt-image-2";

const MIME_TYPES = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
};

function getMimeType(filePath) {
  return MIME_TYPES[path.extname(filePath).toLowerCase()] || "application/octet-stream";
}

async function appendImageFile(form, fieldName, filePath) {
  if (!filePath || typeof filePath !== "string") {
    throw new Error(`${fieldName} must be a file path string`);
  }

  const absPath = path.resolve(filePath);
  const buffer = await fs.readFile(absPath);
  const blob = new Blob([buffer], { type: getMimeType(absPath) });
  form.append(fieldName, blob, path.basename(absPath));
}

function parseImagePaths(args) {
  const imagePaths = [];

  if (typeof args?.image_path === "string") {
    imagePaths.push(args.image_path);
  }

  if (Array.isArray(args?.image_paths)) {
    for (const imagePath of args.image_paths) {
      if (typeof imagePath !== "string") {
        throw new Error("image_paths must be an array of file path strings");
      }
      imagePaths.push(imagePath);
    }
  }

  return [...new Set(imagePaths)];
}

async function parseImageResponse(response) {
  if (!response.ok) {
    const errorText = await response.text();
    let detail = errorText;
    try {
      const parsed = JSON.parse(errorText);
      detail = parsed.error?.message || parsed.error || errorText;
    } catch {}
    throw new Error(`Image API error (${response.status}): ${detail}`);
  }

  const data = await response.json();
  if (!Array.isArray(data.data)) {
    throw new Error("Image API response did not include a data array");
  }
  return data.data;
}

async function returnImages(images, saveToDir) {
  if (saveToDir) {
    const absDir = path.resolve(saveToDir);
    await fs.mkdir(absDir, { recursive: true });
    const savedFiles = [];
    for (let i = 0; i < images.length; i++) {
      const b64 = images[i].b64_json;
      const url = images[i].url;
      let buffer;

      if (b64) {
        buffer = Buffer.from(b64, "base64");
      } else if (url) {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Failed to download generated image (${response.status})`);
        }
        buffer = Buffer.from(await response.arrayBuffer());
      } else {
        throw new Error("Image API response did not include b64_json or url");
      }

      const filename = `nook_gpt_${Date.now()}_${i}.png`;
      const filepath = path.join(absDir, filename);
      await fs.writeFile(filepath, buffer);
      savedFiles.push(filepath);
    }
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ saved_to: savedFiles }),
        },
      ],
    };
  }

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify({
          images: images.map((img) => ({
            b64_json: img.b64_json,
            url: img.url,
          })),
        }),
      },
    ],
  };
}

const server = new Server(
  { name: "nook-image-gpt", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "generate_image",
      description: `Generate images using ${MODEL} via the relay API. Supports 1K to 4K resolutions. Returns either base64 (default) or saves to a directory.`,
      inputSchema: {
        type: "object",
        properties: {
          prompt: {
            type: "string",
            description: "Image generation prompt (describe what you want to generate)",
          },
          size: {
            type: "string",
            description: "Image resolution. Options: 1024x1024 (1K), 2048x2048 (2K), 2048x1152 (2K wide), 3840x2160 (4K wide), 2160x3840 (4K tall)",
            default: "1024x1024",
          },
          n: {
            type: "number",
            description: "Number of images to generate (default 1, max 10)",
            default: 1,
          },
          save_to_dir: {
            type: "string",
            description: "Directory to save images as PNG files. If not set, returns base64 data. Recommended for large images to avoid transport issues.",
          },
        },
        required: ["prompt"],
      },
    },
    {
      name: "edit_image",
      description: `Edit or transform one or more input images using ${MODEL} via the relay API. Sends multipart image files to the image edits endpoint and returns base64 or saved PNG files.`,
      inputSchema: {
        type: "object",
        properties: {
          prompt: {
            type: "string",
            description: "Edit instruction or image-to-image prompt",
          },
          image_path: {
            type: "string",
            description: "Path to a single source image file (PNG, JPG, JPEG, or WEBP)",
          },
          image_paths: {
            type: "array",
            items: { type: "string" },
            description: "Paths to one or more source image files. Use this for multi-image references.",
          },
          mask_path: {
            type: "string",
            description: "Optional PNG mask path for targeted edits. Transparent areas are edited.",
          },
          size: {
            type: "string",
            description: "Output resolution. Options depend on the relay/model; default 1024x1024.",
            default: "1024x1024",
          },
          n: {
            type: "number",
            description: "Number of images to generate (default 1, max 10)",
            default: 1,
          },
          save_to_dir: {
            type: "string",
            description: "Directory to save images as PNG files. If not set, returns base64 data.",
          },
        },
        required: ["prompt"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name !== "generate_image" && name !== "edit_image") {
    throw new Error(`Unknown tool: ${name}`);
  }

  const prompt = args?.prompt;
  const size = args?.size || "1024x1024";
  const n = Math.min(Math.max(args?.n || 1, 1), 10);
  const saveToDir = args?.save_to_dir;

  if (!prompt || typeof prompt !== "string") {
    throw new Error("prompt is required and must be a string");
  }

  if (name === "generate_image") {
    const response = await fetch(GENERATIONS_API_URL, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: MODEL,
        prompt,
        size,
        n,
        response_format: "b64_json",
      }),
    });

    const images = await parseImageResponse(response);
    return returnImages(images, saveToDir);
  }

  const imagePaths = parseImagePaths(args);
  if (imagePaths.length === 0) {
    throw new Error("edit_image requires image_path or image_paths");
  }

  const form = new FormData();
  form.append("model", MODEL);
  form.append("prompt", prompt);
  form.append("size", size);
  form.append("n", String(n));

  for (const imagePath of imagePaths) {
    await appendImageFile(form, "image", imagePath);
  }

  if (args?.mask_path) {
    await appendImageFile(form, "mask", args.mask_path);
  }

  const response = await fetch(EDITS_API_URL, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
    },
    body: form,
  });

  const images = await parseImageResponse(response);
  return returnImages(images, saveToDir);
});

const transport = new StdioServerTransport();
await server.connect(transport);
