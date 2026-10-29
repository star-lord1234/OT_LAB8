import numpy as np
import pennylane as qml

from optlab.quantum.maxcut import (
    cost_hamiltonian,
    distribution_metrics,
    load_maxcut_fixture,
    noisy_qaoa_probabilities,
    optimize_qaoa_adam,
    qaoa_qnodes,
)
from tracks.C_quantum_optimization.implementation.experiment import FIXTURE


def test_track_b_fixture_is_loaded_without_modification():
    problem = load_maxcut_fixture(FIXTURE)
    assert problem.vertices == 5
    assert problem.optimum_cut == 8.0
    assert problem.fixture_sha256 == "baf60a299f2a2be478511dd30f8de470621aee8103b1e16424912b1cab90a530"


def test_cost_hamiltonian_equals_negative_cut_on_every_basis_state():
    problem = load_maxcut_fixture(FIXTURE)
    hamiltonian = cost_hamiltonian(problem)
    device = qml.device("default.qubit", wires=problem.vertices)

    @qml.qnode(device)
    def basis_energy(bits):
        qml.BasisState(np.asarray(bits), wires=range(problem.vertices))
        return qml.expval(hamiltonian)

    for index in range(2**problem.vertices):
        bits = tuple(map(int, format(index, "05b")))
        assert np.isclose(basis_energy(bits), -problem.cut_value(bits))


def test_qaoa_probabilities_are_valid_and_bounded_by_exact_optimum():
    problem = load_maxcut_fixture(FIXTURE)
    run = optimize_qaoa_adam(problem, depth=1, seed=7, steps=5)
    assert 0 <= run["expected_cut"] <= problem.optimum_cut + 1e-9
    assert 0 <= run["optimal_probability"] <= 1
    _, probabilities = qaoa_qnodes(problem)
    probs = probabilities(np.asarray(run["parameters"]))
    assert np.isclose(np.sum(probs), 1.0)
    assert np.isclose(distribution_metrics(problem, probs)["expected_cut"], run["expected_cut"])


def test_noisy_simulator_distribution_is_normalized():
    problem = load_maxcut_fixture(FIXTURE)
    parameters = np.asarray([[0.3, 0.2]])
    probabilities = noisy_qaoa_probabilities(problem, parameters, single_qubit_error=0.001, two_qubit_error=0.01)
    assert probabilities.shape == (32,)
    assert np.isclose(probabilities.sum(), 1.0)
    assert np.all(probabilities >= 0)
