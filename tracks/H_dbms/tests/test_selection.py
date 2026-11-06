from __future__ import annotations

import pytest

from tracks.H_dbms.implementation.selection import (
    dynamic_programming_select,
    greedy_select,
    ilp_select,
)


def test_exact_solvers_match_and_can_beat_greedy() -> None:
    names = ["small_ratio_winner", "large_exact_winner"]
    costs = [10, 20]
    benefits = [60.0, 100.0]
    greedy = greedy_select(names, costs, benefits, 20, 200.0)
    ilp = ilp_select(names, costs, benefits, 20, 200.0)
    dynamic = dynamic_programming_select(names, costs, benefits, 20, 200.0)
    assert greedy.selected == ("small_ratio_winner",)
    assert ilp.selected == dynamic.selected == ("large_exact_winner",)
    assert ilp.estimated_benefit_seconds == pytest.approx(100.0)
    assert dynamic.optimal is True


@pytest.mark.parametrize("budget", [0, 5, 30])
def test_all_selectors_respect_budget(budget: int) -> None:
    names = ["a", "b", "c"]
    costs = [4, 7, 12]
    benefits = [1.0, 3.0, 5.0]
    results = (
        greedy_select(names, costs, benefits, budget, 10.0),
        ilp_select(names, costs, benefits, budget, 10.0),
        dynamic_programming_select(names, costs, benefits, budget, 10.0),
    )
    assert all(result.total_cost_pages <= budget for result in results)
