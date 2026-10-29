"""CLI-compatible Track A runner registered by experiments/registry.json."""

from __future__ import annotations

from optlab.common.config import load_experiment_config

from ..implementation.experiment import run_experiment


def main(config_path: str) -> int:
    manifest = run_experiment(load_experiment_config(config_path))
    print(f"Track A generated {len(manifest['artifacts']) + 1} artifacts.")
    print(f"Status: {manifest['status']}")
    print(f"Unresolved: {manifest['unresolved']}")
    return 0
