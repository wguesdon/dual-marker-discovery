# CS09 — Statistical best practices for single-cell target ranking

- **Type:** literature search — text answer (Claude Science workbench)
- **Purpose:** Identify the statistical upgrades that would most strengthen our Pareto-frontier target ranking.
- **Attach:** none — web literature only.

## Prompt

Review the statistical and validation best practices for ranking candidate targets from single-cell data,
to critique a per-patient Boolean co-occurrence scan that ranks marker pairs on a Pareto frontier of
lower-quantile tumor coverage vs worst-case healthy-cell liability, currently with bootstrap-over-patient
intervals for the lead pair only.

Cover, each with a citation (DOI/URL) and a one-line "how to apply it here":

- pseudobulk vs per-cell testing and pseudoreplication (Squair et al. 2021; muscat/Crowell);
- differential-abundance methods and FDR (Milo, propeller, scCODA, sccomp);
- beta-binomial / Dirichlet-multinomial overdispersion and compositionality models for proportions;
- hierarchical / mixed-effects models with donor random effects and empirical-Bayes shrinkage;
- cross-dataset comparability, library-depth normalization, and downsampling;
- multiple-testing and selection optimism when scanning many candidate pairs (re-running selection inside
  the bootstrap; Pareto-membership probability);
- cross-cohort replication norms.

Return a prioritized list (highest impact first) of the statistical upgrades that would most strengthen
this pipeline, and note which are achievable in a day vs a larger effort.

## Results

_Paste the Claude Science answer here (keep the sources/citations)._

## Follow-up / notes

_Top 1-2 upgrades to implement next; anything that would change a ranking._
