# CS05 — Key single-cell RNA-seq prostate cancer datasets

- **Type:** literature search — text answer (Claude Science workbench)
- **Purpose:** Find replication and discovery cohorts, especially mCRPC / NEPC, with access details.
- **Attach:** none — web literature only.

## Prompt

Compile the key publicly available single-cell RNA-seq datasets of human prostate cancer suitable for
target-discovery and replication. For each dataset give, with a citation (DOI):

- first author, year, journal;
- cohort size (n patients, n cells);
- disease stages covered (normal, localized/primary, castration-sensitive, castration-resistant/mCRPC,
  neuroendocrine/NEPC);
- assay and chemistry (10x version, Smart-seq2);
- whether it carries author malignant / cell-type annotations (and how malignant cells are defined);
- access location and file format (CELLxGENE, GEO accession, Figshare, Broad Single Cell Portal; ready
  `.h5ad` vs Seurat `.rds` needing conversion);
- license.

Include at least: HuPSA (Cheng et al. 2024, npj Precision Oncology), the localized hormone-naive atlas
(Apostolov et al., Cancer Res 2026 / GSE145843), Chen et al. 2021 (GSE141445), He et al. 2021 mCRPC (Nat
Med, SCP1244 / dbGaP), Song et al. 2022, Dong et al. (GSE137829), and the Tuong/Sanger prostate cell
atlas. Add any others you find.

Return a table sorted by usefulness for **mCRPC / NEPC replication**, with direct access URLs, and flag
which ship a ready `.h5ad`.

## Results

_Paste the Claude Science answer here (keep the sources/citations)._

## Follow-up / notes

_Best next replication cohort and its access/conversion cost._
