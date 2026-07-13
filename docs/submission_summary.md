# Submission summary

_100-200 word written summary for the Built with Claude: Life Sciences submission._

Which pair of cell-surface proteins marks prostate cancer cells while sparing every healthy human
cell type? Single-antigen therapies fail on safety, because few antigens are absent from all normal
tissue. We scored combinatorial surface-marker pairs, AND gates and NOT gates, per patient across a
24-patient localised prostate cancer atlas, against 1.1 million Tabula Sapiens healthy cells and a
matched benign-prostate control from the same tumors. The method recovers the clinically validated
PSMA-PSCA pair as a positive control: each antigen alone engages duodenum or bladder, and requiring
both collapses the worst extra-prostatic liability roughly sevenfold. It then nominates
surface-accessible pairs that improve on the benchmark: PSMA x STEAP1, two antigens with clinical
binders already in humans and 6.5 times the per-patient coverage, and the Pareto-optimal STEAP1 x
hepsin. Claude Code found the datasets, debugged the single-cell dependency stack, ran scDblFinder
doublet detection in an R container, and checked every liability against the Human Protein Atlas.
The result is a reproducible finding with a truth value, not a ranked candidate list.
