from __future__ import annotations

import csv

from optlab.common.config import ExperimentConfig
from tracks.E_case_study.implementation.experiment import run_experiment


def test_track_e_smoke_experiment_writes_verified_evidence(tmp_path) -> None:
    config = ExperimentConfig.from_mapping({
        "track": "E", "experiment": "smoke", "repeats": 1,
        "base_seed": 7, "output_dir": str(tmp_path),
        "parameters": {
            "workload_sizes": [12], "arrival_rates": [0.8], "token_capacities": [384, 512],
            "max_batch_size": 4, "batch_window": 0.8, "max_batch_wait": 2.0,
        },
    })
    manifest = run_experiment(config)
    assert manifest["track"] == "E"
    assert manifest["all_runs_correct"]
    assert manifest["all_objective_checks_exact"]
    assert (tmp_path / "tiny_exact_reference.json").is_file()
    assert (tmp_path / "strategy_selection.csv").is_file()
    assert (tmp_path / "plots" / "latency_throughput_by_size.png").is_file()
    workloads = list(csv.DictReader((tmp_path / "workloads.csv").open()))
    assert len({row["sha256"] for row in workloads}) == 1
