const pptxgen = require("pptxgenjs");
const fs = require("fs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";
const W = 13.33, H = 7.5;
const NAVY="1F2A44", MAROON="9B1B30", LIGHT="F4F5F7", DARK="20242E",
      MUTED="5B6472", WHITE="FFFFFF", GOLD="C9A227";
const TITLE_FONT="Cambria", BODY_FONT="Calibri";

// ---- italic variables: split a string into runs, italicizing math variables ----
// italicize: standalone k,n,F,T ; the k in "k-TSP" ; and n^2 / (n2)
function vruns(str, base){
  base = base || {};
  // tokens to italicize when matched
  const re = /(k-TSP|C\(n-1,\s*k-1\)|\(k-1\)!\/2|3n\/4|n\/4|n\/2|n\^2|n2|Δ|\bk\b|\bn\b|\bF\b|\bT\b)/g;
  const out = []; let last = 0, m;
  while ((m = re.exec(str)) !== null){
    if (m.index > last) out.push(Object.assign({text: str.slice(last, m.index)}, base));
    const tok = m[0];
    if (tok === "k-TSP"){
      out.push(Object.assign({text:"k", options:{italic:true}}, {}, {text:"k"}, base, {italic:true}));
      out.push(Object.assign({text:"-TSP"}, base));
    } else {
      out.push(Object.assign({}, base, {text: tok, italic: true}));
    }
    last = m.index + tok.length;
  }
  if (last < str.length) out.push(Object.assign({text: str.slice(last)}, base));
  // normalize: ensure each run has italic flag from base unless set
  return out.map(r => ({ text: r.text, italic: r.italic===true, bold: base.bold===true, color: base.color, breakLine: base.breakLine, options: r.options }));
}

// header/footer/pagenum
let PAGE = 0;
function foot(s){
  PAGE++;
  s.addText("Nicolás Barrientos · k-TSP · Universidad Andrés Bello · 2026",
    {x:0.5,y:H-0.42,w:10.5,h:0.3,fontFace:BODY_FONT,fontSize:9,color:MUTED,margin:0});
  s.addText(String(PAGE),{x:W-0.9,y:H-0.42,w:0.5,h:0.3,fontFace:BODY_FONT,fontSize:10,color:MUTED,align:"right",margin:0});
}
function bgLight(s){ s.background = { color: WHITE }; }
function header(s,kicker,title){
  s.addText(kicker.toUpperCase(),{x:0.6,y:0.4,w:12,h:0.3,fontFace:BODY_FONT,fontSize:12,color:MAROON,bold:true,charSpacing:2,margin:0});
  const t = vruns(title,{fontFace:TITLE_FONT,fontSize:28,color:NAVY,bold:true});
  s.addText(t.map(r=>({text:r.text,options:{fontFace:TITLE_FONT,fontSize:28,color:NAVY,bold:true,italic:r.italic}})),
    {x:0.6,y:0.66,w:12.1,h:0.8,margin:0});
}
// rich bullets with italic variables
function bullets(s,x,y,w,lines,fsz){
  const fs2=fsz||15; const runs=[];
  lines.forEach(line=>{
    const parts=vruns(line,{});
    parts.forEach((pr,i)=>{
      const opt={fontFace:BODY_FONT,fontSize:fs2,color:DARK,italic:pr.italic};
      if(i===0) opt.bullet={indent:14};
      if(i===parts.length-1){opt.breakLine=true;opt.paraSpaceAfter=8;}
      runs.push({text:pr.text,options:opt});
    });
  });
  s.addText(runs,{x,y,w,h:H-y-0.9,valign:"top",margin:0});
}
function chip(s,x,y,txt,fill){
  s.addShape(p.ShapeType.ellipse,{x,y,w:0.42,h:0.42,fill:{color:fill||MAROON}});
  s.addText(txt,{x,y,w:0.42,h:0.42,align:"center",valign:"middle",fontFace:BODY_FONT,fontSize:14,bold:true,color:WHITE,margin:0});
}

// ============ 1 — COVER ============
let s=p.addSlide(); s.background={color:NAVY};
s.addImage({path:"unab_logo.png",x:0.7,y:0.6,w:1.7,h:1.43});
s.addText("Faculty of Engineering  ·  Computer Engineering (Ingeniería Civil Informática)",
  {x:0.75,y:2.25,w:11.8,h:0.4,fontFace:BODY_FONT,fontSize:14,color:"CADCFC",margin:0});
s.addText([{text:"Heuristic Approaches for the\n",options:{}},
  {text:"k",options:{italic:true}},{text:"-Traveling Salesman Problem",options:{}}],
  {x:0.75,y:2.75,w:11.8,h:1.7,fontFace:TITLE_FONT,fontSize:40,bold:true,color:WHITE,margin:0});
s.addText("A Reproducible Comparison of Ten Methods",
  {x:0.75,y:4.45,w:11.8,h:0.5,fontFace:BODY_FONT,fontSize:20,italic:true,color:GOLD,margin:0});
s.addText([{text:"Author:  ",options:{bold:true,color:"CADCFC"}},{text:"Nicolás Barrientos",options:{color:WHITE,breakLine:true}},
  {text:"Advisor:  ",options:{bold:true,color:"CADCFC"}},{text:"Dr. Gustavo Gatica",options:{color:WHITE}}],
  {x:0.75,y:5.5,w:8,h:0.9,fontFace:BODY_FONT,fontSize:16,margin:0,valign:"top",paraSpaceAfter:4});
s.addText("Undergraduate thesis · Paper submitted to Optima 2025 · Santiago de Chile, 2026",
  {x:0.75,y:6.75,w:11.8,h:0.4,fontFace:BODY_FONT,fontSize:12,color:"9FB0CC",margin:0});
PAGE=1;

// ============ 2 — CONTEXT ============
s=p.addSlide(); bgLight(s); header(s,"1 · Context","Context and Motivation");
bullets(s,0.6,1.7,7.1,[
 "Route optimization drives logistics, transportation, surveillance and resource planning.",
 "The Traveling Salesman Problem (TSP) is the canonical model: a minimum-length closed tour visiting every city.",
 "Many real tasks visit only a SUBSET of sites under a budget on the number of stops.",
 "That is the k-TSP: choose k of n cities (with a depot) and order them into one minimum-length closed tour.",
 "Applications: selective sampling, prize-collecting routing, limited-visit surveillance, resource-constrained logistics.",
],15);
s.addImage({path:"ktsp_plot.png",x:8.0,y:1.9,w:4.7,h:3.9});
s.addText("A k-TSP tour: only the selected k nodes form the loop.",{x:8.0,y:5.8,w:4.7,h:0.4,fontFace:BODY_FONT,fontSize:11,italic:true,color:MUTED,align:"center",margin:0});
foot(s);

// ============ 3 — OBJECTIVES ============
s=p.addSlide(); bgLight(s); header(s,"2 · Objectives","General and Specific Objectives");
s.addShape(p.ShapeType.roundRect,{x:0.6,y:1.7,w:12.1,h:1.1,rectRadius:0.08,fill:{color:LIGHT}});
s.addText([{text:"General objective.  ",options:{bold:true,color:MAROON}},
 {text:"Develop a reproducible repository that models, solves and compares k-TSP instances on standard TSPLIB and synthetic benchmarks, evaluating heuristics and metaheuristics against LKH-3 best-known values.",options:{color:DARK}}],
 {x:0.85,y:1.82,w:11.6,h:0.9,fontFace:BODY_FONT,fontSize:14.5,valign:"middle",margin:0});
s.addText("Specific objectives",{x:0.6,y:3.0,w:12,h:0.4,fontFace:BODY_FONT,fontSize:16,bold:true,color:NAVY,margin:0});
bullets(s,0.6,3.45,12.1,[
 "Formulate the k-TSP mathematically (node selection, degree and subtour-elimination constraints).",
 "Implement ten techniques: Greedy, GRASP, GA, Nearest Neighbor, Nearest / Farthest / Random Insertion, Simulated Annealing, Tabu Search, and the proposed DCIH.",
 "Evaluate solution quality (relative GAP) against LKH-3 best-known values on 38 TSPLIB instances × three values of k.",
 "Complement with anytime benchmarking (progress, ERT, ECDF, global ranking) on a machine-independent time axis.",
 "Release everything so every table and figure regenerates with a single command.",
],14);
foot(s);

// ============ 4 — WORK METHODOLOGY ============
s=p.addSlide(); bgLight(s); header(s,"3 · Methodology","Work Methodology");
const stages=[["a","Data design","Uniform ADTs for TSPLIB and synthetic instances; tour-based encoding of the k selected nodes."],
 ["b","Mathematical model","Single-tour, node-selection formulation with total-length objective and MTZ subtour elimination."],
 ["c","Heuristic resolution","Ten methods over a shared core of vectorized primitives (2-opt, in/out exchange, cheapest insertion)."],
 ["d","Experimental evaluation","38 TSPLIB instances × 3 values of k; full trajectory logged for the anytime analysis."]];
let yy=1.8;
stages.forEach(st=>{ chip(s,0.7,yy,st[0],NAVY);
  s.addText(st[1],{x:1.35,y:yy-0.03,w:4.0,h:0.5,fontFace:BODY_FONT,fontSize:15,bold:true,color:MAROON,margin:0});
  const parts=vruns(st[2],{});
  s.addText(parts.map(r=>({text:r.text,options:{fontFace:BODY_FONT,fontSize:13.5,color:DARK,italic:r.italic}})),
    {x:5.4,y:yy-0.05,w:7.3,h:0.7,valign:"top",margin:0});
  yy+=1.05; });
s.addShape(p.ShapeType.roundRect,{x:0.6,y:6.15,w:12.1,h:0.75,rectRadius:0.08,fill:{color:NAVY}});
s.addText([{text:"Tools & reproducibility:  ",options:{bold:true,color:GOLD}},
 {text:"Python 3.10 (numpy, pandas, matplotlib), Visual Studio Code, private GitHub repository, LKH-3 compiled locally; machine-independent distance-evaluation metric.",options:{color:WHITE}}],
 {x:0.85,y:6.22,w:11.6,h:0.6,fontFace:BODY_FONT,fontSize:12.5,valign:"middle",margin:0});
foot(s);

// ============ 5 — CONFERENCE ============
s=p.addSlide(); bgLight(s); header(s,"4 · Dissemination","Conference Submission — Optima 2025");
s.addShape(p.ShapeType.roundRect,{x:0.6,y:2.0,w:5.9,h:4.2,rectRadius:0.1,fill:{color:LIGHT}});
s.addText("OPTIMA 2025",{x:0.9,y:2.4,w:5.3,h:0.7,fontFace:TITLE_FONT,fontSize:34,bold:true,color:MAROON,margin:0});
s.addText([{text:"Venue:  ",options:{bold:true}},{text:"Universidad Católica del Norte, Chile",options:{breakLine:true}},
 {text:"Submitted:  ",options:{bold:true}},{text:"November 30, 2025",options:{breakLine:true}},
 {text:"Status:  ",options:{bold:true}},{text:"Under review (submitted)",options:{}}],
 {x:0.9,y:3.3,w:5.3,h:2.6,fontFace:BODY_FONT,fontSize:17,color:DARK,valign:"top",paraSpaceAfter:12,margin:0});
bullets(s,6.9,2.1,5.9,[
 "The core of this thesis was written up as a scientific paper and submitted to Optima 2025.",
 "The paper condenses the mathematical model, the ten solution techniques and the experimental comparison.",
 "It constitutes the main scientific contribution and is reproduced as a chapter of the thesis.",
],15.5);
foot(s);

// ============ 6 — RESEARCH PROBLEM ============
s=p.addSlide(); bgLight(s); header(s,"5 · Research Problem","The k-TSP: Selection + Ordering");
bullets(s,0.6,1.7,7.0,[
 "Given n cities with a depot and a fixed k (1 < k ≤ n), find one closed tour of minimum length visiting exactly k cities.",
 "Two coupled decisions: WHICH k nodes to visit and IN WHICH ORDER.",
 "Candidate subsets: C(n-1, k-1), each with (k-1)!/2 tours → exhaustive search is intractable.",
 "It is the unit-prize Quota TSP, within the TSP-with-profits / selective-routing family.",
 "Reference (near-optimal): LKH-3 best-known values (BKS).",
],15);
s.addImage({path:"Genotipo-Fenotipo.png",x:8.05,y:2.0,w:4.6,h:3.5});
s.addText("Genotype → phenotype: selected subset + order map to one closed loop.",{x:8.05,y:5.6,w:4.6,h:0.5,fontFace:BODY_FONT,fontSize:11,italic:true,color:MUTED,align:"center",margin:0});
foot(s);

// ============ 7 — MATHEMATICAL MODEL (NEW) ============
s=p.addSlide(); bgLight(s); header(s,"5 · Model","Mathematical Model of the k-TSP");
s.addText([{text:"Variables:  ",options:{bold:true,color:MAROON}},
 {text:"x",options:{italic:true}},{text:"ᵢⱼ = 1 if arc (",options:{}},{text:"i,j",options:{italic:true}},{text:") is in the tour;   ",options:{}},
 {text:"y",options:{italic:true}},{text:"ᵢ = 1 if node ",options:{}},{text:"i",options:{italic:true}},{text:" is selected;   ",options:{}},
 {text:"u",options:{italic:true}},{text:"ᵢ = MTZ ordering variables.",options:{}}],
 {x:0.6,y:1.75,w:12.1,h:0.5,fontFace:BODY_FONT,fontSize:15,color:DARK,margin:0});
const eqs=[
 ["min",  "Σ Σ dᵢⱼ · xᵢⱼ", "(objective) minimize total tour length"],
 ["s.t.", "y₀ = 1", "the depot is always selected"],
 ["",     "Σ yᵢ = k", "exactly k nodes are visited"],
 ["",     "Σⱼ xᵢⱼ = yᵢ  ,  Σⱼ xⱼᵢ = yᵢ    ∀ i", "degree: one in / one out iff selected"],
 ["",     "uᵢ − uⱼ + k · xᵢⱼ ≤ k − 1    ∀ i,j ≠ 0", "MTZ: eliminate subtours"],
 ["",     "xᵢⱼ , yᵢ ∈ {0,1} ,  uᵢ ∈ ℝ", "domain of the variables"],
];
let ey=2.45;
eqs.forEach(e=>{
  s.addShape(p.ShapeType.roundRect,{x:0.6,y:ey,w:12.1,h:0.62,rectRadius:0.05,fill:{color:LIGHT}});
  s.addText(e[0],{x:0.75,y:ey,w:0.8,h:0.62,fontFace:BODY_FONT,fontSize:13,italic:true,color:MAROON,valign:"middle",margin:0});
  s.addText(e[1],{x:1.6,y:ey,w:6.6,h:0.62,fontFace:"Cambria",fontSize:16,italic:true,color:NAVY,valign:"middle",margin:0});
  s.addText(e[2],{x:8.3,y:ey,w:4.3,h:0.62,fontFace:BODY_FONT,fontSize:11.5,color:MUTED,valign:"middle",margin:0});
  ey+=0.72;
});
foot(s);

// ============ 8 — INSTANCES & QUARTILES (NEW) ============
s=p.addSlide(); bgLight(s); header(s,"6 · Benchmark","Instances and Quartiles of k");
bullets(s,0.6,1.7,6.6,[
 "38 standard TSPLIB instances (n from 48 to 442 cities).",
 "Each instance is tested at three values of k, as quartiles of its size n.",
 "This shows how the methods behave as we visit few or many cities.",
 "38 instances × 3 quartiles = 114 test cases, each compared to LKH-3.",
],15.5);
const quart=[["Q1","k = ⌊n/4⌋","visit ~25% of cities","selection dominates"],
 ["Q2","k = ⌊n/2⌋","visit ~50% of cities","balanced"],
 ["Q3","k = ⌊3n/4⌋","visit ~75% of cities","close to an ordinary TSP"]];
let qy=1.8;
quart.forEach(q=>{
  s.addShape(p.ShapeType.roundRect,{x:7.5,y:qy,w:5.3,h:1.35,rectRadius:0.08,fill:{color:LIGHT}});
  s.addText(q[0],{x:7.7,y:qy+0.1,w:1.0,h:1.1,fontFace:TITLE_FONT,fontSize:30,bold:true,color:MAROON,valign:"middle",align:"center",margin:0});
  s.addText([{text:q[1],options:{fontFace:"Cambria",fontSize:16,italic:true,color:NAVY,breakLine:true}},
             {text:q[2]+" — "+q[3],options:{fontFace:BODY_FONT,fontSize:12,color:DARK}}],
    {x:8.8,y:qy+0.1,w:3.9,h:1.15,valign:"middle",paraSpaceAfter:4,margin:0});
  qy+=1.5;
});
foot(s);

// ============ 9 — REFERENCE TABLE (GAP SUMMARY) ============
s=p.addSlide(); bgLight(s); header(s,"7 · Overview","Reference Result: Average GAP vs LKH-3");
const gap=[["Greedy","7.57","15.26","14.95"],["GRASP","18.03","19.57","17.39"],["GA","29.74","22.50","15.60"],
 ["NN","22.38","20.04","15.56"],["NI","20.47","21.74","21.66"],["FI","98.23","55.67","31.63"],
 ["RI","48.74","28.18","16.11"],["SA","15.72","17.81","17.89"],["TS","9.36","13.63","14.48"],["DCIH","19.83","23.19","20.36"]];
const best=new Set(["Greedy","TS"]);
const rows=[[
  {text:"Method",options:{bold:true,color:WHITE,fill:{color:NAVY},align:"left"}},
  {text:"Q1 GAP%",options:{bold:true,color:WHITE,fill:{color:NAVY},align:"center"}},
  {text:"Q2 GAP%",options:{bold:true,color:WHITE,fill:{color:NAVY},align:"center"}},
  {text:"Q3 GAP%",options:{bold:true,color:WHITE,fill:{color:NAVY},align:"center"}}]];
gap.forEach((r,i)=>{ const hl=best.has(r[0]); const fill=hl?"F3E1E4":(i%2?"FFFFFF":"F4F5F7");
  rows.push([{text:r[0],options:{bold:hl,color:hl?MAROON:DARK,fill:{color:fill},align:"left"}},
    {text:r[1],options:{color:DARK,fill:{color:fill},align:"center"}},
    {text:r[2],options:{color:DARK,fill:{color:fill},align:"center"}},
    {text:r[3],options:{color:DARK,fill:{color:fill},align:"center"}}]);});
s.addTable(rows,{x:0.6,y:1.75,w:7.4,colW:[2.6,1.6,1.6,1.6],rowH:0.36,fontFace:BODY_FONT,fontSize:12.5,
  border:{type:"solid",color:"D7DBE0",pt:0.5},valign:"middle"});
bullets(s,8.4,1.9,4.4,[
 "38 instances × three values of k, vs LKH-3 BKS.",
 "Greedy and Tabu Search give the lowest average GAP.",
 "GA improves for large k (Q3).",
 "Farthest Insertion is clearly the weakest.",
],14);
s.addText([{text:"Q1: ",options:{}},{text:"k",options:{italic:true}},{text:"≈",options:{}},{text:"n",options:{italic:true}},{text:"/4    Q2: ",options:{}},{text:"k",options:{italic:true}},{text:"≈",options:{}},{text:"n",options:{italic:true}},{text:"/2    Q3: ",options:{}},{text:"k",options:{italic:true}},{text:"≈3",options:{}},{text:"n",options:{italic:true}},{text:"/4   ·   lower is better",options:{}}],
 {x:0.6,y:6.35,w:7.6,h:0.35,fontFace:BODY_FONT,fontSize:11,italic:false,color:MUTED,margin:0});
foot(s);

// ============ 10 — COMPLETE TABLE (Q2, split in two slides) (NEW) ============
const q2all=JSON.parse(fs.readFileSync("_q2_rows.json","utf8"));
const head=["Inst.","n","k","Grd","GRA","GA","NN","NI","FI","RI","SA","TS","DCIH","LKH-3"];
function tableSlide(part, subtitle){
  const sl=p.addSlide(); bgLight(sl); header(sl,"7 · Full results","Complete Results — per instance (Q2) "+subtitle);
  const tr=[head.map(h=>({text:h,options:{bold:true,color:WHITE,fill:{color:NAVY},align:"center"}}))];
  part.forEach((r,i)=>{ const bks=r[r.length-1]; const fill=i%2?"FFFFFF":"F4F5F7";
    tr.push(r.map((c,ci)=>{ const isB=ci>=3&&ci<r.length-1&&c===bks;
      return {text:c,options:{color:isB?MAROON:DARK,bold:isB,fill:{color:fill},align:ci===0?"left":"center"}};}));});
  sl.addTable(tr,{x:0.35,y:1.6,w:12.6,rowH:0.24,fontFace:BODY_FONT,fontSize:9.5,
    border:{type:"solid",color:"E1E4E8",pt:0.4},valign:"middle",autoPage:false,
    colW:[0.95,0.5,0.5,1.02,1.02,1.02,1.02,1.02,1.02,1.02,1.02,1.02,1.05,1.1]});
  sl.addText("Total tour length per method for Q2 (k ≈ n/2). Bold = matches the LKH-3 best-known value. Full Q1/Q3 tables in the thesis.",
   {x:0.35,y:H-0.62,w:12.4,h:0.28,fontFace:BODY_FONT,fontSize:9,italic:true,color:MUTED,margin:0});
  foot(sl);
}
tableSlide(q2all.slice(0,19), "— part 1/2");
tableSlide(q2all.slice(19),  "— part 2/2");

// ============ 11 — HEURISTICS 1/3 ============
s=p.addSlide(); bgLight(s); header(s,"8 · Methods (1/3)","Construction Heuristics");
const cons=[["Greedy (cheapest insertion)","Insert the node of smallest marginal cost until k; 2-opt refinement; deterministic restarts."],
 ["Nearest Neighbor (NN)","Extend the tour to the nearest unvisited node until k; then local search."],
 ["Nearest / Farthest Insertion","Insert the node closest to (NI) or farthest from (FI) the tour at its cheapest position."],
 ["Random Insertion (RI)","Multi-start insertion with the next node chosen at random; local search each restart."]];
let y8=1.85;
cons.forEach(c=>{ s.addShape(p.ShapeType.roundRect,{x:0.6,y:y8,w:12.1,h:1.0,rectRadius:0.07,fill:{color:LIGHT}});
  s.addText(c[0],{x:0.85,y:y8+0.1,w:4.4,h:0.8,fontFace:BODY_FONT,fontSize:15,bold:true,color:MAROON,valign:"middle",margin:0});
  const parts=vruns(c[1],{});
  s.addText(parts.map(r=>({text:r.text,options:{fontFace:BODY_FONT,fontSize:13.5,color:DARK,italic:r.italic}})),
    {x:5.35,y:y8+0.1,w:7.15,h:0.8,valign:"middle",margin:0});
  y8+=1.15; });
s.addText("All share a common core: 2-opt, in/out exchange and cheapest insertion → a fair comparison.",
 {x:0.6,y:6.45,w:12,h:0.35,fontFace:BODY_FONT,fontSize:12,italic:true,color:MUTED,margin:0});
foot(s);

// ============ 12 — HEURISTICS 2/3 ============
s=p.addSlide(); bgLight(s); header(s,"9 · Methods (2/3)","Metaheuristics");
const meta=[["GRASP / multi-start","Randomized greedy construction + local search; best over many restarts."],
 ["Genetic Algorithm (GA)","Encodes subset + order; tournament, subset-aware crossover, mutation, elitism, 2-opt."],
 ["Simulated Annealing (SA)","Accepts worsening moves with probability exp(−Δ/T); geometric cooling escapes local optima."],
 ["Tabu Search (TS)","Best non-tabu move each step; tabu list with tenure and aspiration criterion (memory-guided)."]];
let y9=1.85;
meta.forEach(c=>{ s.addShape(p.ShapeType.roundRect,{x:0.6,y:y9,w:12.1,h:1.0,rectRadius:0.07,fill:{color:LIGHT}});
  s.addText(c[0],{x:0.85,y:y9+0.1,w:4.4,h:0.8,fontFace:BODY_FONT,fontSize:15,bold:true,color:MAROON,valign:"middle",margin:0});
  s.addText(c[1],{x:5.35,y:y9+0.1,w:7.15,h:0.8,fontFace:BODY_FONT,fontSize:13.5,color:DARK,valign:"middle",margin:0});
  y9+=1.15; });
s.addText("Tabu Search is the best of the metaheuristics in average GAP.",
 {x:0.6,y:6.45,w:12,h:0.35,fontFace:BODY_FONT,fontSize:12,italic:true,color:MUTED,margin:0});
foot(s);

// ============ 13 — HEURISTICS 3/3 (DCIH) ============
s=p.addSlide(); bgLight(s); header(s,"10 · Methods (3/3)","DCIH — the Proposed Heuristic");
s.addShape(p.ShapeType.roundRect,{x:0.6,y:1.75,w:6.0,h:4.5,rectRadius:0.1,fill:{color:LIGHT}});
s.addText("Deterministic Cheapest-Insertion Heuristic",{x:0.85,y:1.95,w:5.5,h:0.7,fontFace:BODY_FONT,fontSize:16,bold:true,color:MAROON,margin:0});
s.addText([{text:"Phase 1 — Selection + ordering:  ",options:{bold:true,breakLine:true}},
 {text:"pick the k nodes and positions by minimum marginal insertion cost, ties broken by node index.",options:{breakLine:true}},
 {text:"Phase 2 — Refinement:  ",options:{bold:true,breakLine:true}},
 {text:"iterate 2-opt and an in/out exchange until no improvement.",options:{}}],
 {x:0.85,y:2.6,w:5.5,h:2.4,fontFace:BODY_FONT,fontSize:14,color:DARK,valign:"top",paraSpaceAfter:8,margin:0});
s.addText("Same data ⇒ exactly the same tour: fully reproducible, no random seed.",
 {x:0.85,y:5.45,w:5.5,h:0.7,fontFace:BODY_FONT,fontSize:13,italic:true,color:NAVY,margin:0});
bullets(s,7.0,1.95,5.8,[
 "Attacks both k-TSP decisions with a single criterion: marginal insertion cost.",
 "Differs from Greedy: one deterministic construction (ties by index) + iterated 2-opt & in/out exchange.",
 "Prioritizes correctness and reproducibility over winning by chance.",
 "Quality comparable to GRASP and the insertion heuristics.",
],15);
foot(s);

// ============ 14 — RESULTS 1/2 ============
s=p.addSlide(); bgLight(s); header(s,"11 · Results (1/2)","End-of-Run Comparison");
const stt=[["≈12.5%","best avg GAP","Greedy & Tabu Search"],["1st","most frequent\nwinner (large k)","Genetic Algorithm"],["10","methods compared","vs LKH-3 BKS"]];
let sx=0.7; stt.forEach(st=>{ s.addShape(p.ShapeType.roundRect,{x:sx,y:1.85,w:3.9,h:1.7,rectRadius:0.1,fill:{color:NAVY}});
  s.addText(st[0],{x:sx,y:2.0,w:3.9,h:0.8,align:"center",fontFace:TITLE_FONT,fontSize:34,bold:true,color:GOLD,margin:0});
  s.addText(st[1],{x:sx+0.2,y:2.8,w:3.5,h:0.5,align:"center",fontFace:BODY_FONT,fontSize:13,color:WHITE,margin:0});
  s.addText(st[2],{x:sx+0.2,y:3.2,w:3.5,h:0.3,align:"center",fontFace:BODY_FONT,fontSize:11,italic:true,color:"CADCFC",margin:0});
  sx+=4.2; });
bullets(s,0.7,3.95,12.0,[
 "Greedy cheapest-insertion is the most robust on average; Tabu Search essentially ties it as best metaheuristic.",
 "The genetic algorithm closes the gap for large k (Q3) and wins on many individual instances.",
 "Farthest Insertion is the weakest: selecting distant nodes conflicts with the node-selection objective.",
 "DCIH is a deterministic, reproducible alternative of comparable quality.",
],15);
foot(s);

// ============ 15 — RESULTS 2/2 (ANYTIME) ============
s=p.addSlide(); bgLight(s); header(s,"12 · Results (2/2)","Anytime Evaluation (Weise et al.)");
s.addImage({path:"01_progreso_agregado.png",x:0.55,y:1.8,w:7.4,h:4.6});
bullets(s,8.15,1.95,4.7,[
 "Machine-independent time = distance evaluations (scaled by n²).",
 "All methods over a common budget; early-converging methods appear flat.",
 "Global ranking (4 criteria): NN 1st, Greedy 2nd, TS 3rd, SA 4th, DCIH 5th.",
 "NN is fastest to a good tour but only mid-ranked in final quality — speed ≠ best.",
],14.5);
foot(s);

// ============ 16 — CONCLUSIONS ============
s=p.addSlide(); s.background={color:NAVY};
s.addText("13 · CONCLUSIONS",{x:0.6,y:0.45,w:12,h:0.3,fontFace:BODY_FONT,fontSize:12,bold:true,color:GOLD,charSpacing:2,margin:0});
s.addText("Conclusions and Future Work",{x:0.6,y:0.72,w:12,h:0.8,fontFace:TITLE_FONT,fontSize:28,bold:true,color:WHITE,margin:0});
s.addText("Conclusions",{x:0.6,y:1.75,w:6,h:0.4,fontFace:BODY_FONT,fontSize:16,bold:true,color:GOLD,margin:0});
s.addText([
 {text:"Greedy and Tabu Search are the most robust; TS is the best metaheuristic.",options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}},
 {text:"GA wins for large k; Farthest Insertion is the weakest for the k-TSP.",options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}},
 {text:"DCIH: deterministic, reproducible, competitive quality.",options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}},
 {text:"Anytime view separates 'fast' (NN) from 'best' (Greedy/TS).",options:{bullet:{indent:14}}},
],{x:0.6,y:2.2,w:6.1,h:3.9,fontFace:BODY_FONT,fontSize:15,color:WHITE,valign:"top",margin:0});
s.addText("Future work",{x:7.0,y:1.75,w:6,h:0.4,fontFace:BODY_FONT,fontSize:16,bold:true,color:GOLD,margin:0});
s.addText([
 {text:"Stronger / hybrid metaheuristics (ACO, VNS, memetic TS+GA).",options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}},
 {text:"Per-instance parameter tuning (tenure, cooling, population).",options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}},
 {text:"Dedicated node-selection rules beyond insertion cost.",options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}},
 {text:"Larger instances and related selective-routing problems.",options:{bullet:{indent:14}}},
],{x:7.0,y:2.2,w:5.7,h:3.9,fontFace:BODY_FONT,fontSize:15,color:WHITE,valign:"top",margin:0});
foot(s);

// ============ 17 — REFERENCES ============
s=p.addSlide(); bgLight(s); header(s,"14 · References","Selected References");
bullets(s,0.6,1.75,12.1,[
 "Pandiri & Singh (2020). The k-TSP benchmark. OPSEARCH.",
 "Helsgaun (2017). LKH-3: extension of the Lin–Kernighan–Helsgaun TSP solver.",
 "Weise et al. (2014). Benchmarking optimization algorithms: an open-source framework for the TSP. IEEE CIM.",
 "Rosenkrantz, Stearns & Lewis (1977). An analysis of several heuristics for the TSP. SIAM J. Computing.",
 "Feo & Resende (1995). GRASP. J. of Global Optimization.",
 "Kirkpatrick, Gelatt & Vecchi (1983). Optimization by simulated annealing. Science.",
 "Glover (1986); Glover & Laguna (1997). Tabu Search.",
 "Full bibliography (50 references) in the thesis and paper.",
],13.5);
foot(s);

p.writeFile({ fileName:"presentacion_ktsp.pptx" }).then(f=>console.log("OK:",f));
