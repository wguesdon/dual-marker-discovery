"""Shared pytest fixtures and helpers for the dual-marker-discovery test suite.

The pipeline scripts in ``scripts/`` are numbered standalone files, not an importable package.
They are loaded here by file path with :mod:`importlib` and cached, so a script is only executed
once per test session. This mirrors the layout used in the SatMut project.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
TABLES = REPO / "results" / "tables"
APP = REPO / "results" / "app"

_MODULE_CACHE: dict[str, ModuleType] = {}


def load_script(filename: str, module_name: str) -> ModuleType:
    """Import a numbered pipeline script by file path.

    Numbered scripts (e.g. ``30_score_pairs.py``) are not valid Python module names and are not
    packaged, so they cannot be imported with a normal ``import`` statement. This loads them from
    their file path and caches the result.

    Args:
        filename: Script file name relative to the ``scripts/`` directory.
        module_name: A safe module name to register the loaded module under.

    Returns:
        The executed module object.
    """
    if module_name in _MODULE_CACHE:
        return _MODULE_CACHE[module_name]
    path = SCRIPTS / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"could not build import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    # Register before executing so any self-references during module execution resolve.
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    _MODULE_CACHE[module_name] = module
    return module


@pytest.fixture(scope="session")
def repo_paths() -> dict[str, Path]:
    """Absolute paths to the repository's key directories and files under test."""
    return {
        "repo": REPO,
        "scripts": SCRIPTS,
        "tables": TABLES,
        "app": APP,
        "report_qmd": REPO / "reports" / "report.qmd",
    }
