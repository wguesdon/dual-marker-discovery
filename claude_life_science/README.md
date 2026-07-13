# Claude Science task set

Literature-search and review tasks run in the **Claude Science workbench** (the UI), where the answer we
want is a well-sourced **text answer**, not a committed analysis. Each `tasks/csNN_*.md` file holds one
task: its purpose, the exact prompt to paste into Claude Science, and a box to paste the answer back into.

The focus here is **literature and review, not new analysis**: exploring methods for AND / NOT dual-marker
discovery, the approved dual-target landscape, key datasets, and adversarial review of the report. A
finding only enters the report once it has earned a committed script and table in the main pipeline.

## Workflow (workbench machine)

1. `git pull`.
2. Open a task file in `tasks/`, paste its **Prompt** into Claude Science (attach `reports/report.pdf`
   only where the task says to).
3. Paste the text answer into the task file's **Results** section; keep the sources/citations.
4. `git commit` and `git push`.

**Only the `.md` files are committed.** Screenshots (`img/`) and any exported artifacts (`results/`) are
gitignored on purpose — we keep only the prompts and the text answers. A two or three line summary of a
run that should change the report goes into `docs/claude_tooling_log.md`.

## Tasks

| Task | Focus | Attach |
|---|---|---|
| CS01 | Methods for AND-gate dual-marker discovery | none (web) |
| CS02 | Methods for NOT-gate / inhibitory-logic targets | none (web) |
| CS03 | Approved and clinical dual-target / logic-gated prostate therapies | none (web) |
| CS04 | Clinically validated single prostate surface antigens and their binders | none (web) |
| CS05 | Key single-cell RNA-seq prostate cancer datasets | none (web) |
| CS06 | Key proteomics / surface-proteomics prostate datasets | none (web) |
| CS07 | Antigen expression shifts in mCRPC / neuroendocrine disease | none (web) |
| CS08 | Normal-tissue expression liabilities of candidate antigens | none (web) |
| CS09 | Statistical best practices for single-cell target ranking | none (web) |
| CS10 | Adversarial review of the report | `reports/report.pdf` |
