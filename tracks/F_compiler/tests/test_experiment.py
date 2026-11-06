from __future__ import annotations

from optlab.common.config import ExperimentConfig
from tracks.F_compiler.implementation.experiment import run_experiment


def test_track_f_smoke_experiment_writes_complete_evidence(tmp_path) -> None:
    config = ExperimentConfig.from_mapping({
        "track": "F", "experiment": "smoke", "repeats": 1,
        "base_seed": 7, "output_dir": str(tmp_path),
        "parameters": {"execution_iterations": 20, "compilation_iterations": 10, "pass_effort_budget": 8},
    })
    manifest = run_experiment(config)
    assert manifest["all_semantically_equivalent"]
    assert manifest["pass_order_verified_exact"]
    assert len(manifest["passes"]) == 4
    assert (tmp_path / "pass_order_decision.json").is_file()
    assert (tmp_path / "plots" / "runtime_compile_time.png").is_file()
