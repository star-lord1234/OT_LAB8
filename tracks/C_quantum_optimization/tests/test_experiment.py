import json

from optlab.common.config import ExperimentConfig
from tracks.C_quantum_optimization.implementation.experiment import run_experiment


def test_track_c_smoke_experiment_writes_cross_track_evidence(tmp_path):
    config = ExperimentConfig.from_mapping({
        "track": "C",
        "experiment": "smoke",
        "repeats": 1,
        "base_seed": 11,
        "output_dir": str(tmp_path),
        "parameters": {
            "qaoa_steps": 2,
            "spsa_steps": 2,
            "vqe_steps": 3,
            "qnn_steps": 3,
            "shot_repeats": 2,
            "plateau_repeats": 3,
            "depths": [1],
        },
    })
    manifest = run_experiment(config)
    expected = {
        "qaoa_runs.csv",
        "qaoa_best.json",
        "vqe_runs.csv",
        "qnn_runs.csv",
        "parameter_shift.json",
        "finite_shots_summary.csv",
        "noise_simulation.csv",
        "barren_plateau_proxy.csv",
        "embedding_chain_strength.csv",
        "circuit_diagrams.txt",
        "manifest.json",
    }
    assert expected.issubset({path.name for path in tmp_path.iterdir()})
    document = json.loads((tmp_path / "manifest.json").read_text())
    assert document["track_b_fixture_sha256"] == manifest["track_b_fixture_sha256"]
    assert "no physical quantum hardware" in document["result_type"]
