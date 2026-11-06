from __future__ import annotations

from tracks.F_compiler.implementation.ir import compile_source
from tracks.F_compiler.implementation.pass_order import branch_and_bound_pass_order, exhaustive_pass_order
from tracks.F_compiler.implementation.programs import load_programs


def test_branch_and_bound_matches_exhaustive_budgeted_pass_order() -> None:
    suite = {program.name: compile_source(program.source) for program in load_programs()}
    branch = branch_and_bound_pass_order(suite, effort_budget=8)
    exact = exhaustive_pass_order(suite, effort_budget=8)
    assert branch["optimized_instruction_count"] == exact["optimized_instruction_count"]
    assert branch["selected_effort"] == exact["selected_effort"]
    assert branch["selected_order"] == exact["selected_order"]
    assert branch["selected_effort"] <= 8
    assert branch["instruction_reduction"] > 0
    assert branch["nodes_visited"] > 1
