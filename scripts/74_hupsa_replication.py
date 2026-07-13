"""Cross-cohort replication of the nominated pair in HuPSA (Cheng et al. 2024), an independent
prostate-cancer meta-analysis spanning localized, castration-resistant, and metastatic disease.

Replication is on the TUMOR-COVERAGE side (does PSMA x STEAP1 cover malignant cells in an independent
cohort, and does it hold in advanced disease); the healthy-liability side stays with Tabula Sapiens.
HuPSA mixes 10x 3' v2 and v3, so the primary comparison is restricted to v3 to match cohort 1's
chemistry, with a v2 sensitivity reported. Malignancy uses HuPSA's own cell-type states (AdPCa*, NEPCa,
Progenitor_like, KRT7), a label independent of cohort 1's Liu/Wallace + CopyKAT call, so it also sidesteps
the HPN/EPCAM leakage. Patient = HuPSA sample.

Outputs:
    results/tables/hupsa_replication.csv    per-pair coverage (v3, v2, all) vs cohort 1
    results/tables/hupsa_by_disease.csv     PSMA x STEAP1 coverage by disease group and cell state

Run (after scripts/hupsa_extract.R in the Seurat container):
    uv run python scripts/74_hupsa_replication.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.io as sio

from dual_marker_discovery.config import DATA_INTERIM, RESULTS_TABLES

HU = DATA_INTERIM / "hupsa"
MIN_CELLS = 20
Q_LOW = 0.10
MAL_STATES = ["AdPCa_AR+_1", "AdPCa_AR+_2", "AdPCa_AR+_3", "AdPCa_ARhi", "AdPCa_ARlo",
              "AdPCa_Proliferating", "NEPCa", "Progenitor_like", "KRT7"]
BENIGN_EPI = ["Basal", "Club"]
# cohort-1 (localized) headline for concordance, from the committed tables
C1 = {"FOLH1+STEAP1": {"median": 0.69, "q10": 0.45}, "FOLH1+PSCA": {"median": 0.10, "q10": 0.05}}


def _load() -> pd.DataFrame:
    """Build a per-cell panel table (raw counts + labels) from the R extraction."""
    m = sio.mmread(HU / "counts_panel.mtx").tocsr()          # genes x cells
    genes = [g.strip() for g in open(HU / "genes.tsv")]
    cells = pd.read_csv(HU / "barcodes.tsv", header=None)[0].tolist()
    counts = pd.DataFrame(m.T.toarray(), columns=genes)      # cells x genes
    md = pd.read_csv(HU / "metadata.csv", index_col=0).reset_index(drop=True)
    for c in ["sample", "histo", "chemsitry", "cell_type", "study"]:
        counts[c] = md[c].to_numpy()
    counts["is_malignant"] = counts["cell_type"].isin(MAL_STATES)
    counts["is_benign_epi"] = counts["cell_type"].isin(BENIGN_EPI)
    return counts


def _per_patient(df: pd.DataFrame, genes: list[str]) -> pd.Series:
    """Per-sample AND fraction over the given cell subset (samples with >= MIN_CELLS)."""
    pos = np.ones(len(df), dtype=bool)
    for g in genes:
        pos &= df[g].to_numpy() >= 1
    s = pd.DataFrame({"sample": df["sample"].to_numpy(), "pos": pos})
    agg = s.groupby("sample")["pos"].agg(["mean", "size"])
    return agg.loc[agg["size"] >= MIN_CELLS, "mean"]


def main() -> None:
    """Score PSMA x STEAP1 and PSMA-PSCA in HuPSA, matched to v3, split by disease."""
    df = _load()
    print(f"HuPSA: {len(df):,} cells | malignant {int(df.is_malignant.sum()):,} | "
          f"v3 {int((df.chemsitry=='V3').sum()):,} | v2 {int((df.chemsitry=='V2').sum()):,}")

    pairs = {"FOLH1+STEAP1": ["FOLH1", "STEAP1"], "FOLH1+PSCA": ["FOLH1", "PSCA"],
             "FOLH1": ["FOLH1"], "STEAP1": ["STEAP1"], "PSCA": ["PSCA"]}
    rows = []
    for name, gs in pairs.items():
        for chem, sub in [("v3", df[df.chemsitry == "V3"]), ("v2", df[df.chemsitry == "V2"]),
                          ("all", df)]:
            cov = _per_patient(sub[sub.is_malignant], gs)
            rows.append({"pair": name, "chemistry": chem, "n_samples": int(len(cov)),
                         "median": float(cov.median()) if len(cov) else np.nan,
                         "q10": float(cov.quantile(Q_LOW)) if len(cov) else np.nan})
    rep = pd.DataFrame(rows)
    for name in ["FOLH1+STEAP1", "FOLH1+PSCA"]:
        rep.loc[rep.pair == name, "cohort1_median"] = C1[name]["median"]
        rep.loc[rep.pair == name, "cohort1_q10"] = C1[name]["q10"]
    rep.to_csv(RESULTS_TABLES / "hupsa_replication.csv", index=False)

    # By disease group and by malignant cell state (all chemistry; the state effect dwarfs the
    # v2/v3 difference, and this covers every disease group). Tumor-only, so chemistry is a
    # second-order confound named in the report.
    mal_all = df[df.is_malignant]
    dis = []
    for hg, sub in mal_all.groupby("histo"):
        cov = _per_patient(sub, ["FOLH1", "STEAP1"])
        if len(cov):
            dis.append({"group": hg, "kind": "disease", "n_samples": int(len(cov)),
                        "median_cov": float(cov.median()), "n_malignant": int(len(sub))})
    for st, sub in mal_all.groupby("cell_type"):
        pos = (sub["FOLH1"] >= 1) & (sub["STEAP1"] >= 1)
        dis.append({"group": st, "kind": "cell_state", "n_samples": np.nan,
                    "median_cov": float(pos.mean()), "n_malignant": int(len(sub))})
    by_dis = pd.DataFrame(dis).sort_values(["kind", "median_cov"], ascending=[True, False])
    by_dis.to_csv(RESULTS_TABLES / "hupsa_by_disease.csv", index=False)
    v3 = df[(df.chemsitry == "V3") & df.is_malignant]

    # Malignant vs benign-epithelial delta (v3), paired within sample.
    mc = _per_patient(v3, ["FOLH1", "STEAP1"])
    bc = _per_patient(df[(df.chemsitry == "V3") & df.is_benign_epi], ["FOLH1", "STEAP1"])
    common = mc.index.intersection(bc.index)
    delta = (mc.loc[common] - bc.loc[common])

    print("\n=== PSMA x STEAP1 / PSMA-PSCA coverage (median across samples) ===")
    show = rep[rep.pair.isin(["FOLH1+STEAP1", "FOLH1+PSCA"])]
    print(show.round(3).to_string(index=False))
    print("\n=== PSMA x STEAP1 by disease group (v3) ===")
    print(by_dis[by_dis.kind == "disease"][["group", "n_samples", "median_cov", "n_malignant"]]
          .round(3).to_string(index=False))
    print("\n=== PSMA x STEAP1 by malignant cell state (v3, pooled) ===")
    print(by_dis[by_dis.kind == "cell_state"][["group", "median_cov", "n_malignant"]]
          .round(3).to_string(index=False))
    print(f"\nMalignant vs benign-epithelial delta (v3): median {float(delta.median()):.3f} "
          f"over {len(common)} paired samples, positive in {float((delta>0).mean())*100:.0f}%")


if __name__ == "__main__":
    main()
