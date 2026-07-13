# Research plan: technical execution

The `docs/prd.md` file is the contract, what the project must deliver. This file is how it gets built:
the pipeline scripts, the tables they emit, and the order of work. Every number in `reports/report.qmd`
is bound to a committed table in `results/tables/`, so the report rebuilds from tables with no network
or model call.

## Environment

Python is managed with `uv`. The base environment is deliberately light (numpy, pandas, scipy,
scikit-learn, matplotlib, anndata). Heavy or specialized packages are added on demand:

```bash
uv sync --all-groups          # base + dev + report groups
uv add scanpy                 # single-cell QC, normalization, marker scoring
uv add cellxgene-census       # pull Tabula Sapiens and tumor cohorts programmatically
```

## Data acquisition

| Layer | Source | Access | Landing |
|---|---|---|---|
| Tumor (discovery) | HuPSA — Human Prostate Single-cell Atlas | download | `data/raw/hupsa/` |
| Tumor (replication) | second integrated prostate cohort (e.g. GSE141445 / large integrated atlas) | GEO / download | `data/raw/prostate_replication/` |
| Healthy comparator | Tabula Sapiens | CELLxGENE Census | `data/raw/tabula_sapiens/` |
| Surface localization + normal-tissue risk | Human Protein Atlas | download / API | `data/external/hpa/` |
| Protein abundance | PaxDb | download | `data/external/paxdb/` |

Large `.h5ad`/`.zarr` files are gitignored. Scripts fetch them; the folder skeleton is tracked via
`.gitkeep`.

## Pipeline (numbered scripts, each writes a committed table)

Numbering mirrors the SatMut convention: fetch (00), prepare (01–09), score (2x–3x), annotate/validate
(5x), build app data (6x), baselines/ablations (7x), Claude Science bundle (80).

| Script | Output table | Purpose |
|---|---|---|
| `00_fetch_data.py` | — | Pull HuPSA, Tabula Sapiens, replication cohort |
| `01_curate_surface_panel.py` | `surface_panel.csv` | ~30 curated prostate surface genes + discovered membrane candidates |
| `10_prepare_tumor.py` | `tumor_cells.parquet` | QC, malignant-cell labels, per-patient index |
| `11_prepare_healthy.py` | `healthy_cells.parquet` | Tabula Sapiens cell-type index |
| `30_score_pairs_and.py` | `pairs_and.csv` | Per-patient AND scores, worst healthy-cell liability |
| `31_score_pairs_not.py` | `pairs_not.csv` | Per-patient NOT scores (activator+, blocker-) |
| `32_pareto_rank.py` | `pareto_frontier.csv` | Rank on lower patient quantile vs worst healthy liability |
| `40_positive_control.py` | `psma_psca_recovery.csv` | Recover PSMA-PSCA, rank it among all pairs |
| `50_protein_evidence.py` | `protein_evidence.csv` | Join top pairs to HPA localization + PaxDb abundance |
| `60_build_app_data.py` | `results/app/app_data.json` | Data for the explorer / future app |
| `70_threshold_sensitivity.py` | `threshold_sensitivity.csv` | Re-score under several positivity thresholds |
| `80_claude_science_bundle.py` | `claude_life_science/upload/*.csv` | Denormalized tables for the workbench |

## Scoring definitions

For markers A, B, malignant cells of patient p, and healthy cell type c:

- AND: `T_and(p) = P(A+ and B+ | malignant, p)`, liability `N_and(c) = P(A+ and B+ | healthy c)`.
- NOT: `T_not(p) = P(A+ and B- | malignant, p)`, liability `N_not(c) = P(A+ and B- | healthy c)`.

Rank pairs on a Pareto frontier: maximize the lower patient quantile `Q0.10{T(p)}` and the median
`T(p)`, minimize `max_c N(c)`. Report AND coverage (specificity) and OR coverage (antigen escape)
separately.

## Compute

Scoring is a set of vectorized co-occurrence counts over sparse matrices, so it runs locally. If a full
pairwise sweep over a large panel and the whole healthy atlas gets heavy, offload one scoring pass to
SageMaker (`aws/`), following the user's rule of training on AWS rather than the workstation. Gate on
CV-style stability across the two tumor cohorts, not a single cohort.

## Correctness guards (state in the report, implement as time allows)

- Positivity is not `count > 0`; test several thresholds and pseudo-bulk per cell type and donor.
- Score per patient first, then summarize, so no high-cell-count patient dominates.
- NOT-gate calls trust B-negatives, which are dropout-sensitive; label those results exploratory.
- Confirm malignant identity from author labels; CNV inference and ambient/doublet correction are
  future-work refinements.
- Transcript presence is not targetability, and bulk proteomics cannot prove same-cell co-expression;
  name CITE-seq / multiplex IHC as the validation that would follow.
