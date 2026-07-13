"""Unit tests for the AND-gate and NOT-gate pair-scoring logic.

Placeholder suite for the skeleton. As the scoring module lands under ``src/dual_marker_discovery/``
or ``scripts/``, replace the smoke test below with tests that assert:
  - AND score of a pair equals the per-cell fraction positive for both markers, per patient.
  - NOT score equals the fraction positive for the activator and negative for the blocker.
  - The known PSMA-PSCA pair scores above a random surface pair on a small synthetic AnnData.
  - Per-patient summarization is invariant to duplicating one patient's cells.
"""

from __future__ import annotations

from pathlib import Path


def test_repo_layout_present() -> None:
    """The core skeleton directories exist, so a fresh clone can run the pipeline."""
    repo = Path(__file__).resolve().parents[1]
    for sub in ("scripts", "results/tables", "reports", "src/dual_marker_discovery"):
        assert (repo / sub).is_dir(), f"missing expected directory: {sub}"
