# Claude Science workbench outputs

Deliverables from the Claude Science UI runs described in `../tasks/`. They are kept here so the repo
records what the tasks **concluded**, not only that they ran: the `csNN_*.md` task files hold the pasted
workbench transcript, while the written answers and their backing tables live in this directory.

## Read these as literature, not as results

**These are not pipeline output.** `make` does not regenerate them and they are not inputs to any committed
analysis. They are Claude Science literature syntheses, built from GTEx, the Human Protein Atlas and
OpenAlex. The kernel code that produced them is reconstructed in `../scripts/`. The data pulls there run
only inside the workbench, since they go through a connector bridge that does not exist in this repo. The
heatmap is the exception: it regenerates from `gtex_median_tpm.csv` below, pixel for pixel, using the
committed plotting cells.

A claim from this directory enters `reports/report.qmd` only after it is checked against the cited primary
source. Every file carries DOIs for that purpose: `cs08_normal_tissue_liabilities/literature_refs.csv` maps
each claim to its DOI and URL.

Only the report-usable subset is committed. The remaining workbench deliverables (the AND/NOT-gate method
surveys, the dataset and proteomics reviews, the statistics review, the CS10 peer review) stay local by the
policy in `../README.md`.

## cs08_normal_tissue_liabilities

The safety-side evidence for the 10 candidate surface antigens. This is the protein-level counterpart to
the scRNA co-detection estimate, which the report itself names as a surrogate rather than a safety measure.

| File | What it is |
|---|---|
| `antigen_safety_review.md` | The full written answer: master risk table, per-antigen normal expression, toxicity, polarity. |
| `risk_reclassification.md` | Antigens whose protein reality moves their safety rank away from the transcript estimate. |
| `concordance.csv` | HPA RNA vs IHC per antigen, with reliability category and a concordance call. |
| `antigen_risk_table.csv` | Per-antigen risk note with GTEx top normal tissues, polarity, toxicity, DOIs. |
| `gtex_median_tpm.csv` | GTEx v8 median TPM, 10 genes x 54 tissues. Source data for the heatmap. |
| `hpa_summary.csv` | HPA release 25.1 RNA + IHC fields, including reliability category. |
| `literature_refs.csv` | Claim to DOI map for every cited statement. |

The heatmap built from `gtex_median_tpm.csv` is committed as
`results/figures/fig_s1_gtex_normal_tissue_tpm.png`.

Two findings here matter for the report:

- **`concordance.csv` independently corroborates the HPA overrule.** The tooling log records Claude Code
  declining to use HPA localization as a hard surface gate, because HPA calls PSMA, STEAP1 and CD276 "not
  plasma membrane". This run reached the same conclusion from the other direction and supplies the reason:
  STEAP1's IHC "Not detected" rests on a single antibody (HPA030985) at *Uncertain* reliability, so it is
  assay-limited, not biological absence. TMPRSS2 is discordant on the same grounds despite an *Enhanced*
  tag. Two independent runs, one verdict.
- **HPN's transcript signal overstates its risk.** Protein concentrates in liver and is weak in kidney and
  pancreas, so the broad RNA liability is not matched at the protein level.

## cs03_clinical_dual_target

`prostate_combinatorial_therapies.{md,csv}` — approved and clinical dual-target / logic-gated prostate
programs, with sponsor, phase, NCT identifier and reported efficacy. Covers xaluritamig (Phase 3 XALute),
ABBV-969 (Phase 1, 45% confirmed ORR), the Kloss 2013 PSMA x PSCA split-signal prototype, P-PSMA-101 and
the PSMA/CD70 bispecific. The report cites ABBV-969 already; this is the surrounding clinical context.

## Note on the CS10 peer review (not committed here)

The workbench peer review (`rev/peer_review_combinatorial_targets.md`, kept local) returns a **Major
revision** verdict and states that the computed PSMA x STEAP1 single-cell AND-gate coverage result "is not
present in the record".

**That verdict is scoped to the workbench project, not to this repository.** The reviewer saw only the
literature files listed in its own header. It never saw the pipeline in `scripts/`, which computes exactly
the per-cell AND coverage it says is missing. Its algebra point (a marginal prevalence is an upper bound on
the AND, not the AND itself) is correct and is precisely what the per-cell scoring here measures. Do not
read it as a review of `reports/report.qmd`.
