# CS01 — Methods for AND-gate dual-marker discovery

- **Type:** literature search — text answer (Claude Science workbench)
- **Purpose:** Position our per-patient Boolean AND scan against the state of the art, and spot methods or objectives worth adopting.
- **Attach:** none — web literature only.

## Prompt

Survey the computational methods for discovering AND-gate combinatorial cell-surface antigen targets
(both markers positive on the same tumor cell) for logic-gated cell therapies (CAR-T, T-cell engagers,
ADCs) from omics data. For each method give, with a citation (DOI or URL):

- input data (bulk vs single-cell; which tumor and normal references it uses);
- whether scoring is per-patient or pooled / pseudobulk;
- the objective and algorithm (supervised classifier, integer-programming hitting set, genetic algorithm,
  plain Boolean co-occurrence, etc.);
- whether it integrates protein-level data;
- whether it quantifies uncertainty (CIs, FDR, bootstrap);
- whether it uses a known validated pair as a positive control;
- the largest combination order it searches (pairs, triples, N-antigen circuits).

Include at least: Kwon et al. 2023 (Nat Biotechnol), Dannenfelser/Yosef et al. 2020 (Cell Systems),
MadHitter (Nat Commun 2022), LogiCAR designer (Ruppin lab, bioRxiv 2025), SCAN-ACT (Testa et al., Genome
Medicine 2025), Perna et al. 2017 (Cancer Cell), Gottschlich et al. 2023 (Nat Biotechnol). Add any newer
methods you find.

Return (1) a comparison table across those axes and (2) a short paragraph on what the state of the art
does that a curated-panel, per-patient Boolean scan (like ours) does not — and one or two ideas we could
realistically adopt. Cite everything.

## Results

_Paste the Claude Science answer here (keep the sources/citations)._

## Follow-up / notes

_Methods worth adopting, disagreements, or what should change in `docs/research_plan.md`._
