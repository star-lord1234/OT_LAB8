from __future__ import annotations

from tracks.D_parallel_distributed.implementation.submodular import (
    exact_max_coverage,
    greedy_max_coverage,
    run_submodular_experiment,
    verify_submodularity,
)


def test_coverage_is_exhaustively_monotone_and_submodular() -> None:
    verification = verify_submodularity()
    assert verification["normalized"]
    assert verification["monotone"]
    assert verification["diminishing_returns"]
    assert verification["submodular_inequality"]
    assert verification["violations"] == []


def test_greedy_counterexample_is_compared_with_exact_enumeration() -> None:
    greedy, exact = greedy_max_coverage(), exact_max_coverage()
    assert greedy["objective"] == 7
    assert exact["objective"] == 8
    assert greedy["selection"] == [0, 2]
    assert exact["selection"] == [1, 2]
    experiment = run_submodular_experiment()
    assert experiment["approximation_ratio_observed"] == 7 / 8
    assert 7 / 8 >= 1 - 1 / 2.718281828
