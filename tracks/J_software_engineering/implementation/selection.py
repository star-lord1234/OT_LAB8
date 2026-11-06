"""Budgeted maximum-coverage models for test-suite selection."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class TestCandidate:
    candidate_id: str
    original_order: int
    cost_seconds: float
    covered_lines: frozenset[str]
    test_count: int

    def __post_init__(self) -> None:
        if self.cost_seconds <= 0:
            raise ValueError("candidate cost must be positive")
        if self.test_count <= 0:
            raise ValueError("candidate must contain at least one test")


@dataclass(frozen=True)
class Selection:
    method: str
    selected: tuple[TestCandidate, ...]
    budget_seconds: float

    @property
    def cost_seconds(self) -> float:
        return sum(candidate.cost_seconds for candidate in self.selected)

    @property
    def covered_lines(self) -> frozenset[str]:
        return frozenset().union(*(candidate.covered_lines for candidate in self.selected))


def _validate(candidates: tuple[TestCandidate, ...], budget_seconds: float) -> None:
    if not candidates:
        raise ValueError("at least one candidate is required")
    if budget_seconds <= 0:
        raise ValueError("budget must be positive")
    identifiers = [candidate.candidate_id for candidate in candidates]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("candidate identifiers must be unique")


def original_order_select(
    candidates: tuple[TestCandidate, ...], budget_seconds: float
) -> Selection:
    """Naive baseline: scan original order and retain each candidate that fits."""

    _validate(candidates, budget_seconds)
    chosen: list[TestCandidate] = []
    spent = 0.0
    for candidate in sorted(candidates, key=lambda item: item.original_order):
        if spent + candidate.cost_seconds <= budget_seconds + 1e-12:
            chosen.append(candidate)
            spent += candidate.cost_seconds
    return Selection("original_order", tuple(chosen), budget_seconds)


def greedy_maximum_coverage(
    candidates: tuple[TestCandidate, ...], budget_seconds: float
) -> Selection:
    """Greedy maximum marginal line coverage per measured second."""

    _validate(candidates, budget_seconds)
    remaining = list(candidates)
    chosen: list[TestCandidate] = []
    covered: set[str] = set()
    spent = 0.0
    while remaining:
        feasible = [
            candidate
            for candidate in remaining
            if spent + candidate.cost_seconds <= budget_seconds + 1e-12
        ]
        if not feasible:
            break
        best = max(
            feasible,
            key=lambda candidate: (
                len(candidate.covered_lines - covered) / candidate.cost_seconds,
                len(candidate.covered_lines - covered),
                -candidate.cost_seconds,
                -candidate.original_order,
            ),
        )
        marginal = best.covered_lines - covered
        remaining.remove(best)
        if not marginal:
            continue
        chosen.append(best)
        spent += best.cost_seconds
        covered.update(best.covered_lines)
    return Selection("greedy_coverage_per_second", tuple(chosen), budget_seconds)


def exhaustive_maximum_coverage(
    candidates: tuple[TestCandidate, ...], budget_seconds: float
) -> Selection:
    """Exact enumeration for a deliberately small candidate subset."""

    _validate(candidates, budget_seconds)
    best: tuple[TestCandidate, ...] = ()
    best_coverage = -1
    best_cost = float("inf")
    for size in range(len(candidates) + 1):
        for subset in combinations(candidates, size):
            cost = sum(candidate.cost_seconds for candidate in subset)
            if cost > budget_seconds + 1e-12:
                continue
            coverage = len(frozenset().union(*(candidate.covered_lines for candidate in subset)))
            order_key = tuple(candidate.original_order for candidate in subset)
            best_order_key = tuple(candidate.original_order for candidate in best)
            if (
                coverage > best_coverage
                or (coverage == best_coverage and cost < best_cost - 1e-12)
                or (
                    coverage == best_coverage
                    and abs(cost - best_cost) <= 1e-12
                    and order_key < best_order_key
                )
            ):
                best, best_coverage, best_cost = subset, coverage, cost
    return Selection("exact_exhaustive", tuple(best), budget_seconds)


def cumulative_schedule(selection: Selection) -> list[dict[str, object]]:
    rows = []
    covered: set[str] = set()
    spent = 0.0
    for position, candidate in enumerate(selection.selected, start=1):
        previous = len(covered)
        covered.update(candidate.covered_lines)
        spent += candidate.cost_seconds
        rows.append({
            "method": selection.method,
            "selection_position": position,
            "candidate_id": candidate.candidate_id,
            "candidate_test_count": candidate.test_count,
            "candidate_profiled_cost_seconds": candidate.cost_seconds,
            "marginal_covered_lines": len(covered) - previous,
            "cumulative_profiled_cost_seconds": spent,
            "cumulative_covered_lines": len(covered),
            "budget_seconds": selection.budget_seconds,
        })
    return rows
