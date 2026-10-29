"""Data models and validation for the shared 0/1 selection problem."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class KnapsackInstance:
    name: str
    weights: tuple[int, ...]
    values: tuple[int, ...]
    capacity: int

    def __post_init__(self) -> None:
        if not self.name or not self.weights or len(self.weights) != len(self.values):
            raise ValueError("instance needs a name and equally sized nonempty arrays")
        if self.capacity < 0 or any(weight <= 0 for weight in self.weights):
            raise ValueError("weights must be positive and capacity nonnegative")
        if any(value < 0 for value in self.values):
            raise ValueError("values must be nonnegative")

    @property
    def size(self) -> int:
        return len(self.weights)

    def evaluate(self, selected: Iterable[int]) -> tuple[int, int, bool]:
        bits = tuple(int(bit) for bit in selected)
        if len(bits) != self.size or any(bit not in (0, 1) for bit in bits):
            raise ValueError("selection must contain one binary value per item")
        weight = sum(weight * bit for weight, bit in zip(self.weights, bits))
        value = sum(value * bit for value, bit in zip(self.values, bits))
        return value, weight, weight <= self.capacity


@dataclass(frozen=True)
class DiscreteSolution:
    method: str
    selected: tuple[int, ...]
    objective: int
    total_weight: int
    feasible: bool
    runtime_seconds: float
    status: str
    nodes_or_states: int


def benchmark_instances() -> tuple[KnapsackInstance, ...]:
    """Small fixed instances; the first is a known greedy counterexample."""

    return (
        KnapsackInstance("classic_greedy_counterexample", (10, 20, 30), (60, 100, 120), 50),
        KnapsackInstance(
            "project_selection_8",
            (4, 7, 3, 8, 5, 9, 6, 2),
            (7, 13, 6, 12, 9, 16, 10, 4),
            24,
        ),
        KnapsackInstance(
            "allocation_14",
            (2, 5, 4, 7, 3, 9, 6, 8, 5, 4, 11, 3, 6, 7),
            (6, 10, 9, 13, 7, 17, 12, 14, 11, 8, 20, 6, 13, 12),
            39,
        ),
    )
