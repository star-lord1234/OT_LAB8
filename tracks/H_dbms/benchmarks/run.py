"""CLI-compatible Track H runner."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache" / "xdg"))

from optlab.common.config import load_experiment_config

from ..implementation.experiment import run_experiment


def main(config_path: str) -> int:
    manifest = run_experiment(load_experiment_config(config_path))
    print(f"Track H generated {len(manifest['artifacts']) + 1} artifacts.")
    print(f"Rows: {manifest['database_rows']}; candidates: {manifest['candidates']}; queries: {manifest['queries']}")
    print(f"Logical equivalence: {manifest['all_results_equivalent']}")
    print(f"All configurations within budget: {manifest['all_configurations_within_budget']}")
    print(f"Status: {manifest['status']}")
    return 0
