"""Export the tumor UMAP and per-cell panel positivity for the web app.

The app draws the AND gate. For a chosen pair of markers it colours every malignant-cohort cell by
which of the two it carries: neither, A only, B only, or both. The "both" population *is* the gate,
so the claim stops being a number in a table and becomes something you can see appear and disappear
as you change the pair.

This script is the only place that reads the 734 MB tumor ``.h5ad``. Everything it emits is small
enough to ship inside the app container:

    results/app/umap.json    ~65k cells: x, y, malignant flag, patient, and a 29-bit positivity mask

Why a bitmask. One bit per panel gene per cell, packed into a uint32, is 4 bytes per cell instead of
29 numbers. The browser reads the mask and tests two bits to colour a cell, so switching pairs is a
bit test rather than a refetch. The whole file gzips to a few hundred kilobytes, which is why the app
needs no more server than it already has.

Positivity is the SAME definition the scoring uses (raw count >= K, from the shared config), read
from the same singlet cells the analysis scored. If this file and the tables ever disagree, this
script is wrong, not the tables.

Run:
    uv run python scripts/91_export_app_umap.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from dual_marker_discovery.config import RESULTS

APP_DIR = RESULTS / "app"
OUT = APP_DIR / "umap.json"

# Quantise the UMAP coordinates to uint16. The embedding is a 2D picture, not a measurement: a
# 1/65535 grid is far finer than a screen pixel, and it halves the payload versus float32.
QUANT = 65535


def main() -> None:
    """Read the tumor h5ad, extract the embedding and panel positivity, and write umap.json."""
    import anndata as ad

    from dual_marker_discovery.config import DATA_RAW, RESULTS_TABLES
    from dual_marker_discovery.scan import DEFAULT_K

    h5ad = DATA_RAW / "tumor_localised_pca" / "tumor_localised_pca.h5ad"
    if not h5ad.exists():
        raise SystemExit(f"missing {h5ad}. Run scripts/00_fetch_data.py first.")

    panel = __import__("pandas").read_csv(RESULTS_TABLES / "surface_panel.csv")
    genes = [g for g in panel["gene"].tolist()]

    print(f"reading {h5ad} ...")
    adata = ad.read_h5ad(h5ad)

    # The embedding. CELLxGENE standardised h5ads are required to carry one; fail loudly rather than
    # silently drawing a scatter of something that is not a UMAP.
    key = next((k for k in ("X_umap", "X_UMAP", "X_umap_original") if k in adata.obsm), None)
    if key is None:
        raise SystemExit(f"no UMAP in obsm. Present: {list(adata.obsm)}")
    xy = np.asarray(adata.obsm[key][:, :2], dtype=np.float64)
    print(f"  embedding {key}: {xy.shape}")

    # Gene symbols live in var['feature_name'] in a CELLxGENE h5ad, not the index.
    sym = adata.var["feature_name"].astype(str).values if "feature_name" in adata.var else adata.var_names.astype(str).values
    present = [g for g in genes if g in set(sym)]
    missing = sorted(set(genes) - set(present))
    print(f"  panel genes present: {len(present)}/{len(genes)}" + (f"  missing: {missing}" if missing else ""))
    if len(present) > 32:
        raise SystemExit(f"{len(present)} genes will not fit a uint32 bitmask; widen the encoding.")

    # Malignant label: the cohort authors' own copy-number + signature call, the same one the scoring
    # uses. Adopted, not re-derived.
    mal_col = next((c for c in ("malignant_anno_merged", "malignant_anno", "malignant") if c in adata.obs), None)
    if mal_col is None:
        raise SystemExit(f"no malignant label in obs. Candidates: {[c for c in adata.obs if 'malig' in c.lower()]}")
    mal_raw = adata.obs[mal_col].astype(str).str.lower()
    malignant = mal_raw.isin({"malignant", "true", "1", "yes"}).values
    print(f"  malignant cells: {int(malignant.sum()):,} / {len(malignant):,}  (column {mal_col!r})")

    # Per-cell positivity, at the same threshold the scoring uses.
    idx = {g: i for i, g in enumerate(sym)}
    X = adata.X
    mask = np.zeros(adata.n_obs, dtype=np.uint32)
    for bit, g in enumerate(present):
        col = X[:, idx[g]]
        col = np.asarray(col.todense()).ravel() if sp.issparse(col) else np.asarray(col).ravel()
        mask |= ((col >= DEFAULT_K).astype(np.uint32) << np.uint32(bit))
    print(f"  positivity at raw count >= {DEFAULT_K}")

    # Patient, so the app can say which donor a cell came from.
    donor_col = next((c for c in ("donor_id", "patient", "sample") if c in adata.obs), None)
    donors = adata.obs[donor_col].astype(str).values if donor_col else np.array(["?"] * adata.n_obs)

    # Doublets. Two cells captured as one carry both markers and would fake exactly the co-expression
    # the AND gate looks for, so the scoring drops them BEFORE it counts anything. The picture has to
    # be drawn on the same cells the numbers were computed on, or it is arguing for a result the
    # analysis deliberately refused to claim. A cell with no call is kept: absence of a call is not
    # proof of a doublet.
    import pandas as pd

    from dual_marker_discovery.config import DATA_INTERIM

    calls_path = DATA_INTERIM / "doublets" / "doublet_calls.csv"
    singlets = np.ones(adata.n_obs, dtype=bool)
    have_calls = calls_path.exists()
    if have_calls:
        calls = pd.read_csv(calls_path).set_index("barcode")["doublet_class"]
        cls = calls.reindex(adata.obs_names.astype(str))
        singlets = (cls != "doublet").fillna(True).to_numpy()
        print(f"  scDblFinder: keeping {int(singlets.sum()):,} singlets, "
              f"dropping {int((~singlets).sum()):,} doublets")
    else:
        print("  WARNING: no doublet calls; the plot will include doublets. Run the scDblFinder container.")

    keep = singlets
    xy, mask, malignant, donors = xy[keep], mask[keep], malignant[keep], donors[keep]
    n_kept = int(keep.sum())
    print(f"  cells plotted: {n_kept:,}  (malignant {int(malignant.sum()):,})")

    donor_levels = sorted(set(donors.tolist()))
    donor_idx = {d: i for i, d in enumerate(donor_levels)}

    # Quantise the coordinates into a fixed box.
    lo, hi = xy.min(axis=0), xy.max(axis=0)
    span = np.where((hi - lo) == 0, 1.0, hi - lo)
    q = np.round((xy - lo) / span * QUANT).astype(np.uint16)

    APP_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "n": n_kept,
        "genes": present,          # bit i of `mask` is genes[i]
        "quant": QUANT,
        "donors": donor_levels,
        "x": q[:, 0].tolist(),
        "y": q[:, 1].tolist(),
        "mask": mask.tolist(),
        "malignant": malignant.astype(np.uint8).tolist(),
        "donor": [donor_idx[d] for d in donors],
        "k": int(DEFAULT_K),
        # The app says so on screen. If this is ever False, the picture and the tables disagree.
        "singlets": bool(have_calls),
    }
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    mb = OUT.stat().st_size / 1e6
    print(f"wrote {OUT}  ({mb:.1f} MB raw, gzips to roughly a third)")


if __name__ == "__main__":
    main()
