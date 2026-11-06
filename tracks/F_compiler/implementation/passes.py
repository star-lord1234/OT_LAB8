"""Four semantics-preserving optimization passes over the toy IR."""

from __future__ import annotations

from collections.abc import Callable

from .ir import Instruction, Operand


def _replace(operand: Operand, constants: dict[str, int]) -> Operand:
    return constants.get(operand, operand) if isinstance(operand, str) else operand


def _evaluate(op: str, left: int, right: int) -> int | None:
    if op == "ADD": return left + right
    if op == "SUB": return left - right
    if op == "MUL": return left * right
    if op == "DIV":
        return None if right == 0 else int(left / right)
    if op == "SHL": return left << right
    return None


def constant_folding_propagation(instructions: list[Instruction]) -> list[Instruction]:
    constants: dict[str, int] = {}
    output: list[Instruction] = []
    for instruction in instructions:
        arguments = tuple(_replace(argument, constants) for argument in instruction.args)
        if instruction.op == "CONST":
            value = int(arguments[0])
            constants[str(instruction.dest)] = value
            output.append(Instruction("CONST", instruction.dest, (value,)))
        elif instruction.op in {"ADD", "SUB", "MUL", "DIV", "SHL"}:
            if len(arguments) == 2 and all(isinstance(argument, int) for argument in arguments):
                value = _evaluate(instruction.op, int(arguments[0]), int(arguments[1]))
            else:
                value = None
            if value is not None:
                constants[str(instruction.dest)] = value
                output.append(Instruction("CONST", instruction.dest, (value,)))
            else:
                constants.pop(str(instruction.dest), None)
                output.append(Instruction(instruction.op, instruction.dest, arguments))
        else:
            if instruction.dest is not None:
                constants.pop(instruction.dest, None)
            output.append(Instruction(instruction.op, instruction.dest, arguments))
    return output


def common_subexpression_elimination(instructions: list[Instruction]) -> list[Instruction]:
    expressions: dict[tuple[str, tuple[Operand, ...]], str] = {}
    aliases: dict[str, Operand] = {}
    output: list[Instruction] = []

    def canonical(operand: Operand) -> Operand:
        seen = set()
        while isinstance(operand, str) and operand in aliases and operand not in seen:
            seen.add(operand)
            operand = aliases[operand]
        return operand

    for instruction in instructions:
        arguments = tuple(canonical(argument) for argument in instruction.args)
        if instruction.op in {"ADD", "MUL"}:
            arguments = tuple(sorted(arguments, key=lambda value: (isinstance(value, str), str(value))))
        if instruction.op in {"ADD", "SUB", "MUL", "DIV", "SHL"}:
            key = (instruction.op, arguments)
            if key in expressions:
                aliases[str(instruction.dest)] = expressions[key]
                continue
            expressions[key] = str(instruction.dest)
        output.append(Instruction(instruction.op, instruction.dest, arguments))
    return output


def strength_reduction(instructions: list[Instruction]) -> list[Instruction]:
    output = []
    for instruction in instructions:
        if instruction.op == "MUL":
            left, right = instruction.args
            if isinstance(left, int) and not isinstance(right, int):
                left, right = right, left
            if isinstance(right, int) and right > 1 and right & (right - 1) == 0:
                output.append(Instruction("SHL", instruction.dest, (left, right.bit_length() - 1)))
                continue
        output.append(instruction)
    return output


def dead_code_elimination(instructions: list[Instruction]) -> list[Instruction]:
    live: set[str] = set()
    kept: list[Instruction] = []
    for instruction in reversed(instructions):
        uses = {argument for argument in instruction.args if isinstance(argument, str) and argument.startswith("%")}
        if instruction.op == "PRINT":
            kept.append(instruction)
            live.update(uses)
            continue
        if instruction.dest is None:
            kept.append(instruction)
            live.update(uses)
            continue
        if instruction.dest not in live:
            continue
        kept.append(instruction)
        live.discard(instruction.dest)
        live.update(uses)
    return list(reversed(kept))


PASS_FUNCTIONS: dict[str, Callable[[list[Instruction]], list[Instruction]]] = {
    "constant_folding_propagation": constant_folding_propagation,
    "common_subexpression_elimination": common_subexpression_elimination,
    "strength_reduction": strength_reduction,
    "dead_code_elimination": dead_code_elimination,
}
PASS_COSTS = {
    "constant_folding_propagation": 3,
    "common_subexpression_elimination": 3,
    "strength_reduction": 2,
    "dead_code_elimination": 3,
}
FULL_PASS_ORDER = (
    "constant_folding_propagation",
    "common_subexpression_elimination",
    "strength_reduction",
    "dead_code_elimination",
)


def apply_pass(instructions: list[Instruction], name: str) -> list[Instruction]:
    if name not in PASS_FUNCTIONS:
        raise ValueError(f"unknown optimization pass: {name}")
    return PASS_FUNCTIONS[name](list(instructions))


def apply_passes(instructions: list[Instruction], order: tuple[str, ...] | list[str] = FULL_PASS_ORDER) -> list[Instruction]:
    result = list(instructions)
    for name in order:
        result = apply_pass(result, name)
    return result


def optimization_trace(instructions: list[Instruction], order: tuple[str, ...] = FULL_PASS_ORDER) -> list[dict[str, object]]:
    result = list(instructions)
    trace = [{"step": 0, "pass": "baseline", "instruction_count": len(result), "instructions_removed": 0}]
    for step, name in enumerate(order, start=1):
        before = len(result)
        result = apply_pass(result, name)
        trace.append({"step": step, "pass": name, "instruction_count": len(result), "instructions_removed": before - len(result)})
    return trace
