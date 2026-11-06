"""Lexer for the deliberately small Track F integer language."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int


TOKEN_PATTERN = re.compile(
    r"(?P<COMMENT>//[^\n]*)|(?P<NUMBER>\d+)|(?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)|"
    r"(?P<SYMBOL>[+\-*/=();])|(?P<SPACE>\s+)|(?P<MISMATCH>.)"
)
KEYWORDS = {"input": "INPUT", "let": "LET", "print": "PRINT"}


def lex(source: str) -> list[Token]:
    tokens: list[Token] = []
    for match in TOKEN_PATTERN.finditer(source):
        kind, value = match.lastgroup, match.group()
        if kind in {"SPACE", "COMMENT"}:
            continue
        if kind == "MISMATCH":
            raise SyntaxError(f"unexpected character {value!r} at offset {match.start()}")
        if kind == "IDENT":
            kind = KEYWORDS.get(value, "IDENT")
        elif kind == "SYMBOL":
            kind = value
        tokens.append(Token(str(kind), value, match.start()))
    tokens.append(Token("EOF", "", len(source)))
    return tokens
