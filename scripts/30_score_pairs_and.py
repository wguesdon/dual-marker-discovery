"""Score AND-gate pairs and single markers: per-patient tumor coverage vs worst healthy risk.

AND(A, B) engages a cell positive for both markers. For each pair the script reports the
per-patient tumor coverage floor (Q0.10), median, and mean across the malignant compartment,
and the worst-case co-positive fraction over every healthy cell population (Rule 8). Single
markers are scored the same way for the "one antigen is not enough" contrast.

Outputs:
    results/tables/pairs_and.csv
    results/tables/singles_markers.csv

Run:
    uv run python scripts/30_score_pairs_and.py
"""

from __future__ import annotations

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.scan import DEFAULT_K, load_scan_frames, scan


def main() -> None:
    """Run the AND scan and write the pair and single-marker tables."""
    malignant, benign, healthy, genes = load_scan_frames()
    print(f"Scanning {len(genes)} genes | malignant={len(malignant):,} | "
          f"benign-prostate={len(benign):,} | healthy={len(healthy):,} | k={DEFAULT_K}")
    res = scan(malignant, benign, healthy, genes, k=DEFAULT_K)

    and_df = res["and"].sort_values(
        "selectivity_xprostate", ascending=False).reset_index(drop=True)
    singles = res["singles"].sort_values(
        "selectivity_xprostate", ascending=False).reset_index(drop=True)

    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    and_df.to_csv(RESULTS_TABLES / "pairs_and.csv", index=False)
    singles.to_csv(RESULTS_TABLES / "singles_markers.csv", index=False)

    print(f"Patients scored: {res['n_patients']} | benign-prostate patients: "
          f"{res['n_benign_patients']} | healthy populations: {res['n_healthy_pops']}")
    print(f"Wrote pairs_and.csv ({len(and_df)} pairs), singles_markers.csv ({len(singles)})")
    cols = ["marker_a", "marker_b", "tumor_q10", "tumor_median", "benign_prostate_median",
            "worst_healthy_xprostate", "worst_xp_celltype", "malignant_vs_benign"]
    print("\nTop 12 AND pairs by extra-prostatic selectivity:")
    print(and_df[cols].head(12).to_string(index=False))


if __name__ == "__main__":
    main()
