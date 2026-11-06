"""Tiny, inspectable quantum-algorithm demonstrations shared by Track I.

Every routine uses a local PennyLane simulator.  The circuits are deliberately
small enough for a laptop and return correctness evidence rather than implying
physical-hardware performance.
"""

from __future__ import annotations

import math
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
import pennylane as qml

from .maxcut import MaxCutProblem, load_maxcut_fixture


def _resources(qnode, *arguments) -> tuple[int, int]:
    resources = qml.specs(qnode)(*arguments)["resources"]
    return int(resources.num_gates), int(resources.depth)


def deutsch_jozsa(*, oracle: str = "balanced", input_qubits: int = 2) -> dict[str, object]:
    """Hand-written Deutsch-Jozsa circuit for constant or parity-balanced f."""

    if oracle not in {"constant_zero", "constant_one", "balanced"}:
        raise ValueError("oracle must be constant_zero, constant_one, or balanced")
    if input_qubits < 1:
        raise ValueError("input_qubits must be positive")
    device = qml.device("default.qubit", wires=input_qubits + 1)
    ancilla = input_qubits

    @qml.qnode(device)
    def circuit():
        qml.PauliX(ancilla)
        for wire in range(input_qubits + 1):
            qml.Hadamard(wire)
        if oracle == "constant_one":
            qml.PauliX(ancilla)
        elif oracle == "balanced":
            for wire in range(input_qubits):
                qml.CNOT(wires=[wire, ancilla])
        for wire in range(input_qubits):
            qml.Hadamard(wire)
        return qml.probs(wires=range(input_qubits))

    started = time.perf_counter()
    probabilities = np.asarray(circuit(), dtype=float)
    runtime = time.perf_counter() - started
    gate_count, depth = _resources(circuit)
    zero_probability = float(probabilities[0])
    classification = "constant" if zero_probability > 1.0 - 1e-9 else "balanced"
    return {
        "algorithm": "Deutsch-Jozsa",
        "instance": f"{input_qubits} input qubits; {oracle}",
        "expected": "constant" if oracle.startswith("constant") else "balanced",
        "observed": classification,
        "success_probability": zero_probability if oracle.startswith("constant") else 1.0 - zero_probability,
        "query_count": 1,
        "gate_count": gate_count,
        "circuit_depth": depth,
        "runtime_seconds": runtime,
        "hand_written_circuit": True,
        "simulator": "PennyLane default.qubit",
    }


def bernstein_vazirani(secret: str = "101") -> dict[str, object]:
    """Hand-written Bernstein-Vazirani phase-kickback circuit."""

    if not secret or any(bit not in "01" for bit in secret):
        raise ValueError("secret must be a non-empty binary string")
    input_qubits = len(secret)
    ancilla = input_qubits
    device = qml.device("default.qubit", wires=input_qubits + 1)

    @qml.qnode(device)
    def circuit():
        qml.PauliX(ancilla)
        for wire in range(input_qubits + 1):
            qml.Hadamard(wire)
        for wire, bit in enumerate(secret):
            if bit == "1":
                qml.CNOT(wires=[wire, ancilla])
        for wire in range(input_qubits):
            qml.Hadamard(wire)
        return qml.probs(wires=range(input_qubits))

    started = time.perf_counter()
    probabilities = np.asarray(circuit(), dtype=float)
    runtime = time.perf_counter() - started
    observed = format(int(np.argmax(probabilities)), f"0{input_qubits}b")
    gate_count, depth = _resources(circuit)
    return {
        "algorithm": "Bernstein-Vazirani",
        "instance": f"secret={secret}",
        "expected": secret,
        "observed": observed,
        "success_probability": float(probabilities[int(secret, 2)]),
        "query_count": 1,
        "gate_count": gate_count,
        "circuit_depth": depth,
        "runtime_seconds": runtime,
        "hand_written_circuit": True,
        "simulator": "PennyLane default.qubit",
    }


def _multi_controlled_z(qubits: int) -> None:
    if qubits == 1:
        qml.PauliZ(0)
    else:
        qml.ctrl(qml.PauliZ, control=list(range(qubits - 1)))(wires=qubits - 1)


def apply_grover_oracle(target: str) -> None:
    """Phase-flip one computational basis target without an algorithm wrapper."""

    for wire, bit in enumerate(target):
        if bit == "0":
            qml.PauliX(wire)
    _multi_controlled_z(len(target))
    for wire, bit in enumerate(target):
        if bit == "0":
            qml.PauliX(wire)


def apply_grover_diffuser(qubits: int) -> None:
    for wire in range(qubits):
        qml.Hadamard(wire)
        qml.PauliX(wire)
    _multi_controlled_z(qubits)
    for wire in range(qubits):
        qml.PauliX(wire)
        qml.Hadamard(wire)


def grover_search(target: str, *, iterations: int | None = None) -> dict[str, object]:
    """Hand-written Grover oracle and diffuser for one marked state."""

    if len(target) < 2 or any(bit not in "01" for bit in target):
        raise ValueError("target must be a binary string of at least two bits")
    qubits = len(target)
    items = 2**qubits
    if iterations is None:
        iterations = max(1, int(math.floor(math.pi * math.sqrt(items) / 4.0)))
    device = qml.device("default.qubit", wires=qubits)

    @qml.qnode(device)
    def circuit():
        for wire in range(qubits):
            qml.Hadamard(wire)
        for _ in range(iterations):
            apply_grover_oracle(target)
            apply_grover_diffuser(qubits)
        return qml.probs(wires=range(qubits))

    started = time.perf_counter()
    probabilities = np.asarray(circuit(), dtype=float)
    runtime = time.perf_counter() - started
    observed = format(int(np.argmax(probabilities)), f"0{qubits}b")
    gate_count, depth = _resources(circuit)
    return {
        "algorithm": "Grover",
        "instance": f"N={items}; target={target}",
        "expected": target,
        "observed": observed,
        "success_probability": float(probabilities[int(target, 2)]),
        "query_count": iterations,
        "gate_count": gate_count,
        "circuit_depth": depth,
        "runtime_seconds": runtime,
        "hand_written_circuit": True,
        "simulator": "PennyLane default.qubit",
    }


def apply_qft(wires: tuple[int, ...] | list[int]) -> None:
    """Textbook QFT constructed from H, controlled phases, and swaps."""

    wires = tuple(wires)
    for position, target in enumerate(wires):
        qml.Hadamard(target)
        for offset, control in enumerate(wires[position + 1 :], start=1):
            qml.ControlledPhaseShift(np.pi / (2**offset), wires=[control, target])
    for index in range(len(wires) // 2):
        qml.SWAP(wires=[wires[index], wires[-index - 1]])


def qft_roundtrip(bitstring: str = "101") -> dict[str, object]:
    if not bitstring or any(bit not in "01" for bit in bitstring):
        raise ValueError("bitstring must be non-empty and binary")
    qubits = len(bitstring)
    device = qml.device("default.qubit", wires=qubits)

    @qml.qnode(device)
    def transformed():
        qml.BasisState(np.asarray([int(bit) for bit in bitstring]), wires=range(qubits))
        apply_qft(tuple(range(qubits)))
        return qml.state()

    @qml.qnode(device)
    def roundtrip():
        qml.BasisState(np.asarray([int(bit) for bit in bitstring]), wires=range(qubits))
        apply_qft(tuple(range(qubits)))
        qml.adjoint(apply_qft)(tuple(range(qubits)))
        return qml.probs(wires=range(qubits))

    started = time.perf_counter()
    state = np.asarray(transformed())
    probabilities = np.asarray(roundtrip(), dtype=float)
    runtime = time.perf_counter() - started
    expected_index = int(bitstring, 2)
    gate_count, depth = _resources(transformed)
    uniform_error = float(np.max(np.abs(np.abs(state) ** 2 - 1.0 / 2**qubits)))
    return {
        "algorithm": "Quantum Fourier Transform",
        "instance": f"{qubits}-qubit basis state |{bitstring}>",
        "expected": bitstring,
        "observed": format(int(np.argmax(probabilities)), f"0{qubits}b"),
        "success_probability": float(probabilities[expected_index]),
        "uniform_probability_max_error": uniform_error,
        "query_count": 0,
        "gate_count": gate_count,
        "circuit_depth": depth,
        "runtime_seconds": runtime,
        "hand_written_circuit": True,
        "simulator": "PennyLane default.qubit",
    }


def phase_estimation(*, phase: float = 0.25, counting_qubits: int = 3) -> dict[str, object]:
    """QPE for a PhaseShift eigenstate |1>, using the hand-written inverse QFT."""

    if not 0.0 <= phase < 1.0:
        raise ValueError("phase must lie in [0, 1)")
    if counting_qubits < 2:
        raise ValueError("counting_qubits must be at least two")
    target = counting_qubits
    counting = tuple(range(counting_qubits))
    device = qml.device("default.qubit", wires=counting_qubits + 1)

    @qml.qnode(device)
    def circuit():
        qml.PauliX(target)
        for wire in counting:
            qml.Hadamard(wire)
        for position, control in enumerate(counting):
            power = 2 ** (counting_qubits - position - 1)
            qml.ctrl(qml.PhaseShift, control=control)(2 * np.pi * phase * power, wires=target)
        qml.adjoint(apply_qft)(counting)
        return qml.probs(wires=counting)

    started = time.perf_counter()
    probabilities = np.asarray(circuit(), dtype=float)
    runtime = time.perf_counter() - started
    observed_index = int(np.argmax(probabilities))
    expected_index = int(round(phase * 2**counting_qubits)) % 2**counting_qubits
    gate_count, depth = _resources(circuit)
    return {
        "algorithm": "Quantum Phase Estimation",
        "instance": f"phase={phase}; counting_qubits={counting_qubits}",
        "expected": f"{expected_index / 2**counting_qubits:.6f}",
        "observed": f"{observed_index / 2**counting_qubits:.6f}",
        "success_probability": float(probabilities[expected_index]),
        "query_count": (2**counting_qubits) - 1,
        "gate_count": gate_count,
        "circuit_depth": depth,
        "runtime_seconds": runtime,
        "hand_written_circuit": True,
        "simulator": "PennyLane default.qubit",
    }


def _modular_multiplication_matrix(base: int, modulus: int) -> np.ndarray:
    qubits = math.ceil(math.log2(modulus))
    dimension = 2**qubits
    matrix = np.zeros((dimension, dimension), dtype=complex)
    for value in range(dimension):
        mapped = (base * value) % modulus if value < modulus else value
        matrix[mapped, value] = 1.0
    if not np.allclose(matrix.conj().T @ matrix, np.eye(dimension)):
        raise ValueError("base must be coprime to modulus so multiplication is unitary")
    return matrix


def shor_order_finding_15(*, base: int = 2, counting_qubits: int = 4) -> dict[str, object]:
    """Small Shor order finding for N=15 with matrix-compiled modular powers.

    This is a valid phase-estimation/order-finding circuit, but QubitUnitary
    hides the exponentially large modular-arithmetic matrix and is therefore
    not a scalable implementation of Shor's algorithm.
    """

    modulus = 15
    if math.gcd(base, modulus) != 1:
        raise ValueError("base must be coprime to 15")
    work_qubits = 4
    counting = tuple(range(counting_qubits))
    work = tuple(range(counting_qubits, counting_qubits + work_qubits))
    base_unitary = _modular_multiplication_matrix(base, modulus)
    device = qml.device("default.qubit", wires=counting_qubits + work_qubits)

    @qml.qnode(device)
    def circuit():
        qml.BasisState(np.asarray([0] * counting_qubits + [0, 0, 0, 1]), wires=range(counting_qubits + work_qubits))
        for wire in counting:
            qml.Hadamard(wire)
        for position, control in enumerate(counting):
            power = 2 ** (counting_qubits - position - 1)
            powered = np.linalg.matrix_power(base_unitary, power)
            qml.ctrl(qml.QubitUnitary, control=control)(powered, wires=work)
        qml.adjoint(apply_qft)(counting)
        return qml.probs(wires=counting)

    started = time.perf_counter()
    probabilities = np.asarray(circuit(), dtype=float)
    runtime = time.perf_counter() - started
    candidates: list[dict[str, object]] = []
    factors: set[int] = set()
    for index in np.argsort(probabilities)[::-1]:
        probability = float(probabilities[index])
        if probability < 1e-8 or index == 0:
            continue
        estimate = index / 2**counting_qubits
        fraction = Fraction(estimate).limit_denominator(modulus)
        order = fraction.denominator
        if order % 2 == 0 and pow(base, order, modulus) == 1:
            left = math.gcd(pow(base, order // 2) - 1, modulus)
            right = math.gcd(pow(base, order // 2) + 1, modulus)
            for factor in (left, right):
                if factor not in {1, modulus}:
                    factors.add(factor)
                    factors.add(modulus // factor)
            candidates.append({"phase_index": int(index), "probability": probability, "fraction": str(fraction), "order": order})
    gate_count, depth = _resources(circuit)
    observed_factors = sorted(factors)
    return {
        "algorithm": "Shor order finding",
        "instance": f"N=15; base={base}; {counting_qubits}+4 qubits",
        "expected": "[3, 5]",
        "observed": str(observed_factors),
        "success_probability": float(sum(row["probability"] for row in candidates)),
        "query_count": (2**counting_qubits) - 1,
        "gate_count": gate_count,
        "circuit_depth": depth,
        "runtime_seconds": runtime,
        "hand_written_circuit": False,
        "simulator": "PennyLane default.qubit",
        "factors": observed_factors,
        "phase_candidates": candidates,
        "limitation": "matrix-compiled modular multiplication; valid for N=15 but exponentially sized and not scalable",
    }


def simulated_quantum_annealing_proxy(
    fixture: str | Path,
    *,
    seed: int,
    sweeps: int = 1200,
    initial_temperature: float = 4.0,
    final_temperature: float = 0.02,
) -> dict[str, object]:
    """Classical Metropolis annealing on the Track B QUBO; no quantum hardware."""

    problem: MaxCutProblem = load_maxcut_fixture(fixture)
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, size=problem.vertices)
    current = problem.cut_value(bits)
    best_bits = bits.copy()
    best = current
    accepted = 0
    started = time.perf_counter()
    for step in range(sweeps):
        fraction = step / max(1, sweeps - 1)
        temperature = initial_temperature * (final_temperature / initial_temperature) ** fraction
        wire = int(rng.integers(problem.vertices))
        proposal = bits.copy()
        proposal[wire] = 1 - proposal[wire]
        candidate = problem.cut_value(proposal)
        delta = candidate - current
        if delta >= 0 or rng.random() < math.exp(delta / temperature):
            bits, current = proposal, candidate
            accepted += 1
        if current > best:
            best_bits, best = bits.copy(), current
    return {
        "algorithm": "annealing proxy",
        "seed": seed,
        "sweeps": sweeps,
        "best_bitstring": "".join(map(str, best_bits)),
        "best_cut": float(best),
        "exact_cut": problem.optimum_cut,
        "optimality_gap": float(problem.optimum_cut - best),
        "accepted_moves": accepted,
        "runtime_seconds": time.perf_counter() - started,
        "method": "classical simulated annealing over a QUBO/Ising objective",
        "physical_quantum_annealer": False,
        "limitation": "does not model tunnelling, device topology, calibration, or physical annealing dynamics",
    }


def noisy_grover_success(
    target: str = "11", *, single_qubit_error: float, two_qubit_error: float
) -> float:
    """Two-qubit Grover under a gate-local depolarizing density-matrix model."""

    if len(target) != 2 or any(bit not in "01" for bit in target):
        raise ValueError("the noise demonstration uses exactly two target bits")
    device = qml.device("default.mixed", wires=2)

    def one_qubit(operation, wire: int) -> None:
        operation(wires=wire)
        if single_qubit_error:
            qml.DepolarizingChannel(single_qubit_error, wires=wire)

    def entangler() -> None:
        qml.CZ(wires=[0, 1])
        if two_qubit_error:
            qml.DepolarizingChannel(two_qubit_error, wires=0)
            qml.DepolarizingChannel(two_qubit_error, wires=1)

    @qml.qnode(device)
    def circuit():
        for wire in range(2):
            one_qubit(qml.Hadamard, wire)
        for wire, bit in enumerate(target):
            if bit == "0":
                one_qubit(qml.PauliX, wire)
        entangler()
        for wire, bit in enumerate(target):
            if bit == "0":
                one_qubit(qml.PauliX, wire)
        for wire in range(2):
            one_qubit(qml.Hadamard, wire)
            one_qubit(qml.PauliX, wire)
        entangler()
        for wire in range(2):
            one_qubit(qml.PauliX, wire)
            one_qubit(qml.Hadamard, wire)
        return qml.probs(wires=[0, 1])

    return float(np.asarray(circuit())[int(target, 2)])


def algorithm_circuits() -> dict[str, str]:
    """Return diagrams of representative circuits without executing benchmarks."""

    diagrams: dict[str, str] = {}

    dj_device = qml.device("default.qubit", wires=3)

    @qml.qnode(dj_device)
    def dj():
        qml.PauliX(2)
        for wire in range(3):
            qml.Hadamard(wire)
        qml.CNOT(wires=[0, 2])
        qml.CNOT(wires=[1, 2])
        qml.Hadamard(0)
        qml.Hadamard(1)
        return qml.probs(wires=[0, 1])

    grover_device = qml.device("default.qubit", wires=2)

    @qml.qnode(grover_device)
    def grover():
        qml.Hadamard(0)
        qml.Hadamard(1)
        apply_grover_oracle("10")
        apply_grover_diffuser(2)
        return qml.probs(wires=[0, 1])

    qft_device = qml.device("default.qubit", wires=3)

    @qml.qnode(qft_device)
    def qft_circuit():
        qml.BasisState(np.asarray([1, 0, 1]), wires=[0, 1, 2])
        apply_qft((0, 1, 2))
        return qml.state()

    diagrams["Deutsch-Jozsa (hand-written)"] = qml.draw(dj)()
    diagrams["Grover (hand-written oracle and diffuser)"] = qml.draw(grover)()
    diagrams["QFT (hand-written primitive gates)"] = qml.draw(qft_circuit)()
    return diagrams
