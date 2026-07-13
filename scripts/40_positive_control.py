"""Positive control (PSMA-PSCA recovery) and negative control (random surface pairs).

The positive control is sacred (Rule 13): the scan must recover PSMA (FOLH1) x PSCA as a
genuine combinatorial pair before any new pair is trustworthy. Recovery here is not "highest
coverage" (PSCA transcript is dropout-prone, so raw AND coverage is low); it is the AND-gate
*safety collapse*: each marker alone carries a large extra-prostatic liability, and requiring
both at once removes it.

The negative control is a random surface pair, which must score worse on extra-prostatic
selectivity (tumor coverage minus worst extra-prostatic liability) than PSMA x PSCA (Rule 7).

Outputs:
    results/tables/psma_psca_recovery.csv   single A, single B, and the AND pair side by side
    results/tables/negative_control.csv     random-pair baseline and explicit negative examples

Run:
    uv run python scripts/40_positive_control.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.panel import POSITIVE_CONTROL_PAIR

RNG_SEED = 0
N_RANDOM = 200


def _and_row(and_df: pd.DataFrame, a: str, b: str) -> pd.Series:
    """Return the AND row for an unordered pair regardless of column order."""
    m = (((and_df["marker_a"] == a) & (and_df["marker_b"] == b))
         | ((and_df["marker_a"] == b) & (and_df["marker_b"] == a)))
    return and_df[m].iloc[0]


def main() -> None:
    """Build the recovery and negative-control tables and print the verdict."""
    and_df = pd.read_csv(RESULTS_TABLES / "pairs_and.csv")
    singles = pd.read_csv(RESULTS_TABLES / "singles_markers.csv").set_index("marker")
    panel = pd.read_csv(RESULTS_TABLES / "surface_panel.csv").set_index("gene")
    a, b = POSITIVE_CONTROL_PAIR

    pair = _and_row(and_df, a, b)
    sa, sb = singles.loc[a], singles.loc[b]

    recovery = pd.DataFrame([
        {"entity": f"{a} (single)", "kind": "single",
         "tumor_median": sa["tumor_median"], "tumor_q10": sa["tumor_q10"],
         "worst_healthy_xprostate": sa["worst_healthy_xprostate"],
         "worst_xp_celltype": sa["worst_xp_celltype"],
         "worst_healthy_all": sa["worst_healthy_all"]},
        {"entity": f"{b} (single)", "kind": "single",
         "tumor_median": sb["tumor_median"], "tumor_q10": sb["tumor_q10"],
         "worst_healthy_xprostate": sb["worst_healthy_xprostate"],
         "worst_xp_celltype": sb["worst_xp_celltype"],
         "worst_healthy_all": sb["worst_healthy_all"]},
        {"entity": f"{a} AND {b}", "kind": "AND_pair",
         "tumor_median": pair["tumor_median"], "tumor_q10": pair["tumor_q10"],
         "worst_healthy_xprostate": pair["worst_healthy_xprostate"],
         "worst_xp_celltype": pair["worst_xp_celltype"],
         "worst_healthy_all": pair["worst_healthy_all"]},
    ])
    recovery.to_csv(RESULTS_TABLES / "psma_psca_recovery.csv", index=False)

    # AND-gate safety gain: how much the pair cuts the worse of the two single liabilities.
    single_worst = max(sa["worst_healthy_xprostate"], sb["worst_healthy_xprostate"])
    gate_reduction = single_worst - pair["worst_healthy_xprostate"]

    # Negative control: random surface pairs. Score = extra-prostatic selectivity.
    surface = set(panel.index[panel["compartment"].isin(["surface", "membrane"])])
    surf_pairs = and_df[and_df["marker_a"].isin(surface) & and_df["marker_b"].isin(surface)].copy()
    rng = np.random.default_rng(RNG_SEED)
    take = min(N_RANDOM, len(surf_pairs))
    rand = surf_pairs.iloc[rng.choice(len(surf_pairs), size=take, replace=False)]
    pair_sel = pair["tumor_median"] - pair["worst_healthy_xprostate"]
    rand_sel = rand["tumor_median"] - rand["worst_healthy_xprostate"]
    pct_worse = float((rand_sel < pair_sel).mean())

    # Explicit low-prostate comparator pairs as named negatives.
    comparators = list(panel.index[panel["category"] == "low_pc_comparator"])
    neg_rows = []
    for i in range(len(comparators)):
        for j in range(i + 1, len(comparators)):
            r = _and_row(and_df, comparators[i], comparators[j])
            neg_rows.append({"pair": f"{comparators[i]} AND {comparators[j]}",
                             "tumor_median": r["tumor_median"],
                             "worst_healthy_xprostate": r["worst_healthy_xprostate"],
                             "selectivity_xprostate": r["selectivity_xprostate"]})
    neg = pd.DataFrame(neg_rows)
    neg_summary = pd.DataFrame([{
        "psma_psca_selectivity_xprostate": pair_sel,
        "random_surface_pair_median_selectivity": float(rand_sel.median()),
        "frac_random_pairs_worse_than_psma_psca": pct_worse,
        "n_random_pairs": take,
        "and_gate_xprostate_reduction": gate_reduction,
    }])
    pd.concat([neg_summary.assign(row="summary"),
               neg.assign(row="comparator_example")], ignore_index=True
              ).to_csv(RESULTS_TABLES / "negative_control.csv", index=False)

    print("=== PSMA-PSCA recovery (extra-prostatic safety collapse) ===")
    print(recovery.to_string(index=False))
    print(f"\nAND-gate cuts worst extra-prostatic liability from {single_worst:.3f} "
          f"(worse single) to {pair['worst_healthy_xprostate']:.3f} "
          f"(reduction {gate_reduction:.3f}).")
    print(f"\nExtra-prostatic selectivity: PSMA-PSCA={pair_sel:.3f}; "
          f"random surface pair median={rand_sel.median():.3f}; "
          f"{pct_worse*100:.0f}% of random pairs score worse.")
    recovered = (gate_reduction > 0) and (pair_sel >= rand_sel.median())
    print(f"\nPOSITIVE CONTROL {'RECOVERED' if recovered else 'NOT recovered'}.")


if __name__ == "__main__":
    main()
