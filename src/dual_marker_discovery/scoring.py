"""Per-patient logic-gate scoring for combinatorial surface-marker pairs.

The scientific rules this module encodes (see ``SESSION_SUMMARY.md``):

* **Score per patient, then summarize. Never pool cells** (Rule 8). A patient with
  thousands of malignant cells must not dominate a pair's tumor-coverage score. Every
  tumor score is computed as a fraction *within* each patient first, then summarized
  across patients with a robust lower quantile.
* **Positivity is not ``count > 0``** (Rule 9). Positivity is a threshold on normalized
  expression, evaluated over a grid of thresholds by the sensitivity analysis. A single
  ``> 0`` call is never trusted, least of all for NOT-gate blocker-negative calls.

Two gate logics are scored:

* **AND gate** — a cell is engaged when positive for both markers. Tumor objective
  ``P(A+ and B+ | malignant, patient)``; healthy liability ``P(A+ and B+ | healthy cell type)``.
* **NOT gate** — a cell is engaged when positive for activator A and negative for blocker
  B. Tumor objective ``P(A+ and B- | malignant, patient)``; healthy liability
  ``P(A+ and B- | healthy cell type)``. NOT calls trust B-negatives and are dropout
  sensitive; they are reported as exploratory.

All functions operate on dense ``numpy`` arrays of normalized expression (log1p of
counts-per-10k is the convention used upstream), so a pair sweep is a handful of
vectorized boolean operations.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def positivity(expr: np.ndarray, tau: float) -> np.ndarray:
    """Binarize a normalized-expression matrix into positivity calls.

    Positivity is ``expr > tau`` on the normalized scale, never ``count > 0``. The caller
    sweeps ``tau`` to test sensitivity (Rule 9).

    Args:
        expr: Normalized expression, shape ``(n_cells, n_genes)``.
        tau: Positivity threshold on the same scale as ``expr``.

    Returns:
        Boolean array of shape ``(n_cells, n_genes)`` where ``True`` marks a positive cell.
    """
    return expr > tau


def and_mask(pos: np.ndarray, i: int, j: int) -> np.ndarray:
    """Return the AND-gate engagement mask for marker columns ``i`` and ``j``.

    Args:
        pos: Boolean positivity matrix, shape ``(n_cells, n_genes)``.
        i: Column index of marker A.
        j: Column index of marker B.

    Returns:
        Boolean vector of length ``n_cells`` that is ``True`` where a cell is A+ and B+.
    """
    return pos[:, i] & pos[:, j]


def not_mask(pos: np.ndarray, i: int, j: int) -> np.ndarray:
    """Return the NOT-gate engagement mask: activator ``i`` positive, blocker ``j`` negative.

    Args:
        pos: Boolean positivity matrix, shape ``(n_cells, n_genes)``.
        i: Column index of activator A.
        j: Column index of blocker B.

    Returns:
        Boolean vector of length ``n_cells`` that is ``True`` where a cell is A+ and B-.
    """
    return pos[:, i] & ~pos[:, j]


def group_fraction(
    engaged: np.ndarray, groups: np.ndarray, min_cells: int = 1
) -> pd.Series:
    """Fraction of engaged cells within each group, excluding under-powered groups.

    This is the primitive that keeps scoring per-group rather than pooled: it computes a
    within-group mean of a boolean engagement mask. Groups with fewer than ``min_cells``
    cells are returned as ``NaN`` so a handful of cells never produces a spurious 0 or 1.

    Args:
        engaged: Boolean engagement mask, length ``n_cells``.
        groups: Group label per cell (e.g. patient id or cell type), length ``n_cells``.
        min_cells: Minimum cells for a group to receive a score; smaller groups are ``NaN``.

    Returns:
        Series indexed by group label giving the engaged fraction, ``NaN`` where the group
        has fewer than ``min_cells`` cells.
    """
    df = pd.DataFrame({"engaged": np.asarray(engaged, dtype=float), "group": groups})
    grouped = df.groupby("group", observed=True)["engaged"]
    frac = grouped.mean()
    counts = grouped.size()
    frac[counts < min_cells] = np.nan
    return frac


@dataclass(frozen=True)
class CoverageSummary:
    """Summary of a pair's per-patient tumor coverage.

    Attributes:
        q_low: Lower-quantile coverage across patients (default Q0.10), the robustness floor.
        median: Median coverage across patients.
        mean: Mean coverage across patients.
        n_patients: Number of patients that met the minimum-cell threshold.
    """

    q_low: float
    median: float
    mean: float
    n_patients: int


def summarize_coverage(per_patient: pd.Series, q: float = 0.10) -> CoverageSummary:
    """Summarize per-patient coverage into a robustness floor and central tendency.

    The headline metric is the lower quantile ``q_low``: a pair only scores well if it
    covers the tumor in the *worst* patients, not just on average. Patients scored ``NaN``
    (too few cells) are dropped before summarizing.

    Args:
        per_patient: Per-patient coverage fractions (output of :func:`group_fraction`).
        q: Lower quantile to report as the robustness floor.

    Returns:
        A :class:`CoverageSummary`. All statistics are ``NaN`` when no patient qualifies.
    """
    vals = per_patient.dropna()
    if vals.empty:
        return CoverageSummary(np.nan, np.nan, np.nan, 0)
    return CoverageSummary(
        q_low=float(vals.quantile(q)),
        median=float(vals.median()),
        mean=float(vals.mean()),
        n_patients=int(vals.size),
    )


@dataclass(frozen=True)
class LiabilitySummary:
    """Worst-case healthy-tissue liability for a pair.

    Attributes:
        worst_frac: Highest engaged fraction across qualifying healthy cell types.
        worst_group: The cell type carrying that worst-case liability.
        n_types: Number of healthy cell types that met the minimum-cell threshold.
    """

    worst_frac: float
    worst_group: object
    n_types: int


def worst_healthy_liability(
    engaged: np.ndarray, celltypes: np.ndarray, min_cells: int = 20
) -> LiabilitySummary:
    """Worst-case healthy-cell-type engagement for a pair.

    Safety is governed by the *worst* healthy cell type, not the average, so this returns
    the maximum engaged fraction over cell types that clear ``min_cells``. A higher
    ``min_cells`` than the tumor side is appropriate because a false-positive liability on
    a rare, noisily-measured cell type would be over-weighted otherwise.

    Args:
        engaged: Boolean engagement mask over healthy cells, length ``n_cells``.
        celltypes: Healthy cell-type label per cell, length ``n_cells``.
        min_cells: Minimum cells for a cell type to count toward the worst case.

    Returns:
        A :class:`LiabilitySummary` with the worst fraction and the cell type that carries it.
    """
    frac = group_fraction(engaged, celltypes, min_cells=min_cells).dropna()
    if frac.empty:
        return LiabilitySummary(np.nan, None, 0)
    worst_group = frac.idxmax()
    return LiabilitySummary(
        worst_frac=float(frac.loc[worst_group]),
        worst_group=worst_group,
        n_types=int(frac.size),
    )


def pareto_front(
    df: pd.DataFrame, maximize: list[str], minimize: list[str]
) -> np.ndarray:
    """Boolean mask of Pareto-non-dominated rows over the given objectives.

    A row is dominated when another row is at least as good on every objective and strictly
    better on at least one. Rows with a ``NaN`` in any objective are treated as dominated
    (never on the frontier). Comparison is O(n^2) in rows, which is fine for the pair counts
    here (hundreds to low thousands).

    Args:
        df: One row per candidate pair.
        maximize: Column names where larger is better (e.g. tumor coverage floor, median).
        minimize: Column names where smaller is better (e.g. worst healthy liability).

    Returns:
        Boolean array aligned to ``df.index``; ``True`` marks a non-dominated (frontier) row.
    """
    cols = maximize + minimize
    sign = np.array([1.0] * len(maximize) + [-1.0] * len(minimize))
    # Flip minimized objectives so every column is "larger is better".
    vals = df[cols].to_numpy(dtype=float) * sign
    n = vals.shape[0]
    on_front = np.ones(n, dtype=bool)
    finite = np.isfinite(vals).all(axis=1)
    on_front &= finite
    for a in range(n):
        if not on_front[a]:
            continue
        for b in range(n):
            if a == b or not finite[b]:
                continue
            # b dominates a: b >= a on all, and b > a on at least one.
            if np.all(vals[b] >= vals[a]) and np.any(vals[b] > vals[a]):
                on_front[a] = False
                break
    return on_front
