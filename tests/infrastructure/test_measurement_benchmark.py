from __future__ import annotations

from optlab.common.benchmark import BenchmarkOutcome, run_repeated
from optlab.common.measurement import measure_call


def test_measure_call_returns_value_time_and_memory() -> None:
    value, measurement = measure_call(lambda: sum(range(1000)))
    assert value == 499500
    assert measurement.elapsed_seconds >= 0
    assert measurement.peak_python_bytes >= 0
    assert measurement.process_max_rss_bytes > 0


def test_repeated_benchmark_retains_raw_runs() -> None:
    def operation(seed: int) -> BenchmarkOutcome:
        return BenchmarkOutcome(
            objective=float(seed % 10),
            correct=True,
            metrics={"iterations": 3},
            notes="test",
        )

    records = run_repeated(
        track="A",
        experiment="infrastructure-test",
        algorithm="identity",
        seeds=[10, 11, 12],
        operation=operation,
    )
    assert [record.repeat for record in records] == [0, 1, 2]
    assert [record.seed for record in records] == [10, 11, 12]
    assert [record.objective for record in records] == [0.0, 1.0, 2.0]
    assert all(record.correct for record in records)


def test_repeated_benchmark_rejects_no_runs() -> None:
    def operation(seed: int) -> BenchmarkOutcome:
        raise AssertionError("must not be called")

    try:
        run_repeated(
            track="A",
            experiment="empty",
            algorithm="none",
            seeds=[],
            operation=operation,
        )
    except ValueError as error:
        assert "at least one seed" in str(error)
    else:
        raise AssertionError("empty benchmark should fail")
