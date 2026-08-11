"""
ktsp_core.py
============
Núcleo del k-TSP para el benchmarking estilo Weise et al. (2014),
"Benchmarking Optimization Algorithms: An Open Source Framework for the TSP".

Contiene:
  * primitivas vectorizadas (2-opt, swap in/out, cheapest insertion)
  * los 4 métodos del repositorio original: greedy, GRASP, GA, DCIH (determinista)
  * un contador GLOBAL de EVALUACIONES DE DISTANCIA (DE), medida de tiempo
    MACHINE-INDEPENDENT que Weise recomienda como eje "runtime" reproducible.
  * cada método acepta un callback `log(de, t, length)` que registra "log points"
    ANYTIME (calidad de la mejor solución a lo largo del tiempo), en vez de
    reportar únicamente el resultado final (end-of-run), que es exactamente la
    crítica central del paper de Weise.

Los algoritmos son los MISMOS del notebook `ktsp_corregido_2_0.ipynb`; sólo se
añadió instrumentación (contador DE + log points). Para enchufar tu código
original basta con envolverlo con el mismo patrón de `log(...)`.
"""

from __future__ import annotations
import time, random
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict

import numpy as np

HOME = 0  # ciudad-hogar (depósito). Siempre incluida en el tour.


# ─────────────────────────────────────────────────────────────────────────────
# Contador de evaluaciones de distancia (DE) — el "runtime" machine-independent
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class EvalCounter:
    de: int = 0  # nº de accesos a la matriz de distancias (evaluaciones de distancia)

    def add(self, n) -> None:
        self.de += int(n)

    def reset(self) -> None:
        self.de = 0


EVAL = EvalCounter()

# callback de logging que el runner instala antes de cada corrida
LogFn = Callable[[int, float, float], None]


# ─────────────────────────────────────────────────────────────────────────────
# Primitivas del k-TSP (idénticas al notebook, con conteo de DE añadido)
# ─────────────────────────────────────────────────────────────────────────────
def tour_length(tour, D: np.ndarray) -> float:
    """Longitud del ciclo cerrado sobre los k nodos (vectorizado)."""
    t = np.asarray(tour)
    EVAL.add(len(t))
    return float(D[t, np.roll(t, -1)].sum())


def validate_ktsp(tour, n: int, k: int, home: int = HOME):
    if len(tour) != k:               return False, f"|tour|={len(tour)} != k={k}"
    if home not in tour:             return False, "la ciudad-hogar no esta en el tour"
    if len(set(tour)) != len(tour):  return False, "nodos repetidos"
    if any(not (0 <= v < n) for v in tour): return False, "nodo fuera de rango"
    return True, "OK"


def two_opt_cycle(tour, D, max_passes: int = 40):
    """2-opt vectorizado por NumPy sobre el ciclo (mantiene el subconjunto)."""
    best = list(tour); m = len(best)
    if m < 4: return best
    improved = True; passes = 0
    while improved and passes < max_passes:
        improved = False; passes += 1
        arr = np.asarray(best); nxt = np.roll(arr, -1); d_ab = D[arr, nxt]
        for i in range(m - 1):
            a = arr[i]; b = arr[i + 1]
            js = np.arange(i + 2, m)
            if i == 0:
                js = js[js != m - 1]
            if js.size == 0: continue
            c = arr[js]; d = arr[(js + 1) % m]
            delta = D[a, c] + D[b, d] - d_ab[i] - d_ab[js]
            EVAL.add(2 * js.size)  # dos lookups por candidato
            jmin = int(np.argmin(delta))
            if delta[jmin] < -1e-9:
                j = int(js[jmin])
                best[i + 1:j + 1] = best[i + 1:j + 1][::-1]
                improved = True
                arr = np.asarray(best); nxt = np.roll(arr, -1); d_ab = D[arr, nxt]
    return best


def swap_in_out(tour, D, n, home=HOME):
    """Intercambio dentro/fuera vectorizado: por posicion prueba todos los nodos fuera."""
    inset = np.zeros(n, dtype=bool); inset[np.asarray(tour)] = True
    outside = np.where(~inset)[0]
    if outside.size == 0: return tour, False
    best = list(tour); m = len(best); improved = False
    for pos in range(m):
        node = best[pos]
        if node == home: continue
        a = best[pos - 1]; b = best[(pos + 1) % m]
        cur = D[a, node] + D[node, b]
        cand_cost = D[a, outside] + D[outside, b]
        EVAL.add(2 * outside.size)
        cmin = int(np.argmin(cand_cost))
        if cand_cost[cmin] + 1e-9 < cur:
            new = int(outside[cmin])
            best[pos] = new
            inset[node] = False; inset[new] = True
            outside = np.where(~inset)[0]
            improved = True
    return best, improved


def local_search_ktsp(tour, D, n, home=HOME, max_rounds=8):
    cur = two_opt_cycle(tour, D)
    for _ in range(max_rounds):
        cur, ch = swap_in_out(cur, D, n, home)
        cur = two_opt_cycle(cur, D)
        if not ch: break
    return cur


def _cheapest_insertion_build(D, n, k, home, seed_node, rng=None, cand_limit=80):
    """Construye un tour de k nodos por insercion mas barata desde [home, seed_node]."""
    tour = [home, seed_node]
    inset = np.zeros(n, dtype=bool); inset[home] = True; inset[seed_node] = True
    while len(tour) < k:
        outside = np.where(~inset)[0]
        if outside.size == 0: break
        cand = outside
        if rng is not None and outside.size > cand_limit:
            cand = np.array(rng.sample(list(outside), cand_limit))
        arr = np.asarray(tour); nxt = np.roll(arr, -1)
        A = arr; B = nxt
        dab = D[A, B]
        dac = D[np.ix_(cand, A)]
        dcb = D[np.ix_(cand, B)]
        delta = dac + dcb - dab[None, :]
        EVAL.add(delta.size + dab.size)
        flat = int(np.argmin(delta))
        ci, ei = divmod(flat, delta.shape[1])
        node = int(cand[ci]); pos = ei + 1
        tour.insert(pos, node); inset[node] = True
    return tour


# ─────────────────────────────────────────────────────────────────────────────
# Métodos instrumentados (mismo comportamiento; añaden log points anytime)
#   Cada uno acepta:
#     log: callback log(de, t, length) invocado al mejorar la mejor solución
#     budget_de: presupuesto opcional en evaluaciones de distancia (corta la corrida)
#   y devuelve dict {tour, length, source}.
# ─────────────────────────────────────────────────────────────────────────────
def _mk_logger(log: Optional[LogFn], t0: float):
    def _emit(length: float):
        if log is not None:
            log(EVAL.de, time.perf_counter() - t0, float(length))
    return _emit


def greedy_ktsp(D, n, k, home=HOME, restarts=5, seed=42,
                log: Optional[LogFn] = None, budget_de: Optional[int] = None):
    t0 = time.perf_counter(); emit = _mk_logger(log, t0)
    best_tour, best_len = None, float("inf")
    order = np.argsort(D[home])
    seeds = [int(v) for v in order if v != home][:max(1, restarts)]
    for s in seeds:
        built = _cheapest_insertion_build(D, n, k, home, s)
        emit(tour_length(built, D))            # punto anytime: construido (pre-LS)
        tour = local_search_ktsp(built, D, n, home)
        L = tour_length(tour, D)
        if L < best_len:
            best_tour, best_len = tour, L
        emit(L)                                 # punto anytime: tras cada restart
        if budget_de is not None and EVAL.de >= budget_de:
            break
    return {"tour": best_tour, "length": best_len, "source": "greedy_insertion+LS"}


def grasp_ktsp(D, n, k, home=HOME, time_limit=3.0, seed=42,
               log: Optional[LogFn] = None, budget_de: Optional[int] = None,
               max_iters: int = 10_000):
    t0 = time.perf_counter(); emit = _mk_logger(log, t0)
    rng = random.Random(seed + 1)
    best_tour, best_len = None, float("inf")
    others = [v for v in range(n) if v != home]
    it = 0
    while it < max_iters:
        it += 1
        noise = np.array([rng.random() for _ in range(len(others))])
        score = D[home, others] * (0.7 + 0.6 * noise)
        idx = np.argsort(score)
        chosen = [home] + [others[i] for i in idx[:k - 1]]
        tour = local_search_ktsp(chosen, D, n, home)
        L = tour_length(tour, D)
        if L < best_len:
            best_tour, best_len = tour, L
        emit(L)                                 # punto anytime en cada iteración
        stop_time = (time.perf_counter() - t0) >= time_limit
        stop_de = budget_de is not None and EVAL.de >= budget_de
        if stop_time or stop_de:
            break
    if best_tour is None:
        best_tour = local_search_ktsp([home] + others[:k - 1], D, n, home)
        best_len = tour_length(best_tour, D); emit(best_len)
    return {"tour": best_tour, "length": best_len, "source": "GRASP_multistart+LS"}


def ga_ktsp(D, n, k, home=HOME, pop_size=30, time_limit=4.0, seed=42,
            log: Optional[LogFn] = None, budget_de: Optional[int] = None,
            max_gens: int = 100_000):
    t0 = time.perf_counter(); emit = _mk_logger(log, t0)
    rng = random.Random(seed + 2)
    others = [v for v in range(n) if v != home]

    def random_indiv():
        return [home] + rng.sample(others, k - 1)

    def fitness(ind):
        return tour_length(ind, D)

    def crossover(p1, p2):
        keep = set([home]) | set(rng.sample(p1[1:], (k - 1) // 2))
        child = [home] + [v for v in p1[1:] if v in keep]
        for v in p2[1:]:
            if len(child) >= k: break
            if v not in keep: child.append(v); keep.add(v)
        pool = [v for v in others if v not in keep]; rng.shuffle(pool)
        while len(child) < k: child.append(pool.pop())
        return child

    def mutate(ind, pm=0.3):
        ind = ind[:]
        if rng.random() < pm:
            i, j = rng.sample(range(1, k), 2); ind[i], ind[j] = ind[j], ind[i]
        if rng.random() < pm:
            inset = set(ind); outside = [v for v in others if v not in inset]
            if outside:
                pos = rng.randrange(1, k); ind[pos] = rng.choice(outside)
        return ind

    pop = [random_indiv() for _ in range(pop_size)]
    pop[0] = local_search_ktsp(pop[0], D, n, home)
    pop.sort(key=fitness)
    best_len = fitness(pop[0]); emit(best_len)
    gens = 0
    while gens < max_gens:
        gens += 1
        new = pop[:max(2, pop_size // 5)]
        while len(new) < pop_size:
            a = min(rng.sample(pop, 3), key=fitness)
            b = min(rng.sample(pop, 3), key=fitness)
            child = mutate(crossover(a, b))
            if rng.random() < 0.25:
                child = local_search_ktsp(child, D, n, home)
            new.append(child)
        pop = sorted(new, key=fitness)[:pop_size]
        cur = fitness(pop[0])
        if cur < best_len:
            best_len = cur
        emit(cur)                               # punto anytime en cada generación
        stop_time = (time.perf_counter() - t0) >= time_limit
        stop_de = budget_de is not None and EVAL.de >= budget_de
        if stop_time or stop_de:
            break
    best = local_search_ktsp(pop[0], D, n, home)
    L = tour_length(best, D)
    if L < best_len:
        best_len = L; emit(best_len)
    return {"tour": best, "length": tour_length(best, D), "source": "GA_subset+order+LS"}


def nbr_ktsp(D, n, k, home=HOME, cand_window=0,
             log: Optional[LogFn] = None, budget_de: Optional[int] = None):
    """DCIH — heuristica propia DETERMINISTA (mismos datos => mismo tour). (funcion: nbr_ktsp)"""
    t0 = time.perf_counter(); emit = _mk_logger(log, t0)
    pool_all = np.array([v for v in range(n) if v != home])
    if cand_window:
        eff = max(cand_window, k - 1)
        if eff < pool_all.size:
            order = np.argsort(D[home, pool_all])
            pool_all = pool_all[order[:eff]]
    pool = set(int(v) for v in pool_all)

    second = min(pool, key=lambda v: (D[home, v], v))
    tour = [home, second]; pool.discard(second)
    while len(tour) < k and pool:
        cand = np.array(sorted(pool))
        arr = np.asarray(tour); nxt = np.roll(arr, -1)
        dab = D[arr, nxt]
        dac = D[np.ix_(cand, arr)]
        dcb = D[np.ix_(cand, nxt)]
        delta = dac + dcb - dab[None, :]
        EVAL.add(delta.size + dab.size)
        m = delta.shape[1]
        flat = np.argsort(delta, axis=None, kind="stable")[0]
        ci, ei = divmod(int(flat), m)
        node = int(cand[ci]); pos = ei + 1
        tour.insert(pos, node); pool.discard(node)
    emit(tour_length(tour, D))  # log point tras la fase constructiva

    cur = two_opt_cycle(tour, D)
    for _ in range(12):
        cur, ch = swap_in_out(cur, D, n, home)
        cur = two_opt_cycle(cur, D)
        if not ch:
            break

    if len(cur) < k:
        present = set(cur)
        rest = [v for v in range(n) if v not in present]
        rest.sort(key=lambda v: (float(np.min(D[v, cur])), v))
        for v in rest:
            if len(cur) >= k: break
            arr = np.asarray(cur); nxt = np.roll(arr, -1)
            delta = D[v, arr] + D[v, nxt] - D[arr, nxt]
            pos = int(np.argmin(delta)) + 1
            cur.insert(pos, v)
        cur = two_opt_cycle(cur, D)

    L = tour_length(cur, D); emit(L)  # log point tras el refinamiento
    return {"tour": cur, "length": L,
            "source": "DCIH_deterministic"}


# Registro de metodos (nombre visible -> (fn, es_estocastico))
METHODS = {
    "Greedy": (greedy_ktsp, True),
    "GRASP":  (grasp_ktsp,  True),
    "GA":     (ga_ktsp,     True),
    "DCIH":   (nbr_ktsp,    False),  # heuristica determinista propuesta (paper: DCIH)
}
