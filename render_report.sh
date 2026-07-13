#!/usr/bin/env bash
# Render the scientific report to BOTH HTML and PDF.
#
# The HTML is the primary deliverable. The PDF is printed from that same self-contained HTML with
# headless Chrome, so it matches the HTML styling and figures exactly, rather than being a separate
# LaTeX rendering. Run this instead of a bare `quarto render` so the two never drift apart.
#
# Note on the source-commit stamp: the report footer stamps the current git HEAD. For an honest stamp,
# commit the report sources and tables first, then run this, then commit the rendered outputs.
#
# Usage:  ./render_report.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HTML="$REPO/reports/report.html"
PDF="$REPO/reports/report.pdf"

echo "==> Rendering HTML (quarto)"
( cd "$REPO" && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 uv run quarto render reports/report.qmd --to html )

# Find a Chrome/Chromium binary for the HTML -> PDF print.
CHROME=""
for b in google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "$b" >/dev/null 2>&1; then CHROME="$b"; break; fi
done
if [ -z "$CHROME" ]; then
  echo "WARNING: no Chrome/Chromium found; HTML rendered but PDF skipped." >&2
  echo "         Install Chrome/Chromium, then re-run, to also get reports/report.pdf." >&2
  exit 0
fi

echo "==> Printing PDF from the HTML ($CHROME)"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PDF" "file://$HTML" >/dev/null 2>&1

echo "==> Done."
echo "    HTML: reports/report.html  ($(wc -c < "$HTML") bytes)"
echo "    PDF:  reports/report.pdf   ($(wc -c < "$PDF") bytes)"
