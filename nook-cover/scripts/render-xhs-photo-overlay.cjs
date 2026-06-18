#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

const root = path.resolve(__dirname, "..");

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function splitTitle(brief) {
  if (Array.isArray(brief.title_lines) && brief.title_lines.length) return brief.title_lines;
  const raw = String(brief.title || "").trim();
  if (raw.length <= 8) return [raw];
  if (raw.length <= 15) return [raw.slice(0, 7), raw.slice(7)];
  return [raw.slice(0, 7), raw.slice(7, 14), raw.slice(14)];
}

function classFor(value) {
  return String(value || "left-card").toLowerCase().replace(/[^a-z0-9-]/g, "-");
}

function resolveImagePath(briefFile, imagePath) {
  const absolute = path.isAbsolute(imagePath)
    ? imagePath
    : path.resolve(path.dirname(briefFile), imagePath);
  if (!fs.existsSync(absolute)) {
    throw new Error(`background_image not found: ${absolute}`);
  }
  return absolute;
}

function imageDataUrl(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".png" ? "image/png" : ext === ".webp" ? "image/webp" : "image/jpeg";
  return `data:${mime};base64,${fs.readFileSync(filePath).toString("base64")}`;
}

function renderStamp(value) {
  const raw = String(value || "可复用\n封面链路");
  return raw
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/\\A/g, "\n")
    .split(/\r?\n/)
    .map((line) => escapeHtml(line))
    .join("<br>");
}

function renderHtml(brief, briefFile) {
  const canvas = brief.canvas || { width: 1080, height: 1440 };
  const layout = classFor(brief.layout_family);
  const palette = brief.palette || {};
  const titleLines = splitTitle(brief);
  const tags = Array.isArray(brief.tags) ? brief.tags : [];
  const bullets = Array.isArray(brief.bullets) ? brief.bullets : [];
  const bgPath = resolveImagePath(briefFile, brief.background_image);
  const bgUrl = imageDataUrl(bgPath);
  const bgPosition = brief.background_position || "center";
  const textAlign = brief.text_align || "left";
  const accent = palette.accent || "#ff3f67";
  const accent2 = palette.accent2 || "#ffe45f";
  const ink = palette.ink || "#17110f";
  const paper = palette.paper || "#fff8df";
  const textColor = palette.text || "#17110f";
  const cardBg = palette.card || "rgba(255, 248, 223, .92)";

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=${canvas.width}, initial-scale=1" />
  <title>${escapeHtml(brief.title)}</title>
  <style>
    :root {
      --w: ${canvas.width}px;
      --h: ${canvas.height}px;
      --ink: ${ink};
      --paper: ${paper};
      --accent: ${accent};
      --accent2: ${accent2};
      --text: ${textColor};
      --card: ${cardBg};
      font-family: "HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;
    }
    * { box-sizing: border-box; }
    html, body { width: var(--w); height: var(--h); margin: 0; overflow: hidden; background: #ddd; }
    .poster {
      position: relative;
      width: var(--w);
      height: var(--h);
      overflow: hidden;
      color: var(--text);
      background: #111;
    }
    .bg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: ${bgPosition};
      transform: scale(1.01);
    }
    .grade {
      position: absolute;
      inset: 0;
      background:
        linear-gradient(180deg, rgba(0,0,0,.02), rgba(0,0,0,.22)),
        radial-gradient(72% 54% at 24% 26%, rgba(255,248,223,.78), rgba(255,248,223,.10) 48%, transparent 68%);
    }
    .topbar {
      position: absolute;
      left: 64px;
      right: 64px;
      top: 52px;
      z-index: 5;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      font-size: 28px;
      font-weight: 950;
      color: #fff;
      text-shadow: 0 3px 14px rgba(0,0,0,.36);
    }
    .mark {
      padding: 9px 18px;
      border-radius: 999px;
      background: rgba(0,0,0,.38);
      border: 2px solid rgba(255,255,255,.44);
      backdrop-filter: blur(10px);
    }
    .tags { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
    .tag {
      padding: 9px 16px;
      border-radius: 999px;
      background: rgba(255,255,255,.78);
      color: var(--ink);
      border: 3px solid rgba(23,17,15,.14);
      text-shadow: none;
      box-shadow: 0 6px 0 rgba(0,0,0,.10);
    }
    .copy {
      position: absolute;
      z-index: 6;
      width: 760px;
      text-align: ${textAlign};
    }
    h1 {
      margin: 0;
      font-size: 92px;
      line-height: .98;
      letter-spacing: 0;
      font-weight: 950;
      color: var(--text);
    }
    .title-line { display: block; }
    .subtitle {
      display: inline-block;
      margin-top: 24px;
      padding: 15px 22px;
      border-radius: 19px;
      background: var(--accent);
      color: #fff;
      font-size: 34px;
      line-height: 1.14;
      font-weight: 950;
      box-shadow: 0 10px 0 rgba(0,0,0,.20);
    }
    .bullets {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 28px;
    }
    .bullet {
      padding: 12px 17px;
      border-radius: 999px;
      background: rgba(255,255,255,.86);
      color: var(--ink);
      border: 3px solid rgba(23,17,15,.16);
      font-size: 28px;
      font-weight: 900;
      box-shadow: 0 8px 0 rgba(0,0,0,.12);
    }
    .stamp {
      position: absolute;
      z-index: 7;
      right: 66px;
      bottom: 86px;
      width: 230px;
      height: 230px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      text-align: center;
      padding: 26px;
      background: var(--accent2);
      border: 7px solid #fff;
      color: var(--ink);
      font-size: 34px;
      line-height: 1.04;
      font-weight: 950;
      transform: rotate(8deg);
      box-shadow: 0 18px 0 rgba(0,0,0,.22);
    }
    .sticker {
      position: absolute;
      z-index: 7;
      color: var(--accent2);
      font-size: 68px;
      font-weight: 950;
      text-shadow: 0 6px 0 rgba(0,0,0,.16);
    }
    .s1 { left: 60px; bottom: 266px; transform: rotate(-14deg); }
    .s2 { right: 88px; top: 420px; transform: rotate(16deg); }
    .left-card .copy {
      left: 62px;
      top: 196px;
      padding: 34px 38px 38px;
      border-radius: 34px;
      background: var(--card);
      border: 5px solid rgba(255,255,255,.72);
      box-shadow: 18px 20px 0 rgba(0,0,0,.18);
      backdrop-filter: blur(8px);
    }
    .left-card h1 {
      text-shadow: 4px 0 0 #fff, -4px 0 0 #fff, 0 4px 0 #fff, 0 -4px 0 #fff;
    }
    .bottom-band .grade {
      background:
        linear-gradient(180deg, rgba(0,0,0,.02), rgba(0,0,0,.10) 46%, rgba(0,0,0,.62)),
        radial-gradient(80% 40% at 50% 90%, rgba(255,248,223,.22), transparent 64%);
    }
    .bottom-band .copy {
      left: 64px;
      right: 64px;
      bottom: 110px;
      width: auto;
      padding: 34px 38px;
      border-radius: 32px;
      background: rgba(14,11,10,.62);
      border: 3px solid rgba(255,255,255,.24);
      backdrop-filter: blur(12px);
    }
    .bottom-band h1 { color: #fff; text-shadow: 0 8px 22px rgba(0,0,0,.42); }
    .bottom-band .bullet { background: rgba(255,255,255,.16); color: #fff; border-color: rgba(255,255,255,.32); }
    .right-note .grade {
      background:
        linear-gradient(180deg, rgba(0,0,0,.01), rgba(0,0,0,.20)),
        radial-gradient(68% 52% at 77% 23%, rgba(255,248,223,.86), rgba(255,248,223,.12) 54%, transparent 72%);
    }
    .right-note .copy {
      right: 62px;
      top: 176px;
      width: 625px;
      padding: 32px 36px 38px;
      border-radius: 34px;
      background: var(--card);
      border: 5px solid rgba(255,255,255,.72);
      box-shadow: -16px 18px 0 rgba(0,0,0,.16);
      backdrop-filter: blur(8px);
    }
    .right-note h1 { font-size: 84px; text-shadow: 4px 0 0 #fff, -4px 0 0 #fff, 0 4px 0 #fff, 0 -4px 0 #fff; }
    .big-punch .grade {
      background:
        linear-gradient(180deg, rgba(0,0,0,.01), rgba(0,0,0,.30)),
        radial-gradient(72% 48% at 36% 28%, rgba(255,228,95,.46), rgba(255,228,95,.08) 48%, transparent 72%);
    }
    .big-punch .copy {
      left: 56px;
      top: 166px;
      width: 830px;
    }
    .big-punch h1 {
      color: var(--accent);
      font-size: 100px;
      text-shadow: 6px 0 0 #fff, -6px 0 0 #fff, 0 6px 0 #fff, 0 -6px 0 #fff, 12px 14px 0 rgba(0,0,0,.20);
    }
    .big-punch .title-line:nth-child(2) {
      display: inline-block;
      margin-top: 12px;
      padding: 4px 22px 10px;
      border-radius: 24px;
      background: var(--ink);
      color: #fff;
      text-shadow: none;
      box-shadow: 12px 12px 0 var(--accent2);
    }
  </style>
</head>
<body>
  <main class="poster ${layout}">
    <img class="bg" src="${bgUrl}" alt="" />
    <div class="grade"></div>
    <div class="topbar">
      <div class="mark">${escapeHtml(brief.series || "nook cover")}</div>
      <div class="tags">${tags.slice(0, 2).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div>
    </div>
    <div class="sticker s1">✦</div>
    <div class="sticker s2">✦</div>
    <section class="copy">
      <h1>${titleLines.map((line) => `<span class="title-line">${escapeHtml(line)}</span>`).join("")}</h1>
      <div class="subtitle">${escapeHtml(brief.subtitle || "")}</div>
      <div class="bullets">${bullets.slice(0, 3).map((x) => `<span class="bullet">${escapeHtml(x)}</span>`).join("")}</div>
    </section>
    <div class="stamp">${renderStamp(brief.stamp)}</div>
  </main>
</body>
</html>`;
}

async function launchChromium() {
  const { chromium } = require("playwright");
  const fallbackChromium = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE;
  try {
    return await chromium.launch({ headless: true });
  } catch (error) {
    if (!fallbackChromium || !fs.existsSync(fallbackChromium)) throw error;
    return await chromium.launch({ headless: true, executablePath: fallbackChromium });
  }
}

async function main() {
  const briefFile = process.argv[2];
  if (!briefFile) {
    console.error("Usage: node scripts/render-xhs-photo-overlay.cjs <brief.json> --stdout-base64");
    process.exit(1);
  }
  const resolvedBrief = path.resolve(process.cwd(), briefFile);
  const brief = readJson(resolvedBrief);
  const canvas = brief.canvas || { width: 1080, height: 1440 };
  const html = renderHtml(brief, resolvedBrief);
  const browser = await launchChromium();
  const page = await browser.newPage({ viewport: { width: canvas.width, height: canvas.height }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  const png = await page.locator(".poster").screenshot({ type: "png" });
  await browser.close();
  process.stdout.write(JSON.stringify({
    html_base64: Buffer.from(html, "utf8").toString("base64"),
    png_base64: png.toString("base64")
  }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
