# Claude Science task set

Each `claude_science_task_csN_*.md` file holds one task: what it is for, what to upload, a prompt to
paste into the Claude Science workbench, and a box to paste the output back into. Figures go into
`img/`, saved artifacts into `results/CSN/`, and a two or three line summary of each run goes into
`docs/claude_tooling_log.md`.

The workbench is where external datasets the pipeline has not touched get pulled in: literature checks,
clinical annotation of the top pairs, protein-level cross-checks, and adversarial review of the frozen
result. The report is not changed by a workbench run unless a finding is strong enough to earn a
committed script and table first.

## Planned tasks

| Task | What it does | Needs external data |
|---|---|---|
| CS1 | Literature check: PSMA-PSCA AND-gate, STEAP1 engager, A2 Bio Tmod NOT-gate. Confirm the benchmark and the clinical framing. | literature |
| CS2 | Clinical / target annotation of the top-ranked pairs (Open Targets, clinical trials). | Open Targets, ClinicalTrials.gov |
| CS3 | Protein cross-check: HPA localization and normal-tissue liability, PaxDb abundance for the top pairs. | HPA, PaxDb |
| CS4 | Reviewer-agent critique of the frozen report. A review that finds nothing has failed. | the frozen report |
| CS5 | Steelman the null: how well does a single best marker do without the second? Does the gate actually add specificity? | none |

Order and additional tasks are decided as the pipeline produces tables. This file is the plan; the
committed `claude_science_task_*.md` files are the record.
