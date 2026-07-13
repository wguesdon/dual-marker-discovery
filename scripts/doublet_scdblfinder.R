#!/usr/bin/env Rscript
# scDblFinder doublet detection on the tumor cohort (run inside the bioconductor container).
#
# Reads the Python export (genes x cells MatrixMarket counts + per-cell sample labels), calls
# doublets per sample, and writes per-cell doublet scores and classes back to disk for Python to
# ingest. This is the R half of the write-to-disk Python<->R handoff; it uses only Matrix,
# SingleCellExperiment and scDblFinder.
#
# Usage (via podman):
#   podman run --rm -v "$PWD":/work -w /work <scdblfinder-image> \
#     Rscript scripts/doublet_scdblfinder.R
suppressMessages({
  library(Matrix)
  library(SingleCellExperiment)
  library(scDblFinder)
})

indir <- "data/interim/doublets"
counts <- as(readMM(file.path(indir, "counts.mtx")), "CsparseMatrix")  # genes x cells
barcodes <- readLines(file.path(indir, "barcodes.tsv"))
samples <- readLines(file.path(indir, "samples.tsv"))
colnames(counts) <- barcodes

sce <- SingleCellExperiment(assays = list(counts = counts))
set.seed(1)
sce <- scDblFinder(sce, samples = samples)

out <- data.frame(
  barcode = barcodes,
  sample = samples,
  doublet_score = colData(sce)$scDblFinder.score,
  doublet_class = as.character(colData(sce)$scDblFinder.class)
)
write.csv(out, file.path(indir, "doublet_calls.csv"), row.names = FALSE)
cat("scDblFinder done:", sum(out$doublet_class == "doublet"), "of", nrow(out),
    "cells called doublet\n")
