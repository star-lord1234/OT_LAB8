"""Exact-verifiable maximum-coverage benchmark and greedy solver."""

from __future__ import annotations

from itertools import combinations
from time import perf_counter
from typing import Iterable


UNIVERSE = frozenset(range(10))
SETS = (
    frozenset({0, 1, 2, 3, 4}),       # Greedy takes this unique largest set.
    frozenset({0, 1, 2, 5}),
    frozenset({3, 4, 6, 7}),           # Sets 1 and 2 are the exact best pair.
    frozenset({8, 9}),
    frozenset({0, 6, 8}),
    frozenset({2, 7, 9}),
)
BUDGET = 2


def coverage_value(selection: Iterable[int], sets: tuple[frozenset[int], ...] = SETS) -> int:
    """Return the normalized monotone coverage objective f(S)=|union(S)|."""
    covered: set[int] = set()
    for index in selection:
        covered.update(sets[index])
    return len(covered)


def marginal_gain(selection: Iterable[int], candidate: int) -> int:
    selected = frozenset(selection)
    return coverage_value(selected | {candidate}) - coverage_value(selected)


def greedy_max_coverage(budget: int = BUDGET) -> dict[str, object]:
    started = perf_counter()
    selected: list[int] = []
    trace: list[dict[str, int]] = []
    for step in range(budget):
        candidates = [index for index in range(len(SETS)) if index not in selected]
        best = max(candidates, key=lambda index: (marginal_gain(selected, index), -index))
        gain = marginal_gain(selected, best)
        selected.append(best)
        trace.append({"step": step + 1, "selected_set": best, "marginal_gain": gain, "value": coverage_value(selected)})
    return {"method": "greedy", "selection": selected, "objective": coverage_value(selected), "trace": trace, "runtime_seconds": perf_counter() - started}


def exact_max_coverage(budget: int = BUDGET) -> dict[str, object]:
    started = perf_counter()
    candidates = list(combinations(range(len(SETS)), budget))
    selection = max(candidates, key=lambda choice: (coverage_value(choice), tuple(-i for i in choice)))
    return {"method": "exact_enumeration", "selection": list(selection), "objective": coverage_value(selection), "evaluated_subsets": len(candidates), "runtime_seconds": perf_counter() - started}


def verify_submodularity() -> dict[str, object]:
    """Exhaustively verify normalization, monotonicity, and diminishing returns."""
    indices = range(len(SETS))
    subsets = [frozenset(choice) for size in range(len(SETS) + 1) for choice in combinations(indices, size)]
    monotonicity_checks = 0
    diminishing_returns_checks = 0
    submodular_inequality_checks = 0
    violations: list[dict[str, object]] = []
    for left in subsets:
        for right in subsets:
            if left <= right:
                monotonicity_checks += 1
                if coverage_value(left) > coverage_value(right):
                    violations.append({"property": "monotonicity", "left": sorted(left), "right": sorted(right)})
                for element in set(indices) - right:
                    diminishing_returns_checks += 1
                    if marginal_gain(left, element) < marginal_gain(right, element):
                        violations.append({"property": "diminishing_returns", "left": sorted(left), "right": sorted(right), "element": element})
            submodular_inequality_checks += 1
            if coverage_value(left) + coverage_value(right) < coverage_value(left | right) + coverage_value(left & right):
                violations.append({"property": "submodular_inequality", "left": sorted(left), "right": sorted(right)})
    return {
        "normalized": coverage_value(()) == 0,
        "monotone": not any(row["property"] == "monotonicity" for row in violations),
        "diminishing_returns": not any(row["property"] == "diminishing_returns" for row in violations),
        "submodular_inequality": not any(row["property"] == "submodular_inequality" for row in violations),
        "monotonicity_checks": monotonicity_checks,
        "diminishing_returns_checks": diminishing_returns_checks,
        "submodular_inequality_checks": submodular_inequality_checks,
        "violations": violations,
    }


def run_submodular_experiment() -> dict[str, object]:
    greedy = greedy_max_coverage()
    exact = exact_max_coverage()
    ratio = float(greedy["objective"]) / float(exact["objective"])
    return {
        "universe": sorted(UNIVERSE),
        "sets": [sorted(value) for value in SETS],
        "budget": BUDGET,
        "objective": "f(S) = cardinality of the union of selected sets",
        "greedy": greedy,
        "exact": exact,
        "approximation_ratio_observed": ratio,
        "theoretical_guarantee": "greedy >= (1 - 1/e) OPT",
        "guarantee_assumptions": ["normalized", "nonnegative", "monotone", "submodular", "cardinality constraint"],
        "verification": verify_submodularity(),
    }
