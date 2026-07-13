"""Render standalone, video-legible demo figures from the committed tables.

These are the on-screen assets for the three-minute demo. They read only the tables in
``results/tables/`` and write high-resolution PNGs to ``results/figures/``; the report draws its
own in-document versions, so the two never share a burned-in image. Fonts and line weights are
larger than the report's for projection.

Output: results/figures/*.png

Run:
    uv run python scripts/90_demo_figures.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dual_marker_discovery.config import RESULTS_FIGURES, RESULTS_TABLES

PAL = {"ink": "#0A0F29", "blue": "#1E4FA3", "verm": "#c9542b", "green": "#2e7d5b",
       "amber": "#d99a1c", "grey": "#9aa0ab", "faint": "#dce5f2"}


def _load(name):
    p = RESULTS_TABLES / name
    return pd.read_csv(p) if p.exists() else None


def _style():
    plt.rcParams.update({
        "figure.dpi": 200, "savefig.dpi": 200, "font.size": 13, "font.family": "sans-serif",
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#8c8c8c",
        "axes.titlesize": 15, "axes.titleweight": "bold", "axes.labelsize": 13,
    })


def _pair(df, a, b):
    m = (((df.marker_a == a) & (df.marker_b == b)) | ((df.marker_a == b) & (df.marker_b == a)))
    return df[m].iloc[0]


def fig_singles(singles):
    keys = ["FOLH1", "PSCA", "STEAP1", "STEAP2", "TACSTD2", "CD276", "TMPRSS2", "HPN", "DLL3"]
    s = singles.set_index("marker").reindex([k for k in keys if k in singles.marker.values])
    s = s.sort_values("worst_healthy_xprostate")
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(s)); h = 0.38
    ax.barh(y + h/2, s["tumor_median"], height=h, color=PAL["blue"], label="tumor coverage (median)")
    ax.barh(y - h/2, s["worst_healthy_xprostate"], height=h, color=PAL["verm"],
            label="worst extra-prostatic liability")
    ax.set_yticks(y); ax.set_yticklabels(s.index); ax.set_xlim(0, 1)
    ax.set_xlabel("fraction of cells positive")
    ax.set_title("No single surface antigen is both high-coverage and safe")
    ax.legend(loc="lower right", frameon=False, fontsize=11)
    fig.tight_layout(); fig.savefig(RESULTS_FIGURES / "fig1_single_liabilities.png"); plt.close(fig)


def fig_pareto(frontier):
    d = frontier.copy()
    on = d[d.on_frontier].sort_values("worst_healthy_xprostate"); off = d[~d.on_frontier]
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.scatter(off["worst_healthy_xprostate"], off["tumor_q10"], s=34, color=PAL["grey"],
               alpha=0.55, label="surface pair (dominated)")
    ax.plot(on["worst_healthy_xprostate"], on["tumor_q10"], "-", color=PAL["blue"], lw=1.6, zorder=2)
    ax.scatter(on["worst_healthy_xprostate"], on["tumor_q10"], s=70, color=PAL["blue"],
               zorder=3, label="Pareto frontier")
    for (a, b), txt, col, dy in [(("FOLH1", "PSCA"), "PSMA x PSCA (control)", PAL["verm"], -20),
                                 (("FOLH1", "STEAP1"), "PSMA x STEAP1", PAL["ink"], 8),
                                 (("STEAP1", "HPN"), "STEAP1 x hepsin", PAL["green"], -20)]:
        r = _pair(d, a, b)
        ax.scatter(r["worst_healthy_xprostate"], r["tumor_q10"], s=150, facecolor="none",
                   edgecolor=col, linewidth=2.2, zorder=5)
        ax.annotate(txt, (r["worst_healthy_xprostate"], r["tumor_q10"]), textcoords="offset points",
                    xytext=(10, dy), fontsize=12, fontweight="bold", color=col)
    ax.set_xlabel("worst extra-prostatic liability  (lower is safer)")
    ax.set_ylabel("per-patient coverage floor  Q0.10  (higher is better)")
    ax.set_title("Surface-accessible AND pairs: coverage vs off-tissue risk")
    ax.set_xlim(-0.02, max(0.6, d.worst_healthy_xprostate.max()*1.05)); ax.set_ylim(-0.02, 1.0)
    ax.legend(loc="upper right", frameon=False, fontsize=11)
    fig.tight_layout(); fig.savefig(RESULTS_FIGURES / "fig2_pareto_frontier.png"); plt.close(fig)


def fig_recovery(recovery):
    r = recovery.copy()
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(r["entity"], r["worst_healthy_xprostate"],
                  color=[PAL["verm"], PAL["amber"], PAL["green"]][:len(r)], width=0.6)
    for bar, ct in zip(bars, r["worst_xp_celltype"]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.015, str(ct)[:22],
                ha="center", va="bottom", fontsize=10)
    ax.set_ylim(0, 1.08); ax.set_ylabel("worst extra-prostatic liability")
    ax.set_title("The AND gate removes the single-agent liabilities")
    fig.tight_layout(); fig.savefig(RESULTS_FIGURES / "fig3_psma_psca_recovery.png"); plt.close(fig)


def fig_doublets(qc):
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(qc)); w = 0.38
    ax.bar(x - w/2, qc["and_coverage_all"], width=w, color=PAL["blue"], label="all malignant cells")
    ax.bar(x + w/2, qc["and_coverage_singlets"], width=w, color=PAL["green"],
           label="doublets removed")
    ax.set_xticks(x); ax.set_xticklabels(qc["pair"]); ax.set_ylim(0, 1)
    ax.set_ylabel("AND coverage (median across patients)")
    ax.set_title("AND co-expression is not a doublet artifact")
    ax.legend(frameon=False, fontsize=11)
    fig.tight_layout(); fig.savefig(RESULTS_FIGURES / "fig4_doublet_robustness.png"); plt.close(fig)


def fig_nomination(pairs_and):
    fig, ax = plt.subplots(figsize=(8.5, 5))
    pairs = [("FOLH1", "PSCA", "PSMA x PSCA\n(control)"),
             ("FOLH1", "STEAP1", "PSMA x STEAP1\n(translatable)"),
             ("STEAP1", "HPN", "STEAP1 x hepsin\n(Pareto-optimal)")]
    x = np.arange(len(pairs)); w = 0.26
    mal = [_pair(pairs_and, a, b)["tumor_median"] for a, b, _ in pairs]
    ben = [_pair(pairs_and, a, b)["benign_prostate_median"] for a, b, _ in pairs]
    xp = [_pair(pairs_and, a, b)["worst_healthy_xprostate"] for a, b, _ in pairs]
    ax.bar(x - w, mal, w, color=PAL["blue"], label="malignant coverage")
    ax.bar(x, ben, w, color=PAL["amber"], label="benign prostate")
    ax.bar(x + w, xp, w, color=PAL["verm"], label="worst extra-prostatic")
    ax.set_xticks(x); ax.set_xticklabels([p[2] for p in pairs], fontsize=11)
    ax.set_ylim(0, 1); ax.set_ylabel("fraction of cells positive")
    ax.set_title("Nominated pairs: tumor-specific and off-tissue safe")
    ax.legend(frameon=False, fontsize=11)
    fig.tight_layout(); fig.savefig(RESULTS_FIGURES / "fig5_nomination_profile.png"); plt.close(fig)


def main() -> None:
    """Render all demo figures to results/figures/."""
    _style()
    RESULTS_FIGURES.mkdir(parents=True, exist_ok=True)
    fig_singles(_load("singles_markers.csv"))
    fig_pareto(_load("surface_frontier.csv"))
    fig_recovery(_load("psma_psca_recovery.csv"))
    qc = _load("doublet_qc.csv")
    if qc is not None:
        fig_doublets(qc)
    fig_nomination(_load("pairs_and.csv"))
    print(f"Wrote demo figures to {RESULTS_FIGURES}")
    for p in sorted(RESULTS_FIGURES.glob("*.png")):
        print(f"  {p.name}  ({p.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
