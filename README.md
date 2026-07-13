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

> Status: in progress. See `docs/prd.md` for the contract and `docs/research_plan.md` for the build.

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

Every number in the report is bound to a table in `results/tables/`, so the report rebuilds from the
committed tables. Regenerating the tables from scratch re-fetches the atlases and re-scores.

```bash
uv sync --all-groups
./render_report.sh                 # renders reports/report.html and reports/report.pdf
uv run pytest -q                   # the test suite
```

Regenerate from scratch (re-fetches large atlases, not committed):

```bash
uv add scanpy cellxgene-census
uv run python scripts/00_fetch_data.py
uv run python scripts/01_curate_surface_panel.py
uv run python scripts/10_prepare_tumor.py
uv run python scripts/11_prepare_healthy.py
uv run python scripts/30_score_pairs_and.py
uv run python scripts/31_score_pairs_not.py
uv run python scripts/32_pareto_rank.py
uv run python scripts/40_positive_control.py
uv run python scripts/50_protein_evidence.py
```

Python dependencies are managed with uv. The base environment is light; the single-cell stack
(`scanpy`, `cellxgene-census`) is added on demand.

## Data and licences

HuPSA and the prostate cohorts are public (GEO). Tabula Sapiens is public via CELLxGENE Census. The
Human Protein Atlas and PaxDb are open for non-commercial use. This repository is MIT licensed.

## Author

William Guesdon.
