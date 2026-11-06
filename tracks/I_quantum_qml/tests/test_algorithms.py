from pathlib import Path

import numpy as np

from optlab.quantum.algorithms import (
    bernstein_vazirani,
    deutsch_jozsa,
    grover_search,
    phase_estimation,
    qft_roundtrip,
    shor_order_finding_15,
    simulated_quantum_annealing_proxy,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tracks" / "B_discrete" / "results" / "maxcut_track_c_fixture.json"


def test_deutsch_jozsa_distinguishes_constant_and_balanced_oracles():
    constant = deutsch_jozsa(oracle="constant_one", input_qubits=2)
    balanced = deutsch_jozsa(oracle="balanced", input_qubits=2)
    assert constant["observed"] == "constant"
    assert balanced["observed"] == "balanced"
    assert np.isclose(constant["success_probability"], 1.0)
    assert np.isclose(balanced["success_probability"], 1.0)
    assert constant["hand_written_circuit"] is True


def test_bernstein_vazirani_recovers_secret_in_one_oracle_query():
    result = bernstein_vazirani("101")
    assert result["observed"] == "101"
    assert result["query_count"] == 1
    assert result["success_probability"] > 1.0 - 1e-9


def test_hand_written_grover_marks_target():
    result = grover_search("10")
    assert result["observed"] == "10"
    assert result["query_count"] == 1
    assert result["success_probability"] > 1.0 - 1e-9


def test_qft_roundtrip_is_identity_and_transform_is_uniform():
    result = qft_roundtrip("101")
    assert result["observed"] == "101"
    assert result["success_probability"] > 1.0 - 1e-9
    assert result["uniform_probability_max_error"] < 1e-12


def test_phase_estimation_recovers_exact_binary_phase():
    result = phase_estimation(phase=0.25, counting_qubits=3)
    assert result["observed"] == "0.250000"
    assert result["success_probability"] > 1.0 - 1e-9


def test_small_shor_order_finding_recovers_factors_and_discloses_compilation():
    result = shor_order_finding_15()
    assert result["factors"] == [3, 5]
    assert result["success_probability"] >= 0.49
    assert "matrix-compiled" in result["limitation"]


def test_annealing_proxy_uses_unchanged_track_b_fixture_and_exact_reference():
    result = simulated_quantum_annealing_proxy(FIXTURE, seed=7, sweeps=1000)
    assert result["exact_cut"] == 8.0
    assert result["best_cut"] <= result["exact_cut"]
    assert result["optimality_gap"] >= 0.0
    assert result["physical_quantum_annealer"] is False
