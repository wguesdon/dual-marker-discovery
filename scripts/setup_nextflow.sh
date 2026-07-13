#!/usr/bin/env bash
# User-level install of a JDK + Nextflow for running nf-core/scdownstream with podman.
# No sudo. Installs into ~/.local. Idempotent. Prints the env lines to source afterwards.
set -euo pipefail

PREFIX="${PREFIX:-$HOME/.local}"
BIN_DIR="$PREFIX/bin"
JDK_DIR="$PREFIX/jdk-17"
mkdir -p "$BIN_DIR"

# --- Temurin (Eclipse Adoptium) JDK 17, x64 Linux ---
if [ ! -x "$JDK_DIR/bin/java" ]; then
  echo "Installing Temurin JDK 17 -> $JDK_DIR ..."
  tmp="$(mktemp -d)"
  curl -fsSL \
    "https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse" \
    -o "$tmp/jdk.tar.gz"
  mkdir -p "$JDK_DIR"
  tar -xzf "$tmp/jdk.tar.gz" -C "$JDK_DIR" --strip-components=1
  rm -rf "$tmp"
fi

export JAVA_HOME="$JDK_DIR"
export PATH="$JDK_DIR/bin:$BIN_DIR:$PATH"
echo "java: $("$JDK_DIR/bin/java" -version 2>&1 | head -1)"

# --- Nextflow ---
if [ ! -x "$BIN_DIR/nextflow" ]; then
  echo "Installing Nextflow -> $BIN_DIR/nextflow ..."
  tmp="$(mktemp -d)"
  ( cd "$tmp" && curl -s https://get.nextflow.io | bash )
  mv "$tmp/nextflow" "$BIN_DIR/nextflow"
  chmod +x "$BIN_DIR/nextflow"
  rm -rf "$tmp"
fi

echo "nextflow: $("$BIN_DIR/nextflow" -version 2>&1 | grep -i version | head -1 || true)"
echo ""
echo "To use in this shell:"
echo "  export JAVA_HOME=$JDK_DIR"
echo "  export PATH=$JDK_DIR/bin:$BIN_DIR:\$PATH"
