"""Score NOT-gate pairs: activator on the tumor, blocker sparing healthy cells.

NOT(A, B) engages a cell positive for activator A and negative for blocker B. This opens up
broadly-expressed activators that are untargetable alone, at the cost of trusting B-negative
calls, which are dropout-sensitive in scRNA. These results are therefore reported as
exploratory (Rule 14). Metrics mirror the AND scan: per-patient tumor coverage floor and the
worst-case healthy liability over all cell populations.

Output:
    results/tables/pairs_not.csv

Run:
    uv run python scripts/31_score_pairs_not.py
"""

from __future__ import annotations

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.scan import DEFAULT_K, load_scan_frames, scan


def main() -> None:
    """Run the NOT scan and write the ordered activator/blocker table."""
    malignant, benign, healthy, genes = load_scan_frames()
    print(f"Scanning NOT gates over {len(genes)} genes | malignant={len(malignant):,} | "
          f"benign={len(benign):,} | healthy={len(healthy):,} | k={DEFAULT_K}")
    res = scan(malignant, benign, healthy, genes, k=DEFAULT_K)

    not_df = res["not"].sort_values(
        "selectivity_xprostate", ascending=False).reset_index(drop=True)
    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    not_df.to_csv(RESULTS_TABLES / "pairs_not.csv", index=False)

    print(f"Wrote pairs_not.csv ({len(not_df)} ordered activator/blocker pairs)")
    cols = ["activator", "blocker", "tumor_q10", "tumor_median", "benign_prostate_median",
            "worst_healthy_xprostate", "worst_xp_celltype", "malignant_vs_benign"]
    print("\nTop 12 NOT gates by extra-prostatic selectivity (exploratory):")
    print(not_df[cols].head(12).to_string(index=False))


if __name__ == "__main__":
    main()
