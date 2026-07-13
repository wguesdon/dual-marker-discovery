# CS03 — Approved and clinical dual-target / logic-gated prostate therapies

- **Type:** literature search — text answer (Claude Science workbench)
- **Purpose:** Map the clinical landscape our nominated pair sits in, and delimit novelty (own that the pair is not new).
- **Attach:** none — web literature only.

## Prompt

List the approved and clinical-stage combinatorial, dual-target, or logic-gated therapies relevant to
prostate-cancer cell-surface antigens. For each entry give: the antigen(s), modality (CAR-T, T-cell
engager, bispecific, ADC, radioligand, logic-gated CAR), the logic (AND / OR / NOT / single-target),
sponsor, phase, NCT or trial identifier, and the latest reported status or efficacy.

Include at least:

- PSMA (FOLH1) x PSCA split-signal / balanced-signalling CAR (Kloss et al. 2013, preclinical benchmark);
- PSMA x CD70 logic-gated CAR (NCT05437341);
- STEAP1 x CD3 T-cell engager (xaluritamig / AMG 509, NCT04221542);
- ABBV-969, dual PSMA/STEAP1 ADC (NCT06318273);
- PSMA-directed CARs, engagers, and radioligands broadly;
- A2 Bio Tmod HLA-LOH NOT-gates (note: not prostate).

For each, state explicitly whether it is a true AND gate, an OR-like dual-target agent, or single-target.
Return a table with citations/URLs, and a two-line summary of where a PSMA x STEAP1 **AND** gate would and
would not be differentiated from what already exists.

## Results

Ran 11 searches, ran 2 commands, saved artifacts
14 steps
Combinatorial, Dual-Target & Logic-Gated Therapies Against Prostate-Cancer Cell-Surface Antigens
Below is the compiled landscape, distinguishing true AND-gate logic (activation requires co-engagement of two antigens, with a mechanism that spares single-antigen-positive cells), OR-like dual-target agents (bind/kill via either antigen, broadening coverage but not adding a specificity gate), and single-target programs (included for context on PSMA/STEAP1 breadth).

Program	Antigen(s)	Modality	Logic	Sponsor	Phase	Identifier	Latest status/efficacy
Kloss et al. 2013 PSMA×PSCA "balanced signaling" CAR	PSMA (low-affinity CAR) + PSCA (chimeric costimulatory receptor, CCR)	CAR-T (dual-receptor, preclinical)	True AND gate	MSKCC (Sadelain lab)	Preclinical	Nat Biotechnol 2013;31:71-75	Foundational benchmark: T cells transduced with both a CAR providing suboptimal activation upon binding one antigen and a CCR recognizing a second antigen destroy tumors expressing both PSMA and PSCA but spare tumors expressing either antigen alone. Never directly commercialized as designed, but is the conceptual ancestor of today's logic-gated CAR trials.
PSMA/CD70 bi-specific CAR-T (bi-4SCAR-PSMA/CD70)	PSMA + CD70	CAR-T (single construct, bispecific)	Framed as "logic-gated"; publicly described as dual-antigen recognition for antigen-escape coverage rather than a confirmed Kloss-style split AND gate	Shenzhen Geno-Immune Medical Institute	Phase 1/2, recruiting	NCT05437341	T cells are modified to express a 4th-generation lentiviral anti-PSMA/CD70 bi-specific CAR that recognizes either CD70 or PSMA. A 2026 review calls it "the first logic-gated bispecific CAR-T for mCRPC to enter clinical testing", describing the rationale as "dual-targeting strategy against antigen escape; CD70 co-engagement may also provide intrinsic co-stimulation" — with no published results to date as of this review.
Xaluritamig (AMG 509)	STEAP1 × CD3	T-cell engager (XmAb 2+1 bispecific)	Single tumor-antigen × CD3 (avidity-tuned 2+1 format — not a dual-tumor-antigen gate)	Amgen	Ph1 dose exploration complete → Ph3 (XALute) ongoing	NCT04221542 (Ph1); NCT06691984 (Ph3 XALute)	Xaluritamig is a STEAP1-targeted T-cell engager designed to facilitate lysis of STEAP1-expressing prostate cancer cells. In the Ph1 dose-exploration cohort of 97 patients, it was tolerable with low-grade CRS occurring primarily in cycle 1, with encouraging preliminary efficacy in heavily pretreated mCRPC patients. Phase 3 XALute is comparing it against cabazitaxel or a second ARPI in post-taxane mCRPC.
ABBV-969	PSMA + STEAP1	Antibody-drug conjugate (dual-variable-domain IgG1, topoisomerase-1 inhibitor payload)	OR-like dual-target — a dual-variable domain immunoglobulin capable of binding cells expressing PSMA and/or STEAP1, for broader tumor targeting across heterogeneous disease, not an AND gate	AbbVie	Phase 1 (dose escalation complete, optimization ongoing)	NCT06318273	ASCO 2026: confirmed ORR of 45% among 29 RECIST-evaluable patients, with 67% PSA50 and 28% PSA90 responses at active dose levels; median rPFS ~15 months versus a typical 3–6 months in this population, in a population where over 80% had received docetaxel and more than half had prior lutetium.
P-PSMA-101	PSMA	CAR-T (non-viral piggyBac, TSCM-enriched, iCasp9 safety switch)	Single-target	Poseida Therapeutics	Phase 1	NCT04249947	Reported PSA50 responses and durable (>12 mo) remissions in a subset of 33 treated mCRPC patients; manageable but non-trivial CRS.
PSMA-TGFβdn armored CAR-T	PSMA	CAR-T (armored, dominant-negative TGFβ receptor)	Single-target	MSKCC	Phase 1	NCT03089203	Feasibility/safety endpoints met across 4 dose levels; dose-dependent expansion and toxicity, transient antitumor activity.
Acapatamab (AMG 160)	PSMA × CD3	T-cell engager (half-life-extended BiTE)	Single tumor-antigen × CD3	Amgen	Phase 1 (discontinued)	NCT04671186 (+related)	Modest activity (ORR 7.4%, PSA50 30.4%) with high rates of CRS (~95–98%) and anti-drug antibodies; program discontinued.
Pasotuxizumab (AMG 212/BAY 2010112)	PSMA × CD3	T-cell engager (canonical continuous-IV BiTE)	Single tumor-antigen × CD3	Amgen/Bayer	Phase 1 (terminated)	NCT01723475	First-in-human PSMA BiTE; meaningful PSA declines but high-grade toxicity; superseded by acapatamab.
HPN424	PSMA × CD3 × albumin (tri-specific)	T-cell engager (TriTAC)	Single tumor-antigen × CD3 (albumin arm is PK only)	Harpoon Therapeutics	Phase 1/2a	NCT03577028	Manageable, transient AEs; PSA declines and CTC reductions in a subset; no registrational data.
JNJ-63898081	PSMA × CD3	T-cell engager	Single tumor-antigen × CD3	Janssen	Phase 1 (discontinued)	NCT03926013	Preliminary safety/activity reported; not advanced.
177Lu-PSMA-617 (Pluvicto)	PSMA	Radioligand therapy (177Lu beta-emitter)	Single-target	Novartis	FDA-approved	NCT03511664 (VISION); NCT04689828 (PSMAfore)	FDA expanded approval on March 28, 2025 for PSMA-positive mCRPC, including patients who have not yet received chemotherapy, building on the original March 2022 post-ARPI/taxane approval.
225Ac-PSMA-617	PSMA	Radioligand therapy (225Ac alpha-emitter)	Single-target	Academic/multiple sponsors (investigational)	Early-phase / neoadjuvant comparative studies	e.g. NCT07054346	Investigational alpha-emitter variant being compared head-to-head with the beta-emitter form; not approved.
A2 Bio Tmod™ platform (not prostate)	Activator (EGFR/CEA/MSLN) + inhibitory anti-HLA-A*02 receptor	Logic-gated allogeneic/autologous CAR-T	True AND-NOT combinatorial gate: dual receptors toward HLA-A*02 and a target such as CEA or mesothelin cause the cells to target cancer cells with HLA loss of heterozygosity while sparing healthy, HLA-expressing tissue	A2 Biotherapeutics	Phase 1/2 (multiple arms)	A2B530: NCT05736731 (EVEREST-1); A2B694/A2B543: NCT06051695 (EVEREST-2); screening: NCT04981119 (BASECAMP-1)	Indications are CRC, NSCLC, pancreatic, ovarian, mesothelioma and other EGFR/CEA/MSLN-expressing solid tumors with HLA-A*02 LOH — included only as the reference NOT-gate architecture, not a prostate program.
Two-line summary: where would a PSMA × STEAP1 AND gate differentiate?
A true AND gate would mainly differentiate on specificity/toxicity, not novelty of target pairing — ABBV-969 already validates PSMA+STEAP1 as a biologically sound pair by exploiting it as an OR-like ADC, and xaluritamig has established STEAP1 as clinically tractable via CD3 engagement, so a combinatorial CAR/engager would need to demonstrate reduced on-target/off-tumor toxicity or lower CRS versus single-antigen STEAP1/PSMA engagers to earn its added engineering complexity. It would not be differentiated on antigen novelty or on broadening tumor coverage (ABBV-969's OR-logic already solves the heterogeneity/antigen-escape problem that motivates most dual-PSMA/STEAP1 combination rationale) — the AND gate's unique value proposition is narrower: sparing normal tissue that expresses one antigen alone, a benefit only relevant if single-antigen normal-tissue toxicity (e.g., PSMA expression in salivary gland/kidney) is dose-limiting for the OR/single-target agents in practice.

Note on efficacy figures: minor rounding differences exist across ABBV-969 press materials (PSA50 reported as both 67% and 67.4% across sources); the table uses the AbbVie/ASCO 2026 press-release figures.

prostate_combinatorial_therapies.csv — full structured table (13 rows) with all fields.
prostate_combinatorial_therapies.md — markdown version of the same table.
GENERATED · 2


prostate_combinatorial_th
erapies.md


prostate_combinatorial_th
erapies.csv





Reviewer
1 finding
Confirmed — NCT07054346 (UCSF LUTACT trial, 225Ac-PSMA-617 vs 177Lu-PSMA-617 neoadjuvant comparison) is real, not a placeholder. Fixing the identifier field to drop the hedging "e.g." and cite it properly (a second real accession, NCT04597411, the AcTION Phase 1 study of 225Ac-PSMA-617, is also confirmed and more representative of the broader investigational program, so I'll list both).


Ran a command, ran a search, saved artifacts
3 steps

Fixing 225Ac-PSMA-617 identifier field in therapy table
2 lines of output

Web Search·NCT07054346 225Ac-PSMA-617 UCSF trial
9 results

Saving corrected therapy landscape table with verified 225Ac-PSMA-617 identifiers
2 artifacts
Fixed: the 225Ac-PSMA-617 row now cites two verified accessions — NCT04597411 (AcTION, Endocyte/Novartis Phase 1) and NCT07054346 (LUTACT, UCSF neoadjuvant comparative pilot) — replacing the unverified "e.g." placeholder, in both prostate_combinatorial_therapies.csv and prostate_combinatorial_therapies.md.

GENERATED · 2


prostate_combinatorial_th
erapies.md


prostate_combinatorial_th
erapies.csv





Reviewer
1 finding
Rebuttal: those specifics are directly confirmed by my own search results already in context — NCT04597411's title states it's the "AcTION" Phase I study of 225Ac-PSMA-617 "With or Without Prior 177Lu-PSMA-617", sponsor Endocyte/Novartis, status ACTIVE_NOT_RECRUITING; NCT07054346's page confirms "LUTACT Trial" and its neoadjuvant/prostatectomy design. I'll tighten one unsupported word ("dose-finding" wasn't stated) for precision.


Ran 2 commands, saved artifacts
3 steps

Tightening 225Ac-PSMA-617 status text to match confirmed source wording
1 line of output

Cleaning up status wording phrasing
ok

Saving final corrected therapy landscape table
2 artifacts
Wording tightened to match confirmed source detail exactly ("dose-finding" removed, "active, not recruiting" per trial status). Updated: prostate_combinatorial_therapies.csv / prostate_combinatorial_therapies.md.
## Follow-up / notes

_Novelty framing for the report; any competitor we should cite._
