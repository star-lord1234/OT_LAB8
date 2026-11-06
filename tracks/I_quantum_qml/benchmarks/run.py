"""CLI-compatible Track I benchmark runner."""

from __future__ import annotations

from optlab.common.config import load_experiment_config

from ..implementation.experiment import run_experiment


def main(config_path: str) -> int:
    manifest = run_experiment(load_experiment_config(config_path))
    print(f"Track I generated {len(manifest['artifacts'])} artifacts.")
    print(f"Simulation-only mean VQC accuracy: {manifest['mean_vqc_accuracy']:.3f}")
    print(f"Simulation-only mean quantum-kernel accuracy: {manifest['mean_quantum_kernel_accuracy']:.3f}")
    print(f"Status: {manifest['status']}")
    print(f"Unresolved: {manifest['unresolved']}")
    return 0
