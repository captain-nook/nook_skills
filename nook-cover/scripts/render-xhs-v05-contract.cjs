#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

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

function cls(value, fallback) {
  return String(value || fallback).toLowerCase().replace(/[^a-z0-9-]/g, "-");
}

function splitTitle(title) {
  const raw = String(title || "").trim();
  if (!raw) return ["封面标题"];
  if (raw.includes("\n")) return raw.split(/\n+/).filter(Boolean);
  if (raw.length <= 7) return [raw];
  if (raw.length <= 14) return [raw.slice(0, 7), raw.slice(7)];
  return [raw.slice(0, 6), raw.slice(6, 12), raw.slice(12, 19)];
}

function lines(brief) {
  return Array.isArray(brief.title_lines) && brief.title_lines.length ? brief.title_lines : splitTitle(brief.title);
}

function arr(value, fallback = []) {
  return Array.isArray(value) ? value : fallback;
}

function assetCssUrl(brief, value) {
  if (!value) return "";
  const raw = String(value);
  const resolved = path.isAbsolute(raw) ? raw : path.resolve(brief.__briefDir || process.cwd(), raw);
  if (!fs.existsSync(resolved)) {
    if (!brief.__missingAssets) brief.__missingAssets = new Set();
    brief.__missingAssets.add(resolved);
    return "";
  }
  const normalized = resolved.replace(/\\/g, "/");
  const fileUrl = normalized.match(/^[A-Za-z]:\//) ? `file:///${normalized}` : `file://${normalized}`;
  return `url("${fileUrl}")`;
}

function titleHtml(titleLines, mode = "hot") {
  return titleLines.map((line, index) => (
    `<span class="title-line line-${index + 1} ${mode}">${escapeHtml(line)}</span>`
  )).join("");
}

function badgeHtml(badges) {
  return arr(badges).slice(0, 3).map((badge, index) => (
    `<div class="badge b${index + 1}">${escapeHtml(badge)}</div>`
  )).join("");
}

function stickerHtml(items) {
  return arr(items).slice(0, 4).map((item, index) => (
    `<div class="mini-sticker s${index + 1}">${escapeHtml(item)}</div>`
  )).join("");
}

function commonDecor() {
  return `
    <i class="burst burst-1">✦</i>
    <i class="burst burst-2">✦</i>
    <i class="burst burst-3">✦</i>
    <i class="arrow arrow-1"></i>
    <i class="arrow arrow-2"></i>
    <i class="tape tape-1"></i>
    <i class="tape tape-2"></i>
  `;
}

function visualPlaceholder(brief, label, kind) {
  const image = assetCssUrl(brief, brief.main_visual_image || brief.main_visual_path);
  return `
    <div class="visual ${kind} ${image ? "has-image" : ""}" data-label="${escapeHtml(label)}" style="${image ? `--visual-image:${image};` : ""}">
      <span class="face-dot"></span>
      <span class="body-dot"></span>
    </div>
  `;
}

function imageStyle(brief) {
  const image = assetCssUrl(brief, brief.main_visual_image || brief.main_visual_path);
  return image ? `--visual-image:${image};` : "";
}

function renderFaceImpact(brief) {
  return `
    <main class="poster face-impact-v05">
      <div class="bg-rip red"></div>
      <div class="bg-rip yellow"></div>
      <div class="paper paper-title rag-1"></div>
      ${visualPlaceholder(brief, brief.main_visual_label || "真人半身主视觉", "person-hero")}
      <section class="title-stack face-title">${titleHtml(lines(brief), "hot")}</section>
      <aside class="badge-stack">${badgeHtml(brief.badges)}</aside>
      <section class="food-strip">${stickerHtml(brief.foreground_stickers)}</section>
      ${commonDecor()}
      <div class="footnote">${escapeHtml(brief.person_note || "真人主视觉由 image2.0 / zimage / 用户素材提供，HTML 负责标题、撕纸、贴纸与构图。")}</div>
    </main>
  `;
}

function renderScrapbook(brief) {
  const titleLines = lines(brief);
  return `
    <main class="poster scrapbook-collage-v05">
      <div class="scrap-bg-a"></div>
      <div class="scrap-bg-b"></div>
      <section class="scrap-title">
        ${titleLines.map((line, index) => `<span class="paper-strip p${index + 1}">${escapeHtml(line)}</span>`).join("")}
      </section>
      <div class="photo-card photo-main ${imageStyle(brief) ? "has-image" : ""}" data-label="${escapeHtml(brief.main_visual_label || "咖啡 / 店铺照片")}" style="${imageStyle(brief)}"></div>
      <div class="photo-card photo-small" data-label="细节"></div>
      <section class="note-grid">${stickerHtml(brief.foreground_stickers)}</section>
      <aside class="badge-stack">${badgeHtml(brief.badges)}</aside>
      <i class="doodle-loop"></i>
      <i class="doodle-line d1"></i>
      <i class="doodle-line d2"></i>
      ${commonDecor()}
      <div class="footnote">${escapeHtml(brief.person_note || "手账拼贴模板：用多层纸片、胶带、照片卡与手绘标注制造种草感。")}</div>
    </main>
  `;
}

function renderProductHero(brief) {
  return `
    <main class="poster product-hero-v05">
      <div class="neon-grid"></div>
      <section class="title-stack product-title">${titleHtml(lines(brief), "neon")}</section>
      <div class="screen-frame ${imageStyle(brief) ? "has-image" : ""}" data-label="${escapeHtml(brief.main_visual_label || "产品 / 截图主视觉")}" style="${imageStyle(brief)}">
        <div class="screen-toolbar"><span></span><span></span><span></span></div>
        <div class="screen-glow"></div>
      </div>
      <section class="feature-row">${stickerHtml(brief.foreground_stickers)}</section>
      <aside class="badge-stack">${badgeHtml(brief.badges)}</aside>
      ${commonDecor()}
      <div class="footnote">${escapeHtml(brief.person_note || "产品截图主视觉由图片通道提供；HTML 负责透视框、标题压边与箭头标注。")}</div>
    </main>
  `;
}

function renderPerspectiveCompare(brief) {
  return `
    <main class="poster perspective-compare-v05">
      <div class="split left"></div>
      <div class="split right"></div>
      ${visualPlaceholder(brief, brief.main_visual_label || "中景人物 / 场景", "person-ghost")}
      <section class="title-stack compare-title">${titleHtml(lines(brief), "contrast")}</section>
      <section class="compare-board">
        ${arr(brief.foreground_stickers, ["以前：凭感觉乱调", "现在：有结构出图"]).slice(0, 2).map((item, index) => (
          `<div class="compare-item c${index + 1}">${escapeHtml(item)}</div>`
        )).join("")}
      </section>
      <aside class="badge-stack">${badgeHtml(brief.badges)}</aside>
      ${commonDecor()}
      <div class="footnote">${escapeHtml(brief.person_note || "对比模板：前景卡片近大远小，标题斜压进画面，人物或场景只做第二视觉。")}</div>
    </main>
  `;
}

function css(width, height) {
  return `
    :root {
      --w: ${width}px;
      --h: ${height}px;
      --ink: #111111;
      --red: #ef1b1b;
      --orange: #ff7a00;
      --yellow: #ffda36;
      --cream: #fff4d6;
      --green: #2f6b35;
      --mint: #24f0ce;
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
      isolation: isolate;
    }
    .poster::after {
      content: "";
      position: absolute;
      inset: 0;
      z-index: 2;
      opacity: .24;
      background-image:
        linear-gradient(rgba(255,255,255,.42) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.42) 1px, transparent 1px);
      background-size: 42px 42px;
      pointer-events: none;
    }
    .title-stack {
      position: absolute;
      z-index: 40;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
      transform-origin: 12% 60%;
    }
    .title-line {
      display: block;
      width: max-content;
      max-width: 940px;
      font-weight: 950;
      letter-spacing: 0;
      line-height: .86;
      white-space: nowrap;
    }
    .hot {
      color: var(--red);
      text-shadow:
        8px 0 #fff, -8px 0 #fff, 0 8px #fff, 0 -8px #fff,
        15px 17px 0 var(--ink);
    }
    .neon {
      color: #fff;
      text-shadow:
        6px 0 #071226, -6px 0 #071226, 0 6px #071226, 0 -6px #071226,
        13px 15px 0 var(--mint);
    }
    .contrast {
      color: #fff;
      text-shadow:
        7px 0 var(--orange), -7px 0 var(--orange), 0 7px var(--orange), 0 -7px var(--orange),
        14px 16px 0 #000;
    }
    .line-2 { margin-left: 44px; }
    .line-3 { margin-left: 16px; }
    .paper,
    .paper-strip,
    .mini-sticker,
    .photo-card,
    .compare-board,
    .screen-frame {
      filter: drop-shadow(13px 15px 0 rgba(0,0,0,.24));
    }
    .rag-1,
    .paper-strip {
      clip-path: polygon(0 9%, 7% 3%, 15% 8%, 24% 2%, 34% 7%, 45% 3%, 56% 8%, 67% 2%, 77% 7%, 88% 3%, 100% 7%, 98% 93%, 89% 97%, 76% 92%, 63% 98%, 48% 93%, 35% 99%, 21% 94%, 9% 99%, 1% 94%);
    }
    .badge-stack {
      position: absolute;
      right: 7%;
      top: 8%;
      z-index: 48;
      display: grid;
      gap: 12px;
    }
    .badge {
      padding: 13px 22px;
      border: 7px solid #fff;
      border-radius: 999px;
      background: var(--yellow);
      box-shadow: 8px 9px 0 #000;
      font-size: 32px;
      font-weight: 950;
      line-height: 1.1;
      transform: rotate(3deg);
    }
    .badge.b2 { transform: rotate(-2deg) translateX(18px); }
    .mini-sticker {
      display: grid;
      place-items: center;
      min-height: 116px;
      padding: 18px 22px;
      border: 8px solid #fff;
      border-radius: 28px;
      background: #fff;
      font-size: 32px;
      line-height: 1.05;
      font-weight: 950;
      text-align: center;
    }
    .burst {
      position: absolute;
      z-index: 50;
      color: var(--yellow);
      font-style: normal;
      font-size: 62px;
      line-height: 1;
      -webkit-text-stroke: 8px #fff;
      text-shadow: 7px 8px 0 #000;
    }
    .burst-1 { left: 6%; top: 40%; transform: rotate(-12deg); }
    .burst-2 { right: 6%; top: 37%; transform: rotate(16deg); }
    .burst-3 { left: 10%; bottom: 11%; transform: rotate(8deg); }
    .arrow {
      position: absolute;
      z-index: 49;
      width: 150px;
      height: 96px;
      border-right: 14px solid #fff;
      border-bottom: 14px solid #fff;
      border-radius: 18px;
      filter: drop-shadow(6px 7px 0 #000);
    }
    .arrow-1 { left: 35%; top: 50%; transform: rotate(-28deg) skew(-8deg); }
    .arrow-2 { right: 18%; bottom: 25%; transform: rotate(34deg) skew(-8deg); }
    .tape {
      position: absolute;
      z-index: 46;
      width: 168px;
      height: 48px;
      border-radius: 7px;
      background: rgba(255, 208, 92, .76);
      mix-blend-mode: multiply;
    }
    .tape-1 { left: 7%; top: 7%; transform: rotate(-10deg); }
    .tape-2 { left: 43%; top: 42%; transform: rotate(12deg); }
    .footnote {
      position: absolute;
      left: 5%;
      right: 5%;
      bottom: 3%;
      z-index: 55;
      padding: 14px 20px;
      border-radius: 20px;
      background: rgba(0,0,0,.78);
      color: #fff;
      font-size: 22px;
      line-height: 1.28;
      font-weight: 850;
    }

    .face-impact-v05 {
      background:
        radial-gradient(circle at 18% 12%, rgba(255,255,255,.76), transparent 17%),
        linear-gradient(135deg, #f31b1b 0 30%, transparent 30%),
        linear-gradient(26deg, transparent 0 53%, #ffdb35 53%),
        linear-gradient(160deg, #ff7a59 0%, #ffc46c 100%);
    }
    .face-impact-v05 .bg-rip {
      position: absolute;
      z-index: 4;
      opacity: .9;
      clip-path: polygon(0 8%, 13% 0, 27% 9%, 41% 1%, 58% 11%, 77% 2%, 100% 8%, 96% 94%, 78% 100%, 61% 92%, 42% 99%, 24% 91%, 9% 100%, 0 92%);
    }
    .face-impact-v05 .bg-rip.red { left: -5%; top: 8%; width: 68%; height: 34%; background: #fff6dc; transform: rotate(-5deg); }
    .face-impact-v05 .bg-rip.yellow { right: -8%; top: 29%; width: 38%; height: 55%; background: #fff0b3; transform: rotate(8deg); }
    .face-impact-v05 .paper-title {
      position: absolute;
      left: 2%;
      top: 6%;
      width: 74%;
      height: 43%;
      z-index: 17;
      background: var(--cream);
      transform: rotate(-4deg);
    }
    .face-title { left: 5%; top: 17%; width: 72%; height: 38%; transform: rotate(-5deg) skew(-4deg); }
    .face-title .line-1 { font-size: 120px; }
    .face-title .line-2 { font-size: 108px; color: #111; }
    .face-title .line-3 { font-size: 136px; }
    .visual {
      position: absolute;
      z-index: 22;
      background: linear-gradient(#fff2df 0 35%, #fff 35% 100%);
      opacity: .96;
    }
    .visual.has-image,
    .photo-card.has-image,
    .screen-frame.has-image {
      background-image: var(--visual-image);
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
    }
    .visual.has-image .face-dot,
    .visual.has-image .body-dot,
    .visual.has-image::before,
    .photo-card.has-image::after,
    .screen-frame.has-image::after {
      display: none;
    }
    .visual::before {
      content: attr(data-label);
      position: absolute;
      left: 50%;
      top: 26%;
      transform: translate(-50%, -50%);
      padding: 8px 14px;
      border-radius: 999px;
      background: rgba(255,255,255,.86);
      color: rgba(0,0,0,.56);
      font-size: 23px;
      font-weight: 950;
      white-space: nowrap;
    }
    .person-hero {
      right: 6%;
      top: 22%;
      width: 39%;
      height: 58%;
      border-radius: 48% 48% 34% 34%;
      filter: drop-shadow(21px 25px 0 rgba(0,0,0,.24));
    }
    .face-dot {
      position: absolute;
      left: 30%;
      top: 8%;
      width: 40%;
      height: 22%;
      border-radius: 50%;
      background: #ffe1cb;
      border: 8px solid rgba(0,0,0,.08);
    }
    .body-dot {
      position: absolute;
      left: 22%;
      right: 22%;
      bottom: 7%;
      height: 55%;
      border-radius: 44% 44% 16% 16%;
      background: #fff;
      border: 8px solid rgba(0,0,0,.08);
    }
    .food-strip {
      position: absolute;
      left: 5%;
      bottom: 18%;
      z-index: 44;
      width: 68%;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      transform: rotate(-3deg);
    }
    .food-strip .s2 { transform: translateY(-25px) rotate(5deg); background: #e9ffdb; color: #145223; }
    .food-strip .s3 { transform: translateY(9px) rotate(-5deg); background: #fff2ca; color: #145223; }

    .scrapbook-collage-v05 {
      background:
        radial-gradient(circle at 85% 12%, rgba(255,255,255,.78), transparent 18%),
        linear-gradient(135deg, #fff5da 0 31%, #dff2bf 31% 63%, #ffb4a0 63% 100%);
    }
    .scrapbook-collage-v05 .scrap-bg-a,
    .scrapbook-collage-v05 .scrap-bg-b {
      position: absolute;
      z-index: 4;
      background: rgba(255,255,255,.36);
      clip-path: polygon(4% 4%, 96% 0, 100% 88%, 8% 100%);
    }
    .scrapbook-collage-v05 .scrap-bg-a { left: 0; top: 5%; width: 58%; height: 46%; transform: rotate(-7deg); }
    .scrapbook-collage-v05 .scrap-bg-b { right: 0; top: 26%; width: 46%; height: 56%; transform: rotate(9deg); }
    .scrap-title {
      position: absolute;
      left: 7%;
      top: 11%;
      z-index: 42;
      display: grid;
      gap: 14px;
      transform: rotate(-3deg);
    }
    .paper-strip {
      display: block;
      width: max-content;
      max-width: 720px;
      padding: 10px 24px;
      background: #fff;
      color: #315b2d;
      font-size: 86px;
      line-height: .98;
      font-weight: 950;
      text-shadow: 5px 6px 0 rgba(49,91,45,.18);
    }
    .paper-strip.p2 { margin-left: 34px; transform: rotate(2deg); }
    .paper-strip.p3 { margin-left: 10px; transform: rotate(-4deg); }
    .photo-card {
      position: absolute;
      z-index: 25;
      display: grid;
      place-items: center;
      background: #fff;
      border: 14px solid #fff;
      color: rgba(0,0,0,.45);
      font-size: 30px;
      font-weight: 950;
    }
    .photo-card::after { content: attr(data-label); }
    .photo-main {
      right: 9%;
      top: 29%;
      width: 42%;
      height: 36%;
      transform: rotate(-5deg);
    }
    .photo-small {
      left: 10%;
      top: 55%;
      width: 34%;
      height: 22%;
      transform: rotate(7deg);
      opacity: .95;
    }
    .note-grid {
      position: absolute;
      left: 8%;
      bottom: 12%;
      z-index: 43;
      width: 74%;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      transform: rotate(3deg);
    }
    .note-grid .mini-sticker {
      min-height: 98px;
      border-radius: 8px;
      background: #fff8c9;
      color: #315b2d;
      font-size: 30px;
      filter: drop-shadow(10px 12px 0 rgba(49,91,45,.18));
    }
    .doodle-loop {
      position: absolute;
      left: 38%;
      top: 43%;
      z-index: 47;
      width: 260px;
      height: 140px;
      border: 10px dashed #fff;
      border-radius: 50%;
      transform: rotate(-22deg);
      filter: drop-shadow(5px 5px 0 #111);
    }
    .doodle-line {
      position: absolute;
      z-index: 47;
      width: 180px;
      border-top: 11px solid #fff;
      filter: drop-shadow(5px 5px 0 #111);
    }
    .d1 { left: 18%; top: 49%; transform: rotate(-18deg); }
    .d2 { right: 16%; bottom: 28%; transform: rotate(16deg); }

    .product-hero-v05 {
      background:
        radial-gradient(circle at 18% 12%, rgba(36,240,206,.36), transparent 22%),
        linear-gradient(146deg, #071126 0%, #122653 56%, #0ee4c0 100%);
    }
    .neon-grid {
      position: absolute;
      inset: 0;
      z-index: 3;
      opacity: .42;
      background-image:
        linear-gradient(rgba(255,255,255,.16) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.16) 1px, transparent 1px);
      background-size: 36px 36px;
    }
    .product-title {
      left: 7%;
      top: 15%;
      width: 66%;
      transform: rotate(-4deg) skew(-5deg);
    }
    .product-title .line-1 { font-size: 104px; }
    .product-title .line-2 { font-size: 106px; margin-left: 28px; }
    .product-title .line-3 { font-size: 84px; color: #bffdf2; }
    .screen-frame {
      position: absolute;
      left: 14%;
      top: 39%;
      z-index: 24;
      width: 72%;
      height: 34%;
      border: 9px solid #fff;
      border-radius: 34px;
      background: #0a1738;
      transform: perspective(900px) rotateX(5deg) rotateY(-9deg) rotate(-3deg);
    }
    .screen-frame::after {
      content: attr(data-label);
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      padding: 10px 16px;
      border-radius: 999px;
      color: rgba(255,255,255,.72);
      background: rgba(255,255,255,.1);
      font-size: 28px;
      font-weight: 950;
      white-space: nowrap;
    }
    .screen-toolbar {
      position: absolute;
      top: 22px;
      left: 26px;
      display: flex;
      gap: 12px;
    }
    .screen-toolbar span {
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: var(--mint);
    }
    .screen-glow {
      position: absolute;
      right: 6%;
      bottom: 12%;
      width: 38%;
      height: 36%;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(36,240,206,.42), transparent 70%);
    }
    .feature-row {
      position: absolute;
      left: 12%;
      bottom: 13%;
      z-index: 44;
      width: 76%;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      transform: rotate(-2deg);
    }
    .feature-row .mini-sticker {
      min-height: 132px;
      border: 5px solid var(--mint);
      border-radius: 18px;
      background: rgba(255,255,255,.94);
      color: #071126;
      font-size: 32px;
    }

    .perspective-compare-v05 {
      background: #111;
    }
    .split {
      position: absolute;
      inset: 0;
      z-index: 3;
      clip-path: polygon(0 0, 62% 0, 45% 100%, 0 100%);
      background: #111;
    }
    .split.right {
      clip-path: polygon(62% 0, 100% 0, 100% 100%, 45% 100%);
      background: linear-gradient(160deg, #ff7a00, #ffd33d);
    }
    .person-ghost {
      right: 8%;
      top: 25%;
      width: 34%;
      height: 56%;
      border-radius: 48% 48% 34% 34%;
      background: #fff0d3;
      opacity: .78;
      filter: drop-shadow(18px 24px 0 rgba(0,0,0,.24));
    }
    .compare-title {
      left: 5%;
      top: 17%;
      width: 74%;
      transform: rotate(-5deg) skew(-8deg);
    }
    .compare-title .line-1 { font-size: 112px; }
    .compare-title .line-2 { font-size: 112px; margin-left: 32px; }
    .compare-title .line-3 { font-size: 88px; color: #ffe3aa; }
    .compare-board {
      position: absolute;
      left: 7%;
      bottom: 17%;
      z-index: 43;
      width: 78%;
      height: 28%;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      padding: 24px;
      border: 9px solid #fff;
      border-radius: 34px;
      background: #111;
      transform: perspective(900px) rotate(-6deg) skew(-7deg);
    }
    .compare-item {
      display: grid;
      place-items: center;
      padding: 18px;
      border-radius: 22px;
      background: #fff;
      color: #111;
      font-size: 34px;
      line-height: 1.08;
      font-weight: 950;
      text-align: center;
    }
  `;
}

function renderHtml(brief) {
  const canvas = brief.canvas || { width: 1080, height: 1440 };
  const contract = cls(brief.layout_contract, "face-impact-v05");
  const body = contract.includes("scrapbook")
    ? renderScrapbook(brief)
    : contract.includes("product")
      ? renderProductHero(brief)
      : contract.includes("compare")
        ? renderPerspectiveCompare(brief)
        : renderFaceImpact(brief);

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=${canvas.width}, initial-scale=1" />
  <title>${escapeHtml(brief.title || "小红书封面")}</title>
  <style>${css(canvas.width, canvas.height)}</style>
</head>
<body>${body}</body>
</html>`;
}

async function launchChromium() {
  let chromium;
  try {
    ({ chromium } = require("playwright"));
  } catch (error) {
    if (error && error.code === "MODULE_NOT_FOUND") {
      throw new Error("Missing dependency: playwright. Run `npm install` before PNG rendering. HTML was written successfully.");
    }
    throw error;
  }
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

async function main() {
  const briefFile = process.argv[2];
  if (!briefFile) {
    console.error("Usage: node scripts/render-xhs-v05-contract.cjs <brief.json> [output-dir]");
    process.exit(1);
  }
  const briefPath = path.resolve(process.cwd(), briefFile);
  const brief = readJson(briefPath);
  brief.__briefDir = path.dirname(briefPath);
  const canvas = brief.canvas || { width: 1080, height: 1440 };
  const outDir = path.resolve(process.cwd(), process.argv[3] || "output/xhs-v05-contract");
  fs.mkdirSync(outDir, { recursive: true });
  const htmlFile = path.join(outDir, "index.html");
  const pngFile = path.join(outDir, "cover.png");
  fs.writeFileSync(htmlFile, renderHtml(brief), "utf8");
  if (brief.__missingAssets && brief.__missingAssets.size) {
    for (const missing of brief.__missingAssets) console.warn(`Missing visual asset: ${missing}`);
  }
  console.log(`HTML=${htmlFile}`);
  if (process.argv.includes("--html-only")) return;
  await screenshot(htmlFile, pngFile, canvas.width, canvas.height);
  console.log(`PNG=${pngFile}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
