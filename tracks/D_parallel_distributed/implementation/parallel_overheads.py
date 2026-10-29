"""Controlled locality, synchronization, and communication experiments."""

from __future__ import annotations

import multiprocessing as mp
import os
import time
from concurrent.futures import ProcessPoolExecutor


def _payload_values(seed: int, size: int) -> list[int]:
    return [((index * 1103515245 + seed * 12345) & 0xFFFF) for index in range(size)]


def sum_transferred_payload(payload: list[int]) -> tuple[int, int]:
    return sum(payload), os.getpid()


def generate_and_sum(specification: tuple[int, int]) -> tuple[int, int]:
    seed, size = specification
    return sum(_payload_values(seed, size)), os.getpid()


def _ack_payload(payload: list[int]) -> tuple[int, int]:
    return len(payload), os.getpid()


def _ack_compact(specification: tuple[int, int]) -> tuple[int, int]:
    return specification[1], os.getpid()


def communication_experiment(processes: int = 2, payload_size: int = 250_000) -> dict[str, object]:
    """Compare large and compact equivalent messages in one warmed pool."""
    specifications = [(seed, payload_size) for seed in range(processes * 2)]
    payloads = [_payload_values(*specification) for specification in specifications]
    context = mp.get_context("spawn")
    with ProcessPoolExecutor(max_workers=processes, mp_context=context) as pool:
        list(pool.map(_ack_compact, specifications))  # Exclude one-time spawn startup.
        started = time.perf_counter()
        transferred = list(pool.map(_ack_payload, payloads))
        transfer_seconds = time.perf_counter() - started
        started = time.perf_counter()
        compact = list(pool.map(_ack_compact, specifications))
        compact_seconds = time.perf_counter() - started
    if [row[0] for row in transferred] != [row[0] for row in compact]:
        raise AssertionError("communication variants produced different sums")
    return {
        "experiment": "communication",
        "processes": processes,
        "payload_size_integers": payload_size,
        "approx_payload_bytes": processes * 2 * payload_size * 8,
        "transferred_payload_seconds": transfer_seconds,
        "compact_message_seconds": compact_seconds,
        "communication_overhead_seconds": transfer_seconds - compact_seconds,
        "large_over_compact_ratio": transfer_seconds / compact_seconds,
        "checksum": sum(sum(payload) for payload in payloads),
        "transferred_worker_pids": sorted({row[1] for row in transferred}),
        "compact_worker_pids": sorted({row[1] for row in compact}),
    }


def _row_major(matrix: list[list[int]]) -> int:
    return sum(value for row in matrix for value in row)


def _column_major(matrix: list[list[int]]) -> int:
    width = len(matrix[0])
    return sum(matrix[row][column] for column in range(width) for row in range(len(matrix)))


def locality_experiment(size: int = 600, repeats: int = 3) -> dict[str, object]:
    """Compare cache-friendly and pointer-heavy traversal of identical data."""
    matrix = [[(row * size + column) % 97 for column in range(size)] for row in range(size)]
    started = time.perf_counter()
    row_checksum = sum(_row_major(matrix) for _ in range(repeats))
    row_seconds = time.perf_counter() - started
    started = time.perf_counter()
    column_checksum = sum(_column_major(matrix) for _ in range(repeats))
    column_seconds = time.perf_counter() - started
    if row_checksum != column_checksum:
        raise AssertionError("locality variants traversed different values")
    return {
        "experiment": "locality",
        "matrix_size": size,
        "repeats": repeats,
        "row_major_seconds": row_seconds,
        "column_major_seconds": column_seconds,
        "column_over_row_ratio": column_seconds / row_seconds,
        "checksum": row_checksum,
    }


def _locked_increments(counter, iterations: int) -> None:
    for _ in range(iterations):
        with counter.get_lock():
            counter.value += 1


def _local_increments(iterations: int) -> tuple[int, int]:
    total = 0
    for _ in range(iterations):
        total += 1
    return total, os.getpid()


def _local_increment_process(iterations: int, output_queue) -> None:
    output_queue.put(_local_increments(iterations))


def synchronization_experiment(processes: int = 2, iterations: int = 20_000) -> dict[str, object]:
    """Compare a lock per update with independent local reduction."""
    context = mp.get_context("spawn")
    counter = context.Value("q", 0, lock=True)
    workers = [context.Process(target=_locked_increments, args=(counter, iterations)) for _ in range(processes)]
    started = time.perf_counter()
    for worker in workers:
        worker.start()
    pids = [worker.pid for worker in workers]
    for worker in workers:
        worker.join()
        if worker.exitcode != 0:
            raise RuntimeError(f"locked worker failed with exit code {worker.exitcode}")
    locked_seconds = time.perf_counter() - started

    started = time.perf_counter()
    output_queue = context.Queue()
    local_workers = [context.Process(target=_local_increment_process, args=(iterations, output_queue)) for _ in range(processes)]
    for worker in local_workers:
        worker.start()
    local_results = [output_queue.get() for _ in local_workers]
    for worker in local_workers:
        worker.join()
        if worker.exitcode != 0:
            raise RuntimeError("local reduction worker failed")
    reduced_seconds = time.perf_counter() - started
    reduced_total = sum(row[0] for row in local_results)
    if counter.value != reduced_total:
        raise AssertionError("synchronization variants produced different totals")
    return {
        "experiment": "synchronization",
        "processes": processes,
        "increments_per_process": iterations,
        "locked_shared_counter_seconds": locked_seconds,
        "local_then_reduce_seconds": reduced_seconds,
        "lock_overhead_seconds": locked_seconds - reduced_seconds,
        "total": int(counter.value),
        "locked_worker_pids": pids,
        "reduction_worker_pids": sorted({row[1] for row in local_results}),
    }


def run_overhead_experiments() -> list[dict[str, object]]:
    return [locality_experiment(), synchronization_experiment(), communication_experiment()]
