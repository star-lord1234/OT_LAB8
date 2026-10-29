"""CLI-compatible Track B benchmark runner."""

from __future__ import annotations

from optlab.common.config import load_experiment_config

from ..implementation.experiment import run_experiment


def main(config_path: str) -> int:
    manifest = run_experiment(load_experiment_config(config_path))
    print(f"Track B generated {len(manifest['artifacts']) + 1} artifacts.")
    print(f"Classical Max-Cut optimum: {manifest['maxcut_classical_optimum']}")
    print(f"Track C fixture SHA-256: {manifest['track_c_fixture_sha256']}")
    print(f"Status: {manifest['status']}")
    print(f"Unresolved: {manifest['unresolved']}")
    return 0
