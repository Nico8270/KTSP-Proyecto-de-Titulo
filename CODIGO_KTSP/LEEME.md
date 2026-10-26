# Código k-TSP — comparación reproducible (protocolo Pandiri & Singh)

Autor: Nicolás Barrientos · Prof. guía: Dr. Gustavo Gatica · UNAB

Este paquete contiene todo lo necesario para **ejecutar los experimentos** del
proyecto: diez métodos para el k-TSP evaluados sobre las 76 instancias de TSPLIB
bajo el protocolo de Pandiri & Singh (OPSEARCH 2020) —tres valores de k
(⌊n/4⌋, ⌊n/2⌋, ⌊3n/4⌋), límites de tiempo short run 0.05·n s y long run 0.2·n s,
10 corridas— con el test de Wilcoxon y LKH-3 como referencia (BKS).

## Archivos
| Archivo | Qué es |
|---|---|
| `ktsp_core.py` | Los 10 métodos (Greedy, GRASP, GA, NN, NI, FI, RI, SA, TS, DCIH) y el núcleo común de búsqueda local (2-opt, intercambio, inserción). |
| `instances.py` | Carga las 76 instancias de TSPLIB y la tabla de valores de referencia (BKS de LKH-3 / Pandiri & Singh). |
| `run_opsearch_protocol.py` | **Script principal**: corre el protocolo completo y produce los resultados. |
| `wilcoxon_test.py` | Test de Wilcoxon de rangos con signo sobre los resultados. |
| `check_instances.py` | Diagnóstico: verifica qué instancias se cargan reales (TSPLIB) o sintéticas. |
| `requirements.txt` | Dependencias de Python. |
| `resultados/` | Resultados ya generados (CSV) y los datos de referencia de Pandiri & Singh. |

## Requisitos
- Python 3.10+ (probado en Python 3.1x).
- Instalar dependencias:
  ```
  pip install -r requirements.txt
  ```
- Conexión a internet la primera vez (el cargador descarga las instancias de
  TSPLIB automáticamente). Sin internet, caería en coordenadas sintéticas y los
  GAP no tendrían sentido; `check_instances.py` avisa de eso.

## Cómo ejecutar
Desde esta carpeta, en una terminal:

```
# 1) (opcional) verificar que las 76 instancias cargan reales
python check_instances.py

# 2) primera pasada rápida: solo short run (~unas horas según la máquina)
python run_opsearch_protocol.py --criteria SR

# 3) protocolo completo (short + long run; varias horas, usa todos los núcleos)
python run_opsearch_protocol.py
```

Opciones útiles: `--jobs N` (procesos en paralelo), `--max-n 300` (saltar
instancias grandes), `--runs K` (corridas por método estocástico), `--smoke`
(prueba rápida de 3 instancias).

## Salidas (se escriben en esta carpeta)
- `resultados_opsearch.csv` — mejor longitud y GAP% por método, instancia,
  escenario de k y criterio de tiempo.
- `resumen_opsearch.csv` — GAP% medio por método × escenario × criterio.
- `wilcoxon_*.csv` — resultados del test de Wilcoxon (se corre automáticamente al
  final).

En la carpeta `resultados/` se incluyen estos mismos archivos **ya generados**
(los que se reportan en el paper y la tesis), para revisarlos sin tener que
re-ejecutar las varias horas de cómputo.

## Nota
Los valores de referencia (BKS de LKH-3) y las columnas de GVNS/HH_RAND/HH_GREEDY
(`resultados/pandiri_baselines.csv`) son valores publicados de Pandiri & Singh
(2020), usados como referencia y comparación; no se recomputan en esta ejecución.
