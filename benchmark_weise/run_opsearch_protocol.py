#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPSEARCH experimental protocol runner for the k-TSP
===================================================

Reproduces the experimental protocol of Pandiri & Singh (2020),
"Two multi-start heuristics for the k-traveling salesman problem",
OPSEARCH 57:1164-1204, so that our results are directly comparable with
that paper (same journal, same benchmark).

Protocol (identical to Pandiri & Singh 2020):
  * 76 TSPLIB instances (the full OFFICIAL_KTSP table in instances.py).
  * Three k scenarios per instance:
        Small  : k = floor(n/4)
        Medium : k = floor(n/2)
        Large  : k = floor(3n/4)
  * Two wall-clock termination criteria:
        SR (Short Run) : 0.05 * n seconds
        LR (Long Run)  : 0.20 * n seconds
  * 10 independent runs per (instance, scenario, criterion, method).
  * GAP% against the LKH-3 best-known solution (BKS).
  * Two-tailed Wilcoxon signed-rank test over the per-case results
    (delegated to wilcoxon_test.py).

All ten methods are evaluated: Greedy, GRASP, GA, NN, NI, FI, RI, SA, TS, DCIH.

------------------------------------------------------------------------
HOW TO RUN (VS Code: open this file and press "Run Python File", or a
terminal in this folder):

    python run_opsearch_protocol.py                 # full protocol (all cores)
    python run_opsearch_protocol.py --smoke         # 3 tiny instances, fast
    python run_opsearch_protocol.py --max-n 300     # skip instances with n>300
    python run_opsearch_protocol.py --criteria SR   # only Short Run
    python run_opsearch_protocol.py --runs 5        # fewer runs (testing)
    python run_opsearch_protocol.py --jobs 8        # 8 parallel workers

WARNING: the full protocol is heavy. Each of the 10 methods gets the full
time budget, over 76 x 3 x 2 = 456 configs with 10 runs each. Rough
single-core cost ~210 h. The configs are independent, so the runner
parallelises across CPU cores by default (--jobs, default CPUs-1):

    cores        full protocol      --max-n 300        SR only
    1 (serial)   ~210 h             ~87 h              ~42 h
    8            ~27 h              ~11 h              ~5 h
    16           ~13 h              ~5.5 h             ~3 h

Recommended first pass: `--criteria SR` to get Short-Run results in a day,
then add LR. Progress + ETA is printed as configs finish.

NOTE: results are only meaningful with the REAL TSPLIB instances. On a
machine with internet the loader downloads them automatically; otherwise
place the .tsp files locally. Without them it falls back to synthetic
coordinates and prints a warning (GAP%% vs BKS would be meaningless).

Outputs (in this folder):
    resultados_opsearch.csv      one row per (instance, scenario, criterion);
                                 best/mean/worst length + GAP% for each method
    resumen_opsearch.csv         mean GAP% per method x scenario x criterion
    wilcoxon_*.csv / .tex        statistical test (via wilcoxon_test.py)
------------------------------------------------------------------------
"""
import argparse
import inspect
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

import ktsp_core as core
import instances as inst

SCENARIOS = [(1, "Small"), (2, "Medium"), (3, "Large")]       # k = n/4, n/2, 3n/4
CRITERIA = {"SR": 0.05, "LR": 0.20}                           # factor * n seconds
METHOD_ORDER = ["Greedy", "GRASP", "GA", "NN", "NI", "FI", "RI", "SA", "TS", "DCIH"]
HERE = os.path.dirname(os.path.abspath(__file__))


def _accepts(fn, param):
    try:
        return param in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


def solve_once(method, D, n, k, time_limit, seed):
    """Run one method under a wall-clock budget. Returns tour length (float)."""
    fn, _stoch = core.METHODS[method]
    core.EVAL.reset()
    kwargs = dict(home=core.HOME)
    if _accepts(fn, "seed"):
        kwargs["seed"] = seed
    if _accepts(fn, "time_limit"):
        kwargs["time_limit"] = time_limit
    res = fn(D, n, k, **kwargs)
    return float(res["length"])


def run_config(instance, k, time_limit, n_runs):
    """All methods on one (instance, k, criterion). Returns {method: stats}."""
    D, n = instance.D, instance.n
    out = {}
    for method in METHOD_ORDER:
        _, stochastic = core.METHODS[method]
        reps = n_runs if stochastic else 1          # deterministic -> single run
        lengths = []
        for r in range(reps):
            seed = 1000 + r                          # reproducible seeds 1000..
            lengths.append(solve_once(method, D, n, k, time_limit, seed))
        arr = np.asarray(lengths, float)
        out[method] = {
            "best": float(arr.min()),
            "mean": float(arr.mean()),
            "worst": float(arr.max()),
            "std": float(arr.std(ddof=0)),
            "runs": reps,
        }
    return out


def gap(length, bks):
    if bks is None or bks <= 0:
        return np.nan
    return 100.0 * (length - bks) / bks


def _run_task(task):
    """Worker: one (instance, scenario, criterion) config -> result row dict.

    Self-contained so it can run in a separate process.
    """
    instance, q, qlabel, crit, n_runs = task
    n = instance.n
    k = instance.k_for(q)
    bks = instance.bks_for(q)
    tlim = CRITERIA[crit] * n
    t0 = time.perf_counter()
    stats = run_config(instance, k, tlim, n_runs)
    row = {
        "Instance": instance.name, "n": n, "Scenario": qlabel, "k": k,
        "Criterion": crit, "time_limit_s": round(tlim, 3), "LKH3_BKS": bks,
    }
    for method in METHOD_ORDER:
        s = stats[method]
        row[f"{method}_best"] = round(s["best"], 2)
        row[f"{method}_mean"] = round(s["mean"], 2)
        row[f"{method}_worst"] = round(s["worst"], 2)
        row[f"{method}_GAP%"] = round(gap(s["best"], bks), 3)
    row["_elapsed"] = time.perf_counter() - t0
    return row


def main():
    ap = argparse.ArgumentParser(description="OPSEARCH k-TSP protocol runner.")
    ap.add_argument("--runs", type=int, default=10, help="runs per stochastic method")
    ap.add_argument("--criteria", nargs="+", default=["SR", "LR"], choices=["SR", "LR"])
    ap.add_argument("--max-n", type=int, default=None, help="skip instances with n greater than this")
    ap.add_argument("--smoke", action="store_true", help="3 tiny instances, quick test")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 1) - 1),
                    help="parallel worker processes (default: CPUs-1)")
    ap.add_argument("--names", nargs="+", default=None,
                    help="run only these instances (by TSPLIB name)")
    ap.add_argument("--merge", action="store_true",
                    help="merge results into existing resultados_opsearch.csv "
                         "(replace rows for the instances/criteria just run)")
    ap.add_argument("--outdir", default=HERE)
    args = ap.parse_args()

    names = list(inst.OFFICIAL_KTSP.keys())
    if args.smoke:
        names = names[:3]
        args.criteria = ["SR"]
    if args.names:
        wanted = set(args.names)
        names = [m for m in names if m in wanted]
        missing = wanted - set(names)
        if missing:
            print(f"WARNING: unknown instance names ignored: {sorted(missing)}")
    if args.max_n is not None:
        names = [m for m in names if inst.OFFICIAL_KTSP[m]["n"] <= args.max_n]

    print(f"Instances: {len(names)} | criteria: {args.criteria} | "
          f"runs/stochastic: {args.runs} | jobs: {args.jobs}")
    specs = [(m, inst.OFFICIAL_KTSP[m]["n"]) for m in names]
    print("Loading instances (TSPLIB if available, else synthetic)...")
    iset, used_real = inst.build_instance_set(specs)
    print(f"  (using {'real TSPLIB' if used_real else 'synthetic'} coordinates)")
    if not used_real:
        print("  WARNING: no TSPLIB coordinates available -> GAP%% vs BKS is "
              "meaningless. Run on a machine with network or local .tsp files.")
    by_name = {it.name: it for it in iset}

    # Build the full list of independent (instance, scenario, criterion) tasks.
    tasks = []
    for name in names:
        instance = by_name.get(name)
        if instance is None:
            print(f"  [skip] {name}: could not build")
            continue
        for q, qlabel in SCENARIOS:
            for crit in args.criteria:
                tasks.append((instance, q, qlabel, crit, args.runs))
    total = len(tasks)
    print(f"Total configs to run: {total}\n")

    rows = []
    t_start = time.perf_counter()
    done = 0
    if args.jobs <= 1:
        for task in tasks:
            row = _run_task(task)
            rows.append(row)
            done += 1
            tot = time.perf_counter() - t_start
            print(f"  [{done}/{total}] {row['Instance']} n={row['n']} "
                  f"{row['Scenario']} {row['Criterion']} "
                  f"t_lim={row['time_limit_s']:.1f}s  "
                  f"({row['_elapsed']:.1f}s, total {tot/60:.1f} min)")
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futs = {ex.submit(_run_task, t): t for t in tasks}
            for fut in as_completed(futs):
                row = fut.result()
                rows.append(row)
                done += 1
                tot = time.perf_counter() - t_start
                eta = (tot / done) * (total - done) / 60
                print(f"  [{done}/{total}] {row['Instance']} n={row['n']} "
                      f"{row['Scenario']} {row['Criterion']} "
                      f"({row['_elapsed']:.1f}s, total {tot/60:.1f} min, "
                      f"ETA {eta:.1f} min)")

    df = pd.DataFrame(rows).drop(columns=["_elapsed"])
    out_csv = os.path.join(args.outdir, "resultados_opsearch.csv")

    if args.merge and os.path.exists(out_csv):
        old = pd.read_csv(out_csv)
        # Drop the (Instance, Criterion) combos we just recomputed, keep the rest.
        done_keys = set(zip(df.Instance, df.Criterion))
        mask = [(i, c) not in done_keys for i, c in zip(old.Instance, old.Criterion)]
        kept = old[mask]
        df = pd.concat([kept, df], ignore_index=True)
        print(f"Merged: kept {len(kept)} old rows + {len(rows)} new rows.")

    # Stable ordering regardless of completion order.
    df = df.sort_values(["Criterion", "n", "Scenario"]).reset_index(drop=True)
    df.to_csv(out_csv, index=False)
    print(f"\nWrote {out_csv}  ({len(df)} rows)")

    # Per-method mean GAP% summary (scenario x criterion)
    summ = []
    for crit in args.criteria:
        for _, qlabel in SCENARIOS:
            sub = df[(df.Criterion == crit) & (df.Scenario == qlabel)]
            if sub.empty:
                continue
            rec = {"Criterion": crit, "Scenario": qlabel, "cases": len(sub)}
            for method in METHOD_ORDER:
                rec[method] = round(sub[f"{method}_GAP%"].mean(), 3)
            summ.append(rec)
    summdf = pd.DataFrame(summ)
    out_sum = os.path.join(args.outdir, "resumen_opsearch.csv")
    summdf.to_csv(out_sum, index=False)
    print(f"Wrote {out_sum}")
    print("\nMean GAP% per method:")
    with pd.option_context("display.width", 160, "display.max_columns", 30):
        print(summdf.to_string(index=False))

    # Wilcoxon signed-rank test on the per-case GAP% (delegated)
    wtest = os.path.join(HERE, "wilcoxon_test.py")
    if os.path.exists(wtest):
        print("\n" + "=" * 60 + "\nWilcoxon signed-rank test\n" + "=" * 60)
        try:
            subprocess.run([sys.executable, wtest, out_csv, "--outdir", args.outdir],
                           check=True)
        except subprocess.CalledProcessError as e:
            print(f"Wilcoxon step failed: {e}")
    else:
        print("\n(wilcoxon_test.py not found; skipping statistical test.)")

    print(f"\nDone in {(time.perf_counter() - t_start)/60:.1f} min.")


if __name__ == "__main__":
    main()
