# Project: Combinatorial Surface-Marker Targets for Prostate Cancer

**Track:** Researcher (Build From the Bench)
**Working title:** ANDmark-PCa — patient-robust discovery of dual-antigen surface targets in prostate adenocarcinoma
**Status:** scoping

## One-line summary

Use single-cell data (open to proteomic evidence) to find pairs of cell-surface proteins that are co-present on prostate cancer cells but not on healthy cells, so a two-receptor therapy could hit the tumor while sparing normal tissue. We search both AND-gate and NOT-gate logic and benchmark against the known PSMA-PSCA pair.

## Biological question

Many targeted therapies fail on safety, not potency. A single tumor antigen is rarely absent from every healthy tissue, so single-target CAR-T, T-cell engagers, and ADCs carry on-target off-tumor toxicity. Combinatorial (logic-gated) targeting fixes this by requiring two conditions before a cell is attacked.

The question: **which pair of cell-surface proteins maximizes malignant-cell targeting across prostate cancer patients while minimizing collateral risk to every healthy human cell type?**

## Two gate types (both in scope)

- **AND gate** — kill only cells positive for both A and B. Safety comes from a second tumor antigen. Objective: maximize per-patient P(A+ and B+ | tumor), minimize the worst-case P(A+ and B+ | healthy cell type). Positive calls, robust to scRNA dropout.
- **NOT gate** — kill cells positive for activator A unless blocker B is present; B marks healthy cells to spare. Objective: maximize P(A+ and B- | tumor), minimize the worst-case P(A+ and B- | healthy cell type). Opens up broadly-expressed antigens that are untargetable alone, at the cost of depending on B-negative calls, which are dropout-sensitive in scRNA.

AND gate is the validated headline; NOT gate is the novel extension, reported with the dropout caveat stated.

## Why prostate adenocarcinoma

- **Re-discoverable positive control.** PSMA (FOLH1) x PSCA is the canonical AND-gate pair, validated preclinically in split-signal CAR systems. Recovering it from an unsupervised scan is a real validation, not a claim judges must trust. STEAP1 gives a second anchor with live clinical data (xaluritamig / AMG 509, STEAP1xCD3 T-cell engager, NCT04221542).
- **Abundant single-cell data**, including pre-integrated, annotated atlases.
- **Clean normal-tissue liabilities to check against.** FOLH1 shows normal expression in kidney tubules, duodenum, and small intestine; PSCA is enriched in stomach and detected in kidney. These are exactly the signals the analysis must catch, so the indication has a real, non-trivial safety question.

## Known combinatorial-targeting context (for the write-up)

| Markers | Logic | Modality | Status |
|---|---|---|---|
| PSMA + PSCA | AND (split-signal) | CAR-T | preclinical, our benchmark |
| PSMA + CD70 | AND (bispecific) | CAR-T | NCT05437341, first logic-gated CAR-T for mCRPC |
| STEAP1 x CD3 | single-target TCE | T-cell engager | NCT04221542, ~41% ORR high dose |
| CEA / MSLN / EGFR + HLA-A*02 | NOT (LOH blocker) | Tmod CAR-T (A2 Bio) | NCT05736731 / NCT06051695 / NCT06682793 — other solid tumors, not prostate; HLA LOH is genomic, not scRNA-recoverable |

## Data stack

**Tumor (discover + replicate on independent cohorts)**
- HuPSA — Human Prostate Single-cell Atlas (~369k cells, 6 studies, annotated). Primary discovery set.
- A large integrated prostate atlas (~128 patients, ~560k cells) as an independent replication cohort.
- Chen et al. 2021, GSE141445 (~36k cells, 13 patients) as a smaller well-labeled reference.

**Healthy comparator (the denominator for the safety claim)**
- Tabula Sapiens (~500k cells, ~24 organs, healthy). The core off-tumor reference.
- CELLxGENE Census for programmatic pulls and differential expression.

**Protein / surface evidence**
- Human Protein Atlas — surface/membrane localization plus normal-tissue distribution and IHC (the surface-targetability and normal-tissue-risk layer).
- PaxDb — tissue-level protein abundance to confirm candidates are present at the protein level.
- CPTAC / PDC prostate proteogenomics as supportive tissue-level evidence.

## Candidate surface panel (starting point, ~30 curated)

FOLH1 (PSMA), PSCA, STEAP1, STEAP2, TACSTD2 (TROP2), CD276 (B7-H3), DLL3, KLK2 (comparator, secreted), plus top differentially-expressed membrane genes discovered from the tumor data.

Use FOLH1-PSCA as the positive control; test whether pairs such as PSCA-STEAP1 or FOLH1-STEAP1 improve on it. Present alternatives as hypotheses until the analysis supports them.

## Analysis design

1. Load tumor (HuPSA) and healthy (Tabula Sapiens) references.
2. Confirm malignant identity using author labels; note that CNV-based confirmation and ambient-RNA/doublet correction are future-work refinements if time is short.
3. Restrict to the curated surface panel plus discovered membrane candidates.
4. For every candidate pair, compute per-patient AND scores and worst-case healthy co-expression. Repeat with inverted blocker for NOT scores.
5. Rank on a Pareto frontier: maximize the lower patient quantile (e.g. Q0.10) of tumor coverage, maximize median tumor coverage, minimize the worst healthy-cell-type liability. Report AND coverage (specificity) and OR coverage (antigen-escape) separately.
6. Recover PSMA-PSCA as the labeled control, then surface improved AND pairs and exploratory NOT pairs.
7. Cross-check top pairs against HPA localization/normal-tissue and PaxDb abundance.

## Methodological pitfalls to state explicitly

- Do not define expression as count > 0. A scRNA zero is not proof of absence. Use multiple thresholds and pseudo-bulk per cell type and donor.
- Do not pool all malignant cells before scoring; a high-cell-count patient would dominate. Score per patient, then summarize.
- NOT-gate calls trust B-negatives, which are dropout-sensitive. Flag NOT results as exploratory.
- Transcript evidence is not targetability. Antigen density, epitope accessibility, shedding, isoform specificity, and internalization all matter; scRNA cannot settle them.
- Bulk proteomics cannot prove same-cell co-expression. CITE-seq, multiplex IHC, or dual-color flow are the real validation, named as next steps.

## Prior art to differentiate against

A March 2025 bioRxiv preprint performs single-cell-guided logic-gated antigen discovery. The general method is therefore not novel. Our defensible angle: per-patient robust scoring (not pooled cells), explicit AND-versus-OR and AND-versus-NOT reporting, and benchmark recovery of PSMA-PSCA followed by ranked improvement. State this framing up front.

## Deliverable

A reproducible notebook plus a short write-up that: (1) recovers PSMA-PSCA as a positive control, (2) nominates at least one improved AND pair and one exploratory NOT pair with per-patient tumor coverage and worst-case healthy-cell risk, (3) backs top pairs with HPA localization and PaxDb abundance, and (4) states uncertainty and the validation experiments that would come next. A discrete, reproducible finding, not a ranked candidate list.

## Three-minute demo arc

1. Single targets and their normal-tissue liabilities.
2. Scatter: tumor AND-coverage vs worst-normal-cell co-expression, Pareto-optimal pairs highlighted.
3. PSMA-PSCA recovered as the positive control.
4. One new pair: per-patient tumor coverage, healthy-cell risk, single-cell co-expression, protein evidence, replication.
5. Close: "Pair X improves worst-case healthy-cell separation over PSMA-PSCA while retaining dual-positive malignant cells in Y of Z independent patients."

## Scope note

The full Pareto, two-cohort, ambient-corrected pipeline is multi-day. The minimum honest version for a tight deadline: HuPSA tumor, Tabula Sapiens healthy, ~30 curated genes, per-patient co-expression, one Pareto scatter, PSMA-PSCA recovered, one new AND pair and one NOT pair highlighted with caveats. CellBender, doublet removal, CNV malignant calling, and second-cohort replication move to the future-work slide.
