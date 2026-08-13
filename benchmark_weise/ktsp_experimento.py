"""
ktsp_experimento.py
===================
Script de comparacion de heuristicas para el k-TSP, pensado para abrirse y
EJECUTARSE directamente en Visual Studio Code (boton Run o F5).

Corre los NUEVE metodos del repositorio sobre un conjunto de instancias
(TSPLIB reales si hay conexion; si no, sinteticas deterministas) y para cada
instancia y cuartil (Q1~n/4, Q2~n/2, Q3~3n/4) reporta:
  * la longitud total del tour (SUM) de cada metodo, y
  * el GAP relativo (%) contra la referencia:
        - BKS oficial de LKH-3/Pandiri-Singh si la instancia es real y esta
          tabulada, o
        - el mejor valor encontrado (best-found) en caso contrario.

Metodos comparados:
  Greedy, GRASP, GA, NN, NI, FI, RI, SA, DCIH (propuesto).

Uso en VS Code:
  1) Abrir la carpeta 'benchmark_weise' en VS Code.
  2) (opcional) crear entorno e instalar dependencias:  pip install numpy pandas
  3) Ejecutar este archivo (Run Python File).
Salidas: se imprime la tabla en consola y se guardan
         'comparacion_9metodos.csv' y 'comparacion_9metodos.tex'.

Configuracion rapida abajo en CONFIG.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# Modulos del repositorio (mismo directorio)
import ktsp_core as core
from ktsp_core import METHODS, EVAL, tour_length, validate_ktsp
import instances as inst_mod

# ─────────────────────────────── CONFIG ─────────────────────────────────────
# Instancias a evaluar (nombre TSPLIB, n). Se descargan reales si hay red.
INSTANCE_SPECS: List[Tuple[str, int]] = [
    ("att48", 48), ("eil51", 51), ("berlin52", 52), ("st70", 70),
    ("eil76", 76), ("pr76", 76), ("kroA100", 100), ("kroB100", 100),
    ("kroC100", 100), ("kroD100", 100), ("kroE100", 100), ("eil101", 101),
    ("lin105", 105), ("pr107", 107), ("pr124", 124), ("bier127", 127),
    ("ch130", 130), ("pr136", 136), ("gr137", 137), ("ch150", 150),
    ("kroA150", 150), ("kroB150", 150), ("rat195", 195), ("kroA200", 200),
    ("kroB200", 200), ("ts225", 225), ("tsp225", 225), ("pr226", 226),
    ("gr229", 229), ("gil262", 262), ("pr264", 264), ("a280", 280),
    ("pr299", 299), ("lin318", 318), ("rd400", 400), ("fl417", 417),
    ("pr439", 439), ("pcb442", 442),
]
QUARTILES = [1, 2, 3]                 # Q1~n/4, Q2~n/2, Q3~3n/4
SEED0 = 42                            # semilla base de los metodos estocasticos
TIME_LIMIT = 2.0                      # segundos por metodo estocastico y por instancia
PREFER_TSPLIB = os.environ.get("KTSP_NO_NET") != "1"   # KTSP_NO_NET=1 fuerza sinteticas
OUTDIR = Path(__file__).resolve().parent


# ─────────────────────── ejecucion de un metodo ─────────────────────────────
def run_method(name: str, fn, D, n: int, k: int, seed: int) -> dict:
    """Despacha cada metodo con sus parametros propios y devuelve su resultado.
    Solo interesa el resultado final (no se registran log points aqui)."""
    EVAL.reset()
    if name == "Greedy":
        return fn(D, n, k, restarts=min(n - 1, 40), seed=seed)
    if name == "GRASP":
        return fn(D, n, k, time_limit=TIME_LIMIT, seed=seed, max_iters=10_000)
    if name == "GA":
        return fn(D, n, k, time_limit=TIME_LIMIT, seed=seed, max_gens=100_000)
    if name == "RI":
        return fn(D, n, k, time_limit=TIME_LIMIT, seed=seed, max_iters=10_000)
    if name == "SA":
        return fn(D, n, k, time_limit=TIME_LIMIT, seed=seed)
    if name == "DCIH":
        win = 0 if n <= 200 else min(n - 1, max(120, k + 20))
        return fn(D, n, k, cand_window=win)
    # NN, NI, FI: construcciones deterministas
    return fn(D, n, k)


def _write_latex_table(resumen: pd.DataFrame, path: Path) -> None:
    """Escribe la tabla-resumen en LaTeX sin dependencias externas (jinja2)."""
    lines = [
        r"\begin{table}[H]", r"\centering",
        r"\caption{GAP relativo (\%) de los nueve metodos frente a la referencia "
        r"(BKS de LKH-3 o best-found), agregado sobre instancias y cuartiles.}",
        r"\label{tab:comparacion9}",
        r"\begin{tabular}{lrrr}", r"\hline",
        r"\textbf{Method} & \textbf{Median GAP\%} & \textbf{Mean GAP\%} & \textbf{\# best} \\ \hline",
    ]
    for _, r in resumen.iterrows():
        lines.append(f"{r['Metodo']} & {r['GAP_mediano%']:.3f} & "
                     f"{r['GAP_promedio%']:.3f} & {int(r['Veces_mejor'])} \\\\")
    lines += [r"\hline", r"\end{tabular}", r"\end{table}", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


# ─────────────────────────────── main ───────────────────────────────────────
def main() -> pd.DataFrame:
    print("Construyendo instancias...")
    insts, any_real = inst_mod.build_instance_set(INSTANCE_SPECS, prefer_tsplib=PREFER_TSPLIB)
    fuente = "TSPLIB real" if any_real else "SINTETICAS deterministas (sin red)"
    print(f"Fuente de instancias: {fuente}\n")

    method_names = list(METHODS.keys())
    rows: List[Dict] = []

    for inst in insts:
        for q in QUARTILES:
            k = inst.k_for(q)
            if k < 3 or k >= inst.n:
                continue
            res_by_method = {}
            for name, (fn, stoch) in METHODS.items():
                seed = SEED0 + 100 * q
                res = run_method(name, fn, inst.D, inst.n, k, seed)
                ok, msg = validate_ktsp(res["tour"], inst.n, k)
                if not ok:
                    print(f"  [WARN] {inst.name} Q{q} {name} invalido: {msg}")
                res_by_method[name] = float(res["length"])

            # referencia de error: BKS oficial si existe; si no, best-found
            bks = inst.bks_for(q) if not inst.synthetic else None
            best_found = min(res_by_method.values())
            if bks is not None:
                ref, ref_src = float(bks), "BKS_LKH3"
            else:
                ref, ref_src = float(best_found), "best_found"

            row = {"Instancia": inst.name, "n": inst.n, "k": k, "Quartil": q,
                   "Ref": round(ref, 2), "Ref_src": ref_src}
            for name in method_names:
                L = res_by_method[name]
                row[f"{name}_Len"] = round(L, 2)
                row[f"{name}_GAP%"] = round(100.0 * (L / ref - 1.0), 3)
            rows.append(row)
            best = min(method_names, key=lambda m: res_by_method[m])
            print(f"  {inst.name} Q{q}: k={k}, ref={ref_src}({ref:.0f}), mejor={best}")

    df = pd.DataFrame(rows)

    # ── resumen: GAP mediano por metodo (menor es mejor) ──
    gap_cols = {m: f"{m}_GAP%" for m in method_names}
    resumen = pd.DataFrame({
        "Metodo": method_names,
        "GAP_mediano%": [round(float(df[gap_cols[m]].median()), 3) for m in method_names],
        "GAP_promedio%": [round(float(df[gap_cols[m]].mean()), 3) for m in method_names],
        "Veces_mejor": [int((df[[gap_cols[mm] for mm in method_names]]
                             .idxmin(axis=1) == gap_cols[m]).sum()) for m in method_names],
    }).sort_values("GAP_mediano%").reset_index(drop=True)

    # ── exportar ──
    csv_path = OUTDIR / "comparacion_9metodos.csv"
    tex_path = OUTDIR / "comparacion_9metodos.tex"
    df.to_csv(csv_path, index=False)
    _write_latex_table(resumen, tex_path)

    print("\n================ RESUMEN (GAP mediano por metodo) ================")
    print(resumen.to_string(index=False))
    print(f"\nDetalle por instancia -> {csv_path}")
    print(f"Tabla LaTeX del resumen -> {tex_path}")
    return df


if __name__ == "__main__":
    main()
