#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

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
  return String(value || "big-type").toLowerCase().replace(/[^a-z0-9-]/g, "-");
}

function renderHtml(brief) {
  const canvas = brief.canvas || { width: 1080, height: 1440 };
  const route = classFor(brief.layout_family);
  const titleLines = splitTitle(brief);
  const tags = Array.isArray(brief.tags) ? brief.tags : [];
  const bullets = Array.isArray(brief.bullets) ? brief.bullets : [];
  const palette = brief.palette || {};
  const cssVars = [
    ["--bg1", palette.bg1 || "#ff7a68"],
    ["--bg2", palette.bg2 || "#ffd35b"],
    ["--ink", palette.ink || "#16110f"],
    ["--paper", palette.paper || "#fff7df"],
    ["--accent", palette.accent || "#ff4f66"],
    ["--accent2", palette.accent2 || "#58d3b5"]
  ].map(([k, v]) => `${k}: ${v};`).join("\n        ");

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
      ${cssVars}
      font-family: "HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;
    }
    * { box-sizing: border-box; }
    html, body { width: var(--w); height: var(--h); margin: 0; overflow: hidden; background: #ddd; }
    .poster {
      position: relative;
      width: var(--w);
      height: var(--h);
      overflow: hidden;
      color: var(--ink);
      background:
        radial-gradient(circle at 14% 12%, rgba(255,255,255,.72), transparent 22%),
        radial-gradient(circle at 86% 84%, rgba(255,255,255,.36), transparent 26%),
        linear-gradient(150deg, var(--bg1), var(--bg2));
    }
    .poster::before {
      content: "";
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(255,255,255,.18) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.18) 1px, transparent 1px);
      background-size: 58px 58px;
      opacity: .58;
    }
    .wrap { position: absolute; inset: 70px; z-index: 2; }
    .topbar { display: flex; justify-content: space-between; align-items: center; font-size: 28px; font-weight: 950; }
    .tags { display: flex; gap: 12px; }
    .tag { padding: 10px 18px; border-radius: 999px; background: rgba(255,255,255,.72); border: 3px solid rgba(22,17,15,.14); box-shadow: 0 8px 0 rgba(22,17,15,.08); }
    h1 { margin: 0; font-size: 92px; line-height: .98; letter-spacing: 0; font-weight: 950; }
    .title-line { display: block; }
    .sticker { position: absolute; z-index: 4; font-weight: 950; }
    .spark { color: #fff7b7; text-shadow: 0 5px 0 rgba(22,17,15,.12); font-size: 58px; }
    .s1 { left: 54px; top: 156px; transform: rotate(-14deg); }
    .s2 { right: 82px; top: 490px; transform: rotate(17deg); }
    .s3 { left: 78px; bottom: 250px; transform: rotate(10deg); }
    .footer-strip { position: absolute; left: 70px; right: 70px; bottom: 58px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; z-index: 5; }
    .footer-strip div { min-height: 104px; display: grid; place-items: center; border-radius: 28px; border: 5px solid #fff; background: var(--ink); color: #fff; font-size: 32px; font-weight: 950; box-shadow: 0 12px 0 rgba(22,17,15,.18); }

    .person-emotion .photo {
      position: absolute; right: 34px; bottom: 128px; width: 500px; height: 690px;
      border-radius: 250px 250px 46px 46px; background:
        radial-gradient(circle at 48% 22%, #ffe3d3 0 15%, transparent 16%),
        radial-gradient(circle at 50% 30%, #2d201d 0 7%, transparent 8%),
        linear-gradient(180deg, #ffd8c3 0 28%, #fff2e6 29% 100%);
      border: 8px solid #fff; box-shadow: 24px 28px 0 rgba(22,17,15,.25);
    }
    .person-emotion .photo::before { content: "AI"; position: absolute; left: 150px; top: 155px; font-size: 84px; font-weight: 950; color: #fff; text-shadow: 4px 4px 0 var(--accent); }
    .person-emotion h1 { position: relative; margin-top: 145px; max-width: 640px; color: var(--accent); text-shadow: 5px 0 0 #fff, -5px 0 0 #fff, 0 5px 0 #fff, 0 -5px 0 #fff, 12px 14px 0 rgba(22,17,15,.18); }
    .person-emotion .subtitle { display: inline-block; margin-top: 32px; padding: 18px 24px; border-radius: 20px; background: var(--paper); border: 5px solid var(--ink); box-shadow: 9px 9px 0 var(--ink); font-size: 38px; font-weight: 950; }
    .person-emotion .notes { position: absolute; left: 22px; bottom: 290px; display: grid; gap: 18px; width: 430px; }
    .person-emotion .note { padding: 18px 24px; border-radius: 999px; background: rgba(255,255,255,.86); border: 5px solid #fff; box-shadow: 0 13px 0 rgba(22,17,15,.12); font-size: 32px; font-weight: 950; }

    .object-proof h1 { margin-top: 126px; color: var(--ink); text-shadow: 5px 0 0 #fff, -5px 0 0 #fff, 0 5px 0 #fff, 0 -5px 0 #fff; }
    .object-proof .hero-object { position: absolute; right: 44px; top: 484px; width: 470px; height: 560px; border: 7px solid var(--ink); border-radius: 42px; background: #fffaf0; box-shadow: 18px 20px 0 var(--ink); padding: 70px 28px 28px; }
    .object-proof .hero-object::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 58px; background: linear-gradient(90deg, var(--accent), var(--accent2)); border-bottom: 6px solid var(--ink); border-radius: 34px 34px 0 0; }
    .object-proof .screen-title { font-size: 42px; font-weight: 950; margin-bottom: 28px; }
    .object-proof .flow { display: grid; grid-template-columns: repeat(2,1fr); gap: 14px; }
    .object-proof .flow span { display: grid; place-items: center; min-height: 92px; border-radius: 20px; border: 5px solid var(--ink); background: var(--paper); font-size: 30px; font-weight: 950; }
    .object-proof .proof-list { position: absolute; left: 0; bottom: 238px; width: 470px; display: grid; gap: 18px; }
    .object-proof .proof { padding: 20px 26px; border-radius: 26px; background: rgba(255,255,255,.86); border: 5px solid #fff; box-shadow: 0 12px 0 rgba(22,17,15,.12); font-size: 34px; font-weight: 950; }
    .object-proof .subtitle { margin-top: 28px; display: inline-block; padding: 16px 22px; border-radius: 18px; background: var(--accent); color: #fff; font-size: 38px; font-weight: 950; }

    .scrapbook-collage { background: linear-gradient(150deg, #e7f2ce, #fff3cf 58%, #ffc8a8); }
    .scrapbook-collage::after { content: ""; position: absolute; left: -80px; top: 160px; width: 1200px; height: 440px; background: rgba(255,255,255,.82); transform: rotate(-7deg); border-radius: 60px; box-shadow: 0 24px 0 rgba(112,143,73,.28); }
    .scrapbook-collage .wrap { z-index: 5; }
    .scrapbook-collage h1 { margin-top: 126px; max-width: 790px; color: #386231; text-shadow: 4px 0 0 #fff, -4px 0 0 #fff, 0 4px 0 #fff, 0 -4px 0 #fff; transform: rotate(-2deg); }
    .scrapbook-collage .photo-card { position: absolute; right: 36px; bottom: 224px; width: 420px; height: 500px; border: 14px solid #fff8e5; background: linear-gradient(160deg, #78966c, #f6e6b6); box-shadow: 16px 18px 0 rgba(56,98,49,.28); transform: rotate(4deg); }
    .scrapbook-collage .photo-card::before { content: ""; position: absolute; left: 95px; top: -30px; width: 160px; height: 54px; background: rgba(255,227,90,.82); transform: rotate(-5deg); }
    .scrapbook-collage .memo { position: absolute; left: 26px; bottom: 282px; width: 440px; padding: 26px; border-radius: 28px; background: #fff9dc; box-shadow: 12px 14px 0 rgba(56,98,49,.24); font-size: 34px; line-height: 1.28; font-weight: 850; transform: rotate(-3deg); }
    .scrapbook-collage .subtitle { display: inline-block; margin-top: 28px; padding: 14px 24px; border: 4px dashed #386231; background: rgba(56,98,49,.82); color: #fff; font-size: 34px; font-weight: 950; transform: rotate(-1deg); }

    .big-type .slab { position: absolute; left: -80px; top: 178px; width: 1220px; height: 360px; background: rgba(255,247,223,.92); transform: rotate(-5deg); border-radius: 60px; box-shadow: 0 34px 0 rgba(255,227,90,.72); }
    .big-type h1 { position: relative; margin-top: 112px; color: var(--accent); font-size: 84px; text-shadow: 5px 0 0 #fff, -5px 0 0 #fff, 0 5px 0 #fff, 0 -5px 0 #fff, 12px 14px 0 rgba(22,17,15,.18); }
    .big-type .title-line:nth-child(2) { color: var(--ink); }
    .big-type .title-line:nth-child(3) { display: inline-block; margin-top: 12px; padding: 4px 22px 10px; color: #fff; background: var(--ink); border-radius: 24px; box-shadow: 12px 12px 0 var(--paper); text-shadow: none; }
    .big-type .subtitle { display: inline-block; margin-top: 28px; padding: 16px 22px; border-radius: 18px; background: var(--paper); border: 5px solid var(--ink); box-shadow: 8px 8px 0 var(--ink); font-size: 34px; line-height: 1.12; font-weight: 950; }
    .big-type .compare { display: grid; grid-template-columns: .95fr 1.15fr; gap: 24px; margin-top: 46px; }
    .big-type .chip, .big-type .panel { min-height: 285px; padding: 28px; border-radius: 36px; background: rgba(255,255,255,.84); border: 6px solid var(--ink); box-shadow: 14px 16px 0 var(--ink); }
    .big-type .chip h2, .big-type .panel h2 { margin: 0 0 18px; font-size: 40px; }
    .big-type .chip p, .big-type .panel p { margin: 0; font-size: 32px; line-height: 1.22; font-weight: 850; }
  </style>
</head>
<body>
  <main class="poster ${route}">
    <div class="sticker spark s1">✦</div>
    <div class="sticker spark s2">✦</div>
    <div class="sticker spark s3">✦</div>
    ${route === "big-type" ? `<div class="slab"></div>` : ""}
    ${route === "person-emotion" ? `<div class="photo"></div>` : ""}
    <section class="wrap">
      <div class="topbar">
        <div>${escapeHtml(brief.series || "封面实验室")}</div>
        <div class="tags">${tags.slice(0, 2).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div>
      </div>
      <h1>${titleLines.map((line) => `<span class="title-line">${escapeHtml(line)}</span>`).join("")}</h1>
      <div class="subtitle">${escapeHtml(brief.subtitle || "")}</div>
      ${route === "person-emotion" ? `
        <div class="notes">${bullets.slice(0, 3).map((x) => `<div class="note">✓ ${escapeHtml(x)}</div>`).join("")}</div>
      ` : ""}
      ${route === "object-proof" ? `
        <div class="proof-list">${bullets.slice(0, 3).map((x) => `<div class="proof">✓ ${escapeHtml(x)}</div>`).join("")}</div>
        <div class="hero-object">
          <div class="screen-title">${escapeHtml(brief.panel_title || "证据面板")}</div>
          <div class="flow">${(brief.pipeline || ["输入", "分析", "排版", "导出"]).slice(0, 4).map((x) => `<span>${escapeHtml(x)}</span>`).join("")}</div>
        </div>
      ` : ""}
      ${route === "scrapbook-collage" ? `
        <div class="photo-card"></div>
        <div class="memo">${escapeHtml(brief.memo || "像手账一样收藏，但标题必须一眼看懂。")}</div>
      ` : ""}
      ${route === "big-type" ? `
        <div class="compare">
          <div class="chip"><h2>${escapeHtml(brief.before_label || "以前")}</h2><p>${escapeHtml(brief.before_text || "靠感觉瞎调")}</p></div>
          <div class="panel"><h2>${escapeHtml(brief.panel_title || "现在")}</h2><p>${escapeHtml(brief.panel_note || "brief 驱动，HTML 控制，PNG 导出。")}</p></div>
        </div>
      ` : ""}
    </section>
    <div class="footer-strip">${bullets.slice(0, 3).map((x) => `<div>${escapeHtml(x)}</div>`).join("")}</div>
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
    console.error("Usage: node scripts/render-xhs-route-sample.cjs <brief.json> --stdout-base64");
    process.exit(1);
  }
  const brief = readJson(path.resolve(process.cwd(), briefFile));
  const canvas = brief.canvas || { width: 1080, height: 1440 };
  const html = renderHtml(brief);
  const browser = await launchChromium();
  const page = await browser.newPage({ viewport: { width: canvas.width, height: canvas.height }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: "networkidle" });
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
