# k-TSP — Proyecto de Título

Comparación reproducible de heurísticas para el **k-Traveling Salesman Problem**
(seleccionar exactamente *k* nodos, un solo tour, distancia total mínima).

Se comparan **9 métodos**: Greedy (cheapest insertion), GRASP, Genetic Algorithm (GA),
Nearest Neighbor (NN), Nearest Insertion (NI), Farthest Insertion (FI),
Random Insertion (RI), Simulated Annealing (SA) y la heurística propuesta
**DCIH** (Deterministic Cheapest-Insertion Heuristic). La referencia de calidad
es el BKS de **LKH-3** sobre el benchmark de Pandiri & Singh.

## Contenido

- `resumen_k_tsp_13.0.tex` — el paper (se compila en Overleaf; usa la clase IEEEtran).
- `ktsp_corregido_2_0.ipynb` — notebook principal: descarga TSPLIB, corre los 9 métodos
  + LKH-3 y genera las tablas de resultados (GAP por instancia y cuartil).
- `benchmark_weise/` — pipeline de *benchmarking anytime* estilo Weise et al. (2014):
  - `ktsp_core.py` — los 9 métodos (núcleo).
  - `ktsp_experimento.py` — **script listo para VS Code**: corre los 9 métodos y
    exporta una tabla comparativa (`comparacion_9metodos.csv` / `.tex`).
  - `run_benchmark.py` — curvas anytime, ERT, ECDF y ranking global (figuras).

## Cómo correrlo en VS Code

1. Clonar el repositorio y abrir la carpeta en VS Code.
2. Instalar dependencias:

   ```
   pip install -r requirements.txt
   ```

3. Ejecutar el script de comparación (botón **Run** / F5):

   ```
   python benchmark_weise/ktsp_experimento.py
   ```

   Genera en `benchmark_weise/` los archivos `comparacion_9metodos.csv` y `.tex`.
   Sin conexión usa instancias sintéticas; con conexión baja TSPLIB reales.

## Cómo generar las tablas del paper (con LKH-3)

Para reproducir las tablas de GAP del paper (BKS oficial de LKH-3):

- **Google Colab** (recomendado): abrir `ktsp_corregido_2_0.ipynb`, ejecutar en orden
  la celda que compila LKH-3, el `pip install`, la celda principal y la del reporte.
- **Local**: requiere el binario LKH-3 compilado y acceso a internet para TSPLIB.

La corrida produce `resultados_ktsp/resultados_kTSP.csv` con las columnas de los 9
métodos (`*_Len`, `*_GAP%`) y el `BKS_oficial`.

## Reproducibilidad

Los métodos estocásticos (GRASP, GA, RI, SA) usan semilla fija; los deterministas
(NN, NI, FI, DCIH) devuelven siempre el mismo tour.
