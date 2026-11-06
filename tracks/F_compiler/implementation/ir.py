"""SSA-like three-address IR, lowering, serialization, and interpreter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .parser import Assign, Binary, Expression, Input, Let, Number, Print, Statement, Variable, parse


Operand = int | str
BINARY_OPS = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV"}


@dataclass(frozen=True)
class Instruction:
    op: str
    dest: str | None = None
    args: tuple[Operand, ...] = ()

    def text(self) -> str:
        arguments = ", ".join(str(value) for value in self.args)
        if self.dest is None:
            return f"{self.op} {arguments}".rstrip()
        return f"{self.dest} = {self.op} {arguments}".rstrip()


class Lowerer:
    def __init__(self) -> None:
        self.instructions: list[Instruction] = []
        self.environment: dict[str, Operand] = {}
        self.temporary = 0

    def new_temporary(self) -> str:
        name = f"%{self.temporary}"
        self.temporary += 1
        return name

    def expression(self, expression: Expression) -> Operand:
        if isinstance(expression, Number):
            destination = self.new_temporary()
            self.instructions.append(Instruction("CONST", destination, (expression.value,)))
            return destination
        if isinstance(expression, Variable):
            if expression.name not in self.environment:
                raise NameError(f"variable {expression.name!r} used before assignment")
            return self.environment[expression.name]
        if isinstance(expression, Binary):
            left, right = self.expression(expression.left), self.expression(expression.right)
            destination = self.new_temporary()
            self.instructions.append(Instruction(BINARY_OPS[expression.operator], destination, (left, right)))
            return destination
        raise TypeError(f"unsupported expression: {type(expression)}")

    def statement(self, statement: Statement) -> None:
        if isinstance(statement, Input):
            destination = self.new_temporary()
            self.instructions.append(Instruction("INPUT", destination, (statement.name,)))
            self.environment[statement.name] = destination
        elif isinstance(statement, (Let, Assign)):
            self.environment[statement.name] = self.expression(statement.expression)
        elif isinstance(statement, Print):
            self.instructions.append(Instruction("PRINT", None, (self.expression(statement.expression),)))
        else:
            raise TypeError(f"unsupported statement: {type(statement)}")

    def program(self, statements: list[Statement]) -> list[Instruction]:
        for statement in statements:
            self.statement(statement)
        return self.instructions


def lower(statements: list[Statement]) -> list[Instruction]:
    return Lowerer().program(statements)


def compile_source(source: str) -> list[Instruction]:
    return lower(parse(source))


def serialize(instructions: list[Instruction]) -> str:
    return "\n".join(instruction.text() for instruction in instructions) + ("\n" if instructions else "")


def code_size_bytes(instructions: list[Instruction]) -> int:
    return len(serialize(instructions).encode("utf-8"))


def _value(operand: Operand, values: Mapping[str, int]) -> int:
    return operand if isinstance(operand, int) else values[operand]


def execute(instructions: list[Instruction], inputs: Mapping[str, int] | None = None) -> tuple[int, ...]:
    input_values = dict(inputs or {})
    values: dict[str, int] = {}
    outputs: list[int] = []
    for instruction in instructions:
        if instruction.op == "INPUT":
            source_name = str(instruction.args[0])
            if source_name not in input_values:
                raise KeyError(f"missing input {source_name!r}")
            values[str(instruction.dest)] = int(input_values[source_name])
        elif instruction.op == "CONST":
            values[str(instruction.dest)] = int(instruction.args[0])
        elif instruction.op in {"ADD", "SUB", "MUL", "DIV"}:
            left, right = _value(instruction.args[0], values), _value(instruction.args[1], values)
            if instruction.op == "ADD": result = left + right
            elif instruction.op == "SUB": result = left - right
            elif instruction.op == "MUL": result = left * right
            else:
                if right == 0: raise ZeroDivisionError("integer division by zero")
                result = int(left / right)
            values[str(instruction.dest)] = result
        elif instruction.op == "SHL":
            values[str(instruction.dest)] = _value(instruction.args[0], values) << int(instruction.args[1])
        elif instruction.op == "PRINT":
            outputs.append(_value(instruction.args[0], values))
        else:
            raise ValueError(f"unknown IR opcode: {instruction.op}")
    return tuple(outputs)
