#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function classFor(value, fallback) {
  return String(value || fallback).toLowerCase().replace(/[^a-z0-9-]/g, "-");
}

function splitTitle(title) {
  const raw = String(title || "").trim();
  if (raw.includes("\n")) return raw.split(/\n+/).filter(Boolean);
  if (raw.length <= 9) return [raw];
  if (raw.length <= 16) return [raw.slice(0, 8), raw.slice(8)];
  return [raw.slice(0, 8), raw.slice(8, 16), raw.slice(16)];
}

function renderHtml(brief) {
  const canvas = brief.canvas || { width: 1080, height: 1440 };
  const visualSystem = classFor(brief.visual_system, "hook-title");
  const layoutFamily = classFor(brief.layout_family, "info-hook-cover");
  const tags = Array.isArray(brief.tags) ? brief.tags : [];
  const bullets = Array.isArray(brief.bullets) ? brief.bullets : [];
  const titleLines = Array.isArray(brief.title_lines) && brief.title_lines.length
    ? brief.title_lines
    : splitTitle(brief.title);
  const outputNote = brief.footer || "nook-cover / xhs v0.1";
  const bgImage = brief.background_image ? String(brief.background_image).replace(/\\/g, "/") : "";
  const hasBg = bgImage.length > 0;

  if (layoutFamily === "bold-compare-generator") {
    const compare = brief.compare || {};
    const pipeline = Array.isArray(brief.pipeline) && brief.pipeline.length
      ? brief.pipeline
      : ["主题", "brief", "HTML", "PNG"];
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
      --ink: #15120f;
      --cream: #fff7df;
      --hot: #ff4f66;
      --coral: #ff7459;
      --lemon: #ffe35a;
      --mint: #59d3b4;
      font-family: "HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;
    }
    * { box-sizing: border-box; }
    html, body {
      width: var(--w);
      height: var(--h);
      margin: 0;
      overflow: hidden;
      background: #f0f0f0;
    }
    .poster {
      position: relative;
      width: var(--w);
      height: var(--h);
      overflow: hidden;
      color: var(--ink);
      background:
        radial-gradient(circle at 12% 14%, rgba(255, 255, 255, .86), transparent 23%),
        radial-gradient(circle at 88% 10%, rgba(255, 227, 90, .78), transparent 24%),
        radial-gradient(circle at 78% 82%, rgba(89, 211, 180, .42), transparent 26%),
        linear-gradient(155deg, #ff8b73 0%, #ff5d70 46%, #ffc74f 100%);
    }
    .poster::before {
      content: "";
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(255,255,255,.16) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.16) 1px, transparent 1px);
      background-size: 58px 58px;
      opacity: .62;
    }
    .poster::after {
      content: "";
      position: absolute;
      left: -90px;
      top: 180px;
      width: 1230px;
      height: 360px;
      background: rgba(255, 247, 223, .92);
      transform: rotate(-5.5deg);
      border-radius: 60px;
      box-shadow: 0 34px 0 rgba(255, 227, 90, .76);
    }
    .spark, .arrow, .ring, .dash {
      position: absolute;
      z-index: 4;
      pointer-events: none;
    }
    .spark {
      color: #fff5b9;
      font-size: 54px;
      font-weight: 900;
      text-shadow: 0 4px 0 rgba(21,18,15,.12);
    }
    .s1 { left: 72px; top: 116px; transform: rotate(-12deg); }
    .s2 { right: 84px; top: 538px; transform: rotate(18deg); }
    .s3 { left: 92px; bottom: 250px; transform: rotate(12deg); }
    .arrow {
      right: 96px;
      top: 408px;
      width: 94px;
      height: 94px;
      border-right: 10px solid #fff;
      border-top: 10px solid #fff;
      border-radius: 18px;
      transform: rotate(38deg);
    }
    .ring {
      right: 48px;
      bottom: 104px;
      width: 180px;
      height: 180px;
      border: 12px solid rgba(255,255,255,.62);
      border-radius: 999px;
    }
    .dash {
      left: 76px;
      top: 88px;
      display: flex;
      gap: 16px;
      transform: rotate(18deg);
    }
    .dash span {
      width: 16px;
      height: 64px;
      border-radius: 999px;
      background: #fff;
    }
    .wrap {
      position: absolute;
      inset: 74px 70px 66px;
      z-index: 5;
    }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: rgba(21,18,15,.72);
      font-size: 28px;
      font-weight: 900;
    }
    .tags {
      display: flex;
      gap: 14px;
    }
    .tag {
      padding: 12px 18px;
      border-radius: 999px;
      background: rgba(255,255,255,.78);
      border: 3px solid rgba(21,18,15,.12);
      box-shadow: 0 9px 0 rgba(21,18,15,.07);
      white-space: nowrap;
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      margin-top: 62px;
      padding: 16px 28px;
      border-radius: 999px;
      background: var(--lemon);
      border: 4px solid var(--ink);
      box-shadow: 8px 8px 0 var(--ink);
      font-size: 34px;
      font-weight: 950;
      transform: rotate(-2deg);
    }
    h1 {
      position: relative;
      z-index: 2;
      margin: 38px 0 0;
      font-size: 93px;
      line-height: .98;
      font-weight: 950;
      letter-spacing: 0;
      color: var(--hot);
      text-shadow:
        5px 0 0 #fff,
        -5px 0 0 #fff,
        0 5px 0 #fff,
        0 -5px 0 #fff,
        11px 13px 0 rgba(21,18,15,.18);
    }
    .title-line { display: block; }
    .title-line:nth-child(2) {
      color: var(--ink);
      font-size: 86px;
      transform: translateX(8px) rotate(-1deg);
    }
    .title-line:nth-child(3) {
      display: inline-block;
      margin-top: 14px;
      padding: 2px 22px 10px;
      color: #fff;
      background: var(--ink);
      border-radius: 24px;
      box-shadow: 12px 12px 0 var(--lemon);
      transform: rotate(-1.5deg);
      text-shadow: none;
    }
    .subtitle {
      display: inline-block;
      margin-top: 34px;
      padding: 18px 24px;
      background: var(--lemon);
      border-radius: 20px;
      border: 4px solid rgba(21,18,15,.9);
      font-size: 40px;
      line-height: 1.12;
      font-weight: 950;
      box-shadow: 8px 8px 0 rgba(21,18,15,.82);
    }
    .middle {
      display: grid;
      grid-template-columns: 1fr 1.22fr;
      gap: 26px;
      margin-top: 62px;
      align-items: stretch;
    }
    .compare {
      display: grid;
      gap: 18px;
      align-content: center;
    }
    .chip {
      min-height: 150px;
      padding: 22px 24px;
      border-radius: 30px;
      border: 5px solid #fff;
      background: rgba(255,255,255,.72);
      box-shadow: 0 18px 0 rgba(21,18,15,.12);
    }
    .chip.after {
      background: #fff7df;
      border-color: var(--ink);
      transform: rotate(-1.5deg);
    }
    .chip-label {
      display: inline-block;
      margin-bottom: 12px;
      padding: 6px 14px;
      border-radius: 999px;
      background: var(--ink);
      color: #fff;
      font-size: 24px;
      font-weight: 950;
    }
    .chip.after .chip-label { background: var(--hot); }
    .chip-text {
      font-size: 37px;
      line-height: 1.08;
      font-weight: 950;
    }
    .panel {
      position: relative;
      min-height: 396px;
      padding: 28px 28px 24px;
      border-radius: 36px;
      border: 6px solid var(--ink);
      background: rgba(255,255,255,.88);
      box-shadow: 16px 18px 0 rgba(21,18,15,.85);
      overflow: hidden;
    }
    .panel::before {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      top: 0;
      height: 54px;
      background: linear-gradient(90deg, var(--hot), var(--lemon));
      border-bottom: 5px solid var(--ink);
    }
    .dots {
      position: absolute;
      top: 17px;
      left: 24px;
      display: flex;
      gap: 10px;
    }
    .dots span {
      width: 18px;
      height: 18px;
      border-radius: 999px;
      background: var(--ink);
    }
    .panel-title {
      margin-top: 58px;
      font-size: 41px;
      font-weight: 950;
    }
    .flow {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      margin-top: 26px;
    }
    .flow-item {
      min-height: 86px;
      display: grid;
      place-items: center;
      padding: 10px 8px;
      border-radius: 18px;
      background: var(--cream);
      border: 4px solid var(--ink);
      font-size: 25px;
      line-height: 1;
      font-weight: 950;
      text-align: center;
    }
    .panel-note {
      margin-top: 28px;
      padding: 18px 20px;
      border-radius: 20px;
      background: rgba(255, 227, 90, .55);
      font-size: 27px;
      line-height: 1.22;
      font-weight: 850;
    }
    .bullets {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-top: 34px;
    }
    .bullet {
      min-height: 112px;
      display: grid;
      place-items: center;
      border-radius: 28px;
      background: var(--ink);
      color: #fff;
      border: 5px solid #fff;
      box-shadow: 0 12px 0 rgba(21,18,15,.18);
      font-size: 34px;
      font-weight: 950;
    }
    .footer {
      display: none;
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      justify-content: space-between;
      color: rgba(21,18,15,.58);
      font-size: 22px;
      font-weight: 850;
    }
  </style>
</head>
<body>
  <main class="poster ${visualSystem} ${layoutFamily}" data-platform="xhs">
    <div class="dash"><span></span><span></span><span></span></div>
    <div class="spark s1">✦</div>
    <div class="spark s2">✦</div>
    <div class="spark s3">✦</div>
    <div class="arrow"></div>
    <div class="ring"></div>
    <section class="wrap">
      <div class="topbar">
        <div>${escapeHtml(brief.series || "封面实验室")}</div>
        <div class="tags">${tags.slice(0, 2).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div>
      </div>
      <div class="eyebrow">${escapeHtml(brief.eyebrow || "教程实测")}</div>
      <h1>${titleLines.map((line) => `<span class="title-line">${escapeHtml(line)}</span>`).join("")}</h1>
      <div class="subtitle">${escapeHtml(brief.subtitle)}</div>
      <div class="middle">
        <div class="compare">
          <div class="chip">
            <span class="chip-label">${escapeHtml(compare.before_label || "以前")}</span>
            <div class="chip-text">${escapeHtml(compare.before_text || "靠感觉瞎调")}</div>
          </div>
          <div class="chip after">
            <span class="chip-label">${escapeHtml(compare.after_label || "现在")}</span>
            <div class="chip-text">${escapeHtml(compare.after_text || "brief 驱动出图")}</div>
          </div>
        </div>
        <div class="panel">
          <div class="dots"><span></span><span></span><span></span></div>
          <div class="panel-title">${escapeHtml(brief.panel_title || "封面生成器")}</div>
          <div class="flow">${pipeline.slice(0, 4).map((item) => `<div class="flow-item">${escapeHtml(item)}</div>`).join("")}</div>
          <div class="panel-note">${escapeHtml(brief.panel_note || "标题 / 色彩 / 版式 / 导出全部可控")}</div>
        </div>
      </div>
      <div class="bullets">
        ${bullets.slice(0, 3).map((item) => `<div class="bullet">${escapeHtml(item)}</div>`).join("")}
      </div>
      <div class="footer">
        <span>${escapeHtml(outputNote)}</span>
        <span>${escapeHtml(brief.platform_label || (brief.platform === "xiaohongshu" ? "小红书" : brief.platform || "小红书"))} · ${escapeHtml((brief.canvas && brief.canvas.ratio) || "3:4")}</span>
      </div>
    </section>
  </main>
</body>
</html>`;
  }

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
      --ink: #121212;
      --muted: rgba(18, 18, 18, 0.68);
      --paper: #fbf7ef;
      --accent: #ff4d2e;
      --accent-2: #0f8f7f;
      --line: rgba(18, 18, 18, 0.14);
      --radius: 30px;
      font-family: "HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;
    }

    * { box-sizing: border-box; }
    html, body {
      width: var(--w);
      height: var(--h);
      margin: 0;
      overflow: hidden;
      background: #ddd;
    }

    .poster {
      position: relative;
      width: var(--w);
      height: var(--h);
      overflow: hidden;
      color: var(--ink);
      background:
        radial-gradient(circle at 16% 86%, rgba(255, 188, 166, 0.54), transparent 28%),
        radial-gradient(circle at 84% 12%, rgba(255, 132, 120, 0.36), transparent 30%),
        linear-gradient(160deg, #8f2424 0%, #b93b35 38%, #ff8f73 100%);
    }

    .poster::before {
      content: "";
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.12) 1px, transparent 1px);
      background-size: 54px 54px;
      pointer-events: none;
    }

    .ai-bg {
      position: absolute;
      inset: 0;
      background-size: cover;
      background-position: center;
      z-index: 0;
    }

    .ai-overlay {
      position: absolute;
      inset: 0;
      background:
        linear-gradient(180deg, rgba(0, 0, 0, 0.35) 0%, rgba(0, 0, 0, 0.55) 100%);
      z-index: 1;
    }

    .poster.has-bg {
      background: #1a1a1a;
    }

    .poster.has-bg h1 { color: #ffffff; text-shadow: 0 4px 24px rgba(0,0,0,0.4); }
    .poster.has-bg .eyebrow { background: #ffffff; color: #f11136; }
    .poster.has-bg .eyebrow::before { background: #f11136; box-shadow: 0 0 0 7px rgba(241, 17, 54, 0.18); }
    .poster.has-bg .subtitle { color: #ffffff; background: linear-gradient(180deg, #f11136, #ff6a5b); }
    .poster.has-bg .badge { background: rgba(255,255,255,0.92); color: rgba(18,18,18,0.78); }
    .poster.has-bg .grid { background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,255,255,0.9)); }
    .poster.has-bg .bullet { background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,255,255,0.88)); color: #f11136; }
    .poster.has-bg .topbar { color: rgba(255,255,255,0.78); }

    .grid {
      position: absolute;
      inset: 74px 88px;
      border-radius: 62px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.94)),
        linear-gradient(rgba(255, 77, 46, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 77, 46, 0.05) 1px, transparent 1px);
      background-size: auto, 42px 42px, 42px 42px;
      box-shadow: 0 40px 110px rgba(62, 17, 12, 0.28);
    }

    .content {
      position: absolute;
      inset: 118px 126px 112px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      z-index: 2;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      font-size: 30px;
      font-weight: 700;
      color: rgba(18, 18, 18, 0.58);
    }

    .badge-row {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .badge {
      padding: 12px 20px;
      border: 1.5px solid rgba(18, 18, 18, 0.16);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.72);
      white-space: nowrap;
    }

    .hero {
      margin-top: 112px;
      text-align: center;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 12px;
      padding: 14px 22px;
      margin-bottom: 42px;
      border-radius: 999px;
      color: white;
      background: #f11136;
      font-size: 32px;
      font-weight: 800;
      letter-spacing: 0;
    }

    .eyebrow::before {
      content: "";
      width: 13px;
      height: 13px;
      border-radius: 999px;
      background: var(--accent);
      box-shadow: 0 0 0 7px rgba(241, 17, 54, 0.16);
    }

    h1 {
      margin: 0;
      font-size: 108px;
      line-height: 1.02;
      font-weight: 950;
      letter-spacing: 0;
      color: #f11136;
      text-wrap: balance;
    }

    .title-line {
      display: block;
    }

    .subtitle {
      max-width: 760px;
      margin: 42px auto 0;
      padding: 22px 26px;
      border-radius: 28px;
      font-size: 46px;
      line-height: 1.18;
      font-weight: 850;
      color: white;
      background: linear-gradient(180deg, #f11136, #ff6a5b);
    }

    .bottom {
      display: block;
    }

    .bullet-card {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 22px;
      padding: 0;
      border: 0;
      background: transparent;
      box-shadow: none;
    }

    .bullet {
      min-height: 158px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 14px;
      padding: 22px 16px;
      border-radius: 28px;
      background: linear-gradient(180deg, #fff8f4, #ffe2db);
      box-shadow: 0 16px 45px rgba(96, 20, 16, 0.11);
      font-size: 29px;
      line-height: 1.1;
      font-weight: 900;
      color: #f11136;
      text-align: center;
    }

    .num {
      width: 58px;
      height: 58px;
      display: grid;
      place-items: center;
      border-radius: 19px;
      color: #f11136;
      background: rgba(255, 255, 255, 0.9);
      font-family: Inter, Arial, sans-serif;
      font-size: 28px;
    }

    .visual {
      display: none;
    }

    .visual::after {
      content: "";
      position: absolute;
      width: 220px;
      height: 220px;
      right: -58px;
      bottom: -42px;
      border-radius: 999px;
      border: 34px solid rgba(255, 255, 255, 0.14);
    }

    .visual-title {
      font-size: 31px;
      font-weight: 850;
      line-height: 1.16;
      position: relative;
      z-index: 1;
    }

    .footer {
      position: absolute;
      left: 126px;
      right: 126px;
      bottom: 88px;
      display: flex;
      justify-content: space-between;
      color: rgba(18, 18, 18, 0.38);
      font-size: 23px;
      font-weight: 700;
      z-index: 3;
    }

    .poster.life-aesthetic {
      --accent: #d96f45;
      --accent-2: #577c6b;
      background:
        radial-gradient(circle at 20% 18%, rgba(255,255,255,.9), transparent 28%),
        linear-gradient(150deg, #fff9ef 0%, #f7ded1 52%, #dbeee2 100%);
    }

    .poster.proof-signal {
      --ink: #eff8ff;
      --muted: rgba(239, 248, 255, 0.72);
      --accent: #48d3ff;
      --accent-2: #52e6a5;
      color: var(--ink);
      background:
        radial-gradient(circle at 16% 20%, rgba(72,211,255,.34), transparent 28%),
        linear-gradient(145deg, #0b1220 0%, #14243c 54%, #10261f 100%);
    }

    .poster.proof-signal .badge,
    .poster.proof-signal .bullet-card {
      background: rgba(255,255,255,.09);
      border-color: rgba(255,255,255,.18);
      color: var(--ink);
    }

    .poster.proof-signal h1 { color: var(--ink); }
    .poster.proof-signal .subtitle { color: rgba(239,248,255,.78); }
    .poster.proof-signal .footer { color: rgba(239,248,255,.48); }
    .poster.proof-signal .grid { background-size: 42px 42px; opacity: .78; }

    .poster.hook-title {
      --accent: #ff4d2e;
      --accent-2: #111111;
    }
  </style>
</head>
<body>
  <main class="poster ${visualSystem} ${layoutFamily} ${hasBg ? "has-bg" : ""}" data-platform="xhs">
    ${hasBg ? `<div class="ai-bg" style="background-image: url('file:///${bgImage}');"></div><div class="ai-overlay"></div>` : ""}
      <div class="grid"></div>
    <section class="content">
      <div>
        <div class="topbar">
          <div>${escapeHtml(brief.series || "封面实验室")}</div>
          <div class="badge-row">
            ${tags.slice(0, 2).map((tag) => `<span class="badge">${escapeHtml(tag)}</span>`).join("")}
          </div>
        </div>
        <div class="hero">
          <div class="eyebrow">${escapeHtml(brief.eyebrow || "教程实测")}</div>
          <h1>${titleLines.map((line) => `<span class="title-line">${escapeHtml(line)}</span>`).join("")}</h1>
          <div class="subtitle">${escapeHtml(brief.subtitle)}</div>
        </div>
      </div>
      <div class="bottom">
        <div class="bullet-card">
          ${bullets.slice(0, 3).map((item, index) => `
            <div class="bullet">
              <span class="num">${String(index + 1).padStart(2, "0")}</span>
              <span>${escapeHtml(item)}</span>
            </div>
          `).join("")}
        </div>
      </div>
    </section>
    <div class="footer">
      <span>${escapeHtml(outputNote)}</span>
      <span>${escapeHtml(brief.platform_label || (brief.platform === "xiaohongshu" ? "小红书" : brief.platform || "小红书"))} · ${escapeHtml((brief.canvas && brief.canvas.ratio) || "3:4")}</span>
    </div>
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

async function screenshot(htmlFile, outputFile, width, height) {
  const browser = await launchChromium();
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.goto(`file://${htmlFile.replace(/\\/g, "/")}`, { waitUntil: "networkidle" });
  await page.locator(".poster").screenshot({ path: outputFile });
  await browser.close();
}

async function screenshotHtml(html, width, height) {
  const browser = await launchChromium();
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: "networkidle" });
  const buffer = await page.locator(".poster").screenshot({ type: "png" });
  await browser.close();
  return buffer;
}

async function main() {
  const briefFile = process.argv[2];
  if (!briefFile) {
    console.error("Usage: node scripts/render-xhs-cover.cjs <brief.json> [output-dir] [--stdout-base64]");
    process.exit(1);
  }
  const briefPath = path.resolve(process.cwd(), briefFile);
  const brief = readJson(briefPath);
  const canvas = brief.canvas || { width: 1080, height: 1440 };
  const html = renderHtml(brief);
  if (process.argv.includes("--stdout-base64")) {
    const png = await screenshotHtml(html, canvas.width, canvas.height);
    process.stdout.write(JSON.stringify({
      html_base64: Buffer.from(html, "utf8").toString("base64"),
      png_base64: png.toString("base64")
    }));
    return;
  }
  const outDir = path.resolve(process.cwd(), process.argv[3] || "output/xhs-v01");
  fs.mkdirSync(outDir, { recursive: true });
  const htmlFile = path.join(outDir, "index.html");
  const pngFile = path.join(outDir, "cover.png");
  fs.writeFileSync(htmlFile, html, "utf8");
  await screenshot(htmlFile, pngFile, canvas.width, canvas.height);
  console.log(`HTML=${htmlFile}`);
  console.log(`PNG=${pngFile}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
