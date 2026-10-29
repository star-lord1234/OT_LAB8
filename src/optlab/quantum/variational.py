"""Small VQE, QNG, parameter-shift, and QNN demonstrations."""

from __future__ import annotations

import time

import numpy as np
import pennylane as qml
from pennylane import numpy as qnp
from scipy.optimize import minimize


def parameter_shift_demo(theta: float = 0.432) -> dict[str, float]:
    device = qml.device("default.qubit", wires=1)

    @qml.qnode(device)
    def expectation(angle):
        qml.RY(angle, wires=0)
        return qml.expval(qml.PauliZ(0))

    shifted = 0.5 * (float(expectation(theta + np.pi / 2)) - float(expectation(theta - np.pi / 2)))
    epsilon = 1e-6
    finite = (float(expectation(theta + epsilon)) - float(expectation(theta - epsilon))) / (2 * epsilon)
    analytic = -np.sin(theta)
    return {
        "theta": theta,
        "expectation": float(expectation(theta)),
        "parameter_shift_gradient": shifted,
        "finite_difference_gradient": finite,
        "analytic_gradient": float(analytic),
        "parameter_shift_absolute_error": abs(shifted - analytic),
        "finite_difference_absolute_error": abs(finite - analytic),
        "circuit_evaluations_parameter_shift": 2,
    }


def vqe_hamiltonian() -> qml.Hamiltonian:
    return 0.5 * qml.PauliZ(0) + 0.7 * qml.PauliZ(1) + 0.3 * (qml.PauliX(0) @ qml.PauliX(1)) + 0.2 * (qml.PauliZ(0) @ qml.PauliZ(1))


def apply_vqe_ansatz(parameters) -> None:
    qml.RY(parameters[0], wires=0)
    qml.RY(parameters[1], wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RY(parameters[2], wires=0)
    qml.RY(parameters[3], wires=1)


def vqe_qnode():
    device = qml.device("default.qubit", wires=2)
    hamiltonian = vqe_hamiltonian()

    @qml.qnode(device, interface="autograd", diff_method="backprop")
    def energy(parameters):
        apply_vqe_ansatz(parameters)
        return qml.expval(hamiltonian)

    return energy


def exact_vqe_ground_energy() -> float:
    return float(np.linalg.eigvalsh(qml.matrix(vqe_hamiltonian())).min())


def optimize_vqe(method: str, *, seed: int, steps: int = 70, learning_rate: float = 0.15) -> dict[str, object]:
    if method not in {"gradient_descent", "quantum_natural_gradient"}:
        raise ValueError(method)
    energy = vqe_qnode()
    parameters = qnp.array(np.random.default_rng(seed).normal(0.0, 0.3, size=4), requires_grad=True)
    optimizer = qml.GradientDescentOptimizer(learning_rate) if method == "gradient_descent" else qml.QNGOptimizer(learning_rate, approx="block-diag", lam=1e-3)
    history = []
    started = time.perf_counter()
    for iteration in range(steps):
        parameters, previous = optimizer.step_and_cost(energy, parameters)
        history.append({"iteration": iteration, "energy": float(previous)})
    final = float(energy(parameters))
    history.append({"iteration": steps, "energy": final})
    exact = exact_vqe_ground_energy()
    return {
        "method": method,
        "seed": seed,
        "steps": steps,
        "learning_rate": learning_rate,
        "parameters": np.asarray(parameters).tolist(),
        "final_energy": final,
        "exact_ground_energy": exact,
        "absolute_error": abs(final - exact),
        "runtime_seconds": time.perf_counter() - started,
        "history": history,
    }


QNN_FEATURES = np.asarray([[-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]])
QNN_LABELS = np.asarray([-1.0, -1.0, 1.0, 1.0])


def qnn_qnode():
    device = qml.device("default.qubit", wires=2)

    @qml.qnode(device, interface="autograd", diff_method="parameter-shift")
    def circuit(weights, features):
        qml.RY(features[0], wires=0)
        qml.RY(features[1], wires=1)
        qml.CNOT(wires=[0, 1])
        qml.RY(weights[0], wires=0)
        qml.RY(weights[1], wires=1)
        qml.CNOT(wires=[1, 0])
        qml.RY(weights[2], wires=0)
        return qml.expval(qml.PauliZ(0))

    return circuit


def optimize_qnn(*, seed: int, steps: int = 60) -> dict[str, object]:
    circuit = qnn_qnode()
    features = qnp.array(QNN_FEATURES, requires_grad=False)
    labels = qnp.array(QNN_LABELS, requires_grad=False)

    def loss(weights):
        predictions = qnp.stack([circuit(weights, row) for row in features])
        return qnp.mean((predictions - labels) ** 2)

    weights = qnp.array(np.random.default_rng(seed).normal(0.0, 0.2, size=3), requires_grad=True)
    optimizer = qml.AdamOptimizer(0.1)
    history = []
    started = time.perf_counter()
    for iteration in range(steps):
        weights, previous = optimizer.step_and_cost(loss, weights)
        history.append({"iteration": iteration, "loss": float(previous)})
    predictions = np.asarray([circuit(weights, row) for row in features], dtype=float)
    final_loss = float(np.mean((predictions - QNN_LABELS) ** 2))
    return {
        "method": "two_qubit_qnn_parameter_shift_adam",
        "seed": seed,
        "steps": steps,
        "weights": np.asarray(weights).tolist(),
        "predictions": predictions.tolist(),
        "final_loss": final_loss,
        "accuracy": float(np.mean(np.where(predictions >= 0, 1.0, -1.0) == QNN_LABELS)),
        "runtime_seconds": time.perf_counter() - started,
        "history": history + [{"iteration": steps, "loss": final_loss}],
    }


def classical_qnn_baseline() -> dict[str, object]:
    started = time.perf_counter()

    def loss(parameters):
        predictions = np.tanh(QNN_FEATURES @ parameters[:2] + parameters[2])
        return float(np.mean((predictions - QNN_LABELS) ** 2))

    result = minimize(loss, np.zeros(3), method="BFGS")
    predictions = np.tanh(QNN_FEATURES @ result.x[:2] + result.x[2])
    return {
        "method": "classical_tanh_linear_bfgs",
        "final_loss": loss(result.x),
        "accuracy": float(np.mean(np.where(predictions >= 0, 1.0, -1.0) == QNN_LABELS)),
        "runtime_seconds": time.perf_counter() - started,
        "parameters": result.x.tolist(),
        "success": bool(result.success),
    }
