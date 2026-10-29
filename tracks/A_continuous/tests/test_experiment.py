import json

from optlab.common.config import ExperimentConfig
from tracks.A_continuous.implementation.experiment import run_experiment


def test_experiment_writes_complete_evidence_bundle(tmp_path):
    config = ExperimentConfig.from_mapping(
        {
            "track": "A",
            "experiment": "smoke",
            "repeats": 1,
            "base_seed": 9,
            "output_dir": str(tmp_path),
            "parameters": {"epochs": 8},
        }
    )
    manifest = run_experiment(config)
    expected = {
        "method_runs.csv",
        "method_summary.csv",
        "convergence.csv",
        "curvature.json",
        "backprop.json",
        "gradient_check.json",
        "landscapes.json",
        "manifest.json",
    }
    assert expected.issubset({path.name for path in tmp_path.iterdir()})
    assert set(manifest["methods"]) >= {"batch_gd", "adam", "newton", "gauss_newton", "bfgs"}
    result = json.loads((tmp_path / "gradient_check.json").read_text())
    assert result["maximum_absolute_error"] < 2e-6
