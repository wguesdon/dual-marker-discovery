"""Write the curated cell-surface marker panel to a committed table.

The panel is defined once in :mod:`dual_marker_discovery.panel`. This script materializes it
as ``results/tables/surface_panel.csv``, the single source of truth that the data fetch reads
to subset both the tumor cohort and the healthy reference to the same genes.

Run:
    uv run python scripts/01_curate_surface_panel.py
"""

from __future__ import annotations

from dual_marker_discovery.config import RESULTS_TABLES
from dual_marker_discovery.panel import POSITIVE_CONTROL_PAIR, panel_frame


def main() -> None:
    """Materialize the surface panel table and print a short summary."""
    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    df = panel_frame()
    out = RESULTS_TABLES / "surface_panel.csv"
    df.to_csv(out, index=False)

    print(f"Wrote {out} with {len(df)} markers.")
    print("\nMarkers by category:")
    print(df["category"].value_counts().to_string())
    print("\nMarkers by compartment:")
    print(df["compartment"].value_counts().to_string())
    pc = df.loc[df["positive_control"], "gene"].tolist()
    print(f"\nPositive-control pair: {POSITIVE_CONTROL_PAIR}  (flagged genes: {pc})")


if __name__ == "__main__":
    main()
