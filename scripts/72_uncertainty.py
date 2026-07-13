"""Uncertainty for the nominated pair: bootstrap over patients, donor-level liability upper bound,
and a paired within-patient malignant-vs-benign delta.

Point estimates alone do not show a ranking is stable (reviewer concern). This script resamples the
unit of replication, patients (and donors, for the healthy side), rather than cells, so the
intervals reflect between-subject variation and cannot be inflated by cell count.

Outputs:
    results/tables/uncertainty_coverage.csv   Q0.10 / median bootstrap CIs + Pareto-membership prob
    results/tables/uncertainty_liability.csv  donor median vs bootstrap 95% upper bound of worst pop
    results/tables/uncertainty_paired.csv     paired malignant-minus-benign delta per patient + CI

Run (after the scan pipeline):
    uv run python scripts/72_uncertainty.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.scan import (
    DEFAULT_K, MIN_CELLS_DONOR, MIN_CELLS_TUMOR, MIN_DONORS, PROSTATE_PREFIX, Q_LOW,
    SIGNATURE_LEAK_GENES, load_scan_frames, positivity_matrix,
)

LEAD = ("FOLH1", "STEAP1")
CONTROL = ("FOLH1", "PSCA")
NON_TARGETABLE = {"KLK3", "KLK2", "ACPP", "SLC45A3"}
B = 2000
RNG_SEED = 0


def _per_patient_and(df: pd.DataFrame, genes: list[str]) -> tuple[list[str], np.ndarray]:
    """Per-patient AND-fraction tensor ``[P, G, G]`` for patients clearing MIN_CELLS_TUMOR."""
    P = positivity_matrix(df, genes, DEFAULT_K)
    pats = df["patient"].to_numpy()
    labels, mats = [], []
    for p in pd.unique(pats):
        m = pats == p
        if m.sum() < MIN_CELLS_TUMOR:
            continue
        Xg = P[m]
        mats.append((Xg.T @ Xg) / Xg.shape[0])
        labels.append(p)
    return labels, np.stack(mats)


def main() -> None:
    """Compute the bootstrap coverage CIs, Pareto-membership probability, liability upper bound."""
    mal, ben, hea, genes = load_scan_frames()
    gi = {g: i for i, g in enumerate(genes)}
    labels, T = _per_patient_and(mal, genes)   # [P, G, G], symmetric per patient
    n_pat = len(labels)
    rng = np.random.default_rng(RNG_SEED)

    # --- 1) Bootstrap over patients: Q0.10 and median CI for lead and control ---
    rows = []
    for name, (a, b) in [("PSMA x STEAP1", LEAD), ("PSMA x PSCA", CONTROL)]:
        v = T[:, gi[a], gi[b]]
        bq, bm = [], []
        for _ in range(B):
            s = v[rng.integers(0, n_pat, n_pat)]
            bq.append(np.quantile(s, Q_LOW)); bm.append(np.median(s))
        rows.append({
            "pair": name, "n_patients": n_pat,
            "q10": float(np.quantile(v, Q_LOW)),
            "q10_lo": float(np.percentile(bq, 2.5)), "q10_hi": float(np.percentile(bq, 97.5)),
            "median": float(np.median(v)),
            "median_lo": float(np.percentile(bm, 2.5)), "median_hi": float(np.percentile(bm, 97.5)),
            "frac_pat_ge_0.4": float((v >= 0.4).mean()), "frac_pat_ge_0.5": float((v >= 0.5).mean()),
        })

    # --- 2) Pareto-membership probability of the lead among clean surface pairs ---
    panel = pd.read_csv(RESULTS_TABLES / "surface_panel.csv").set_index("gene")
    surface = set(panel.index[panel["compartment"].isin(["surface", "membrane"])])
    clean = (surface - NON_TARGETABLE - set(SIGNATURE_LEAK_GENES))
    cl = [g for g in genes if g in clean]
    pa = pd.read_csv(RESULTS_TABLES / "pairs_and.csv")
    wmap = {frozenset((r.marker_a, r.marker_b)): r.worst_healthy_xprostate for _, r in pa.iterrows()}
    lead_key = frozenset(LEAD)
    I, J, risk, is_lead = [], [], [], []
    for ii in range(len(cl)):
        for jj in range(ii + 1, len(cl)):
            k = frozenset((cl[ii], cl[jj]))
            if k not in wmap:
                continue
            I.append(gi[cl[ii]]); J.append(gi[cl[jj]]); risk.append(wmap[k]); is_lead.append(k == lead_key)
    I, J, risk = np.array(I), np.array(J), np.array(risk)
    lead_pos = int(np.where(is_lead)[0][0])
    on = 0
    for _ in range(B):
        q10 = np.quantile(T[rng.integers(0, n_pat, n_pat)], Q_LOW, axis=0)
        cov = q10[I, J]
        lc, lr = cov[lead_pos], risk[lead_pos]
        if not np.any((cov >= lc) & (risk <= lr) & ((cov > lc) | (risk < lr))):
            on += 1
    pareto_prob = on / B
    cov_df = pd.DataFrame(rows)
    cov_df["lead_pareto_prob"] = np.where(cov_df["pair"] == "PSMA x STEAP1", pareto_prob, np.nan)
    cov_df.to_csv(RESULTS_TABLES / "uncertainty_coverage.csv", index=False)

    # --- 3) Donor-level upper bound for the lead's worst extra-prostatic liability ---
    a, b = LEAD
    Ph = positivity_matrix(hea, genes, DEFAULT_K)
    hh = pd.DataFrame({
        "pop": (hea["tissue_general"].astype(str) + " | " + hea["cell_type"].astype(str)).to_numpy(),
        "donor": hea["donor_id"].astype(str).to_numpy(),
        "eng": Ph[:, gi[a]] * Ph[:, gi[b]],
    })
    hh = hh[~hh["pop"].str.startswith(PROSTATE_PREFIX)]
    per = hh.groupby(["pop", "donor"]).agg(frac=("eng", "mean"), n=("eng", "size")).reset_index()
    per = per[per["n"] >= MIN_CELLS_DONOR]
    pop = per.groupby("pop").agg(med=("frac", "median"), nd=("donor", "nunique"))
    pop = pop[pop["nd"] >= MIN_DONORS]
    worst_pop = pop["med"].idxmax()
    dv = per.loc[per["pop"] == worst_pop, "frac"].to_numpy()
    ub = float(np.percentile([np.median(dv[rng.integers(0, len(dv), len(dv))]) for _ in range(B)], 95))
    pd.DataFrame([{
        "pair": "PSMA x STEAP1", "worst_pop": worst_pop, "n_donors": int(len(dv)),
        "donor_median": float(np.median(dv)), "donor_max": float(dv.max()), "donor_ub95": ub,
    }]).to_csv(RESULTS_TABLES / "uncertainty_liability.csv", index=False)

    # --- 4) Paired within-patient malignant-minus-benign delta for the lead ---
    def _cov(df):
        Pm = positivity_matrix(df, genes, DEFAULT_K)
        s = pd.DataFrame({"patient": df["patient"].astype(str).to_numpy(),
                          "e": Pm[:, gi[a]] * Pm[:, gi[b]]})
        g = s.groupby("patient").agg(cov=("e", "mean"), n=("e", "size"))
        return g[g["n"] >= MIN_CELLS_TUMOR]["cov"]

    mc, bc = _cov(mal), _cov(ben)
    common = mc.index.intersection(bc.index)
    delta = (mc.loc[common] - bc.loc[common]).to_numpy()
    db = [np.median(delta[rng.integers(0, len(delta), len(delta))]) for _ in range(B)]
    pd.DataFrame([{
        "pair": "PSMA x STEAP1", "n_paired_patients": int(len(common)),
        "median_delta": float(np.median(delta)),
        "delta_lo": float(np.percentile(db, 2.5)), "delta_hi": float(np.percentile(db, 97.5)),
        "frac_patients_positive": float((delta > 0).mean()),
    }]).to_csv(RESULTS_TABLES / "uncertainty_paired.csv", index=False)

    print(cov_df.round(3).to_string(index=False))
    print(f"\nLead Pareto-membership probability (bootstrap over patients): {pareto_prob:.3f}")
    print(f"Worst extra-prostatic liability {worst_pop}: donor median {np.median(dv):.3f}, "
          f"95% upper bound {ub:.3f} ({len(dv)} donors)")
    print(f"Paired malignant-benign delta: median {np.median(delta):.3f} "
          f"[{np.percentile(db,2.5):.3f}, {np.percentile(db,97.5):.3f}], "
          f"{(delta>0).mean()*100:.0f}% of {len(common)} paired patients positive")


if __name__ == "__main__":
    main()
