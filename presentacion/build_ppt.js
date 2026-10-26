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
  s.addText("Proyecto de título · Nicolás Barrientos",
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
s.addText("Undergraduate thesis · k-TSP · Santiago de Chile, 2026",
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
 "Evaluate solution quality (relative GAP) against LKH-3 best-known values on the 76 TSPLIB instances of Pandiri & Singh × three values of k.",
 "Compare statistically (Wilcoxon signed-rank) against the published GVNS and hyper-heuristics of Pandiri & Singh.",
 "Release everything so every table and figure regenerates with a single command.",
],14);
foot(s);

// ============ 4 — WORK METHODOLOGY ============
s=p.addSlide(); bgLight(s); header(s,"3 · Methodology","Work Methodology");
const stages=[["a","Data design","Uniform ADTs for TSPLIB and synthetic instances; tour-based encoding of the k selected nodes."],
 ["b","Mathematical model","Single-tour, node-selection formulation with total-length objective and MTZ subtour elimination."],
 ["c","Heuristic resolution","Ten methods over a shared core of vectorized primitives (2-opt, in/out exchange, cheapest insertion)."],
 ["d","Experimental evaluation","76 TSPLIB instances × 3 values of k; short/long-run time limits (0.05n, 0.2n s), 10 runs, Wilcoxon test."]];
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

// ============ 6 — RESEARCH PROBLEM ============
s=p.addSlide(); bgLight(s); header(s,"4 · Research Problem","The k-TSP: Selection + Ordering");
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
s=p.addSlide(); bgLight(s); header(s,"6 · Benchmark","Benchmark and Protocol (Pandiri & Singh)");
bullets(s,0.6,1.7,6.6,[
 "76 standard TSPLIB instances (n from 14 to 783 cities).",
 "Each instance is tested at three values of k (fractions of its size n).",
 "Two wall-clock time limits: short run 0.05·n s and long run 0.2·n s; 10 runs each.",
 "76 instances × 3 values of k = 228 test cases, each compared to LKH-3.",
],15);
const quart=[["Small","k = ⌊n/4⌋","visit ~25% — selection dominates"],
 ["Medium","k = ⌊n/2⌋","visit ~50% — balanced"],
 ["Large","k = ⌊3n/4⌋","visit ~75% — close to an ordinary TSP"]];
let qy=1.85;
quart.forEach(q=>{
  s.addShape(p.ShapeType.roundRect,{x:7.5,y:qy,w:5.3,h:1.3,rectRadius:0.08,fill:{color:LIGHT}});
  s.addText(q[0],{x:7.7,y:qy+0.1,w:1.9,h:1.1,fontFace:TITLE_FONT,fontSize:20,bold:true,color:MAROON,valign:"middle",align:"center",margin:0});
  s.addText([{text:q[1],options:{fontFace:"Cambria",fontSize:15,italic:true,color:NAVY,breakLine:true}},
             {text:q[2],options:{fontFace:BODY_FONT,fontSize:11.5,color:DARK}}],
    {x:9.5,y:qy+0.1,w:3.2,h:1.1,valign:"middle",paraSpaceAfter:4,margin:0});
  qy+=1.45;
});
foot(s);

// ============ 9 — REFERENCE TABLE (GAP SUMMARY) ============
s=p.addSlide(); bgLight(s); header(s,"7 · Results","Mean GAP vs LKH-3, by Scenario");
s.addImage({path:"Fig1_gap_scenario.png",x:0.5,y:1.75,w:8.3,h:3.4});
bullets(s,9.0,1.9,3.9,[
 "Greedy and Tabu Search are the most robust of our methods.",
 "Both clearly beat the GVNS of Pandiri & Singh.",
 "GA improves for large k under the long run.",
 "Farthest Insertion is clearly the weakest.",
],13);
s.addText("Solid bars: our methods. Hatched bars (*): GVNS and hyper-heuristics of Pandiri & Singh (2020). Lower is better.",
 {x:0.6,y:5.4,w:8.2,h:0.5,fontFace:BODY_FONT,fontSize:11,italic:true,color:MUTED,margin:0});
foot(s);

// ============ 10 — COMPARISON WITH THE STATE OF THE ART ============
s=p.addSlide(); bgLight(s); header(s,"8 · Comparison","Comparison with the State of the Art");
const rankRows=[["HH_RAND*","6.2"],["HH_GREEDY*","7.3"],["Greedy","8.1"],["TS","8.8"],["SA","11.9"],
 ["GA","12.8"],["GRASP","13.6"],["GVNS*","16.2"],["DCIH","17.5"],["NI","18.3"],["NN","18.5"],["RI","25.3"],["FI","64.6"]];
const mine=new Set(["Greedy","TS"]);
const rr=[[{text:"Method",options:{bold:true,color:WHITE,fill:{color:NAVY},align:"left"}},
  {text:"Mean GAP%",options:{bold:true,color:WHITE,fill:{color:NAVY},align:"center"}}]];
rankRows.forEach((r,i)=>{ const hl=mine.has(r[0]); const fill=hl?"F3E1E4":(i%2?"FFFFFF":"F4F5F7");
  rr.push([{text:r[0],options:{bold:hl,color:hl?MAROON:DARK,fill:{color:fill},align:"left"}},
    {text:r[1],options:{bold:hl,color:hl?MAROON:DARK,fill:{color:fill},align:"center"}}]);});
s.addTable(rr,{x:0.6,y:1.75,w:5.0,colW:[3.3,1.7],rowH:0.33,fontFace:BODY_FONT,fontSize:12,
  border:{type:"solid",color:"D7DBE0",pt:0.5},valign:"middle"});
bullets(s,6.1,1.85,6.7,[
 "Global mean GAP over all 76 instances × 3 k × SR/LR. Lower is better.",
 "Our Greedy (8.1%) and Tabu Search (8.8%) rank just behind the two hyper-heuristics of Pandiri & Singh.",
 "Both clearly beat their GVNS (16.2%).",
 "Our best method matches or beats the best of Pandiri & Singh in 103 / 228 short-run cases, and HH_GREEDY in 123 / 228.",
],13.5);
s.addText("* Published results of Pandiri & Singh (2020) on the same benchmark.",
 {x:0.6,y:6.5,w:9,h:0.3,fontFace:BODY_FONT,fontSize:11,italic:true,color:MUTED,margin:0});
foot(s);

// ============ 10b — STATISTICAL SIGNIFICANCE (WILCOXON) ============
s=p.addSlide(); bgLight(s); header(s,"9 · Statistics","Statistical Significance (Wilcoxon)");
s.addImage({path:"Fig2_boxplot_gap.png",x:0.5,y:1.75,w:8.1,h:3.3});
bullets(s,8.8,1.9,4.1,[
 "Two-tailed Wilcoxon signed-rank test on the paired per-instance gaps.",
 "Greedy and Tabu Search are significantly better than GVNS (p < 0.05), SR and LR.",
 "In the short run, Greedy even beats HH_GREEDY; TS ties it.",
 "HH_RAND stays strongest, especially in the long run.",
],12.5);
s.addText("Distribution of the per-instance gap (long run), clipped at 80%. * = Pandiri & Singh.",
 {x:0.6,y:5.3,w:8.0,h:0.4,fontFace:BODY_FONT,fontSize:11,italic:true,color:MUTED,margin:0});
foot(s);

// ============ 11 — HEURISTICS 1/3 ============
s=p.addSlide(); bgLight(s); header(s,"10 · Methods (1/3)","Construction Heuristics");
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
s=p.addSlide(); bgLight(s); header(s,"11 · Methods (2/3)","Metaheuristics");
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
s=p.addSlide(); bgLight(s); header(s,"12 · Methods (3/3)","DCIH — the Proposed Heuristic");
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
s=p.addSlide(); bgLight(s); header(s,"13 · Results (1/2)","Overall Comparison");
const stt=[["≈8%","best avg GAP (ours)","Greedy & Tabu Search"],["< GVNS","significantly better","Wilcoxon, p < 0.05"],["76","TSPLIB instances","× 3 k · SR & LR"]];
let sx=0.7; stt.forEach(st=>{ s.addShape(p.ShapeType.roundRect,{x:sx,y:1.85,w:3.9,h:1.7,rectRadius:0.1,fill:{color:NAVY}});
  s.addText(st[0],{x:sx,y:2.0,w:3.9,h:0.8,align:"center",fontFace:TITLE_FONT,fontSize:34,bold:true,color:GOLD,margin:0});
  s.addText(st[1],{x:sx+0.2,y:2.8,w:3.5,h:0.5,align:"center",fontFace:BODY_FONT,fontSize:13,color:WHITE,margin:0});
  s.addText(st[2],{x:sx+0.2,y:3.2,w:3.5,h:0.3,align:"center",fontFace:BODY_FONT,fontSize:11,italic:true,color:"CADCFC",margin:0});
  sx+=4.2; });
bullets(s,0.7,3.95,12.0,[
 "Greedy cheapest-insertion is the most robust on average; Tabu Search is the best of our metaheuristics.",
 "Both are significantly better than the GVNS of Pandiri & Singh, and competitive with their hyper-heuristics.",
 "The genetic algorithm closes the gap for large k, especially under the long run.",
 "Farthest Insertion is the weakest; DCIH is a deterministic, reproducible alternative of comparable quality.",
],15);
foot(s);

// ============ 15 — RESULTS 2/2 (ANYTIME) ============
s=p.addSlide(); bgLight(s); header(s,"14 · Results (2/2)","Effect of the Time Budget (SR vs LR)");
const srlrRows=[["Greedy","8.5","7.8"],["TS","9.4","8.2"],["SA","12.0","11.7"],["GA","14.6","11.0"],
 ["GRASP","14.1","13.1"],["GVNS*","20.3","12.1"],["HH_RAND*","8.1","4.4"],["HH_GREEDY*","9.5","5.1"]];
const tb=[[{text:"Method",options:{bold:true,color:WHITE,fill:{color:NAVY},align:"left"}},
  {text:"SR (0.05n s)",options:{bold:true,color:WHITE,fill:{color:NAVY},align:"center"}},
  {text:"LR (0.2n s)",options:{bold:true,color:WHITE,fill:{color:NAVY},align:"center"}}]];
srlrRows.forEach((r,i)=>{ const fill=i%2?"FFFFFF":"F4F5F7";
  tb.push([{text:r[0],options:{color:DARK,fill:{color:fill},align:"left"}},
    {text:r[1],options:{color:DARK,fill:{color:fill},align:"center"}},
    {text:r[2],options:{color:MAROON,bold:true,fill:{color:fill},align:"center"}}]);});
s.addTable(tb,{x:0.6,y:1.8,w:6.1,colW:[2.5,1.8,1.8],rowH:0.36,fontFace:BODY_FONT,fontSize:12.5,
  border:{type:"solid",color:"D7DBE0",pt:0.5},valign:"middle"});
bullets(s,7.0,1.95,5.8,[
 "Mean GAP% averaged over the three k scenarios; lower is better.",
 "More time (LR) helps the time-driven methods; the deterministic ones (NN, NI, FI, DCIH) do not change.",
 "The genetic algorithm gains the most and becomes the best of our methods in the Large scenario under LR.",
 "Greedy and Tabu Search stay the most robust across both budgets.",
],13);
s.addText("* Published results of Pandiri & Singh (2020).",
 {x:0.6,y:6.4,w:9,h:0.3,fontFace:BODY_FONT,fontSize:11,italic:true,color:MUTED,margin:0});
foot(s);

// ============ 16 — CONCLUSIONS ============
s=p.addSlide(); s.background={color:NAVY};
s.addText("15 · CONCLUSIONS",{x:0.6,y:0.45,w:12,h:0.3,fontFace:BODY_FONT,fontSize:12,bold:true,color:GOLD,charSpacing:2,margin:0});
s.addText("Conclusions and Future Work",{x:0.6,y:0.72,w:12,h:0.8,fontFace:TITLE_FONT,fontSize:28,bold:true,color:WHITE,margin:0});
s.addText("Conclusions",{x:0.6,y:1.75,w:6,h:0.4,fontFace:BODY_FONT,fontSize:16,bold:true,color:GOLD,margin:0});
s.addText([
 {text:"Greedy and Tabu Search are the most robust; both beat GVNS significantly (Wilcoxon).",options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}},
 {text:"Competitive with the Pandiri & Singh hyper-heuristics on their own benchmark and protocol.",options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}},
 {text:"GA wins for large k; Farthest Insertion is the weakest for the k-TSP.",options:{bullet:{indent:14},breakLine:true,paraSpaceAfter:8}},
 {text:"DCIH: deterministic, reproducible, competitive quality.",options:{bullet:{indent:14}}},
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
s=p.addSlide(); bgLight(s); header(s,"16 · References","Selected References");
bullets(s,0.6,1.75,12.1,[
 "Pandiri & Singh (2020). Two multi-start heuristics for the k-TSP. OPSEARCH.",
 "Helsgaun (2017). LKH-3: extension of the Lin–Kernighan–Helsgaun TSP solver.",
 "Knox (1994). Tabu search performance on the symmetric TSP (Wilcoxon test). Computers & OR.",
 "Rosenkrantz, Stearns & Lewis (1977). An analysis of several heuristics for the TSP. SIAM J. Computing.",
 "Feo & Resende (1995). GRASP. J. of Global Optimization.",
 "Kirkpatrick, Gelatt & Vecchi (1983). Optimization by simulated annealing. Science.",
 "Glover (1986); Glover & Laguna (1997). Tabu Search.",
 "Full bibliography (50 references) in the thesis and paper.",
],13.5);
foot(s);

p.writeFile({ fileName:"presentacion_ktsp.pptx" }).then(f=>console.log("OK:",f));
