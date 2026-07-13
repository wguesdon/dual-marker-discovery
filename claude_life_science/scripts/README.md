# Claude Science kernel code

The workbench runs each analysis step as a cell in an ephemeral Jupyter kernel. Those cells are never
written to the workspace, so the deliverables in `../outputs/` arrived with no visible code behind them.
They are recorded verbatim in the workbench store (`operon-cli.db`, table `execution_log`), and these
scripts are reconstructed from that record, cell by cell, in execution order.

One script per task, covering the two tasks whose deliverables are committed:

| Script | Cells | Produces |
|---|---|---|
| `cs08_normal_tissue_liabilities.py` | 18 of 22 | `results/figures/fig_s1_gtex_normal_tissue_tpm.png` and the whole `../outputs/cs08_normal_tissue_liabilities/` pack |
| `cs03_clinical_dual_target.py` | 5 of 5 | `../outputs/cs03_clinical_dual_target/prostate_combinatorial_therapies.{md,csv}` |

## What runs here, and what does not

**The data pulls do not.** Every external fetch goes through `host.mcp(server, method, **kwargs)`, the
workbench connector bridge to GTEx, the Human Protein Atlas and OpenAlex. That name exists nowhere in this
repo, so cells 0-9 and 13-16 of CS08 are a record of how the data was obtained, not a way to obtain it
again.

**The figure does.** CS08 cell 11 builds the heatmap and reads exactly one input,
`gtex_median_tpm.csv`, which is committed at `../outputs/cs08_normal_tissue_liabilities/`. Cell 10 is the
workbench `figure-style` skill, and it is not an import: it defines `apply_figure_style()` and its helpers
inline, so it came across in the extraction. Cells 10 and 11 together therefore regenerate the figure from
committed data, with no workbench and no network.

That was checked rather than assumed. Running cells 10 and 11 against the committed CSV in a clean
directory reproduces `results/figures/fig_s1_gtex_normal_tissue_tpm.png` **pixel for pixel**: 0 of
6,052,606 pixels differ, max channel delta 0. The figure is not an orphan artifact; it is derived from
committed data by committed code.

## Reading the scripts

Cells share one kernel, so a later cell depends on names bound by an earlier one. Cells that errored and
were retried are left out and the successful retry kept; the header of each script lists what was dropped
and why. CS08 cell 17 is a `diff` rather than kernel code, an edit the agent applied directly to
`risk_reclassification.md`.

The eight other task frames (CS01, CS02, CS04-CS07, CS09, CS10) also have code in the workbench store,
between 1 and 23 cells each. It is not extracted here, because their deliverables are not committed.
