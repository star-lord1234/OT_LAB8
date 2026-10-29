"""CLI-compatible Track D runner."""

from __future__ import annotations

from optlab.common.config import load_experiment_config

from ..implementation.experiment import run_experiment


def main(config_path: str) -> int:
    manifest = run_experiment(load_experiment_config(config_path))
    print(f"Track D generated {len(manifest['artifacts'])} artifacts.")
    print(f"Maximum-coverage greedy/exact ratio: {manifest['submodular_observed_ratio']:.3f}")
    print(f"Negative parallel speedups retained: {manifest['parallel_negative_speedups_retained']}")
    print(f"Status: {manifest['status']}")
    print(f"Unresolved: {manifest['unresolved']}")
    return 0
