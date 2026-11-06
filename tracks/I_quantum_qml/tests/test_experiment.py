import csv
import json

from optlab.common.config import ExperimentConfig
from tracks.I_quantum_qml.implementation.experiment import run_experiment


def test_track_i_smoke_writes_traceable_simulation_evidence(tmp_path):
    config = ExperimentConfig.from_mapping({
        "track": "I",
        "experiment": "smoke",
        "repeats": 1,
        "base_seed": 11,
        "output_dir": str(tmp_path),
        "parameters": {
            "vqc_steps": 2,
            "samples_per_class": 6,
            "annealing_sweeps": 80,
            "grover_qubits": [2],
            "plateau_qubits": [2],
            "plateau_repeats": 2,
        },
    })
    manifest = run_experiment(config)
    expected = {
        "algorithm_results.csv",
        "shor_order_finding.json",
        "annealing_runs.csv",
        "grover_query_comparison.csv",
        "noise_model.csv",
        "dataset_split.csv",
        "qml_comparison.csv",
        "barren_plateau_proxy.csv",
        "cross_track_comparison.json",
        "coverage_checklist.csv",
        "circuit_diagrams.txt",
        "manifest.json",
    }
    assert expected.issubset({path.name for path in tmp_path.iterdir()})
    document = json.loads((tmp_path / "manifest.json").read_text())
    assert document["status"] == "verified_simulation_with_syllabus_gap"
    assert "no physical quantum" in document["result_type"]
    assert "Chapter 6" in document["unresolved"]
    with (tmp_path / "coverage_checklist.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert any(row["topic"] == "Shor" and row["status"] == "verified-compiled-simulation" for row in rows)
    assert any(row["status"] == "blocked-awaiting-syllabus" for row in rows)
    assert manifest["dataset_digest"]
