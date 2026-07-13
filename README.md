# Combinatorial surface-marker targets for prostate cancer

**Built with Claude: Life Sciences, Research Track. 2026.**
Event page: https://cerebralvalley.ai/e/built-with-claude-life-sciences

## The project

A Researcher-track entry for the Built with Claude: Life Sciences hackathon: start from a biological
question, find the public datasets and tools to answer it, and produce a discrete, reproducible analysis.

We chose prostate adenocarcinoma and asked which pairs of cell-surface proteins could let a logic-gated
therapy (CAR-T, T-cell engager, or ADC) engage tumor cells while sparing normal tissue. The pipeline
scans a curated cell-surface panel in public single-cell data under two logics — an **AND gate** (engage
cells positive for both markers) and a **NOT gate** (engage an activator-positive cell unless a blocker
marks it healthy) — scoring each pair per patient against a matched benign-prostate control and a healthy
cell atlas, and benchmarking against the known PSMA-PSCA pair. It runs on transcript data.

**All findings, figures, and numbers are in the report** (`reports/report.pdf` or `reports/report.html`),
not in this README. The indication rationale and the contract for the work are in `docs/prd.md`; the
technical plan is in `docs/research_plan.md`.

## What is in here

| Path | What |
|---|---|
| `docs/prd.md` | Product requirements — the contract for the project |
| `docs/research_plan.md` | Technical execution plan: scripts, tables, order of work |
| `docs/claude_tooling_log.md` | Evidence of how Claude Code and Claude Science were used |
| `docs/hackathon_brief.md`, `docs/judging_criteria.md` | The event brief and Research-track scoring |
| `scripts/` | The pipeline. Each numbered script writes a committed table |
| `results/tables/` | The committed tables the report is built from |
| `reports/` | The rendered Quarto report |
| `claude_life_science/` | Claude Science workbench tasks and their outputs |

## Reproduce

The report is built from committed tables in `results/tables/`, so it rebuilds with no network or model
call. Python is managed with `uv` (Python 3.11); Quarto is installed at user level and bundles the Typst
engine, so the PDF needs no system LaTeX or Chrome.

**Rebuild the report from the committed tables (no data download):**

```bash
uv sync --all-groups               # Python env, incl. cellxgene-census
bash scripts/setup_env.sh          # install Quarto (user-level) into ~/.local
uv run pytest -q                   # scoring unit tests
./render_report.sh                 # writes reports/report.html and reports/report.pdf
```

**Regenerate every table from scratch** (re-fetches the atlases; not committed). Run in order — `00`
reads the panel written by `01`:

```bash
uv run python scripts/01_curate_surface_panel.py   # curated surface panel
uv run python scripts/00_fetch_data.py             # tumor cohort + Tabula Sapiens (Census) + verify
uv run python scripts/10_prepare_tumor.py          # per-cell table, malignant labels
uv run python scripts/11_prepare_healthy.py         # per-cell healthy table
uv run python scripts/12_export_for_doublets.py    # export tumor counts for R doublet calling
# doublet calling runs in a Bioconductor container (rootless Podman):
podman run --rm -v "$PWD":/work -w /work \
    quay.io/biocontainers/bioconductor-scdblfinder:1.24.0--r45hdfd78af_0 \
    Rscript scripts/doublet_scdblfinder.R          # scDblFinder per-sample doublet calls
uv run python scripts/14_apply_doublet_removal.py  # remove doublets -> singlet table (primary input)
uv run python scripts/13_doublet_qc.py             # doublet-removal robustness check
uv run python scripts/30_score_pairs_and.py        # AND pairs + singles + analysis summary
uv run python scripts/31_score_pairs_not.py        # NOT pairs (exploratory)
uv run python scripts/32_pareto_rank.py            # Pareto frontier
uv run python scripts/40_positive_control.py       # PSMA-PSCA recovery + random-pair control
uv run python scripts/50_protein_evidence.py       # Human Protein Atlas evidence
uv run python scripts/55_nominate.py               # surface-accessible nomination
uv run python scripts/56_pair_profiles.py          # per-patient + tissue-liability profiles
uv run python scripts/70_threshold_sensitivity.py  # positivity-threshold sensitivity
uv run python scripts/71_deleaked_sensitivity.py   # de-leaked label sensitivity
uv run python scripts/72_uncertainty.py            # bootstrap CIs, Pareto-membership, liability UB
uv run python scripts/73_coescape.py               # marker co-escape check
```

**Optional: cross-cohort replication in HuPSA** (independent PCa meta-analysis, Seurat V5 `.rds`):

```bash
curl -fL -o data/raw/hupsa/HuPSA_share.rds https://ndownloader.figshare.com/files/51043067
podman run --rm -v "$PWD":/work -w /work docker.io/satijalab/seurat:5.0.0 \
    Rscript scripts/hupsa_extract.R                 # panel counts + metadata (write-to-disk handoff)
uv run python scripts/74_hupsa_replication.py       # cross-cohort concordance
```

## Data sources

Public datasets fetched by the scripts; the large `.h5ad`/`.parquet`/`.rds` files are gitignored.

- **Tumor** — CZ CELLxGENE localised prostate cancer atlas (DOI 10.1101/2024.10.23.619925), CELLxGENE
  Discover CDN.
- **Replication** — HuPSA (Cheng et al., npj Precision Oncology 2024, DOI 10.1038/s41698-024-00667-x),
  Figshare Seurat V5 `.rds`, CC BY 4.0.
- **Healthy** — Tabula Sapiens 2.0 via the CELLxGENE Census.
- **Protein** — Human Protein Atlas, open for research use.

This repository is MIT licensed; all datasets are public.

## Author

William Guesdon.
