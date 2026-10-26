# Paper k-TSP v15.0 — versión final (OPSEARCH / Springer Nature)

Archivo principal: **`resumen_k_tsp_15.0.tex`** (documento único, autocontenido:
incluye el cuerpo, las tablas y las declaraciones; solo depende de la bibliografía
y las figuras).

Contenido de la carpeta:
- `resumen_k_tsp_15.0.tex` — documento principal (Springer Nature `sn-jnl`, citas autor-año `sn-chicago`).
- `sn-bibliography.bib` — 50 referencias (BibTeX).
- `figs/` — Fig1 (GAP por escenario), Fig2 (boxplot) y esquemas conceptuales.

## Compilar en Overleaf
1. **New Project → Templates** → busca **"Springer Nature LaTeX Template"** y crea el
   proyecto (trae `sn-jnl.cls` y los estilos de bibliografía).
2. Sube a ese proyecto `resumen_k_tsp_15.0.tex`, `sn-bibliography.bib` y la carpeta `figs/`.
3. Marca `resumen_k_tsp_15.0.tex` como documento principal → **Recompile** (pdfLaTeX).

> Citas en autor-año (`sn-chicago`). Si OPSEARCH pide APA estricto, cambia
> `sn-chicago` por `sn-apa` en la primera línea de `\documentclass`.

## Qué incluye esta versión (todas las modificaciones actuales)
- Protocolo de Pandiri & Singh: 76 instancias TSPLIB, k = ⌊n/4⌋/⌊n/2⌋/⌊3n/4⌋,
  short run 0.05·n s / long run 0.2·n s, 10 corridas.
- Referencia LKH-3 (BKS) y comparación con GVNS/HH_RAND/HH_GREEDY de Pandiri & Singh.
- Tabla de GAP medio (Tabla 1), test de Wilcoxon (Tabla 2), Fig1 y Fig2.
- Diez métodos (Greedy, GRASP, GA, NN, NI, FI, RI, SA, TS, DCIH) + algoritmo DCIH.
- Abstract (150–250 palabras), keywords y "Statements and Declarations".
