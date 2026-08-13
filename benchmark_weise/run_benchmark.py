"""
run_benchmark.py
================
Driver del benchmarking estilo Weise et al. (2014) para el k-TSP.

Qué hace:
  1) construye el conjunto de instancias (TSPLIB real si hay red; si no, sintéticas);
  2) por cada (instancia, cuartil) corre los 4 métodos con logging ANYTIME,
     R corridas para los estocásticos (Greedy/GRASP/GA) y 1 para el determinista (DCIH);
     todos comparten un presupuesto de DE (evaluaciones de distancia) para que la
     comparación anytime sea justa;
  3) fija la referencia de error F (BKS oficial si la instancia es real y está
     tabulada; si no, el mejor valor encontrado — "best-of");
  4) calcula progreso, ERT, ECDF, AUC y el ranking agregado;
  5) exporta CSVs y figuras a ./salidas_weise/.

Uso:
    python run_benchmark.py
Parámetros rápidos abajo en CONFIG.
"""

from __future__ import annotations
import os, json, pickle, time, shutil
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import ktsp_core as core
from ktsp_core import EVAL, METHODS
import instances as inst_mod
import metrics as M
from metrics import Run

# ─────────────────────────────── CONFIG ─────────────────────────────────────
HERE = Path(__file__).resolve().parent
OUTDIR = Path(os.environ.get("KTSP_OUT", str(HERE / "salidas_weise")))
OUTDIR.mkdir(parents=True, exist_ok=True)
FIGDIR = OUTDIR / "figuras"; FIGDIR.mkdir(exist_ok=True)
PREFER_TSPLIB = os.environ.get("KTSP_NO_NET") != "1"

# (nombre TSPLIB, n). Si hay red se bajan reales; si no, sintéticas del mismo n.
# Las 38 instancias del paper (mismas que las tablas de resultados).
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
QUARTILES = [1, 2, 3]              # Q1~n/4, Q2~n/2, Q3~3n/4
N_RUNS_STOCH = 10                  # corridas por método estocástico (coincide con el paper)
GOAL_ERRORS = [0.35, 0.30, 0.25, 0.20, 0.15]   # umbrales de error meta F_t (Weise)
SEED0 = 42
BUDGET_SCALE = float(os.environ.get("KTSP_BUDGET_SCALE", "15"))  # presupuesto 15*n^2 DE

# Overrides rápidos por entorno (para pruebas / smoke tests):
#   KTSP_FAST=1  reduce instancias, corridas y presupuesto.
if os.environ.get("KTSP_FAST") == "1":
    INSTANCE_SPECS = [("burma14", 14), ("eil51", 51)]
    QUARTILES = [1, 2]
    N_RUNS_STOCH = 4
    BUDGET_SCALE = 8.0
if os.environ.get("KTSP_NRUNS"):
    N_RUNS_STOCH = int(os.environ["KTSP_NRUNS"])
if os.environ.get("KTSP_MAXINST"):
    INSTANCE_SPECS = INSTANCE_SPECS[:int(os.environ["KTSP_MAXINST"])]


def budget_for(n: int) -> int:
    """Presupuesto de DE por instancia (machine-independent)."""
    return int(max(20_000, BUDGET_SCALE * n * n))


# ─────────────────────────── ejecución de una corrida ───────────────────────
def run_once(method_name: str, fn, D, n, k, quartile, run_id, budget_de) -> Run:
    trace_de: List[int] = []
    trace_len: List[float] = []

    def log(de, t, length):
        trace_de.append(de); trace_len.append(length)

    EVAL.reset()
    seed = SEED0 + 100 * quartile + run_id
    kwargs = dict(home=core.HOME, log=log, budget_de=budget_de)
    if method_name == "Greedy":
        # restarts amplios para que consuma su presupuesto de forma anytime
        res = fn(D, n, k, restarts=min(n - 1, 40), seed=seed, **kwargs)
    elif method_name == "GRASP":
        res = fn(D, n, k, time_limit=1e9, seed=seed, max_iters=10_000, **kwargs)
    elif method_name == "GA":
        res = fn(D, n, k, time_limit=1e9, seed=seed, max_gens=100_000, **kwargs)
    elif method_name == "RI":
        res = fn(D, n, k, time_limit=1e9, seed=seed, max_iters=10_000, **kwargs)
    elif method_name == "SA":
        res = fn(D, n, k, time_limit=1e9, seed=seed, **kwargs)
    elif method_name == "DCIH":
        win = 0 if n <= 200 else min(n - 1, max(120, k + 20))
        res = fn(D, n, k, cand_window=win, **kwargs)
    else:  # NN, NI, FI: construcciones deterministas
        res = fn(D, n, k, **kwargs)

    de = np.array(trace_de, dtype=float)
    ln = np.array(trace_len, dtype=float)
    # asegurar monotonía decreciente de la mejor longitud
    if ln.size:
        ln = np.minimum.accumulate(ln)
    return Run(method=method_name, instance="", quartile=quartile, n=n,
               run_id=run_id, de=de, length=ln,
               final_length=float(res["length"]))


# ─────────────────────────────── main ───────────────────────────────────────
def main():
    t_start = time.time()
    print("Construyendo instancias...")
    insts, any_real = inst_mod.build_instance_set(INSTANCE_SPECS, prefer_tsplib=PREFER_TSPLIB)
    src = "TSPLIB real" if any_real else "SINTÉTICAS deterministas (sin red)"
    print(f"Fuente de instancias: {src}")

    all_runs: Dict[Tuple[str, int], List[Run]] = {}   # (instancia, q) -> runs
    refs: Dict[Tuple[str, int], Tuple[float, str]] = {}
    summary_rows = []

    for inst in insts:
        for q in QUARTILES:
            k = inst.k_for(q)
            if k < 3 or k >= inst.n:
                continue
            budget = budget_for(inst.n)
            runs: List[Run] = []
            for mname, (fn, stoch) in METHODS.items():
                R = N_RUNS_STOCH if stoch else 1
                for rid in range(R):
                    run = run_once(mname, fn, inst.D, inst.n, k, q, rid, budget)
                    run.instance = inst.name
                    runs.append(run)
            all_runs[(inst.name, q)] = runs

            # referencia de error F
            bks = inst.bks_for(q) if not inst.synthetic else None
            best_found = min(r.final_length for r in runs)
            if bks is not None:
                ref, ref_src = float(bks), "BKS_oficial"
            else:
                ref, ref_src = float(best_found), "best_found"
            refs[(inst.name, q)] = (ref, ref_src)

            for mname, (fn, stoch) in METHODS.items():
                mruns = [r for r in runs if r.method == mname]
                finals = np.array([r.final_length for r in mruns])
                gap = 100.0 * (finals / ref - 1.0)
                summary_rows.append({
                    "Instancia": inst.name, "n": inst.n, "k": k, "Quartil": q,
                    "Metodo": mname, "sintetica": inst.synthetic,
                    "Ref": round(ref, 2), "Ref_src": ref_src,
                    "GAP_min%": round(float(gap.min()), 3),
                    "GAP_med%": round(float(np.median(gap)), 3),
                    "GAP_max%": round(float(gap.max()), 3),
                    "Len_best": round(float(finals.min()), 2),
                    "corridas": len(mruns),
                    "DE_budget": budget,
                })
            print(f"  {inst.name} Q{q}: k={k}, ref={ref_src}({ref:.0f}) listo")

    df = pd.DataFrame(summary_rows)
    df.to_csv(OUTDIR / "resumen_gaps.csv", index=False)
    with open(OUTDIR / "runs.pkl", "wb") as f:
        pickle.dump({"runs": all_runs, "refs": refs,
                     "meta": {"any_real": any_real, "specs": INSTANCE_SPECS,
                              "quartiles": QUARTILES, "n_runs": N_RUNS_STOCH}}, f)

    # ── métricas agregadas + figuras ──
    method_names = list(METHODS.keys())
    make_all_figures(all_runs, refs, method_names)
    ert_df, rank_df = compute_tables(all_runs, refs, method_names)
    ert_df.to_csv(OUTDIR / "ert_por_instancia.csv", index=False)
    rank_df.to_csv(OUTDIR / "ranking_global.csv", index=False)

    manifest = {
        "descripcion": "Benchmarking anytime (Weise et al. 2014) para el k-TSP",
        "fuente_instancias": src,
        "instancias": [f"{n}(n={i})" for n, i in INSTANCE_SPECS],
        "cuartiles": QUARTILES, "corridas_estocasticas": N_RUNS_STOCH,
        "goal_errors": GOAL_ERRORS,
        "eje_tiempo": "DE = evaluaciones de distancia (machine-independent, escalado por n^2 al agregar)",
        "referencia_error": "BKS oficial si TSPLIB real+tabulada; si no, best-found",
        "salidas": ["resumen_gaps.csv", "ert_por_instancia.csv", "ranking_global.csv",
                    "runs.pkl", "figuras/"],
        "segundos": round(time.time() - t_start, 1),
    }
    (OUTDIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    # Copiar las 3 figuras agregadas a la carpeta del paper (raíz del repo),
    # que es donde el .tex las incluye con \includegraphics.
    paper_dir = HERE.parent
    for fig in ("01_progreso_agregado.png", "02_ecdf_agregado.png", "03_ert_vs_meta.png"):
        src = FIGDIR / fig
        if src.exists():
            shutil.copy(str(src), str(paper_dir / fig))
    print(f"[OK] Figuras del paper actualizadas en: {paper_dir}")

    print(f"\nLISTO en {manifest['segundos']}s. Salidas en {OUTDIR}")
    print(rank_df.to_string(index=False))
    return df, ert_df, rank_df


# ─────────────────────────── tablas ERT y ranking ───────────────────────────
def compute_tables(all_runs, refs, method_names):
    ert_rows = []
    # rank por instancia/cuartil según varias métricas -> rank global
    per_metric_ranks: Dict[str, List[Dict[str, float]]] = {
        "GAP_final": [], "AUC_progreso": [], "AUC_ECDF": [], "ERT@20%": []
    }
    for (name, q), runs in all_runs.items():
        ref, _ = refs[(name, q)]
        budget = max(float(r.de.max()) for r in runs if r.de.size)
        grid = M.de_grid(runs)
        gap_final, auc_prog, auc_ecdf, ert5 = {}, {}, {}, {}
        for m in method_names:
            mruns = [r for r in runs if r.method == m]
            gap_final[m] = float(np.median([r.final_length / ref - 1.0 for r in mruns]))
            prog = M.progress_curve(mruns, ref, grid)
            auc_prog[m] = M.auc_log(grid, prog)
            ec = M.ecdf_curve(mruns, ref, 0.20, grid)
            auc_ecdf[m] = M.auc_log(grid, ec)
            ert5[m] = M.ert(mruns, ref, 0.20, budget)
            for F_t in GOAL_ERRORS:
                ert_rows.append({
                    "Instancia": name, "Quartil": q, "Metodo": m,
                    "F_t": F_t, "ERT_DE": M.ert(mruns, ref, F_t, budget),
                })
        per_metric_ranks["GAP_final"].append(M.rank_lower_better(gap_final))
        per_metric_ranks["AUC_progreso"].append(M.rank_lower_better(auc_prog))
        per_metric_ranks["AUC_ECDF"].append(M.rank_higher_better(auc_ecdf))
        per_metric_ranks["ERT@20%"].append(M.rank_lower_better(ert5))

    rank_rows = []
    for metric, lst in per_metric_ranks.items():
        for m in method_names:
            vals = [d[m] for d in lst if m in d]
            rank_rows.append({"Metrica": metric, "Metodo": m,
                              "rank_mediano": round(float(np.median(vals)), 3)})
    rank_df = pd.DataFrame(rank_rows)
    # ranking GLOBAL: mediana de los rank medianos entre métricas
    glob = (rank_df.groupby("Metodo")["rank_mediano"].median()
            .sort_values().reset_index()
            .rename(columns={"rank_mediano": "rank_global_mediano"}))
    glob["puesto"] = range(1, len(glob) + 1)
    return pd.DataFrame(ert_rows), glob.merge(
        rank_df.pivot(index="Metodo", columns="Metrica", values="rank_mediano"),
        on="Metodo").sort_values("rank_global_mediano")


# ─────────────────────────────── figuras ────────────────────────────────────
COLORS = {
    "Greedy": "#1f77b4", "GRASP": "#ff7f0e", "GA": "#2ca02c",
    "NN": "#9467bd", "NI": "#8c564b", "FI": "#e377c2",
    "RI": "#7f7f7f", "SA": "#bcbd22", "DCIH": "#d62728",
}


def make_all_figures(all_runs, refs, method_names):
    _fig_progress_aggregated(all_runs, refs, method_names)
    _fig_ecdf_aggregated(all_runs, refs, method_names)
    _fig_ert_vs_goal(all_runs, refs, method_names)
    # dos instancias representativas (mayor y menor n disponibles)
    keys = sorted(all_runs.keys(), key=lambda kq: max(r.n for r in all_runs[kq]))
    for kq in {keys[0], keys[-1]}:
        _fig_progress_one(kq, all_runs[kq], refs[kq][0])


def _scaled_common_grid(all_runs, method):
    """Rejilla comun de DE ESCALADO (de/n^2) que cubre todas las corridas del metodo."""
    smin, smax = np.inf, 0.0
    for (name, q), runs in all_runs.items():
        for r in runs:
            if r.method != method or r.de.size == 0:
                continue
            s = r.de / (r.n * r.n)
            smin = min(smin, float(s.min())); smax = max(smax, float(s.max()))
    if not np.isfinite(smin) or smax <= 0:
        return None
    return np.logspace(np.log10(max(smin, 1e-6)), np.log10(smax), 60)


def _fig_progress_aggregated(all_runs, refs, method_names):
    """
    Progreso agregado: cada corrida se evalua como funcion escalon best-so-far
    sobre una rejilla comun de DE escalado (de/n^2), agrupando TODAS las corridas
    de todas las instancias/cuartiles y tomando la mediana. Al ser cada serie
    monotona decreciente, la mediana tambien lo es.
    """
    plt.figure(figsize=(7.5, 5))
    for m in method_names:
        sgrid = _scaled_common_grid(all_runs, m)
        if sgrid is None:
            continue
        series = []
        for (name, q), runs in all_runs.items():
            ref = refs[(name, q)][0]
            for r in runs:
                if r.method != m or r.de.size == 0:
                    continue
                grid_de = sgrid * (r.n * r.n)
                series.append(M.best_error_on_grid(r, ref, grid_de))
        if not series:
            continue
        med = np.nanmedian(np.vstack(series), axis=0)
        plt.plot(sgrid, 100 * med, color=COLORS[m], label=m, lw=2)
    plt.xscale("log"); plt.yscale("log")
    plt.xlabel("Scaled DE  (distance evaluations / n^2)")
    plt.ylabel("Median error F  (%)   [F = len/ref - 1]")
    plt.title("Anytime progress curves (aggregated over instances and quartiles)")
    plt.grid(True, which="both", ls=":", alpha=0.5); plt.legend()
    plt.tight_layout(); plt.savefig(FIGDIR / "01_progreso_agregado.png", dpi=150)
    plt.close()


def _fig_progress_one(kq, runs, ref):
    name, q = kq
    plt.figure(figsize=(7.5, 5))
    grid = M.de_grid(runs)
    for m in COLORS:
        mruns = [r for r in runs if r.method == m]
        if not any(r.de.size for r in mruns):
            continue
        prog = M.progress_curve(mruns, ref, grid)
        plt.plot(grid, 100 * prog, color=COLORS[m], label=m, lw=2)
    plt.xscale("log"); plt.yscale("symlog", linthresh=0.1)
    plt.xlabel("DE (distance evaluations)")
    plt.ylabel("Median error F (%)")
    plt.title(f"Anytime progress — {name} Q{q}")
    plt.grid(True, which="both", ls=":", alpha=0.5); plt.legend()
    plt.tight_layout()
    plt.savefig(FIGDIR / f"04_progreso_{name}_Q{q}.png", dpi=150)
    plt.close()


def _fig_ecdf_aggregated(all_runs, refs, method_names, F_t=0.20):
    plt.figure(figsize=(7.5, 5))
    for m in method_names:
        xs, ys = [], []
        for (name, q), runs in all_runs.items():
            ref = refs[(name, q)][0]
            mruns = [r for r in runs if r.method == m]
            if not any(r.de.size for r in mruns):
                continue
            n = mruns[0].n
            grid = M.de_grid(mruns)
            ec = M.ecdf_curve(mruns, ref, F_t, grid)
            xs.append(grid / (n * n)); ys.append(ec)
        if not xs:
            continue
        common = np.logspace(np.log10(min(x.min() for x in xs)),
                             np.log10(max(x.max() for x in xs)), 60)
        stacked = [np.interp(np.log10(common), np.log10(gx), gy, left=0.0, right=gy[-1])
                   for gx, gy in zip(xs, ys)]
        mean = np.mean(np.vstack(stacked), axis=0)
        plt.plot(common, mean, color=COLORS[m], label=m, lw=2)
    plt.xscale("log")
    plt.xlabel("Scaled DE (distance evaluations / n^2)")
    plt.ylabel(f"Fraction of runs with F <= {int(F_t*100)}%")
    plt.title("Aggregated ECDF — probability of reaching the target error vs time")
    plt.ylim(-0.02, 1.02); plt.grid(True, which="both", ls=":", alpha=0.5); plt.legend()
    plt.tight_layout(); plt.savefig(FIGDIR / "02_ecdf_agregado.png", dpi=150)
    plt.close()

def _fig_ert_vs_goal(all_runs, refs, method_names):
    """ERT medio (DE escalado por n^2) vs error meta F_t, agregado."""
    plt.figure(figsize=(7.5, 5))
    Fts = [f for f in GOAL_ERRORS if f > 0]
    for m in method_names:
        ys = []
        for F_t in Fts:
            vals = []
            for (name, q), runs in all_runs.items():
                ref = refs[(name, q)][0]
                mruns = [r for r in runs if r.method == m]
                if not any(r.de.size for r in mruns):
                    continue
                n = mruns[0].n
                budget = max(float(r.de.max()) for r in mruns if r.de.size)
                e = M.ert(mruns, ref, F_t, budget)
                if np.isfinite(e):
                    vals.append(e / (n * n))
            ys.append(np.median(vals) if vals else np.nan)
        plt.plot([100 * f for f in Fts], ys, "o-", color=COLORS[m], label=m, lw=2)
    plt.xscale("log"); plt.yscale("log")
    plt.gca().invert_xaxis()
    plt.xlabel("Target error F_t (%) — more demanding to the right")
    plt.ylabel("Median ERT (DE / n^2)")
    plt.title("Estimated Running Time (ERT) to reach the target error")
    plt.grid(True, which="both", ls=":", alpha=0.5); plt.legend(loc="center left")
    plt.tight_layout(); plt.savefig(FIGDIR / "03_ert_vs_meta.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    main()
