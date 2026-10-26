#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wilcoxon signed-rank analysis for the k-TSP comparison.

Reads a per-instance results CSV with columns "<Method>_GAP%" (one row per
instance x quartile) and runs the paired Wilcoxon signed-rank test between
methods on the paired GAP% values. It produces:

  - wilcoxon_pairs.csv  : full pairwise table (p-value, better method, effect)
  - wilcoxon_matrix.csv : symmetric matrix of p-values
  - wilcoxon_vs_best.csv: each method vs. the best method (by mean GAP%)
  - wilcoxon_vs_best.tex : LaTeX table (IEEE-ready) for the paper/thesis

The Wilcoxon signed-rank test is the non-parametric paired test recommended by
Derrac et al. (2011) for comparing two algorithms over many instances without
assuming normality. H0: the two methods have the same median GAP%.

Usage:
    python wilcoxon_test.py [results.csv] [--alpha 0.05] [--outdir .]
Default results file: comparacion_9metodos.csv
"""
import argparse
import itertools
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

DEFAULT_CSV = "comparacion_9metodos.csv"


def load_gaps(csv_path):
    """Return (DataFrame of GAP% columns indexed by case, list of methods)."""
    df = pd.read_csv(csv_path)
    gap_cols = [c for c in df.columns if c.endswith("_GAP%")]
    if not gap_cols:
        sys.exit(f"No '<Method>_GAP%' columns found in {csv_path}.")
    methods = [c[:-len("_GAP%")] for c in gap_cols]
    gaps = df[gap_cols].copy()
    gaps.columns = methods
    # Drop rows with any missing value so every pair is tested on common cases.
    gaps = gaps.dropna(how="any").reset_index(drop=True)
    return gaps, methods


def paired_wilcoxon(a, b):
    """Two-sided Wilcoxon on paired samples. Returns (statistic, p-value).

    If every paired difference is zero the test is undefined; return p=1.0.
    """
    diff = np.asarray(a, float) - np.asarray(b, float)
    if np.allclose(diff, 0.0):
        return 0.0, 1.0
    # zero_method="wilcox" discards zero-differences, the classic definition.
    try:
        stat, p = wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
    except ValueError:
        # Happens when all non-zero diffs share a sign and n is tiny; fall back.
        stat, p = wilcoxon(a, b, zero_method="zsplit", alternative="two-sided")
    return float(stat), float(p)


def main():
    ap = argparse.ArgumentParser(description="Wilcoxon signed-rank analysis for k-TSP.")
    ap.add_argument("csv", nargs="?", default=DEFAULT_CSV, help="results CSV")
    ap.add_argument("--alpha", type=float, default=0.05, help="significance level")
    ap.add_argument("--outdir", default=".", help="output directory")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        sys.exit(f"Results file not found: {args.csv}")
    os.makedirs(args.outdir, exist_ok=True)

    gaps, methods = load_gaps(args.csv)
    n_cases = len(gaps)
    means = gaps.mean().sort_values()
    best = means.index[0]
    print(f"Cases (instance x quartile): {n_cases}")
    print(f"Methods ({len(methods)}): {', '.join(methods)}")
    print(f"Best mean GAP%: {best} ({means[best]:.3f}%)\n")

    # --- Full pairwise table ---------------------------------------------
    rows = []
    mat = pd.DataFrame(np.ones((len(methods), len(methods))),
                       index=methods, columns=methods)
    for m1, m2 in itertools.combinations(methods, 2):
        stat, p = paired_wilcoxon(gaps[m1], gaps[m2])
        md = gaps[m1].mean() - gaps[m2].mean()
        better = m1 if md < 0 else m2
        rows.append({
            "A": m1, "B": m2,
            "mean_A": round(gaps[m1].mean(), 3),
            "mean_B": round(gaps[m2].mean(), 3),
            "statistic": round(stat, 1),
            "p_value": p,
            "significant": p < args.alpha,
            "better": better if p < args.alpha else "ns",
        })
        mat.loc[m1, m2] = p
        mat.loc[m2, m1] = p
    pairs = pd.DataFrame(rows).sort_values("p_value").reset_index(drop=True)
    pairs.to_csv(os.path.join(args.outdir, "wilcoxon_pairs.csv"), index=False)
    mat.round(6).to_csv(os.path.join(args.outdir, "wilcoxon_matrix.csv"))

    # --- Each method vs. the best ----------------------------------------
    vb = []
    for m in means.index:
        if m == best:
            continue
        stat, p = paired_wilcoxon(gaps[best], gaps[m])
        vb.append({
            "method": m,
            "mean_GAP%": round(means[m], 3),
            "delta_vs_best": round(means[m] - means[best], 3),
            "p_value": p,
            "significant": "yes" if p < args.alpha else "no",
        })
    vsbest = pd.DataFrame(vb)
    vsbest.to_csv(os.path.join(args.outdir, "wilcoxon_vs_best.csv"), index=False)

    # --- LaTeX table (vs. best) ------------------------------------------
    def fmt_p(p):
        return "$<$0.001" if p < 1e-3 else f"{p:.3f}"

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Wilcoxon signed-rank test of each method against the best "
        r"method (%s), paired on the per-instance GAP\%% over all %d cases. "
        r"$p<%.2f$ indicates a statistically significant difference.}"
        % (best, n_cases, args.alpha),
        r"\label{tab:wilcoxon}",
        r"\begin{tabular}{lrrcc}",
        r"\hline",
        r"Method & Mean GAP\% & $\Delta$ vs.\ best & $p$-value & Sig. \\",
        r"\hline",
        r"\textbf{%s} & \textbf{%.2f} & --- & --- & --- \\" % (best, means[best]),
    ]
    for r in vb:
        lines.append(
            r"%s & %.2f & %+.2f & %s & %s \\"
            % (r["method"], r["mean_GAP%"], r["delta_vs_best"],
               fmt_p(r["p_value"]), r["significant"])
        )
    lines += [r"\hline", r"\end{tabular}", r"\end{table}", ""]
    with open(os.path.join(args.outdir, "wilcoxon_vs_best.tex"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    # --- Console summary --------------------------------------------------
    print("Each method vs. best (paired Wilcoxon):")
    for r in vb:
        print(f"  {r['method']:>8}: mean {r['mean_GAP%']:7.3f}%  "
              f"(+{r['delta_vs_best']:.3f})  p={r['p_value']:.4g}  "
              f"{'SIGNIFICANT' if r['significant']=='yes' else 'n.s.'}")
    n_sig = int(pairs['significant'].sum())
    print(f"\nPairwise: {n_sig}/{len(pairs)} comparisons significant at "
          f"alpha={args.alpha}.")
    print(f"\nWrote to {args.outdir}:")
    print("  wilcoxon_pairs.csv, wilcoxon_matrix.csv, "
          "wilcoxon_vs_best.csv, wilcoxon_vs_best.tex")


if __name__ == "__main__":
    main()
