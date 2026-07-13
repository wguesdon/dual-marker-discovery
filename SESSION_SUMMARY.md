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
