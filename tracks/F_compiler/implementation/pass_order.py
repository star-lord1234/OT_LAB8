"""Budgeted pass-order selection by branch-and-bound with exhaustive verification."""

from __future__ import annotations

from itertools import permutations

from .ir import Instruction
from .passes import PASS_COSTS, PASS_FUNCTIONS, apply_pass


Suite = dict[str, list[Instruction]]


def apply_order(suite: Suite, order: tuple[str, ...]) -> Suite:
    result = {name: list(instructions) for name, instructions in suite.items()}
    for pass_name in order:
        result = {name: apply_pass(instructions, pass_name) for name, instructions in result.items()}
    return result


def suite_instruction_count(suite: Suite) -> int:
    return sum(len(instructions) for instructions in suite.values())


def _candidate_key(objective: int, effort: int, order: tuple[str, ...]) -> tuple[int, int, tuple[str, ...]]:
    return objective, effort, order


def branch_and_bound_pass_order(suite: Suite, effort_budget: int) -> dict[str, object]:
    if effort_budget < 0:
        raise ValueError("effort budget must be nonnegative")
    lower_bound = sum(sum(instruction.op == "PRINT" for instruction in instructions) for instructions in suite.values())
    baseline = suite_instruction_count(suite)
    incumbent = {"objective": baseline, "effort": 0, "order": (), "suite": suite}
    nodes = 0
    pruned_budget = 0
    pruned_bound = 0

    def search(current: Suite, order: tuple[str, ...], effort: int, remaining: tuple[str, ...]) -> None:
        nonlocal incumbent, nodes, pruned_budget, pruned_bound
        nodes += 1
        objective = suite_instruction_count(current)
        if _candidate_key(objective, effort, order) < _candidate_key(int(incumbent["objective"]), int(incumbent["effort"]), tuple(incumbent["order"])):
            incumbent = {"objective": objective, "effort": effort, "order": order, "suite": current}
        if objective == lower_bound:
            pruned_bound += 1
            return
        for name in remaining:
            new_effort = effort + PASS_COSTS[name]
            if new_effort > effort_budget:
                pruned_budget += 1
                continue
            updated = {program: apply_pass(instructions, name) for program, instructions in current.items()}
            search(updated, (*order, name), new_effort, tuple(candidate for candidate in remaining if candidate != name))

    search(suite, (), 0, tuple(PASS_FUNCTIONS))
    return {
        "method": "branch_and_bound",
        "effort_budget": effort_budget,
        "selected_order": list(incumbent["order"]),
        "selected_effort": incumbent["effort"],
        "baseline_instruction_count": baseline,
        "optimized_instruction_count": incumbent["objective"],
        "instruction_reduction": baseline - int(incumbent["objective"]),
        "nodes_visited": nodes,
        "pruned_by_budget": pruned_budget,
        "pruned_by_lower_bound": pruned_bound,
        "lower_bound": lower_bound,
    }


def exhaustive_pass_order(suite: Suite, effort_budget: int) -> dict[str, object]:
    names = tuple(PASS_FUNCTIONS)
    best = (suite_instruction_count(suite), 0, ())
    evaluated = 1
    for length in range(1, len(names) + 1):
        for order in permutations(names, length):
            effort = sum(PASS_COSTS[name] for name in order)
            if effort > effort_budget:
                continue
            evaluated += 1
            objective = suite_instruction_count(apply_order(suite, order))
            best = min(best, _candidate_key(objective, effort, order))
    return {
        "method": "exhaustive_enumeration",
        "effort_budget": effort_budget,
        "selected_order": list(best[2]),
        "selected_effort": best[1],
        "optimized_instruction_count": best[0],
        "orders_evaluated": evaluated,
    }
