from __future__ import annotations

import math

from tracks.E_case_study.implementation.models import Request, SimulationConfig, batch_feasible
from tracks.E_case_study.implementation.strategies import (
    batch_selection_score,
    choose_dp,
    choose_fcfs,
    exhaustive_best_batch,
)
from tracks.E_case_study.implementation.workload import generate_workload, workload_digest


def test_workload_is_reproducible_valid_and_varied() -> None:
    config = SimulationConfig()
    first = generate_workload(40, 1.0, 123, config)
    second = generate_workload(40, 1.0, 123, config)
    assert workload_digest(first) == workload_digest(second)
    assert first == second
    assert [request.arrival_time for request in first] == sorted(request.arrival_time for request in first)
    assert len({request.token_length for request in first}) > 5
    assert all(request.deadline > request.arrival_time for request in first)


def test_fcfs_selects_a_feasible_prefix() -> None:
    config = SimulationConfig(max_batch_size=3, token_capacity=120, padded_token_capacity=180)
    pending = [Request(i, 0.0, length, length * 0.01, 10.0) for i, length in enumerate((30, 40, 100, 20))]
    selected = choose_fcfs(pending, 0.0, config)
    assert [request.request_id for request in selected] == [0, 1]
    assert batch_feasible(selected, config)


def test_dynamic_programming_selector_matches_exhaustive_score() -> None:
    config = SimulationConfig(max_batch_size=4, token_capacity=220, padded_token_capacity=300, dp_lookahead=12)
    pending = [Request(i, i * 0.1, length, length * 0.015, 6.0 + i) for i, length in enumerate((20, 55, 70, 80, 35, 110, 45))]
    dispatch = 2.5
    selected = choose_dp(pending, dispatch, config)
    exact = exhaustive_best_batch(pending, dispatch, config)
    assert batch_feasible(selected, config)
    assert math.isclose(batch_selection_score(selected, dispatch, config), batch_selection_score(exact, dispatch, config), rel_tol=0.0, abs_tol=1e-12)
