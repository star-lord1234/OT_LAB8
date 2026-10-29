from __future__ import annotations

from optlab.common.config import ExperimentConfig
from tracks.D_parallel_distributed.implementation.experiment import run_experiment


def test_track_d_smoke_experiment_writes_complete_evidence(tmp_path) -> None:
    config = ExperimentConfig.from_mapping({
        "track": "D", "experiment": "smoke", "repeats": 1,
        "base_seed": 7, "output_dir": str(tmp_path),
        "parameters": {"workload_scale": 1, "multitask_epochs": 10},
    })
    manifest = run_experiment(config)
    assert manifest["track"] == "D"
    assert manifest["submodular_exact_verified"]
    assert manifest["parallel_forms_max_error"] < 1e-10
    assert (tmp_path / "work_stealing_simulation.json").is_file()
    assert (tmp_path / "plots" / "multitask_comparison.png").is_file()
    assert len(manifest["artifacts"]) == 20
