"""De-leaked sensitivity: does the nominated pair survive a malignant compartment defined without the
screened panel genes?

The cohort's malignant label uses the Liu and Wallace prostate-cancer signatures (which contain HPN and
EPCAM) plus CopyKAT aneuploidy. This is a partial control, not the authors' exact reannotation: it
recomputes the two signatures with all 29 panel genes removed, builds a leakage-free malignant proxy
(top de-leaked signature among CopyKAT-aneuploid cells, count-matched to the authors' malignant set),
and re-scores PSMA x STEAP1 and the PSMA-PSCA control on it. Stable coverage means the pair's signal is
not an artifact of the panel genes helping to define the compartment.

Output:
    results/tables/deleaked_sensitivity.csv

Run:
    uv run python scripts/71_deleaked_sensitivity.py
"""

from __future__ import annotations

import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as sp
from scipy.stats import spearmanr

from dual_marker_discovery.config import DATA_EXTERNAL, DATA_RAW, RESULTS_TABLES

TUMOR = DATA_RAW / "tumor_localised_pca" / "tumor_localised_pca.h5ad"
SIG = DATA_EXTERNAL / "signatures"
PAIRS = [("FOLH1", "STEAP1"), ("FOLH1", "PSCA")]
ANEUPLOID_FLOOR = 0.20  # CopyKAT correlation floor for a signature-independent aneuploid call


def main() -> None:
    """Recompute de-leaked signatures, build a leakage-free malignant proxy, re-score the pairs."""
    a = ad.read_h5ad(TUMOR)
    raw = a.raw
    syms = (raw.var["feature_name"].astype(str).to_numpy()
            if "feature_name" in raw.var else np.array(raw.var_names))
    panel = pd.read_csv(RESULTS_TABLES / "surface_panel.csv")["gene"].tolist()

    # Lognorm anndata on the full raw gene set for scanpy scoring.
    adn = ad.AnnData(X=raw.X.copy())
    adn.var_names = syms
    adn.var_names_make_unique()  # scanpy scoring needs a unique index; signatures match first occurrence
    sc.pp.normalize_total(adn, target_sum=1e4)
    sc.pp.log1p(adn)

    liu = pd.read_csv(SIG / "pca_liu_up.csv").iloc[:, 0].astype(str).tolist()
    wal = pd.read_csv(SIG / "pca_wallace_up.csv").iloc[:, 0].astype(str).tolist()
    present = set(syms)

    def score(genes: list[str], name: str) -> None:
        gl = [g for g in genes if g in present]
        sc.tl.score_genes(adn, gl, score_name=name)

    score(liu, "liu_full"); score(wal, "wal_full")
    score([g for g in liu if g not in panel], "liu_dl")
    score([g for g in wal if g not in panel], "wal_dl")
    sig_full = adn.obs[["liu_full", "wal_full"]].mean(1).to_numpy()
    sig_dl = adn.obs[["liu_dl", "wal_dl"]].mean(1).to_numpy()

    mal = (a.obs["malignant_anno_merged"].astype(str) == "malignant").to_numpy()
    n_mal = int(mal.sum())
    r_all = float(spearmanr(sig_full, sig_dl).correlation)
    r_mal = float(spearmanr(sig_full[mal], sig_dl[mal]).correlation)

    # Leakage-free malignant proxy: CopyKAT-aneuploid, then top-n_mal by de-leaked signature.
    aneu_val = pd.to_numeric(a.obs["cor.estimate.ck"], errors="coerce").to_numpy()
    aneu = np.nan_to_num(aneu_val, nan=-1.0) >= ANEUPLOID_FLOOR
    cand = np.where(aneu)[0]
    order = cand[np.argsort(sig_dl[cand])[::-1]]
    proxy = np.zeros(len(mal), dtype=bool)
    proxy[order[:n_mal]] = True
    overlap = float((proxy & mal).sum() / n_mal)

    X = raw.X.tocsc() if sp.issparse(raw.X) else sp.csc_matrix(raw.X)
    pos = {g: (np.asarray(X[:, np.where(syms == g)[0][0]].todense()).ravel() >= 1)
           for pr in PAIRS for g in pr if g in present}

    def cov(mask, x, y):
        return float((pos[x][mask] & pos[y][mask]).mean()) if mask.sum() else float("nan")

    rows = []
    for x, y in PAIRS:
        rows.append({
            "pair": f"{x.replace('FOLH1','PSMA')} x {y.replace('FOLH1','PSMA')}",
            "cov_author_malignant": cov(mal, x, y),
            "cov_deleaked_proxy": cov(proxy, x, y),
        })
    out = pd.DataFrame(rows)
    out["sig_spearman_all"] = round(r_all, 4)
    out["sig_spearman_malignant"] = round(r_mal, 4)
    out["proxy_overlap_with_author"] = round(overlap, 4)
    out["n_malignant"] = n_mal
    out.to_csv(RESULTS_TABLES / "deleaked_sensitivity.csv", index=False)

    print(f"Signature Spearman (full vs de-leaked): all cells {r_all:.3f}, malignant {r_mal:.3f}")
    print(f"De-leaked malignant proxy overlaps author label in {overlap*100:.0f}% of {n_mal} cells")
    print(out[["pair", "cov_author_malignant", "cov_deleaked_proxy"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
