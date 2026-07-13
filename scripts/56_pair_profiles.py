"""Per-patient coverage and healthy-tissue liability profiles for the headline pairs.

Two views that summaries alone cannot show:

* **Per-patient coverage** — the AND coverage of each key pair in every scored patient, so the
  robustness (or fragility) of a pair is visible cell-population by cell-population, not just as a
  single median (Rule 8).
* **Healthy-tissue liability profile** — for the nominated pair, the AND co-positive fraction in the
  healthy cell populations where it is highest, so the residual off-tumor risk is named, not hidden.

Outputs:
    results/tables/nomination_per_patient.csv
    results/tables/pair_tissue_liability.csv

Run:
    uv run python scripts/56_pair_profiles.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.scan import DEFAULT_K, load_scan_frames, positivity_matrix

KEY_PAIRS = [("FOLH1", "PSCA"), ("FOLH1", "STEAP1"), ("STEAP1", "HPN")]
NOMINATED = ("FOLH1", "STEAP1")
MIN_CELLS = 20


def _and_fraction(df: pd.DataFrame, genes: list[str], a: str, b: str,
                  group_col: str) -> pd.DataFrame:
    """AND co-positive fraction of (a, b) within each group of ``group_col``."""
    P = positivity_matrix(df, genes, DEFAULT_K)
    ia, ib = genes.index(a), genes.index(b)
    engaged = (P[:, ia] * P[:, ib])
    g = pd.DataFrame({"grp": df[group_col].to_numpy(), "engaged": engaged})
    agg = g.groupby("grp")["engaged"].agg(["mean", "size"]).reset_index()
    return agg[agg["size"] >= MIN_CELLS].rename(columns={"grp": group_col, "mean": "coverage",
                                                         "size": "n_cells"})


def main() -> None:
    """Write per-patient coverage and the nominated pair's healthy-tissue liability profile."""
    malignant, benign, healthy, genes = load_scan_frames()

    # Per-patient malignant coverage for each key pair.
    rows = []
    for a, b in KEY_PAIRS:
        cov = _and_fraction(malignant, genes, a, b, "patient")
        for _, r in cov.iterrows():
            rows.append({"pair": f"{a} + {b}", "patient": r["patient"],
                         "coverage": r["coverage"], "n_malignant": int(r["n_cells"])})
    pd.DataFrame(rows).to_csv(RESULTS_TABLES / "nomination_per_patient.csv", index=False)

    # Healthy-tissue liability profile for the nominated pair.
    a, b = NOMINATED
    healthy = healthy.copy()
    healthy["population"] = (healthy["tissue_general"].astype(str) + " | "
                             + healthy["cell_type"].astype(str))
    prof = _and_fraction(healthy, genes, a, b, "population")
    prof = prof.sort_values("coverage", ascending=False).head(15)
    prof[["tissue", "cell_type"]] = prof["population"].str.split(
        " | ", n=1, expand=True, regex=False)
    prof.insert(0, "pair", f"{a} + {b}")
    prof[["pair", "tissue", "cell_type", "coverage", "n_cells"]].to_csv(
        RESULTS_TABLES / "pair_tissue_liability.csv", index=False)

    pp = pd.DataFrame(rows)
    print("Wrote nomination_per_patient.csv and pair_tissue_liability.csv")
    print("\nPer-patient coverage summary by pair:")
    print(pp.groupby("pair")["coverage"].describe()[["min", "25%", "50%", "75%", "max"]].round(3))
    print(f"\n{a} + {b} top healthy-tissue liabilities:")
    print(prof[["tissue", "cell_type", "coverage", "n_cells"]].head(8).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
