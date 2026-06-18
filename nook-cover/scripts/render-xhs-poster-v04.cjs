#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function imgData(file) {
  const ext = path.extname(file).toLowerCase();
  const mime = ext === ".png" ? "image/png" : ext === ".webp" ? "image/webp" : "image/jpeg";
  return `data:${mime};base64,${fs.readFileSync(file).toString("base64")}`;
}

function resolveImage(baseFile, imagePath) {
  const absolute = path.isAbsolute(imagePath) ? imagePath : path.resolve(path.dirname(baseFile), imagePath);
  if (!fs.existsSync(absolute)) throw new Error(`image not found: ${absolute}`);
  return absolute;
}

function slugFileName(value) {
  return String(value || "cover")
    .replace(/[\\/:*?"<>|]/g, "")
    .replace(/\s+/g, "")
    .slice(0, 60) || "cover";
}

function renderLines(lines, cls = "title-line") {
  return (lines || []).map((line, i) => `<span class="${cls} l${i + 1}">${esc(line)}</span>`).join("");
}

function renderBadges(items) {
  return (items || []).map((item, i) => `<span class="badge b${i + 1}">${esc(item)}</span>`).join("");
}

function renderSafeZones(item) {
  const zones = item.safe_zones || {};
  const face = zones.face;
  if (!face) return "";
  const style = [
    `left:${face.x * 100}%`,
    `top:${face.y * 100}%`,
    `width:${face.w * 100}%`,
    `height:${face.h * 100}%`
  ].join(";");
  return `<div class="safe-zone safe-face" style="${style}"></div>`;
}

function perspectiveClass(item) {
  const raw = item.title_perspective?.mode || item.title_perspective || "flat-sticker";
  return String(raw).toLowerCase().replace(/[^a-z0-9-]/g, "-");
}

function tornPaper(id, content = "", extraClass = "") {
  return `
    <div class="torn-paper ${extraClass}">
      <svg class="paper-edge" viewBox="0 0 1000 360" preserveAspectRatio="none" aria-hidden="true">
        <filter id="paper-noise-${id}">
          <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="${id}" result="noise" />
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" />
        </filter>
        <path filter="url(#paper-noise-${id})" d="M22,34 C80,14 126,42 194,23 C254,8 316,33 376,18 C438,2 500,38 562,19 C642,-2 690,29 760,18 C838,6 898,36 973,18 L990,326 C922,345 862,316 790,342 C724,362 658,330 588,346 C502,368 452,329 374,346 C300,363 232,329 164,348 C98,366 52,334 18,348 Z" />
      </svg>
      <div class="paper-fill"></div>
      <div class="paper-content">${content}</div>
    </div>`;
}

function titleBlock(item, extraClass = "") {
  return `<h1 class="title ${perspectiveClass(item)} ${extraClass}">${renderLines(item.title_lines || [item.title || ""])}</h1>`;
}

function faceImpact(item) {
  return `
    <div class="warm-wash"></div>
    ${titleBlock(item, "face-title")}
    <div class="subtitle sticker-subtitle">${esc(item.subtitle || "")}</div>
    <div class="badge-row">${renderBadges(item.tags || [])}</div>
    <div class="check-stack">${(item.bullets || []).slice(0, 3).map((x) => `<div class="check-pill">${esc(x)}</div>`).join("")}</div>
    <div class="spark s1">✦</div><div class="spark s2">↗</div><div class="spark s3">♡</div>
  `;
}

function scrapbookCollage(item) {
  const title = titleBlock(item, "scrapbook-title");
  return `
    <div class="soft-paper-wash"></div>
    ${tornPaper(41, title, "title-paper main-paper")}
    ${tornPaper(17, `<strong>${esc(item.subtitle || "")}</strong>`, "small-paper subtitle-paper")}
    <div class="memo-paper">${(item.bullets || []).slice(0, 3).map((x) => `<span>${esc(x)}</span>`).join("")}</div>
    <div class="photo-stub"><span>${esc(item.note || "收藏这张")}</span></div>
    <div class="tape tape-a"></div><div class="tape tape-b"></div>
    <div class="line-doodle d1">↝</div><div class="line-doodle d2">☼</div><div class="line-doodle d3">♡</div>
  `;
}

function productHero(item) {
  return `
    <div class="tech-wash"></div>
    <div class="product-panel">
      <div class="panel-title">${esc(item.panel_title || "工具画面")}</div>
      ${(item.bullets || []).slice(0, 5).map((x) => `<div class="tool-row">${esc(x)}</div>`).join("")}
    </div>
    ${titleBlock(item, "product-title")}
    <div class="subtitle tech-subtitle">${esc(item.subtitle || "")}</div>
    <div class="badge-row">${renderBadges(item.tags || [])}</div>
    <div class="hud-corner c1"></div><div class="hud-corner c2"></div>
  `;
}

function perspectiveCompare(item) {
  return `
    <div class="impact-wash"></div>
    <div class="push-card before-card"><span>${esc(item.before_label || "以前")}</span></div>
    <div class="push-card after-card">
      <span>${esc(item.after_label || item.subtitle || "现在")}</span>
    </div>
    ${titleBlock(item, "compare-title")}
    <div class="badge-row">${renderBadges(item.tags || [])}</div>
    <div class="impact-list">${(item.bullets || []).slice(0, 4).map((x) => `<div>${esc(x)}</div>`).join("")}</div>
    <div class="blast">✸</div>
  `;
}

function renderContract(item) {
  const contract = item.layout_contract || item.system || "face-impact";
  if (contract === "face-impact") return faceImpact(item);
  if (contract === "scrapbook-collage") return scrapbookCollage(item);
  if (contract === "product-hero") return productHero(item);
  if (contract === "perspective-compare") return perspectiveCompare(item);
  throw new Error(`unknown layout_contract: ${contract}`);
}

function renderHtml(item, sourceFile) {
  const width = item.canvas?.width || 1080;
  const height = item.canvas?.height || 1440;
  const image = item.background_image ? imgData(resolveImage(sourceFile, item.background_image)) : "";
  const pos = item.background_position || "center";
  const palette = item.palette || {};
  const accent = palette.accent || "#ff5a6f";
  const accent2 = palette.accent2 || "#ffe15a";
  const ink = palette.ink || "#17110f";
  const paper = palette.paper || "#fff8df";
  const contract = item.layout_contract || "face-impact";
  const debugSafeZones = item.debug_safe_zones ? "debug-safe-zones" : "";

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=${width}, initial-scale=1" />
  <title>${esc(item.id || item.title)}</title>
  <style>
    :root {
      --w: ${width}px;
      --h: ${height}px;
      --accent: ${accent};
      --accent2: ${accent2};
      --ink: ${ink};
      --paper: ${paper};
      font-family: "HYZhongHeiTi-197", "Noto Sans SC", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;
    }
    * { box-sizing: border-box; }
    html, body { width: var(--w); height: var(--h); margin: 0; overflow: hidden; background: #ddd; }
    .poster { position: relative; width: var(--w); height: var(--h); overflow: hidden; background: #111; color: var(--ink); }
    .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: ${pos}; }
    .gradient-bg { position: absolute; inset: 0; background:
      radial-gradient(80% 52% at 18% 14%, rgba(255,255,255,.34), transparent 62%),
      linear-gradient(135deg, var(--accent), var(--accent2) 44%, #111 112%); }
    .poster::before { content: ""; position: absolute; inset: 0; z-index: 1; background: linear-gradient(180deg, rgba(0,0,0,.04), rgba(0,0,0,.18)); }
    .title { margin: 0; position: absolute; z-index: 8; font-weight: 950; letter-spacing: 0; line-height: .86; transform-origin: 50% 50%; }
    .title-line { display: block; }
    .flat-sticker { transform: rotate(-5deg); }
    .top-slam { transform: perspective(900px) rotateX(6deg) rotateZ(-7deg) skewX(-8deg); }
    .side-push { transform: perspective(850px) rotateY(-14deg) rotateZ(-5deg) skewX(-6deg); }
    .card-perspective { transform: perspective(760px) rotateX(12deg) rotateY(-10deg) rotateZ(-6deg); }
    .title {
      text-shadow:
        7px 0 #fff, -7px 0 #fff, 0 7px #fff, 0 -7px #fff,
        12px 13px 0 rgba(0,0,0,.22);
    }
    .badge-row { position: absolute; z-index: 11; left: 54px; top: 44px; display: flex; gap: 12px; transform: rotate(-3deg); }
    .badge { display: inline-block; padding: 8px 16px; border: 3px solid rgba(255,255,255,.86); border-radius: 999px; background: rgba(0,0,0,.28); color: #fff; font-size: 28px; font-weight: 950; text-shadow: 0 4px 14px rgba(0,0,0,.35); }
    .safe-zone { position: absolute; z-index: 50; pointer-events: none; display: none; border: 4px dashed rgba(255,0,90,.86); background: rgba(255,0,90,.10); }
    .debug-safe-zones .safe-zone { display: block; }

    .warm-wash { position: absolute; inset: 0; z-index: 2; background: radial-gradient(90% 48% at 20% 14%, rgba(255,122,95,.52), transparent 62%); }
    .face-title { left: 46px; top: 108px; width: 970px; font-size: 134px; color: var(--accent); }
    .face-title .l1 { color: #5f311d; }
    .face-title .l2, .face-title .l3 { font-size: 156px; }
    .sticker-subtitle { position: absolute; z-index: 10; left: 94px; top: 470px; padding: 12px 28px; background: var(--accent2); color: #4e2418; font-size: 42px; font-weight: 950; transform: rotate(-6deg); box-shadow: 10px 10px 0 rgba(0,0,0,.15); }
    .check-stack { position: absolute; z-index: 10; left: 68px; bottom: 248px; display: grid; gap: 18px; transform: rotate(-5deg); }
    .check-pill { width: max-content; padding: 14px 24px; border-radius: 999px; background: rgba(255,255,255,.88); font-size: 36px; font-weight: 950; box-shadow: 0 9px 0 rgba(0,0,0,.14); }
    .check-pill::before { content: "✓"; color: #fff; background: var(--accent); border-radius: 50%; padding: 0 10px; margin-right: 10px; }
    .spark { position: absolute; z-index: 12; color: var(--accent2); font-size: 74px; font-weight: 950; text-shadow: 0 7px 0 rgba(0,0,0,.15); }
    .s1 { right: 88px; top: 330px; transform: rotate(18deg); }
    .s2 { right: 120px; bottom: 180px; transform: rotate(-12deg); color: #fff; }
    .s3 { left: 72px; bottom: 108px; transform: rotate(13deg); color: #fff; }

    .soft-paper-wash { position: absolute; inset: 0; z-index: 2; background: linear-gradient(90deg, rgba(224,235,188,.78), transparent 66%); }
    .torn-paper { position: absolute; z-index: 7; filter: drop-shadow(14px 15px 0 rgba(0,0,0,.13)); }
    .paper-edge { position: absolute; inset: 0; width: 100%; height: 100%; fill: rgba(255,252,230,.96); }
    .paper-fill { position: absolute; inset: 16px; background: rgba(255,252,230,.72); filter: blur(3px); }
    .paper-content { position: absolute; inset: 34px 42px; }
    .main-paper { left: -18px; top: 72px; width: 760px; height: 640px; transform: rotate(-4deg); }
    .small-paper { left: 76px; top: 664px; width: 560px; height: 132px; transform: rotate(-2deg); }
    .scrapbook-title { position: static; font-family: "STXingkai", "KaiTi", "Microsoft YaHei", serif; color: #41682f; font-size: 106px; line-height: .9; text-shadow: 3px 3px 0 rgba(255,255,255,.92); }
    .scrapbook-title .l3 { color: #78a344; font-size: 150px; }
    .subtitle-paper strong { color: #fff; background: rgba(65,104,47,.84); border: 3px dashed rgba(255,255,255,.85); padding: 12px 20px; font-size: 36px; display: inline-block; transform: rotate(1deg); }
    .memo-paper { position: absolute; z-index: 9; left: 72px; top: 830px; width: 330px; display: grid; gap: 8px; padding: 24px; border-radius: 26px; background: rgba(255,252,221,.88); color: #456133; font-family: "STXingkai", "KaiTi", serif; font-size: 36px; transform: rotate(5deg); box-shadow: 0 9px 0 rgba(0,0,0,.12); }
    .photo-stub { position: absolute; z-index: 8; right: 72px; bottom: 90px; width: 330px; height: 230px; background: rgba(255,249,224,.93); border: 12px solid #fff8da; transform: rotate(-7deg); box-shadow: 12px 14px 0 rgba(0,0,0,.13); display: grid; place-items: center; text-align: center; color: #6a8643; font-family: "STXingkai", "KaiTi", serif; font-size: 34px; }
    .tape { position: absolute; z-index: 12; width: 142px; height: 42px; background: rgba(136,172,92,.72); }
    .tape-a { right: 170px; bottom: 300px; transform: rotate(3deg); }
    .tape-b { left: 390px; top: 640px; transform: rotate(-7deg); }
    .line-doodle { position: absolute; z-index: 13; color: #fff; font-size: 62px; font-weight: 950; }
    .d1 { left: 430px; bottom: 280px; transform: rotate(-12deg); }
    .d2 { left: 38px; top: 46px; transform: rotate(-15deg); }
    .d3 { left: 500px; top: 212px; color: #5d8941; transform: rotate(12deg); }

    .tech-wash { position: absolute; inset: 0; z-index: 2; background: linear-gradient(180deg, rgba(4,10,28,.18), rgba(4,10,28,.76)), radial-gradient(70% 44% at 58% 18%, rgba(48,230,255,.35), transparent 64%); }
    .product-panel { position: absolute; z-index: 6; right: 54px; top: 330px; width: 600px; min-height: 720px; padding: 30px; border: 3px solid rgba(64,232,255,.78); background: rgba(3,9,28,.68); transform: perspective(900px) rotateY(-9deg) rotateZ(2deg); box-shadow: 0 0 30px rgba(64,232,255,.25); }
    .panel-title { color: var(--accent2); font-size: 42px; font-weight: 950; margin-bottom: 22px; }
    .tool-row { color: #fff; font-size: 30px; font-weight: 850; padding: 15px 12px; border-left: 6px solid var(--accent2); background: rgba(255,255,255,.06); margin-bottom: 12px; }
    .product-title { left: 52px; top: 112px; width: 930px; color: #fff; font-size: 116px; text-shadow: 0 0 18px rgba(64,232,255,.56), 9px 9px 0 rgba(30,80,180,.62); }
    .product-title .l1 { color: var(--accent2); font-size: 136px; }
    .tech-subtitle { position: absolute; z-index: 10; left: 94px; top: 576px; padding: 14px 30px; color: #fff; background: rgba(3,10,30,.80); border: 3px solid var(--accent2); font-size: 38px; font-weight: 950; transform: skew(-12deg) rotate(-3deg); }
    .hud-corner { position: absolute; z-index: 7; width: 220px; height: 220px; border-color: var(--accent2); border-style: solid; opacity: .85; }
    .c1 { left: 42px; bottom: 52px; border-width: 0 0 4px 4px; }
    .c2 { right: 42px; top: 52px; border-width: 4px 4px 0 0; }

    .impact-wash { position: absolute; inset: 0; z-index: 2; background: linear-gradient(120deg, rgba(0,0,0,.58), rgba(0,0,0,.08) 58%, rgba(255,110,0,.34)); }
    .push-card { position: absolute; z-index: 6; display: grid; place-items: center; text-align: center; font-weight: 950; }
    .before-card { left: 60px; bottom: 350px; width: 280px; height: 130px; color: #fff; border: 4px solid rgba(255,255,255,.75); background: rgba(0,0,0,.55); transform: perspective(700px) rotateY(18deg) rotateZ(-8deg); font-size: 38px; }
    .after-card { right: -32px; bottom: 142px; width: 560px; height: 170px; color: #111; background: var(--accent); transform: perspective(680px) rotateY(-18deg) rotateZ(-9deg); font-size: 48px; box-shadow: 18px 22px 0 rgba(0,0,0,.22); }
    .compare-title { left: 44px; top: 94px; width: 970px; color: #fff; font-size: 128px; text-shadow: 7px 7px 0 #000, 14px 14px 0 var(--accent); }
    .compare-title .l2, .compare-title .l3 { color: var(--accent); font-size: 150px; }
    .impact-list { position: absolute; z-index: 9; left: 64px; bottom: 86px; display: grid; gap: 18px; color: #fff; font-size: 34px; font-weight: 950; }
    .impact-list div::before { content: "↗"; color: var(--accent); border: 3px solid var(--accent); padding: 2px 10px; margin-right: 14px; }
    .blast { position: absolute; z-index: 12; right: 70px; top: 90px; color: var(--accent); font-size: 90px; transform: rotate(18deg); }
  </style>
</head>
<body>
  <main class="poster ${contract} ${debugSafeZones}">
    ${image ? `<img class="bg" src="${image}" alt="" />` : `<div class="gradient-bg"></div>`}
    ${renderContract(item)}
    ${renderSafeZones(item)}
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
  const sourceFile = process.argv[2];
  if (!sourceFile) {
    console.error("Usage: node scripts/render-xhs-poster-v04.cjs <cases.json> [case-id]");
    process.exit(1);
  }
  const resolved = path.resolve(process.cwd(), sourceFile);
  const itemId = process.argv[3];
  const cases = readJson(resolved).cases;
  const item = itemId ? cases.find((x) => x.id === itemId) : cases[0];
  if (!item) throw new Error(`case not found: ${itemId}`);
  const width = item.canvas?.width || 1080;
  const height = item.canvas?.height || 1440;
  const html = renderHtml(item, resolved);
  const browser = await launchChromium();
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  const png = await page.locator(".poster").screenshot({ type: "png" });
  await browser.close();
  process.stdout.write(JSON.stringify({
    id: item.id,
    output_name: item.output_name || `${slugFileName(item.title || item.id)}.png`,
    html_name: `${slugFileName(item.id)}.html`,
    html_base64: Buffer.from(html, "utf8").toString("base64"),
    png_base64: png.toString("base64")
  }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
