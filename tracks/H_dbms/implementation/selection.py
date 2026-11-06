"""Greedy, MILP, and dynamic-programming index selection."""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


@dataclass(frozen=True)
class SelectionResult:
    method: str
    selected: tuple[str, ...]
    total_cost_pages: int
    estimated_benefit_seconds: float
    estimated_cost_seconds: float
    runtime_seconds: float
    optimal: bool


def _result(
    method: str,
    names: list[str],
    costs: list[int],
    benefits: list[float],
    selected_indices: list[int],
    baseline_cost: float,
    runtime: float,
    optimal: bool,
) -> SelectionResult:
    selected = tuple(names[index] for index in selected_indices)
    benefit = sum(benefits[index] for index in selected_indices)
    return SelectionResult(
        method=method,
        selected=selected,
        total_cost_pages=sum(costs[index] for index in selected_indices),
        estimated_benefit_seconds=benefit,
        estimated_cost_seconds=baseline_cost - benefit,
        runtime_seconds=runtime,
        optimal=optimal,
    )


def greedy_select(
    names: list[str], costs: list[int], benefits: list[float], budget: int, baseline_cost: float
) -> SelectionResult:
    started = time.perf_counter_ns()
    ordering = sorted(
        range(len(names)),
        key=lambda index: (benefits[index] / costs[index], benefits[index], names[index]),
        reverse=True,
    )
    selected: list[int] = []
    used = 0
    for index in ordering:
        if benefits[index] > 0 and used + costs[index] <= budget:
            selected.append(index)
            used += costs[index]
    runtime = (time.perf_counter_ns() - started) / 1e9
    return _result("greedy", names, costs, benefits, selected, baseline_cost, runtime, False)


def ilp_select(
    names: list[str], costs: list[int], benefits: list[float], budget: int, baseline_cost: float
) -> SelectionResult:
    started = time.perf_counter_ns()
    result = milp(
        c=-np.asarray(benefits, dtype=float),
        integrality=np.ones(len(names), dtype=int),
        bounds=Bounds(np.zeros(len(names)), np.ones(len(names))),
        constraints=LinearConstraint(np.asarray([costs], dtype=float), -np.inf, float(budget)),
        options={"disp": False},
    )
    runtime = (time.perf_counter_ns() - started) / 1e9
    if not result.success or result.x is None:
        raise RuntimeError(f"MILP selection failed: {result.message}")
    selected = [index for index, value in enumerate(result.x) if value > 0.5]
    return _result("ilp", names, costs, benefits, selected, baseline_cost, runtime, True)


def dynamic_programming_select(
    names: list[str], costs: list[int], benefits: list[float], budget: int, baseline_cost: float
) -> SelectionResult:
    started = time.perf_counter_ns()
    count = len(names)
    values = [[0.0] * (budget + 1) for _ in range(count + 1)]
    choices = [[False] * (budget + 1) for _ in range(count + 1)]
    for item in range(1, count + 1):
        cost = costs[item - 1]
        benefit = benefits[item - 1]
        for capacity in range(budget + 1):
            values[item][capacity] = values[item - 1][capacity]
            if cost <= capacity:
                candidate = values[item - 1][capacity - cost] + benefit
                if candidate > values[item][capacity] + 1e-15:
                    values[item][capacity] = candidate
                    choices[item][capacity] = True
    selected: list[int] = []
    capacity = budget
    for item in range(count, 0, -1):
        if choices[item][capacity]:
            selected.append(item - 1)
            capacity -= costs[item - 1]
    selected.reverse()
    runtime = (time.perf_counter_ns() - started) / 1e9
    return _result("dynamic_programming", names, costs, benefits, selected, baseline_cost, runtime, True)
