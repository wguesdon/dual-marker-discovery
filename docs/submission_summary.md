# Submission summary

_100-200 word written summary for the Built with Claude: Life Sciences submission._

Which pair of cell-surface proteins marks prostate cancer cells while sparing every healthy human cell
type? Antigen-directed therapies are limited by on-target off-tumor toxicity; few antigens are absent from
all normal tissue. We scored combinatorial surface-marker pairs, AND gates and NOT gates, per patient
across a 24-patient localised prostate cancer atlas, against an assay-matched, donor-robust Tabula Sapiens
reference and a matched benign-prostate control from the same tumors. The method recovers the
preclinically validated PSMA-PSCA pair as a positive control: each antigen alone engages duodenum or
bladder, and requiring both collapses the worst extra-prostatic co-detection roughly sixfold. It nominates
one clean surface pair, PSMA x STEAP1 (both antigens have clinical binders; the pair is already a phase-1
dual ADC), and finds no usable NOT gate. An independent 369,000-cell cohort (HuPSA) confirms
tumor-specificity but shows the pair covers AR-driven adenocarcinoma and is lost in metastatic and
neuroendocrine disease. Claude Code drove the pipeline (datasets, containerised doublet removal and cohort
conversion, uncertainty and label-leakage controls, a multi-agent report review); Claude Science added
the literature survey and a GTEx and Protein Atlas protein-level safety cross-check. This is a
reproducible, hypothesis-generating finding with a truth value, not a validated target.

## Links

- **Live site:** https://base-by-base.com — the project overview, the full report, and an interactive
  marker-pair explorer.
- **Demo video (3 min):** _add link after recording._
- **Repositories (open-source, MIT):**
  - Analysis and report: https://github.com/wguesdon/dual-marker-discovery
  - Website: https://github.com/wguesdon/dual-marker-discovery-site
  - Explorer app: https://github.com/wguesdon/dual-marker-discovery-app
