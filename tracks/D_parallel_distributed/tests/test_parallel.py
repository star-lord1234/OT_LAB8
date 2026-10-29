from __future__ import annotations

import math

from tracks.D_parallel_distributed.implementation.parallel_cpu import run_dynamic, run_serial, run_static, simulate_work_stealing
from tracks.D_parallel_distributed.implementation.parallel_forms import (
    data_parallel_gradient,
    model_parallel_forward,
    pipeline_parallel_forward,
)
from tracks.D_parallel_distributed.implementation.parallel_overheads import locality_experiment


def test_spawned_schedulers_execute_identical_cpu_work() -> None:
    tasks = [(index, 20_000 + 1_000 * index) for index in range(6)]
    serial = run_serial(tasks)
    static = run_static(tasks, 2)
    dynamic = run_dynamic(tasks, 2)
    assert serial["checksum"] == static["checksum"] == dynamic["checksum"]
    assert static["worker_count_observed"] >= 1
    assert dynamic["worker_count_observed"] >= 1
    assert static["worker_pids"] != serial["worker_pids"]


def test_work_stealing_simulation_preserves_tasks_and_rebalances() -> None:
    result = simulate_work_stealing([(0, 100), (1, 90), (2, 10), (3, 10), (4, 10), (5, 10)], 2)
    assert len(result["schedule"]) == 6
    assert result["steals"] > 0
    assert result["work_stealing_makespan_cost_units"] <= result["static_contiguous_makespan_cost_units"]


def test_data_model_and_pipeline_parallel_match_serial_results() -> None:
    rows = [data_parallel_gradient(), model_parallel_forward(), pipeline_parallel_forward(microbatches=4)]
    assert {row["form"] for row in rows} == {"data_parallel", "model_tensor_parallel", "pipeline_parallel"}
    for row in rows:
        assert row["max_absolute_error"] < 1e-10
        assert math.isclose(row["serial_checksum"], row["parallel_checksum"], rel_tol=1e-10, abs_tol=1e-10)
        assert all(pid > 0 for pid in row["worker_pids"])
        assert len(row["worker_pids"]) == 2


def test_locality_variants_traverse_the_same_data() -> None:
    result = locality_experiment(size=80, repeats=1)
    assert result["checksum"] > 0
    assert result["row_major_seconds"] > 0
    assert result["column_major_seconds"] > 0
