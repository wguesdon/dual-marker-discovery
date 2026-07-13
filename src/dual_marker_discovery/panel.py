"""Curated cell-surface marker panel for prostate-cancer logic-gate discovery.

This is the single source of truth for which genes the pair scan considers. Script
``01_curate_surface_panel.py`` writes it to ``results/tables/surface_panel.csv``; the data
fetch (``00_fetch_data.py``) reads that gene list to subset both the tumor cohort and the
Tabula Sapiens healthy reference to the same panel.

Each gene is annotated with a ``compartment`` (surface / membrane / secreted) because
transcript presence is not targetability: secreted markers such as KLK3 (PSA) and KLK2 are
kept as comparators, not as targetable antigens. ``role_prior`` records how a marker is
expected to enter a gate, but the scan itself is unsupervised and evaluates every pair in
both directions. Normal-tissue notes are drawn from the Human Protein Atlas (FOLH1
ENSG00000086205, STEAP1 ENSG00000164647) and the PSCA tissue-expression literature
(Cancer Res 2002;62:2546); the PSMA x PSCA AND-gate benchmark is Kloss et al.,
Nat Biotechnol 2013;31:71 (10.1038/nbt.2459).
"""

from __future__ import annotations

import pandas as pd

# Fields: gene, alt_name, category, compartment, role_prior, positive_control, rationale.
_PANEL: list[dict] = [
    # --- Prostate-lineage tumor antigens (candidate activators) ---
    ("FOLH1", "PSMA", "prostate_antigen", "surface", "activator", True,
     "Canonical prostate target; PSMA x PSCA split-signal AND-gate benchmark (Kloss 2013). "
     "Normal expression in kidney proximal tubule, small intestine, salivary gland."),
    ("PSCA", "PSCA", "prostate_antigen", "surface", "activator", True,
     "GPI-anchored prostate stem-cell antigen; PSMA x PSCA benchmark. Normal expression in "
     "stomach, bladder urothelium, kidney collecting duct."),
    ("STEAP1", "STEAP1", "prostate_antigen", "surface", "activator", False,
     "Six-transmembrane epithelial antigen; xaluritamig (AMG509) STEAP1xCD3 engager, NCT04221542."),
    ("STEAP2", "STEAP2", "prostate_antigen", "surface", "activator", False,
     "Six-transmembrane metalloreductase; prostate-enriched STEAP1 paralog."),
    ("STEAP4", "STEAP4", "prostate_antigen", "surface", "activator", False,
     "STEAP-family metalloreductase with prostate expression."),
    ("TMEFF2", "TMEFF2", "prostate_antigen", "surface", "activator", False,
     "Transmembrane protein with EGF/follistatin domains; prostate-associated ADC target."),
    ("SLC45A3", "prostein", "prostate_antigen", "membrane", "activator", False,
     "Prostein; prostate-restricted membrane protein."),
    ("HPN", "hepsin", "prostate_antigen", "membrane", "activator", False,
     "Hepsin; type II membrane serine protease overexpressed in prostate cancer."),
    ("TMPRSS2", "TMPRSS2", "prostate_antigen", "membrane", "activator", False,
     "Type II transmembrane serine protease; luminal prostate; TMPRSS2-ERG fusion partner."),
    ("GRPR", "GRPR", "prostate_antigen", "surface", "activator", False,
     "Gastrin-releasing peptide receptor; prostate-cancer imaging/therapy GPCR."),
    # --- Broad epithelial / cross-tumor surface antigens ---
    ("TACSTD2", "TROP2", "epithelial_antigen", "surface", "activator", False,
     "TROP2; pan-epithelial surface antigen; sacituzumab govitecan target."),
    ("EPCAM", "EPCAM", "epithelial_antigen", "surface", "activator", False,
     "Pan-epithelial adhesion molecule; broad carcinoma antigen."),
    ("CEACAM5", "CEA", "epithelial_antigen", "surface", "activator", False,
     "Carcinoembryonic antigen; epithelial surface antigen."),
    ("CDH1", "E-cadherin", "epithelial_antigen", "surface", "activator", False,
     "E-cadherin; epithelial adhesion; broadly expressed."),
    ("CD276", "B7-H3", "tumor_antigen", "surface", "activator", False,
     "B7-H3; broadly tumor-associated surface antigen."),
    ("CD46", "CD46", "tumor_antigen", "surface", "activator", False,
     "Complement regulator; FOR46 antibody-drug conjugate in mCRPC."),
    ("ADAM9", "ADAM9", "tumor_antigen", "membrane", "activator", False,
     "Membrane metalloprotease; ADC target (IMGC936)."),
    ("NECTIN4", "Nectin-4", "tumor_antigen", "surface", "activator", False,
     "Nectin-4; enfortumab vedotin target; variable prostate expression."),
    ("CD70", "CD70", "tumor_antigen", "surface", "activator", False,
     "TNF-family surface ligand; PSMA/CD70 dual CAR-T (NCT05437341, bispecific)."),
    ("MME", "CD10", "tumor_antigen", "surface", "activator", False,
     "CD10; membrane metalloendopeptidase; prostate basal/stromal expression."),
    # --- Neuroendocrine-prostate antigen ---
    ("DLL3", "DLL3", "neuroendocrine_antigen", "surface", "activator", False,
     "Notch ligand; neuroendocrine prostate-cancer surface antigen."),
    # --- Low-prostate cross-tumor comparators (expected weak activators) ---
    ("FOLR1", "FRalpha", "low_pc_comparator", "surface", "comparator", False,
     "Folate receptor alpha; low prostate expression; cross-tumor comparator."),
    ("MSLN", "mesothelin", "low_pc_comparator", "surface", "comparator", False,
     "Mesothelin; low prostate expression; cross-tumor comparator."),
    ("ERBB2", "HER2", "low_pc_comparator", "surface", "comparator", False,
     "HER2; low/variable prostate expression; comparator."),
    # --- Secreted markers: NOT targetable at the surface, kept as pitfall comparators ---
    ("KLK3", "PSA", "secreted_comparator", "secreted", "comparator", False,
     "Prostate-specific antigen; secreted serine protease; classic marker but not "
     "surface-targetable (transcript-is-not-targetability pitfall)."),
    ("KLK2", "hK2", "secreted_comparator", "secreted", "comparator", False,
     "Human kallikrein 2; secreted; comparator."),
    ("ACPP", "PAP", "secreted_comparator", "secreted", "comparator", False,
     "Prostatic acid phosphatase; secreted/membrane; comparator."),
    # --- Normal-tissue markers as candidate NOT-gate blockers (spare healthy tissue) ---
    ("SLC34A1", "NaPi-IIa", "healthy_blocker_candidate", "membrane", "blocker_candidate", False,
     "Kidney proximal-tubule sodium-phosphate cotransporter; candidate NOT-gate blocker to "
     "spare kidney (a PSMA liability tissue)."),
    ("CDH16", "Ksp-cadherin", "healthy_blocker_candidate", "surface", "blocker_candidate", False,
     "Kidney-specific cadherin; candidate NOT-gate blocker to spare kidney."),
    ("MUC1", "MUC1", "healthy_blocker_candidate", "surface", "blocker_candidate", False,
     "Broadly expressed epithelial mucin; candidate NOT-gate blocker for normal epithelia."),
]

_COLUMNS = [
    "gene",
    "alt_name",
    "category",
    "compartment",
    "role_prior",
    "positive_control",
    "rationale",
]


def panel_frame() -> pd.DataFrame:
    """Return the curated surface panel as a DataFrame.

    Returns:
        One row per marker with columns ``gene``, ``alt_name``, ``category``,
        ``compartment``, ``role_prior``, ``positive_control`` and ``rationale``.
    """
    return pd.DataFrame(_PANEL, columns=_COLUMNS)


def panel_genes() -> list[str]:
    """Return the panel gene symbols in curation order.

    Returns:
        List of HGNC gene symbols to subset from the tumor cohort and healthy reference.
    """
    return [row[0] for row in _PANEL]


# The clinically/preclinically validated AND-gate pair used as the positive control.
POSITIVE_CONTROL_PAIR: tuple[str, str] = ("FOLH1", "PSCA")
