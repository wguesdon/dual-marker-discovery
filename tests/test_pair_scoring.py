"""Unit tests for the logic-gate pair-scoring core.

These assert the two rules the scoring must never break: positivity is a real threshold, not a
``count > 0`` shortcut baked into the summary (Rule 9), and tumor coverage is summarized per
patient so a high cell-count patient cannot dominate (Rule 8). A small synthetic scan checks
that a genuinely tumor-specific, healthy-clean pair beats a random pair and that the matched
benign-prostate control separates from the malignant coverage.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dual_marker_discovery import scoring
from dual_marker_discovery.scan import scan


def test_positivity_threshold() -> None:
    """Positivity is ``expr > tau``; a stricter tau removes low counts."""
    expr = np.array([[0.0, 2.0], [1.0, 0.0]])
    assert scoring.positivity(expr, 0.0).tolist() == [[False, True], [True, False]]
    assert scoring.positivity(expr, 1.5).tolist() == [[False, True], [False, False]]


def test_group_fraction_ignores_small_groups() -> None:
    """A group below ``min_cells`` is scored NaN rather than 0 or 1."""
    engaged = np.array([1, 1, 0, 1])
    groups = np.array(["A", "A", "B", "A"])  # B has one cell
    frac = scoring.group_fraction(engaged, groups, min_cells=2)
    assert frac["A"] == 1.0
    assert np.isnan(frac["B"])


def test_summary_is_per_patient_not_pooled() -> None:
    """The coverage summary must not collapse to the pooled cell fraction."""
    # Group A: 2 cells, both engaged (frac 1.0). Group B: 10 cells, 2 engaged (frac 0.2).
    engaged = np.array([1, 1] + [1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    groups = np.array(["A", "A"] + ["B"] * 10)
    frac = scoring.group_fraction(engaged, groups, min_cells=2)
    summ = scoring.summarize_coverage(frac, q=0.10)
    assert summ.median == 0.6          # median of the two per-patient fractions
    pooled = engaged.mean()            # 4 / 12
    assert abs(pooled - 0.3333) < 1e-3
    assert summ.median != pooled       # per-patient summary differs from pooling


def test_worst_healthy_is_worst_case() -> None:
    """Healthy liability is the maximum over cell types, not the average."""
    engaged = np.array([1, 1, 1, 0, 0, 0])
    celltypes = np.array(["risky", "risky", "risky", "safe", "safe", "safe"])
    liab = scoring.worst_healthy_liability(engaged, celltypes, min_cells=3)
    assert liab.worst_frac == 1.0
    assert liab.worst_group == "risky"


def test_pareto_front_basic() -> None:
    """A dominated pair is excluded; non-dominated pairs are kept."""
    df = pd.DataFrame({
        # row0 and row1 trade off (neither dominates); row2 is dominated by row0
        # (same risk 0.3, lower cov 0.8 < 0.9).
        "cov": [0.9, 0.5, 0.8],
        "risk": [0.3, 0.1, 0.3],
    })
    front = scoring.pareto_front(df, maximize=["cov"], minimize=["risk"])
    assert front.tolist() == [True, True, False]


def _synthetic_frames():
    """Build tiny malignant / benign / healthy frames for an end-to-end scan."""
    genes = ["G0", "G1", "G2", "G3"]
    rng = np.random.default_rng(0)

    def block(n, patient, g0, g1, g2, g3):
        return pd.DataFrame({
            "patient": [patient] * n,
            "G0": rng.binomial(3, g0, n), "G1": rng.binomial(3, g1, n),
            "G2": rng.binomial(3, g2, n), "G3": rng.binomial(3, g3, n),
        })

    # Malignant: G0 and G1 almost always on; G2/G3 rare. Two patients, very different sizes.
    malignant = pd.concat([
        block(40, "P1", 0.95, 0.95, 0.05, 0.05),
        block(600, "P2", 0.95, 0.95, 0.05, 0.05),
    ], ignore_index=True)
    # Benign prostate: G0/G1 much lower -> pair separates malignant from benign.
    benign = pd.concat([
        block(50, "P1", 0.15, 0.15, 0.05, 0.05),
        block(50, "P2", 0.15, 0.15, 0.05, 0.05),
    ], ignore_index=True)
    # Healthy: G0/G1 essentially off everywhere. Two donors so the population is donor-replicated.
    healthy = block(400, "d", 0.02, 0.02, 0.3, 0.3)
    healthy["tissue_general"] = "blood"
    healthy["cell_type"] = "t cell"
    healthy["donor_id"] = (["d1"] * 200) + (["d2"] * 200)
    return malignant, benign, healthy, genes


def test_scan_recovers_specific_pair() -> None:
    """A tumor-specific, healthy-clean pair beats a random pair and clears the benign control."""
    malignant, benign, healthy, genes = _synthetic_frames()
    res = scan(malignant, benign, healthy, genes, k=1, min_cells_tumor=20,
               min_cells_donor=10, min_donors=2)
    and_df = res["and"].set_index(["marker_a", "marker_b"])

    good = and_df.loc[("G0", "G1")]
    rand = and_df.loc[("G2", "G3")]
    assert good["tumor_median"] > 0.6                 # strong malignant coverage
    assert good["worst_healthy_all"] < 0.2            # clean in healthy
    assert good["malignant_vs_benign"] > 0.4          # separates from benign prostate
    assert good["tumor_median"] > rand["tumor_median"]  # beats the random pair
    assert res["n_patients"] == 2
