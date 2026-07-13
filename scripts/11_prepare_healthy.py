"""Prepare the Tabula Sapiens healthy reference into a per-cell panel table.

This is the safety denominator: for every normal cell type across ~24 organs, it holds the
panel genes as raw counts plus the true library size (Census ``raw_sum``, summed over all
genes before the panel subset), so CP10k values are recoverable and count-based positivity is
comparable to the tumor side.

Output: ``data/processed/healthy_cells.parquet`` with one row per cell, panel genes as raw
integer counts, ``total_counts``, ``cell_type``, ``tissue``, ``tissue_general``, ``donor_id``.

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


def main() -> None:
    """Build and write the healthy per-cell panel table."""
    genes = pd.read_csv(RESULTS_TABLES / "surface_panel.csv")["gene"].tolist()
    adata = ad.read_h5ad(TS_H5AD)
    symbols = gene_symbols(adata.var)

    counts, found, missing = panel_count_frame(symbols, adata.X, genes)

    obs = adata.obs
    meta = pd.DataFrame(index=adata.obs_names)
    meta["cell_id"] = adata.obs_names
    meta["cell_type"] = obs["cell_type"].astype(str).to_numpy()
    meta["tissue"] = obs["tissue"].astype(str).to_numpy()
    meta["tissue_general"] = obs["tissue_general"].astype(str).to_numpy()
    meta["donor_id"] = obs["donor_id"].astype(str).to_numpy()
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
