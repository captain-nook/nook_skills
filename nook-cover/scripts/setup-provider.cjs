#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const readline = require("readline");
const { spawnSync } = require("child_process");

const root = path.resolve(__dirname, "..");
const envFile = path.join(root, ".env");
const skillsRoot = path.resolve(root, "..", "..");

const tools = [
  {
    key: "zimage",
    label: "nook-zimage",
    envKey: "NOOK_ZIMAGE_PATH",
    candidates: [
      path.join(skillsRoot, "nook-zimage", "nook-zimage"),
      path.join(skillsRoot, "nook-zimage")
    ],
    setup: "setup.js",
    hint: "ModelScope 免费/低成本通道，通常需要 MS_API_KEY。"
  },
  {
    key: "qwen",
    label: "nook-qwen-image",
    envKey: "NOOK_QWEN_IMAGE_PATH",
    candidates: [
      path.join(skillsRoot, "nook-qwen-image")
    ],
    setup: "setup.js",
    hint: "Qwen-Image 中文海报通道，通常需要 MS_API_KEY。"
  },
  {
    key: "image2",
    label: "nook-image2-gpt",
    envKey: "NOOK_IMAGE2_GPT_PATH",
    candidates: [
      path.join(skillsRoot, "nook-image2-gpt")
    ],
    setup: "setup.js",
    hint: "高质量 image2 / 图生图通道，通常需要 IMAGE_API_KEY 和可选 IMAGE_API_BASE_URL。"
  }
];

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function ask(question, fallback = "") {
  return new Promise((resolve) => {
    const suffix = fallback ? ` [${fallback}]` : "";
    rl.question(`${question}${suffix}: `, (answer) => resolve((answer || fallback).trim()));
  });
}

function mask(value) {
  if (!value) return "";
  if (value.length <= 8) return "********";
  return `${value.slice(0, 4)}...${value.slice(-4)}`;
}

function detectTool(tool) {
  return tool.candidates.find((candidate) => fs.existsSync(candidate)) || "";
}

function hasSetup(toolPath, setupFile) {
  return toolPath && fs.existsSync(path.join(toolPath, setupFile));
}

function runToolSetup(tool, toolPath) {
  const setupFile = path.join(toolPath, tool.setup);
  if (!fs.existsSync(setupFile)) {
    console.log(`跳过 ${tool.label}：未找到 ${setupFile}`);
    return;
  }

  console.log("");
  console.log(`开始配置 ${tool.label}`);
  console.log(tool.hint);
  console.log("密钥会写入该原子工具自己的 .env，不会写入 nook-cover。");
  const result = spawnSync(process.execPath, [setupFile], {
    cwd: toolPath,
    stdio: "inherit"
  });
  if (result.status !== 0) {
    console.log(`${tool.label} 配置未完成，可稍后手动运行：node ${setupFile}`);
  }
}

async function main() {
  console.log("nook-cover 交互式配置");
  console.log("本脚本配置 nook-cover 如何找到外部出图工具。");
  console.log("API key / base URL 仍由各原子出图工具自己的 .env 管理。");
  console.log("");

  const outputDir = await ask("默认输出目录", "./output");
  const defaultProvider = await ask("默认素材路线 none/zimage/qwen/image2", "none");
  const configured = {};

  for (const tool of tools) {
    const detected = detectTool(tool);
    const prompt = `${tool.label} 路径，未安装可留空`;
    configured[tool.envKey] = await ask(prompt, detected);
  }

  const lines = [
    "# nook-cover only stores routing information.",
    "# Provider API keys and base URLs belong to each atomic tool's own .env.",
    `NOOK_COVER_OUTPUT_DIR=${outputDir}`,
    `NOOK_COVER_DEFAULT_PROVIDER=${defaultProvider}`,
    ...tools.map((tool) => `${tool.envKey}=${configured[tool.envKey] || ""}`),
    ""
  ];

  fs.writeFileSync(envFile, lines.join("\n"), "utf8");

  console.log("");
  console.log(`已写入 ${envFile}`);
  console.log(`默认路线: ${defaultProvider}`);
  for (const tool of tools) {
    const toolPath = configured[tool.envKey] || "";
    const setupState = hasSetup(toolPath, tool.setup) ? "可运行 setup.js" : "未找到 setup.js";
    console.log(`${tool.label}: ${mask(toolPath) || "未配置"} (${setupState})`);
  }
  console.log("");

  const shouldSetupTools = await ask("是否现在逐个配置已找到的原子出图工具？y/N", "N");
  if (/^y(es)?$/i.test(shouldSetupTools)) {
    for (const tool of tools) {
      const toolPath = configured[tool.envKey] || "";
      if (hasSetup(toolPath, tool.setup)) runToolSetup(tool, toolPath);
    }
  } else {
    console.log("稍后可手动运行：");
    for (const tool of tools) {
      const toolPath = configured[tool.envKey] || "";
      if (hasSetup(toolPath, tool.setup)) {
        console.log(`  cd ${toolPath}`);
        console.log("  node setup.js");
      }
    }
  }

  console.log("");
  console.log("完成。nook-cover 现在知道外部工具路径；密钥仍留在各原子工具自己的 .env。");
}

main()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  })
  .finally(() => rl.close());
