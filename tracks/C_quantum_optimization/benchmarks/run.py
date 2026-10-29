"""CLI-compatible Track C runner."""

from __future__ import annotations

from optlab.common.config import load_experiment_config

from ..implementation.experiment import run_experiment


def main(config_path: str) -> int:
    manifest = run_experiment(load_experiment_config(config_path))
    print(f"Track C generated {len(manifest['artifacts'])} artifacts.")
    print(f"Simulation-only best QAOA expected cut: {manifest['best_qaoa_expected_cut']:.6f}")
    print(f"Track B exact optimum: {manifest['track_b_classical_optimum_cut']:.6f}")
    print(f"Status: {manifest['status']}")
    print(f"Unresolved: {manifest['unresolved']}")
    return 0
