# Antigens whose protein-level normal expression changes the safety ranking

**Premise.** A transcript co-detection estimate ranks off-tumor risk by where a
gene's mRNA is co-detected across normal tissues (e.g. GTEx median TPM, HPA RNA
distribution). This is a proxy. Protein-level reality can move an antigen up or
down that ranking for four reasons: (1) protein is more/less broadly present
than transcript; (2) protein is polarized (apical/luminal vs basolateral) and
therefore differentially accessible to a systemic agent; (3) protein is
intracellular and not surface-accessible at all; (4) the antibody assay
under-detects, so a transcript signal has no protein counterpart in the
database even though protein exists.

Ranked by the *magnitude and direction* of the transcript→protein correction:

---

## 1. HPN / hepsin — transcript OVERSTATES risk (rank should move DOWN)
- **Transcript estimate:** high, broad — liver, kidney cortex/medulla, pancreas,
  stomach, prostate. A co-detection score reads hepsin as a *multi-organ* risk.
- **Protein reality:** HPA IHC (Approved) shows strong protein in **liver** with
  weak/variable staining in kidney and pancreas — the protein map is narrower
  than the transcript map. This is the user-flagged weak RNA↔protein
  concordance case. Additionally hepsin is an **apical** type-II transmembrane
  protease on luminal epithelial surfaces (bile canaliculi, tubule lumen,
  prostatic lumen), i.e. less exposed to circulating agents than a
  basolateral/vascular antigen.
- **Net effect:** protein data **downgrade** the apparent breadth (liver-dominant,
  apical) but concentrate concern on the liver specifically. A transcript-only
  ranking would over-penalize kidney/pancreas and under-weight the polarity
  shielding. **Ranking changes materially.**
- Refs: 10.2741/2447; 10.3390/ijms21082663

## 2. TMPRSS2 — database protein UNDERSTATES risk (rank should move UP)
- **Transcript estimate:** high in prostate, stomach, colon, pancreas, lung.
- **Protein reality:** HPA IHC scores **"Not detected"** despite an *Enhanced*
  reliability tag — an internal contradiction. Primary literature (in situ
  protein profiling) confirms TMPRSS2 protein in prostate, airway/alveolar lung,
  and GI epithelium, on the **apical** surface. A naive reader trusting HPA
  "Not detected" would rank TMPRSS2 as low-risk; the transcript + literature say
  otherwise.
- **Net effect:** protein evidence **upgrades** risk relative to the HPA IHC
  call. Here the *transcript* estimate is actually the more faithful proxy and
  the database protein call is the outlier. **Ranking changes materially.**
- Refs: 10.1183/13993003.01123-2020

## 3. CD276 / B7-H3 — protein EXCEEDS transcript (rank should move UP)
- **Transcript estimate:** "low tissue specificity", broad but low — a
  co-detection score treats it as diffuse/low.
- **Protein reality:** B7-H3 is **post-transcriptionally de-repressed** (miR-29,
  mTORC1); protein is present more widely and at higher levels than mRNA
  predicts, on epithelia, stroma, and some endothelium (vascular-accessible).
  HPA IHC is *Enhanced* and calls protein "detected in many".
- **Net effect:** a transcript co-detection estimate **understates** normal
  protein burden. This is the clearest case where mRNA is a poor proxy in the
  *upward* direction. **Ranking changes materially.**
- Refs: 10.1038/s41467-023-36881-7; 10.1186/s12943-023-01751-9

## 4. STEAP1 (and STEAP2) — assay under-detection creates a FALSE-SAFE signal
- **Transcript estimate:** prostate-enriched, low elsewhere → looks favorable.
- **Protein reality:** HPA IHC calls STEAP1 protein **"Not detected"** but with
  *Uncertain* reliability (single antibody, HPA030985). This "Not detected" must
  **not** be read as proof of absence; STEAP1 membrane protein is documented in
  prostate and at lower levels in bladder/testis. STEAP2 is analogous
  (*Uncertain*, scattered low-confidence calls).
- **Net effect:** the *direction* of the transcript estimate (prostate-restricted,
  low-risk) is probably correct, but the database protein layer cannot confirm
  it. The ranking should carry an **explicit low-confidence flag**, not a false
  reassurance from "Not detected". Requires orthogonal protein validation.
- Refs: 10.1158/2159-8290.cd-23-0964; 10.3390/cancers14164034

## 5. DLL3 — transcript AND protein agree the surface is empty (rank stays LOW, correctly)
- **Transcript estimate:** brain-enriched but very low absolute (max ~11 TPM);
  a co-detection score already reads it as narrow.
- **Protein reality:** protein is **intracellular (Golgi)** with essentially no
  normal cell-surface presentation; aberrant surface expression appears only in
  SCLC/NEPC. Here protein data **confirm** and even strengthen the low-risk call
  — the accessible (surface) protein pool is near zero even where transcript exists.
- **Net effect:** no reclassification, but it illustrates the opposite lesson —
  transcript that looks worrisome can be inaccessible at the protein/surface level.
  DLL3 is the safety benchmark for "tumor-selective surface antigen".
- Refs: 10.1056/nejmoa2307980; 10.1186/s13045-023-01464-y

---

## Antigens where transcript ≈ protein (ranking unchanged)
- **FOLH1/PSMA** — broad transcript, matching apical protein; toxicity
  (salivary/kidney) predicted by both. Concordant, *Enhanced*.
- **PSCA** — high stomach/bladder transcript, matching strong protein; *Approved*.
- **TACSTD2/TROP2** — broad epithelial transcript, matching broad protein; *Enhanced*.
- **EPCAM** — broad epithelial transcript, matching broad basolateral protein; *Enhanced*.

For these four, a transcript co-detection estimate and the protein-level truth
point to the same ranking, so protein data refine the *mechanism* (which cells,
which polarity) but not the *rank*.

## Bottom line
The antigens where protein-level data **materially change the safety ranking**
relative to a transcript co-detection estimate are **HPN (down/relocate),
TMPRSS2 (up), CD276/B7-H3 (up), and STEAP1/STEAP2 (confidence flag, not a
reclassification of direction).** PSMA, PSCA, TROP2, and EPCAM are transcript-faithful;
DLL3 is transcript-and-protein-concordant at the low-risk end.
