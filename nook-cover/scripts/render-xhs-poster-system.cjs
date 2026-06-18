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

function renderLines(lines, cls = "title-line") {
  return (lines || []).map((line, i) => `<span class="${cls} l${i + 1}">${esc(line)}</span>`).join("");
}

function renderPills(items, cls = "pill") {
  return (items || []).map((item, i) => `<span class="${cls} p${i + 1}">${esc(item)}</span>`).join("");
}

function renderHtml(item, sourceFile) {
  const width = item.canvas?.width || 1080;
  const height = item.canvas?.height || 1440;
  const image = imgData(resolveImage(sourceFile, item.background_image));
  const pos = item.background_position || "center";
  const system = item.system;
  const title = item.title_lines || [item.title || ""];
  const bullets = item.bullets || [];
  const tags = item.tags || [];
  const palette = item.palette || {};
  const accent = palette.accent || "#ff5f6d";
  const accent2 = palette.accent2 || "#ffe45f";
  const ink = palette.ink || "#1a120f";
  const paper = palette.paper || "#fff8df";

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=${width}, initial-scale=1" />
  <title>${esc(item.id)}</title>
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
    .doodle { position: absolute; z-index: 7; font-weight: 950; pointer-events: none; }
    .top-note { position: absolute; z-index: 8; left: 54px; top: 44px; font-size: 28px; font-weight: 950; color: #fff; text-shadow: 0 4px 16px rgba(0,0,0,.35); transform: rotate(-3deg); }
    .top-note span { display: inline-block; padding: 8px 16px; margin-right: 10px; border: 3px solid rgba(255,255,255,.82); border-radius: 999px; background: rgba(0,0,0,.24); backdrop-filter: blur(8px); }

    .peach-sticker::after {
      content: "";
      position: absolute;
      inset: 0;
      background:
        radial-gradient(86% 58% at 18% 15%, rgba(255,130,99,.46), transparent 62%),
        linear-gradient(180deg, rgba(255,146,118,.12), rgba(255,112,98,.25));
      z-index: 1;
    }
    .peach-sticker .brush {
      position: absolute; z-index: 3; left: 48px; top: 116px; width: 930px; height: 262px;
      background: rgba(255,250,233,.92);
      clip-path: polygon(2% 19%, 94% 0, 100% 18%, 94% 31%, 100% 47%, 88% 62%, 94% 78%, 7% 100%, 0 84%, 6% 64%, 0 48%, 8% 34%);
      transform: rotate(-6deg);
      box-shadow: 0 16px 0 rgba(117,46,27,.16);
    }
    .peach-sticker h1 {
      position: absolute; z-index: 9; left: 92px; top: 102px; width: 880px; margin: 0;
      font-size: 128px; line-height: .84; font-weight: 950; color: var(--accent);
      transform: rotate(-4deg); letter-spacing: 0;
      text-shadow: 7px 0 #fff, -7px 0 #fff, 0 7px #fff, 0 -7px #fff, 13px 15px 0 rgba(83,34,23,.24);
    }
    .peach-sticker h1 .l1 { color: #6b3a24; font-size: 124px; }
    .peach-sticker .subtitle {
      position: absolute; z-index: 10; left: 120px; top: 418px; padding: 12px 28px;
      background: var(--accent2); color: #5c2b1b; font-size: 44px; font-weight: 950;
      transform: rotate(-5deg); box-shadow: 10px 10px 0 rgba(108,55,32,.16);
    }
    .peach-sticker .check-list { position: absolute; z-index: 10; left: 82px; top: 660px; display: grid; gap: 20px; transform: rotate(-5deg); }
    .peach-sticker .check { display: inline-flex; align-items: center; gap: 10px; width: max-content; padding: 12px 24px 12px 15px; border-radius: 999px; background: rgba(255,255,255,.88); font-size: 38px; font-weight: 950; box-shadow: 0 8px 0 rgba(88,42,30,.16); }
    .peach-sticker .check::before { content: "✓"; display: grid; place-items: center; width: 42px; height: 42px; border-radius: 50%; color: #fff; background: var(--accent); }
    .peach-sticker .cloud { position: absolute; z-index: 10; left: 58px; bottom: 126px; width: 390px; padding: 28px 34px; border: 4px dashed #fff; border-radius: 46% 54% 48% 52%; background: rgba(255,111,94,.88); color: #fff; font-family: "STXingkai", "KaiTi", serif; font-size: 46px; line-height: 1.12; text-align: center; transform: rotate(-8deg); box-shadow: 0 13px 0 rgba(118,48,35,.16); }
    .peach-sticker .d1 { left: 46px; top: 74px; font-size: 62px; color: #fff; transform: rotate(-22deg); }
    .peach-sticker .d2 { right: 92px; top: 236px; font-size: 72px; color: #ffe66a; transform: rotate(12deg); }
    .peach-sticker .d3 { right: 94px; bottom: 212px; font-size: 78px; color: #fff; transform: rotate(22deg); }

    .green-handbook { color: #35512b; }
    .green-handbook::after {
      content: ""; position: absolute; inset: 0; z-index: 1;
      background: linear-gradient(90deg, rgba(221,231,186,.80), rgba(221,231,186,.08) 58%, rgba(0,0,0,.04));
    }
    .green-handbook .paper {
      position: absolute; z-index: 3; left: -22px; top: 62px; width: 740px; height: 610px;
      background: rgba(255,254,233,.94);
      clip-path: polygon(0 8%, 96% 0, 92% 10%, 100% 21%, 94% 38%, 99% 54%, 91% 71%, 96% 90%, 4% 100%, 10% 88%, 0 75%, 8% 59%, 0 44%, 7% 27%);
      transform: rotate(-2deg);
      box-shadow: 16px 18px 0 rgba(63,91,45,.12);
    }
    .green-handbook h1 {
      position: absolute; z-index: 9; left: 78px; top: 104px; width: 660px; margin: 0;
      color: #365a2f; font-family: "STXingkai", "KaiTi", "Microsoft YaHei", serif;
      font-size: 116px; line-height: .90; font-weight: 950; transform: rotate(3deg);
      text-shadow: 3px 3px 0 rgba(255,255,255,.9);
    }
    .green-handbook h1 .l3 { color: #80aa42; font-size: 166px; line-height: .70; }
    .green-handbook .subtitle {
      position: absolute; z-index: 10; left: 84px; top: 624px; padding: 12px 22px;
      background: rgba(70,112,55,.88); color: #fff; border: 3px dashed rgba(255,255,255,.88);
      font-size: 37px; font-weight: 850; transform: rotate(-2deg);
    }
    .green-handbook .memo {
      position: absolute; z-index: 10; left: 72px; top: 795px; width: 350px; padding: 24px;
      background: rgba(255,252,220,.90); color: #4c6537; border-radius: 20px 32px 22px 28px;
      font-family: "STXingkai", "KaiTi", serif; font-size: 38px; line-height: 1.25; transform: rotate(5deg);
      box-shadow: 0 9px 0 rgba(68,90,48,.14);
    }
    .green-handbook .postcard {
      position: absolute; z-index: 9; right: 84px; bottom: 88px; width: 330px; height: 238px;
      background: rgba(255,251,231,.92); border: 12px solid #fff8da; transform: rotate(-6deg);
      box-shadow: 12px 14px 0 rgba(68,90,48,.15);
    }
    .green-handbook .postcard::before { content: ""; position: absolute; left: 82px; top: -34px; width: 130px; height: 42px; background: rgba(122,165,78,.72); transform: rotate(5deg); }
    .green-handbook .postcard span { position: absolute; inset: 30px; display: grid; place-items: center; border: 2px dashed rgba(53,81,43,.35); color: #6f9046; font-family: "STXingkai", "KaiTi", serif; font-size: 34px; text-align: center; }
    .green-handbook .d1 { left: 42px; top: 42px; font-size: 54px; color: #fff; transform: rotate(-18deg); }
    .green-handbook .d2 { left: 420px; top: 192px; font-size: 54px; color: #6c9846; transform: rotate(18deg); }
    .green-handbook .d3 { left: 418px; bottom: 248px; font-size: 70px; color: #fff; transform: rotate(-12deg); }

    .neon-tech { background: #070b1b; color: #fff; }
    .neon-tech::after {
      content: ""; position: absolute; inset: 0; z-index: 1;
      background:
        radial-gradient(70% 48% at 50% 15%, rgba(25,209,255,.34), transparent 65%),
        linear-gradient(180deg, rgba(2,5,18,.18), rgba(2,5,18,.86));
    }
    .neon-tech .hud {
      position: absolute; z-index: 3; inset: 58px 46px 520px 46px;
      border: 3px solid rgba(56,222,255,.68);
      clip-path: polygon(6% 0, 90% 0, 100% 16%, 100% 88%, 92% 100%, 8% 100%, 0 88%, 0 12%);
      box-shadow: 0 0 34px rgba(46,207,255,.25), inset 0 0 28px rgba(46,207,255,.15);
    }
    .neon-tech h1 {
      position: absolute; z-index: 9; left: 92px; top: 124px; width: 890px; margin: 0;
      font-size: 112px; line-height: .92; font-weight: 950; color: #fff; transform: skew(-7deg) rotate(-2deg);
      text-shadow: 0 0 18px rgba(56,222,255,.58), 8px 8px 0 rgba(24,87,187,.55);
    }
    .neon-tech h1 .l1 { color: var(--accent2); font-size: 132px; }
    .neon-tech .subtitle {
      position: absolute; z-index: 10; left: 160px; top: 560px; padding: 14px 36px;
      color: #fff; background: rgba(4,18,42,.84); border: 3px solid #23e6ff; font-size: 42px; font-weight: 950;
      transform: skew(-12deg) rotate(-2deg); box-shadow: 0 0 28px rgba(35,230,255,.28);
    }
    .neon-tech .tool-list { position: absolute; z-index: 10; left: 60px; bottom: 132px; width: 360px; display: grid; gap: 14px; }
    .neon-tech .tool { padding: 14px 16px; border-left: 6px solid var(--accent2); background: rgba(2,9,32,.66); color: #fff; font-size: 30px; font-weight: 850; box-shadow: 0 0 18px rgba(84,108,255,.20); }
    .neon-tech .bottom { position: absolute; z-index: 10; right: 54px; bottom: 74px; display: flex; gap: 14px; }
    .neon-tech .bottom span { width: 150px; min-height: 126px; display: grid; place-items: center; text-align: center; padding: 14px; color: #fff; font-size: 26px; font-weight: 900; border: 2px solid rgba(141,101,255,.8); background: rgba(12,18,55,.72); box-shadow: 0 0 18px rgba(141,101,255,.28); }
    .neon-tech .d1 { left: 34px; top: 34px; color: #38deff; font-size: 52px; }
    .neon-tech .d2 { right: 70px; top: 642px; color: #9a63ff; font-size: 82px; transform: rotate(16deg); }

    .power-impact { color: #fff; background: #050505; }
    .power-impact::after {
      content: ""; position: absolute; inset: 0; z-index: 1;
      background:
        linear-gradient(120deg, rgba(0,0,0,.60), rgba(0,0,0,.05) 52%, rgba(245,115,0,.42)),
        radial-gradient(62% 44% at 24% 16%, rgba(255,119,0,.42), transparent 64%);
    }
    .power-impact .slash {
      position: absolute; z-index: 3; left: -70px; top: 106px; width: 920px; height: 340px;
      background: rgba(0,0,0,.76); clip-path: polygon(6% 0, 100% 0, 92% 100%, 0 88%);
      transform: rotate(-5deg); box-shadow: 16px 20px 0 rgba(255,119,0,.72);
    }
    .power-impact h1 {
      position: absolute; z-index: 9; left: 70px; top: 78px; width: 790px; margin: 0;
      font-size: 122px; line-height: .88; font-weight: 950; color: #fff; transform: skew(-9deg) rotate(-5deg);
      text-shadow: 7px 7px 0 #000, 13px 13px 0 rgba(255,119,0,.88);
    }
    .power-impact h1 .l2, .power-impact h1 .l3 { color: var(--accent); font-size: 142px; }
    .power-impact .subtitle {
      position: absolute; z-index: 10; left: 74px; top: 552px; padding: 12px 28px;
      color: #fff; background: rgba(0,0,0,.78); border: 3px solid var(--accent); font-size: 40px; font-weight: 950;
      transform: skew(-12deg) rotate(-4deg);
    }
    .power-impact .check-list { position: absolute; z-index: 10; left: 72px; bottom: 116px; width: 420px; display: grid; gap: 18px; }
    .power-impact .check { display: grid; grid-template-columns: 62px 1fr; align-items: center; gap: 14px; color: #fff; font-size: 32px; font-weight: 900; }
    .power-impact .check::before { content: "↗"; display: grid; place-items: center; width: 56px; height: 56px; color: var(--accent); border: 3px solid var(--accent); transform: rotate(-12deg); }
    .power-impact .ribbon {
      position: absolute; z-index: 9; right: -62px; bottom: 18px; width: 500px; height: 156px;
      background: var(--accent); transform: rotate(-12deg); clip-path: polygon(0 15%, 100% 0, 92% 100%, 8% 84%);
      display: grid; place-items: center; color: #111; font-size: 42px; font-weight: 950;
    }
    .power-impact .d1 { left: 40px; top: 34px; color: var(--accent); font-size: 64px; transform: rotate(-17deg); }
    .power-impact .d2 { right: 48px; top: 38px; color: var(--accent); font-size: 86px; transform: rotate(21deg); }
  </style>
</head>
<body>
  <main class="poster ${system}">
    <img class="bg" src="${image}" alt="" />
    <div class="top-note">${renderPills(tags, "top-tag")}</div>
    ${system === "peach-sticker" ? `
      <div class="brush"></div>
      <h1>${renderLines(title)}</h1>
      <div class="subtitle">${esc(item.subtitle)}</div>
      <div class="check-list">${bullets.slice(0, 3).map((x) => `<div class="check">${esc(x)}</div>`).join("")}</div>
      <div class="cloud">${esc(item.note || "普通人也能\\A逆袭赚钱").replace(/\\A/g, "<br>")}</div>
      <div class="doodle d1">〰</div><div class="doodle d2">✦</div><div class="doodle d3">↗</div>
    ` : ""}
    ${system === "green-handbook" ? `
      <div class="paper"></div>
      <h1>${renderLines(title)}</h1>
      <div class="subtitle">${esc(item.subtitle)}</div>
      <div class="memo">${bullets.slice(0, 3).map((x) => esc(x)).join("<br>")}</div>
      <div class="postcard"><span>${esc(item.note || "值得收藏的小店")}</span></div>
      <div class="doodle d1">☼</div><div class="doodle d2">♡</div><div class="doodle d3">↝</div>
    ` : ""}
    ${system === "neon-tech" ? `
      <div class="hud"></div>
      <h1>${renderLines(title)}</h1>
      <div class="subtitle">${esc(item.subtitle)}</div>
      <div class="tool-list">${bullets.slice(0, 5).map((x) => `<div class="tool">${esc(x)}</div>`).join("")}</div>
      <div class="bottom">${(item.metrics || ["效率翻倍", "少踩坑", "可复用"]).slice(0, 3).map((x) => `<span>${esc(x)}</span>`).join("")}</div>
      <div class="doodle d1">＋</div><div class="doodle d2">⌁</div>
    ` : ""}
    ${system === "power-impact" ? `
      <div class="slash"></div>
      <h1>${renderLines(title)}</h1>
      <div class="subtitle">${esc(item.subtitle)}</div>
      <div class="check-list">${bullets.slice(0, 4).map((x) => `<div class="check">${esc(x)}</div>`).join("")}</div>
      <div class="ribbon">${esc(item.note || "今天开始")}</div>
      <div class="doodle d1">╱</div><div class="doodle d2">✸</div>
    ` : ""}
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
    console.error("Usage: node scripts/render-xhs-poster-system.cjs <cases.json>");
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
    html_base64: Buffer.from(html, "utf8").toString("base64"),
    png_base64: png.toString("base64")
  }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
