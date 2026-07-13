# CS06 — Key proteomics / surface-proteomics prostate datasets

- **Type:** literature search — text answer (Claude Science workbench)
- **Purpose:** Find protein-level resources to validate surface antigens and same-cell co-expression (what scRNA cannot settle).
- **Attach:** none — web literature only.

## Prompt

Compile the key publicly available proteomics and cell-surface-proteomics resources relevant to
validating prostate-cancer surface-antigen targets at the protein level. Cover:

- CPTAC prostate proteogenomics (Proteomic Data Commons);
- Human Protein Atlas (tissue IHC, subcellular localization, RNA, with its reliability categories);
- PaxDb protein abundance;
- cell-surface-capture (CSC) N-glycoproteomics and the Cell Surface Protein Atlas (CSPA);
- CIRFESS and the in-silico human surfaceome (SURFY, Bausch-Fluck et al. 2018);
- any mass-spec surfaceomics of prostate cancer cell lines or tissues.

For each resource give, with URLs: what it measures, its coverage/scale, access and format, license, and
specifically whether it can quantify (a) antigen surface density and (b) same-cell co-expression of two
antigens. Return a table, and a short paragraph on which resources could confirm a PSMA x STEAP1 pair at
the protein level and how.

## Results

I'll research the current details, URLs, and licensing for each resource, then compile the comparison table and the PSMA×STEAP1 assessment. Let me verify key facts. Let me verify SURFY/surfaceome, CIRFESS, and the CPTAC prostate study details. Now let me confirm the CPTAC prostate study details and a prostate cell-line surfaceomics reference. Let me verify the prostate proteogenomics data available via PDC, since CPTAC's core discovery cohorts didn't emphasize prostate. I have what I need. Let me compile the report.


Ran 6 searches, edited a file, saved artifacts
8 steps

Writing prostate surface-antigen resources report

Web Search·Cell Surface Protein Atlas CSPA Bausch-Fluck cell surface ca…
9 results

Web Search·SURFY in silico human surfaceome Bausch-Fluck 2018 PNAS 2886…
7 results

Web Search·CIRFESS compartmentalized protein database cell surface acce…
5 results

Web Search·CPTAC prostate cancer proteogenomics study Proteomic Data Co…
9 results

Web Search·cell surface capture surfaceome prostate cancer cell lines L…
6 results

Web Search·prostate cancer proteogenomics Proteomic Data Commons PDC st…
9 results

Saving prostate surfaceomics resources report
1 artifact
Compiled. The full report is saved as prostate_surface_antigen_proteomics_resources.md. Here's the summary.

Comparison table
Resource	What it measures	Coverage / scale	Access & format	License	(a) Surface density?	(b) Same-cell co-expression?
CPTAC prostate proteogenomics — Proteomic Data Commons (pdc.cancer.gov)	Deep TMT LC-MS/MS whole-proteome + phosphoproteome of tumor tissue, harmonized with matched genomics/transcriptomics	Patient tumor cohorts (CPTAC/ICPC/APOLLO); reprocessed via the CPTAC Common Data Analysis Pipeline	Web portal + API + AWS; .raw, PSM/peptide/protein reports, harmonized matrices	Open (NIH public data)	Partial — relative whole-cell abundance, not surface-specific	No — bulk tissue lysate
Human Protein Atlas (proteinatlas.org)	Tissue IHC, subcellular localization (IF), bulk & single-cell RNA, cancer pathology	~all protein-coding genes; normal + cancer incl. prostate; per-annotation reliability tier	Browser + TSV/XML/JSON + images	CC BY-SA 3.0	Partial — semi-quant staining intensity + % stained cells, spatially resolved	Partial only in principle — standard sections single-marker; dual/multiplex IHC not routine output
PaxDb (pax-db.org)	Integrated whole-cell protein abundance (ppm) from many public MS datasets	Proteome-wide; human whole-organism + tissue incl. prostate	Browser + flat files (protein→ppm)	Free academic; underlying data public	Partial — relative whole-cell ppm, not surface-specific	No — population average
CSC N-glycoproteomics / CSPA (wlab.ethz.ch/CSPA)	MS ID + relative quant of N-glyco surface proteins via hydrazide capture	41 human + 31 mouse cell types → 1,492 human surface glycoproteins	DB + data matrix; raw = PRIDE PXD000589	Academic/open (CC BY article)	Partial — relative surface abundance; confirms surface localization directly	No — bulk population capture
CIRFESS (cellsurfer.net/cirfess)	In-silico integration of surface prediction/annotation → surface-consensus score + MS-detectable peptides	Whole human proteome	Web app; query + export	Free web resource	No — prediction only	No — no expression data
SURFY surfaceome (wlab.ethz.ch/surfaceome)	Random-forest prediction of plasma-membrane residence from 131 features	2,886 predicted surface proteins, ~93.5% accuracy	PNAS suppl. (Dataset S3) + viewer; PMID 30373828	Open (PNAS)	No — scored prediction, not abundance	No
Prostate cell-line/tissue surfaceomics (Lee et al., PNAS 2018) (pnas.org)	Cell-surface biotinylation + LC-MS/MS of prostate cancer line panel; validated by immunoblot/IHC/flow	PrAd + NEPC lines/xenografts; 1,080 proteins (~46% PM); FOLH1/STEAP1/NCAM1 quantified	Paper + suppl.; raw MS in public repos	Open-access article	Partial — relative per-line surface abundance; embedded flow gives per-cell staining	Partial — bulk MS is averaged, but co-stained flow can measure two markers per cell
Confirming a PSMA (FOLH1) × STEAP1 pair at the protein level
No single public repository proves the two antigens sit on the same cell, but a tiered strategy works. First, SURFY and CIRFESS both classify FOLH1 and STEAP1 as bona fide plasma-membrane/surface proteins — <cite index="11-6">SURFY predicted a human surfaceome of 2,886 proteins with an accuracy of 93.5%</cite>, and <cite index="17-6,17-7,17-8">CIRFESS integrates prediction strategies and annotations into a single online resource to reveal the cell surface proteome theoretically detectable by current approaches (www.cellsurfer.net/cirfess)</cite> — the accessibility sanity check before pursuing abundance. Next, the Lee et al. prostate surfaceomics study provides the most direct evidence: <cite index="32-1,32-2,32-3">they profiled prostate cancer cell-line surfaceomes by labeling extracellular domains with membrane-impermeable biotin, streptavidin enrichment, and quantitative MS, identifying 1,080 proteins, 45.6% annotated for plasma-membrane localization</cite>, and <cite index="33-6">compared expression of known markers including FOLH1 (PSMA), STEAP1, and NCAM1</cite>, with <cite index="33-12,33-13,33-14">the PrAd-specific expression of STEAP1, FXYD3, and FOLH1 validated by immunoblot and immunohistochemistry of prostate cancer cell lines and xenografts</cite>. CSPA supplies orthogonal surface-glycoprotein confirmation in reference cell types — <cite index="6-5">the Cell Surface Capture technology applied to 41 human and 31 mouse cell types generated a mass-spectrometry-derived Cell Surface Protein Atlas providing surfaceome snapshots at high resolution</cite>. HPA then cross-checks membranous staining and reliability tier in prostate tumor tissue, and CPTAC/PDC plus PaxDb confirm both proteins are expressed and place their abundance on proteome-wide scales.

The gap: for (a) absolute surface density (copies/cell), MS and IHC give relative/semi-quant signals, not molecules per cell — that needs calibrated quantitative flow. For (b) same-cell co-expression, every bulk resource averages over the population and cannot distinguish separate single-positive cells from true double-positives. The only listed resource with single-cell capability is the flow cytometry in the prostate surfaceomics study; dual-color flow (or CyTOF / multiplex IF / imaging mass cytometry) co-staining PSMA and STEAP1 is the definitive protein-level confirmation of co-expression and, with bead calibration, of per-cell surface density. The databases nominate and prioritize the pair; a targeted co-staining experiment closes it.

One reliability note for the HPA calls: tiers run Enhanced → Supported → Approved → Uncertain — check the tier before trusting an antigen's staining annotation.

GENERATED · 1




prostate_surface_antigen_proteomics_re
sources.md





Reviewer
1 finding
The PMID wasn't confirmed in-window — let me verify it rather than leave a possibly-wrong identifier.


Ran 2 commands
2 steps · 1 failed

Verifying SURFY PNAS PMID via NCBI
exit 3

Verifying SURFY PMID via NCBI eutils
['30373828']
Confirmed via NCBI eutils: DOI 10.1073/pnas.1808790115 → PMID 30373828. The identifier in the report is correct; no fix needed.


## Follow-up / notes

_Which protein resource is the realistic next validation step._
