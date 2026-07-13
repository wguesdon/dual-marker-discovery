"""Prepare the tumor cohort into a per-cell panel table with a validated malignant label.

Malignant identity uses the cohort authors' merged annotation
(``malignant_anno_merged == 'malignant'``), which is derived from copy-number inference and
expression signatures rather than a marker guess (Rule 13). The patient key is ``sample_id``
(24 patients). Raw counts come from ``adata.raw`` (full gene set), so the per-cell library
size is exact.

Output: ``data/processed/tumor_cells.parquet`` with one row per cell, the panel genes as raw
integer counts, ``total_counts``, and the labels needed for per-patient scoring.

Run:
    uv run python scripts/10_prepare_tumor.py
"""

from __future__ import annotations

import anndata as ad
import pandas as pd

from dual_marker_discovery.config import DATA_PROCESSED, DATA_RAW, RESULTS_TABLES
from dual_marker_discovery.prepare import gene_symbols, library_size, panel_count_frame

TUMOR_H5AD = DATA_RAW / "tumor_localised_pca" / "tumor_localised_pca.h5ad"
OUT = DATA_PROCESSED / "tumor_cells.parquet"


def main() -> None:
    """Build and write the tumor per-cell panel table."""
    genes = pd.read_csv(RESULTS_TABLES / "surface_panel.csv")["gene"].tolist()
    adata = ad.read_h5ad(TUMOR_H5AD)
    raw = adata.raw
    symbols = gene_symbols(raw.var)

    counts, found, missing = panel_count_frame(symbols, raw.X, genes)
    counts.index = adata.obs_names

    obs = adata.obs
    meta = pd.DataFrame(index=adata.obs_names)
    meta["cell_id"] = adata.obs_names
    meta["patient"] = obs["sample_id"].astype(str).to_numpy()
    meta["malignant_anno"] = obs["malignant_anno_merged"].astype(str).to_numpy()
    meta["is_malignant"] = meta["malignant_anno"] == "malignant"
    meta["celltype_major"] = obs["celltype_major_v2"].astype(str).to_numpy()
    meta["cell_type"] = obs["cell_type"].astype(str).to_numpy()
    meta["sample_type"] = obs["type"].astype(str).to_numpy()
    meta["isup_clinical"] = obs["ISUP_clinical"].astype(str).to_numpy()
    meta["total_counts"] = library_size(raw.X)

    out_df = pd.concat([meta.reset_index(drop=True), counts.reset_index(drop=True)], axis=1)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(OUT, index=False)

    n_mal = int(meta["is_malignant"].sum())
    per_pat = meta.loc[meta["is_malignant"], "patient"].value_counts()
    print(f"Wrote {OUT}: {len(out_df):,} cells x {len(found)} panel genes")
    print(f"Panel genes found: {len(found)}; missing: {missing}")
    print(f"Malignant cells: {n_mal:,} across {per_pat.size} patients")
    print(f"Patients with >=20 malignant: {(per_pat >= 20).sum()}; "
          f">=50: {(per_pat >= 50).sum()}")
    print("\nmalignant_anno breakdown:")
    print(meta["malignant_anno"].value_counts().to_string())


if __name__ == "__main__":
    main()
