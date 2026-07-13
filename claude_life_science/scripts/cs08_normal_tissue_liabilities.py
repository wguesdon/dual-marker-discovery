"""CS08 — Normal-tissue expression liabilities of 10 candidate prostate surface antigens

Verbatim Claude Science kernel code, reconstructed from the workbench execution log. This is a
**provenance record of how the committed artifacts were produced**, not a pipeline script.

The data pulls do not run outside the Claude Science workbench: they go through
``host.mcp(server, method, **kwargs)``, the connector bridge to GTEx, the Human Protein Atlas and
OpenAlex, which exists nowhere in this repo.

The figure does. Cell 10 defines ``apply_figure_style()`` and its helpers inline (it is the workbench
``figure-style`` skill, not an import), and cell 11 reads only ``gtex_median_tpm.csv``, committed under
``claude_life_science/outputs/cs08_normal_tissue_liabilities/``. Cells 10 and 11 run against that CSV in
a clean directory and reproduce ``results/figures/fig_s1_gtex_normal_tissue_tpm.png`` pixel for pixel
(0 of 6,052,606 pixels differ), with no workbench and no network.

Cells run in one shared kernel, so later cells depend on names bound by earlier ones. Cells are
reproduced in execution order with their original index. Cells that errored and were retried are
omitted; the retry that succeeded is kept.

Not reproduced below:
  - cell 6: errored, retried
  - cell 17: diff edit -> risk_reclassification.md
  - cell 18: errored, retried
  - cell 19: errored, retried

Outputs (relative to the workbench working directory):
  - handoff/gtex_raw.json
  - gtex_median_tpm.csv
  - handoff/hpa_records.json
  - handoff/hpa_flat.json
  - hpa_summary.csv
  - gtex_tpm_heatmap.png
  - concordance.csv
  - handoff/lit_raw.json
  - handoff/lit_raw2.json
  - literature_refs.csv
  - antigen_risk_table.csv
  - risk_reclassification.md
  - handoff/report_parts.json
  - antigen_safety_review.md
"""

# ruff: noqa
# fmt: off

# %% cell 0
import json, os
os.makedirs("handoff", exist_ok=True)

genes = ["FOLH1","STEAP1","STEAP2","PSCA","HPN","TMPRSS2","TACSTD2","CD276","EPCAM","DLL3"]

# 1) resolve to versioned GENCODE ids (gtex_v8)
res = host.mcp("expression","gtex_resolve_genes", gene_ids=genes)
print(json.dumps(res, indent=2)[:3000])

# %% cell 1  ->  handoff/gtex_raw.json
gmap = {g["geneSymbol"]: g["gencodeId"] for g in res["genes"]}
gencode_ids = list(gmap.values())

med = host.mcp("expression","gtex_median_expression", gencode_ids=gencode_ids)
print("total rows:", med.get("total"))
rows = med.get("data") or med.get("medianGeneExpression") or med.get("rows")
# inspect structure
print(list(med.keys()))
print(json.dumps((med.get("data") or med.get("medianGeneExpression"))[:2], indent=2) if isinstance(med.get("data") or med.get("medianGeneExpression"), list) else "n/a")
json.dump({"gmap":gmap, "median":med}, open("handoff/gtex_raw.json","w"))

# %% cell 2  ->  handoff/gtex_raw.json
print(json.dumps(med["medians"][:2], indent=2))
json.dump({"gmap":gmap, "medians":med["medians"]}, open("handoff/gtex_raw.json","w"))

# %% cell 3  ->  gtex_median_tpm.csv
import json, pandas as pd
d = json.load(open("handoff/gtex_raw.json"))
df = pd.DataFrame(d["medians"])[["geneSymbol","tissueSiteDetailId","median","unit"]]
df.columns = ["gene","tissue","median_tpm","unit"]
# pretty tissue label
df["tissue_label"] = df["tissue"].str.replace("_"," ")
df = df.sort_values(["gene","median_tpm"], ascending=[True,False])
df.to_csv("gtex_median_tpm.csv", index=False)

# per-gene top-5 tissues summary
top = (df.sort_values("median_tpm",ascending=False)
         .groupby("gene").head(5)
         .groupby("gene")
         .apply(lambda g: "; ".join(f"{t} ({v:.1f})" for t,v in zip(g.tissue_label,g.median_tpm)), include_groups=False))
print(df.shape, "| tissues:", df.tissue.nunique())
for g in ["FOLH1","STEAP1","STEAP2","PSCA","HPN","TMPRSS2","TACSTD2","CD276","EPCAM","DLL3"]:
    print(f"\n{g}: {top[g]}")

# %% cell 4  ->  handoff/hpa_records.json
import json
genes = ["FOLH1","STEAP1","STEAP2","PSCA","HPN","TMPRSS2","TACSTD2","CD276","EPCAM","DLL3"]
hpa = {}
for g in genes:
    try:
        hpa[g] = host.mcp("protein-annotation","get_protein_atlas_gene", gene=g)
    except Exception as e:
        hpa[g] = {"error": str(e)}
json.dump(hpa, open("handoff/hpa_records.json","w"))
# inspect one record's structure
print(list(hpa["FOLH1"].keys()))

# %% cell 5
import json
r = hpa["FOLH1"]
for k in ["tissue_expression","subcellular","antibody"]:
    print("="*30, k)
    print(json.dumps(r[k], indent=2)[:2500])

# %% cell 7  ->  handoff/hpa_flat.json
import json
rows=[]
for g,r in hpa.items():
    te=r.get("tissue_expression",{})
    sc=r.get("subcellular",{})
    ab=r.get("antibody",{})
    rows.append({
     "gene":g,
     "RNA_specificity":te.get("RNA tissue specificity"),
     "RNA_distribution":te.get("RNA tissue distribution"),
     "RNA_specific_nTPM":te.get("RNA tissue specific nTPM"),
     "RNA_celltype_enrichment":te.get("RNA tissue cell type enrichment"),
     "Protein_specificity":te.get("Protein tissue specificity"),
     "Protein_distribution":te.get("Protein tissue distribution"),
     "Protein_specific_Intensity":te.get("Protein tissue specific Intensity"),
     "IHC_reliability":ab.get("Reliability (IH)"),
     "Antibodies":ab.get("Antibody"),
     "Subcell_main":sc.get("Subcellular main location"),
     "Subcell_loc":sc.get("Subcellular location"),
    })
json.dump(rows, open("handoff/hpa_flat.json","w"))
for x in rows:
    print(json.dumps(x, default=str)[:600])
    print("-"*40)

# %% cell 8
for g in ["HPN","TMPRSS2","TACSTD2","CD276","EPCAM"]:
    ab=hpa[g]["antibody"]; sc=hpa[g]["subcellular"]; te=hpa[g]["tissue_expression"]
    print(g, "| IHC_reliab:", ab.get("Reliability (IH)"),
          "| Prot_spec:", te.get("Protein tissue specificity"),
          "| Prot_intensity:", te.get("Protein tissue specific Intensity"),
          "| Subcell:", sc.get("Subcellular location"))

# %% cell 9  ->  hpa_summary.csv
import json, pandas as pd
flat = json.load(open("handoff/hpa_flat.json"))
h = pd.DataFrame(flat)
for c in ["RNA_specific_nTPM","RNA_celltype_enrichment","Protein_specific_Intensity","Antibodies","Subcell_main","Subcell_loc"]:
    h[c] = h[c].apply(lambda v: json.dumps(v, default=str) if isinstance(v,(dict,list)) else v)
h.to_csv("hpa_summary.csv", index=False)
print(h[["gene","RNA_specificity","Protein_specificity","IHC_reliability"]].to_string(index=False))

# %% cell 10
# skill:figure-style kernel.py (auto-injected on skill load)
META_GREY = "#888888"


def apply_figure_style(*, frame="open", font=None, sizes=(8, 7, 6), grid=False):
    """Set matplotlib rcParams for publication-grade output. Call once before plotting.

    This sets mechanics (role-mapped font-size ladder, outward ticks, frameless
    legends, 300-dpi save, Type-42 embedded fonts) — not a house aesthetic.
    Frame, font and the size ladder are parameters.

    frame : 'open' (bottom+left spines, default) | 'boxed' (all four) | 'none'
    font  : sans-serif family name; None = system default sans-serif
    sizes : (base, secondary, tick) — titles/axis-labels, legend/annotation, ticks
    grid  : whether to draw axes.grid (default False)
    """
    import matplotlib as mpl
    if frame not in ("open", "boxed", "none"):
        raise ValueError(f"frame must be 'open'|'boxed'|'none', got {frame!r}")

    try:
        import os, sys, glob, matplotlib.font_manager as fm
        fdir = os.path.join(os.environ.get("CONDA_PREFIX") or sys.prefix, "fonts")
        if os.path.isdir(fdir):
            known = {f.fname for f in fm.fontManager.ttflist}
            for f in glob.glob(os.path.join(fdir, "*.ttf")):
                if f not in known:
                    fm.fontManager.addfont(f)
    except Exception:
        pass
    base, secondary, tick = sizes
    boxed = (frame == "boxed")
    rc = {
        "font.family": "sans-serif",
        "font.size": base,
        "axes.labelsize": base,
        "axes.titlesize": base,
        "legend.fontsize": secondary,
        "xtick.labelsize": tick,
        "ytick.labelsize": tick,
        "axes.linewidth": 0.6,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3, "ytick.major.size": 3,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "axes.spines.top": boxed, "axes.spines.right": boxed,
        "axes.spines.left": frame != "none", "axes.spines.bottom": frame != "none",
        "axes.grid": bool(grid),
        "legend.frameon": False,
        "figure.dpi": 200,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.titleweight": "normal",
        "axes.titlelocation": "left",
        "axes.labelweight": "normal",
        "lines.linewidth": 1.2,
        "patch.linewidth": 0.6,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    }
    if font:
        rc["font.sans-serif"] = [font, "DejaVu Sans"]
    mpl.rcParams.update(rc)


def set_frame(ax, style="open"):
    """§3: set spine visibility on an existing axes. style ∈ {'open','boxed','none'}."""
    show = {"open": (False, False, True, True),
            "boxed": (True, True, True, True),
            "none": (False, False, False, False)}[style]
    for side, vis in zip(("top", "right", "bottom", "left"), show):
        ax.spines[side].set_visible(vis)
        if vis:
            ax.spines[side].set_linewidth(0.6)
    ax.tick_params(direction="out", length=0 if style == "none" else 3, width=0.6)


def panel_letter(ax, letter, dx=-0.18, dy=1.02, case="lower", fontsize=None):
    """§5.7: bold panel letter outside top-left of axes. case ∈ {'lower','upper'}."""
    import matplotlib.pyplot as plt
    if fontsize is None:
        fontsize = plt.rcParams.get("font.size", 8) + 1
    s = letter.lower() if case == "lower" else letter.upper()
    ax.text(dx, dy, s, transform=ax.transAxes,
            fontweight="bold", fontsize=fontsize, va="bottom", ha="left")


def focal_palette(labels, focal, focal_color, other="muted", base_colors=None):
    """§4.2: map labels → colors with the focal series visually dominant.

    other='muted'   — desaturate base_colors (or a default cycle) toward gray
    other='grey'    — uniform light gray for all non-focal
    other='ordinal' — non-focal on a single light→dark gray ramp (input order)
    """
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    focal_set = {focal} if isinstance(focal, str) else set(focal)
    n = len(labels)
    if not focal_set & set(labels):
        raise ValueError(f"focal {focal!r} not found in labels")
    if base_colors is None:
        base_colors = plt.rcParams["axes.prop_cycle"].by_key().get("color", ["#444444"])
    base_colors = [base_colors[i % len(base_colors)] for i in range(n)]
    if other == "grey":
        rest = ["#BCBCBC"] * n
    elif other == "ordinal":
        nf = max(1, n - len(focal_set))
        ramp = [mcolors.to_hex((v, v, v)) for v in
                ([0.55] if nf == 1 else [0.80 - 0.35 * i / (nf - 1) for i in range(nf)])]
        rest, k = [], 0
        for l in labels:
            rest.append(ramp[min(k, nf - 1)]); k += (l not in focal_set)
    else:
        def mute(c):
            r, g, b = mcolors.to_rgb(c)
            m = (r + g + b) / 3
            return mcolors.to_hex((0.3 * r + 0.7 * m, 0.3 * g + 0.7 * m, 0.3 * b + 0.7 * m))
        rest = [mute(c) for c in base_colors]
    return [focal_color if l in focal_set else rest[i] for i, l in enumerate(labels)]


def bar_with_points(ax, x, ymat, labels, colors, jitter=0.08, show_points=True,
                    errorbar=None, point_alpha=0.5, point_size=8):
    """§6.1: bar = mean; optionally overlay raw points or draw an interval.

    colors   : per-label color list (e.g. from focal_palette)
    errorbar : None | 'sd' | 'ci95' — drawn only when show_points is False.
               'ci95' is the t-distribution 95% CI of the mean
               (half-width t_{0.975,n-1} · s/√n); correct at small n where the
               z-approximation (1.96·s/√n) is markedly too narrow.
    """
    import numpy as np
    means = np.array([np.mean(y) for y in ymat], float)
    err = None
    if errorbar and not show_points:
        if errorbar == "sd":
            err = np.array([np.std(y, ddof=1) if np.asarray(y).size > 1 else 0 for y in ymat])
        elif errorbar == "ci95":
            from scipy.stats import t
            def _hw(y):
                n = np.asarray(y).size
                return t.ppf(0.975, n - 1) * np.std(y, ddof=1) / np.sqrt(n) if n > 1 else 0
            err = np.array([_hw(y) for y in ymat])
    ax.bar(x, means, color=colors, width=0.7, edgecolor="none",
           yerr=err, error_kw={"elinewidth": 0.8, "capsize": 0})
    if show_points:
        for xi, ys in zip(x, ymat):
            ys = np.asarray(ys)
            if ys.ndim and ys.size > 1:
                jit = (np.random.rand(ys.size) - 0.5) * 2 * jitter
                ax.scatter(np.full(ys.size, xi) + jit, ys, s=point_size, color="black",
                           alpha=point_alpha, zorder=3, linewidths=0)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    return ax


def strip_with_median(ax, groups, values, colors=None, jitter=0.12):
    """§6.1: jittered points + bold horizontal median tick per group."""
    import numpy as np
    labs = list(groups)
    if colors is None:
        colors = ["#444444"] * len(labs)
    for i, (ys, c) in enumerate(zip(values, colors)):
        ys = np.asarray(ys)
        jit = (np.random.rand(ys.size) - 0.5) * 2 * jitter
        ax.scatter(np.full(ys.size, i) + jit, ys, s=10, color=c, alpha=0.6, linewidths=0, zorder=2)
        m = np.median(ys)
        ax.plot([i - 0.22, i + 0.22], [m, m], color="black", lw=1.6, zorder=3)
    ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs)
    return ax


def goodness_arrow(ax, text="higher = better", loc="upper left", axis="y", fontsize=None):
    """§3.6: small upright direction-of-goodness cue in the margin."""
    import matplotlib.pyplot as plt
    if fontsize is None:
        fontsize = plt.rcParams["legend.fontsize"]
    pos = {"upper left": (0.02, 0.98), "upper right": (0.98, 0.98),
           "lower left": (0.02, 0.02), "lower right": (0.98, 0.02)}[loc]
    ha = "left" if "left" in loc else "right"
    va = "top" if "upper" in loc else "bottom"
    arrow = "↑ " if axis == "y" else "→ "
    ax.text(pos[0], pos[1], arrow + text, transform=ax.transAxes,
            fontsize=fontsize, color=META_GREY, ha=ha, va=va)


def two_tier_label(name, meta):
    """§5: two-line label string (name / metadata). Meta line styled separately by caller."""
    return f"{name}\n{meta}"


def end_of_line_labels(ax, xs, ys, labels, colors=None, dx=0.01, fontsize=None):
    """§6.3 / §7.3: label each line series at its right end instead of a legend box."""
    import matplotlib.pyplot as plt
    if fontsize is None:
        fontsize = plt.rcParams["font.size"]
    if colors is None:
        colors = [None] * len(labels)
    span = ax.get_xlim()[1] - ax.get_xlim()[0]
    for x, y, lab, c in zip(xs, ys, labels, colors):
        ax.text(x[-1] + dx * span, y[-1], lab, color=c, va="center", ha="left", fontsize=fontsize)


def panel_crops(fig, dpi=None, pad_px=6, bbox_inches=None, pad_inches=None):
    """§9.2: pixel-space crop boxes for each lettered panel in the SAVED PNG.

    Returns ``{letter: (x0, y0, x1, y1)}`` in image-space pixels (origin
    top-left, matching ``host.view_image(path, crop=...)`` and PIL's
    ``Image.crop``). Panels are detected as bold single-character ``Text``
    objects placed by :func:`panel_letter`; each panel's crop is its axes'
    tightbbox mapped into the saved file's pixel space, padded by ``pad_px``.
    For §3.4 composites (abutting subplots sharing an axis, letter on the
    leftmost only) the crop unions in letterless ``sharex``/``sharey`` siblings
    on the same grid row/col so the whole composite is covered. When no axes
    carries a panel letter (standalone plot, or a figure-composer sub-agent),
    falls back to one crop per axes keyed by index.

    ``bbox_inches`` mirrors ``Figure.savefig`` semantics: ``None`` means
    *consult rcParams* (so under :func:`apply_figure_style` it resolves to
    ``'tight'``); pass an explicit ``Bbox`` only if you saved with one. The
    boxes are clamped to the saved image extent regardless.

        >>> fig.savefig("fig.png")            # bbox_inches='tight' via rcParams
        >>> for letter, box in panel_crops(fig).items():
        ...     host.view_image("fig.png", crop=box)
    """
    import matplotlib as mpl
    import matplotlib.text
    if dpi is None:
        dpi = mpl.rcParams.get("savefig.dpi", fig.dpi)
        if dpi == "figure":
            dpi = fig.dpi
    dpi = float(dpi)
    if bbox_inches is None:
        bbox_inches = mpl.rcParams.get("savefig.bbox")
    fig.canvas.draw()
    r = fig.canvas.get_renderer()

    if bbox_inches == "tight":
        if pad_inches is None:
            pad_inches = mpl.rcParams.get("savefig.pad_inches", 0.1)
        tb = fig.get_tightbbox(r).padded(pad_inches)
        ox_in, oy_in = tb.x0, tb.y0
        W_in, H_in = tb.width, tb.height
    elif isinstance(bbox_inches, mpl.transforms.BboxBase):
        ox_in, oy_in = bbox_inches.x0, bbox_inches.y0
        W_in, H_in = bbox_inches.width, bbox_inches.height
    else:
        ox_in, oy_in = 0.0, 0.0
        W_in, H_in = fig.get_size_inches()
    W_px, H_px = int(round(W_in * dpi)), int(round(H_in * dpi))
    lettered = {}
    for ax in fig.axes:
        for t in ax.findobj(matplotlib.text.Text):
            s = (t.get_text() or "").strip()
            if len(s) == 1 and s.isalpha() and t.get_fontweight() in ("bold", 700):
                lettered[ax] = s
                break



    if not lettered:
        lettered = {ax: str(i) for i, ax in enumerate(fig.axes)}
    out = {}
    for ax, letter in lettered.items():
        bbs = [ax.get_tightbbox(r)]




        ss = ax.get_subplotspec()
        for sib in fig.axes:
            if sib is ax or sib in lettered:
                continue
            ssib = sib.get_subplotspec()
            same_row = ss is None or ssib is None or ss.rowspan == ssib.rowspan
            same_col = ss is None or ssib is None or ss.colspan == ssib.colspan
            if ((ax.get_shared_y_axes().joined(ax, sib) and same_row)
                    or (ax.get_shared_x_axes().joined(ax, sib) and same_col)):
                bbs.append(sib.get_tightbbox(r))
        bb = mpl.transforms.Bbox.union(bbs)

        bx0 = (bb.x0 / fig.dpi - ox_in) * dpi
        bx1 = (bb.x1 / fig.dpi - ox_in) * dpi
        by0 = H_px - (bb.y1 / fig.dpi - oy_in) * dpi
        by1 = H_px - (bb.y0 / fig.dpi - oy_in) * dpi
        out[letter] = (
            max(int(bx0) - pad_px, 0),
            max(int(by0) - pad_px, 0),
            min(int(bx1) + pad_px, W_px),
            min(int(by1) + pad_px, H_px),
        )
    return out

# %% cell 11  ->  gtex_tpm_heatmap.png
import numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
apply_figure_style()

df = pd.read_csv("gtex_median_tpm.csv")
genes = ["FOLH1","STEAP1","STEAP2","PSCA","HPN","TMPRSS2","TACSTD2","CD276","EPCAM","DLL3"]
mat = df.pivot(index="gene", columns="tissue_label", values="median_tpm").reindex(genes)

# log10(TPM+1)
logm = np.log10(mat + 1)

# order tissues by max expression across the 10 antigens (surface high-signal normal tissues left→right)
order = logm.max(axis=0).sort_values(ascending=False).index
logm = logm[order]

fig, ax = plt.subplots(figsize=(15, 4.6))
im = ax.imshow(logm.values, aspect="auto", cmap="magma")
ax.set_xticks(range(len(order))); ax.set_xticklabels(order, rotation=90, fontsize=6)
ax.set_yticks(range(len(genes))); ax.set_yticklabels(genes, fontsize=8, style="italic")
# annotate cells with raw TPM where >=5
for i in range(len(genes)):
    for j in range(len(order)):
        v = mat.values[i,j]
        if v >= 10:
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=4.5,
                    color="white" if logm.values[i,j] < logm.values.max()*0.62 else "black")
cb = fig.colorbar(im, ax=ax, fraction=0.018, pad=0.01)
cb.set_label("log$_{10}$(median TPM + 1)", fontsize=7)
cb.ax.tick_params(labelsize=6)
ax.set_title("GTEx v8 median expression across normal tissues — 10 candidate prostate surface antigens\n(cell value = median TPM where ≥10; tissues ordered by peak signal)", fontsize=8.5, loc="left")
fig.tight_layout()
fig.savefig("gtex_tpm_heatmap.png", dpi=300, bbox_inches="tight")
print("saved", logm.shape)

# %% cell 12  ->  concordance.csv
import pandas as pd
# Synthesis grounded in the pulled HPA fields (RNA_specificity vs Protein_specificity + IHC reliability)
# and GTEx tissue ranking. Concordance = does HPA IHC protein staining match the RNA tissue distribution?
conc = [
 # gene, rna_call(GTEx+HPA), ihc_protein_call(HPA), ihc_reliab, concordance, rationale
 ("FOLH1","High: prostate, brain, kidney PT, salivary gland, small intestine (GTEx brain 61/prostate 51; HPA intestine+prostate)",
   "Protein group-enriched: small intestine, salivary gland; strong kidney proximal-tubule brush border, prostate epithelium","Enhanced","Concordant",
   "IHC brush-border + neuroendocrine staining matches RNA; PSMA protein sites (kidney PT, salivary, duodenum, brain astrocytes) well established."),
 ("STEAP1","Prostate-enriched (GTEx prostate 56; HPA prostate 79)","HPA IHC scores 'Not detected'","Uncertain","DISCORDANT (assay-limited)",
   "Single antibody (HPA030985), Uncertain reliability → HPA IHC underdetects. STEAP1 protein is documented at prostate/bladder/testis membranes in primary literature; do NOT read HPA 'Not detected' as absence."),
 ("STEAP2","Prostate-enriched (GTEx prostate 76; HPA prostate 120)","Group-enriched (cerebral cortex, fallopian tube); vesicles","Uncertain","Partial (assay-limited)",
   "Two antibodies but Uncertain reliability; RNA is prostate-dominant while protein calls are scattered → low confidence in protein map."),
 ("PSCA","Stomach>>bladder>esophagus>prostate (GTEx stomach 1261; HPA stomach 3010)","Tissue-enriched: stomach (very strong), plus bladder/urothelium, prostate; plasma membrane","Approved","Concordant",
   "Protein staining tracks RNA: stomach neck/isthmus mucous cells, urothelium, prostate. Strong GI/bladder normal protein confirmed."),
 ("HPN","Liver>>kidney>pancreas>stomach (GTEx liver 493, kidney 171, pancreas 133)","Protein 'detected in some' — HPA protein-specific intensity only LIVER; kidney/pancreas protein weak/absent by IHC","Approved","DISCORDANT (user-flagged)",
   "RNA broad (liver+kidney+pancreas+prostate) but IHC protein concentrates in liver and is weak elsewhere; hepsin RNA↔protein concordance reported weak. Protein map narrower than transcript."),
 ("TMPRSS2","Prostate>>stomach>colon>pancreas>lung (GTEx prostate 178)","HPA IHC scores 'Not detected'","Enhanced","DISCORDANT",
   "Despite Enhanced reliability tag, HPA IHC calls protein 'Not detected' while RNA is high in prostate/GI/lung and protein is well documented (lung, prostate, GI) in literature. HPA absence is assay/threshold artifact, not biology."),
 ("TACSTD2","Broad epithelial: esophagus>skin>salivary gland>vagina>cervix (GTEx esophagus 1419, skin ~700)","Tissue-enhanced, detected in many; strong squamous/glandular epithelia; plasma membrane","Enhanced","Concordant",
   "TROP2 protein staining broadly matches RNA across stratified/glandular epithelia (skin, oral/esophageal mucosa, salivary, breast, urothelium). Broad normal protein confirmed."),
 ("CD276","Low tissue specificity RNA (GTEx broad, fibroblast/stromal); HPA 'low tissue specificity'","Protein detected in many tissues; tissue-enhanced (ovary), vesicles/membrane","Enhanced","Partial / protein>RNA",
   "B7-H3 is post-transcriptionally repressed (miR-29); protein can exceed what mRNA suggests. HPA protein broad. Normal protein present on epithelia, some endothelium/stroma."),
 ("EPCAM","Epithelial: colon>ileum>thyroid>kidney medulla>pituitary (GTEx colon 347, ileum 309)","Tissue-enhanced, detected in many; strong basolateral epithelial membrane (GI, liver bile ducts, kidney, thyroid); plasma membrane","Enhanced","Concordant",
   "Protein tracks RNA across simple/glandular epithelia; classic basolateral epithelial adhesion molecule. Broad normal protein confirmed."),
 ("DLL3","Brain-enriched, low absolute (GTEx max ~11 TPM CNS); HPA brain 27","HPA IHC 'Not detected'; subcellular Golgi/nucleoplasm, not surface","None/NA","Concordant (low)",
   "DLL3 normal expression minimal and intracellular (Golgi); little/no normal cell-surface protein. HPA 'Not detected' consistent with tumor-selective surface presentation."),
]
cdf = pd.DataFrame(conc, columns=["gene","RNA_distribution","IHC_protein_call","IHC_reliability","concordance","concordance_rationale"])
cdf.to_csv("concordance.csv", index=False)
print(cdf[["gene","concordance","IHC_reliability"]].to_string(index=False))

# %% cell 13  ->  handoff/lit_raw.json
import json
queries = {
 "PSMA_tox":"PSMA radioligand therapy xerostomia salivary gland toxicity lutetium-177 PSMA-617",
 "PSMA_kidney":"PSMA folate hydrolase kidney proximal tubule expression normal tissue",
 "STEAP1_tox":"STEAP1 T-cell engager AMG 509 xaluritamig prostate cancer",
 "PSCA_cart":"PSCA CAR T cell prostate cancer normal tissue toxicity bladder stomach",
 "hepsin_polarity":"hepsin HPN apical membrane expression normal epithelium prostate",
 "TMPRSS2_expr":"TMPRSS2 protein expression normal tissue prostate lung apical",
 "TROP2_tox":"sacituzumab govitecan TROP2 TACSTD2 skin mucositis toxicity normal tissue",
 "B7H3_tox":"B7-H3 CD276 antibody drug conjugate normal tissue expression toxicity",
 "EPCAM_tox":"catumaxomab EpCAM EPCAM adhesion molecule basolateral epithelium toxicity",
 "DLL3_tox":"tarlatamab DLL3 delta-like ligand 3 small cell lung cancer cytokine release neurotoxicity",
}
out={}
for k,q in queries.items():
    try:
        r = host.mcp("literature","openalex_search_works", query=q, max_records=6)
        recs = r.get("records", r) if isinstance(r,dict) else r
        out[k]=recs
    except Exception as e:
        out[k]={"error":str(e)}
json.dump(out, open("handoff/lit_raw.json","w"))
# print titles + doi + year
for k,recs in out.items():
    print("="*20,k)
    if isinstance(recs,dict) and "error" in recs: print("ERR",recs["error"]); continue
    for w in (recs or [])[:6]:
        print(f"  {w.get('publication_year')} | {w.get('doi')} | {(w.get('title') or '')[:90]}")

# %% cell 14  ->  handoff/lit_raw2.json
import json
q2 = {
 "PSCA_trial":"PSCA-directed CAR T cells metastatic castration resistant prostate cancer phase 1 first-in-human",
 "hepsin_normal":"hepsin serine protease normal tissue distribution liver kidney immunohistochemistry",
 "TROP2_normal":"TROP2 Trop-2 expression normal human epithelial tissues immunohistochemistry distribution",
 "B7H3_normal":"B7-H3 CD276 normal tissue protein expression immunohistochemistry post-transcriptional",
 "EPCAM_catumaxomab":"catumaxomab EpCAM malignant ascites trifunctional antibody",
 "PSMA_neuro":"PSMA glutamate carboxypeptidase II brain astrocyte NAAG expression nervous system",
 "STEAP1_normal":"STEAP1 six transmembrane epithelial antigen prostate normal tissue expression membrane",
 "TACSTD2_polarity":"TROP2 epithelial junction membrane localization tight junction claudin",
}
out2={}
for k,q in q2.items():
    try:
        r = host.mcp("literature","openalex_search_works", query=q, max_records=5)
        out2[k]= r.get("records", r) if isinstance(r,dict) else r
    except Exception as e:
        out2[k]={"error":str(e)}
json.dump(out2, open("handoff/lit_raw2.json","w"))
for k,recs in out2.items():
    print("="*20,k)
    if isinstance(recs,dict) and "error" in recs: print("ERR",recs["error"]); continue
    for w in (recs or [])[:5]:
        print(f"  {w.get('publication_year')} | {w.get('doi')} | {(w.get('title') or '')[:85]}")

# %% cell 15  ->  literature_refs.csv
import pandas as pd
refs = [
 # antigen, topic, claim, doi/url, source_short
 ("FOLH1","expression/polarity","PSMA (GCPII/folate hydrolase) in kidney proximal tubule brush border, small intestine, salivary/lacrimal gland, and CNS astrocytes; PSMA imaging/therapy biodistribution","10.2967/jnumed.117.203877","J Nucl Med 2018 (PSMA biology perspective)"),
 ("FOLH1","toxicity","Salivary gland toxicity (xerostomia) is the dominant on-target off-tumor effect of 177Lu-PSMA radioligand therapy; preventive strategies reviewed","10.2967/jnumed.118.214379","J Nucl Med 2018 (salivary tox)"),
 ("FOLH1","toxicity","177Lu-PSMA-617 multicenter safety: xerostomia and nephrotoxicity as key normal-tissue dose-limiting sites","10.2967/jnumed.116.183194","J Nucl Med 2016 (German multicenter)"),
 ("FOLH1","CNS expression","PSMA = glutamate carboxypeptidase II in brain; NAAG hydrolysis, astrocyte/neuropil expression","10.1038/s41380-022-01656-x","Mol Psychiatry 2022 (GCPII DLPFC)"),
 ("STEAP1","toxicity/target","Xaluritamig (AMG 509), STEAP1xCD3 T-cell engager, mCRPC phase 1: CRS the main toxicity; STEAP1 prostate-restricted with low normal expression","10.1158/2159-8290.cd-23-0964","Cancer Discov 2023 (xaluritamig clinical)"),
 ("STEAP1","target biology","AMG 509 preclinical: STEAP1 avidity-driven targeting; normal expression low outside prostate","10.1158/2159-8290.cd-23-0984","Cancer Discov 2023 (AMG509 preclinical)"),
 ("STEAP1","expression","STEAP1 six-transmembrane membrane antigen; prostate + bladder/testis; family review","10.3390/cancers14164034","Cancers 2022 (STEAP1-4 review)"),
 ("STEAP1","CAR-T","STEAP1 CAR-T for advanced prostate cancer; STEAP1 as membrane target","10.1038/s41467-023-37874-2","Nat Commun 2023 (STEAP1 CAR-T)"),
 ("STEAP2","expression","STEAP family oxidoreductases; STEAP2 prostate-enriched; targets for immunotherapy","10.1111/boc.201200027","Biol Cell 2012 (STEAP family)"),
 ("PSCA","toxicity/CAR-T","PSCA-CAR T phase 1 in mCRPC: on-target activity; PSCA normal expression in bladder/stomach urothelium raises off-tumor risk","10.1038/s41591-024-02979-8","Nat Med 2024 (PSCA-CAR T phase 1)"),
 ("HPN","expression/polarity","Hepsin (TMPRSS1) type II transmembrane serine protease; apical/luminal on epithelia; liver, kidney, prostate; RNA-protein relationship","10.2741/2447","Front Biosci 2007 (hepsin & prostate)"),
 ("HPN","biology","Type II transmembrane serine protease dysregulation; hepsin tissue distribution & activation","10.3390/ijms21082663","IJMS 2020 (TTSP review)"),
 ("TMPRSS2","expression","TMPRSS2 protein in prostate, lung (alveolar/airway), GI; in situ protein profiling","10.1183/13993003.01123-2020","Eur Respir J 2020 (SARS-CoV-2 receptors in situ)"),
 ("TACSTD2","toxicity","Sacituzumab govitecan (anti-TROP2 ADC): neutropenia, diarrhea, mucositis, skin toxicity reflecting broad TROP2 epithelial expression","10.1002/cncr.30789","Cancer 2017 (sacituzumab govitecan)"),
 ("TACSTD2","polarity","TROP2 required for proper subcellular localization at epithelial junctions; controls claudin stability / tight-junction","10.2353/ajpath.2010.100149","Am J Pathol 2010 (TROP2 subcellular)"),
 ("TACSTD2","polarity","EPCAM and TROP2 share role in claudin stabilization and intestinal epithelium development (junctional/basolateral)","10.1242/bio.059403","Biol Open 2022 (EPCAM/TROP2 claudin)"),
 ("TACSTD2","expression","TROP2 expression across normal squamous/glandular epithelia; prognostic in multiple carcinomas","10.1038/modpathol.3801001","Mod Pathol 2007 (TROP2 marker)"),
 ("CD276","toxicity/target","B7-H3 (CD276) ADC/immunotherapy; broad tumor + normal stromal/epithelial expression; therapeutic landscape","10.1186/s12943-023-01751-9","Mol Cancer 2023 (B7-H3 frontiers)"),
 ("CD276","expression regulation","B7-H3 post-transcriptionally regulated; protein can exceed mRNA (miR-29); mTORC1 upregulation","10.1038/s41467-023-36881-7","Nat Commun 2023 (mTORC1-B7-H3)"),
 ("CD276","prostate","B7-H3 therapeutic vulnerability in PTEN/prostate cancer","10.1126/scitranslmed.adf6724","Sci Transl Med 2023 (B7-H3 prostate)"),
 ("EPCAM","toxicity","Catumaxomab (anti-EpCAM x anti-CD3 trifunctional): malignant ascites; on-target hepatotoxicity/cytokine effects reflecting broad epithelial EpCAM","10.1002/ijc.25423","Int J Cancer 2010 (catumaxomab ascites)"),
 ("EPCAM","polarity/normal","EpCAM basolateral epithelial adhesion; germline loss → congenital tufting enteropathy (essential normal-gut role)","10.1002/humu.23688","Hum Mutat 2018 (EPCAM tufting enteropathy)"),
 ("EPCAM","polarity","Matriptase cleavage of EpCAM destabilizes claudins & dysregulates intestinal barrier (junctional localization)","10.1172/jci88428","J Clin Invest 2017 (EpCAM claudin)"),
 ("DLL3","toxicity","Tarlatamab (DLL3xCD3 BiTE) in SCLC: CRS and neurologic events (ICANS); DLL3 minimal normal surface expression","10.1056/nejmoa2307980","NEJM 2023 (tarlatamab SCLC)"),
 ("DLL3","toxicity/mgmt","Practical management of tarlatamab adverse events (CRS/neurotoxicity)","10.1002/cncr.35738","Cancer 2025 (tarlatamab AE management)"),
 ("DLL3","target biology","DLL3 an inhibitory Notch ligand, normally intracellular (Golgi), aberrantly surface-expressed in SCLC/NEPC — basis of tumor selectivity","10.1186/s13045-023-01464-y","Exp Hematol Oncol 2023 (DLL3 therapies)"),
]
rdf = pd.DataFrame(refs, columns=["antigen","topic","claim","doi","source"])
rdf["url"] = "https://doi.org/" + rdf["doi"]
rdf.to_csv("literature_refs.csv", index=False)
print(rdf.groupby("antigen").size().to_string())
print("\nTotal refs:", len(rdf))

# %% cell 16  ->  antigen_risk_table.csv
import pandas as pd, json
gtex = pd.read_csv("gtex_median_tpm.csv")
# GTEx top-5 normal tissues per gene
top5 = (gtex.sort_values("median_tpm",ascending=False).groupby("gene").head(5)
        .groupby("gene").apply(lambda g:"; ".join(f"{t} {v:.0f}" for t,v in zip(g.tissue_label,g.median_tpm)), include_groups=False).to_dict())

# Master table rows. TPM values pulled from gtex; protein/tox/polarity from HPA + literature.
M = [
{"antigen":"FOLH1 (PSMA)",
 "gtex_top_normal_tpm":top5["FOLH1"],
 "hpa_rna_specificity":"Tissue enhanced (intestine, prostate)",
 "protein_normal_tissues":"Kidney proximal-tubule brush border, small intestine, salivary/lacrimal gland, CNS astrocytes/neuropil, prostate epithelium",
 "ihc_reliability":"Enhanced",
 "rna_ihc_concordance":"Concordant",
 "polarity_access":"APICAL (renal PT brush border, gut) — luminal, largely shielded from blood; but salivary/lacrimal & CNS accessible to radioligands",
 "clinical_toxicity":"Xerostomia (salivary), lacrimal, nephrotoxicity with 177Lu-PSMA RLT; well-documented on-target off-tumor",
 "risk_note":"MODERATE. Broad normal expression but apical/enzymatic; toxicity real (salivary/kidney) yet clinically manageable. Well-validated target.",
 "key_dois":"10.2967/jnumed.117.203877; 10.2967/jnumed.118.214379"},

{"antigen":"STEAP1",
 "gtex_top_normal_tpm":top5["STEAP1"],
 "hpa_rna_specificity":"Tissue enhanced (prostate)",
 "protein_normal_tissues":"Prostate epithelium; low-level bladder/testis; HPA IHC 'Not detected' (Uncertain, single Ab)",
 "ihc_reliability":"Uncertain",
 "rna_ihc_concordance":"DISCORDANT (assay-limited — HPA underdetects)",
 "polarity_access":"Plasma-membrane, multi-span; prostate luminal epithelium",
 "clinical_toxicity":"Xaluritamig (STEAP1xCD3): CRS predominant; limited off-tumor at doses tested — favorable prostate restriction",
 "risk_note":"LOW-MODERATE. Prostate-restricted, low normal expression. Do NOT treat HPA 'Not detected' as proof of absence (Uncertain reliability).",
 "key_dois":"10.1158/2159-8290.cd-23-0964; 10.3390/cancers14164034"},

{"antigen":"STEAP2",
 "gtex_top_normal_tpm":top5["STEAP2"],
 "hpa_rna_specificity":"Tissue enriched (prostate)",
 "protein_normal_tissues":"Prostate epithelium; scattered protein calls (cerebral cortex, fallopian tube) at low confidence",
 "ihc_reliability":"Uncertain",
 "rna_ihc_concordance":"Partial (assay-limited)",
 "polarity_access":"Plasma-membrane; prostate luminal epithelium",
 "clinical_toxicity":"No approved agent; expected prostate-restricted like STEAP1; toxicity profile unproven",
 "risk_note":"LOW-MODERATE (uncertain). Prostate-enriched transcript; protein map low-confidence. Needs orthogonal protein validation.",
 "key_dois":"10.1111/boc.201200027"},

{"antigen":"PSCA",
 "gtex_top_normal_tpm":top5["PSCA"],
 "hpa_rna_specificity":"Tissue enriched (stomach >> bladder, esophagus, prostate)",
 "protein_normal_tissues":"Stomach (mucous neck cells, strong), bladder/urothelium, esophagus, prostate; plasma membrane",
 "ihc_reliability":"Approved",
 "rna_ihc_concordance":"Concordant",
 "polarity_access":"Plasma-membrane, GPI-anchored; urothelial/gastric — apical/luminal but urothelium accessible",
 "clinical_toxicity":"PSCA-CAR T (mCRPC ph1): on-target activity; substantial normal stomach/bladder expression is the key off-tumor liability",
 "risk_note":"MODERATE-HIGH. High normal GI/bladder protein confirmed. On-target off-tumor to stomach/urothelium is the dominant concern.",
 "key_dois":"10.1038/s41591-024-02979-8"},

{"antigen":"HPN (hepsin)",
 "gtex_top_normal_tpm":top5["HPN"],
 "hpa_rna_specificity":"Tissue enhanced (liver, kidney, pancreas)",
 "protein_normal_tissues":"Liver (strong IHC), variable/weak kidney & pancreas at protein; prostate epithelium. Protein narrower than RNA",
 "ihc_reliability":"Approved",
 "rna_ihc_concordance":"DISCORDANT (RNA broad liver+kidney+pancreas; protein concentrates in liver) — weak RNA/protein concordance",
 "polarity_access":"APICAL type-II transmembrane serine protease on epithelial luminal surface (bile canaliculi, renal tubule, prostate lumen) — luminal, less vascular-accessible",
 "clinical_toxicity":"No approved agent; expected hepatic/renal on-target if protein present; protease activity adds functional risk",
 "risk_note":"MODERATE. RNA overstates breadth; protein liver-dominant & apical. Concordance weak → protein data change the risk map.",
 "key_dois":"10.2741/2447; 10.3390/ijms21082663"},

{"antigen":"TMPRSS2",
 "gtex_top_normal_tpm":top5["TMPRSS2"],
 "hpa_rna_specificity":"Tissue enhanced (prostate, stomach, colon, lung)",
 "protein_normal_tissues":"Prostate, lung (alveolar/airway epithelium), GI, kidney — protein documented in literature despite HPA IHC 'Not detected'",
 "ihc_reliability":"Enhanced (but scores 'Not detected')",
 "rna_ihc_concordance":"DISCORDANT (HPA IHC negative vs high RNA + literature-confirmed protein)",
 "polarity_access":"APICAL type-II transmembrane serine protease; airway/prostate luminal surface",
 "clinical_toxicity":"Mainly a fusion-partner/entry protease; not a mature ADC/T-cell target; expected lung/GI/prostate off-tumor if targeted",
 "risk_note":"MODERATE. Broad epithelial protein (lung, GI, prostate). HPA 'Not detected' is misleading — transcript+literature indicate real protein.",
 "key_dois":"10.1183/13993003.01123-2020"},

{"antigen":"TACSTD2 (TROP2)",
 "gtex_top_normal_tpm":top5["TACSTD2"],
 "hpa_rna_specificity":"Tissue enhanced (esophagus, skin, salivary gland — broad epithelial)",
 "protein_normal_tissues":"Broad: skin keratinocytes, oral/esophageal squamous mucosa, salivary gland, breast, urothelium, lung, GI; plasma membrane",
 "ihc_reliability":"Enhanced",
 "rna_ihc_concordance":"Concordant",
 "polarity_access":"Membranous at epithelial junctions (claudin/tight-junction regulator); largely basolateral/junctional but broadly present in skin & mucosa (accessible)",
 "clinical_toxicity":"Sacituzumab govitecan: neutropenia, diarrhea, mucositis, skin/rash — reflect broad normal epithelial TROP2 (plus payload effects)",
 "risk_note":"HIGH breadth. Very broad normal epithelial protein confirmed at high reliability. Therapeutic index depends on ADC payload/dose, not antigen restriction.",
 "key_dois":"10.1002/cncr.30789; 10.1242/bio.059403"},

{"antigen":"CD276 (B7-H3)",
 "gtex_top_normal_tpm":top5["CD276"],
 "hpa_rna_specificity":"Low tissue specificity (broad, fibroblast/stromal)",
 "protein_normal_tissues":"Broad low-level: epithelia, some endothelium, stroma, fibroblasts; protein often exceeds mRNA (post-transcriptional/miR-29)",
 "ihc_reliability":"Enhanced",
 "rna_ihc_concordance":"Partial — protein > RNA (post-transcriptional de-repression)",
 "polarity_access":"Plasma-membrane; broad including vascular/stromal — vascular-accessible in some sites",
 "clinical_toxicity":"ADC/CAR programs: broad normal protein raises off-tumor concern; toxicity dominated by payload; tumor overexpression vs normal is quantitative not qualitative",
 "risk_note":"MODERATE-HIGH & UNDER-ESTIMATED BY RNA. Because protein exceeds transcript, a transcript-only estimate understates normal presence. Flag.",
 "key_dois":"10.1038/s41467-023-36881-7; 10.1186/s12943-023-01751-9"},

{"antigen":"EPCAM",
 "gtex_top_normal_tpm":top5["EPCAM"],
 "hpa_rna_specificity":"Tissue enhanced (intestine — broad epithelial)",
 "protein_normal_tissues":"Broad simple/glandular epithelia: GI tract, hepatic bile ducts, kidney tubules, thyroid, pancreas, breast; strong membranous",
 "ihc_reliability":"Enhanced",
 "rna_ihc_concordance":"Concordant",
 "polarity_access":"BASOLATERAL epithelial adhesion molecule (junctional); essential for gut barrier (loss→tufting enteropathy). Basolateral = less luminal but junctional/accessible",
 "clinical_toxicity":"Catumaxomab (anti-EpCAM x CD3): cytokine effects, hepatotoxicity, GI; broad epithelial EpCAM drives on-target risk",
 "risk_note":"HIGH breadth. Ubiquitous epithelial protein confirmed at high reliability. Off-tumor GI/hepatic risk intrinsic to target.",
 "key_dois":"10.1002/ijc.25423; 10.1002/humu.23688"},

{"antigen":"DLL3",
 "gtex_top_normal_tpm":top5["DLL3"],
 "hpa_rna_specificity":"Tissue enriched (brain — low absolute, max ~11 TPM)",
 "protein_normal_tissues":"Minimal normal surface protein; predominantly intracellular (Golgi). HPA IHC 'Not detected'. Aberrant surface expression in SCLC/NEPC",
 "ihc_reliability":"None/NA",
 "rna_ihc_concordance":"Concordant (low) — low RNA, intracellular protein, no normal surface",
 "polarity_access":"Normally INTRACELLULAR (Golgi/cytoplasm), not cell-surface accessible in normal tissue; surface only on tumor",
 "clinical_toxicity":"Tarlatamab (DLL3xCD3): CRS and neurologic events (ICANS) — mechanism/on-tumor driven, minimal normal on-target off-tumor",
 "risk_note":"LOWEST off-tumor. Near-absent normal surface protein; tumor-selective surface presentation. Toxicity is CRS/neuro, not normal-tissue on-target.",
 "key_dois":"10.1056/nejmoa2307980; 10.1186/s13045-023-01464-y"},
]
mdf = pd.DataFrame(M)
mdf.to_csv("antigen_risk_table.csv", index=False)
print(mdf[["antigen","ihc_reliability","rna_ihc_concordance"]].to_string(index=False))
print("\ncols:", list(mdf.columns))

# %% cell 20  ->  handoff/report_parts.json
import pandas as pd
mdf = pd.read_csv("antigen_risk_table.csv")
rdf = pd.read_csv("literature_refs.csv")
HEATMAP_ART = "e3d6cb58-b077-4fcb-9327-859dc5b11962"

def to_md(df):
    cols=list(df.columns)
    esc=lambda x:str(x).replace("|","\\|").replace("\n"," ")
    L=["| "+" | ".join(cols)+" |","| "+" | ".join(["---"]*len(cols))+" |"]
    for r in df.itertuples(index=False): L.append("| "+" | ".join(esc(v) for v in r)+" |")
    return "\n".join(L)

tbl_cols=["antigen","protein_normal_tissues","ihc_reliability","rna_ihc_concordance","polarity_access","clinical_toxicity","risk_note"]
tbl=mdf[tbl_cols].copy()
tbl.columns=["Antigen","Normal tissues/cell types (protein)","IHC reliab.","RNA↔IHC concordance","Apical/basolateral & access","Clinical toxicity","Risk note"]
md_tbl=to_md(tbl)

def block(r):
    return (f"### {r.antigen}\n\n"
    f"- **Normal tissues / cell types (protein-level where possible):** {r.protein_normal_tissues}\n"
    f"- **GTEx transcript (top normal tissues, median TPM):** {r.gtex_top_normal_tpm}\n"
    f"- **HPA RNA specificity:** {r.hpa_rna_specificity}\n"
    f"- **HPA IHC reliability:** {r.ihc_reliability}\n"
    f"- **RNA-vs-IHC concordance:** {r.rna_ihc_concordance}\n"
    f"- **Apical/basolateral & vascular accessibility:** {r.polarity_access}\n"
    f"- **Documented / expected clinical toxicity:** {r.clinical_toxicity}\n"
    f"- **Risk note:** {r.risk_note}\n"
    f"- **Key refs:** {r.key_dois}\n")
narr="\n".join(block(r) for r in mdf.itertuples())
reflist="\n".join(f"- **{r.antigen}** — {r.claim} — {r.source}. [{r.doi}]({r.url})" for r in rdf.sort_values('antigen').itertuples())

import json
json.dump({"md_tbl":md_tbl,"narr":narr,"reflist":reflist,"HEATMAP_ART":HEATMAP_ART}, open("handoff/report_parts.json","w"))
print("parts ready:", len(md_tbl), len(narr), len(reflist))

# %% cell 21  ->  antigen_safety_review.md
import json
p=json.load(open("handoff/report_parts.json"))
md_tbl,narr,reflist,HEATMAP_ART=p["md_tbl"],p["narr"],p["reflist"],p["HEATMAP_ART"]

report=f"""# Normal-tissue expression and on-target/off-tumor risk of 10 candidate prostate surface antigens

**Targets:** FOLH1/PSMA, STEAP1, STEAP2, PSCA, HPN/hepsin, TMPRSS2, TACSTD2/TROP2, CD276/B7-H3, EPCAM, DLL3

## Methods & data sources
- **Transcript:** GTEx v8 (GENCODE v26, GRCh38), median TPM across all 54 tissue sites, via the pinned GTEx API. Gene symbols resolved to versioned GENCODE IDs before querying.
- **RNA + protein (IHC):** Human Protein Atlas release 25.1 — per-gene RNA tissue specificity/distribution, protein (IHC) tissue specificity and intensity, IHC **reliability category** (Enhanced > Supported > Approved > Uncertain), and subcellular location.
- **Toxicity, polarity, and concordance interpretation:** primary literature retrieved via OpenAlex; DOIs listed per claim below.
- **Interpretive rule:** HPA IHC "Not detected" is treated as evidence of absence **only** when the reliability category is Enhanced/Supported *and* transcript/literature agree. An *Uncertain* "Not detected" is treated as assay-limited, not biological absence.

## GTEx median-TPM heatmap
Median expression (log10 TPM+1) for the 10 antigens across 54 GTEx normal tissues; cell values show median TPM where ≥10; tissues ordered left→right by peak signal, which surfaces the high-risk normal sites (esophagus, stomach, skin, salivary gland, liver, kidney, GI, prostate, brain).

![GTEx median-TPM heatmap across normal tissues for the 10 antigens]({{{{artifact:{HEATMAP_ART}}}}})

## Master risk table

{md_tbl}

## Per-antigen detail

{narr}

## Antigens whose protein-level normal expression would change the safety ranking

A transcript co-detection estimate (ranking risk by where mRNA is co-detected) is a proxy that protein reality can shift in either direction. The material reclassifications:

1. **HPN / hepsin — transcript OVERSTATES breadth (move down / relocate to liver).** RNA is broad (liver+kidney+pancreas+prostate) but HPA IHC (Approved) concentrates protein in **liver**, weak elsewhere — the user-flagged weak RNA↔protein concordance. Hepsin is also **apical** (luminal epithelial surface), so less vascular-accessible than the transcript breadth implies.
2. **TMPRSS2 — database protein UNDERSTATES risk (move up).** HPA IHC calls protein "Not detected" despite an Enhanced tag, but transcript is high and literature confirms **apical** protein in prostate, lung, and GI. The transcript estimate is the more faithful proxy here.
3. **CD276 / B7-H3 — protein EXCEEDS transcript (move up).** Post-transcriptional de-repression (miR-29, mTORC1) means protein is broader and higher than "low tissue specificity" mRNA predicts; HPA IHC (Enhanced) confirms broad protein including some vascular/stromal (accessible) sites.
4. **STEAP1 / STEAP2 — assay under-detection creates a false-safe signal (add confidence flag).** HPA IHC "Not detected" is *Uncertain* (single/low-confidence antibodies); the prostate-restricted direction is likely right, but the protein layer cannot confirm it — flag rather than reassure.

**Concordant, ranking-unchanged (transcript ≈ protein):** FOLH1/PSMA, PSCA, TACSTD2/TROP2, EPCAM. **DLL3** is concordant at the low-risk end — transcript low and protein intracellular (Golgi), no normal surface — the benchmark tumor-selective surface antigen.

## Key caveats
- GTEx TPM is **bulk** tissue; cell-type-restricted expression (e.g. FOLH1 in kidney proximal tubule) is diluted in whole-tissue medians — cross-check the HPA cell-type enrichment column.
- HPA IHC reliability is heterogeneous here: two antigens (STEAP1, STEAP2) are *Uncertain* and one (DLL3) has no IHC score — protein calls for these carry low confidence.
- Apical/luminal localization reduces but does not eliminate accessibility to systemic agents (radioligands reach salivary/renal apical PSMA); polarity modifies, not negates, risk.
- Toxicity for agents in trials (xaluritamig, PSCA-CAR T, tarlatamab) is dominated by CRS/neurologic mechanism-based effects; classic normal-tissue on-target off-tumor is most prominent for PSMA (salivary/kidney), TROP2 (skin/mucosa), and EPCAM (GI/hepatic).

## References (claim → DOI/URL)

{reflist}

## Artifacts
- `antigen_risk_table.csv` — full master table (all columns incl. GTEx TPM and DOIs)
- `gtex_median_tpm.csv` — GTEx v8 median TPM, 10 genes × 54 tissues (long format)
- `hpa_summary.csv` / `hpa_records.json` — HPA RNA + IHC + reliability + subcellular
- `concordance.csv` — RNA-vs-IHC concordance calls with rationale
- `literature_refs.csv` — 26 curated primary references with DOIs
- `gtex_tpm_heatmap.png` — the figure above
- `risk_reclassification.md` — detailed ranking-change analysis
"""
open("antigen_safety_review.md","w").write(report)
print("report bytes:", len(report))
