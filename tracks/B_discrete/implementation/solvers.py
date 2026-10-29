"""Transparent reference solvers for identical 0/1 knapsack instances."""

from __future__ import annotations

import time
from itertools import product

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from .models import DiscreteSolution, KnapsackInstance


def _solution(instance: KnapsackInstance, method: str, selected, started: float, status: str, explored: int) -> DiscreteSolution:
    bits = tuple(int(bit) for bit in selected)
    objective, weight, feasible = instance.evaluate(bits)
    return DiscreteSolution(method, bits, objective, weight, feasible, time.perf_counter() - started, status, explored)


def solve_exhaustive(instance: KnapsackInstance) -> DiscreteSolution:
    started = time.perf_counter()
    best_bits = (0,) * instance.size
    best_value = -1
    states = 0
    for bits in product((0, 1), repeat=instance.size):
        states += 1
        value, _, feasible = instance.evaluate(bits)
        if feasible and value > best_value:
            best_value, best_bits = value, bits
    return _solution(instance, "exhaustive_reference", best_bits, started, "optimal_by_enumeration", states)


def solve_greedy(instance: KnapsackInstance) -> DiscreteSolution:
    started = time.perf_counter()
    order = sorted(range(instance.size), key=lambda index: (-instance.values[index] / instance.weights[index], -instance.values[index], index))
    selected = [0] * instance.size
    remaining = instance.capacity
    for index in order:
        if instance.weights[index] <= remaining:
            selected[index] = 1
            remaining -= instance.weights[index]
    return _solution(instance, "greedy", selected, started, "heuristic_feasible", instance.size)


def solve_dynamic_programming(instance: KnapsackInstance) -> DiscreteSolution:
    started = time.perf_counter()
    count, capacity = instance.size, instance.capacity
    table = np.zeros((count + 1, capacity + 1), dtype=np.int64)
    for item in range(1, count + 1):
        weight, value = instance.weights[item - 1], instance.values[item - 1]
        table[item] = table[item - 1]
        for limit in range(weight, capacity + 1):
            table[item, limit] = max(table[item, limit], table[item - 1, limit - weight] + value)
    selected = [0] * count
    limit = capacity
    for item in range(count, 0, -1):
        if table[item, limit] != table[item - 1, limit]:
            selected[item - 1] = 1
            limit -= instance.weights[item - 1]
    return _solution(instance, "dynamic_programming", selected, started, "optimal_integer_capacity_dp", count * (capacity + 1))


def solve_ilp(instance: KnapsackInstance) -> DiscreteSolution:
    started = time.perf_counter()
    result = milp(
        c=-np.asarray(instance.values, dtype=float),
        integrality=np.ones(instance.size),
        bounds=Bounds(np.zeros(instance.size), np.ones(instance.size)),
        constraints=LinearConstraint(np.asarray(instance.weights, dtype=float), -np.inf, instance.capacity),
        options={"disp": False},
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"SciPy HiGHS MILP failed: {result.message}")
    selected = np.rint(result.x).astype(int)
    explored = int(getattr(result, "mip_node_count", 0) or 0)
    return _solution(instance, "integer_linear_programming", selected, started, "optimal_solver_status", explored)


def solve_branch_and_bound(instance: KnapsackInstance) -> DiscreteSolution:
    started = time.perf_counter()
    order = sorted(range(instance.size), key=lambda index: instance.values[index] / instance.weights[index], reverse=True)
    best_value = 0
    best_sorted = [0] * instance.size
    current = [0] * instance.size
    nodes = 0

    def fractional_bound(level: int, weight: int, value: int) -> float:
        remaining = instance.capacity - weight
        bound = float(value)
        for position in range(level, instance.size):
            index = order[position]
            if instance.weights[index] <= remaining:
                remaining -= instance.weights[index]
                bound += instance.values[index]
            else:
                bound += instance.values[index] * remaining / instance.weights[index]
                break
        return bound

    def search(level: int, weight: int, value: int) -> None:
        nonlocal best_value, best_sorted, nodes
        nodes += 1
        if value > best_value:
            best_value, best_sorted = value, current.copy()
        if level == instance.size or fractional_bound(level, weight, value) <= best_value + 1e-12:
            return
        index = order[level]
        if weight + instance.weights[index] <= instance.capacity:
            current[level] = 1
            search(level + 1, weight + instance.weights[index], value + instance.values[index])
            current[level] = 0
        search(level + 1, weight, value)

    search(0, 0, 0)
    selected = [0] * instance.size
    for position, bit in enumerate(best_sorted):
        selected[order[position]] = bit
    return _solution(instance, "branch_and_bound", selected, started, "optimal_by_bound", nodes)


SOLVERS = {
    "greedy": solve_greedy,
    "integer_linear_programming": solve_ilp,
    "branch_and_bound": solve_branch_and_bound,
    "dynamic_programming": solve_dynamic_programming,
}
