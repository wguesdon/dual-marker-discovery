# Dual-marker discovery - SESSION SUMMARY

Working memory across sessions. Four sections, in this order: **How to maintain**, **Rules**,
**Insights**, **Logs**. An LLM opening this file reads How to maintain and Rules first, on purpose.

---

## How to maintain this file

This file is how we work and what we have learned. It is not the project aim. **The aim lives in
`docs/prd.md`** (the product requirements document, the contract); the technical plan lives in
`docs/research_plan.md`. Read those for what we are building and why.

Keep only the four sections below. Do not add a "current state" or "next steps" section here; track
live work in the harness task list and in `docs/`.

**Who edits what.** Rules and Insights are the user's to curate. The LLM proposes a change and the user
decides; the LLM does not add, reword, or remove a Rule or an Insight on its own. The LLM maintains Logs
by itself.

- **Rules** - persistent how-we-work directives. Change one only when the user says a working rule has
  genuinely changed.
- **Insights** - key lessons learned, and only those. Be selective: a plain fact about the project
  belongs in `docs/`, not here. One tight bullet each. If a new lesson overturns an old one, the user
  edits the old bullet and notes "(supersedes ...)".
- **Logs** - append-only, LLM-maintained. One dated block per session, newest at the bottom. One line
  per commit plus a bullet or two for what happened. Record dead ends here, prefixed `DEAD END:`, so no
  session repeats them; the user may later promote a recurring one to an Insight. Keep it brief. Never
  delete a line.

Session discipline: at start, read Rules then Insights. During, commit each logical unit and add its
Logs line immediately. At end, leave the tree clean and add a Logs bullet.

---

## Rules

1. **Scientific accuracy is the first priority, above everything else including demo appeal.** A correct,
   understated result beats a compelling overstated one; when the two conflict, accuracy wins. Verify every
   external fact (accession, DOI, trial ID, a prior number) against a primary source before it enters a
   table or the report. When a claim is refuted, retract it immediately across every surface rather than
   defend it.
2. **The human sets strategy and report organization; the LLM executes.** Strategic calls (the
   indication, which analyses and levers to run, the framing, and how the report is structured) are the
   human's. The LLM proposes options with a recommendation, then implements the chosen one. It does not
   change the plan, the framing, or the report's organization without sign-off. The LLM's lane is code
   execution, verification, and faithful reporting of what actually happened.
3. **Reproducibility is non-negotiable. All code runs inside a controlled environment: a `uv` virtual
   environment, a Podman container, or an nf-core pipeline.** Never against a system or global
   interpreter, never an ad hoc install. Pin what defines the environment (`uv.lock`, image digests, the
   pipeline revision). The README's first job is to let a stranger, from a clean clone, set up the
   project and run the whole analysis: dependencies, data fetch, and the exact command sequence that
   regenerates every table and figure.
4. **Make the result legible and watchable.** Demo is 30 percent of the score and Claude Use is 25 percent,
   so more than half the grade is the video and the tooling story. Build for a result a judge can see and
   trust, but never trade accuracy for polish. Rule 1 wins every time.
5. **This file is public. Never put secrets in it** - no keys, tokens, access codes, private URLs, or
   otherwise sensitive information. It ships with the repo.
6. **Work like a scientist:** literature, then implement, then critically review, then report. Establish
   what the field does before implementing. Attack the result before believing it.
7. **Assert nothing you have not checked against a control that could fail.** Positive control is
   PSMA-PSCA recovery. Negative control is a random surface pair, which must score worse.
8. **Score per patient, then summarize. Never pool cells.** A patient with thousands of cells must not
   dominate a pair's score. Any pooled score is a bug.
9. **Positivity is not `count > 0`.** A scRNA zero is not proof of absence. Test several thresholds and
   pseudo-bulk per cell type and donor. This matters doubly for NOT-gate blocker-negative calls.
10. **Scripts preprocess, the report draws.** Each script writes a committed table to `results/tables/`.
    Every inline number in the report binds to one. Figures are drawn from tables, never burned into a PNG.
11. **The report is a peer-reviewed IMRaD paper:** Abstract, Introduction, Methods (with data accessions),
    Results, Discussion with a Limitations paragraph, References. Scientific prose, every result stated with
    its uncertainty, no marketing verbs, short sentences, no em dashes.
12. **Claim discipline.** Own the PSMA-PSCA recovery as a trust signal, not a discovery. The method is not
    novel (a March 2025 preprint does single-cell logic-gated antigen discovery); the contribution is the
    per-patient scoring, the AND-vs-NOT reporting, and benchmark recovery then ranked improvement.
    Transcript presence is not targetability.
13. **The positive-control gate is sacred.** Recover PSMA-PSCA above the random-pair baseline before
    presenting any new pair. If it does not recover, the scoring is wrong and no nomination is trustworthy.
14. **Two gates, one story.** AND is the validated headline. NOT is the novel extension and is reported
    as exploratory, because it depends on trusting scRNA negatives. Report AND coverage (specificity) and
    OR coverage (antigen escape) separately.
15. **Claude Code orchestrates, Claude Science verifies.** Log every handoff in
    `docs/claude_tooling_log.md`, including where one agent disagreed with or corrected another. An empty
    disagreements column is a weak submission.
16. **Commit during the work, one logical unit per commit.** Conventional Commits, short message, no
    backticks in `-m`, never mention Claude. Append one Logs line immediately after each commit.
17. **PRD before code. Python via uv only.** Google-style docstrings on every function and class. Output
    file names are snake_case with a date where relevant.

---

## Insights

None yet. Work has not started, so there are no lessons learned. Add a bullet only when one is genuinely
earned; a plain fact about the project belongs in `docs/prd.md`, not here.

---

## Logs

### 2026-07-13 - Session 1

- Chose prostate adenocarcinoma over ovarian and colorectal: only solid tumor with a re-discoverable
  AND-gate positive control (PSMA-PSCA), abundant annotated single-cell data, real normal-tissue
  liabilities. Decided to pursue both AND and NOT logic, NOT reported as exploratory.
- Scaffolded the repo mirroring the SatMut layout: numbered-script pipeline, tables-bound Quarto report,
  tests, docs, Claude Science task folder. `uv sync --all-groups` resolves; `pytest` green.
- `c734663` chore: scaffold dual-marker-discovery repo. Pushed to origin/main.
- `4e62860` docs: restructured this file to four sections (how-to-maintain, rules, insights, logs).
- Set the working rules with the user: elevated scientific accuracy to Rule 1 (verify external facts,
  retract when refuted), and added Rule 2, the human sets strategy and report organization while the LLM
  executes.
- Added Rule 3 (reproducibility: all code runs in a uv env, a Podman container, or an nf-core pipeline;
  the README carries full setup and run instructions). Emptied Insights until work starts; the seeded
  facts already live in `docs/prd.md`.
- Session 1 close. Foundation set: falsifiable question, PSMA-PSCA positive control, working scaffold,
  rules, and docs. No analysis code yet. Next session starts at `scripts/00_fetch_data.py` per
  `docs/research_plan.md`, and its FIRST job is to verify data access before any scoring (Rule 1): that
  HuPSA and Tabula Sapiens actually download, carry malignant-cell / cell-type labels, and capture the
  surface-panel genes. Read the March 2025 logic-gated-discovery preprint early to lock differentiation.

### 2026-07-13 - Session 2 (analysis build)

- Data locked: tumor = CZ CELLxGENE "24 hormone-naive localised PCa" h5ad (68,322 cells, 24 patients,
  author CNV/signature malignant call `malignant_anno_merged`, 3,802 malignant); healthy = Tabula
  Sapiens via CELLxGENE Census, server-side subset to panel genes (1,136,218 cells, 180 cell types,
  75 tissues). 29/30 panel genes present (ACPP absent).
- Prior art to differentiate against: LogiCAR designer (Madan/Ruppin, bioRxiv 2025.03.19.644074, breast,
  cohort-pooled) and Kwon 2023 Nat Biotech (pan-cancer, pooled). Our edge: per-patient, matched benign
  control, PSMA-PSCA recovery gate.
- Scoring: one matrix product per group over the panel positivity matrix yields AND/NOT/OR for all pairs;
  per-patient (Q0.10 floor) never pooled; three references (malignant, matched benign prostate,
  Tabula Sapiens worst-case split into all-organ and extra-prostatic).
- Positive control RECOVERED: PSMA single worst extra-prostatic 0.87 (duodenum), PSCA 0.92 (bladder);
  PSMA AND PSCA 0.13 (small intestine) - a ~7x collapse; 79% of random surface pairs score worse.
- Nomination framing (user pick): frontier + two co-leads - PSMA x STEAP1 (translatable, Q10 0.45,
  median 0.68 = 6.5x PSMA-PSCA, worst 0.28) and STEAP1 x HPN (Pareto-optimal, Q10 0.47, worst 0.16).
- Report rendered to HTML + PDF (Quarto + bundled Typst, no Chrome), figures drawn in-document from
  committed tables; PDF committed for GitHub viewing.
- `e1a34d2` feat: data access, surface panel, prepare, per-patient pair scoring (env, panel, fetch,
  prepare, scoring, scan, tests green).
- `e5103d6` feat: positive/negative control, HPA protein evidence, pair nomination.
- `8ba1697` docs: rendered IMRaD report (HTML+PDF via Quarto+Typst) with figures and nomination frontier.
- `e38a751` feat: threshold sensitivity (70) + per-patient/tissue profiles (56); report gains
  per-patient coverage and sensitivity figures (5 figures total) plus a named residual-liability table.
  Sensitivity confirms nominations hold and grow safer as positivity tightens (k=1..3).
- README reproduce-from-clone corrected (real script order, data sources, Quarto+Typst render); Result
  paragraph added. (uncommitted at time of writing)
- DEAD END: Python 3.13 + numpy>=2.2 makes uv resolve cellxgene-census onto ancient numba 0.53.1
  (py<3.10 only) via tiledbsoma->scanpy; fixed by pinning py3.11 + numpy<2 (gets tiledbsoma 2.3.0).
- DEAD END: HPA immunofluorescence subcellular localization gives FALSE NEGATIVES for known surface
  targets (FOLH1, STEAP1, STEAP2, CD276 all show "not plasma membrane"); cannot be used as a hard
  surface-accessibility gate. Used curated compartment instead; HPA still correctly flags prostein
  (SLC45A3) as vesicular -> demoted from nomination.
- Pending: minimal-R scDblFinder doublet refinement (scripts 12/13 + doublet_scdblfinder.R present,
  container quay.io/biocontainers/bioconductor-scdblfinder:1.24.0 pulled), nf-core/scdownstream
  background run (Nextflow 26.04.6 + JDK17 installed), demo figure set, written 100-200 word summary,
  claude_tooling_log.md update.

### 2026-07-13 - Session 3 (doublet removal made primary)

- User decision: make doublet-removed singlets the PRIMARY scoring input (not just the robustness QC
  that was already committed). scDblFinder R step had already run; this session applied the removal.
- `14_apply_doublet_removal.py` drops the 3,282 flagged doublets after prepare, writes
  `tumor_cells_singlets.parquet` (gitignored) + `doublet_removal.csv`. `load_scan_frames` now reads the
  singlet table and RAISES if it is absent - no silent all-cells fallback (Rule 1). Scripts 30/31/56/70
  inherit singlets through the loader; 40/50/55 inherit through the tables; 13 keeps the all-vs-singlet QC.
- Re-ran 14->30->31->32->40->50->55->56->70->13->90 on 3,590 malignant singlets (was 3,802). Finding
  holds and slightly strengthens: PSMA x STEAP1 median 0.68->0.69 (6.5x->6.7x PSMA-PSCA), malignant-vs-
  benign 0.585->0.601; STEAP1 x HPN Q0.10 0.47->0.48. Safety numbers identical (healthy cells are not
  doublet-filtered): PSMA 0.87 / PSCA 0.92 / AND 0.13, ~7x collapse. Negative control 79%->80%. Positive
  control still RECOVERED.
- Report Methods gained a table-bound doublet-removal bullet; Data notes the singlet count. README
  regenerate sequence now lists the doublet steps (12 -> container -> 14 -> 13) because scoring requires
  the singlet table. README/submission_summary/claude_tooling_log numbers reconciled to singlets.
- BUG FIXED (pre-existing): `Markdown(...)` nested in an `if` was never emitted, so the residual-liability
  table had been silently missing from the rendered report; also would have dropped the new doublet bullet.
  Switched conditional blocks to `display(Markdown(...))`. Report re-rendered HTML+PDF; both verified to
  carry the new numbers, the doublet bullet, and the residual-liability table. pytest 6/6 green.
- `7002e68` feat: apply scDblFinder doublet removal as primary scoring input.
- `f76adb0` docs: describe doublet removal in report, reconcile singlet numbers.
- User direction: results belong in the report only; README should be overview + competition link +
  reproduce steps. Stripped the README Result paragraph (which also retired the "across 24 patients"
  wording concern), added the CV event-page link, pointed readers to `reports/report.pdf` for findings.
- User direction: doublet robustness matters, so add a QC figure to the report Methods. Drew it
  in-document from `doublet_qc.csv` (all cells vs scored singlets, per-pair delta annotated); report now
  carries 6 in-document figures. HTML+PDF re-rendered and verified.
- `d82dfb1` docs: keep README to overview and reproduce steps, link the competition.
- `eebf23a` docs: add doublet-robustness QC figure to report Methods.

### 2026-07-13 - Session 4 (peer-review revision: P0 confound fix + P1 claims + P2 citations)

- Peer review received. Its top concern: mixing scRNA assays under one raw-count threshold could
  confound the normal-tissue liabilities. VERIFIED from raw data: tumor is 100% 10x 3' v3; the pulled
  Tabula Sapiens 2.0 is 90.3% 10x 3' v3 but 3.7% Smart-seq2 + 5.9% 10x 5' v2. The scan also POOLED
  healthy across donors (bias the tumor side already avoids). User approved scope P0+P1+P2 with the
  healthy design "10x 3' v3 only + donor-robust".
- P0 fix: `11_prepare_healthy.py` filters to `assay == "10x 3' v3"` (carries `assay`); `00_fetch_data.py`
  adds the assay filter to the Census pull for reproducibility. `scan.py` `_donor_robust_healthy`:
  per donor x population fraction, median across donors, MIN_CELLS_DONOR=10, MIN_DONORS=2; worst-liability
  rows now carry worst_xp_n_donors / worst_xp_n_cells. 55/56 propagate the support columns; 56 profile is
  donor-robust too. Test updated (synthetic healthy now 2 donors).
- Impact (assay-matched + donor-robust): positive control HELD (single 0.85/0.95 -> pair 0.15, ~6x).
  The reported PSMA x STEAP1 worst 0.28 was a 39-cell single-donor Smart-seq2 artifact; corrected it is
  0.167 (mucus secreting cell, 5 donors), ~level with PSMA-PSCA 0.153. STEAP1 x HPN worst 0.166
  (hepatocyte - the tissue the reviewer flagged for HPN). Negative control 80% -> 57% (donor-robust also
  cleans the comparison pairs; honest, weaker). Healthy populations 585 pooled -> 442 donor-replicated.
  Fixing the confound STRENGTHENED the finding.
- P2 citations verified by a web subagent (Rule 1): localized atlas now PUBLISHED in Cancer Research 2026
  (Apostolov et al., DOI 10.1158/0008-5472.CAN-25-1202, PMID 41879555); healthy ref is Tabula Sapiens 2.0
  (bioRxiv 2024.12.03.626516, >1.1M cells / 28 tissues). references.bib + report Data updated.
- P1 claim discipline (report + README + summary): clinically -> preclinically validated; safe /
  off-tissue / qualifying targetability -> transcript co-detection + normal-tissue liability + membrane
  plausibility; unsupervised -> systematic scan of a curated panel; translatable lead -> translationally
  tractable candidate; Pareto-optimal -> Pareto-front; NOT gate reframed as a NEGATIVE result (no usable
  candidate, best escape 0.41); dropped "never a count>0 call"; softened PSCA-dropout; added Boolean-gate
  screening-abstraction caveat and a hypothesis-generating Conclusion.
- P3 DEFERRED (noted in Limitations): per-patient beta-binomial CIs, bootstrap-over-patients intervals,
  donor-level upper confidence bound for liability. Point estimates only for now.
- `3d8a0f4` feat: assay-match healthy reference to 10x 3' v3 and make liability donor-robust.
- `81b2c7d` docs: revise report for peer review - claim discipline and citations.
