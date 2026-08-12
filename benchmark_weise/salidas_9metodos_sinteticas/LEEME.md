# Demostración: benchmark anytime con los 9 métodos (instancias sintéticas)

Estas salidas se generaron para **validar** que el pipeline `benchmark_weise`
funciona con las 5 heurísticas nuevas (NN, NI, FI, RI, SA) además de las 4
originales (Greedy, GRASP, GA, DCIH).

IMPORTANTE — estas NO son las cifras definitivas del paper:
- Se corrieron sobre **instancias sintéticas deterministas** (el entorno no tenía
  red para descargar TSPLIB ni el binario LKH-3), por lo que la referencia de
  error es *best-found*, no el BKS oficial de LKH-3.
- Configuración: 8 instancias, 3 cuartiles, 15 corridas estocásticas,
  presupuesto 60·n² evaluaciones de distancia.

Para las cifras definitivas del paper, reproducir en una máquina con red:

    cd benchmark_weise
    python run_benchmark.py        # usa TSPLIB real si hay conexión

Las salidas oficiales viven en `benchmark_weise/salidas_weise/`.

Ranking global (anytime, esta corrida sintética):
NN, Greedy, DCIH, SA, GRASP, NI, RI, GA, FI.
