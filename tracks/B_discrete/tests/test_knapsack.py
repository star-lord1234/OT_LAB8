import pytest

from tracks.B_discrete.implementation.models import KnapsackInstance, benchmark_instances
from tracks.B_discrete.implementation.solvers import (
    SOLVERS,
    solve_branch_and_bound,
    solve_dynamic_programming,
    solve_exhaustive,
    solve_ilp,
)


@pytest.mark.parametrize("instance", benchmark_instances(), ids=lambda item: item.name)
def test_all_methods_are_feasible_and_exact_methods_match_enumeration(instance):
    reference = solve_exhaustive(instance)
    for name, solver in SOLVERS.items():
        solution = solver(instance)
        assert solution.feasible, name
        assert solution.objective <= reference.objective, name
        if name != "greedy":
            assert solution.objective == reference.objective, name


def test_greedy_counterexample_has_verified_nonzero_gap():
    instance = benchmark_instances()[0]
    greedy = SOLVERS["greedy"](instance)
    reference = solve_exhaustive(instance)
    assert greedy.objective == 160
    assert reference.objective == 220
    assert greedy.objective < reference.objective


def test_exact_methods_match_enumeration_on_additional_tiny_instance():
    instance = KnapsackInstance("tiny", (2, 3, 4, 5, 7), (3, 4, 8, 8, 10), 10)
    optimum = solve_exhaustive(instance).objective
    assert solve_dynamic_programming(instance).objective == optimum
    assert solve_branch_and_bound(instance).objective == optimum
    assert solve_ilp(instance).objective == optimum


def test_instance_rejects_nonbinary_selection():
    with pytest.raises(ValueError):
        benchmark_instances()[0].evaluate([0, 2, 1])
