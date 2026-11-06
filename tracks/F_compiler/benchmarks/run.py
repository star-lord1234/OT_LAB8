"""CLI-compatible Track F runner."""

from __future__ import annotations

from optlab.common.config import load_experiment_config

from ..implementation.experiment import run_experiment


def main(config_path: str) -> int:
    manifest = run_experiment(load_experiment_config(config_path))
    print(f"Track F generated {len(manifest['artifacts'])} artifacts.")
    print(f"Programs: {len(manifest['programs'])}; passes: {len(manifest['passes'])}")
    print(f"Semantic equivalence: {manifest['all_semantically_equivalent']}")
    print(f"Pass-order exact verification: {manifest['pass_order_verified_exact']}")
    print(f"Status: {manifest['status']}")
    return 0
