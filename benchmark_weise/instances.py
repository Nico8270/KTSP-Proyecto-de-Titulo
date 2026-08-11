"""
instances.py
============
Carga de instancias para el benchmark.

Estrategia doble (mismo código en Colab y offline):
  1) `load_tsplib(name)`  -> intenta descargar la instancia TSPLIB real
     (funciona en tu entorno Colab, donde la red está abierta).
  2) `make_synthetic(name, n, seed)` -> instancia euclidiana determinista,
     usada como RESPALDO cuando no hay red (p.ej. en este sandbox) para poder
     validar la maquinaria y generar figuras de forma 100% reproducible.

`build_instance_set(...)` decide automáticamente: usa TSPLIB si hay red, si no
cae a sintéticas con los mismos tamaños. El eje de calidad (error F de Weise) se
mide contra un valor de referencia:
  * el BKS oficial de Helsgaun/Pandiri-Singh si la instancia+cuartil está tabulada,
  * o el mejor valor encontrado por cualquier método/corrida (best-of, se calcula
    en el driver) cuando el óptimo no se conoce (caso sintético).
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

# Fuentes TSPLIB (idénticas a tu notebook)
TSPLIB_SOURCES = [
    "https://raw.githubusercontent.com/mastqe/tsplib/master/{name}.tsp",
    "https://softlib.rice.edu/pub/tsplib/tsp/{name}.tsp.gz",
    "http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/{name}.tsp.gz",
]

# BKS oficiales del k-TSP (Helsgaun / Pandiri & Singh 2020) para las instancias
# pequeñas; usados como referencia de error cuando están disponibles.
OFFICIAL_KTSP: Dict[str, Dict[str, int]] = {
    "burma14":   {"n": 14, "k_q1": 3,  "bks_q1": 359,  "k_q2": 7,  "bks_q2": 1272, "k_q3": 10, "bks_q3": 1642},
    "ulysses16": {"n": 16, "k_q1": 4,  "bks_q1": 935,  "k_q2": 8,  "bks_q2": 1685, "k_q3": 12, "bks_q3": 3183},
    "gr17":      {"n": 17, "k_q1": 4,  "bks_q1": 234,  "k_q2": 8,  "bks_q2": 517,  "k_q3": 12, "bks_q3": 951},
    "gr21":      {"n": 21, "k_q1": 5,  "bks_q1": 324,  "k_q2": 10, "bks_q2": 918,  "k_q3": 15, "bks_q3": 1501},
    "ulysses22": {"n": 22, "k_q1": 5,  "bks_q1": 747,  "k_q2": 11, "bks_q2": 1902, "k_q3": 16, "bks_q3": 2941},
    "gr24":      {"n": 24, "k_q1": 6,  "bks_q1": 264,  "k_q2": 12, "bks_q2": 504,  "k_q3": 18, "bks_q3": 844},
    "fri26":     {"n": 26, "k_q1": 6,  "bks_q1": 243,  "k_q2": 13, "bks_q2": 414,  "k_q3": 19, "bks_q3": 601},
    "bayg29":    {"n": 29, "k_q1": 7,  "bks_q1": 332,  "k_q2": 14, "bks_q2": 626,  "k_q3": 21, "bks_q3": 999},
    "bays29":    {"n": 29, "k_q1": 7,  "bks_q1": 400,  "k_q2": 14, "bks_q2": 733,  "k_q3": 21, "bks_q3": 1194},
    "dantzig42": {"n": 42, "k_q1": 10, "bks_q1": 145,  "k_q2": 21, "bks_q2": 260,  "k_q3": 31, "bks_q3": 427},
    "swiss42":   {"n": 42, "k_q1": 10, "bks_q1": 192,  "k_q2": 21, "bks_q2": 458,  "k_q3": 31, "bks_q3": 760},
    "att48":     {"n": 48, "k_q1": 12, "bks_q1": 1925, "k_q2": 24, "bks_q2": 3603, "k_q3": 36, "bks_q3": 6563},
}


@dataclass
class Instance:
    name: str
    n: int
    D: np.ndarray          # matriz de distancias (n x n)
    ewtype: str
    synthetic: bool
    coords: Optional[np.ndarray] = None

    def k_for(self, quartile: int) -> int:
        """k según el cuartil (Q1~n/4, Q2~n/2, Q3~3n/4), con el k oficial si existe."""
        off = OFFICIAL_KTSP.get(self.name)
        if off is not None and f"k_q{quartile}" in off:
            return int(off[f"k_q{quartile}"])
        frac = {1: 0.25, 2: 0.50, 3: 0.75}[quartile]
        return max(2, min(self.n, int(round(frac * self.n))))

    def bks_for(self, quartile: int) -> Optional[float]:
        off = OFFICIAL_KTSP.get(self.name)
        if off is not None and f"bks_q{quartile}" in off:
            return float(off[f"bks_q{quartile}"])
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Distancias (mismos redondeos que TSPLIB EUC_2D)
# ─────────────────────────────────────────────────────────────────────────────
def _euc2d_matrix(coords: np.ndarray) -> np.ndarray:
    diff = coords[:, None, :] - coords[None, :, :]
    d = np.sqrt((diff ** 2).sum(-1))
    return np.rint(d).astype(float)  # EUC_2D: redondeo al entero más cercano


# ─────────────────────────────────────────────────────────────────────────────
# Instancia sintética determinista (respaldo offline)
# ─────────────────────────────────────────────────────────────────────────────
def make_synthetic(name: str, n: int, seed: int = 12345) -> Instance:
    rng = np.random.default_rng(seed)
    coords = rng.uniform(0, 1000, size=(n, 2))
    D = _euc2d_matrix(coords)
    return Instance(name=name, n=n, D=D, ewtype="EUC_2D", synthetic=True, coords=coords)


# ─────────────────────────────────────────────────────────────────────────────
# TSPLIB real (para Colab / entornos con red)
# ─────────────────────────────────────────────────────────────────────────────
def load_tsplib(name: str) -> Optional[Instance]:
    import gzip
    try:
        import requests
    except Exception:
        return None
    for tpl in TSPLIB_SOURCES:
        url = tpl.format(name=name)
        try:
            r = requests.get(url, timeout=20)
            if r.status_code != 200 or len(r.content) < 50:
                continue
            data = r.content
            if url.endswith(".gz"):
                data = gzip.decompress(data)
            coords, ewtype = _parse_tsplib(data.decode("latin-1"))
            if coords is None:
                continue
            D = _distance_matrix(coords, ewtype)
            return Instance(name=name, n=len(coords), D=D, ewtype=ewtype,
                            synthetic=False, coords=coords)
        except Exception:
            continue
    return None


def _parse_tsplib(text: str) -> Tuple[Optional[np.ndarray], str]:
    ewtype = "EUC_2D"
    lines = text.splitlines()
    coords: List[Tuple[float, float]] = []
    reading = False
    for ln in lines:
        s = ln.strip()
        if s.startswith("EDGE_WEIGHT_TYPE"):
            ewtype = s.split(":")[-1].strip()
        elif s.startswith("NODE_COORD_SECTION"):
            reading = True
        elif s in ("EOF", "") and reading:
            if s == "EOF":
                break
        elif reading:
            parts = s.split()
            if len(parts) >= 3:
                coords.append((float(parts[1]), float(parts[2])))
    if not coords:
        return None, ewtype
    return np.array(coords), ewtype


def _geo_rad(x: float) -> float:
    deg = int(x); mn = x - deg
    return math.pi * (deg + 5.0 * mn / 3.0) / 180.0


def _distance_matrix(coords: np.ndarray, ewtype: str) -> np.ndarray:
    n = len(coords)
    if ewtype == "GEO":
        lat = np.array([_geo_rad(c[0]) for c in coords])
        lon = np.array([_geo_rad(c[1]) for c in coords])
        RRR = 6378.388
        D = np.zeros((n, n))
        for i in range(n):
            q1 = np.cos(lon[i] - lon)
            q2 = np.cos(lat[i] - lat)
            q3 = np.cos(lat[i] + lat)
            dij = RRR * np.arccos(0.5 * ((1 + q1) * q2 - (1 - q1) * q3)) + 1.0
            D[i] = dij.astype(int)
        np.fill_diagonal(D, 0.0)
        return D
    if ewtype == "ATT":
        diff = coords[:, None, :] - coords[None, :, :]
        rij = np.sqrt((diff ** 2).sum(-1) / 10.0)
        tij = np.rint(rij)
        D = np.where(tij < rij, tij + 1, tij)
        np.fill_diagonal(D, 0.0)
        return D.astype(float)
    if ewtype == "CEIL_2D":
        diff = coords[:, None, :] - coords[None, :, :]
        return np.ceil(np.sqrt((diff ** 2).sum(-1))).astype(float)
    return _euc2d_matrix(coords)


# ─────────────────────────────────────────────────────────────────────────────
# Conjunto de instancias del experimento
# ─────────────────────────────────────────────────────────────────────────────
def build_instance_set(specs: List[Tuple[str, int]], prefer_tsplib: bool = True
                        ) -> Tuple[List[Instance], bool]:
    """
    specs: lista de (nombre, n). Intenta TSPLIB real; si no hay red, sintético.
    Devuelve (instancias, usadas_reales).
    """
    insts: List[Instance] = []
    any_real = False
    for name, n in specs:
        inst = load_tsplib(name) if prefer_tsplib else None
        if inst is not None:
            any_real = True
        else:
            inst = make_synthetic(name, n, seed=1000 + abs(hash(name)) % 9000)
        insts.append(inst)
    return insts, any_real
