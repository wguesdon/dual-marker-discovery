"""Join the panel to Human Protein Atlas protein-level evidence (Rule 12).

Transcript co-expression is not targetability. This script qualifies each panel marker with:

* **Surface accessibility** — the HPA subcellular localization. A cell-surface therapy needs the
  epitope at the plasma membrane; a marker localized to the Golgi or cytoplasm (e.g. prostein /
  SLC45A3) cannot be a surface target however co-expressed it is on the tumor.
* **Normal-tissue distribution** — the HPA consensus RNA nTPM across ~50 tissues, so the
  single-cell liabilities can be cross-checked against an orthogonal bulk reference.

Output:
    results/tables/protein_evidence.csv

Run:
    uv run python scripts/50_protein_evidence.py
"""

from __future__ import annotations

import subprocess

import pandas as pd

from dual_marker_discovery.config import DATA_EXTERNAL, RESULTS_TABLES

HPA_DIR = DATA_EXTERNAL / "hpa"
FILES = {
    "subcellular_location": "subcellular_location.tsv.zip",
    "rna_tissue_consensus": "rna_tissue_consensus.tsv.zip",
}
BASE_URL = "https://www.proteinatlas.org/download/tsv"


def _ensure(name: str) -> None:
    """Download an HPA table if it is not already present."""
    path = HPA_DIR / FILES[name]
    if path.exists() and path.stat().st_size > 1000:
        return
    HPA_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-fsSL", f"{BASE_URL}/{FILES[name]}", "-o", str(path)], check=True)


def main() -> None:
    """Build the protein-evidence table for every panel marker."""
    for name in FILES:
        _ensure(name)
    panel = pd.read_csv(RESULTS_TABLES / "surface_panel.csv")
    genes = panel["gene"].tolist()

    sub = pd.read_csv(HPA_DIR / FILES["subcellular_location"], sep="\t")
    cons = pd.read_csv(HPA_DIR / FILES["rna_tissue_consensus"], sep="\t")

    sub_by_gene = sub.set_index("Gene name")
    rows = []
    for g in genes:
        main_loc = add_loc = ""
        surface = False
        if g in sub_by_gene.index:
            r = sub_by_gene.loc[g]
            r = r.iloc[0] if isinstance(r, pd.DataFrame) else r
            main_loc = str(r.get("Main location", "") or "")
            add_loc = str(r.get("Additional location", "") or "")
            surface = ("Plasma membrane" in main_loc) or ("Plasma membrane" in add_loc)

        gc = cons[cons["Gene name"] == g]
        if len(gc):
            gc = gc.sort_values("nTPM", ascending=False)
            top = gc.head(5)
            top_tissues = "; ".join(f"{t}:{v:.0f}" for t, v in zip(top["Tissue"], top["nTPM"]))
            max_tissue = gc.iloc[0]["Tissue"]
            max_ntpm = float(gc.iloc[0]["nTPM"])
            prostate = gc[gc["Tissue"].str.lower() == "prostate"]
            prostate_ntpm = float(prostate["nTPM"].iloc[0]) if len(prostate) else float("nan")
        else:
            top_tissues, max_tissue, max_ntpm, prostate_ntpm = "", "", float("nan"), float("nan")

        rows.append({
            "gene": g,
            "compartment_curated": panel.loc[panel["gene"] == g, "compartment"].iloc[0],
            "hpa_main_location": main_loc,
            "hpa_additional_location": add_loc,
            "hpa_plasma_membrane": surface,
            "hpa_max_tissue": max_tissue,
            "hpa_max_ntpm": max_ntpm,
            "hpa_prostate_ntpm": prostate_ntpm,
            "hpa_top5_tissues_ntpm": top_tissues,
        })

    out = pd.DataFrame(rows)
    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    out.to_csv(RESULTS_TABLES / "protein_evidence.csv", index=False)

    print(f"Wrote protein_evidence.csv for {len(out)} markers")
    show = ["gene", "compartment_curated", "hpa_main_location", "hpa_plasma_membrane",
            "hpa_max_tissue", "hpa_max_ntpm"]
    print("\nSurface accessibility + top normal tissue (key markers):")
    key = out[out["gene"].isin(["FOLH1", "PSCA", "STEAP1", "STEAP2", "STEAP4", "SLC45A3",
                                "TMPRSS2", "TACSTD2", "CD276", "DLL3", "KLK3"])]
    print(key[show].to_string(index=False))
    n_surface = int(out["hpa_plasma_membrane"].sum())
    print(f"\nMarkers with HPA plasma-membrane evidence: {n_surface}/{len(out)}")


if __name__ == "__main__":
    main()
