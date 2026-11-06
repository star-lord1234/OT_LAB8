"""Recursive-descent parser and tiny abstract syntax tree."""

from __future__ import annotations

from dataclasses import dataclass

from .lexer import Token, lex


@dataclass(frozen=True)
class Number:
    value: int


@dataclass(frozen=True)
class Variable:
    name: str


@dataclass(frozen=True)
class Binary:
    operator: str
    left: "Expression"
    right: "Expression"


Expression = Number | Variable | Binary


@dataclass(frozen=True)
class Input:
    name: str


@dataclass(frozen=True)
class Let:
    name: str
    expression: Expression


@dataclass(frozen=True)
class Assign:
    name: str
    expression: Expression


@dataclass(frozen=True)
class Print:
    expression: Expression


Statement = Input | Let | Assign | Print


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def accept(self, kind: str) -> Token | None:
        if self.current.kind == kind:
            token = self.current
            self.index += 1
            return token
        return None

    def expect(self, kind: str) -> Token:
        token = self.accept(kind)
        if token is None:
            raise SyntaxError(f"expected {kind}, got {self.current.kind} at offset {self.current.position}")
        return token

    def parse_program(self) -> list[Statement]:
        statements = []
        while self.current.kind != "EOF":
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self) -> Statement:
        if self.accept("INPUT"):
            name = self.expect("IDENT").value
            self.expect(";")
            return Input(name)
        if self.accept("LET"):
            name = self.expect("IDENT").value
            self.expect("=")
            expression = self.parse_expression()
            self.expect(";")
            return Let(name, expression)
        if self.accept("PRINT"):
            expression = self.parse_expression()
            self.expect(";")
            return Print(expression)
        if self.current.kind == "IDENT":
            name = self.expect("IDENT").value
            self.expect("=")
            expression = self.parse_expression()
            self.expect(";")
            return Assign(name, expression)
        raise SyntaxError(f"unexpected token {self.current.kind} at offset {self.current.position}")

    def parse_expression(self) -> Expression:
        expression = self.parse_term()
        while self.current.kind in {"+", "-"}:
            operator = self.current.kind
            self.index += 1
            expression = Binary(operator, expression, self.parse_term())
        return expression

    def parse_term(self) -> Expression:
        expression = self.parse_factor()
        while self.current.kind in {"*", "/"}:
            operator = self.current.kind
            self.index += 1
            expression = Binary(operator, expression, self.parse_factor())
        return expression

    def parse_factor(self) -> Expression:
        number = self.accept("NUMBER")
        if number:
            return Number(int(number.value))
        identifier = self.accept("IDENT")
        if identifier:
            return Variable(identifier.value)
        if self.accept("-"):
            return Binary("-", Number(0), self.parse_factor())
        if self.accept("("):
            expression = self.parse_expression()
            self.expect(")")
            return expression
        raise SyntaxError(f"expected expression at offset {self.current.position}")


def parse(source: str) -> list[Statement]:
    return Parser(lex(source)).parse_program()
