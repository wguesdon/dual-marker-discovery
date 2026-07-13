"""Pair-scan driver: tumor coverage, matched benign-prostate control, and healthy liability.

The scan reduces every group (a patient's malignant cells, a patient's benign/normal prostate
cells, or a healthy Tabula Sapiens cell population) to three summaries over the panel
positivity matrix ``P`` (cells x genes, 0/1):

* ``n`` — number of cells in the group,
* ``s`` — per-gene positive counts (``P.sum(axis=0)``),
* ``C`` — pairwise co-positive counts (``P.T @ P``).

From these, every gate fraction for the group follows without another pass over the cells:

* AND(i, j) = C[i, j] / n
* NOT(i as activator, j as blocker) = (s[i] - C[i, j]) / n
* OR(i, j) = (s[i] + s[j] - C[i, j]) / n
* single(i) = s[i] / n

Three references are scored so a nominated pair must clear all of them (Rule 7, Rule 8):

* **Tumor coverage** — per patient over malignant cells, summarized by a lower quantile so no
  high cell-count patient dominates.
* **Matched benign prostate** — the same cohort's adjacent-benign and normal epithelial cells,
  per patient. This is the same-sample control for tumor specificity: a pair expressed across
  all prostate cells would hit normal prostate too, so this must be low relative to coverage.
* **Healthy liability** — worst-case co-positive fraction over Tabula Sapiens populations,
  reported both across all organs and excluding the prostate (the extra-prostatic tissues that
  cannot be removed and drive dose-limiting toxicity).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Default positivity threshold: a cell is positive for a gene when its raw count is >= K.
# K = 1 is detection; the sensitivity analysis sweeps larger K (Rule 9).
DEFAULT_K = 1
MIN_CELLS_TUMOR = 20
MIN_CELLS_HEALTHY = 20
MIN_CELLS_BENIGN = 20
Q_LOW = 0.10
PROSTATE_PREFIX = "prostate gland | "


def load_scan_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    """Load prepared tables and return ``(malignant_df, benign_df, healthy_df, genes)``.

    ``benign_df`` is the tumor cohort's non-malignant epithelial cells (author annotation
    ``normal`` or ``altered_benign``), used as the matched normal-prostate control. Only genes
    present in both the tumor and healthy tables are kept.

    Returns:
        Malignant cells, matched benign-prostate cells, healthy cells, and the usable genes.
    """
    from .config import DATA_PROCESSED, RESULTS_TABLES

    genes = pd.read_csv(RESULTS_TABLES / "surface_panel.csv")["gene"].tolist()
    tumor = pd.read_parquet(DATA_PROCESSED / "tumor_cells.parquet")
    healthy = pd.read_parquet(DATA_PROCESSED / "healthy_cells.parquet")
    genes = [g for g in genes if g in tumor.columns and g in healthy.columns]
    malignant = tumor[tumor["is_malignant"]].copy()
    benign = tumor[tumor["malignant_anno"].isin(["normal", "altered_benign"])].copy()
    return malignant, benign, healthy, genes


def positivity_matrix(df: pd.DataFrame, genes: list[str], k: int = DEFAULT_K) -> np.ndarray:
    """Boolean-as-float positivity matrix ``count >= k`` for the panel genes.

    Args:
        df: Per-cell table with one raw-count column per gene.
        genes: Panel genes, in the desired column order.
        k: Positivity threshold on raw counts.

    Returns:
        Float32 array of shape ``(n_cells, n_genes)`` with 1.0 where ``count >= k``.
    """
    counts = df[genes].to_numpy()
    return (counts >= k).astype(np.float32)


def _group_stats(
    P: np.ndarray, groups: np.ndarray, min_cells: int
) -> list[tuple[object, int, np.ndarray, np.ndarray]]:
    """Return ``(label, n, s, C)`` for each group clearing ``min_cells``."""
    groups = np.asarray(groups)
    out: list[tuple[object, int, np.ndarray, np.ndarray]] = []
    for lab in pd.unique(groups):
        mask = groups == lab
        n = int(mask.sum())
        if n < min_cells:
            continue
        Xg = P[mask]
        out.append((lab, n, Xg.sum(axis=0), Xg.T @ Xg))
    return out


def _patient_gate_arrays(
    stats: list[tuple[object, int, np.ndarray, np.ndarray]]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Stack per-group AND, NOT and single fractions.

    Returns:
        ``(and_frac[P,G,G], not_frac[P,G,G], single_frac[P,G])``.
    """
    and_list, not_list, single_list = [], [], []
    for _lab, n, s, C in stats:
        andf = C / n
        and_list.append(andf)
        single_list.append(s / n)
        not_list.append(s[:, None] / n - andf)
    return np.stack(and_list), np.stack(not_list), np.stack(single_list)


def _split_label(lab: object) -> tuple[str, str]:
    """Split a ``"tissue | cell_type"`` label into ``(tissue, cell_type)``."""
    parts = str(lab).split(" | ")
    return (parts[0], parts[1]) if len(parts) == 2 else ("", parts[0])


def scan(
    malignant_df: pd.DataFrame,
    benign_df: pd.DataFrame,
    healthy_df: pd.DataFrame,
    genes: list[str],
    k: int = DEFAULT_K,
    min_cells_tumor: int = MIN_CELLS_TUMOR,
    min_cells_healthy: int = MIN_CELLS_HEALTHY,
    q_low: float = Q_LOW,
) -> dict[str, object]:
    """Run the AND / NOT / single scan against all three references.

    Args:
        malignant_df: Malignant cells with a ``patient`` column and per-gene count columns.
        benign_df: Matched benign/normal prostate cells (same columns).
        healthy_df: Tabula Sapiens cells with ``tissue_general`` and ``cell_type`` columns.
        genes: Panel genes to scan.
        k: Positivity threshold on raw counts.
        min_cells_tumor: Minimum cells for a patient group to be scored (tumor and benign).
        min_cells_healthy: Minimum cells for a healthy population to count as a liability.
        q_low: Lower quantile used as the per-patient robustness floor.

    Returns:
        Dict with keys ``"and"``, ``"not"``, ``"singles"`` (DataFrames) and ``"n_healthy_pops"``.
    """
    G = len(genes)

    Pt = positivity_matrix(malignant_df, genes, k)
    Pb = positivity_matrix(benign_df, genes, k)
    Ph = positivity_matrix(healthy_df, genes, k)

    tumor_stats = _group_stats(Pt, malignant_df["patient"].to_numpy(), min_cells_tumor)
    benign_stats = _group_stats(Pb, benign_df["patient"].to_numpy(), min_cells_tumor)
    healthy_key = (
        healthy_df["tissue_general"].astype(str) + " | " + healthy_df["cell_type"].astype(str)
    ).to_numpy()
    healthy_stats = _group_stats(Ph, healthy_key, min_cells_healthy)
    if not tumor_stats or not healthy_stats:
        raise RuntimeError("No qualifying tumor patients or healthy populations to score.")

    t_and, t_not, t_single = _patient_gate_arrays(tumor_stats)
    n_patients = t_and.shape[0]

    # Matched benign-prostate control (per patient). Median and worst-patient across patients.
    if benign_stats:
        b_and, b_not, b_single = _patient_gate_arrays(benign_stats)
        ben_and_med, ben_and_worst = np.median(b_and, 0), np.max(b_and, 0)
        ben_not_med, ben_not_worst = np.median(b_not, 0), np.max(b_not, 0)
        ben_single_med = np.median(b_single, 0)
    else:  # pragma: no cover - benign cells always present in this cohort
        nanGG, nanG = np.full((G, G), np.nan), np.full(G, np.nan)
        ben_and_med = ben_and_worst = ben_not_med = ben_not_worst = nanGG
        ben_single_med = nanG

    def _summ(arr: np.ndarray) -> dict[str, np.ndarray]:
        return {"q_low": np.quantile(arr, q_low, 0), "median": np.median(arr, 0),
                "mean": arr.mean(0)}

    and_t, not_t = _summ(t_and), _summ(t_not)

    # Healthy liabilities over all populations and excluding the prostate.
    h_and = np.stack([C / n for _l, n, _s, C in healthy_stats])
    h_single = np.stack([s / n for _l, n, s, _C in healthy_stats])
    h_not = np.stack([s[:, None] / n for _l, n, s, _C in healthy_stats]) - h_and
    h_labels = np.array([lab for lab, _n, _s, _C in healthy_stats], dtype=object)
    keep_xp = ~np.array([str(lab).startswith(PROSTATE_PREFIX) for lab in h_labels])

    def _worst(h_pij: np.ndarray, keep: np.ndarray | None = None):
        """Return ``(worst[G,G], label[G,G])`` over healthy populations, optionally masked."""
        if keep is not None:
            idx = np.where(keep)[0]
            sub = h_pij[idx]
            arg = idx[np.argmax(sub, 0)]
            return np.max(sub, 0), h_labels[arg]
        return np.max(h_pij, 0), h_labels[np.argmax(h_pij, 0)]

    and_all, and_all_lab = _worst(h_and)
    and_xp, and_xp_lab = _worst(h_and, keep_xp)
    not_all, not_all_lab = _worst(h_not)
    not_xp, not_xp_lab = _worst(h_not, keep_xp)

    # --- AND table (unordered pairs i < j) ---
    and_rows = []
    for a in range(G):
        for b in range(a + 1, G):
            t_all, c_all = _split_label(and_all_lab[a, b])
            t_xp, c_xp = _split_label(and_xp_lab[a, b])
            and_rows.append({
                "marker_a": genes[a], "marker_b": genes[b], "gate": "AND",
                "n_patients": n_patients,
                "tumor_q10": and_t["q_low"][a, b],
                "tumor_median": and_t["median"][a, b], "tumor_mean": and_t["mean"][a, b],
                "benign_prostate_median": ben_and_med[a, b],
                "benign_prostate_worst": ben_and_worst[a, b],
                "worst_healthy_all": and_all[a, b],
                "worst_healthy_all_tissue": t_all, "worst_healthy_all_celltype": c_all,
                "worst_healthy_xprostate": and_xp[a, b],
                "worst_xp_tissue": t_xp, "worst_xp_celltype": c_xp,
                "malignant_vs_benign": and_t["median"][a, b] - ben_and_med[a, b],
                "selectivity_xprostate": and_t["median"][a, b] - and_xp[a, b],
            })
    and_df = pd.DataFrame(and_rows)

    # --- NOT table (ordered: a = activator, b = blocker) ---
    not_rows = []
    for a in range(G):
        for b in range(G):
            if a == b:
                continue
            t_all, c_all = _split_label(not_all_lab[a, b])
            t_xp, c_xp = _split_label(not_xp_lab[a, b])
            not_rows.append({
                "activator": genes[a], "blocker": genes[b], "gate": "NOT",
                "n_patients": n_patients,
                "tumor_q10": not_t["q_low"][a, b], "tumor_median": not_t["median"][a, b],
                "tumor_mean": not_t["mean"][a, b],
                "benign_prostate_median": ben_not_med[a, b],
                "benign_prostate_worst": ben_not_worst[a, b],
                "worst_healthy_all": not_all[a, b],
                "worst_healthy_all_tissue": t_all, "worst_healthy_all_celltype": c_all,
                "worst_healthy_xprostate": not_xp[a, b],
                "worst_xp_tissue": t_xp, "worst_xp_celltype": c_xp,
                "malignant_vs_benign": not_t["median"][a, b] - ben_not_med[a, b],
                "selectivity_xprostate": not_t["median"][a, b] - not_xp[a, b],
            })
    not_df = pd.DataFrame(not_rows)

    # --- Singles table ---
    s_low, s_med = np.quantile(t_single, q_low, 0), np.median(t_single, 0)
    hs_all, hs_all_lab = np.max(h_single, 0), h_labels[np.argmax(h_single, 0)]
    idx_xp = np.where(keep_xp)[0]
    hs_xp = np.max(h_single[idx_xp], 0)
    hs_xp_lab = h_labels[idx_xp[np.argmax(h_single[idx_xp], 0)]]
    single_rows = []
    for i in range(G):
        t_all, c_all = _split_label(hs_all_lab[i])
        t_xp, c_xp = _split_label(hs_xp_lab[i])
        single_rows.append({
            "marker": genes[i], "n_patients": n_patients,
            "tumor_q10": s_low[i], "tumor_median": s_med[i],
            "benign_prostate_median": ben_single_med[i],
            "worst_healthy_all": hs_all[i],
            "worst_healthy_all_tissue": t_all, "worst_healthy_all_celltype": c_all,
            "worst_healthy_xprostate": hs_xp[i],
            "worst_xp_tissue": t_xp, "worst_xp_celltype": c_xp,
            "malignant_vs_benign": s_med[i] - ben_single_med[i],
            "selectivity_xprostate": s_med[i] - hs_xp[i],
        })
    single_df = pd.DataFrame(single_rows)

    return {"and": and_df, "not": not_df, "singles": single_df,
            "n_healthy_pops": len(healthy_stats), "n_patients": n_patients,
            "n_benign_patients": len(benign_stats)}
