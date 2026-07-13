# Dual-marker discovery - SESSION SUMMARY

Committed on purpose. This file splits work across days and survives a dead session. It carries no
secrets, so it is safe in a public repo. Update it as work proceeds, not at the end.

> ## ★★★ RESUME NOW - 2026-07-13 (Session 1). REPO SCAFFOLDED. Environment resolves, tests pass.
>
> **STATE: skeleton in place, no science yet.** The repository mirrors the SatMut project layout:
> numbered-script pipeline, a Quarto IMRaD report bound to committed tables, a test suite, and a Claude
> Science task folder. `uv sync --all-groups` resolves. The package imports. `pytest` passes (1 test, a
> layout smoke check). No pipeline script exists yet, so there is no load-bearing self-test to run.
>
> **THE PROJECT AIM lives in `docs/prd.md`** (the product requirements document, our contract). Read it
> first; it defines the biological question, the two gate types, why prostate, the data stack, and the
> deliverable. This file tracks execution; `docs/prd.md` defines what we are trying to do.
>
> **THE OFFICIAL COMPETITION DEADLINE is Mon 13 July 21:00 ET** (per `docs/hackathon_brief.md`). This
> repo was scaffolded on 2026-07-13. If this is a same-day entry the scope must be the minimum honest
> version in N-MIN below; if it is a later effort, the full pipeline in NEXT applies.
>
> **SINGLE NEXT ACTION.** Take N0 (add `scanpy` and `cellxgene-census`, fetch HuPSA and Tabula Sapiens),
> then N1 (curate the ~30-gene surface panel). The first load-bearing self-test will be N4's positive
> control: the method must recover PSMA-PSCA above random surface pairs.
>
> **NOTHING RUNNING IN THE BACKGROUND.** Data is public; no key needed for the analysis.

> ### How to maintain this file (LLM: read before editing)
> - **RULES** - how-we-work directives. Pinned. Change only when a working rule genuinely changes.
> - **DO NOT REDO** - dead ends already paid for. Append when something fails. Never delete.
> - **INSIGHTS** - durable findings and decisions. Append a tight bullet when something is proven or
>   decided. If it overturns an earlier one, edit that bullet and note "(supersedes ...)". Detail belongs
>   in `docs/`, not here.
> - **NEXT** - overwrite each session. Self-contained: the harness task list does NOT survive a session,
>   so never write "task #13". Give the work a stable label (N0, N1 ...) and state it in full, with the
>   FILES it touches and a DONE WHEN you can run.
> - **SUBMISSION** - the deadline checklist. Only ticks, no prose.
> - **REFERENCE** - paths, data URLs, commands. No secrets, this file is public.
> - **WORKLOG** - append-only, one line per commit, time order. Never delete a line.
> - **JOURNAL** - append-only. ONE dated entry per session at the top, newest first. Terse bullets: what
>   was done, and the outcome or number.
> - Keep RESUME NOW, DO NOT REDO, and NEXT tight; those are what a cold start reads. WORKLOG and JOURNAL
>   may grow as long as they need to.

> ### SESSION PROTOCOL (follow it exactly)
>
> **AT SESSION START**
> 1. Run FIRST 60 SECONDS below. If a self-test exits non-zero, STOP and diagnose. Do not build.
> 2. Read RESUME NOW, then DO NOT REDO. The second one is what stops you paying twice.
> 3. Pick the topmost NEXT item that is not blocked. Mark it `[~]` before you start. If you change the
>    plan, change this file first.
>
> **DURING** - RULE #0A (commit each unit) and RULE #0B (one WORKLOG line per commit, immediately).
>
> **AT SESSION END, or when handing back control**
> 1. Working tree clean. `git status --porcelain` empty.
> 2. Update RESUME NOW: state, single next action, what is blocked on the user, what is running.
> 3. Mark finished NEXT items `[x]`. Add any new ones with FILES and DONE WHEN.
> 4. Add ONE bullet to today's JOURNAL entry.

═════════════════ FIRST 60 SECONDS (do this before anything else) ═════════════════

```bash
cd /home/ubuntu/Documents/dual-marker-discovery
git status -sb && git log --oneline -3     # expect: clean, in sync with origin
uv sync --all-groups                        # expect: environment resolves, no error
uv run pytest -q                            # expect: green
ls docs/prd.md docs/research_plan.md        # expect: the contract and the plan are present
# The FIRST load-bearing script will be the positive control:
# uv run python scripts/40_positive_control.py   # MUST exit 0 once it exists: PSMA-PSCA recovered
```

**Once a load-bearing script exists, it goes here and MUST exit 0 on a cold start.** The first one is the
positive control. If it ever exits non-zero, STOP and diagnose. Do not build on a broken claim.

═══════════════════════════ GOAL ═══════════════════════════

**The canonical statement of the project aim is `docs/prd.md`.** The paragraphs below are the short
version; `docs/prd.md` is the contract and wins on any conflict.

Solo Research-track entry, 2026 Built with Claude: Life Sciences. Find pairs of cell-surface proteins
that separate prostate cancer cells from every healthy human cell type, under two logics: AND (both
markers on the tumor) and NOT (an activator on the tumor with a blocker that spares healthy cells
expressing the activator). Benchmark against the known PSMA-PSCA pair. The deliverable is a Quarto report
in IMRaD form, plus figures for the video and the three submission artifacts.

**Working thesis, stated as it may be defended:** a patient-aware scan of public single-cell data
recovers the historically validated PSMA-PSCA combination and nominates at least one pair that improves
worst-case healthy-cell separation while keeping malignant coverage across independent patients. The
contribution is not a new therapy. It is a cheap, open, reproducible recipe for combinatorial-target
discovery, with a built-in positive control.

**What we do NOT claim.** That a nominated pair is clinically ready; it is a computational hypothesis.
That single-cell co-expression proves same-cell surface co-localization; that needs CITE-seq or multiplex
IHC. That the NOT-gate pairs are as trustworthy as the AND-gate pairs; NOT-gate calls depend on scRNA
negatives, which are dropout-sensitive, so they are exploratory.

Claude Code orchestrates and audits itself. Claude Science verifies and annotates live.

Read in this order: `docs/prd.md` → `docs/research_plan.md` → `docs/judging_criteria.md`.

═══════════════════════════════ RULES (persistent) ═══════════════════════════════

## ★★★ RULE #0 (NORTH STAR): ship a finding a judge can TRUST, and that is cool to watch.
Demo is 30 percent of the score and Claude Use is 25 percent. More than half the grade is the video and
the tooling story. Every choice serves a legible, trustworthy, watchable result.

## ★★★ RULE #0A: COMMIT DURING THE WORK, NEVER BATCHED AT THE END.
One logical unit, one commit. Conventional Commits. Short message, a few lines. No backticks in `-m`.
Never mention Claude in a commit message.

## ★★★ RULE #0B: APPEND ONE WORKLOG LINE AFTER EVERY COMMIT.
Immediately after each commit, add one line to WORKLOG with the time, the commit, and what it did.

## ★★★ RULE #1 (THE METHOD): WORK LIKE A SCIENTIST. literature → implement → critical-review → report.
Run the four steps in order for every new analysis or lever. Establish what the field does before
implementing. Attack the result before believing it.

## ★★★ RULE #2: ASSERT NOTHING YOU HAVE NOT CHECKED AGAINST A CONTROL.
Every headline claim needs a control that could have failed. The positive control is PSMA-PSCA recovery.
The negative control is a random surface pair, which must score worse. If a control cannot fail, it
proves nothing.

## ★★★ RULE #3: SCORE PER PATIENT, THEN SUMMARIZE. NEVER POOL CELLS.
A patient contributing thousands of cells must not dominate a pair's score. Compute co-expression within
each patient, then summarize across patients (median and a lower quantile). Any pooled score is a bug.

## ★★★ RULE #4: POSITIVITY IS NOT count > 0.
A zero in scRNA is not proof a cell lacks the marker. Test several positivity thresholds, use pseudo-bulk
per cell type and donor, and report sensitivity. This matters doubly for NOT-gate blocker-negative calls.

## ★★★ RULE #5: SCRIPTS PREPROCESS. THE REPORT DRAWS.
Each script writes a committed table to `results/tables/`. The Quarto report reads tables and computes no
science of its own. Every inline number in the report is bound to a committed table. Figures are drawn in
the document from table data, with the caption in the figure metadata, never burned into a PNG.

## ★★★ RULE #5A: THE REPORT IS A PEER-REVIEWED PAPER. IMRaD structure, scientific prose.
Abstract, Introduction, Methods (with data accessions and the scoring definitions), Results, Discussion
with a dedicated Limitations paragraph, References from `references.bib`. Past tense for what was done.
Every result stated with its uncertainty. No marketing verbs. Short sentences, no em dashes.

## ★★★ RULE #6: CLAIM DISCIPLINE. The register is a paper, not a pitch.
Own the PSMA-PSCA recovery as a trust signal, not a discovery. There is a March 2025 preprint doing
single-cell logic-gated antigen discovery, so the general method is not novel; the owned contribution is
the per-patient robust scoring, the explicit AND-vs-OR and AND-vs-NOT reporting, and benchmark recovery
followed by ranked improvement. Transcript presence is not targetability; say so.

## ★★★ RULE #7: CLAUDE CODE ORCHESTRATES, CLAUDE SCIENCE VERIFIES. Log every handoff with disagreements.
Both tools must be visible for the 25 percent Claude Use score. Log every round-trip in
`docs/claude_tooling_log.md`, including where an agent disagreed or corrected another. An empty
disagreements column is a weak submission.

## ★★★ RULE #8: PRD BEFORE CODE. Solo entry. Repo is PUBLIC.
The PRD (`docs/prd.md`) is the contract. Python via uv only. Google-style docstrings on every function
and class. Output file names are snake_case with a date where relevant. No secrets in git; `.env` is
gitignored and the analysis needs none.

## ★ RULE #9 (PROJECT-SPECIFIC): THE POSITIVE-CONTROL GATE IS SACRED.
The scan must recover PSMA-PSCA (FOLH1 + PSCA) as a high-ranking AND-gate pair, above a random-pair
baseline, before any new pair is presented. If the benchmark does not recover, the scoring is wrong and
no nomination is trustworthy. Diagnose the pipeline before believing any ranking.

## ★ RULE #10 (PROJECT-SPECIFIC): TWO GATES, ONE STORY, HONEST ABOUT THE ASTERISK.
AND is the validated headline. NOT is the novel extension and is reported as exploratory, because it
depends on trusting scRNA negatives. Report AND coverage (specificity) and OR coverage (antigen escape)
separately. The demo climax is the Pareto scatter with PSMA-PSCA recovered and one new pair highlighted.

═══════════════ DO NOT REDO (dead ends already paid for) ═══════════════

Nothing yet. Append here the moment something fails, so no future session pays for it twice.

Standing warnings carried in from prior projects:
- Do NOT pool all malignant cells before scoring; one high-cell-count patient will dominate (RULE #3).
- Do NOT trust a scRNA zero as absence, especially for a NOT-gate blocker (RULE #4).
- Do NOT present a ranked candidate list as the result. The deliverable is a benchmark-anchored finding
  with a truth value: PSMA-PSCA recovered, plus a nominated pair with its per-patient coverage and its
  worst-case healthy-cell risk.

═══════════════════════════ INSIGHTS (durable, all current) ═══════════════════════════

- **★★★ PROSTATE IS THE ONLY SOLID TUMOR WITH A RE-DISCOVERABLE COMBINATORIAL POSITIVE CONTROL.** PSMA
  (FOLH1) + PSCA is a validated preclinical AND-gate (split-signal CAR). Recovering it from an
  unsupervised scan is a real control that can fail. No other indication offers this cleanly.
- **★ THE METHOD IS NOT NOVEL; THE FRAMING IS THE CONTRIBUTION.** A March 2025 bioRxiv preprint does
  single-cell logic-gated antigen discovery. Owned angle: per-patient robust scoring, AND-vs-NOT
  reporting, benchmark recovery then ranked improvement. Lead with that, not the general concept.
- **★ NOT-GATE RESULTS CARRY A BIGGER ASTERISK THAN AND-GATE RESULTS.** AND depends on positive
  co-detection (robust to dropout); NOT depends on blocker-negative calls (dropout-sensitive). Keep AND
  as the validated headline and label NOT exploratory.
- **★ THE HEALTHY ATLAS IS THE LOAD-BEARING DENOMINATOR.** The safety claim lives or dies on a broad
  healthy human reference. Tabula Sapiens (~500k cells, ~24 organs) via CELLxGENE Census is that
  reference. Without it there is no "not expressed on healthy cells" claim.
- **★ REAL NORMAL-TISSUE LIABILITIES EXIST FOR THE BENCHMARK.** FOLH1 in kidney tubules and small
  intestine, PSCA in stomach and kidney. The scan must catch these, which is why the indication has a
  genuine, non-trivial safety question rather than a toy one.

═══════════ NEXT - self-contained work packages. The harness task list does NOT persist. These do. ═══════

Status: `[ ]` not started · `[~]` in progress · `[x]` done. Mark `[~]` BEFORE you start.

**`[x] N-SCAFFOLD - Repository skeleton.`** DONE 2026-07-13.
Mirrors the SatMut layout: `src/dual_marker_discovery/`, numbered `scripts/`, tables-bound
`reports/report.qmd`, `tests/`, `claude_life_science/`, docs. `uv sync` resolves; `pytest` green.

**`[ ] N0 - Environment and data access. UNBLOCKED.`**
FILES: `pyproject.toml`, `scripts/00_fetch_data.py`. DONE WHEN: `uv add scanpy cellxgene-census` succeeds,
HuPSA and Tabula Sapiens are fetched into `data/raw/`, and a second prostate cohort is identified for
replication. No key needed.

**`[ ] N1 - Curate the surface-marker panel.`**
FILES: `scripts/01_curate_surface_panel.py` → `results/tables/surface_panel.csv`. DONE WHEN: ~30 curated
prostate surface genes (FOLH1, PSCA, STEAP1, STEAP2, TACSTD2, CD276, DLL3, KLK2, plus discovered membrane
candidates) are written with a source column and a surface-localization flag.

**`[ ] N2 - Prepare the tumor cells.`**
FILES: `scripts/10_prepare_tumor.py` → `data/interim/tumor_cells.parquet`. DONE WHEN: HuPSA is QC'd,
malignant cells are labelled from the authors' annotations, and a per-patient index exists.

**`[ ] N3 - Prepare the healthy comparator.`**
FILES: `scripts/11_prepare_healthy.py` → `data/interim/healthy_cells.parquet`. DONE WHEN: Tabula Sapiens
cell-type labels are indexed for the panel genes, ready for per-cell-type liability scoring.

**`[ ] N4 - AND scoring and THE POSITIVE-CONTROL GATE.`**
FILES: `scripts/30_score_pairs_and.py`, `scripts/40_positive_control.py` → `results/tables/pairs_and.csv`,
`results/tables/psma_psca_recovery.csv`. DONE WHEN: per-patient AND scores and worst-case healthy-cell
liability are computed for all pairs, and `40` exits 0 only if PSMA-PSCA ranks above the random-pair
baseline. THIS IS THE GATE (RULE #9).

**`[ ] N5 - NOT scoring.`**
FILES: `scripts/31_score_pairs_not.py` → `results/tables/pairs_not.csv`. DONE WHEN: per-patient NOT scores
(activator+, blocker-) and their healthy-cell liability are computed, flagged exploratory (RULE #10).

**`[ ] N6 - Pareto ranking.`**
FILES: `scripts/32_pareto_rank.py` → `results/tables/pareto_frontier.csv`. DONE WHEN: pairs are ranked on
the lower patient quantile of tumor coverage against the worst healthy-cell liability, AND and NOT
reported separately, with AND vs OR coverage broken out.

**`[ ] N7 - Protein evidence for the top pairs.`**
FILES: `scripts/50_protein_evidence.py` → `results/tables/protein_evidence.csv`. DONE WHEN: the top pairs
are joined to Human Protein Atlas localization and normal-tissue distribution and to PaxDb abundance.

**`[ ] N8 - Freeze the report and build the figures.`**
FILES: `reports/report.qmd`, `reports/report.html`, `reports/report.pdf`. DONE WHEN: the report is a
peer-reviewed IMRaD paper (RULE #5A), every inline number binds to a committed table, the Pareto scatter
and the PSMA-PSCA recovery figure render, and `./render_report.sh` produces both HTML and PDF.

**`[ ] N9 - Build the app data (bridge to the website + LLM app).`**
FILES: `scripts/60_build_app_data.py` → `results/app/app_data.json`. DONE WHEN: the top pairs, their
per-patient coverage, and their protein evidence are serialized for the explorer and the future
Claude-powered app.

**`[ ] N-MIN - Minimum honest version if the timeline is tight.`**
HuPSA tumor + Tabula Sapiens healthy, ~30 curated genes, per-patient AND scoring, one Pareto scatter,
PSMA-PSCA recovered, one new AND pair and one NOT pair highlighted with caveats. CellBender, doublet
removal, CNV malignant calling, and the second replication cohort move to a future-work slide.

═══════════ SUBMISSION CHECKLIST ═══════════

Artifacts:
- [ ] 3-minute demo video. Pareto scatter, PSMA-PSCA recovered, one nominated pair, the protein evidence.
- [ ] Public repository with the rendered Quarto report committed.
- [ ] 100-200 word written summary.

Repo state:
- [ ] Repo is PUBLIC.
- [ ] `reports/report.html` and `reports/report.pdf` current (rebuilt from the frozen tables).
- [ ] `docs/claude_tooling_log.md` complete, Claude Science rows filled, disagreements column populated.
- [ ] LICENSE present (MIT). Dataset licences respected and noted.

Leak and hygiene check:
- [ ] Rerun every script. `git status --porcelain` empty. No table rotted silently.
- [ ] No secrets committed. `.env` untracked. `git grep` finds no key.

═══════════════════════════ REFERENCE ═══════════════════════════

**Repo.** `github.com/wguesdon/dual-marker-discovery`. Local `/home/ubuntu/Documents/dual-marker-discovery`.
Python 3.13, uv, MIT, remote over SSH.

**Related work (planned, mirrors the SatMut delivery shape).** Once the report reaches a stable state, the
plan is a public showcase website plus an LLM-powered "ask the data" app on the native Anthropic API,
hosted on AWS, the same pattern used for the SatMut project. Not started yet.

**Data URLs (all public).**
- HuPSA - Human Prostate Single-cell Atlas (~369k cells, 6 studies).
- Prostate replication cohort - GEO GSE141445 (Chen et al. 2021, ~36k cells, 13 patients), or a larger
  integrated atlas (~128 patients).
- Tabula Sapiens - healthy human atlas (~500k cells, ~24 organs), via CELLxGENE Census.
- Human Protein Atlas - proteinatlas.org (surface localization, normal-tissue distribution).
- PaxDb - pax-db.org (tissue-level protein abundance).

**Clinical context (for the write-up).**
- PSMA + PSCA: preclinical AND-gate (split-signal CAR). The benchmark.
- PSMA + CD70: bispecific CAR-T, NCT05437341 (first logic-gated CAR-T for mCRPC).
- STEAP1 x CD3: T-cell engager (xaluritamig), NCT04221542.
- A2 Bio Tmod NOT gate (CEA/MSLN/EGFR + HLA-A*02 loss): other solid tumors, not prostate; HLA loss is
  genomic, not scRNA-recoverable.
- Prior art: a March 2025 bioRxiv preprint on single-cell logic-gated antigen discovery.

**Commands.**
```bash
uv sync --all-groups                        # base + dev + report deps
uv add scanpy cellxgene-census              # single-cell stack, added on demand
uv run pytest -q                            # tests
./render_report.sh                          # report.html + report.pdf
```

**Scoring definitions.** For markers A, B, malignant cells of patient p, healthy cell type c:
- AND: T_and(p) = P(A+ and B+ | malignant, p); liability N_and(c) = P(A+ and B+ | healthy c).
- NOT: T_not(p) = P(A+ and B- | malignant, p); liability N_not(c) = P(A+ and B- | healthy c).
- Rank on the Pareto frontier: maximize Q0.10{T(p)} and median T(p); minimize max_c N(c).

═══════════ WORKLOG (append-only, one line per commit, time order. NEVER delete a line.) ═══════════

### 2026-07-13 (Session 1)
- (pending first commit) chore: scaffold the dual-marker-discovery repo. uv package layout, MIT,
  tables-bound Quarto report skeleton, tests, docs (prd, research_plan, claude_tooling_log, brief,
  judging), Claude Science task folder, this SESSION_SUMMARY.

══════════════════════════ JOURNAL (append-only, newest first) ═══════════════════════════

### 2026-07-13 - Session 1: indication chosen, repo scaffolded

- Compared prostate, ovarian, and colorectal for AND/NOT-gate combinatorial-target discovery against
  three constraints: a re-discoverable benchmark, single-cell depth, and protein coverage. Verified the
  current clinical programs (PSMA-PSCA, STEAP1 engager, A2 Bio Tmod) with web search.
- **Chose prostate.** It is the only solid tumor with a re-discoverable AND-gate positive control
  (PSMA-PSCA), it has abundant annotated single-cell data (HuPSA, integrated atlases), and it has genuine
  normal-tissue liabilities (FOLH1, PSCA) so the safety question is real.
- Decided to be open to both AND and NOT logic. AND is the validated headline; NOT doubles the candidate
  space but depends on scRNA negatives, so it is reported as exploratory.
- Scaffolded the repository mirroring the SatMut project: numbered-script pipeline, tables-bound Quarto
  report, tests, Claude Science task folder. `uv sync --all-groups` resolved; `pytest` green.
- Noted the prior art (March 2025 preprint) so the framing leads with the owned contribution, not the
  general method.
