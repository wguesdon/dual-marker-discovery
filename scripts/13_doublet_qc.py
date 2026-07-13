"""Ingest scDblFinder calls and check the AND coverage is robust to doublet removal.

This closes the Python<->R handoff: it reads the doublet classes produced in the container,
reports the doublet rate overall and among the malignant cells that drive AND scoring, and
recomputes the per-patient AND coverage of the key pairs with doublets removed. A large shift
would mean the co-expression signal was partly an artifact of two-cells-as-one; a small shift
means the finding holds.

Output:
    results/tables/doublet_qc.csv

Run (after scripts/12 and the container step):
    uv run python scripts/13_doublet_qc.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dual_marker_discovery.config import DATA_INTERIM, DATA_PROCESSED, RESULTS_TABLES

CALLS = DATA_INTERIM / "doublets" / "doublet_calls.csv"
KEY_PAIRS = [("FOLH1", "PSCA"), ("FOLH1", "STEAP1"), ("STEAP1", "STEAP2")]
MIN_CELLS = 20


def _median_and_coverage(df: pd.DataFrame, a: str, b: str) -> float:
    """Median across patients of per-patient P(A+ and B+ | cells in df)."""
    pos = (df[a] >= 1) & (df[b] >= 1)
    per = pos.groupby(df["patient"]).mean()
    counts = df.groupby("patient").size()
    per = per[counts >= MIN_CELLS]
    return float(per.median()) if len(per) else float("nan")


def main() -> None:
    """Report doublet rates and doublet-removed AND coverage for the key pairs."""
    calls = pd.read_csv(CALLS)
    tumor = pd.read_parquet(DATA_PROCESSED / "tumor_cells.parquet")
    tumor = tumor.merge(
        calls[["barcode", "doublet_class"]], left_on="cell_id", right_on="barcode", how="left")

    mal = tumor[tumor["is_malignant"]].copy()
    n_dbl_all = int((calls["doublet_class"] == "doublet").sum())
    rate_all = n_dbl_all / len(calls)
    rate_mal = float((mal["doublet_class"] == "doublet").mean())
    mal_singlet = mal[mal["doublet_class"] != "doublet"]

    rows = []
    for a, b in KEY_PAIRS:
        cov_all = _median_and_coverage(mal, a, b)
        cov_sng = _median_and_coverage(mal_singlet, a, b)
        rows.append({
            "pair": f"{a}+{b}",
            "and_coverage_all": cov_all,
            "and_coverage_singlets": cov_sng,
            "delta": cov_sng - cov_all,
        })
    qc = pd.DataFrame(rows)
    qc.attrs = {}
    summary = pd.DataFrame([{
        "n_cells": len(calls), "n_doublet": n_dbl_all,
        "doublet_rate_all": rate_all, "doublet_rate_malignant": rate_mal,
        "n_malignant": len(mal), "n_malignant_singlet": len(mal_singlet),
    }])

    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    qc.to_csv(RESULTS_TABLES / "doublet_qc.csv", index=False)
    summary.to_csv(RESULTS_TABLES / "doublet_summary.csv", index=False)

    print(f"Doublet rate: all cells {rate_all:.3f} ({n_dbl_all}/{len(calls)}); "
          f"malignant {rate_mal:.3f}")
    print("\nAND coverage, all malignant vs doublet-removed (median across patients):")
    print(qc.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
