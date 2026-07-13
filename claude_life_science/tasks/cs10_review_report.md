# CS10 — Adversarial review of the report

- **Type:** review — text answer (Claude Science workbench)
- **Purpose:** A skeptical, sourced peer review of the frozen report before it is treated as final. A review that finds nothing has failed.
- **Attach:** `reports/report.pdf` (pull the latest first).

## Prompt

Act as a rigorous, skeptical peer reviewer of the attached report on combinatorial surface-marker targets
for prostate cancer. Assess and be specific:

1. Is the scientific premise and the Boolean AND / NOT gate algebra sound?
2. Are the quantitative claims supported and not overstated? Point to any number that outruns its evidence.
3. Are label-leakage, assay-comparability (10x vs Smart-seq2 / chemistry), doublet handling, and
   uncertainty adequately controlled and disclosed?
4. Is the nominated pair (PSMA x STEAP1) justified given the replication finding that its coverage holds in
   AR+ adenocarcinoma but is lost in mCRPC / neuroendocrine disease?
5. Is the NOT-gate negative result interpreted correctly, or is it an artifact of the search space?
6. What controls, datasets, statistics, or citations are missing?
7. Which specific claims would you ask to be softened or retracted, and why?

Cite where you can. Return a severity-ranked list of issues, each with a concrete fix, followed by a
one-paragraph overall verdict (accept / minor revision / major revision, with the single most important
thing to fix first).

## Results

_Paste the Claude Science answer here (keep the sources/citations)._

## Follow-up / notes

_Which issues become committed fixes vs future work; log material changes in `docs/claude_tooling_log.md`._
