# Paper k-TSP para OPSEARCH (plantilla Springer Nature)

Contenido de esta carpeta:

| Archivo | Qué es |
|---|---|
| `sn-article.tex` | Documento principal (envoltorio Springer, estilo autor-año sn-chicago) |
| `body.tex` | Cuerpo del paper (secciones, modelo, métodos, resultados) |
| `sn-bibliography.bib` | 50 referencias en formato BibTeX |
| `tab_comparacion_global.tex` | Tabla 1: GAP medio por método, escenario y criterio (incluye GVNS/HH de Pandiri) |
| `tab_wilcoxon.tex` | Tabla 2: test de Wilcoxon (tus mejores métodos vs Pandiri) |
| `figs/` | Figuras (Fig1, Fig2 + los esquemas conceptuales) |
| `PREVIEW_local_validation.pdf` | Vista previa compilada localmente (clase genérica, sin la plantilla Springer) |

## Cómo compilarlo en Overleaf
1. En Overleaf: **New Project → Templates** y busca **"Springer Nature LaTeX Template"**.
   Crea el proyecto (trae `sn-jnl.cls` y los estilos `.bst`).
2. Sube a ese proyecto: `sn-article.tex`, `body.tex`, `sn-bibliography.bib`,
   `tab_comparacion_global.tex`, `tab_wilcoxon.tex` y la carpeta `figs/`.
3. Marca `sn-article.tex` como documento principal (Menu → Main document).
4. Compilador **pdfLaTeX** → **Recompile**.

Si Overleaf pide el estilo de citas exacto de OPSEARCH (APA), cambia en la primera
línea `sn-chicago` por `sn-apa`. Ambos son autor-año; con `sn-apa` las citas
narrativas pueden requerir `\citeA` en vez de `\citet` (avísame y lo ajusto).

## Datos
- 76 instancias TSPLIB, k = ⌊n/4⌋, ⌊n/2⌋, ⌊3n/4⌋.
- Criterios de tiempo: SR = 0.05·n s, LR = 0.2·n s, 10 corridas.
- Referencia: BKS de LKH-3. Comparación con GVNS/HH_RAND/HH_GREEDY de Pandiri & Singh (2020).
- Análisis estadístico: Wilcoxon signed-rank (dos colas).
