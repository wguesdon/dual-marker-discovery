"""CS03 — Approved and clinical dual-target / logic-gated prostate therapies

Verbatim Claude Science kernel code, reconstructed from the workbench execution log. This is a
**provenance record of how the committed artifacts were produced**, not a pipeline script.

It does not run outside the Claude Science workbench. Two dependencies are injected by the workbench
and are not importable here:

- ``host.mcp(server, method, **kwargs)`` — the connector bridge (GTEx, Human Protein Atlas, OpenAlex).
- ``apply_figure_style()`` — supplied by the workbench ``figure-style`` skill.

Cells run in one shared kernel, so later cells depend on names bound by earlier ones. Cells are
reproduced in execution order with their original index. Cells that errored and were retried are
omitted; the retry that succeeded is kept.

Outputs (relative to the workbench working directory):
  - prostate_combinatorial_therapies.csv
  - prostate_combinatorial_therapies.md
"""

# ruff: noqa
# fmt: off

# %% cell 0  ->  prostate_combinatorial_therapies.csv
import pandas as pd

rows = [
dict(Program="Kloss et al. 2013 PSMA×PSCA split-signal (\"balanced signaling\") CAR",
     Antigens="PSMA (activation, low-affinity CAR) + PSCA (costimulation, CCR)",
     Modality="CAR-T (dual-receptor: CAR + chimeric costimulatory receptor)",
     Logic="True AND gate (preclinical prototype)",
     Sponsor="Memorial Sloan Kettering (Sadelain lab)",
     Phase="Preclinical (mouse xenograft)",
     Identifier="Nat Biotechnol 2013;31:71-75 (no NCT)",
     Status_Efficacy="Benchmark paper establishing split-signal logic gating; co-transduced T cells eradicated PSMA+PSCA+ tumors but spared single-antigen-positive tumors in NSG mice. Never clinically translated as designed; conceptual basis for later logic-gated CAR trials."),

dict(Program="PSMA/CD70 bispecific \"logic-gated\" CAR-T (bi-4SCAR PSMA/CD70)",
     Antigens="PSMA + CD70",
     Modality="CAR-T (bispecific/dual CAR construct)",
     Logic="Marketed as logic-gated / AND-like dual-antigen CAR; public trial record does not confirm a Kloss-style split-signal (CAR+CCR) architecture — construct co-expresses both specificities in one product, so functionally it may behave more OR-like unless a true split design is used",
     Sponsor="Shenzhen Geno-Immune Medical Institute (investigator-initiated)",
     Phase="Phase 1/2 (recruiting)",
     Identifier="NCT05437341",
     Status_Efficacy="Described in reviews as the first logic-gated bispecific CAR-T for mCRPC to enter clinical testing; recruiting, no efficacy data publicly reported as of mid-2026."),

dict(Program="Xaluritamig (AMG 509)",
     Antigens="STEAP1 (tumor) × CD3 (T cell)",
     Modality="T-cell engager (XmAb 2+1 bispecific)",
     Logic="Single tumor-antigen × CD3 engager (avidity-based 2+1 format, not a dual-tumor-antigen AND gate)",
     Sponsor="Amgen",
     Phase="Phase 1 completed dose exploration → Phase 3 (XALute) ongoing",
     Identifier="NCT04221542 (Ph1); NCT06691984 (Ph3 XALute)",
     Status_Efficacy="Ph1: manageable safety, encouraging efficacy in heavily pretreated mCRPC (41% ORR in high-dose cohort). Ph3 XALute (~675 pts, xaluritamig vs cabazitaxel/2nd ARDT, OS primary endpoint) actively enrolling as of 2026."),

dict(Program="ABBV-969",
     Antigens="PSMA + STEAP1",
     Modality="Antibody-drug conjugate (dual-variable-domain IgG1, topoisomerase-1 inhibitor payload)",
     Logic="OR-like dual-target agent — binds and is cytotoxic to cells expressing either or both antigens, explicitly intended to broaden tumor coverage vs single-antigen ADCs, not an AND gate",
     Sponsor="AbbVie",
     Phase="Phase 1 (dose escalation complete, dose optimization ongoing)",
     Identifier="NCT06318273",
     Status_Efficacy="ASCO 2026: 45% confirmed ORR (29 RECIST-evaluable pts), 67% PSA50, 28% PSA90 at active doses in heavily pretreated mCRPC; manageable safety profile."),

dict(Program="P-PSMA-101",
     Antigens="PSMA",
     Modality="CAR-T (autologous, piggyBac non-viral, TSCM-enriched, iCasp9 safety switch)",
     Logic="Single-target",
     Sponsor="Poseida Therapeutics",
     Phase="Phase 1",
     Identifier="NCT04249947",
     Status_Efficacy="Clin Cancer Res 2026: 33 pts treated; PSA50 in 21% (7/33); 1 PR among 13 RECIST-evaluable; durable (>12 mo) remissions in 2 pts; CRS 61% (grade≥3 9%); DLTs in 18%."),

dict(Program="PSMA-TGFβdn armored CAR-T",
     Antigens="PSMA",
     Modality="CAR-T (autologous, armored with dominant-negative TGF-β receptor)",
     Logic="Single-target",
     Sponsor="Memorial Sloan Kettering / academic",
     Phase="Phase 1",
     Identifier="NCT03089203",
     Status_Efficacy="Nat Med 2022: 18 enrolled/13 treated across 4 dose levels; grade≥2 CRS in 5/13, transient antitumor activity, dose-dependent toxicity/expansion; all prespecified safety/feasibility endpoints met."),

dict(Program="Acapatamab (AMG 160)",
     Antigens="PSMA × CD3",
     Modality="T-cell engager (half-life-extended BiTE)",
     Logic="Single tumor-antigen × CD3",
     Sponsor="Amgen",
     Phase="Phase 1 (discontinued)",
     Identifier="NCT04671186 / related program (n=133 pooled dose-exploration+expansion)",
     Status_Efficacy="Discontinued after Phase 1: ORR 7.4%, PSA50 30.4%, rPFS 3.7 months, CRS in ~95-98% of patients (~20% grade≥3), 55% developed ADAs reducing exposure."),

dict(Program="Pasotuxizumab (AMG 212/BAY 2010112)",
     Antigens="PSMA × CD3",
     Modality="T-cell engager (canonical BiTE, continuous IV)",
     Logic="Single tumor-antigen × CD3",
     Sponsor="Amgen/Bayer",
     Phase="Phase 1 (terminated)",
     Identifier="NCT01723475",
     Status_Efficacy="First-in-human BiTE in prostate cancer; PSA reduction up to 54.9% in the highest-dose cohort but 81% grade 3/4 treatment-related AEs; program terminated in favor of acapatamab."),

dict(Program="HPN424",
     Antigens="PSMA × CD3 × albumin (tri-specific TriTAC)",
     Modality="T-cell engager (tri-specific small-format protein)",
     Logic="Single tumor-antigen × CD3 (albumin arm is for half-life, not tumor targeting)",
     Sponsor="Harpoon Therapeutics (partnered with AbbVie/Merck historically)",
     Phase="Phase 1/2a",
     Identifier="NCT03577028",
     Status_Efficacy="Dose escalation showed manageable, transient AEs, dose-proportional PK, PSA declines and CTC reductions in a subset of heavily pretreated mCRPC patients; no registrational data reported."),

dict(Program="JNJ-63898081",
     Antigens="PSMA × CD3",
     Modality="T-cell engager (bispecific antibody)",
     Logic="Single tumor-antigen × CD3",
     Sponsor="Janssen (J&J)",
     Phase="Phase 1 (discontinued)",
     Identifier="NCT03926013",
     Status_Efficacy="Reported preliminary safety/activity; program not advanced further."),

dict(Program="177Lu-PSMA-617 (Pluvicto, vipivotide tetraxetan)",
     Antigens="PSMA",
     Modality="Radioligand therapy (beta-emitter, 177Lu)",
     Logic="Single-target",
     Sponsor="Novartis",
     Phase="FDA-approved (Phase 3 VISION-supported)",
     Identifier="NCT03511664 (VISION)",
     Status_Efficacy="First FDA-approved PSMA radioligand therapy (March 2022) for post-ARPI/taxane mCRPC; label expanded (March 2025) to pre-taxane, post-ARPI setting. VISION: HR 0.40 for imaging-based PFS vs SOC."),

dict(Program="225Ac-PSMA-617 (actinium-PSMA)",
     Antigens="PSMA",
     Modality="Radioligand therapy (alpha-emitter, 225Ac)",
     Logic="Single-target",
     Sponsor="Academic / multiple industry programs (investigational)",
     Phase="Investigational (Phase 1/2, e.g. neoadjuvant LUTACT-type comparative studies)",
     Identifier="e.g. NCT07054346",
     Status_Efficacy="Alpha-emitter hypothesized to be more potent than 177Lu-PSMA-617 per unit dose; being compared head-to-head in early-phase/neoadjuvant prostatectomy studies; not yet approved."),

dict(Program="A2 Bio Tmod™ CAR-T platform (HLA-LOH NOT-gate) — NOT prostate",
     Antigens="Activator: EGFR (A2B395), CEA (A2B530), MSLN (A2B694/A2B543) — each paired with an inhibitory HLA-A*02 receptor",
     Modality="Logic-gated (Boolean AND-NOT) allogeneic/autologous CAR-T",
     Logic="True combinatorial logic gate: activating CAR requires tumor antigen (AND) while an inhibitory receptor recognizing HLA-A*02 imposes a NOT-gate, sparing HLA-A*02-retaining normal tissue and killing only tumor cells with HLA-A*02 loss-of-heterozygosity (LOH)",
     Sponsor="A2 Biotherapeutics",
     Phase="Phase 1/2 (multiple arms)",
     Identifier="A2B395: NCT06682793; A2B530: NCT05736731; A2B694/A2B543 (EVEREST-2): NCT06051695; screening protocol BASECAMP-1: NCT04981119",
     Status_Efficacy="Indications are CRC, NSCLC, HNSCC, TNBC, RCC and other EGFR/CEA/MSLN-expressing solid tumors with HLA-A*02 LOH — NOT a prostate program; included here only as the reference NOT-gate architecture."),
]

df = pd.DataFrame(rows)
df.to_csv("prostate_combinatorial_therapies.csv", index=False)
print(df[["Program","Logic"]].to_string())
print(df.shape)

# %% cell 1  ->  prostate_combinatorial_therapies.md
md = []
md.append("# Combinatorial / Dual-Target / Logic-Gated Therapies for Prostate-Cancer Cell-Surface Antigens\n")
md.append("Compiled from ClinicalTrials.gov records, ASCO/AACR/Annals of Oncology abstracts, and peer-reviewed literature (see citations in accompanying chat response).\n")

header = "| Program | Antigen(s) | Modality | Logic | Sponsor | Phase | Identifier | Latest status / efficacy |\n"
sep    = "|---|---|---|---|---|---|---|---|\n"
md.append(header + sep)
for r in rows:
    line = f"| {r['Program']} | {r['Antigens']} | {r['Modality']} | {r['Logic']} | {r['Sponsor']} | {r['Phase']} | {r['Identifier']} | {r['Status_Efficacy']} |\n"
    md.append(line)

with open("prostate_combinatorial_therapies.md","w") as f:
    f.writelines(md)

print("".join(md)[:500])

# %% cell 2  ->  prostate_combinatorial_therapies.csv, prostate_combinatorial_therapies.md
import pandas as pd
df = pd.read_csv("prostate_combinatorial_therapies.csv")

mask = df["Program"] == "225Ac-PSMA-617 (actinium-PSMA)"
df.loc[mask, "Identifier"] = "NCT04597411 (AcTION Ph1, Endocyte/Novartis); NCT07054346 (LUTACT, UCSF neoadjuvant comparative)"
df.loc[mask, "Status_Efficacy"] = ("Alpha-emitter hypothesized to be more potent than 177Lu-PSMA-617 per unit dose. AcTION (NCT04597411) is an active Phase 1 dose-finding study "
    "in men with PSMA-positive prostate cancer with/without prior 177Lu-PSMA-617; LUTACT (NCT07054346) is a UCSF pilot neoadjuvant trial directly comparing "
    "177Lu-PSMA-617 vs 225Ac-PSMA-617 before prostatectomy. Not yet FDA-approved.")

df.to_csv("prostate_combinatorial_therapies.csv", index=False)

rows_dict = df.to_dict("records")
header = "| Program | Antigen(s) | Modality | Logic | Sponsor | Phase | Identifier | Latest status / efficacy |\n"
sep    = "|---|---|---|---|---|---|---|---|\n"
lines = ["# Combinatorial / Dual-Target / Logic-Gated Therapies for Prostate-Cancer Cell-Surface Antigens\n",
         "Compiled from ClinicalTrials.gov records, ASCO/AACR/Annals of Oncology abstracts, and peer-reviewed literature.\n",
         header, sep]
for r in rows_dict:
    lines.append(f"| {r['Program']} | {r['Antigens']} | {r['Modality']} | {r['Logic']} | {r['Sponsor']} | {r['Phase']} | {r['Identifier']} | {r['Status_Efficacy']} |\n")

with open("prostate_combinatorial_therapies.md","w") as f:
    f.writelines(lines)

print(df.loc[mask, ["Program","Identifier"]].to_string())

# %% cell 3  ->  prostate_combinatorial_therapies.csv, prostate_combinatorial_therapies.md
import pandas as pd
df = pd.read_csv("prostate_combinatorial_therapies.csv")

mask = df["Program"] == "225Ac-PSMA-617 (actinium-PSMA)"
df.loc[mask, "Status_Efficacy"] = (
    "Alpha-emitter hypothesized to be more potent than 177Lu-PSMA-617 per unit dose. AcTION (NCT04597411, sponsor Endocyte/Novartis) is an active, "
    "not-yet-recruiting-closed Phase 1 study of 225Ac-PSMA-617 in men with PSMA-positive prostate cancer with or without prior 177Lu-PSMA-617 therapy; "
    "LUTACT (NCT07054346, UCSF) is a single-center pilot study comparing 177Lu-PSMA-617 and 225Ac-PSMA-617 as neoadjuvant therapy before prostatectomy. "
    "Not yet FDA-approved."
)
df.to_csv("prostate_combinatorial_therapies.csv", index=False)

rows_dict = df.to_dict("records")
header = "| Program | Antigen(s) | Modality | Logic | Sponsor | Phase | Identifier | Latest status / efficacy |\n"
sep    = "|---|---|---|---|---|---|---|---|\n"
lines = ["# Combinatorial / Dual-Target / Logic-Gated Therapies for Prostate-Cancer Cell-Surface Antigens\n",
         "Compiled from ClinicalTrials.gov records, ASCO/AACR/Annals of Oncology abstracts, and peer-reviewed literature.\n",
         header, sep]
for r in rows_dict:
    lines.append(f"| {r['Program']} | {r['Antigens']} | {r['Modality']} | {r['Logic']} | {r['Sponsor']} | {r['Phase']} | {r['Identifier']} | {r['Status_Efficacy']} |\n")

with open("prostate_combinatorial_therapies.md","w") as f:
    f.writelines(lines)

print(df.loc[mask, "Status_Efficacy"].values[0])

# %% cell 4  ->  prostate_combinatorial_therapies.csv, prostate_combinatorial_therapies.md
import pandas as pd
df = pd.read_csv("prostate_combinatorial_therapies.csv")
mask = df["Program"] == "225Ac-PSMA-617 (actinium-PSMA)"
df.loc[mask, "Status_Efficacy"] = (
    "Alpha-emitter hypothesized to be more potent than 177Lu-PSMA-617 per unit dose. AcTION (NCT04597411, sponsor Endocyte/Novartis) is a Phase 1 study "
    "(active, not recruiting) of 225Ac-PSMA-617 in men with PSMA-positive prostate cancer with or without prior 177Lu-PSMA-617 therapy; "
    "LUTACT (NCT07054346, UCSF) is a single-center pilot study comparing 177Lu-PSMA-617 and 225Ac-PSMA-617 as neoadjuvant therapy before prostatectomy. "
    "Not yet FDA-approved."
)
df.to_csv("prostate_combinatorial_therapies.csv", index=False)

rows_dict = df.to_dict("records")
header = "| Program | Antigen(s) | Modality | Logic | Sponsor | Phase | Identifier | Latest status / efficacy |\n"
sep    = "|---|---|---|---|---|---|---|---|\n"
lines = ["# Combinatorial / Dual-Target / Logic-Gated Therapies for Prostate-Cancer Cell-Surface Antigens\n",
         "Compiled from ClinicalTrials.gov records, ASCO/AACR/Annals of Oncology abstracts, and peer-reviewed literature.\n",
         header, sep]
for r in rows_dict:
    lines.append(f"| {r['Program']} | {r['Antigens']} | {r['Modality']} | {r['Logic']} | {r['Sponsor']} | {r['Phase']} | {r['Identifier']} | {r['Status_Efficacy']} |\n")
with open("prostate_combinatorial_therapies.md","w") as f:
    f.writelines(lines)
print("ok")
