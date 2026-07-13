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

I'll start by scoping the data sources available for this task — the GTEx connector, Human Protein Atlas access, and the literature graph — before laying out a plan.


Ran 2 searches, loaded a skill
3 steps

Finding Human Protein Atlas skill

Finding GTEx expression skill

Loading GTEx expression connector docs
loaded
Good — I have GTEx (mcp-expression) and there's a Human Protein Atlas method in mcp-protein-annotation. Let me inspect the HPA method signature.


Loading Protein Atlas connector docs
loaded
I have all three data sources confirmed: GTEx (mcp-expression), Human Protein Atlas RNA+IHC with reliability categories (mcp-protein-annotation → get_protein_atlas_gene), and the literature graph (mcp-literature) plus DOI full-text fetch. This is a substantial multi-antigen safety review, so let me lay out a plan for your approval.


Drafting antigen safety review plan
8 steps
Plan approved. Starting with GTEx normal-tissue expression.


Resolving genes and pulling GTEx medians
102 lines of output
All 10 resolved. Now fetching median TPM across all tissues.


Fetching GTEx median TPM all tissues
3 lines of output
540 rows = 10 genes × 54 tissues. Let me inspect the medians structure and build the tidy table.


Inspecting median rows structure
20 lines of output
Clean structure. Now let me build the tidy CSV in the python kernel.


Building tidy GTEx TPM table
21 lines of output
GTEx transcript profiles are in and already tell the safety story: FOLH1/PSMA high in brain and salivary gland; PSCA very high in stomach/bladder; HPN in liver/kidney; TACSTD2/TROP2 broad across skin, esophagus, salivary gland; EPCAM in GI/kidney/thyroid; DLL3 low everywhere (CNS-restricted). Let me save the GTEx artifacts and pull HPA.


Saving GTEx median TPM table
1 artifact
Now pulling HPA records for all 10 genes.


Ran 2 commands
2 steps

Fetching HPA records for 10 antigens
1 line of output

Inspecting HPA record sections
53 lines of output
Good — I have RNA specificity, protein tissue specificity, IHC reliability category, and subcellular location. Let me flatten across all 10 genes and check whether the summary captures enough IHC per-tissue detail or if I need the full record.


Ran 2 commands
2 steps · 1 failed

Flattening HPA fields across antigens
SyntaxError: '(' was never closed (<kernel:19>, line 5)

Flattening HPA fields across antigens
20 lines of output
Rich data. Let me capture the truncated fields (HPN reliability especially) and build the HPA summary CSV.


Checking HPN and remaining reliability fields
5 lines of output
All HPA reliability categories captured. Let me build the HPA summary CSV.


Ran a command, saved artifacts, loaded a skill
3 steps

Writing HPA summary CSV
11 lines of output

Saving HPA summary and raw records
2 artifacts

Loading figure-style skill
loaded
Now the heatmap. I'll log-scale the median TPM, cluster tissues, and annotate cells so the safety-relevant tissues are readable.


Building GTEx median-TPM heatmap
1 figure · saved (10, 54)
gtex_tpm_heatmap.png
gtex_tpm_heatmap.png
The heatmap reads well — tissues ordered by peak signal surface the safety-relevant sites on the left (esophagus, stomach, skin, salivary gland, liver, kidney, GI). Saving it.


Saving GTEx heatmap figure
1 artifact
Now I'll build the concordance assessment, comparing RNA distribution (GTEx + HPA) against HPA IHC protein staining and its reliability category, flagging disagreements.


Building RNA-vs-IHC concordance table
11 lines of output
Concordance table built. Now for the literature step — I need primary sources for clinical toxicity and apical/basolateral polarity. Let me search OpenAlex for the key targeted therapies and localization papers.


Ran a search, loaded a skill
2 steps

Finding OpenAlex literature methods

Loading OpenAlex search method docs
loaded
Let me get the actual openalex_search_works signature.


Loading OpenAlex works search signature
loaded
The connector handles OpenAlex auth server-side. Let me run targeted literature searches for the clinically-relevant toxicity and polarity topics across the 10 antigens.


Searching literature for toxicity and polarity
69 lines of output
GENERATED · 4

gtex_tpm_heatmap.png
gtex_tpm_
heatmap.png


gtex_med
ian_tpm.csv


hpa_
summary.csv


hpa_
records.json

## Follow-up / notes

_Antigens where protein evidence should override the transcript liability; report caveats._
