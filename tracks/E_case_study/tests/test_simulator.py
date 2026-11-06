from __future__ import annotations

import math

from tracks.E_case_study.implementation.exact_reference import (
    evaluate_plan,
    exhaustive_offline_schedule,
    tiny_reference_requests,
)
from tracks.E_case_study.implementation.models import Request, SimulationConfig
from tracks.E_case_study.implementation.simulator import objective_from_request_rows, simulate
from tracks.E_case_study.implementation.workload import generate_workload


def test_all_strategies_process_every_request_once_with_valid_batches() -> None:
    config = SimulationConfig()
    requests = generate_workload(48, 1.2, 321, config)
    for strategy in ("fcfs", "greedy_length", "dynamic_programming"):
        result = simulate(requests, strategy, config)
        assert result["verification"]["valid"], result["verification"]["errors"]
        assert result["verification"]["processed_count"] == 48
        assert result["verification"]["unique_processed_count"] == 48
        assert result["metrics"]["correct"]
        assert result["metrics"]["simulated"]
        recalculated = objective_from_request_rows(result["request_rows"], result["metrics"]["total_busy_time"], config)
        assert math.isclose(recalculated, result["metrics"]["objective"], abs_tol=1e-12)


def test_intentional_batch_wait_can_worsen_sparse_latency() -> None:
    config = SimulationConfig(batch_window=0.8, max_batch_wait=2.0)
    requests = [
        Request(0, 0.0, 32, 0.48, 8.0),
        Request(1, 10.0, 36, 0.54, 18.0),
    ]
    baseline = simulate(requests, "fcfs", config)
    batched = simulate(requests, "greedy_length", config)
    assert batched["metrics"]["mean_latency"] > baseline["metrics"]["mean_latency"]
    assert batched["metrics"]["mean_waiting_time"] > baseline["metrics"]["mean_waiting_time"]
    assert batched["metrics"]["throughput_requests_per_time"] <= baseline["metrics"]["throughput_requests_per_time"]


def test_tiny_exhaustive_reference_is_feasible_and_self_consistent() -> None:
    config = SimulationConfig(max_batch_size=3, token_capacity=240, padded_token_capacity=330)
    requests = tiny_reference_requests()
    exact = exhaustive_offline_schedule(requests, config)
    reevaluated = evaluate_plan(requests, [tuple(batch) for batch in exact["plan"]], config)
    assert exact["evaluated_as_exact"]
    assert math.isclose(exact["objective"], reevaluated["objective"], abs_tol=1e-12)
    assert sorted(request_id for batch in exact["plan"] for request_id in batch) == list(range(6))
