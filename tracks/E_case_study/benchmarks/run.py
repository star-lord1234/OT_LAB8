"""CLI-compatible Track E runner."""

from __future__ import annotations

from optlab.common.config import load_experiment_config

from ..implementation.experiment import run_experiment


def main(config_path: str) -> int:
    manifest = run_experiment(load_experiment_config(config_path))
    print(f"Track E generated {len(manifest['artifacts'])} artifacts.")
    print(manifest["result_type"])
    print(f"All schedule checks passed: {manifest['all_runs_correct']}")
    print(f"Status: {manifest['status']}")
    return 0
