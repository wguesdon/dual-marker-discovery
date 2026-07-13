"""Marker co-escape check for the nominated AND pair.

An AND gate only recovers safety if its two markers are positive on DIFFERENT healthy cells: if
FOLH1 (PSMA) and STEAP1 escape onto the SAME normal cells, requiring both does not lower the
liability. This scores, per extra-prostatic healthy population (donor-robust, matching the scan),
the two single co-detections and the AND, plus a co-escape ratio = AND / min(single): near 1 means
the two markers overlap on the same cells (co-escape, bad); near 0 means they separate (the AND
buys safety). It also correlates the two single liabilities across populations.

Output:
    results/tables/coescape.csv

Run:
    uv run python scripts/73_coescape.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.scan import (
    DEFAULT_K, MIN_CELLS_DONOR, MIN_DONORS, PROSTATE_PREFIX, load_scan_frames, positivity_matrix,
)

A, B = "FOLH1", "STEAP1"


def main() -> None:
    """Score per-population single vs AND co-detection and the co-escape ratio for the lead pair."""
    _, _, hea, genes = load_scan_frames()
    gi = {g: i for i, g in enumerate(genes)}
    P = positivity_matrix(hea, genes, DEFAULT_K)
    a, b = P[:, gi[A]], P[:, gi[B]]
    df = pd.DataFrame({
        "pop": (hea["tissue_general"].astype(str) + " | " + hea["cell_type"].astype(str)).to_numpy(),
        "donor": hea["donor_id"].astype(str).to_numpy(),
        "a": a, "b": b, "ab": a * b,
    })
    df = df[~df["pop"].str.startswith(PROSTATE_PREFIX)]  # extra-prostatic only

    g = df.groupby(["pop", "donor"]).agg(
        a=("a", "mean"), b=("b", "mean"), ab=("ab", "mean"), n=("a", "size")).reset_index()
    g = g[g["n"] >= MIN_CELLS_DONOR]
    pop = g.groupby("pop").agg(
        a=("a", "median"), b=("b", "median"), ab=("ab", "median"), nd=("donor", "nunique")
    ).reset_index()
    pop = pop[pop["nd"] >= MIN_DONORS].copy()
    pop["coescape_ratio"] = pop["ab"] / pop[["a", "b"]].min(axis=1).clip(lower=1e-9)

    rho = float(spearmanr(pop["a"], pop["b"]).correlation)
    worst_a = pop.loc[pop["a"].idxmax()]
    worst_b = pop.loc[pop["b"].idxmax()]
    worst_ab = pop.loc[pop["ab"].idxmax()]

    out = pop.sort_values("ab", ascending=False).head(12).rename(columns={
        "a": f"single_{A}", "b": f"single_{B}", "ab": "and", "nd": "n_donors"})
    out["single_liab_spearman"] = round(rho, 4)
    out.to_csv(RESULTS_TABLES / "coescape.csv", index=False)

    print(f"Spearman(single {A}, single {B}) across {len(pop)} extra-prostatic populations: {rho:.3f}")
    print(f"Worst {A} population : {worst_a['pop']}  ({A} {worst_a['a']:.2f}, {B} {worst_a['b']:.2f}, "
          f"AND {worst_a['ab']:.2f})")
    print(f"Worst {B} population : {worst_b['pop']}  ({A} {worst_b['a']:.2f}, {B} {worst_b['b']:.2f}, "
          f"AND {worst_b['ab']:.2f})")
    print(f"Worst AND population : {worst_ab['pop']}  ({A} {worst_ab['a']:.2f}, {B} {worst_ab['b']:.2f}, "
          f"AND {worst_ab['ab']:.2f}, co-escape ratio {worst_ab['coescape_ratio']:.2f})")
    print("\nTop extra-prostatic AND populations:")
    print(out[["pop", f"single_{A}", f"single_{B}", "and", "coescape_ratio", "n_donors"]].round(3)
          .to_string(index=False))


if __name__ == "__main__":
    main()
