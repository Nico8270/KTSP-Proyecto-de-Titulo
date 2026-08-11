"""
metrics.py
==========
Métricas del procedimiento de Weise et al. (2014) sobre trazas ANYTIME.

Una "traza" es la lista de log points (de, t, length) de UNA corrida. A partir
de las trazas de muchas corridas se construyen:

  * error normalizado  F = length/ref - 1   (F=0 => óptimo/BKS)   [Weise, sec. II]
  * curvas de progreso : F mediano (sobre corridas) vs DE          [ERT/progress]
  * ERT(F_t)           : Estimated Running Time para alcanzar el error meta F_t
  * ECDF(F_t)          : fracción de corridas que alcanzan F_t a lo largo de DE
  * AUC                : área bajo la curva, para comparar curvas formalmente
  * ranking agregado   : rank por instancia/métrica -> rank global (mediana)

El eje "tiempo" es DE (evaluaciones de distancia), machine-independent. Para
agregar entre instancias de distinto tamaño se escala DE por n^2 (Weise, sec. II).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class Run:
    method: str
    instance: str
    quartile: int
    n: int
    run_id: int
    de: np.ndarray        # evaluaciones de distancia en cada log point (creciente)
    length: np.ndarray    # mejor longitud hasta ese log point (decreciente)
    final_length: float

    @property
    def stochastic(self) -> bool:
        return self.method in ("Greedy", "GRASP", "GA")


def best_length_at(run: Run, de_budget: float) -> float:
    """Mejor longitud alcanzada usando <= de_budget evaluaciones (escalón)."""
    mask = run.de <= de_budget
    if not mask.any():
        return float("inf")
    return float(run.length[mask].min())


def error_at(run: Run, ref: float, de_budget: float) -> float:
    L = best_length_at(run, de_budget)
    if not np.isfinite(L):
        return float("inf")
    return L / ref - 1.0


def de_to_reach(run: Run, ref: float, F_t: float) -> Optional[float]:
    """Primeras DE con las que la corrida alcanza error <= F_t (o None)."""
    target = ref * (1.0 + F_t)
    idx = np.where(run.length <= target + 1e-9)[0]
    if idx.size == 0:
        return None
    return float(run.de[idx[0]])


# ─────────────────────────────────────────────────────────────────────────────
# Rejilla logarítmica de DE
# ─────────────────────────────────────────────────────────────────────────────
def de_grid(runs: List[Run], n_points: int = 60) -> np.ndarray:
    lo = min(float(r.de.min()) for r in runs if r.de.size)
    hi = max(float(r.de.max()) for r in runs if r.de.size)
    lo = max(lo, 1.0)
    return np.unique(np.round(np.logspace(np.log10(lo), np.log10(hi), n_points)))


# ─────────────────────────────────────────────────────────────────────────────
# Curva de progreso: F mediano sobre corridas vs DE
# ─────────────────────────────────────────────────────────────────────────────
def progress_curve(runs: List[Run], ref: float, grid: np.ndarray,
                   q: float = 0.5) -> np.ndarray:
    out = np.full(grid.shape, np.nan)
    for j, de in enumerate(grid):
        errs = [error_at(r, ref, de) for r in runs]
        errs = [e for e in errs if np.isfinite(e)]
        if errs:
            out[j] = np.quantile(errs, q)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# ERT(F_t): tiempo esperado (DE) para alcanzar el error meta
#   ERT = (sum de DE gastadas hasta éxito o hasta el budget) / (#éxitos)
# ─────────────────────────────────────────────────────────────────────────────
def ert(runs: List[Run], ref: float, F_t: float, budget_de: float) -> float:
    total = 0.0; successes = 0
    for r in runs:
        de_hit = de_to_reach(r, ref, F_t)
        if de_hit is not None and de_hit <= budget_de:
            total += de_hit; successes += 1
        else:
            total += budget_de  # corrida fallida aporta el presupuesto completo
    if successes == 0:
        return float("inf")
    return total / successes


# ─────────────────────────────────────────────────────────────────────────────
# ECDF(F_t): fracción de corridas que ya alcanzaron F_t en función de DE
# ─────────────────────────────────────────────────────────────────────────────
def ecdf_curve(runs: List[Run], ref: float, F_t: float, grid: np.ndarray) -> np.ndarray:
    hits = np.array([de_to_reach(r, ref, F_t) for r in runs], dtype=object)
    out = np.zeros(grid.shape)
    for j, de in enumerate(grid):
        reached = sum(1 for h in hits if (h is not None and h <= de))
        out[j] = reached / len(runs)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# AUC sobre eje log(DE). Progreso: menor es mejor. ECDF: mayor es mejor.
# ─────────────────────────────────────────────────────────────────────────────
def auc_log(grid: np.ndarray, y: np.ndarray) -> float:
    x = np.log10(grid)
    valid = ~np.isnan(y)
    if valid.sum() < 2:
        return float("nan")
    return float(np.trapz(y[valid], x[valid]))


# ─────────────────────────────────────────────────────────────────────────────
# Ranking: por instancia/cuartil y métrica se ordenan los métodos; luego se
# agregan por mediana del rank -> ranking global (Weise, sec. II.8).
# ─────────────────────────────────────────────────────────────────────────────
def rank_lower_better(values: Dict[str, float]) -> Dict[str, float]:
    """Rank 1 = mejor (menor valor). Empates -> rank promedio."""
    items = [(m, v) for m, v in values.items()]
    finite = [(m, v) for m, v in items if np.isfinite(v)]
    inf = [m for m, v in items if not np.isfinite(v)]
    finite.sort(key=lambda kv: kv[1])
    ranks: Dict[str, float] = {}
    i = 0
    while i < len(finite):
        j = i
        while j + 1 < len(finite) and abs(finite[j + 1][1] - finite[i][1]) < 1e-12:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        for t in range(i, j + 1):
            ranks[finite[t][0]] = avg
        i = j + 1
    worst = len(finite) + (len(inf) + 1) / 2.0 if inf else len(finite)
    for m in inf:
        ranks[m] = worst
    return ranks


def rank_higher_better(values: Dict[str, float]) -> Dict[str, float]:
    return rank_lower_better({m: -v for m, v in values.items()})


def best_error_on_grid(run: "Run", ref: float, grid_de: np.ndarray) -> np.ndarray:
    """
    Serie best-so-far del error F sobre una rejilla de DE (misma unidad que run.de).
    Función escalón monótona decreciente: en cada DE de la rejilla toma la mejor
    longitud lograda con de <= DE. Para DE por debajo del primer log point usa el
    primer valor logueado (el peor), de modo que la serie queda definida en toda la
    rejilla y su promedio entre corridas es también monótono.
    """
    if run.de.size == 0:
        return np.full(grid_de.shape, np.nan)
    idx = np.searchsorted(run.de, grid_de, side="right") - 1
    idx_clipped = np.clip(idx, 0, run.length.size - 1)
    vals = run.length[idx_clipped].astype(float)
    return vals / ref - 1.0
