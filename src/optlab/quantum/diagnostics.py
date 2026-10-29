"""Small, explicitly limited quantum scaling and embedding diagnostics."""

from __future__ import annotations

from itertools import product

import numpy as np
import pennylane as qml


def barren_plateau_proxy(*, qubit_counts=(2, 4, 6, 8, 10), repeats: int = 32, seed: int = 17, layers: int = 2) -> list[dict[str, float | int]]:
    """Measure one parameter's gradient variance for global and local costs.

    This is a finite-size proxy only, not evidence of asymptotic scaling.
    """

    results = []
    seed_sequence = np.random.SeedSequence(seed)
    for qubits, child in zip(qubit_counts, seed_sequence.spawn(len(qubit_counts))):
        device = qml.device("default.qubit", wires=qubits)

        @qml.qnode(device)
        def circuit(parameters):
            for layer in range(layers):
                for wire in range(qubits):
                    qml.RY(parameters[layer, wire], wires=wire)
                for wire in range(qubits):
                    qml.CZ(wires=[wire, (wire + 1) % qubits])
            return qml.expval(qml.prod(*(qml.PauliZ(wire) for wire in range(qubits)))), qml.expval(qml.PauliZ(0))

        rng = np.random.default_rng(child)
        global_gradients, local_gradients = [], []
        for _ in range(repeats):
            parameters = rng.uniform(-np.pi, np.pi, size=(layers, qubits))
            plus, minus = parameters.copy(), parameters.copy()
            plus[0, 0] += np.pi / 2
            minus[0, 0] -= np.pi / 2
            gradient = 0.5 * (np.asarray(circuit(plus)) - np.asarray(circuit(minus)))
            global_gradients.append(float(gradient[0]))
            local_gradients.append(float(gradient[1]))
        results.append({
            "qubits": qubits,
            "layers": layers,
            "repeats": repeats,
            "global_mean_absolute_gradient": float(np.mean(np.abs(global_gradients))),
            "global_gradient_variance": float(np.var(global_gradients)),
            "local_mean_absolute_gradient": float(np.mean(np.abs(local_gradients))),
            "local_gradient_variance": float(np.var(local_gradients)),
            "simulated": True,
        })
    return results


def embedding_chain_strength_demo(strengths=(0.25, 1.0, 3.0)) -> list[dict[str, object]]:
    """Embed logical K3 in a four-node square using one two-qubit chain."""

    rows = []
    for strength in strengths:
        states = []
        for spins in product((-1, 1), repeat=4):
            # logical A -> chain (q0,q1), B -> q2, C -> q3
            problem_energy = spins[1] * spins[2] + spins[0] * spins[3] + spins[2] * spins[3]
            chain_energy = -strength * spins[0] * spins[1]
            states.append((problem_energy + chain_energy, spins, spins[0] == spins[1]))
        ground = min(energy for energy, _, _ in states)
        ground_states = [state for state in states if np.isclose(state[0], ground)]
        unbroken = sum(int(state[2]) for state in ground_states)
        rows.append({
            "chain_strength": strength,
            "physical_ground_energy": ground,
            "ground_state_count": len(ground_states),
            "unbroken_ground_states": unbroken,
            "broken_chain_fraction": 1.0 - unbroken / len(ground_states),
            "logical_optimum_cut": 2,
            "embedding": "logical A=[q0,q1], B=[q2], C=[q3] on square q0-q1-q2-q3-q0",
            "simulated": True,
        })
    return rows
