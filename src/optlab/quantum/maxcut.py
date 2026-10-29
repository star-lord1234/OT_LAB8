"""Track-B-compatible Max-Cut circuits and QAOA optimization helpers."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pennylane as qml
from pennylane import numpy as qnp


@dataclass(frozen=True)
class MaxCutProblem:
    vertices: int
    edges: tuple[tuple[int, int, float], ...]
    optimum_cut: float
    optimal_bitstrings: tuple[str, ...]
    fixture_sha256: str

    @property
    def uniform_expected_cut(self) -> float:
        return 0.5 * sum(weight for _, _, weight in self.edges)

    def cut_value(self, bits: Iterable[int]) -> float:
        state = tuple(int(bit) for bit in bits)
        return float(sum(weight for left, right, weight in self.edges if state[left] != state[right]))

    def cut_values(self) -> np.ndarray:
        return np.asarray([self.cut_value(map(int, format(index, f"0{self.vertices}b"))) for index in range(2**self.vertices)])


def load_maxcut_fixture(path: str | Path) -> MaxCutProblem:
    with Path(path).open(encoding="utf-8") as stream:
        document = json.load(stream)
    recorded = str(document["sha256_without_hash_field"])
    unhashed = dict(document)
    unhashed.pop("sha256_without_hash_field")
    canonical = json.dumps(unhashed, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(canonical).hexdigest() != recorded:
        raise ValueError("Track B Max-Cut fixture hash mismatch")
    return MaxCutProblem(
        int(document["vertices"]),
        tuple((int(edge["u"]), int(edge["v"]), float(edge["weight"])) for edge in document["edges"]),
        float(document["classical_optimum_cut"]),
        tuple(str(bits) for bits in document["optimal_bitstrings"]),
        recorded,
    )


def cost_hamiltonian(problem: MaxCutProblem) -> qml.Hamiltonian:
    constant = -0.5 * sum(weight for _, _, weight in problem.edges)
    coefficients = [constant] + [0.5 * weight for _, _, weight in problem.edges]
    operators = [qml.Identity(0)] + [qml.PauliZ(left) @ qml.PauliZ(right) for left, right, _ in problem.edges]
    return qml.Hamiltonian(coefficients, operators)


def apply_qaoa(problem: MaxCutProblem, parameters) -> None:
    for wire in range(problem.vertices):
        qml.Hadamard(wire)
    for gamma, beta in parameters:
        for left, right, weight in problem.edges:
            qml.MultiRZ(gamma * weight, wires=[left, right])
        for wire in range(problem.vertices):
            qml.RX(2.0 * beta, wires=wire)


def qaoa_qnodes(problem: MaxCutProblem, *, diff_method: str = "backprop"):
    device = qml.device("default.qubit", wires=problem.vertices)
    hamiltonian = cost_hamiltonian(problem)

    @qml.qnode(device, interface="autograd", diff_method=diff_method)
    def energy(parameters):
        apply_qaoa(problem, parameters)
        return qml.expval(hamiltonian)

    @qml.qnode(device)
    def probabilities(parameters):
        apply_qaoa(problem, parameters)
        return qml.probs(wires=range(problem.vertices))

    return energy, probabilities


def distribution_metrics(problem: MaxCutProblem, probabilities) -> dict[str, object]:
    values = problem.cut_values()
    probs = np.asarray(probabilities, dtype=float)
    most_likely_index = int(np.argmax(probs))
    most_likely_bits = format(most_likely_index, f"0{problem.vertices}b")
    optimal_probability = sum(float(probs[int(bits, 2)]) for bits in problem.optimal_bitstrings)
    expected_cut = float(probs @ values)
    return {
        "expected_cut": expected_cut,
        "approximation_ratio": expected_cut / problem.optimum_cut,
        "optimal_probability": optimal_probability,
        "most_likely_bitstring": most_likely_bits,
        "most_likely_cut": problem.cut_value(map(int, most_likely_bits)),
    }


def optimize_qaoa_adam(problem: MaxCutProblem, *, depth: int, seed: int, steps: int = 60, learning_rate: float = 0.08) -> dict[str, object]:
    energy, probabilities = qaoa_qnodes(problem)
    rng = np.random.default_rng(seed)
    parameters = qnp.array(rng.uniform(0.0, np.pi, size=(depth, 2)), requires_grad=True)
    optimizer = qml.AdamOptimizer(learning_rate)
    history = []
    started = time.perf_counter()
    for iteration in range(steps):
        parameters, previous = optimizer.step_and_cost(energy, parameters)
        history.append({"iteration": iteration, "energy": float(previous), "expected_cut": -float(previous)})
    final_energy = float(energy(parameters))
    history.append({"iteration": steps, "energy": final_energy, "expected_cut": -final_energy})
    metrics = distribution_metrics(problem, probabilities(parameters))
    resources = qml.specs(energy)(parameters)["resources"]
    return {
        "optimizer": "adam_autodiff_simulator",
        "depth": depth,
        "seed": seed,
        "steps": steps,
        "learning_rate": learning_rate,
        "parameters": np.asarray(parameters, dtype=float).tolist(),
        "energy": final_energy,
        **metrics,
        "runtime_seconds": time.perf_counter() - started,
        "simulator_objective_calls": steps + 1,
        "parameter_shift_hardware_evaluation_estimate": steps * (2 * parameters.size + 1),
        "gate_count": int(resources.num_gates),
        "circuit_depth": int(resources.depth),
        "history": history,
    }


def optimize_qaoa_spsa(problem: MaxCutProblem, *, depth: int, seed: int, steps: int = 80) -> dict[str, object]:
    energy, probabilities = qaoa_qnodes(problem, diff_method="best")
    rng = np.random.default_rng(seed)
    parameters = rng.uniform(0.0, np.pi, size=(depth, 2))
    history = []
    evaluations = 0
    started = time.perf_counter()
    for iteration in range(steps):
        a_k = 0.2 / (iteration + 11) ** 0.602
        c_k = 0.15 / (iteration + 1) ** 0.101
        delta = rng.choice((-1.0, 1.0), size=parameters.shape)
        plus = float(energy(parameters + c_k * delta))
        minus = float(energy(parameters - c_k * delta))
        evaluations += 2
        gradient = (plus - minus) * delta / (2.0 * c_k)
        parameters = parameters - a_k * gradient
        current = float(energy(parameters))
        evaluations += 1
        history.append({"iteration": iteration + 1, "energy": current, "expected_cut": -current})
    final_energy = float(energy(parameters))
    evaluations += 1
    return {
        "optimizer": "spsa",
        "depth": depth,
        "seed": seed,
        "steps": steps,
        "learning_rate": "a_k=0.2/(k+11)^0.602; c_k=0.15/(k+1)^0.101",
        "parameters": np.asarray(parameters).tolist(),
        "energy": final_energy,
        **distribution_metrics(problem, probabilities(parameters)),
        "runtime_seconds": time.perf_counter() - started,
        "simulator_objective_calls": evaluations,
        "parameter_shift_hardware_evaluation_estimate": None,
        "gate_count": 5 + depth * (len(problem.edges) + problem.vertices),
        "circuit_depth": 3 + 6 * depth,
        "history": history,
    }


def sample_qaoa(problem: MaxCutProblem, parameters, *, shots: int, seed: int) -> np.ndarray:
    device = qml.device("default.qubit", wires=problem.vertices, seed=seed)

    @qml.set_shots(shots)
    @qml.qnode(device)
    def sampler():
        apply_qaoa(problem, parameters)
        return qml.sample(wires=range(problem.vertices))

    return np.asarray(sampler(), dtype=int)


def noisy_qaoa_probabilities(problem: MaxCutProblem, parameters, *, single_qubit_error: float, two_qubit_error: float) -> np.ndarray:
    device = qml.device("default.mixed", wires=problem.vertices)

    @qml.qnode(device)
    def circuit():
        for wire in range(problem.vertices):
            qml.Hadamard(wire)
            if single_qubit_error:
                qml.DepolarizingChannel(single_qubit_error, wires=wire)
        for gamma, beta in parameters:
            for left, right, weight in problem.edges:
                qml.MultiRZ(gamma * weight, wires=[left, right])
                if two_qubit_error:
                    qml.DepolarizingChannel(two_qubit_error, wires=left)
                    qml.DepolarizingChannel(two_qubit_error, wires=right)
            for wire in range(problem.vertices):
                qml.RX(2.0 * beta, wires=wire)
                if single_qubit_error:
                    qml.DepolarizingChannel(single_qubit_error, wires=wire)
        return qml.probs(wires=range(problem.vertices))

    return np.asarray(circuit(), dtype=float)
