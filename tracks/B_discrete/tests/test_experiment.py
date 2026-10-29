import csv
import json

from optlab.common.config import ExperimentConfig
from tracks.B_discrete.implementation.experiment import run_experiment


def test_track_b_experiment_writes_verified_evidence(tmp_path):
    config = ExperimentConfig.from_mapping({
        "track": "B",
        "experiment": "smoke",
        "repeats": 1,
        "base_seed": 5,
        "output_dir": str(tmp_path),
        "parameters": {},
    })
    manifest = run_experiment(config)
    expected = {
        "knapsack_runs.csv",
        "knapsack_summary.csv",
        "knapsack_references.csv",
        "maxcut_energies.csv",
        "maxcut_track_c_fixture.json",
        "penalty_sweep.csv",
        "manifest.json",
    }
    assert expected.issubset({path.name for path in tmp_path.iterdir()})
    rows = list(csv.DictReader((tmp_path / "knapsack_runs.csv").open()))
    assert len(rows) == 3 * 4
    assert all(row["feasible"] == "True" for row in rows)
    fixture = json.loads((tmp_path / "maxcut_track_c_fixture.json").read_text())
    assert fixture["classical_optimum_cut"] == 8.0
    assert manifest["safe_penalty_demonstrated"] is True
