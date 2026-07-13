"""Rank AND-gate pairs on a Pareto frontier of tumor coverage vs extra-prostatic risk.

The frontier is drawn in the two axes that decide a combinatorial target: the per-patient
tumor coverage floor (Q0.10, larger is better) and the worst-case extra-prostatic healthy
liability (smaller is better; the prostate is the target organ, so its normal cells are not
the safety-limiting tissue, but every other organ is). A pair is on the frontier when no other
pair beats it on both. Each pair is also flagged for surface targetability, since a secreted
marker such as KLK3/PSA cannot be a cell-surface target however co-expressed it is (Rule 12).

Output:
    results/tables/pareto_frontier.csv

Run:
    uv run python scripts/32_pareto_rank.py
"""

from __future__ import annotations

import pandas as pd

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.scoring import pareto_front


def main() -> None:
    """Flag Pareto-non-dominated AND pairs, mark targetability, write the ranked table."""
    and_df = pd.read_csv(RESULTS_TABLES / "pairs_and.csv")
    panel = pd.read_csv(RESULTS_TABLES / "surface_panel.csv").set_index("gene")
    surface = set(panel.index[panel["compartment"].isin(["surface", "membrane"])])

    df = and_df.copy()
    df["both_surface"] = df["marker_a"].isin(surface) & df["marker_b"].isin(surface)

    # Frontier over all pairs (context) and over surface-targetable pairs (the real short list).
    df["on_frontier_all"] = pareto_front(
        df, maximize=["tumor_q10"], minimize=["worst_healthy_xprostate"])
    df["on_frontier_surface"] = False
    surf = df[df["both_surface"]].copy()
    surf_front = pareto_front(surf, maximize=["tumor_q10"], minimize=["worst_healthy_xprostate"])
    df.loc[surf.index[surf_front], "on_frontier_surface"] = True

    df = df.sort_values(
        ["on_frontier_surface", "tumor_q10"], ascending=[False, False]).reset_index(drop=True)
    df["rank_surface"] = range(1, len(df) + 1)
    df.to_csv(RESULTS_TABLES / "pareto_frontier.csv", index=False)

    cols = ["marker_a", "marker_b", "tumor_q10", "tumor_median", "benign_prostate_median",
            "worst_healthy_xprostate", "worst_xp_celltype", "malignant_vs_benign"]
    print(f"Wrote pareto_frontier.csv: {int(df['on_frontier_surface'].sum())} "
          f"surface-targetable frontier pairs; {int(df['on_frontier_all'].sum())} overall")
    print("\nSurface-targetable Pareto frontier (coverage floor vs worst extra-prostatic risk):")
    print(df.loc[df["on_frontier_surface"], cols].to_string(index=False))


if __name__ == "__main__":
    main()
