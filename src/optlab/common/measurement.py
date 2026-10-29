"""Wall-clock and memory measurement helpers."""

from __future__ import annotations

import resource
import sys
import time
import tracemalloc
from dataclasses import dataclass
from typing import Any, Callable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class Measurement:
    elapsed_seconds: float
    peak_python_bytes: int
    process_max_rss_bytes: int


def _max_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def measure_call(function: Callable[..., T], *args: Any, **kwargs: Any) -> tuple[T, Measurement]:
    """Measure one call using a monotonic timer and Python allocation tracing."""

    if not callable(function):
        raise TypeError("function must be callable")

    tracemalloc.start()
    started = time.perf_counter()
    try:
        value = function(*args, **kwargs)
    finally:
        elapsed = time.perf_counter() - started
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    return value, Measurement(
        elapsed_seconds=elapsed,
        peak_python_bytes=int(peak),
        process_max_rss_bytes=_max_rss_bytes(),
    )
