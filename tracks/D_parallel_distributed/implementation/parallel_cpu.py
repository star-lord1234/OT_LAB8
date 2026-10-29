"""Spawn-safe CPU parallel benchmarks and scaling-law calculations."""

from __future__ import annotations

import multiprocessing as mp
import os
import statistics
import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Iterable


Task = tuple[int, int]


def cpu_kernel(task: Task) -> dict[str, object]:
    """A deterministic, CPU-bound integer kernel suitable for process workers."""
    task_id, iterations = task
    started = time.perf_counter()
    value = (task_id + 1) * 104729
    modulus = 2_147_483_647
    for index in range(iterations):
        value = (value * 48271 + index + task_id) % modulus
        value ^= value >> 7
    return {
        "task_id": task_id,
        "iterations": iterations,
        "checksum": int(value),
        "worker_pid": os.getpid(),
        "compute_seconds": time.perf_counter() - started,
    }


def _run_chunk(tasks: list[Task]) -> list[dict[str, object]]:
    return [cpu_kernel(task) for task in tasks]


def default_workload(scale: int = 1) -> list[Task]:
    """Heterogeneous ordering exposes contiguous static-chunk imbalance."""
    units = [220_000, 200_000, 180_000, 160_000, 65_000, 60_000, 55_000, 50_000, 45_000, 40_000, 35_000, 30_000]
    return [(index, max(1, units[index] * scale)) for index in range(len(units))]


def _summarize_results(method: str, processes: int, wall: float, results: list[dict[str, object]]) -> dict[str, object]:
    loads: dict[int, float] = {}
    for row in results:
        pid = int(row["worker_pid"])
        loads[pid] = loads.get(pid, 0.0) + float(row["compute_seconds"])
    mean_load = statistics.fmean(loads.values())
    return {
        "method": method,
        "processes": processes,
        "makespan_seconds": wall,
        "task_compute_seconds": sum(float(row["compute_seconds"]) for row in results),
        "worker_pids": sorted(loads),
        "worker_count_observed": len(loads),
        "worker_load_seconds": {str(pid): value for pid, value in sorted(loads.items())},
        "load_imbalance_ratio": max(loads.values()) / mean_load if mean_load else 1.0,
        "checksum": sum(int(row["checksum"]) for row in sorted(results, key=lambda item: int(item["task_id"]))),
        "task_count": len(results),
    }


def run_serial(tasks: Iterable[Task]) -> dict[str, object]:
    task_list = list(tasks)
    started = time.perf_counter()
    results = [cpu_kernel(task) for task in task_list]
    return _summarize_results("serial", 1, time.perf_counter() - started, results)


def _contiguous_chunks(tasks: list[Task], processes: int) -> list[list[Task]]:
    return [tasks[index * len(tasks) // processes : (index + 1) * len(tasks) // processes] for index in range(processes)]


def run_static(tasks: Iterable[Task], processes: int) -> dict[str, object]:
    task_list = list(tasks)
    context = mp.get_context("spawn")
    started = time.perf_counter()
    results: list[dict[str, object]] = []
    with ProcessPoolExecutor(max_workers=processes, mp_context=context) as pool:
        futures = [pool.submit(_run_chunk, chunk) for chunk in _contiguous_chunks(task_list, processes)]
        for future in futures:
            results.extend(future.result())
    return _summarize_results("static_contiguous", processes, time.perf_counter() - started, results)


def run_dynamic(tasks: Iterable[Task], processes: int) -> dict[str, object]:
    """Use an atomic-task central shared queue for real dynamic scheduling."""
    task_list = list(tasks)
    context = mp.get_context("spawn")
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=processes, mp_context=context) as pool:
        futures = [pool.submit(cpu_kernel, task) for task in task_list]
        results = [future.result() for future in as_completed(futures)]
    return _summarize_results("dynamic_shared_queue", processes, time.perf_counter() - started, results)


def simulate_work_stealing(tasks: Iterable[Task], processes: int) -> dict[str, object]:
    """Discrete-event deque-stealing simulation using task iterations as cost."""
    task_list = list(tasks)
    queues = [deque(chunk) for chunk in _contiguous_chunks(task_list, processes)]
    active: list[tuple[float, Task, int] | None] = [None] * processes
    schedule: list[dict[str, object]] = []
    stolen_tasks = 0

    def assign(worker: int, now: float) -> None:
        nonlocal stolen_tasks
        origin = worker
        stolen = False
        if queues[worker]:
            task = queues[worker].popleft()
        else:
            victims = [index for index in range(processes) if queues[index]]
            if not victims:
                active[worker] = None
                return
            origin = max(victims, key=lambda index: sum(item[1] for item in queues[index]))
            task = queues[origin].pop()
            stolen = True
            stolen_tasks += 1
        finish = now + task[1]
        active[worker] = (finish, task, origin)
        schedule.append({"worker": worker, "task_id": task[0], "start_cost_units": now, "finish_cost_units": finish, "origin_worker": origin, "stolen": stolen})

    for worker in range(processes):
        assign(worker, 0.0)
    now = 0.0
    while any(item is not None for item in active):
        now = min(item[0] for item in active if item is not None)
        finished = [worker for worker, item in enumerate(active) if item is not None and item[0] == now]
        for worker in finished:
            active[worker] = None
        for worker in finished:
            assign(worker, now)
    static_loads = [sum(task[1] for task in chunk) for chunk in _contiguous_chunks(task_list, processes)]
    completed = [int(row["task_id"]) for row in schedule]
    if sorted(completed) != sorted(task[0] for task in task_list):
        raise AssertionError("work-stealing simulation lost or duplicated tasks")
    ideal = sum(task[1] for task in task_list) / processes
    return {
        "model": "discrete-event local deque with idle-worker stealing from the most-loaded victim queue",
        "processes": processes,
        "tasks": len(task_list),
        "steals": stolen_tasks,
        "static_contiguous_makespan_cost_units": max(static_loads),
        "work_stealing_makespan_cost_units": now,
        "ideal_lower_bound_cost_units": ideal,
        "simulated_parallel_efficiency": ideal / now,
        "schedule": schedule,
        "not_a_wall_clock_result": True,
    }


def add_scaling_metrics(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    serials = [float(row["makespan_seconds"]) for row in rows if row["method"] == "serial"]
    baseline = statistics.median(serials)
    enriched = []
    for row in rows:
        result = dict(row)
        speedup = baseline / float(row["makespan_seconds"])
        processes = int(row["processes"])
        result.update({
            "serial_baseline_seconds": baseline,
            "speedup": speedup,
            "parallel_efficiency": speedup / processes,
            "parallel_overhead_seconds": processes * float(row["makespan_seconds"]) - baseline,
        })
        enriched.append(result)
    return enriched


def scaling_laws(rows: list[dict[str, object]]) -> dict[str, object]:
    """Fit an empirical serial fraction and report Amdahl/Gustafson predictions."""
    dynamic = [row for row in rows if row["method"] == "dynamic_shared_queue"]
    two = [float(row["speedup"]) for row in dynamic if int(row["processes"]) == 2]
    if not two:
        raise ValueError("a two-process dynamic result is required")
    measured_s2 = statistics.median(two)
    serial_fraction_raw = (1.0 / measured_s2 - 0.5) / 0.5
    serial_fraction = min(1.0, max(0.0, serial_fraction_raw))
    predictions = []
    for processes in (2, 4):
        predictions.append({
            "processes": processes,
            "amdahl_speedup": 1.0 / (serial_fraction + (1.0 - serial_fraction) / processes),
            "gustafson_scaled_speedup": processes - serial_fraction * (processes - 1),
        })
    return {
        "fit_source": "median measured dynamic-queue speedup at p=2",
        "measured_speedup_p2": measured_s2,
        "empirical_serial_fraction_raw": serial_fraction_raw,
        "empirical_serial_fraction_clamped": serial_fraction,
        "predictions": predictions,
        "interpretation_caveat": "The fitted fraction includes process startup, scheduling, and communication overhead; Gustafson assumes workload scales with processor count.",
    }


def run_parallel_scaling(repeats: int = 3, scale: int = 1) -> tuple[list[dict[str, object]], dict[str, object]]:
    tasks = default_workload(scale)
    rows: list[dict[str, object]] = []
    for repeat in range(repeats):
        for runner, processes in ((run_serial, 1), (run_static, 2), (run_dynamic, 2), (run_static, 4), (run_dynamic, 4)):
            row = runner(tasks) if processes == 1 else runner(tasks, processes)
            row["repeat"] = repeat
            row["spawn_start_method"] = "spawn"
            rows.append(row)
    enriched = add_scaling_metrics(rows)
    checksums = {int(row["checksum"]) for row in enriched}
    if len(checksums) != 1:
        raise AssertionError("parallel variants did not execute identical work")
    return enriched, scaling_laws(enriched)
