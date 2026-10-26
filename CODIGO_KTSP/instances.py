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
    "burma14": {"n": 14, "k_q1": 3, "bks_q1": 359, "k_q2": 7, "bks_q2": 1272, "k_q3": 10, "bks_q3": 1642},
    "ulysses16": {"n": 16, "k_q1": 4, "bks_q1": 935, "k_q2": 8, "bks_q2": 1685, "k_q3": 12, "bks_q3": 3183},
    "gr17": {"n": 17, "k_q1": 4, "bks_q1": 234, "k_q2": 8, "bks_q2": 517, "k_q3": 12, "bks_q3": 951},
    "gr21": {"n": 21, "k_q1": 5, "bks_q1": 324, "k_q2": 10, "bks_q2": 918, "k_q3": 15, "bks_q3": 1501},
    "ulysses22": {"n": 22, "k_q1": 5, "bks_q1": 747, "k_q2": 11, "bks_q2": 1902, "k_q3": 16, "bks_q3": 2941},
    "gr24": {"n": 24, "k_q1": 6, "bks_q1": 264, "k_q2": 12, "bks_q2": 504, "k_q3": 18, "bks_q3": 844},
    "fri26": {"n": 26, "k_q1": 6, "bks_q1": 243, "k_q2": 13, "bks_q2": 414, "k_q3": 19, "bks_q3": 601},
    "bayg29": {"n": 29, "k_q1": 7, "bks_q1": 332, "k_q2": 14, "bks_q2": 626, "k_q3": 21, "bks_q3": 999},
    "bays29": {"n": 29, "k_q1": 7, "bks_q1": 400, "k_q2": 14, "bks_q2": 733, "k_q3": 21, "bks_q3": 1194},
    "dantzig42": {"n": 42, "k_q1": 10, "bks_q1": 145, "k_q2": 21, "bks_q2": 260, "k_q3": 31, "bks_q3": 427},
    "swiss42": {"n": 42, "k_q1": 10, "bks_q1": 192, "k_q2": 21, "bks_q2": 458, "k_q3": 31, "bks_q3": 760},
    "att48": {"n": 48, "k_q1": 12, "bks_q1": 1925, "k_q2": 24, "bks_q2": 3603, "k_q3": 36, "bks_q3": 6563},
    "gr48": {"n": 48, "k_q1": 12, "bks_q1": 874, "k_q2": 24, "bks_q2": 1819, "k_q3": 36, "bks_q3": 3104},
    "hk48": {"n": 48, "k_q1": 12, "bks_q1": 2827, "k_q2": 24, "bks_q2": 4701, "k_q3": 36, "bks_q3": 7278},
    "eil51": {"n": 51, "k_q1": 12, "bks_q1": 82, "k_q2": 25, "bks_q2": 175, "k_q3": 38, "bks_q3": 287},
    "berlin52": {"n": 52, "k_q1": 13, "bks_q1": 679, "k_q2": 26, "bks_q2": 1874, "k_q3": 39, "bks_q3": 4174},
    "brazil58": {"n": 58, "k_q1": 14, "bks_q1": 4965, "k_q2": 29, "bks_q2": 7978, "k_q3": 43, "bks_q3": 11614},
    "st70": {"n": 70, "k_q1": 17, "bks_q1": 120, "k_q2": 35, "bks_q2": 260, "k_q3": 52, "bks_q3": 428},
    "eil76": {"n": 76, "k_q1": 19, "bks_q1": 102, "k_q2": 38, "bks_q2": 213, "k_q3": 57, "bks_q3": 335},
    "pr76": {"n": 76, "k_q1": 19, "bks_q1": 23450, "k_q2": 38, "bks_q2": 41248, "k_q3": 57, "bks_q3": 64142},
    "gr96": {"n": 96, "k_q1": 24, "bks_q1": 10460, "k_q2": 48, "bks_q2": 20688, "k_q3": 72, "bks_q3": 31343},
    "rat99": {"n": 99, "k_q1": 24, "bks_q1": 284, "k_q2": 49, "bks_q2": 573, "k_q3": 74, "bks_q3": 857},
    "kroA100": {"n": 100, "k_q1": 25, "bks_q1": 4931, "k_q2": 50, "bks_q2": 9184, "k_q3": 75, "bks_q3": 14379},
    "kroB100": {"n": 100, "k_q1": 25, "bks_q1": 4305, "k_q2": 50, "bks_q2": 9096, "k_q3": 75, "bks_q3": 14680},
    "kroC100": {"n": 100, "k_q1": 25, "bks_q1": 4964, "k_q2": 50, "bks_q2": 9457, "k_q3": 75, "bks_q3": 13892},
    "kroD100": {"n": 100, "k_q1": 25, "bks_q1": 4762, "k_q2": 50, "bks_q2": 8719, "k_q3": 75, "bks_q3": 14058},
    "kroE100": {"n": 100, "k_q1": 25, "bks_q1": 3905, "k_q2": 50, "bks_q2": 9097, "k_q3": 75, "bks_q3": 14622},
    "rd100": {"n": 100, "k_q1": 25, "bks_q1": 1438, "k_q2": 50, "bks_q2": 3168, "k_q3": 75, "bks_q3": 5094},
    "eil101": {"n": 101, "k_q1": 25, "bks_q1": 107, "k_q2": 50, "bks_q2": 227, "k_q3": 75, "bks_q3": 386},
    "lin105": {"n": 105, "k_q1": 26, "bks_q1": 2606, "k_q2": 52, "bks_q2": 5848, "k_q3": 78, "bks_q3": 8983},
    "pr107": {"n": 107, "k_q1": 26, "bks_q1": 8443, "k_q2": 53, "bks_q2": 18028, "k_q3": 80, "bks_q3": 36292},
    "gr120": {"n": 120, "k_q1": 30, "bks_q1": 1308, "k_q2": 60, "bks_q2": 2669, "k_q3": 90, "bks_q3": 4325},
    "pr124": {"n": 124, "k_q1": 31, "bks_q1": 14325, "k_q2": 62, "bks_q2": 22998, "k_q3": 93, "bks_q3": 39008},
    "bier127": {"n": 127, "k_q1": 31, "bks_q1": 10619, "k_q2": 63, "bks_q2": 25761, "k_q3": 95, "bks_q3": 49680},
    "ch130": {"n": 130, "k_q1": 32, "bks_q1": 1130, "k_q2": 65, "bks_q2": 2408, "k_q3": 97, "bks_q3": 3876},
    "pr136": {"n": 136, "k_q1": 34, "bks_q1": 21116, "k_q2": 68, "bks_q2": 46414, "k_q3": 102, "bks_q3": 67910},
    "gr137": {"n": 137, "k_q1": 34, "bks_q1": 17399, "k_q2": 68, "bks_q2": 29231, "k_q3": 102, "bks_q3": 43670},
    "pr144": {"n": 144, "k_q1": 36, "bks_q1": 14327, "k_q2": 72, "bks_q2": 27424, "k_q3": 108, "bks_q3": 41194},
    "ch150": {"n": 150, "k_q1": 37, "bks_q1": 1276, "k_q2": 75, "bks_q2": 2760, "k_q3": 112, "bks_q3": 4366},
    "kroA150": {"n": 150, "k_q1": 37, "bks_q1": 5690, "k_q2": 75, "bks_q2": 11496, "k_q3": 112, "bks_q3": 17395},
    "kroB150": {"n": 150, "k_q1": 37, "bks_q1": 5812, "k_q2": 75, "bks_q2": 11357, "k_q3": 112, "bks_q3": 16879},
    "pr152": {"n": 152, "k_q1": 38, "bks_q1": 20029, "k_q2": 76, "bks_q2": 36333, "k_q3": 114, "bks_q3": 51826},
    "u159": {"n": 159, "k_q1": 39, "bks_q1": 8983, "k_q2": 79, "bks_q2": 18323, "k_q3": 119, "bks_q3": 27096},
    "si175": {"n": 175, "k_q1": 43, "bks_q1": 4873, "k_q2": 87, "bks_q2": 10087, "k_q3": 131, "bks_q3": 15460},
    "brg180": {"n": 180, "k_q1": 45, "bks_q1": 500, "k_q2": 90, "bks_q2": 980, "k_q3": 135, "bks_q3": 1480},
    "rat195": {"n": 195, "k_q1": 48, "bks_q1": 554, "k_q2": 97, "bks_q2": 1100, "k_q3": 146, "bks_q3": 1667},
    "d198": {"n": 198, "k_q1": 49, "bks_q1": 4964, "k_q2": 99, "bks_q2": 6921, "k_q3": 148, "bks_q3": 9093},
    "kroA200": {"n": 200, "k_q1": 50, "bks_q1": 6154, "k_q2": 100, "bks_q2": 12372, "k_q3": 150, "bks_q3": 19211},
    "kroB200": {"n": 200, "k_q1": 50, "bks_q1": 6016, "k_q2": 100, "bks_q2": 12338, "k_q3": 150, "bks_q3": 18898},
    "gr202": {"n": 202, "k_q1": 50, "bks_q1": 8142, "k_q2": 101, "bks_q2": 13790, "k_q3": 151, "bks_q3": 20927},
    "ts225": {"n": 225, "k_q1": 56, "bks_q1": 28828, "k_q2": 112, "bks_q2": 56828, "k_q3": 168, "bks_q3": 85656},
    "tsp225": {"n": 225, "k_q1": 56, "bks_q1": 913, "k_q2": 112, "bks_q2": 1708, "k_q3": 168, "bks_q3": 2624},
    "pr226": {"n": 226, "k_q1": 56, "bks_q1": 20033, "k_q2": 113, "bks_q2": 36720, "k_q3": 169, "bks_q3": 47142},
    "gr229": {"n": 229, "k_q1": 57, "bks_q1": 18555, "k_q2": 114, "bks_q2": 39618, "k_q3": 171, "bks_q3": 64457},
    "gil262": {"n": 262, "k_q1": 65, "bks_q1": 541, "k_q2": 131, "bks_q2": 993, "k_q3": 196, "bks_q3": 1551},
    "pr264": {"n": 264, "k_q1": 66, "bks_q1": 9232, "k_q2": 132, "bks_q2": 22644, "k_q3": 198, "bks_q3": 34346},
    "a280": {"n": 280, "k_q1": 70, "bks_q1": 649, "k_q2": 140, "bks_q2": 1231, "k_q3": 210, "bks_q3": 1845},
    "pr299": {"n": 299, "k_q1": 74, "bks_q1": 11077, "k_q2": 149, "bks_q2": 22390, "k_q3": 224, "bks_q3": 32738},
    "lin318": {"n": 318, "k_q1": 79, "bks_q1": 8544, "k_q2": 159, "bks_q2": 15916, "k_q3": 238, "bks_q3": 25303},
    "rd400": {"n": 400, "k_q1": 100, "bks_q1": 3091, "k_q2": 200, "bks_q2": 6350, "k_q3": 300, "bks_q3": 9972},
    "fl417": {"n": 417, "k_q1": 104, "bks_q1": 1831, "k_q2": 208, "bks_q2": 5436, "k_q3": 312, "bks_q3": 7930},
    "gr431": {"n": 431, "k_q1": 107, "bks_q1": 14525, "k_q2": 215, "bks_q2": 34985, "k_q3": 323, "bks_q3": 73921},
    "pr439": {"n": 439, "k_q1": 109, "bks_q1": 19751, "k_q2": 219, "bks_q2": 35404, "k_q3": 329, "bks_q3": 58006},
    "pcb442": {"n": 442, "k_q1": 110, "bks_q1": 10932, "k_q2": 221, "bks_q2": 22537, "k_q3": 331, "bks_q3": 34358},
    "d493": {"n": 493, "k_q1": 123, "bks_q1": 9356, "k_q2": 246, "bks_q2": 13574, "k_q3": 369, "bks_q3": 20931},
    "att532": {"n": 532, "k_q1": 133, "bks_q1": 3812, "k_q2": 266, "bks_q2": 8978, "k_q3": 399, "bks_q3": 16360},
    "ali535": {"n": 535, "k_q1": 133, "bks_q1": 11773, "k_q2": 267, "bks_q2": 42563, "k_q3": 401, "bks_q3": 89316},
    "si535": {"n": 535, "k_q1": 133, "bks_q1": 10839, "k_q2": 267, "bks_q2": 22327, "k_q3": 401, "bks_q3": 34320},
    "pa561": {"n": 561, "k_q1": 140, "bks_q1": 465, "k_q2": 280, "bks_q2": 1035, "k_q3": 420, "bks_q3": 1745},
    "u574": {"n": 574, "k_q1": 143, "bks_q1": 7584, "k_q2": 287, "bks_q2": 14858, "k_q3": 430, "bks_q3": 23616},
    "rat575": {"n": 575, "k_q1": 143, "bks_q1": 1572, "k_q2": 287, "bks_q2": 3120, "k_q3": 431, "bks_q3": 4730},
    "p654": {"n": 654, "k_q1": 163, "bks_q1": 6929, "k_q2": 327, "bks_q2": 16174, "k_q3": 490, "bks_q3": 21446},
    "d657": {"n": 657, "k_q1": 164, "bks_q1": 11116, "k_q2": 328, "bks_q2": 20946, "k_q3": 492, "bks_q3": 32119},
    "gr666": {"n": 666, "k_q1": 166, "bks_q1": 26381, "k_q2": 333, "bks_q2": 76925, "k_q3": 499, "bks_q3": 146122},
    "u724": {"n": 724, "k_q1": 181, "bks_q1": 8709, "k_q2": 362, "bks_q2": 16799, "k_q3": 543, "bks_q3": 27469},
    "rat783": {"n": 783, "k_q1": 195, "bks_q1": 2004, "k_q2": 391, "bks_q2": 4008, "k_q3": 587, "bks_q3": 6160},
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
            coords, D, ewtype = _parse_tsplib(data.decode("latin-1"))
            if D is None and coords is None:
                continue
            if D is None:                         # instancia por coordenadas
                D = _distance_matrix(coords, ewtype)
            n = D.shape[0]
            return Instance(name=name, n=n, D=D, ewtype=ewtype,
                            synthetic=False, coords=coords)
        except Exception:
            continue
    return None


def _parse_tsplib(text: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], str]:
    """Devuelve (coords, D, ewtype).

    - Instancias por coordenadas (EUC_2D/GEO/ATT/CEIL_2D): coords != None, D None.
    - Instancias EXPLICIT (matriz de distancias): coords None, D != None.
    """
    ewtype = "EUC_2D"
    ewformat = ""
    dim = None
    lines = text.splitlines()
    coords: List[Tuple[float, float]] = []
    weights: List[float] = []
    section = None                                # None | "COORD" | "WEIGHT"
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        up = s.upper()
        if up.startswith("DIMENSION"):
            try:
                dim = int(s.split(":")[-1].strip())
            except ValueError:
                pass
            continue
        if up.startswith("EDGE_WEIGHT_TYPE"):
            ewtype = s.split(":")[-1].strip(); continue
        if up.startswith("EDGE_WEIGHT_FORMAT"):
            ewformat = s.split(":")[-1].strip().upper(); continue
        if up.startswith("NODE_COORD_SECTION") or up.startswith("DISPLAY_DATA_SECTION"):
            section = "COORD"; continue
        if up.startswith("EDGE_WEIGHT_SECTION"):
            section = "WEIGHT"; continue
        if up in ("EOF",) or up.endswith("_SECTION"):
            if up == "EOF":
                break
            section = None if not up.startswith("EDGE_WEIGHT") else section
            continue
        if section == "COORD":
            parts = s.split()
            if len(parts) >= 3:
                try:
                    coords.append((float(parts[1]), float(parts[2])))
                except ValueError:
                    pass
        elif section == "WEIGHT":
            for tok in s.split():
                try:
                    weights.append(float(tok))
                except ValueError:
                    pass

    if ewtype.upper() == "EXPLICIT" and weights:
        D = _explicit_matrix(weights, dim, ewformat)
        if D is not None:
            return None, D, ewtype
    if coords:
        return np.array(coords), None, ewtype
    return None, None, ewtype


def _explicit_matrix(weights: List[float], dim: Optional[int], fmt: str
                     ) -> Optional[np.ndarray]:
    """Reconstruye la matriz n x n desde EDGE_WEIGHT_SECTION según el formato."""
    w = np.asarray(weights, float)
    fmt = (fmt or "").upper()
    # inferir n si no hay DIMENSION fiable
    def tri_n(count, with_diag):
        # count = n(n+1)/2 (con diag) o n(n-1)/2 (sin diag)
        import math as _m
        if with_diag:
            return int((-1 + _m.isqrt(1 + 8 * count)) // 2)
        return int((1 + _m.isqrt(1 + 8 * count)) // 2)
    n = dim
    if fmt == "FULL_MATRIX":
        if n is None:
            n = int(round(len(w) ** 0.5))
        return w[: n * n].reshape(n, n)
    D = None
    if fmt in ("UPPER_ROW", "LOWER_ROW"):           # sin diagonal
        if n is None:
            n = tri_n(len(w), with_diag=False)
        D = np.zeros((n, n))
        idx = 0
        if fmt == "UPPER_ROW":
            for i in range(n):
                for j in range(i + 1, n):
                    D[i, j] = D[j, i] = w[idx]; idx += 1
        else:  # LOWER_ROW
            for i in range(1, n):
                for j in range(i):
                    D[i, j] = D[j, i] = w[idx]; idx += 1
    elif fmt in ("UPPER_DIAG_ROW", "LOWER_DIAG_ROW", ""):  # con diagonal (defecto)
        if n is None:
            n = tri_n(len(w), with_diag=True)
        D = np.zeros((n, n))
        idx = 0
        if fmt == "UPPER_DIAG_ROW" or fmt == "":
            for i in range(n):
                for j in range(i, n):
                    D[i, j] = D[j, i] = w[idx]; idx += 1
        else:  # LOWER_DIAG_ROW
            for i in range(n):
                for j in range(i + 1):
                    D[i, j] = D[j, i] = w[idx]; idx += 1
    return D


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
