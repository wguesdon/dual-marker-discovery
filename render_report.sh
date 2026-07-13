#!/usr/bin/env bash
# Render the scientific report to BOTH HTML and PDF.
#
# HTML is the primary, fully-styled deliverable. The PDF is rendered with Quarto's bundled Typst
# engine (no system LaTeX or Chrome needed), so the same figures and tables appear in a single
# self-contained PDF that GitHub previews inline. Both formats execute the same code cells and read
# the same committed tables in results/tables/, so they cannot drift from the analysis.
#
# For an honest source-commit stamp, commit the report sources and tables first, then run this,
# then commit the rendered outputs.
#
# Usage:  ./render_report.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.local/bin:$PATH"

echo "==> Rendering HTML (quarto)"
( cd "$REPO" && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 uv run quarto render reports/report.qmd --to html )

echo "==> Rendering PDF (quarto + typst)"
( cd "$REPO" && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 uv run quarto render reports/report.qmd --to typst )

echo "==> Done."
echo "    HTML: reports/report.html  ($(wc -c < "$REPO/reports/report.html" 2>/dev/null || echo 0) bytes)"
echo "    PDF:  reports/report.pdf   ($(wc -c < "$REPO/reports/report.pdf" 2>/dev/null || echo 0) bytes)"
