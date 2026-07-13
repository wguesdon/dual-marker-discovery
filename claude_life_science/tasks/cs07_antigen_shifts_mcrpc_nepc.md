# CS07 — Antigen expression shifts in mCRPC / neuroendocrine disease

- **Type:** literature search — text answer (Claude Science workbench)
- **Purpose:** Interpret our replication finding that PSMA x STEAP1 coverage is lost in advanced/dedifferentiated disease.
- **Attach:** none — web literature only (optionally `reports/report.pdf` for context).

## Prompt

Summarize how prostate-cancer cell-surface-antigen expression changes with disease progression and
lineage plasticity, focusing on metastatic castration-resistant (mCRPC) and neuroendocrine (NEPC) /
double-negative disease. Center on PSMA (FOLH1), STEAP1, PSCA, and AR-lineage dependence.

Address, with citations (DOI/URL):

- protein-level prevalence of PSMA vs STEAP1 across metastatic sites (e.g. reports of STEAP1 ~87.7% vs
  PSMA ~60.5% positivity, and STEAP1-positive / PSMA-negative fractions);
- coordinated loss of AR-lineage antigens (including PSMA and STEAP1) under neuroendocrine
  transdifferentiation and in double-negative prostate cancer;
- heterogeneity across metastatic sites and after AR-pathway inhibitors, taxanes, or PSMA radioligand
  therapy;
- what this implies for an AND gate (both antigens must persist) versus an OR-like agent (either suffices).

We independently observed in the HuPSA cohort that a PSMA x STEAP1 AND gate covers AR+ adenocarcinoma but
falls to near zero in NEPCa / KRT7 / progenitor-like states and in mCRPC. Does the literature support this,
and what antigen or logic would better cover advanced disease? Return a sourced summary and a short
recommendation.

## Results

I'll research this properly against the primary literature rather than answering from memory. Let me load the literature-review skill and run targeted searches in parallel.


Loading literature-review skill
loaded
Found the key paper — the 87.7% STEAP1 vs 60.5% PSMA figures come from the STEAP1 CAR-T study (Nat Commun 2023). Let me gather the rest of the evidence base in parallel. Strong evidence base forming. Let me fill remaining gaps: double-negative CRPC prevalence, PSMA-negative screen-fail on radioligand therapy, PSCA across progression, and NEPC-specific targets. Now the last pieces: PSCA across progression, and the leading NEPC-specific surface targets (DLL3, CEACAM5) for the recommendation. I have a solid evidence base. Let me verify DOIs and fill in a few missing identifiers using CrossRef/OpenAlex before writing.


Ran 7 searches, ran 3 commands
10 steps

Verifying candidate DOIs via OpenAlex
13 lines of output

Web Search·STEAP1 87.7% PSMA 60.5% positivity metastatic castration-res…
9 results

Web Search·PSMA loss neuroendocrine prostate cancer AR-null double-nega…
8 results

Web Search·STEAP1 expression neuroendocrine prostate cancer loss AR sig…
9 results

Web Search·double-negative prostate cancer prevalence Bluemn 2017 AR-nu…
10 results

Web Search·177Lu-PSMA-617 VISION TheraP PSMA PET negative screen failur…
7 results

Web Search·PSCA prostate stem cell antigen expression bone metastasis c…
9 results

Web Search·DLL3 neuroendocrine prostate cancer target expression tarlat…
6 results

Checking helper signatures
3 lines of output

Looking up DOIs for candidate citations
16 lines of output
OpenAlex full-text matching is noisy; let me verify the specific DOIs directly, using the ones exposed in the web results plus known landmark DOIs.


Verifying landmark DOIs via CrossRef
30 lines of output
All ten verified. Now the remaining ones I still need DOIs for.


Resolving remaining DOIs via CrossRef
8 lines of output
Two matched to wrong records (an AACR abstract and a trial registration). Let me resolve the correct DOIs for the STEAP1/ADT Mol Cancer Res paper, the PSCA-CAR Nat Med trial, and the JNM screen-fail paper.


Verifying corrected DOIs
3 lines of output
Two still wrong. Let me find the correct DOIs precisely.


Ran 5 commands
5 steps

Searching OpenAlex for two remaining papers
8 lines of output

Querying CrossRef bibliographic for two papers
8 lines of output

Verifying JNM DOI and probing MCR DOI
4 lines of output

Resolving STEAP1 ADT DOI from PubMed
2 lines of output

Verifying STEAP1 ADT MCR DOI
1 line of output
All DOIs verified. Let me confirm the exact prevalence figures from the STEAP1 CAR-T paper and the TROP2/DLL3/CEACAM5 landscape before writing.


Fetched a page, ran a command
2 steps

Fetching STEAP1 CAR-T paper full text

Extracting prevalence figures from STEAP1 paper
25 lines of output
I have the exact figures. I have enough to write the synthesis. Let me draft the review and run the style pass.


Running style pass on the review draft
1 line of output
I need to fix author names I wasn't sure about, plus the style issues. Let me pull the actual author names.


Fetching first-author names for citations
10 lines of output
Several author names need correcting. Let me rewrite with the verified authors and fix the style issues.


Ran a command, saved artifacts
2 steps

Rewriting review and re-running style pass
{'ok': True, 'issues': []}

Saving prostate antigen review artifact
1 artifact
Prostate cancer surface-antigen expression is a readout of lineage state, not a fixed tumor property, and PSMA and STEAP1 are both AR-target antigens that rise and fall with the AR program. That single fact drives your entire result: the HuPSA finding — that a PSMA × STEAP1 AND gate covers AR+ adenocarcinoma but collapses toward zero in NEPCa/KRT7/progenitor-like and AR-null mCRPC — is well supported by the primary literature.

PSMA vs STEAP1 prevalence across metastatic sites
The figures you cite trace to matched immunohistochemistry on lethal mCRPC. Using an H-score cutoff of 30, Bhatia et al. 2023 (Nat Commun) found STEAP1 staining in 87.7% of evaluable mCRPC tissues (100/114) versus 60.5% (69/114) for PSMA, with the odds of any non-zero staining ~22-fold higher and of H-score ≥30 ~84-fold higher for STEAP1. Decisively for gate design, 28.1% of tissues (32/114) were STEAP1+/PSMA−, and only 0.9% (1/114) were the reverse. At the patient level, 95% (42/44) had STEAP1-expressing tumors versus 68% (30/44) for PSMA, and 23% of patients had no detectable PSMA at any site. STEAP1 was highest in bone (mean H-score ~193). Both antigens co-occurred in AR+/synaptophysin− adenocarcinoma — the AND gate's coverage is bounded above by the less-prevalent partner, PSMA.

Coordinated AR-lineage antigen loss
PSMA (FOLH1) is androgen-regulated and suppressed with neuroendocrine transdifferentiation (Bakht et al. 2019); the heterogeneity landscape (Bakht et al. 2023, Nat Cancer) placed PSMA in AR-active adenocarcinoma and markedly reduced it in AR-low/NE tumors, and RNA correlates agree (McKay et al. 2025). STEAP1 is broader but not lineage-independent — it is also AR-modulated (Bizzaro et al. 2025, Mol Cancer Res) and co-lost with PSMA in NE tumors. Double-negative (AR-null/NE-null) disease is a rising phenotype under potent AR inhibition (Bluemn et al. 2017; taxonomy in Labrecque et al. 2019), treatment-emergent small-cell NE arises in ~17% of AR-inhibitor-resistant mCRPC (Aggarwal et al. 2018), and ADT itself can induce a double-null state (Kim et al. 2024). These are exactly the states where both PSMA and STEAP1 vanish together — your near-zero AND-gate coverage.

Heterogeneity under therapy
Antigen loss is spatial and treatment-induced. PSMA radioligand therapy makes this operational: VISION (Sartor et al. 2021) and TheraP (Hofman et al. 2021) screened out PSMA-low/discordant patients, and screen-failure patients treated anyway did markedly worse (Hotta et al. 2022, JNM). Single-antigen PSMA agents already fail in the AR-null/NE tail — imaging selection exists because that tail isn't addressable.

What covers advanced disease better
The reciprocal antigens matter: DLL3 and CEACAM5 are enriched in NE/AR-low tumors while PSMA/STEAP1 fall (Ajkunic et al. 2024, npj Precision Oncology); DLL3 is the validated NEPC target (tarlatamab). PSCA rises with stage/bone metastasis (Lam et al. 2000) and, unlike PSMA/STEAP1, can persist with NE differentiation (Xiang et al. 2020); it is clinically actionable (Dorff et al. 2024, Nat Med).

Recommendation. Reserve the PSMA × STEAP1 AND gate for cases where on-target/off-tumor safety in confirmed AR+ adenocarcinoma is the binding constraint — it maximizes specificity but cannot cover advanced disease. For coverage, use OR-like logic and do not draw the antigen set from AR-lineage markers alone. A practical set: STEAP1 as the primary AR-lineage antigen (broadest coverage, retained better than PSMA under AR inhibition), in OR with DLL3 to capture the neuroendocrine tail, with PSCA and CEACAM5 as complements for AR-low/amphicrine and NE-differentiating tumors. Pair this with per-patient, ideally per-site, antigen assessment rather than a population-average assumption.

Full sourced synthesis with all DOIs inline: prostate_antigen_review.md.

GENERATED · 1




prostate_antigen
_review.md






## Follow-up / notes

_Does this change the nomination framing or suggest a better advanced-disease pair?_
