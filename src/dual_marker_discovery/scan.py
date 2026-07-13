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
* **Healthy liability** — worst-case co-positive fraction over Tabula Sapiens populations, made
  donor-robust: within each ``tissue_general | cell_type`` population the fraction is computed per
  donor and summarized by the median across donors, so no single donor or tiny population sets the
  worst case. The healthy reference is assay-matched to the tumor (10x 3' v3 only), since a
  raw-count threshold is not comparable across assays. Reported both across all organs and
  excluding the prostate (the extra-prostatic tissues that cannot be removed and drive
  dose-limiting toxicity), each with its supporting donor and cell counts.
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
# Donor-robust healthy liability: a donor must contribute this many cells to a population to count,
# and a population must have this many qualifying donors to be scored at all.
MIN_CELLS_DONOR = 10
MIN_DONORS = 2
Q_LOW = 0.10
PROSTATE_PREFIX = "prostate gland | "


def load_scan_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    """Load prepared tables and return ``(malignant_df, benign_df, healthy_df, genes)``.

    The tumor input is the **singlet** table (``tumor_cells_singlets.parquet``), so scDblFinder
    doublets are removed before scoring and cannot inflate AND co-expression (Rule 8, Rule 9).
    That table is produced by ``scripts/14_apply_doublet_removal.py`` after the container doublet
    step; if it is missing the function raises rather than silently scoring all cells, because
    the singlet analysis is the primary one, not a fallback.

    ``benign_df`` is the tumor cohort's non-malignant epithelial cells (author annotation
    ``normal`` or ``altered_benign``), used as the matched normal-prostate control. Only genes
    present in both the tumor and healthy tables are kept.

    Returns:
        Malignant cells, matched benign-prostate cells, healthy cells, and the usable genes.

    Raises:
        FileNotFoundError: If the singlet tumor table has not been generated yet.
    """
    from .config import DATA_PROCESSED, RESULTS_TABLES

    tumor_path = DATA_PROCESSED / "tumor_cells_singlets.parquet"
    if not tumor_path.exists():
        raise FileNotFoundError(
            f"{tumor_path} not found. Doublet-removed singlets are the primary scoring input; "
            "generate them with\n"
            "    uv run python scripts/12_export_for_doublets.py\n"
            "    podman run --rm -v \"$PWD\":/work -w /work <scdblfinder-image> "
            "Rscript scripts/doublet_scdblfinder.R\n"
            "    uv run python scripts/14_apply_doublet_removal.py"
        )

    genes = pd.read_csv(RESULTS_TABLES / "surface_panel.csv")["gene"].tolist()
    tumor = pd.read_parquet(tumor_path)
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


def _donor_robust_healthy(
    P: np.ndarray, pop: np.ndarray, donor: np.ndarray,
    min_cells_donor: int, min_donors: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Donor-robust healthy liability: per-donor gate fractions, median across donors per population.

    Pooling healthy cells across donors would let a donor with many recovered cells drive a
    population's liability, the same bias avoided on the tumor side (Rule 8). Instead, within each
    population (``tissue_general | cell_type``) every donor contributing at least
    ``min_cells_donor`` cells gets its own AND / NOT / single fraction, and the population liability
    is the median across those donors. A population is kept only if at least ``min_donors`` donors
    qualify, so no single donor and no tiny population can set a worst-case liability.

    Args:
        P: Healthy positivity matrix, cells x genes (0/1), rows aligned with ``pop`` and ``donor``.
        pop: Population label (``tissue_general | cell_type``) per cell.
        donor: Donor id per cell.
        min_cells_donor: Minimum cells a donor must contribute to a population to count.
        min_donors: Minimum qualifying donors for a population to be scored.

    Returns:
        ``(and[Pop,G,G], not[Pop,G,G], single[Pop,G], labels[Pop], n_donors[Pop], n_cells[Pop])``,
        where ``not`` is ordered (activator i, blocker j).
    """
    G = P.shape[1]
    groups = pd.DataFrame({"pop": pop, "donor": donor}).groupby(
        ["pop", "donor"], sort=False).indices
    per_pop: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {}
    per_pop_cells: dict[str, int] = {}
    for (p, _d), rows in groups.items():
        if len(rows) < min_cells_donor:
            continue
        Xg = P[rows]
        n = Xg.shape[0]
        per_pop.setdefault(p, []).append((Xg.sum(axis=0) / n, (Xg.T @ Xg) / n))
        per_pop_cells[p] = per_pop_cells.get(p, 0) + n

    and_list, not_list, single_list = [], [], []
    labels, ndonors, ncells = [], [], []
    for p, donors in per_pop.items():
        if len(donors) < min_donors:
            continue
        d_single = np.stack([s for s, _C in donors])   # [D, G]
        d_and = np.stack([C for _s, C in donors])       # [D, G, G]
        d_not = d_single[:, :, None] - d_and            # [D, G, G], activator i minus co-positive
        and_list.append(np.median(d_and, 0))
        not_list.append(np.median(d_not, 0))
        single_list.append(np.median(d_single, 0))
        labels.append(p)
        ndonors.append(len(donors))
        ncells.append(per_pop_cells[p])

    if not labels:
        return (np.zeros((0, G, G)), np.zeros((0, G, G)), np.zeros((0, G)),
                np.array([], dtype=object), np.array([], dtype=int), np.array([], dtype=int))
    return (np.stack(and_list), np.stack(not_list), np.stack(single_list),
            np.array(labels, dtype=object), np.array(ndonors), np.array(ncells))


def scan(
    malignant_df: pd.DataFrame,
    benign_df: pd.DataFrame,
    healthy_df: pd.DataFrame,
    genes: list[str],
    k: int = DEFAULT_K,
    min_cells_tumor: int = MIN_CELLS_TUMOR,
    min_cells_donor: int = MIN_CELLS_DONOR,
    min_donors: int = MIN_DONORS,
    q_low: float = Q_LOW,
) -> dict[str, object]:
    """Run the AND / NOT / single scan against all three references.

    Args:
        malignant_df: Malignant cells with a ``patient`` column and per-gene count columns.
        benign_df: Matched benign/normal prostate cells (same columns).
        healthy_df: Tabula Sapiens cells with ``tissue_general``, ``cell_type`` and ``donor_id``.
        genes: Panel genes to scan.
        k: Positivity threshold on raw counts.
        min_cells_tumor: Minimum cells for a patient group to be scored (tumor and benign).
        min_cells_donor: Minimum cells a donor contributes to a healthy population to count.
        min_donors: Minimum qualifying donors for a healthy population to be scored.
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
    healthy_pop = (
        healthy_df["tissue_general"].astype(str) + " | " + healthy_df["cell_type"].astype(str)
    ).to_numpy()
    healthy_donor = healthy_df["donor_id"].astype(str).to_numpy()
    h_and, h_not, h_single, h_labels, h_ndonors, h_ncells = _donor_robust_healthy(
        Ph, healthy_pop, healthy_donor, min_cells_donor, min_donors)
    if not tumor_stats or h_labels.size == 0:
        raise RuntimeError("No qualifying tumor patients or donor-replicated healthy populations.")

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

    # Healthy liabilities are donor-robust (computed above); split at the prostate boundary.
    keep_xp = ~np.array([str(lab).startswith(PROSTATE_PREFIX) for lab in h_labels])

    def _worst(h_pij: np.ndarray, keep: np.ndarray | None = None):
        """Return ``(worst, label, n_donors, n_cells)`` (each [G,G]) over populations, optionally masked."""
        idx = np.arange(len(h_labels)) if keep is None else np.where(keep)[0]
        sub = h_pij[idx]
        arg = idx[np.argmax(sub, 0)]
        return np.max(sub, 0), h_labels[arg], h_ndonors[arg], h_ncells[arg]

    and_all, and_all_lab, and_all_nd, and_all_nc = _worst(h_and)
    and_xp, and_xp_lab, and_xp_nd, and_xp_nc = _worst(h_and, keep_xp)
    not_all, not_all_lab, not_all_nd, not_all_nc = _worst(h_not)
    not_xp, not_xp_lab, not_xp_nd, not_xp_nc = _worst(h_not, keep_xp)

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
                "worst_xp_n_donors": int(and_xp_nd[a, b]), "worst_xp_n_cells": int(and_xp_nc[a, b]),
                "worst_all_n_donors": int(and_all_nd[a, b]), "worst_all_n_cells": int(and_all_nc[a, b]),
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
                "worst_xp_n_donors": int(not_xp_nd[a, b]), "worst_xp_n_cells": int(not_xp_nc[a, b]),
                "worst_all_n_donors": int(not_all_nd[a, b]), "worst_all_n_cells": int(not_all_nc[a, b]),
                "malignant_vs_benign": not_t["median"][a, b] - ben_not_med[a, b],
                "selectivity_xprostate": not_t["median"][a, b] - not_xp[a, b],
            })
    not_df = pd.DataFrame(not_rows)

    # --- Singles table ---
    s_low, s_med = np.quantile(t_single, q_low, 0), np.median(t_single, 0)
    hs_all_arg = np.argmax(h_single, 0)
    hs_all, hs_all_lab = np.max(h_single, 0), h_labels[hs_all_arg]
    hs_all_nd, hs_all_nc = h_ndonors[hs_all_arg], h_ncells[hs_all_arg]
    idx_xp = np.where(keep_xp)[0]
    xp_arg = idx_xp[np.argmax(h_single[idx_xp], 0)]
    hs_xp = np.max(h_single[idx_xp], 0)
    hs_xp_lab = h_labels[xp_arg]
    hs_xp_nd, hs_xp_nc = h_ndonors[xp_arg], h_ncells[xp_arg]
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
            "worst_xp_n_donors": int(hs_xp_nd[i]), "worst_xp_n_cells": int(hs_xp_nc[i]),
            "worst_all_n_donors": int(hs_all_nd[i]), "worst_all_n_cells": int(hs_all_nc[i]),
            "malignant_vs_benign": s_med[i] - ben_single_med[i],
            "selectivity_xprostate": s_med[i] - hs_xp[i],
        })
    single_df = pd.DataFrame(single_rows)

    return {"and": and_df, "not": not_df, "singles": single_df,
            "n_healthy_pops": int(h_labels.size), "n_patients": n_patients,
            "n_benign_patients": len(benign_stats)}
