# Combinatorial surface-marker targets for prostate cancer

**Built with Claude: Life Sciences, Research Track. 2026.**
Event page: https://cerebralvalley.ai/e/built-with-claude-life-sciences

Single-antigen therapies against solid tumors are limited by on-target off-tumor toxicity: few surface
antigens are truly absent from healthy tissue. Combinatorial targeting requires two conditions before a
cell is engaged, which recovers specificity. We search public single-cell data for pairs of cell-surface
proteins that separate prostate cancer cells from every healthy human cell type, under two logics:

- **AND gate** — kill only cells positive for both markers. Safety comes from a second tumor antigen.
- **NOT gate** — kill cells positive for an activator unless a blocker marks a healthy cell to spare.

The known **PSMA-PSCA** pair is our positive control: a good method should recover it from a systematic
scan of the curated panel. That benchmark recovery is what makes this a finding with a truth value rather
than a ranked list. Protein-level evidence from the Human Protein Atlas and PaxDb qualifies surface
localization and normal-tissue risk for the top pairs.

This is Gladstone example (a) reframed for safety: instead of one new drug target, find the two-marker
combination that a logic-gated CAR-T, T-cell engager, or ADC could use to hit the tumor and spare
normal tissue.

**The findings live in the report, not here.** See `reports/report.pdf` (or `reports/report.html`) for
the recovered positive control, the nominated marker pairs, the figures, and every number with its
uncertainty. This README is the project overview and the exact steps to reproduce those results from a
clean clone. Contract in `docs/prd.md`; build in `docs/research_plan.md`.

## The idea in one paragraph

For every candidate pair of surface markers, we compute how often prostate cancer cells co-satisfy the
gate (both present, for AND; activator present and blocker absent, for NOT) and how often any healthy
human cell type does the same. Pairs are scored per patient, then summarized across patients, so no
single high-cell-count donor drives the result. We rank on a Pareto frontier that maximizes the lower
patient quantile of tumor coverage while minimizing the worst-case healthy-cell liability. PSMA-PSCA
fires as a built-in positive control; the payload is a new pair that improves worst-case healthy-cell
separation while keeping malignant coverage across independent patients.

## Why prostate

Prostate is the one solid tumor with a re-discoverable combinatorial positive control (PSMA-PSCA,
validated preclinically in split-signal CAR systems), abundant annotated single-cell data, and real
normal-tissue liabilities to catch (FOLH1 in kidney and small intestine, PSCA in stomach). STEAP1 adds
a second anchor with live clinical data (xaluritamig). The reasoning behind the choice is in `docs/prd.md`.

## What is in here

| Path | What |
|---|---|
| `docs/prd.md` | Product requirements. The contract for the project |
| `docs/research_plan.md` | Technical execution plan: scripts, tables, order of work |
| `docs/claude_tooling_log.md` | Evidence of how Claude Code and Claude Science were used |
| `docs/hackathon_brief.md`, `docs/judging_criteria.md` | The event brief and the Research-track scoring |
| `scripts/` | The pipeline. Each numbered script writes a committed table |
| `results/tables/` | Every number in the report comes from here |
| `reports/` | The rendered Quarto report, the scientific record |
| `claude_life_science/` | Claude Science workbench tasks and their outputs |

## Reproduce

Every number in the report is bound to a committed table in `results/tables/`, so the report rebuilds
from those tables with no network or model call. Python is managed with `uv` (Python 3.11); Quarto is
installed at user level and bundles the Typst engine, so the PDF needs no system LaTeX or Chrome.

**Rebuild the report from the committed tables (no data download):**

```bash
uv sync --all-groups               # Python env, incl. cellxgene-census
bash scripts/setup_env.sh          # install Quarto (user-level) into ~/.local
uv run pytest -q                   # scoring unit tests
./render_report.sh                 # writes reports/report.html and reports/report.pdf
```

**Regenerate every table from scratch** (re-fetches the atlases, ~0.7 GB tumor h5ad plus a Census pull;
not committed). Run in order — `00` reads the panel written by `01`:

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
uv run python scripts/74_hupsa_replication.py       # cross-cohort concordance + advanced disease
```

## Data and licences

- **Tumor** — CZ CELLxGENE "Single-cell atlas of 24 hormone therapy-naive localised prostate cancers"
  (68,322 cells, 24 patients; DOI 10.1101/2024.10.23.619925), downloaded from the CELLxGENE Discover CDN.
- **Replication** — HuPSA (Cheng et al., npj Precision Oncology 2024, DOI 10.1038/s41698-024-00667-x;
  ~369k cells, 6 studies, spanning normal to mCRPC/NEPC), Figshare Seurat V5 `.rds`, CC BY 4.0.
- **Healthy** — Tabula Sapiens 2.0 via the CELLxGENE Census (10x 3' v3 subset to the panel genes).
- **Protein** — Human Protein Atlas (subcellular localization + normal-tissue RNA), open for research use.

This repository is MIT licensed. All datasets are public; the large `.h5ad`/`.parquet` files are
gitignored and fetched by the scripts.

## Author

William Guesdon.
