# Combinatorial surface-marker targets for prostate cancer

**Built with Claude: Life Sciences, Research Track. 2026.**

Single-antigen therapies against solid tumors are limited by on-target off-tumor toxicity: few surface
antigens are truly absent from healthy tissue. Combinatorial targeting requires two conditions before a
cell is engaged, which recovers specificity. We search public single-cell data for pairs of cell-surface
proteins that separate prostate cancer cells from every healthy human cell type, under two logics:

- **AND gate** — kill only cells positive for both markers. Safety comes from a second tumor antigen.
- **NOT gate** — kill cells positive for an activator unless a blocker marks a healthy cell to spare.

The known **PSMA-PSCA** pair is our positive control: a good method should recover it from an
unsupervised scan. That benchmark recovery is what makes this a finding with a truth value rather than a
ranked list. Protein-level evidence from the Human Protein Atlas and PaxDb qualifies surface
localization and normal-tissue risk for the top pairs.

This is Gladstone example (a) reframed for safety: instead of one new drug target, find the two-marker
combination that a logic-gated CAR-T, T-cell engager, or ADC could use to hit the tumor and spare
normal tissue.

**Result.** The scan recovers PSMA-PSCA as the positive control: each antigen alone is broadly positive
off the prostate (PSMA in duodenum, 0.87; PSCA in bladder urothelium, 0.92), and requiring both at once
collapses the worst extra-prostatic liability to 0.13 — the clinical rationale for the split-signal CAR,
recovered blind. 79% of random surface pairs score worse. On the surface-accessible Pareto frontier of
per-patient coverage versus off-tissue risk, two co-leads improve on it: **PSMA x STEAP1** (both antigens
have clinical binders; median coverage 0.68 across 24 patients, 6.5x PSMA-PSCA, worst extra-prostatic
0.28) and **STEAP1 x HPN** (Pareto-optimal; coverage floor Q0.10 = 0.47, worst 0.16). Both separate
malignant from matched benign prostate, so they mark cancer rather than the whole gland. See
`reports/report.pdf` for the figures. Contract in `docs/prd.md`; build in `docs/research_plan.md`.

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
uv run python scripts/30_score_pairs_and.py        # AND pairs + singles + analysis summary
uv run python scripts/31_score_pairs_not.py        # NOT pairs (exploratory)
uv run python scripts/32_pareto_rank.py            # Pareto frontier
uv run python scripts/40_positive_control.py       # PSMA-PSCA recovery + random-pair control
uv run python scripts/50_protein_evidence.py       # Human Protein Atlas evidence
uv run python scripts/55_nominate.py               # surface-accessible nomination
uv run python scripts/56_pair_profiles.py          # per-patient + tissue-liability profiles
uv run python scripts/70_threshold_sensitivity.py  # positivity-threshold sensitivity
```

## Data and licences

- **Tumor** — CZ CELLxGENE "Single-cell atlas of 24 hormone therapy-naive localised prostate cancers"
  (68,322 cells, 24 patients; DOI 10.1101/2024.10.23.619925), downloaded from the CELLxGENE Discover CDN.
- **Healthy** — Tabula Sapiens via the CELLxGENE Census (server-side subset to the panel genes).
- **Protein** — Human Protein Atlas (subcellular localization + normal-tissue RNA), open for research use.

This repository is MIT licensed. All datasets are public; the large `.h5ad`/`.parquet` files are
gitignored and fetched by the scripts.

## Author

William Guesdon.
