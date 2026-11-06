from tracks.J_software_engineering.implementation.selection import (
    TestCandidate as Candidate,
    cumulative_schedule,
    exhaustive_maximum_coverage,
    greedy_maximum_coverage,
    original_order_select,
)


def _candidate(identifier, order, cost, lines):
    return Candidate(identifier, order, cost, frozenset(lines), 1)


def test_greedy_maximum_coverage_beats_original_order_on_known_instance():
    candidates = (
        _candidate("slow-first", 0, 2.0, {"a"}),
        _candidate("efficient-one", 1, 1.0, {"b", "c", "d"}),
        _candidate("efficient-two", 2, 1.0, {"e", "f"}),
    )
    original = original_order_select(candidates, 2.0)
    greedy = greedy_maximum_coverage(candidates, 2.0)
    exact = exhaustive_maximum_coverage(candidates, 2.0)
    assert len(original.covered_lines) == 1
    assert len(greedy.covered_lines) == len(exact.covered_lines) == 5
    assert greedy.cost_seconds <= 2.0


def test_exact_solver_accounts_for_overlap_and_budget():
    candidates = (
        _candidate("a", 0, 1.0, {"1", "2"}),
        _candidate("b", 1, 1.0, {"2", "3"}),
        _candidate("c", 2, 1.5, {"4", "5"}),
    )
    result = exhaustive_maximum_coverage(candidates, 2.0)
    assert {candidate.candidate_id for candidate in result.selected} == {"a", "b"}
    assert result.covered_lines == frozenset({"1", "2", "3"})
    assert result.cost_seconds == 2.0


def test_cumulative_schedule_recomputes_marginal_coverage():
    candidates = (
        _candidate("a", 0, 1.0, {"1", "2"}),
        _candidate("b", 1, 1.0, {"2", "3"}),
    )
    rows = cumulative_schedule(original_order_select(candidates, 2.0))
    assert [row["marginal_covered_lines"] for row in rows] == [2, 1]
    assert rows[-1]["cumulative_covered_lines"] == 3
    assert rows[-1]["cumulative_profiled_cost_seconds"] == 2.0
