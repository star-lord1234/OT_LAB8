"""Weighted Max-Cut QUBO/Ising derivation and constrained QUBO example."""

from __future__ import annotations

import hashlib
import json
from itertools import product
from typing import Iterable

import numpy as np


EDGES: tuple[tuple[int, int, float], ...] = (
    (0, 1, 1.0),
    (0, 2, 1.5),
    (1, 2, 0.5),
    (1, 3, 2.0),
    (2, 3, 1.0),
    (2, 4, 2.5),
    (3, 4, 1.5),
)
VERTICES = 5


def cut_value(bits: Iterable[int], edges=EDGES) -> float:
    state = tuple(int(bit) for bit in bits)
    return float(sum(weight for left, right, weight in edges if state[left] != state[right]))


def maxcut_qubo(vertices: int = VERTICES, edges=EDGES) -> np.ndarray:
    """Return symmetric Q for minimizing x^T Q x = -cut(x)."""

    matrix = np.zeros((vertices, vertices), dtype=float)
    for left, right, weight in edges:
        matrix[left, left] -= weight
        matrix[right, right] -= weight
        matrix[left, right] += weight
        matrix[right, left] += weight
    return matrix


def qubo_energy(bits: Iterable[int], matrix: np.ndarray | None = None, offset: float = 0.0) -> float:
    vector = np.asarray(tuple(bits), dtype=float)
    q = maxcut_qubo() if matrix is None else np.asarray(matrix, dtype=float)
    return float(offset + vector @ q @ vector)


def binary_to_spin(bits: Iterable[int]) -> tuple[int, ...]:
    return tuple(2 * int(bit) - 1 for bit in bits)


def maxcut_ising(vertices: int = VERTICES, edges=EDGES) -> tuple[float, np.ndarray, np.ndarray]:
    """Return offset, h, J for E(s)=offset+h.s+sum(i<j)Jij si sj."""

    offset = -0.5 * sum(weight for _, _, weight in edges)
    linear = np.zeros(vertices, dtype=float)
    coupling = np.zeros((vertices, vertices), dtype=float)
    for left, right, weight in edges:
        coupling[left, right] = coupling[right, left] = 0.5 * weight
    return float(offset), linear, coupling


def ising_energy(spins: Iterable[int], offset: float, linear: np.ndarray, coupling: np.ndarray) -> float:
    state = np.asarray(tuple(spins), dtype=float)
    pair = sum(coupling[left, right] * state[left] * state[right] for left in range(len(state)) for right in range(left + 1, len(state)))
    return float(offset + linear @ state + pair)


def enumerate_maxcut() -> list[dict[str, object]]:
    q = maxcut_qubo()
    offset, linear, coupling = maxcut_ising()
    rows = []
    for bits in product((0, 1), repeat=VERTICES):
        spins = binary_to_spin(bits)
        rows.append({
            "bits": "".join(map(str, bits)),
            "spins": " ".join(f"{spin:+d}" for spin in spins),
            "cut_value": cut_value(bits),
            "negative_cut": -cut_value(bits),
            "qubo_energy": qubo_energy(bits, q),
            "ising_energy": ising_energy(spins, offset, linear, coupling),
        })
    return rows


def make_track_c_fixture() -> dict[str, object]:
    q = maxcut_qubo()
    offset, linear, coupling = maxcut_ising()
    rows = enumerate_maxcut()
    optimum = max(float(row["cut_value"]) for row in rows)
    optimal_bits = [str(row["bits"]) for row in rows if float(row["cut_value"]) == optimum]
    fixture: dict[str, object] = {
        "fixture_version": 1,
        "problem": "weighted_max_cut",
        "bit_order": "left-to-right characters are x_0 through x_4; s_i=2*x_i-1",
        "vertices": VERTICES,
        "edges": [{"u": u, "v": v, "weight": w} for u, v, w in EDGES],
        "optimization": "maximize cut_value; equivalently minimize QUBO/Ising energy=-cut_value",
        "qubo_convention": "E(x)=x^T Q x with symmetric off-diagonal entries counted twice",
        "qubo_matrix": q.tolist(),
        "ising_convention": "E(s)=offset+sum_i h_i s_i+sum_{i<j} J_ij s_i s_j",
        "ising_offset": offset,
        "ising_linear": linear.tolist(),
        "ising_coupling": coupling.tolist(),
        "classical_optimum_cut": optimum,
        "classical_optimum_energy": -optimum,
        "optimal_bitstrings": optimal_bits,
        "enumerated_states": len(rows),
    }
    canonical = json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()
    fixture["sha256_without_hash_field"] = hashlib.sha256(canonical).hexdigest()
    return fixture


def exactly_one_energy(bits: Iterable[int], values=(4.0, 3.0, 2.0), penalty: float = 5.0) -> float:
    vector = np.asarray(tuple(bits), dtype=float)
    return float(-np.asarray(values) @ vector + penalty * (vector.sum() - 1.0) ** 2)


def exactly_one_qubo(values=(4.0, 3.0, 2.0), penalty: float = 5.0) -> tuple[np.ndarray, float]:
    """Return Q, offset for -v.x + A(sum(x)-1)^2."""

    count = len(values)
    matrix = np.zeros((count, count), dtype=float)
    for index, value in enumerate(values):
        matrix[index, index] = -value - penalty
    for left in range(count):
        for right in range(left + 1, count):
            matrix[left, right] = matrix[right, left] = penalty
    return matrix, float(penalty)


def penalty_sweep(penalties=(0.5, 2.0, 5.0)) -> list[dict[str, object]]:
    rows = []
    for penalty in penalties:
        q, offset = exactly_one_qubo(penalty=penalty)
        states = []
        for bits in product((0, 1), repeat=3):
            direct = exactly_one_energy(bits, penalty=penalty)
            qubo = qubo_energy(bits, q, offset)
            states.append((direct, bits, sum(bits) == 1, qubo))
        best = min(states, key=lambda item: item[0])
        best_feasible = min(item[0] for item in states if item[2])
        best_infeasible = min(item[0] for item in states if not item[2])
        rows.append({
            "penalty": penalty,
            "best_bits": "".join(map(str, best[1])),
            "best_energy": best[0],
            "best_is_feasible": best[2],
            "best_feasible_energy": best_feasible,
            "best_infeasible_energy": best_infeasible,
            "maximum_direct_qubo_error": max(abs(item[0] - item[3]) for item in states),
        })
    return rows
