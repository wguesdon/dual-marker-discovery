#!/usr/bin/env bash
# User-level environment setup for the dual-marker-discovery pipeline.
#
# Installs the Quarto CLI (which bundles the Typst engine, so PDF rendering needs
# no system LaTeX) into ~/.local without sudo, and symlinks it onto PATH. Python
# dependencies are managed separately with `uv` (see README).
#
# Reproducible: pins the Quarto version. Re-running is idempotent.
set -euo pipefail

QUARTO_VERSION="${QUARTO_VERSION:-1.6.42}"
PREFIX="${PREFIX:-$HOME/.local}"
BIN_DIR="$PREFIX/bin"
OPT_DIR="$PREFIX/quarto-${QUARTO_VERSION}"

mkdir -p "$BIN_DIR" "$OPT_DIR"

if [ ! -x "$OPT_DIR/bin/quarto" ]; then
  url="https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"
  tmp="$(mktemp -d)"
  echo "Downloading Quarto ${QUARTO_VERSION} ..."
  curl -fsSL "$url" -o "$tmp/quarto.tar.gz"
  tar -xzf "$tmp/quarto.tar.gz" -C "$tmp"
  # The tarball extracts to quarto-<version>/ ; move its contents into OPT_DIR.
  cp -a "$tmp/quarto-${QUARTO_VERSION}/." "$OPT_DIR/"
  rm -rf "$tmp"
fi

ln -sf "$OPT_DIR/bin/quarto" "$BIN_DIR/quarto"

echo "Quarto installed at: $OPT_DIR"
"$BIN_DIR/quarto" --version
echo "Typst (bundled) check:"
"$BIN_DIR/quarto" typst --version || true
