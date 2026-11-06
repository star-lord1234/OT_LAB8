from __future__ import annotations

from tracks.F_compiler.implementation.ir import compile_source, execute
from tracks.F_compiler.implementation.passes import (
    FULL_PASS_ORDER,
    apply_passes,
    common_subexpression_elimination,
    constant_folding_propagation,
    dead_code_elimination,
    strength_reduction,
)
from tracks.F_compiler.implementation.programs import load_programs


def test_full_pipeline_preserves_all_program_outputs() -> None:
    for program in load_programs():
        baseline = compile_source(program.source)
        optimized = apply_passes(baseline)
        assert execute(baseline, program.inputs) == execute(optimized, program.inputs) == program.expected
    assert len(FULL_PASS_ORDER) == 4


def test_constant_folding_and_dead_code_elimination_reduce_known_cases() -> None:
    constants = compile_source("let a = 2 + 3; let dead = 9 * 9; print a;")
    folded = constant_folding_propagation(constants)
    optimized = dead_code_elimination(folded)
    assert execute(optimized) == (5,)
    assert len(optimized) == 1
    assert optimized[0].op == "PRINT" and optimized[0].args == (5,)


def test_cse_removes_repeated_expression() -> None:
    source = "input x; input y; let a=x+y; let b=x+y; print a*b;"
    baseline = compile_source(source)
    optimized = common_subexpression_elimination(baseline)
    assert len(optimized) == len(baseline) - 1
    assert execute(optimized, {"x": 3, "y": 4}) == (49,)


def test_strength_reduction_is_algebraically_safe_for_power_of_two() -> None:
    source = "input x; let eight=8; print x*eight;"
    propagated = constant_folding_propagation(compile_source(source))
    optimized = strength_reduction(propagated)
    assert any(instruction.op == "SHL" for instruction in optimized)
    for value in (-9, 0, 7):
        assert execute(propagated, {"x": value}) == execute(optimized, {"x": value})
