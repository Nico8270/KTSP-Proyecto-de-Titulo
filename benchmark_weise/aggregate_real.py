"""aggregate_real.py — carga los checkpoints por instancia y genera figuras + tablas."""
from __future__ import annotations
import os, pickle, json
from pathlib import Path
import numpy as np, pandas as pd


def run(ckpt_dir: Path, out_dir: Path):
    ckpt_dir = Path(ckpt_dir); out_dir = Path(out_dir)
    # apuntar los globals de run_benchmark a esta carpeta ANTES de importarlo
    os.environ["KTSP_OUT"] = str(out_dir)
    import importlib, run_benchmark as RB
    importlib.reload(RB)

    all_runs = {}; refs = {}
    for pk in sorted(ckpt_dir.glob("*.pkl")):
        data = pickle.load(open(pk, "rb"))
        for q, blob in data.items():
            key = (pk.stem, int(q))
            all_runs[key] = blob["runs"]
            refs[key] = (float(blob["ref"]), "LKH-3_oficial")

    if not all_runs:
        print("sin checkpoints"); return

    method_names = list(RB.METHODS.keys())

    # resumen de GAP finales
    rows = []
    for (name, q), runs in all_runs.items():
        ref = refs[(name, q)][0]
        n = runs[0].n
        for m in method_names:
            mr = [r for r in runs if r.method == m]
            finals = np.array([r.final_length for r in mr])
            gap = 100.0 * (finals / ref - 1.0)
            rows.append({"Instancia": name, "n": n, "Quartil": q, "Metodo": m,
                         "Ref_LKH3": ref, "GAP_min%": round(float(gap.min()), 3),
                         "GAP_med%": round(float(np.median(gap)), 3),
                         "Len_best": round(float(finals.min()), 2), "corridas": len(mr)})
    pd.DataFrame(rows).to_csv(out_dir / "resumen_gaps.csv", index=False)

    RB.make_all_figures(all_runs, refs, method_names)
    ert_df, rank_df = RB.compute_tables(all_runs, refs, method_names)
    ert_df.to_csv(out_dir / "ert_por_instancia.csv", index=False)
    rank_df.to_csv(out_dir / "ranking_global.csv", index=False)

    # tabla de GAP promedio por metodo y cuartil (estilo tabla del paper)
    df = pd.DataFrame(rows)
    piv = (df.groupby(["Metodo", "Quartil"])["GAP_med%"].mean().unstack()
           .reindex(method_names))
    piv.to_csv(out_dir / "gap_promedio_por_cuartil.csv")

    meta = {"instancias": sorted({k[0] for k in all_runs}),
            "n_instancias": len({k[0] for k in all_runs}),
            "referencia": "valor LKH-3 del paquete oficial k-TSP (Pandiri & Singh / Helsgaun)"}
    (out_dir / "manifest_real.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print("=== GAP medio (%) por metodo y cuartil ==="); print(piv.round(2).to_string())
    print("\n=== Ranking global ==="); print(rank_df.to_string(index=False))
    print(f"\n{meta['n_instancias']} instancias agregadas. Salidas en {out_dir}")
