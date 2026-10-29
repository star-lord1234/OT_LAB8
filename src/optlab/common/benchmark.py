"""Repeated benchmark runner with a stable result record."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterable

from .measurement import measure_call
from .seeds import seed_everything, validate_seed


@dataclass(frozen=True)
class BenchmarkOutcome:
    objective: float | None
    correct: bool
    metrics: dict[str, float | int | str | bool | None] = field(default_factory=dict)
    notes: str = ""


@dataclass(frozen=True)
class BenchmarkRecord:
    track: str
    experiment: str
    algorithm: str
    repeat: int
    seed: int
    objective: float | None
    elapsed_seconds: float
    peak_python_bytes: int
    process_max_rss_bytes: int
    correct: bool
    metrics: dict[str, float | int | str | bool | None]
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


Operation = Callable[[int], BenchmarkOutcome]


def run_repeated(
    *,
    track: str,
    experiment: str,
    algorithm: str,
    seeds: Iterable[int],
    operation: Operation,
) -> list[BenchmarkRecord]:
    """Run an operation once per seed and retain every raw measurement."""

    if not track or not experiment or not algorithm:
        raise ValueError("track, experiment, and algorithm must be non-empty")
    if not callable(operation):
        raise TypeError("operation must be callable")

    records: list[BenchmarkRecord] = []
    for repeat, seed in enumerate(seeds):
        validated_seed = validate_seed(seed)
        seed_everything(validated_seed)
        outcome, measurement = measure_call(operation, validated_seed)
        if not isinstance(outcome, BenchmarkOutcome):
            raise TypeError("operation must return BenchmarkOutcome")
        records.append(
            BenchmarkRecord(
                track=track.upper(),
                experiment=experiment,
                algorithm=algorithm,
                repeat=repeat,
                seed=validated_seed,
                objective=outcome.objective,
                elapsed_seconds=measurement.elapsed_seconds,
                peak_python_bytes=measurement.peak_python_bytes,
                process_max_rss_bytes=measurement.process_max_rss_bytes,
                correct=outcome.correct,
                metrics=dict(outcome.metrics),
                notes=outcome.notes,
            )
        )
    if not records:
        raise ValueError("at least one seed is required")
    return records
