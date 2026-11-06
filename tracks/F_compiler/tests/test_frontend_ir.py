from __future__ import annotations

import pytest

from tracks.F_compiler.implementation.ir import compile_source, execute, serialize
from tracks.F_compiler.implementation.lexer import lex
from tracks.F_compiler.implementation.parser import Binary, Let, parse
from tracks.F_compiler.implementation.programs import load_programs


def test_lexer_parser_precedence_and_comments() -> None:
    source = "// comment\nlet x = 2 + 3 * 4; print x;"
    tokens = lex(source)
    assert tokens[-1].kind == "EOF"
    statements = parse(source)
    assert isinstance(statements[0], Let)
    assert isinstance(statements[0].expression, Binary)
    assert statements[0].expression.operator == "+"
    assert isinstance(statements[0].expression.right, Binary)
    assert execute(compile_source(source)) == (14,)


def test_frontend_rejects_invalid_and_unbound_programs() -> None:
    with pytest.raises(SyntaxError):
        parse("let x = 1 print x;")
    with pytest.raises(NameError):
        compile_source("print missing;")


def test_unoptimized_ir_executes_all_representative_programs() -> None:
    for program in load_programs():
        instructions = compile_source(program.source)
        assert execute(instructions, program.inputs) == program.expected
        assert len(instructions) > 0
        assert serialize(instructions).endswith("\n")
