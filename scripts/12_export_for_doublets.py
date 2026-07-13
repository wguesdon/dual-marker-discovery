"""Export tumor counts for R-based doublet detection (Python -> disk -> R handoff).

A doublet, two cells captured as one, can fake AND co-expression: marker A from one cell and
marker B from another read as a single A+B+ cell. scDblFinder (the sc-best-practices R tool) is
run in a container on these exports, and the calls are read back in Python. To keep the exchange
file small, only the top ~2000 high-variance genes are written; scDblFinder does its own feature
selection and normalization from raw counts.

Writes to ``data/interim/doublets/``:
    counts.mtx      genes x cells sparse counts (MatrixMarket)
    barcodes.tsv    cell id per column
    samples.tsv     sample_id per column (per-sample doublet calling)
    cell_meta.tsv   barcode, sample, malignant_anno (for downstream concordance)

Run:
    uv run python scripts/12_export_for_doublets.py
"""

from __future__ import annotations

import anndata as ad
import numpy as np
import pandas as pd
import scipy.io as sio
import scipy.sparse as sp

from dual_marker_discovery.config import DATA_INTERIM, DATA_RAW

TUMOR_H5AD = DATA_RAW / "tumor_localised_pca" / "tumor_localised_pca.h5ad"
OUT = DATA_INTERIM / "doublets"
N_HVG = 2000


def main() -> None:
    """Select high-variance genes and export counts, barcodes, samples and metadata."""
    OUT.mkdir(parents=True, exist_ok=True)
    adata = ad.read_h5ad(TUMOR_H5AD)
    raw = adata.raw
    X = raw.X.tocsc() if sp.issparse(raw.X) else sp.csc_matrix(raw.X)
    n = X.shape[0]

    # Per-gene variance on raw counts (sparse), pick the top N_HVG.
    sums = np.asarray(X.sum(axis=0)).ravel()
    sumsq = np.asarray(X.multiply(X).sum(axis=0)).ravel()
    mean = sums / n
    var = sumsq / n - mean**2
    hvg = np.argsort(var)[-N_HVG:]
    sub = X[:, hvg].T.tocoo()  # genes x cells

    sio.mmwrite(str(OUT / "counts.mtx"), sub)
    pd.Series(adata.obs_names).to_csv(OUT / "barcodes.tsv", index=False, header=False)
    pd.Series(adata.obs["sample_id"].astype(str).to_numpy()).to_csv(
        OUT / "samples.tsv", index=False, header=False)
    pd.DataFrame({
        "barcode": adata.obs_names,
        "sample": adata.obs["sample_id"].astype(str).to_numpy(),
        "malignant_anno": adata.obs["malignant_anno_merged"].astype(str).to_numpy(),
    }).to_csv(OUT / "cell_meta.tsv", sep="\t", index=False)

    print(f"Exported {sub.shape[0]} genes x {sub.shape[1]} cells to {OUT}/counts.mtx "
          f"(nnz={sub.nnz:,})")
    print(f"Samples: {adata.obs['sample_id'].nunique()}")


if __name__ == "__main__":
    main()
