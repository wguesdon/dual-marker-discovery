#!/usr/bin/env Rscript
# Extract the panel-gene counts and cell metadata from the HuPSA Seurat V5 object for cohort-2
# replication. Run inside a Seurat V5 container:
#   podman run --rm -v "$PWD":/work -w /work docker.io/satijalab/seurat:5.0.0 \
#     Rscript scripts/hupsa_extract.R
# Writes a small MatrixMarket + TSV/CSV exchange to data/interim/hupsa/ for Python to ingest.
suppressMessages({library(Seurat); library(Matrix)})

obj <- readRDS("data/raw/hupsa/HuPSA_share.rds")
cat("class:", paste(class(obj), collapse=","), "\n")
cat("dim (genes x cells):", paste(dim(obj), collapse=" x "), "\n")
cat("assays:", paste(Assays(obj), collapse=","), "\n")

md <- obj@meta.data
cat("\nmeta.data columns:\n"); print(colnames(md))
for (col in c("histo","histology","disease","cell_type","cell_type2","cell_type3",
              "celltype","sample","orig.ident","patient","donor","assay","study","GSE")) {
  if (col %in% colnames(md)) {
    cat("\n[", col, "] top levels:\n"); print(head(sort(table(as.character(md[[col]])), decreasing=TRUE), 40))
  }
}

panel <- read.csv("results/tables/surface_panel.csv")$gene
assay <- if ("RNA" %in% Assays(obj)) "RNA" else Assays(obj)[1]
DefaultAssay(obj) <- assay
obj <- tryCatch(JoinLayers(obj), error=function(e) { cat("JoinLayers skipped:", conditionMessage(e), "\n"); obj })
cts <- tryCatch(GetAssayData(obj, assay=assay, layer="counts"),
                error=function(e) GetAssayData(obj, assay=assay, slot="counts"))
genes <- rownames(cts)
present <- intersect(panel, genes)
cat("\npanel genes present:", length(present), "of", length(panel), "\n")
cat("missing:", paste(setdiff(panel, genes), collapse=","), "\n")

sub <- cts[present, , drop=FALSE]
outdir <- "data/interim/hupsa"; dir.create(outdir, recursive=TRUE, showWarnings=FALSE)
Matrix::writeMM(sub, file.path(outdir, "counts_panel.mtx"))
writeLines(present, file.path(outdir, "genes.tsv"))
writeLines(colnames(sub), file.path(outdir, "barcodes.tsv"))
# library size over ALL genes (for CP10k), one value per cell
libsize <- Matrix::colSums(cts)
write.csv(data.frame(barcode=colnames(cts), total_counts=as.numeric(libsize)),
          file.path(outdir, "libsize.csv"), row.names=FALSE)
write.csv(md, file.path(outdir, "metadata.csv"), row.names=TRUE)
cat("\nwrote extraction to", outdir, ":", ncol(sub), "cells x", nrow(sub), "panel genes\n")
