"""Configuration and credential loading for the pipeline.

The single-cell analysis needs no credentials: every dataset (CELLxGENE Census, Tabula Sapiens, HuPSA,
the Human Protein Atlas, PaxDb) is public. The accessors below exist for the later phases, the LLM app
and any AWS offload. Secrets are read from the repository ``.env`` file, which is gitignored. Nothing
here ever prints or returns a secret except the accessor the caller explicitly asks for.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
ENV_PATH = REPO / ".env"

# Canonical project paths, so scripts never hard-code relative paths.
DATA = REPO / "data"
DATA_RAW = DATA / "raw"
DATA_INTERIM = DATA / "interim"
DATA_PROCESSED = DATA / "processed"
DATA_EXTERNAL = DATA / "external"
RESULTS = REPO / "results"
RESULTS_TABLES = RESULTS / "tables"
RESULTS_FIGURES = RESULTS / "figures"
RESULTS_APP = RESULTS / "app"


def load_env() -> None:
    """Load environment variables from the repository ``.env`` file if it exists."""
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)


def anthropic_api_key() -> str:
    """Return the Anthropic API key from the environment.

    The key is read from ``ANTHROPIC_API_KEY``, loading the repository ``.env`` first. It is only
    needed for the LLM-powered app phase; the analysis pipeline never calls it.

    Returns:
        The API key.

    Raises:
        RuntimeError: If the key is not set, with guidance on how to obtain and store one.
    """
    load_env()
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to the repository .env file as\n"
            "    ANTHROPIC_API_KEY=your_key_here\n"
            "Obtain one at https://console.anthropic.com/"
        )
    return key
