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

A note on two axes where my confidence is lower without full-text of the 2025 papers: SCAN-ACT and LogiCAR uncertainty handling is characterized from abstracts/summaries — if you want those two nailed down I can pull their full methods. The MadHitter first-author attribution I left at lab level rather than guess a name.

State of the art vs a curated-panel, per-patient Boolean scan
A curated-panel per-patient Boolean scan (fixed antigen list, count double-positive cells per patient) is transparent and clinically legible, but the field has moved past it on four fronts. Search vs enumeration: where a Boolean scan enumerates a hand-picked panel, Dannenfelser/Lim screen millions of dual and tens of millions of triple gates genome-wide, and LogiCAR evolves up to 5-gene circuits via genetic algorithm through a space too large to enumerate. Formal optimization: MadHitter casts the problem as an integer-programming minimum hitting set — the smallest antigen set covering nearly every malignant cell while sparing normals — yielding provably optimal combinations and handling antigen escape directly, which a co-occurrence count cannot. Full logic on single cells: Kwon, SCAN-ACT and LogiCAR score NOT/OR alongside AND against normal single-cell atlases, so off-tumor risk is measured cell-by-cell in real normal tissue. Protein grounding + uncertainty: Perna integrated large transcriptomics and proteomics datasets and developed an algorithm for LSC-restricted targets so hits are surface-confirmed, and MadHitter/LogiCAR quantify robustness via down-sampling and ranked alternatives.

Two realistic adoptions:

Add a formal coverage objective (MadHitter-style ILP or a greedy hitting set) on top of your per-patient double-positive counts — turning "which pairs co-occur" into "smallest panel subset covering the most tumor cells while sparing normals," which also extends to triples without enumeration.
Add per-patient bootstrap CIs — resample cells within each patient to put a confidence interval on each pair's double-positive fraction, so a 55%-with-wide-CI pair doesn't outrank a tight 45% pair. Cheap to bolt on and closes the uncertainty gap directly.
Artifacts:

andgate_target_methods_comparison.csv — full comparison table (all 8 axes, wrapped text)
andgate_target_methods_survey.md — narrative survey + table + state-of-the-art paragraph
Want me to pull full methods text for SCAN-ACT and LogiCAR to firm up their uncertainty/protein axes, or add any adjacent methods (e.g., Perna's TCLP/other AML-surfaceome or pan-cancer engager-target screens)?

GENERATED · 2


andgate_target_methods
_survey.md


andgate_target_methods_com
parison.csv





Reviewer
1 finding
Rebuttal: all three DOIs are backed by in-window tool output — the persisted web_search results contain the resolving URLs verbatim: Kwon nature.com/articles/s41587-023-01686-y, LogiCAR biorxiv.org/content/10.1101/2025.03.19.644074, and SCAN-ACT link.springer.com/article/10.1186/s13073-025-01514-9 (springer path = DOI). No fabrication; the identifiers trace to returned search hits.





Reviewer
1 finding
Acknowledged — I'll settle it with fresh tool output rather than argue provenance.


Ran 3 searches
3 steps

Web Search·Kwon single-cell mapping combinatorial target antigens CAR s…
7 results

Web Search·SCAN-ACT adoptive T cell therapy target discovery single-cel…
7 results

Web Search·LogiCAR single-cell-guided logic-gated antigen combinations …
5 results
Confirmed with fresh searches — the three DOIs resolve correctly: Kwon Nat Biotechnol (2023), doi: 10.1038/s41587-023-01686-y; SCAN-ACT DOI: 10.1186/s13073-025-01514-9; LogiCAR 2025 Mar 19:2025.03.19.644074. doi: 10.1101/2025.03.19.644074. The finding is rebutted, but the searches also surfaced better evidence on two axes I'd under-called, so I'll correct the artifacts.


Ran 2 commands, saved artifacts
3 steps

Updating SCAN-ACT and Kwon rows with verified detail
2 lines of output

Regenerating and saving updated report
rewritten 7771

Saving updated comparison table and report
2 artifacts
All three DOIs are now confirmed against fresh publisher/PubMed output, and the searches let me tighten two axes I had under-called. Summary of what changed:

DOIs verified (fresh tool output this turn):

Kwon et al. 2023 — 10x Genomics reference list gives "doi: 10.1038/s41587-023-01686-y"; KAIST repository confirms Nat Biotechnol v.41, no.11, pp.1593–1605, 2023.
SCAN-ACT (Testa et al. 2025) — PMC record header: DOI 10.1186/s13073-025-01514-9, published 2025-08-14, Genome Medicine 17:89.
LogiCAR designer (Madan et al. 2025) — PubMed: "2025 Mar 19:2025.03.19.644074. doi: 10.1101/2025.03.19.644074."
Corrections made to both artifacts (v2):

SCAN-ACT — upgraded from RNA-only to protein-integrating: it validates selected targets with IHC and proteomics and uses FDR-aware single-cell DGE, with human-tested targets as reference benchmarks. Also confirmed its scale (986,749 STS single cells → 395 monospecific + 14,192 bispecific CAR-T targets) and that its largest surface-target order is pairs (bispecific Boolean gates).
Kwon — refined the algorithm to the actual two-step design (random forest ranks surface antigens → CNN classifier scores gene pairs, evaluating AND/OR/NOT), on a ~1.4M-cell atlas (412 tumors + 12 normal organs); largest order remains pairs.
State-of-the-art paragraph — added SCAN-ACT's IHC/proteomics validation and FDR-aware DGE to the "protein grounding and uncertainty" front.
One incidental confirmation worth noting: the LogiCAR text itself situates the prior art the way the table does — it credits Kwon with circuits "of up to two targets" and MadHitter with OR-gated minimum-target-set selection, and positions its own contribution as scaling to five-gene circuits. That independently corroborates the combination-order column.

Updated artifacts:

andgate_target_methods_comparison.csv — comparison table, v2 with verified DOIs and corrected SCAN-ACT/Kwon rows
andgate_target_methods_survey.md — narrative survey, v2

## Follow-up / notes

_Methods worth adopting, disagreements, or what should change in `docs/research_plan.md`._
