"""Domain models and explicit simulated service/capacity definitions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class Request:
    request_id: int
    arrival_time: float
    token_length: int
    processing_cost: float
    deadline: float


@dataclass(frozen=True)
class SimulationConfig:
    max_batch_size: int = 4
    token_capacity: int = 512
    padded_token_capacity: int = 640
    batch_window: float = 0.8
    max_batch_wait: float = 2.0
    fixed_overhead: float = 0.35
    parallel_penalty: float = 0.22
    tardiness_penalty: float = 2.0
    compute_weight: float = 0.15
    dp_lookahead: int = 12


@dataclass(frozen=True)
class BatchRecord:
    batch_id: int
    strategy: str
    request_ids: tuple[int, ...]
    decision_time: float
    start_time: float
    end_time: float
    service_time: float
    formation_wait: float
    request_count: int
    token_sum: int
    padded_tokens: int
    token_capacity: int
    padded_token_capacity: int
    token_efficiency: float
    token_capacity_utilization: float
    padded_capacity_utilization: float

    def to_mapping(self) -> dict[str, object]:
        row = asdict(self)
        row["request_ids"] = ";".join(str(value) for value in self.request_ids)
        return row


def batch_feasible(requests: Iterable[Request], config: SimulationConfig) -> bool:
    batch = tuple(requests)
    if not batch or len(batch) > config.max_batch_size:
        return False
    token_sum = sum(request.token_length for request in batch)
    padded_tokens = len(batch) * max(request.token_length for request in batch)
    return token_sum <= config.token_capacity and padded_tokens <= config.padded_token_capacity


def simulated_service_time(requests: Iterable[Request], config: SimulationConfig) -> float:
    """Return a documented model value, not measured model-inference time."""
    batch = tuple(requests)
    if not batch:
        raise ValueError("a service batch cannot be empty")
    if not batch_feasible(batch, config):
        raise ValueError("batch violates a capacity constraint")
    largest_cost = max(request.processing_cost for request in batch)
    return config.fixed_overhead + largest_cost * (1.0 + config.parallel_penalty * (len(batch) - 1))
