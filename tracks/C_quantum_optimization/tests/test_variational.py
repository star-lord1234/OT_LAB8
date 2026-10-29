import numpy as np

from optlab.quantum.variational import (
    classical_qnn_baseline,
    exact_vqe_ground_energy,
    optimize_qnn,
    optimize_vqe,
    parameter_shift_demo,
)


def test_parameter_shift_matches_analytic_and_finite_difference_gradients():
    result = parameter_shift_demo()
    assert result["parameter_shift_absolute_error"] < 1e-12
    assert result["finite_difference_absolute_error"] < 1e-9


def test_qng_vqe_matches_classical_diagonalization():
    result = optimize_vqe("quantum_natural_gradient", seed=3, steps=60)
    assert np.isclose(result["exact_ground_energy"], exact_vqe_ground_energy())
    assert result["absolute_error"] < 1e-5


def test_minimal_qnn_and_classical_baseline_classify_tiny_dataset():
    quantum = optimize_qnn(seed=3, steps=60)
    classical = classical_qnn_baseline()
    assert quantum["accuracy"] == 1.0
    assert quantum["final_loss"] < 0.05
    assert classical["accuracy"] == 1.0
