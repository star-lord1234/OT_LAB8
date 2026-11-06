"""Reproducible synthetic request workload generation and validation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

import numpy as np

from .models import Request, SimulationConfig


def generate_workload(size: int, arrival_rate: float, seed: int, config: SimulationConfig) -> list[Request]:
    if size < 1:
        raise ValueError("size must be positive")
    if arrival_rate <= 0:
        raise ValueError("arrival_rate must be positive")
    rng = np.random.default_rng(seed)
    inter_arrivals = rng.exponential(1.0 / arrival_rate, size=size)
    arrivals = np.cumsum(inter_arrivals)
    arrivals -= arrivals[0]
    mixture = rng.random(size)
    lengths = np.empty(size, dtype=int)
    short = mixture < 0.65
    medium = (mixture >= 0.65) & (mixture < 0.92)
    long = mixture >= 0.92
    lengths[short] = rng.integers(16, 65, size=int(np.sum(short)))
    lengths[medium] = rng.integers(65, 161, size=int(np.sum(medium)))
    lengths[long] = rng.integers(161, 257, size=int(np.sum(long)))
    multipliers = rng.uniform(0.012, 0.018, size=size)
    requests = []
    for request_id, (arrival, length, multiplier) in enumerate(zip(arrivals, lengths, multipliers)):
        processing_cost = float(length * multiplier)
        deadline = float(arrival + 3.0 + 0.04 * length)
        requests.append(Request(request_id, float(arrival), int(length), processing_cost, deadline))
    validate_workload(requests, config)
    return requests


def validate_workload(requests: list[Request], config: SimulationConfig) -> None:
    if not requests:
        raise ValueError("workload cannot be empty")
    ids = [request.request_id for request in requests]
    if ids != list(range(len(requests))):
        raise ValueError("request IDs must be contiguous and ordered")
    arrivals = [request.arrival_time for request in requests]
    if arrivals != sorted(arrivals):
        raise ValueError("arrival times must be nondecreasing")
    for request in requests:
        if request.token_length <= 0 or request.token_length > min(config.token_capacity, config.padded_token_capacity):
            raise ValueError("each request must fit alone")
        if request.processing_cost <= 0:
            raise ValueError("processing cost must be positive")
        if request.deadline <= request.arrival_time:
            raise ValueError("deadline must follow arrival")


def workload_digest(requests: list[Request]) -> str:
    payload = json.dumps([asdict(request) for request in requests], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
