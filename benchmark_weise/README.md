# Benchmarking anytime para el k-TSP — metodología de Weise et al. (2014)

Este paquete replica, sobre tu repositorio del **k-TSP**, la metodología de

> T. Weise, R. Chiong, J. Lässig, K. Tang, S. Tsutsui, W. Chen, Z. Michalewicz, X. Yao.
> *Benchmarking Optimization Algorithms: An Open Source Framework for the Traveling
> Salesman Problem.* IEEE Computational Intelligence Magazine, 2014.

La idea central del paper: **no comparar algoritmos sólo por el resultado final**
(end-of-run), sino por su comportamiento *anytime* — la calidad de la mejor
solución a lo largo del tiempo. De ahí salen curvas de progreso, ERT, ECDF, AUC y
un ranking agregado.

## Qué se implementó (mapa al paper)

| Concepto de Weise | Aquí |
|---|---|
| Tiempo *machine-independent* (FE/DE) | Contador global **DE = evaluaciones de distancia** (`ktsp_core.EVAL`), escalado por `n²` al agregar |
| Log points anytime (Fig. 1c–d) | Cada método emite `log(de, t, length)` en cada iteración/restart/generación |
| Error normalizado `F = f/f_opt − 1` | `metrics.error_at` / `best_error_on_grid` (referencia = BKS oficial o best-found) |
| Curvas de progreso (Fig. 5a) | `01_progreso_agregado.png`, `04_progreso_<inst>_Q*.png` |
| ERT (Estimated Running Time) | `metrics.ert`, figura `03_ert_vs_meta.png`, tabla `ert_por_instancia.csv` |
| ECDF (Fig. 6) | `metrics.ecdf_curve`, figura `02_ecdf_agregado.png` |
| Comparación por AUC | `metrics.auc_log` (progreso y ECDF) |
| Ranking agregado (sec. II.8) | `metrics.rank_*`, tabla `ranking_global.csv` |

## Archivos

- `ktsp_core.py` — primitivas (2-opt, swap in/out, cheapest insertion) y los 4 métodos
  del notebook (**Greedy, GRASP, GA, NBR/DCIH**) instrumentados con el contador DE y
  log points anytime. Son los mismos algoritmos; sólo se añadió la instrumentación.
- `instances.py` — carga instancias: intenta **TSPLIB real** (funciona en Colab con
  red) y cae a **euclidianas deterministas** offline. Trae los BKS oficiales
  (Helsgaun/Pandiri & Singh) para las instancias pequeñas.
- `metrics.py` — todas las métricas de Weise.
- `run_benchmark.py` — driver: corre todo, exporta CSVs y figuras a `salidas_weise/`.
- `salidas_weise/` — salida de ejemplo (ver nota abajo).

## Cómo correr

```bash
cd benchmark_weise
python run_benchmark.py
```

Con red (p.ej. **Google Colab**) descarga las instancias TSPLIB reales y usa los
**BKS oficiales** como referencia de error — igual que tu paper. Sin red, usa las
sintéticas y `best-found` como referencia.

### Parámetros (arriba en `run_benchmark.py`)

- `INSTANCE_SPECS` — instancias y tamaños.
- `QUARTILES` — Q1≈n/4, Q2≈n/2, Q3≈3n/4 (los cuartiles de tu paper).
- `N_RUNS_STOCH` — corridas por método estocástico (para ECDF/ERT). Sube a 15–30
  para curvas más suaves.
- `GOAL_ERRORS` — umbrales de error meta `F_t` para ERT/ECDF.
- `BUDGET_SCALE` — presupuesto de DE por instancia = `BUDGET_SCALE · n²`.

Overrides por entorno para pruebas rápidas: `KTSP_FAST=1`, `KTSP_NRUNS`,
`KTSP_MAXINST`, `KTSP_BUDGET_SCALE`, `KTSP_NO_NET=1`, `KTSP_OUT=<dir>`.

## Enchufar tus algoritmos originales

`ktsp_core.py` ya contiene tus métodos. Si quieres usar exactamente tu implementación
del notebook, envuélvela con el mismo patrón: acepta un callback `log(de, t, length)`
y llámalo cada vez que produzcas/actualices una solución, incrementando `EVAL.de` en
las primitivas de distancia. Después regístrala en el diccionario `METHODS`.

## Nota sobre las figuras de ejemplo

La carpeta `salidas_weise/` incluida se generó **offline en un sandbox sin acceso a
TSPLIB**, por lo que usa instancias **euclidianas sintéticas** (mismos tamaños que
`INSTANCE_SPECS`) y `best-found` como referencia. La *maquinaria* (DE, log points,
progreso, ERT, ECDF, AUC, ranking) es idéntica a la que correrás en Colab con las
instancias reales y los BKS oficiales; sólo cambian los números concretos.
