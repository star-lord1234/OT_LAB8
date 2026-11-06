"""CLI-compatible Track J runner."""

from __future__ import annotations

from optlab.common.config import load_experiment_config

from ..implementation.experiment import run_experiment


def main(config_path: str) -> int:
    manifest = run_experiment(load_experiment_config(config_path))
    print(f"Track J generated {len(manifest['artifacts'])} artifacts.")
    print(f"Pinned source: {manifest['source_commit']}")
    print(f"Full suite passed: {manifest['full_suite_passed']} ({manifest['full_suite_tests']} tests)")
    print(f"Greedy line improvement under budget: {manifest['greedy_line_improvement']}")
    print(f"Status: {manifest['status']}")
    print(f"Claim limit: {manifest['claim_limit']}")
    return 0
