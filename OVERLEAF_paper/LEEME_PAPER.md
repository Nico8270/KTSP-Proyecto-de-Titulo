# Paper k-TSP (OPSEARCH) — listo para Overleaf

Dos formas de usarlo:

## A) Vista previa rápida (compila al instante)
1. Overleaf → **New Project → Upload Project** → sube el `.zip` (o arrastra esta carpeta).
2. Marca **`main_preview.tex`** como documento principal.
3. **Recompile** (pdfLaTeX). Compila sin necesitar la plantilla Springer.
   Sirve para leer y revisar el contenido.

## B) Versión de ENVÍO a OPSEARCH (formato Springer)
1. Overleaf → **New Project → Templates** → busca **"Springer Nature LaTeX Template"**
   y crea el proyecto (trae `sn-jnl.cls` y los estilos de bibliografía).
2. Sube a ese proyecto: `sn-article.tex`, `body.tex`, `sn-bibliography.bib`,
   `tab_comparacion_global.tex`, `tab_wilcoxon.tex` y la carpeta `figs/`.
3. Marca **`sn-article.tex`** como documento principal → **Recompile** (pdfLaTeX).

> Estilo de citas: autor-año (`sn-chicago`). Si OPSEARCH pide APA estricto,
> cambia `sn-chicago` por `sn-apa` en la primera línea de `sn-article.tex`.

## Contenido
- `sn-article.tex` — documento principal Springer (título, autores, abstract, keywords, declaraciones).
- `main_preview.tex` — envoltorio genérico para vista previa rápida.
- `body.tex` — cuerpo (intro, modelo, 10 métodos + DCIH, protocolo Pandiri, resultados).
- `sn-bibliography.bib` — 50 referencias (BibTeX).
- `tab_comparacion_global.tex`, `tab_wilcoxon.tex` — tablas de resultados.
- `figs/` — Fig1 (GAP por escenario), Fig2 (boxplot) y esquemas conceptuales.

Datos: 76 instancias TSPLIB, k = ⌊n/4⌋/⌊n/2⌋/⌊3n/4⌋, SR 0.05·n s / LR 0.2·n s,
10 corridas, BKS de LKH-3, comparación con GVNS/HH de Pandiri & Singh (2020) y
test de Wilcoxon.
