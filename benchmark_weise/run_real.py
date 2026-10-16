"""
run_real.py — Benchmark anytime (Weise) sobre las 38 instancias TSPLIB REALES
del paquete oficial k-TSP de Helsgaun (Pandiri & Singh 2020).

k y referencia (valor LKH-3) tomados del paquete oficial (ktsp_table.json).
Checkpoint POR INSTANCIA: cada instancia se guarda en results_real/<name>.pkl,
así el proceso se puede reanudar en varias llamadas sin rehacer trabajo.

Uso:
    KTSP_PKG=/ruta/k-TSP  python run_real.py           # procesa pendientes
    ...  python run_real.py --aggregate                # figuras + tablas
Env:
    KTSP_TIME_BUDGET  segundos por invocacion (default 38)
    KTSP_NRUNS        corridas estocasticas (default 10)
    KTSP_BUDGET_SCALE presupuesto DE = scale*n^2 (default 15)
    KTSP_ONLY         lista de instancias separada por comas (opcional)
"""
from __future__ import annotations
import os, sys, json, pickle, time
from pathlib import Path
from typing import List, Tuple
import numpy as np

import instances as inst_mod
from instances import Instance, _distance_matrix, _parse_tsplib
import ktsp_core as core
from ktsp_core import EVAL, METHODS
from metrics import Run

PKG   = Path(os.environ.get("KTSP_PKG", "/tmp/ktsp_pkg/k-TSP"))
TSPDIR= PKG / "INSTANCES" / "TSPLIB"
TABLE = json.load(open(PKG / "ktsp_table.json"))
OUT   = Path(os.environ.get("KTSP_OUT", str(Path(__file__).resolve().parent / "salidas_reales")))
CKPT  = OUT / "results_real"; CKPT.mkdir(parents=True, exist_ok=True)
(OUT / "figuras").mkdir(exist_ok=True)

N_RUNS = int(os.environ.get("KTSP_NRUNS", "10"))
BSCALE = float(os.environ.get("KTSP_BUDGET_SCALE", "15"))
TIME_BUDGET = float(os.environ.get("KTSP_TIME_BUDGET", "38"))
SEED0 = 42

PAPER38 = ("att48 eil51 berlin52 st70 eil76 pr76 kroA100 kroB100 kroC100 kroD100 "
           "kroE100 eil101 lin105 pr107 pr124 bier127 ch130 pr136 gr137 ch150 "
           "kroA150 kroB150 rat195 kroA200 kroB200 ts225 tsp225 pr226 gr229 gil262 "
           "pr264 a280 pr299 lin318 rd400 fl417 pr439 pcb442").split()


def load_instance(name: str) -> Instance:
    text = (TSPDIR / f"{name}.tsp").read_text(errors="ignore")
    coords, D, ewtype = _parse_tsplib(text)
    if D is None:                                  # instancia por coordenadas
        D = _distance_matrix(coords, ewtype)
    return Instance(name=name, n=D.shape[0], D=D, ewtype=ewtype,
                    synthetic=False, coords=coords)


def budget_for(n: int) -> int:
    return int(min(2_000_000, max(20_000, BSCALE * n * n)))


def run_once(mname, fn, D, n, k, q, rid, budget) -> Run:
    tde: List[int] = []; tln: List[float] = []
    def log(de, t, length): tde.append(de); tln.append(length)
    EVAL.reset()
    seed = SEED0 + 100 * q + rid
    kw = dict(home=core.HOME, log=log, budget_de=budget)
    if mname == "Greedy":
        res = fn(D, n, k, restarts=min(n - 1, 40), seed=seed, **kw)
    elif mname == "GRASP":
        res = fn(D, n, k, time_limit=1e9, seed=seed, max_iters=100000, **kw)
    elif mname == "GA":
        res = fn(D, n, k, time_limit=1e9, seed=seed, max_gens=100000, **kw)
    else:
        win = 0 if n <= 200 else min(n - 1, max(150, k + 30))
        res = fn(D, n, k, cand_window=win, **kw)
    de = np.array(tde, float); ln = np.array(tln, float)
    if ln.size: ln = np.minimum.accumulate(ln)
    return Run(mname, "", q, n, rid, de, ln, float(res["length"]))


def process(name) -> bool:
    ck = CKPT / f"{name}.pkl"
    if ck.exists():
        return False
    inst = load_instance(name)
    runs_by_q = {}
    for q in (1, 2, 3):
        info = TABLE[name][str(q)]
        k, ref = int(info["k"]), float(info["ref"])
        if k < 3 or k >= inst.n:
            continue
        budget = budget_for(inst.n)
        runs = []
        for mname, (fn, stoch) in METHODS.items():
            R = N_RUNS if stoch else 1
            for rid in range(R):
                r = run_once(mname, fn, inst.D, inst.n, k, q, rid, budget)
                r.instance = name; runs.append(r)
        runs_by_q[q] = {"runs": runs, "k": k, "ref": ref, "n": inst.n, "ewtype": inst.ewtype}
    with open(ck, "wb") as f:
        pickle.dump(runs_by_q, f)
    return True


def main_process():
    only = os.environ.get("KTSP_ONLY")
    names = only.split(",") if only else PAPER38
    t0 = time.time(); done = 0
    for name in names:
        if (CKPT / f"{name}.pkl").exists():
            continue
        if time.time() - t0 > TIME_BUDGET:
            print(f"[pausa] tiempo agotado; procesadas {done} en esta llamada"); break
        ts = time.time()
        newly = process(name)
        if newly:
            done += 1
            print(f"  OK {name}  ({time.time()-ts:.1f}s)")
    total = sum(1 for n in names if (CKPT / f"{n}.pkl").exists())
    print(f"progreso: {total}/{len(names)} instancias completas")
    return total, len(names)


if __name__ == "__main__":
    if "--aggregate" in sys.argv:
        import aggregate_real
        aggregate_real.run(CKPT, OUT)
    else:
        main_process()
