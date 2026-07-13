"""Prepare the Tabula Sapiens healthy reference into a per-cell panel table.

This is the safety denominator. It is restricted to the ``10x 3' v3`` assay, the same chemistry
as the tumor cohort (EFO:0009922), because a raw-count positivity threshold has no common meaning
across assays: Tabula Sapiens 2.0 mixes 10x 3' v3, 10x 5' v2, Smart-seq2 and Smart-seq3, whose
count distributions and detection sensitivities differ. Matching the assay keeps count-based
positivity comparable between the tumor and healthy sides. The true library size (Census
``raw_sum``, summed over all genes before the panel subset) is retained so CP10k is recoverable.

Output: ``data/processed/healthy_cells.parquet`` with one row per cell, panel genes as raw
integer counts, ``total_counts``, ``cell_type``, ``tissue``, ``tissue_general``, ``donor_id``,
``assay``.

Run:
    uv run python scripts/11_prepare_healthy.py
"""

from __future__ import annotations

import anndata as ad
import numpy as np
import pandas as pd

from dual_marker_discovery.config import DATA_PROCESSED, DATA_RAW, RESULTS_TABLES
from dual_marker_discovery.prepare import gene_symbols, library_size, panel_count_frame

TS_H5AD = DATA_RAW / "tabula_sapiens" / "tabula_sapiens_panel.h5ad"
OUT = DATA_PROCESSED / "healthy_cells.parquet"
ASSAY = "10x 3' v3"  # match the tumor cohort chemistry (EFO:0009922)


def main() -> None:
    """Build and write the healthy per-cell panel table (10x 3' v3 only)."""
    genes = pd.read_csv(RESULTS_TABLES / "surface_panel.csv")["gene"].tolist()
    adata = ad.read_h5ad(TS_H5AD)

    # Assay-match to the tumor cohort. Raw-count thresholds are only comparable within one assay.
    if "assay" in adata.obs.columns:
        n_before = adata.n_obs
        adata = adata[adata.obs["assay"].astype(str) == ASSAY].copy()
        print(f"Assay filter {ASSAY!r}: kept {adata.n_obs:,} of {n_before:,} cells")
    else:
        raise KeyError("No 'assay' column in the Tabula Sapiens h5ad; re-pull with scripts/00.")

    symbols = gene_symbols(adata.var)
    counts, found, missing = panel_count_frame(symbols, adata.X, genes)

    obs = adata.obs
    meta = pd.DataFrame(index=adata.obs_names)
    meta["cell_id"] = adata.obs_names
    meta["cell_type"] = obs["cell_type"].astype(str).to_numpy()
    meta["tissue"] = obs["tissue"].astype(str).to_numpy()
    meta["tissue_general"] = obs["tissue_general"].astype(str).to_numpy()
    meta["donor_id"] = obs["donor_id"].astype(str).to_numpy()
    meta["assay"] = obs["assay"].astype(str).to_numpy()
    # raw_sum is the library size over all genes; fall back to the panel-subset row sum only
    # if the column is absent (it should always be present from the Census pull).
    if "raw_sum" in obs.columns:
        meta["total_counts"] = obs["raw_sum"].to_numpy().astype(np.float64)
    else:
        meta["total_counts"] = library_size(adata.X)

    out_df = pd.concat([meta.reset_index(drop=True), counts.reset_index(drop=True)], axis=1)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(OUT, index=False)

    print(f"Wrote {OUT}: {len(out_df):,} cells x {len(found)} panel genes")
    print(f"Panel genes found: {len(found)}; missing: {missing}")
    print(f"Cell types: {meta['cell_type'].nunique()}; tissues: {meta['tissue'].nunique()}; "
          f"donors: {meta['donor_id'].nunique()}")
    ok = (meta["total_counts"] > 0).mean()
    print(f"Cells with positive library size: {ok:.4f}")


if __name__ == "__main__":
    main()
