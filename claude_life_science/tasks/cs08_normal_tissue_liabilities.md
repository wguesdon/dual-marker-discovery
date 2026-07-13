# CS08 — Normal-tissue expression liabilities of candidate antigens

- **Type:** literature search — text answer (Claude Science workbench)
- **Purpose:** Build the safety-side literature that scRNA co-detection only approximates.
- **Attach:** none — web literature only.

## Prompt

For the candidate prostate surface antigens FOLH1/PSMA, STEAP1, STEAP2, PSCA, HPN/hepsin, TMPRSS2,
TACSTD2/TROP2, CD276/B7-H3, EPCAM, and DLL3, summarize the normal-tissue expression that drives
on-target off-tumor risk. Use GTEx, the Human Protein Atlas (RNA and IHC, with reliability categories),
and primary literature.

For each antigen give, with citations (DOI/URL):

- which normal tissues and cell types express it, at the protein level where possible;
- the documented or expected clinical toxicity of targeting it;
- the concordance between HPA RNA and antibody staining — explicitly flag antigens where they disagree
  (for example HPN, where RNA/protein concordance is reported to be weak);
- whether expression is apical vs basolateral / accessible from the vasculature, if known.

Return a table with a per-antigen risk note, and highlight any antigen whose real protein-level normal
expression would materially change its safety ranking relative to a transcript co-detection estimate.

## Results

_Paste the Claude Science answer here (keep the sources/citations)._

## Follow-up / notes

_Antigens where protein evidence should override the transcript liability; report caveats._
