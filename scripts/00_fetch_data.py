"""Fetch the tumor and healthy references and verify access before any scoring (Rule 1).

Two datasets:

* **Tumor discovery cohort** — CZ CELLxGENE "Single-cell atlas of 24 hormone therapy-naive
  localised prostate cancers" (68,322 cells, 24 donors, DOI 10.1101/2024.10.23.619925). A
  standardized ``.h5ad`` with ``donor_id`` per patient and HGNC gene symbols in
  ``var['feature_name']``. Downloaded from the CELLxGENE Discover CDN.
* **Healthy reference** — Tabula Sapiens, pulled through the CELLxGENE Census with a
  server-side filter to the panel genes only, so the ~0.5M-cell atlas never leaves the
  server at full width. Carries ``cell_type``, ``tissue`` and ``donor_id``.

This script does not score anything. Its job is to confirm the data actually carries what the
analysis needs: the panel genes, patient identity, and malignant / cell-type labels. It writes
``results/tables/data_manifest.csv`` and prints the tumor ``.obs`` categorical columns so the
malignant label used by ``10_prepare_tumor.py`` is chosen from what is really there.

Run:
    uv run python scripts/00_fetch_data.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import anndata as ad
import pandas as pd

from dual_marker_discovery.config import DATA_RAW, RESULTS_TABLES

# Verified CELLxGENE Discover download (HTTP 200, 734,490,686 bytes).
TUMOR_URL = "https://datasets.cellxgene.cziscience.com/68b23fda-7191-46a5-8870-819feca3e66e.h5ad"
TUMOR_PATH = DATA_RAW / "tumor_localised_pca" / "tumor_localised_pca.h5ad"

# Tabula Sapiens via the Census. Pin an explicit LTS release for reproducibility.
CENSUS_VERSION = "2025-01-30"
TS_PATH = DATA_RAW / "tabula_sapiens" / "tabula_sapiens_panel.h5ad"

PANEL_CSV = RESULTS_TABLES / "surface_panel.csv"


def _panel_genes() -> list[str]:
    """Read the panel gene symbols from the committed surface-panel table."""
    if not PANEL_CSV.exists():
        raise FileNotFoundError(
            f"{PANEL_CSV} missing. Run scripts/01_curate_surface_panel.py first."
        )
    return pd.read_csv(PANEL_CSV)["gene"].tolist()


def download_tumor() -> None:
    """Download the tumor cohort ``.h5ad`` if it is not already present."""
    TUMOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TUMOR_PATH.exists() and TUMOR_PATH.stat().st_size > 700_000_000:
        print(f"Tumor cohort already present: {TUMOR_PATH} "
              f"({TUMOR_PATH.stat().st_size:,} bytes)")
        return
    print(f"Downloading tumor cohort -> {TUMOR_PATH} ...")
    subprocess.run(["curl", "-fsSL", TUMOR_URL, "-o", str(TUMOR_PATH)], check=True)
    print(f"Downloaded {TUMOR_PATH.stat().st_size:,} bytes")


def pull_tabula_sapiens(genes: list[str]) -> None:
    """Pull the Tabula Sapiens panel subset from the CELLxGENE Census.

    Args:
        genes: Panel gene symbols to keep. Only these columns of the atlas cross the wire.
    """
    TS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TS_PATH.exists():
        print(f"Tabula Sapiens panel subset already present: {TS_PATH}")
        return
    import cellxgene_census

    print(f"Opening Census {CENSUS_VERSION} and pulling Tabula Sapiens panel subset ...")
    with cellxgene_census.open_soma(census_version=CENSUS_VERSION) as census:
        datasets = census["census_info"]["datasets"].read().concat().to_pandas()
        ts_ids = datasets.loc[
            datasets["collection_name"] == "Tabula Sapiens", "dataset_id"
        ].tolist()
        if not ts_ids:
            raise RuntimeError("No Tabula Sapiens datasets found in this Census release.")
        adata = cellxgene_census.get_anndata(
            census,
            organism="Homo sapiens",
            measurement_name="RNA",
            X_name="raw",
            obs_value_filter=f"dataset_id in {ts_ids!r} and is_primary_data == True",
            var_value_filter=f"feature_name in {genes!r}",
            obs_column_names=[
                "cell_type", "tissue", "tissue_general", "donor_id",
                "assay", "disease", "sex",
                # raw_sum is the per-cell library size over ALL genes; required to
                # normalize (CP10k) correctly after subsetting to panel genes.
                "raw_sum", "nnz",
            ],
            var_column_names=["feature_id", "feature_name"],
        )
    adata.write_h5ad(TS_PATH)
    print(f"Wrote {TS_PATH}: {adata.n_obs:,} cells x {adata.n_vars} genes")


def _gene_column(var: pd.DataFrame) -> pd.Series:
    """Return the gene-symbol series from a ``.var`` frame (feature_name or the index)."""
    if "feature_name" in var.columns:
        return var["feature_name"].astype(str)
    return pd.Series(var.index.astype(str), index=var.index)


def inspect_and_manifest(genes: list[str]) -> None:
    """Verify labels and panel-gene coverage, print obs categoricals, write the manifest.

    Args:
        genes: Panel gene symbols expected in both datasets.
    """
    rows: list[dict] = []

    # --- Tumor cohort (backed read: only metadata loaded) ---
    tumor = ad.read_h5ad(TUMOR_PATH, backed="r")
    tumor_syms = set(_gene_column(tumor.var))
    tumor_found = [g for g in genes if g in tumor_syms]
    tumor_missing = [g for g in genes if g not in tumor_syms]
    donor_col = "donor_id" if "donor_id" in tumor.obs.columns else None
    n_donors = int(tumor.obs[donor_col].nunique()) if donor_col else 0
    rows.append({
        "dataset": "tumor_localised_pca",
        "n_cells": int(tumor.n_obs),
        "n_genes_total": int(tumor.n_vars),
        "n_donors": n_donors,
        "panel_genes_found": len(tumor_found),
        "panel_genes_missing": ";".join(tumor_missing) or "none",
    })

    print("\n=== TUMOR COHORT obs columns ===")
    print(list(tumor.obs.columns))
    print("\n=== TUMOR categorical obs value counts (<=40 levels) ===")
    for col in tumor.obs.columns:
        s = tumor.obs[col]
        if s.dtype == "object" or str(s.dtype) == "category":
            n = s.nunique()
            if n <= 40:
                print(f"\n[{col}] ({n} levels)")
                print(s.value_counts().head(40).to_string())
    print(f"\nPanel genes found in tumor: {len(tumor_found)}/{len(genes)}; "
          f"missing: {tumor_missing}")

    # --- Healthy reference ---
    if TS_PATH.exists():
        ts = ad.read_h5ad(TS_PATH, backed="r")
        ts_syms = set(_gene_column(ts.var))
        ts_found = [g for g in genes if g in ts_syms]
        ts_missing = [g for g in genes if g not in ts_syms]
        rows.append({
            "dataset": "tabula_sapiens",
            "n_cells": int(ts.n_obs),
            "n_genes_total": int(ts.n_vars),
            "n_donors": int(ts.obs["donor_id"].nunique()) if "donor_id" in ts.obs else 0,
            "panel_genes_found": len(ts_found),
            "panel_genes_missing": ";".join(ts_missing) or "none",
        })
        print("\n=== HEALTHY (Tabula Sapiens) ===")
        print(f"cells={ts.n_obs:,}  cell_types={ts.obs['cell_type'].nunique()}  "
              f"tissues={ts.obs['tissue'].nunique()}  donors={ts.obs['donor_id'].nunique()}")
        print(f"Panel genes found in TS: {len(ts_found)}/{len(genes)}; missing: {ts_missing}")

    manifest = pd.DataFrame(rows)
    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    out = RESULTS_TABLES / "data_manifest.csv"
    manifest.to_csv(out, index=False)
    print(f"\nWrote {out}")
    print(manifest.to_string(index=False))


def main() -> None:
    """Fetch both references and run the access-verification gate."""
    genes = _panel_genes()
    download_tumor()
    try:
        pull_tabula_sapiens(genes)
    except Exception as exc:  # noqa: BLE001 - surface the failure, do not mask it
        print(f"WARNING: Tabula Sapiens Census pull failed: {exc}", file=sys.stderr)
    inspect_and_manifest(genes)


if __name__ == "__main__":
    main()
