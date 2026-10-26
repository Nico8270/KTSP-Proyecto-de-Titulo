# Tesis k-TSP — lista para Overleaf (compila directo)

Esta carpeta es **autocontenida**: compila sin plantillas externas.

1. Overleaf → **New Project → Upload Project** → sube el `.zip` (o arrastra esta carpeta).
2. Marca **`tesis_ktsp.tex`** como documento principal.
3. **Recompile** (pdfLaTeX). Compila en 2 pasadas (la bibliografía va embebida,
   no necesita BibTeX).

## Contenido
- `tesis_ktsp.tex` — documento principal (3 capítulos, por compendio).
- `_bibliografia.tex` — bibliografía (50 referencias, numérica).
- `_tab_opsearch.tex`, `_tab_wilcoxon.tex` — tablas de resultados (protocolo Pandiri).
- `unab_logo.png`, `metodologia.png`, `Genotipo-Fenotipo.png` — imágenes del documento.
- `Fig1_gap_scenario.png`, `Fig2_boxplot_gap.png` — figuras de resultados.

Datos: 76 instancias TSPLIB, k = ⌊n/4⌋/⌊n/2⌋/⌊3n/4⌋, SR 0.05·n s / LR 0.2·n s,
10 corridas, BKS de LKH-3, comparación estadística (Wilcoxon) con GVNS/HH de
Pandiri & Singh (2020).
