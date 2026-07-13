# Submission summary

_100-200 word written summary for the Built with Claude: Life Sciences submission._

Which pair of cell-surface proteins marks prostate cancer cells while sparing every healthy human
cell type? Single-antigen therapies are limited by on-target off-tumor toxicity, because few antigens
are absent from all normal tissue. We scored combinatorial surface-marker pairs, AND gates and NOT
gates, per patient across a 24-patient localised prostate cancer atlas, against an assay-matched,
donor-robust Tabula Sapiens reference (~1.0 million 10x cells) and a matched benign-prostate control
from the same tumors. The method recovers the preclinically validated PSMA-PSCA pair as a positive
control: each antigen alone engages duodenum or bladder, and requiring both collapses the worst
extra-prostatic transcript co-detection roughly sixfold. It then nominates surface-accessible pairs
with higher malignant co-detection than the benchmark at comparable predicted normal-tissue liability:
PSMA x STEAP1 (clinical binders already in humans, 6.7 times the per-patient coverage) and the
Pareto-front STEAP1 x hepsin; the NOT gate yields no usable candidate. Claude Code found the datasets,
debugged the single-cell dependency stack, removed scDblFinder-flagged doublets in an R container
before scoring, and checked every liability against the Human Protein Atlas. The recovered benchmark is
a reproducible result; the nominated pairs are hypothesis-generating candidates for protein-level
validation, not a ranked list.
