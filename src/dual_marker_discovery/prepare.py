"""Helpers to turn an AnnData into a tidy per-cell panel table.

Both references are reduced to the same shape: one row per cell, the panel genes as
raw-count columns, the true per-cell library size, and the grouping labels (patient or cell
type). Positivity is later defined as ``count >= k`` on these raw counts and swept over
``k`` for sensitivity, rather than a single ``count > 0`` call (Rule 9). The library size is
kept so a CP10k-normalized value can be recovered for figures without re-reading the atlas.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.sparse as sp


def gene_symbols(var: pd.DataFrame) -> np.ndarray:
    """Return the gene-symbol array from a ``.var`` frame (``feature_name`` or the index)."""
    if "feature_name" in var.columns:
        return var["feature_name"].astype(str).to_numpy()
    return var.index.astype(str).to_numpy()


def panel_count_frame(
    symbols: np.ndarray, X, genes: list[str]
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Extract raw counts for the panel genes into a dense integer DataFrame.

    Args:
        symbols: Gene symbol per column of ``X``, length ``n_genes``.
        X: Count matrix (sparse or dense), shape ``(n_cells, n_genes)``.
        genes: Panel gene symbols to extract, in the desired output order.

    Returns:
        A tuple ``(frame, found, missing)`` where ``frame`` has one integer column per found
        gene (in panel order), ``found`` lists the genes present, and ``missing`` lists the
        genes absent from ``symbols``.
    """
    sym_to_col: dict[str, int] = {}
    for col, s in enumerate(symbols):
        # First occurrence wins if a symbol is duplicated in the atlas var.
        sym_to_col.setdefault(s, col)
    found = [g for g in genes if g in sym_to_col]
    missing = [g for g in genes if g not in sym_to_col]
    cols = [sym_to_col[g] for g in found]
    sub = X[:, cols]
    dense = sub.toarray() if sp.issparse(sub) else np.asarray(sub)
    dense = np.rint(dense).astype(np.int32)
    frame = pd.DataFrame(dense, columns=found)
    return frame, found, missing


def library_size(X) -> np.ndarray:
    """Return per-cell total counts (row sums) as a 1-D float array."""
    s = X.sum(axis=1)
    return np.asarray(s).ravel().astype(np.float64)
