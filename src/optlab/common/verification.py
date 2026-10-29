"""Small correctness-verification records shared by all tracks."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class VerificationResult:
    name: str
    passed: bool
    detail: str


def verify_close(
    name: str,
    actual: float,
    expected: float,
    *,
    relative_tolerance: float = 1e-9,
    absolute_tolerance: float = 1e-12,
) -> VerificationResult:
    passed = math.isclose(
        actual,
        expected,
        rel_tol=relative_tolerance,
        abs_tol=absolute_tolerance,
    )
    return VerificationResult(
        name=name,
        passed=passed,
        detail=f"actual={actual!r}, expected={expected!r}",
    )


def verify_predicate(name: str, predicate: bool, detail: str) -> VerificationResult:
    return VerificationResult(name=name, passed=bool(predicate), detail=detail)


def require_all(results: Iterable[VerificationResult]) -> None:
    failures = [result for result in results if not result.passed]
    if failures:
        summary = "; ".join(f"{item.name}: {item.detail}" for item in failures)
        raise AssertionError(f"correctness verification failed: {summary}")
