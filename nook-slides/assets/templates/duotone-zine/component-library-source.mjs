import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const C = {
  paper: "#f3ecd8", soft: "#f8f0dd", ink: "#171713", muted: "#625f55",
  blue: "#3153b8", pink: "#e76186", gold: "#e8b13f", white: "#ffffff",
};
const FONT_TITLE = "Source Han Serif CN Heavy";
const FONT_BODY = "LXGW WenKai";
const FONT_MONO = "Consolas";
const FONT_NUM = "Bodoni 72";

const argv = Object.fromEntries(process.argv.slice(2).reduce((rows, value, index, all) => {
  if (value.startsWith("--")) rows.push([value.slice(2), all[index + 1]]);
  return rows;
}, []));
const output = argv.out || path.join(path.dirname(new URL(import.meta.url).pathname), "component-library-v0.4.0.pptx");
const qaDir = argv.qa || path.join(path.dirname(output), "component-library-v0.4.0-qa");

function shape(slide, name, geometry, left, top, width, height, fill = C.soft, line = C.ink, lineWidth = 2, rotation = 0) {
  return slide.shapes.add({
    geometry, name, position: { left, top, width, height, rotation }, fill,
    line: { style: "solid", fill: line, width: lineWidth },
  });
}
function text(slide, name, value, left, top, width, height, size = 22, color = C.ink, bold = false, fontFamily = FONT_BODY, alignment = "left") {
  const box = shape(slide, name, "textbox", left, top, width, height, "none", "none", 0);
  box.text = value;
  box.text.style = { fontSize: size, color, bold, fontFamily, alignment };
  return box;
}
function rule(slide, name, left, top, width, height = 4, fill = C.ink) {
  return shape(slide, name, "rect", left, top, width, height, fill, fill, 0);
}
function panel(slide, name, left, top, width, height, accent = C.blue, fill = C.soft) {
  shape(slide, `${name}-shadow`, "rect", left + 6, top + 6, width, height, accent, accent, 0);
  return shape(slide, name, "rect", left, top, width, height, fill, C.ink, 2);
}
function pill(slide, name, value, left, top, width, fill = C.ink, color = C.white) {
  shape(slide, `${name}-shape`, "rect", left, top, width, 28, fill, C.ink, 1);
  return text(slide, name, value, left + 6, top + 5, width - 12, 18, 10, color, true, FONT_MONO, "center");
}
function page(slide, code, titleValue, note, number) {
  slide.background.fill = C.paper;
  text(slide, `page-${number}-code`, code, 60, 28, 320, 20, 10, C.muted, false, FONT_MONO);
  text(slide, `page-${number}-note`, note, 830, 28, 390, 20, 10, C.muted, false, FONT_MONO, "right");
  text(slide, `page-${number}-title`, titleValue, 60, 62, 800, 60, 38, C.ink, true, FONT_TITLE);
  text(slide, `page-${number}-folio`, `P${String(number).padStart(2, "0")} / ${code.split("/")[1]?.trim() || "COMPONENT"}`, 60, 680, 300, 18, 9, C.muted, false, FONT_MONO);
  panel(slide, `page-${number}-use`, 920, 620, 300, 48, C.ink, C.soft);
  text(slide, `page-${number}-use-text`, "可编辑组件 · 视觉系统 v0.4.0", 940, 636, 260, 16, 11, C.muted, false, FONT_BODY, "center");
}
function addCard(slide, name, x, y, w, h, index, titleValue, bodyValue, accent) {
  const base = panel(slide, name, x, y, w, h, accent);
  shape(slide, `${name}-strip`, "rect", x, y, w, 52, accent, C.ink, 2);
  text(slide, `${name}-index`, index, x + 18, y + 13, 55, 30, 27, accent === C.gold ? C.ink : C.white, true, FONT_NUM);
  text(slide, `${name}-title`, titleValue, x + 28, y + 86, w - 56, 36, 23, C.ink, true, FONT_TITLE);
  rule(slide, `${name}-rule`, x + 28, y + 138, 74, 4, accent);
  if (bodyValue) text(slide, `${name}-body`, bodyValue, x + 28, y + 168, w - 56, h - 192, 16, C.muted, false, FONT_BODY);
  return base;
}

const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

// 01 Cover
{
  const s = deck.slides.add(); page(s, "C01 / GIANT TITLE", "巨型标题页", "少字 / 大字 / 强入口", 1);
  text(s, "cover-headline", "可编辑\nPPT\n不是截图", 74, 150, 520, 230, 55, C.ink, true, FONT_TITLE);
  rule(s, "cover-accent", 76, 420, 90, 5, C.pink);
  text(s, "cover-body", "它是一套能被拆开、移动、重排、再编辑的出版组件。", 76, 452, 500, 70, 21, C.muted);
  panel(s, "cover-image-slot", 735, 132, 430, 420, C.blue, C.soft);
  pill(s, "cover-image-label", "IMG-A / 4:5", 758, 154, 140);
  shape(s, "cover-image-inner", "rect", 758, 198, 384, 320, C.paper, C.muted, 1);
}
// 02 Statement
{
  const s = deck.slides.add(); page(s, "C02 / STATEMENT", "一句话判断页", "纯文字唯一例外", 2);
  panel(s, "statement-panel", 82, 175, 1110, 330, C.pink, C.blue);
  text(s, "statement-main", "模型不能临场\n发明页面", 120, 220, 640, 130, 49, C.white, true, FONT_TITLE);
  text(s, "statement-sub", "它只能选择组件、填入内容、接受校验。", 124, 390, 720, 42, 22, C.white);
  pill(s, "statement-label", "CORE JUDGEMENT", 925, 220, 200, C.ink, C.white);
}
// 03 Big number
{
  const s = deck.slides.add(); page(s, "C03 / BIG NUMBER", "大数字页", "数字是主角", 3);
  text(s, "big-number", "13", 72, 150, 280, 125, 104, C.ink, true, FONT_NUM);
  text(s, "big-label", "类可编辑组件", 78, 285, 360, 48, 31, C.ink, true, FONT_TITLE);
  text(s, "big-body", "少而稳定，比临场发明更重要。", 80, 355, 380, 44, 20, C.muted);
  [["05","图片槽",C.blue],["04","结构骨架",C.pink],["04","内容组件",C.gold]].forEach(([n,t,a],i)=>{
    panel(s,`metric-${i}`,560+i*210,190,170,245,a,C.soft); text(s,`metric-num-${i}`,n,582+i*210,222,120,54,43,C.ink,true,FONT_NUM);
    rule(s,`metric-rule-${i}`,584+i*210,296,70,4,a); text(s,`metric-title-${i}`,t,582+i*210,330,125,60,19,C.ink,true,FONT_TITLE);
  });
}
// 04 Process: connectors first in z-order after creation default behind nodes.
{
  const s = deck.slides.add(); page(s, "C04 / PROCESS", "流程页", "明确线性方向", 4);
  text(s, "process-sub", "输入 → 判断 → 匹配 → 输出", 72, 132, 600, 32, 20, C.muted);
  const cards = [
    addCard(s,"process-1",55,230,245,260,"01","内容锁定","确认可见文字",C.blue),
    addCard(s,"process-2",365,230,245,260,"02","形式确认","确认页面任务",C.pink),
    addCard(s,"process-3",675,230,245,260,"03","组件匹配","进入批准变体",C.gold),
    addCard(s,"process-4",985,230,245,260,"04","确定性生成","脚本填充检查",C.ink),
  ];
  for (let i=0;i<cards.length-1;i++) s.shapes.connect(cards[i],cards[i+1],{kind:"straight",fromSide:"right",toSide:"left",line:{style:"solid",fill:C.ink,width:4},tail:{type:"arrow",width:"med",length:"med"}});
}
// 05 Timeline
{
  const s = deck.slides.add(); page(s, "C05 / TIMELINE", "时间轴", "主轴 / 节点 / 时间标签", 5);
  text(s, "timeline-sub", "所有事件围绕同一时间方向生长。", 72, 132, 560, 32, 20, C.muted);
  shape(s,"timeline-axis","rightArrow",80,352,1120,20,C.blue,C.blue,0);
  const xs=[120,405,690,975], labels=["06.23","06.27","06.28","06.29"], desc=["建立方向","完成组件","跑通生成","回到骨架"], colors=[C.ink,C.blue,C.pink,C.gold];
  xs.forEach((x,i)=>{
    shape(s,`timeline-node-${i}`,"ellipse",x,346,28,28,C.paper,C.ink,3);
    rule(s,`timeline-guide-${i}`,x+12,i%2===0?250:374,3,96,C.ink);
    text(s,`timeline-label-${i}`,labels[i],x-18,i%2===0?190:482,160,54,43,colors[i],true,FONT_NUM);
    text(s,`timeline-desc-${i}`,desc[i],x-16,i%2===0?260:538,170,30,17,C.muted);
  });
}
// 06 Cycle
{
  const s = deck.slides.add(); page(s, "C06 / CYCLE", "循环图", "闭环 / 方向 / 写回", 6);
  text(s, "cycle-sub", "每一次检查都会回到下一轮输入。", 72, 132, 560, 32, 20, C.muted);
  const nodes=[
    panel(s,"cycle-input",500,170,280,80,C.blue),
    panel(s,"cycle-generate",875,330,230,80,C.pink),
    panel(s,"cycle-check",500,490,280,80,C.gold),
    panel(s,"cycle-writeback",175,330,230,80,C.ink),
  ];
  const labels=[["01","输入"],["02","生成"],["03","检查"],["04","写回"]];
  [[0,1,"right","top"],[1,2,"bottom","right"],[2,3,"left","bottom"],[3,0,"top","left"]].forEach(([a,b,fromSide,toSide])=>s.shapes.connect(nodes[a],nodes[b],{kind:"curved",fromSide,toSide,line:{style:"solid",fill:C.ink,width:3},tail:{type:"arrow",width:"med",length:"med"}}));
  nodes.forEach((node,i)=>{const p=node.position;text(s,`cycle-num-${i}`,labels[i][0],p.left+24,p.top+20,50,30,22,[C.blue,C.pink,C.gold,C.ink][i],true,FONT_NUM);text(s,`cycle-title-${i}`,labels[i][1],p.left+90,p.top+22,p.width-110,30,23,C.ink,true,FONT_TITLE);});
  text(s,"cycle-center","能力\n沉淀",540,330,200,80,31,C.ink,true,FONT_TITLE,"center");
}
// 07 Hierarchy
{
  const s = deck.slides.add(); page(s, "C07 / HIERARCHY", "层级页", "父级 / 子级 / 归属", 7);
  text(s, "hierarchy-sub", "层级来自归属关系，不来自上下错落。", 72, 132, 640, 32, 20, C.muted);
  const parent=panel(s,"hierarchy-parent",420,180,440,95,C.blue); text(s,"hierarchy-parent-text","双色独立刊物视觉系统",455,212,370,34,25,C.ink,true,FONT_TITLE,"center");
  const children=[[155,"结构骨架",C.blue],[505,"主题 token",C.pink],[855,"图片资产",C.gold]].map(([x,t,a],i)=>{const n=panel(s,`hierarchy-child-${i}`,x,390,270,110,a);text(s,`hierarchy-child-title-${i}`,t,x+24,420,222,34,22,C.ink,true,FONT_TITLE,"center");return n;});
  children.forEach(n=>s.shapes.connect(parent,n,{kind:"elbow",fromSide:"bottom",toSide:"top",line:{style:"solid",fill:C.ink,width:3}}));
}
// 08 Comparison with matched fields
{
  const s = deck.slides.add(); page(s, "C08 / COMPARISON", "对比页", "镜像字段 / 共享基线", 8);
  text(s,"compare-left-head","自由生成",110,165,360,50,34,C.ink,true,FONT_TITLE); text(s,"compare-right-head","模板执行",810,165,360,50,34,C.pink,true,FONT_TITLE);
  rule(s,"compare-divider",638,160,4,390,C.ink);
  const rows=[["Prompt 约束","CONSTRAINT","Schema 约束"],["重新发明页面","LAYOUT","调用批准变体"],["可能删改文字","TEXT","内容 hash 锁定"],["打开就算完成","QA","真实成品验收"]];
  rows.forEach((r,i)=>{const y=245+i*74;rule(s,`compare-row-${i}`,90,y+52,1100,2,C.ink);text(s,`compare-l-${i}`,r[0],110,y,390,36,20,C.ink,false,FONT_BODY,"center");text(s,`compare-m-${i}`,r[1],545,y+5,190,24,11,C.muted,true,FONT_MONO,"center");text(s,`compare-r-${i}`,r[2],780,y,390,36,20,C.ink,false,FONT_BODY,"center");});
}
// 09 Image-text
{
  const s=deck.slides.add(); page(s,"C09 / IMAGE + TEXT","图文混排页","主图先承担视觉",9);
  panel(s,"image-text-slot",70,165,650,400,C.blue,C.soft);pill(s,"image-text-label","MAIN IMAGE",92,187,145);shape(s,"image-text-inner","rect",95,235,600,300,C.paper,C.muted,1);
  panel(s,"image-text-copy",790,220,380,250,C.pink,C.ink);text(s,"image-text-title","图像先承担\n主视觉",825,260,310,90,36,C.white,true,FONT_TITLE);text(s,"image-text-body","文字只负责把图像和观点扣在一起。",828,380,300,54,18,C.white);
}
// 10 Image collage
{
  const s=deck.slides.add(); page(s,"C10 / COLLAGE","图片拼贴页","一主两辅 / 不平均",10);
  panel(s,"collage-main",65,160,650,430,C.blue,C.soft);pill(s,"collage-main-label","PRIMARY",88,182,120);
  panel(s,"collage-side-1",770,160,400,190,C.pink,C.soft);pill(s,"collage-side-label-1","EVIDENCE B",792,182,130);
  panel(s,"collage-side-2",770,400,400,190,C.gold,C.soft);pill(s,"collage-side-label-2","EVIDENCE C",792,422,130);
}
// 11 Brand assets
{
  const s=deck.slides.add(); page(s,"C11 / BRAND ASSETS","Logo / IP 资产页","品牌资产不临场伪造",11);
  panel(s,"brand-logo",70,170,500,300,C.blue,C.soft);pill(s,"brand-logo-label","LOGO / ORIGINAL",92,192,165);text(s,"brand-logo-copy","保持原貌\n只进入固定角标",110,280,420,90,30,C.ink,true,FONT_TITLE,"center");
  panel(s,"brand-ip",650,170,500,300,C.pink,C.soft);pill(s,"brand-ip-label","IP / STYLE TRANSFER",672,192,195);text(s,"brand-ip-copy","先确认保留特征\n再做风格统一",690,280,420,90,30,C.ink,true,FONT_TITLE,"center");
}
// 12 Generated asset
{
  const s=deck.slides.add(); page(s,"C12 / GENERATED ASSET","出图资产页","非文字、非事实素材",12);
  text(s,"asset-main","出图不是自由发挥\n而是进入槽位",72,160,530,110,38,C.ink,true,FONT_TITLE);
  text(s,"asset-body","每张图先确认用途、比例、裁切和事实边界。",76,305,510,54,19,C.muted);
  [["A","原图输入",C.blue],["B","风格统一",C.pink],["C","抠图裁切",C.gold],["D","进入槽位",C.ink]].forEach(([n,t,a],i)=>{const x=650+(i%2)*260,y=165+Math.floor(i/2)*210;panel(s,`asset-${i}`,x,y,220,150,a);text(s,`asset-num-${i}`,n,x+22,y+24,45,38,27,a,true,FONT_NUM);text(s,`asset-title-${i}`,t,x+78,y+30,120,32,20,C.ink,true,FONT_TITLE);});
}
// 13 Card group: parallel peers only
{
  const s=deck.slides.add(); page(s,"C13 / CARD GROUP","并列卡片组","同字段 / 同权重 / 无方向",13);
  text(s,"card-group-sub","卡片只表达并列，不冒充流程、时间或层级。",72,132,660,32,20,C.muted);
  [["01","内容","页数和可见文字",C.blue],["02","形式","页面任务和变体",C.pink],["03","资产","截图、插图和数据",C.gold]].forEach(([n,t,b,a],i)=>addCard(s,`parallel-${i}`,100+i*390,220,300,300,n,t,b,a));
}

async function writeBlob(filePath, blob) { await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer())); }
await fs.mkdir(path.dirname(output), { recursive: true });
await fs.mkdir(qaDir, { recursive: true });
for (const [index, slide] of deck.slides.items.entries()) {
  const stem=`slide-${String(index+1).padStart(2,"0")}`;
  await writeBlob(path.join(qaDir,`${stem}.png`),await deck.export({slide,format:"png",scale:1}));
  const layout=await slide.export({format:"layout"}); await fs.writeFile(path.join(qaDir,`${stem}.layout.json`),await layout.text(),"utf8");
}
await writeBlob(path.join(qaDir,"montage.webp"),await deck.export({format:"webp",montage:true,scale:1}));
const pptx=await PresentationFile.exportPptx(deck); await pptx.save(output);
console.log(JSON.stringify({output,qaDir,slides:deck.slides.items.length},null,2));
