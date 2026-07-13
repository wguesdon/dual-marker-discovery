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

This is a methods-review/critique task, so I'll ground the citations by verifying the key DOIs rather than relying on memory. Let me confirm a few of the less-obvious ones. Good — those four are confirmed. Let me verify the remaining core DOIs I'll cite. All core DOIs are confirmed. I have what I need to write the critique — this is a methods review, so I'll compose it directly rather than run code. Let me save it as a report artifact and give you the full content inline.


Ran 8 searches, edited a file, saved artifacts
10 steps

Writing statistical critique report markdown

Web Search·propeller testing differences cell type proportions Phipson …
9 results

Web Search·sccomp Mangiola robust differential composition variability …
10 results

Web Search·Zimmerman practical solution pseudoreplication bias single-c…
10 results

Web Search·dream powerful differential expression repeated measures Hof…
8 results

Web Search·Squair confronting false discoveries single-cell differentia…
9 results

Web Search·Milo differential abundance k-nearest neighbor graphs Dann N…
7 results

Web Search·scCODA Bayesian model compositional single-cell Büttner Natu…
9 results

Web Search·muscat Crowell subpopulation-specific state transitions mult…
10 results

Saving target-ranking statistics review
1 artifact
Here's the review. I verified each core DOI against publisher/PMC records before citing. The full write-up is saved as target_ranking_stats_review.md; the substance is below.

What the pipeline does, framed statistically
Your scan is an AND-gate (logic-gated CAR / bispecific) target-discovery procedure: for each marker pair it computes a per-cell Boolean "both on," aggregates to a lower-quantile tumor coverage and a worst-case healthy liability, and ranks pairs on the Pareto frontier of those two objectives, with a patient-bootstrap CI on the lead pair only. Four things make the current inference optimistic: the unit of replication (cells vs patients), selection optimism (scanning many pairs, reporting the winner, CI computed after selection), treating proportions as binomial/deterministic rather than overdispersed and compositional, and cross-dataset technical confounding between the tumor and healthy references.

The seven topics, each with citation + how to apply
1. Pseudobulk vs per-cell testing / pseudoreplication. Cells from one patient aren't independent; the sample size is patients. Methods treating cells as replicates produce large numbers of false discoveries because they ignore between-patient variation (Squair et al. 2021, Nat Commun, https://doi.org/10.1038/s41467-021-25960-2). Pseudobulk aggregation or a patient term restores calibration (muscat — Crowell et al. 2020, https://doi.org/10.1038/s41467-020-19894-4; Zimmerman et al. 2021, https://doi.org/10.1038/s41467-021-21038-1). Apply: compute every pair's coverage and liability once per patient, then aggregate across those — never pool raw cells. Your lead-pair bootstrap already uses the right unit; extend it to all scores.

2. Differential-abundance methods and FDR. "Healthy liability" is a DA question. Milo tests abundance on k-NN neighborhoods with spatial-FDR control (Dann et al. 2022, Nat Biotechnol, https://doi.org/10.1038/s41587-021-01033-z); propeller uses biological replication with an empirical-Bayes linear model on transformed proportions (Phipson et al. 2022, Bioinformatics, https://doi.org/10.1093/bioinformatics/btac582); scCODA is a Bayesian Dirichlet-multinomial for low replicate counts (Büttner et al. 2021, https://doi.org/10.1038/s41467-021-27150-6); sccomp is a constrained beta-binomial mixed model that also models differential variability (Mangiola et al. 2023, PNAS, https://doi.org/10.1073/pnas.2203828120). Apply: run each candidate AND-positive population through sccomp or propeller (closest fit to a patient-replicated design) for an FDR-controlled, replicate-aware healthy-abundance estimate with an interval; BH-adjust across pairs.

3. Beta-binomial / Dirichlet-multinomial overdispersion & compositionality. Proportions between patients are overdispersed relative to binomial, and compositional (constrained to sum to 1), so naïve per-population bars are too narrow and biased (Aitchison 1982, https://doi.org/10.1111/j.2517-6161.1982.tb01195.x; Gloor et al. 2017, https://doi.org/10.3389/fmicb.2017.02224; modeled directly by sccomp and scCODA above). Apply: model the per-patient AND-positive count as beta-binomial (count out of cells profiled), which widens liability intervals honestly and stops one high-count patient dominating.

4. Hierarchical / mixed models + empirical-Bayes shrinkage. A GLMM with a patient random effect is the principled account of within-patient correlation (Zimmerman et al. 2021, above; dream — Hoffman & Roussos 2021, https://doi.org/10.1093/bioinformatics/btaa687), and EB shrinkage stabilizes noisy per-pair estimates (limma — Smyth 2004, https://doi.org/10.2202/1544-6115.1027). Apply: fit AND_positive ~ tissue + (1|patient) per pair and rank on shrunken estimates — this reorders a frontier currently driven by low-n outlier patients.

5. Cross-dataset comparability, depth normalization, downsampling. A Boolean "off" is confounded by depth: a marker reads off from dropout, not absence, and if tumor and healthy references come from different platforms, depth/batch masquerade as coverage/liability. Depth-aware normalization mitigates it (scran — Lun et al. 2016, https://doi.org/10.1186/s13059-016-0947-7; sctransform — Hafemeister & Satija 2019, https://doi.org/10.1186/s13059-019-1874-1). Apply: downsample all datasets to a common median depth before gating, re-derive detection thresholds, and confirm top pairs are stable to the downsampling seed.

6. Multiple testing & selection optimism (the largest gap). Reporting the frontier winner with a CI on only the selected pair is winner's-curse bias. The established fix is that all selection steps must be repeated inside every resample or error is badly underestimated (Ambroise & McLachlan 2002, https://doi.org/10.1073/pnas.102162899; Varma & Simon 2006, https://doi.org/10.1186/1471-2105-7-91). Pareto-membership probability — fraction of bootstraps where a pair lands on the frontier — is the direct analogue of stability selection (Meinshausen & Bühlmann 2010, https://doi.org/10.1111/j.1467-9868.2010.00740.x); BH across pairs (Benjamini & Hochberg 1995, https://doi.org/10.1111/j.2517-6161.1995.tb02031.x). Apply: wrap the entire pipeline (recompute per-patient scores → both objectives → re-identify frontier) inside the patient bootstrap; report per-pair Pareto-membership probability and intervals on both objectives, for all contenders.

7. Cross-cohort replication norms. Marker-combination claims for therapeutic prioritization require independent-cohort validation and transparent, pre-specified reporting (REMARK — McShane et al. 2005, https://doi.org/10.1093/jnci/dji237; TRIPOD — Collins et al. 2015, https://doi.org/10.1136/bmj.g7594). Apply: lock top pairs on discovery, re-estimate coverage/liability on a held-out cohort, and treat replication of the trade-off (not just re-detection of the markers) as success.

Prioritized upgrades (highest impact first)
Re-run the full selection inside the bootstrap; report Pareto-membership probability + intervals for all contending pairs (§6). Removes the biggest current bias (winner's curse). ~1 day — the bootstrap machinery exists; just wrap the whole ranking, not the lead.
Make every score patient-level with patient-bootstrap CIs for all pairs (§1). Fixes pseudoreplication. ~1 day.
Beta-binomial GLMM with patient random effect + EB shrinkage; replace "worst-case max" liability with a shrunken tail quantile / upper prediction bound (§3–4). Extreme statistics have huge variance at small n. Medium, 2–4 days.
Depth-normalize + downsample references to common depth before gating; report detection-rate-vs-depth; check seed stability (§5). Medium, 2–3 days.
Reframe healthy liability as FDR-controlled DA (sccomp/propeller/Milo); BH across pairs (§2). Medium, 2–3 days.
External cross-cohort replication of top pairs (§7). Larger — needs a second dataset and harmonization.
One-day wins: #1 and #2 — both reuse the existing patient-bootstrap and kill the two largest biases. Do these first. Larger: #3–#5 add a modeling layer; #6 needs another cohort.

One structural note worth flagging: your "worst-case (max) healthy liability" and "lower-quantile coverage" are both extreme order statistics, which are exactly the quantities with the worst small-sample variance and the strongest sensitivity to a single patient. Upgrades #2 and #3 together — patient-level scoring plus shrinkage toward a beta-binomial tail bound — are what convert those extremes from brittle point summaries into defensible estimates, and they're a natural pairing to tackle right after the bootstrap-wrapping in #1.

## Follow-up / notes

_Top 1-2 upgrades to implement next; anything that would change a ranking._
