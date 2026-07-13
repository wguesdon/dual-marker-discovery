"""Nominate an improved AND pair and an exploratory NOT gate from the surface-accessible scan.

Transcript co-expression is filtered to what could actually be built as a cell-surface therapy
(Rule 12). Secreted markers (KLK3/PSA, KLK2, ACPP) and prostein (SLC45A3), which the Human
Protein Atlas localizes to intracellular vesicles rather than the plasma membrane, are excluded
as targets. Among the remaining surface-accessible markers the script:

* draws the Pareto frontier of per-patient coverage (Q0.10) versus worst extra-prostatic risk,
* nominates a headline AND pair anchored on two clinically validated antigens, reporting its
  improvement over PSMA-PSCA and over each single marker,
* nominates one exploratory NOT gate (a surface activator spared by a normal-tissue blocker),
  reported with the scRNA blocker-negative dropout caveat (Rule 14).

Outputs:
    results/tables/surface_frontier.csv
    results/tables/nomination.csv
    results/tables/nomination_not.csv

Run:
    uv run python scripts/55_nominate.py
"""

from __future__ import annotations

import pandas as pd

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.panel import POSITIVE_CONTROL_PAIR
from dual_marker_discovery.scoring import pareto_front

# Markers excluded as surface targets, with the reason recorded for the report.
NON_TARGETABLE = {
    "KLK3": "secreted (PSA)", "KLK2": "secreted (hK2)", "ACPP": "secreted (PAP)",
    "SLC45A3": "intracellular; HPA localizes prostein to vesicles, not plasma membrane",
}
# Headline nomination anchored on two antigens with clinical-grade binders already in humans.
HEADLINE_PAIR = ("FOLH1", "STEAP1")


def _and_row(df: pd.DataFrame, a: str, b: str) -> pd.Series:
    m = (((df.marker_a == a) & (df.marker_b == b)) | ((df.marker_a == b) & (df.marker_b == a)))
    return df[m].iloc[0]


def main() -> None:
    """Build the surface frontier, the headline AND nomination, and the exploratory NOT gate."""
    and_df = pd.read_csv(RESULTS_TABLES / "pairs_and.csv")
    not_df = pd.read_csv(RESULTS_TABLES / "pairs_not.csv")
    panel = pd.read_csv(RESULTS_TABLES / "surface_panel.csv").set_index("gene")
    singles = pd.read_csv(RESULTS_TABLES / "singles_markers.csv").set_index("marker")

    surface = set(panel.index[panel["compartment"].isin(["surface", "membrane"])])
    targetable = surface - set(NON_TARGETABLE)

    sa = and_df[and_df.marker_a.isin(targetable) & and_df.marker_b.isin(targetable)].copy()
    sa["on_frontier"] = pareto_front(sa, maximize=["tumor_q10"], minimize=["worst_healthy_xprostate"])
    sa = sa.sort_values(["on_frontier", "tumor_q10"], ascending=[False, False]).reset_index(drop=True)
    sa.to_csv(RESULTS_TABLES / "surface_frontier.csv", index=False)

    # Headline AND nomination vs the PSMA-PSCA positive control and vs each single marker.
    a, b = HEADLINE_PAIR
    pc_a, pc_b = POSITIVE_CONTROL_PAIR
    nom = _and_row(and_df, a, b)
    pc = _and_row(and_df, pc_a, pc_b)
    nomination = pd.DataFrame([{
        "nominated_pair": f"{a} + {b}", "gate": "AND",
        "tumor_q10": nom.tumor_q10, "tumor_median": nom.tumor_median,
        "benign_prostate_median": nom.benign_prostate_median,
        "malignant_vs_benign": nom.malignant_vs_benign,
        "worst_healthy_xprostate": nom.worst_healthy_xprostate,
        "worst_xp_celltype": nom.worst_xp_celltype,
        "worst_xp_n_donors": int(nom.worst_xp_n_donors),
        "worst_xp_n_cells": int(nom.worst_xp_n_cells),
        "single_a_worst_xp": singles.loc[a, "worst_healthy_xprostate"],
        "single_b_worst_xp": singles.loc[b, "worst_healthy_xprostate"],
        "psma_psca_tumor_median": pc.tumor_median,
        "psma_psca_worst_xp": pc.worst_healthy_xprostate,
        "coverage_fold_vs_psma_psca": nom.tumor_median / max(pc.tumor_median, 1e-9),
        "on_surface_frontier": bool(
            sa.loc[((sa.marker_a == a) & (sa.marker_b == b))
                    | ((sa.marker_a == b) & (sa.marker_b == a)), "on_frontier"].iloc[0]),
    }])
    nomination.to_csv(RESULTS_TABLES / "nomination.csv", index=False)

    # Exploratory NOT gate: surface activator, normal-tissue blocker candidate.
    blockers = set(panel.index[panel["role_prior"] == "blocker_candidate"])
    nt = not_df[not_df.activator.isin(targetable) & not_df.blocker.isin(blockers)].copy()
    nt = nt.sort_values("selectivity_xprostate", ascending=False).reset_index(drop=True)
    nt.head(10).to_csv(RESULTS_TABLES / "nomination_not.csv", index=False)

    print("=== Surface-accessible Pareto frontier (AND) ===")
    fcols = ["marker_a", "marker_b", "tumor_q10", "tumor_median", "worst_healthy_xprostate",
             "worst_xp_celltype", "malignant_vs_benign"]
    print(sa.loc[sa.on_frontier, fcols].to_string(index=False))
    print("\n=== Headline AND nomination ===")
    print(nomination.T.to_string(header=False))
    print("\n=== Exploratory NOT gate (top surface activator / normal-tissue blocker) ===")
    ncols = ["activator", "blocker", "tumor_q10", "tumor_median", "worst_healthy_xprostate",
             "worst_xp_celltype"]
    print(nt.head(6)[ncols].to_string(index=False))


if __name__ == "__main__":
    main()
