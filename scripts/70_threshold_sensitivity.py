"""Re-score the key pairs under several positivity thresholds (Rule 9).

Positivity is not a single ``count > 0`` call, so the headline pairs are re-scored at raw-count
thresholds k = 1, 2, 3. A nomination that only survives at the loosest threshold is not
trustworthy; this table shows how per-patient coverage and worst extra-prostatic liability move
as the call is tightened.

Output:
    results/tables/threshold_sensitivity.csv

Run:
    uv run python scripts/70_threshold_sensitivity.py
"""

from __future__ import annotations

import pandas as pd

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.scan import load_scan_frames, scan

# Pairs tracked across thresholds: positive control and the two co-lead nominations.
KEY_PAIRS = [("FOLH1", "PSCA"), ("FOLH1", "STEAP1"), ("STEAP1", "HPN"),
             ("STEAP2", "HPN"), ("STEAP1", "TMPRSS2")]
THRESHOLDS = [1, 2, 3]


def _row(df: pd.DataFrame, a: str, b: str) -> pd.Series:
    m = (((df.marker_a == a) & (df.marker_b == b)) | ((df.marker_a == b) & (df.marker_b == a)))
    return df[m].iloc[0]


def main() -> None:
    """Score the key pairs at each threshold and write the sensitivity table."""
    malignant, benign, healthy, genes = load_scan_frames()
    rows = []
    for k in THRESHOLDS:
        res = scan(malignant, benign, healthy, genes, k=k)
        for a, b in KEY_PAIRS:
            r = _row(res["and"], a, b)
            rows.append({
                "pair": f"{a} + {b}", "k": k,
                "tumor_q10": r.tumor_q10, "tumor_median": r.tumor_median,
                "benign_prostate_median": r.benign_prostate_median,
                "worst_healthy_xprostate": r.worst_healthy_xprostate,
                "malignant_vs_benign": r.malignant_vs_benign,
            })
    out = pd.DataFrame(rows)
    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    out.to_csv(RESULTS_TABLES / "threshold_sensitivity.csv", index=False)

    print(f"Wrote threshold_sensitivity.csv ({len(out)} rows)")
    for pair in out["pair"].unique():
        sub = out[out.pair == pair]
        print(f"\n{pair}")
        print(sub[["k", "tumor_q10", "tumor_median", "worst_healthy_xprostate",
                   "malignant_vs_benign"]].to_string(index=False))


if __name__ == "__main__":
    main()
