"""Apply scDblFinder calls to make the singlet tumor table the primary scoring input.

A doublet, two cells captured as one, can fake AND co-expression: marker A from one cell and
marker B from another read as a single A+B+ cell (Rule 8, Rule 9). Script ``12`` exported the
tumor counts, the container step (``doublet_scdblfinder.R``) called doublets per sample, and
``13`` showed the finding survives their removal. This script closes the loop by *applying* the
removal: it drops the doublet-flagged cells and writes the singlet table that every scoring
script reads through ``load_scan_frames``. Singlets are the primary analysis, not a side check.

Cells with no doublet call (should be none, since ``12`` exports every cell) are kept as
singlets rather than dropped: absence of a call is not proof of a doublet, and the count is
reported so any mismatch is visible.

Outputs:
    data/processed/tumor_cells_singlets.parquet   all-columns table, doublets removed
    results/tables/doublet_removal.csv            provenance: cells in/out, overall and malignant

Run (after scripts/10, scripts/12 and the container doublet step):
    uv run python scripts/14_apply_doublet_removal.py
"""

from __future__ import annotations

import pandas as pd

from dual_marker_discovery.config import DATA_INTERIM, DATA_PROCESSED, RESULTS_TABLES

TUMOR_ALL = DATA_PROCESSED / "tumor_cells.parquet"
CALLS = DATA_INTERIM / "doublets" / "doublet_calls.csv"
OUT = DATA_PROCESSED / "tumor_cells_singlets.parquet"


def main() -> None:
    """Remove scDblFinder doublets from the tumor table and write the singlet table."""
    if not CALLS.exists():
        raise FileNotFoundError(
            f"{CALLS} not found. Run the doublet step first:\n"
            "    uv run python scripts/12_export_for_doublets.py\n"
            "    podman run --rm -v \"$PWD\":/work -w /work <scdblfinder-image> \\\n"
            "        Rscript scripts/doublet_scdblfinder.R\n"
            "Singlets are the primary analysis, so this step is required, not optional."
        )

    tumor = pd.read_parquet(TUMOR_ALL)
    calls = pd.read_csv(CALLS)[["barcode", "doublet_class", "doublet_score"]]

    merged = tumor.merge(calls, left_on="cell_id", right_on="barcode", how="left")
    n_unmatched = int(merged["doublet_class"].isna().sum())

    is_doublet = merged["doublet_class"].eq("doublet")
    singlets = merged.loc[~is_doublet, tumor.columns].reset_index(drop=True)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    singlets.to_parquet(OUT, index=False)

    def _counts(df: pd.DataFrame) -> tuple[int, int, int]:
        mal = int(df["is_malignant"].sum())
        ben = int(df["malignant_anno"].isin(["normal", "altered_benign"]).sum())
        return len(df), mal, ben

    n_all, mal_all, ben_all = _counts(tumor)
    n_sng, mal_sng, ben_sng = _counts(singlets)
    prov = pd.DataFrame([{
        "n_cells_all": n_all,
        "n_cells_singlet": n_sng,
        "n_doublet_removed": int(is_doublet.sum()),
        "doublet_rate": int(is_doublet.sum()) / n_all,
        "n_malignant_all": mal_all,
        "n_malignant_singlet": mal_sng,
        "malignant_doublet_rate": (mal_all - mal_sng) / max(mal_all, 1),
        "n_benign_all": ben_all,
        "n_benign_singlet": ben_sng,
        "n_cells_without_call": n_unmatched,
    }])
    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    prov.to_csv(RESULTS_TABLES / "doublet_removal.csv", index=False)

    if n_unmatched:
        print(f"WARNING: {n_unmatched} cells had no doublet call; kept as singlets.")
    print(f"Wrote {OUT}: {n_sng:,} singlets of {n_all:,} cells "
          f"({int(is_doublet.sum()):,} doublets removed, {is_doublet.mean()*100:.1f}%)")
    print(f"Malignant: {mal_sng:,} of {mal_all:,} kept "
          f"({(mal_all - mal_sng)/max(mal_all,1)*100:.1f}% doublet); "
          f"benign prostate: {ben_sng:,} of {ben_all:,}")


if __name__ == "__main__":
    main()
