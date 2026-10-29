"""Minimal real-process data, tensor-model, and pipeline parallel demonstrations."""

from __future__ import annotations

import multiprocessing as mp
import os
import time
import numpy as np


def _gradient_sums(arguments: tuple[np.ndarray, np.ndarray, np.ndarray, float]) -> tuple[np.ndarray, float, int, int]:
    x, y, weights, bias = arguments
    error = x @ weights + bias - y
    return 2.0 * x.T @ error, float(2.0 * np.sum(error)), len(x), os.getpid()


def _gradient_process(index: int, arguments, output_queue) -> None:
    output_queue.put((index, _gradient_sums(arguments)))


def data_parallel_gradient(seed: int = 20261029, processes: int = 2) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(512, 8))
    y = rng.normal(size=512)
    weights = rng.normal(size=8)
    bias = 0.25
    started = time.perf_counter()
    serial_w_sum, serial_b_sum, count, _ = _gradient_sums((x, y, weights, bias))
    serial_gradient = np.append(serial_w_sum / count, serial_b_sum / count)
    serial_seconds = time.perf_counter() - started

    x_chunks = np.array_split(x, processes)
    y_chunks = np.array_split(y, processes)
    context = mp.get_context("spawn")
    started = time.perf_counter()
    output_queue = context.Queue()
    workers = [context.Process(target=_gradient_process, args=(index, (xc, yc, weights, bias), output_queue)) for index, (xc, yc) in enumerate(zip(x_chunks, y_chunks))]
    for worker in workers:
        worker.start()
    indexed = [output_queue.get() for _ in workers]
    for worker in workers:
        worker.join()
        if worker.exitcode != 0:
            raise RuntimeError("data-parallel worker failed")
    partials = [row[1] for row in sorted(indexed)]
    parallel_seconds = time.perf_counter() - started
    total = sum(row[2] for row in partials)
    parallel_gradient = np.append(sum((row[0] for row in partials), start=np.zeros_like(weights)) / total, sum(row[1] for row in partials) / total)
    return {
        "form": "data_parallel",
        "serial_seconds": serial_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": serial_seconds / parallel_seconds,
        "max_absolute_error": float(np.max(np.abs(serial_gradient - parallel_gradient))),
        "serial_checksum": float(np.sum(serial_gradient)),
        "parallel_checksum": float(np.sum(parallel_gradient)),
        "worker_pids": sorted({row[3] for row in partials}),
        "processes": processes,
    }


def _hidden_partition(arguments: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]) -> tuple[np.ndarray, int]:
    x, weights_1, bias_1, weights_2 = arguments
    hidden = np.maximum(0.0, x @ weights_1 + bias_1)
    return hidden @ weights_2, os.getpid()


def _hidden_process(index: int, arguments, output_queue) -> None:
    output_queue.put((index, _hidden_partition(arguments)))


def model_parallel_forward(seed: int = 20261029, processes: int = 2) -> dict[str, object]:
    """Split hidden units across workers and reduce partial output tensors."""
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(256, 16))
    w1 = rng.normal(size=(16, 24))
    b1 = rng.normal(size=24)
    w2 = rng.normal(size=(24, 4))
    b2 = rng.normal(size=4)
    started = time.perf_counter()
    serial_output = np.maximum(0.0, x @ w1 + b1) @ w2 + b2
    serial_seconds = time.perf_counter() - started
    slices = np.array_split(np.arange(w1.shape[1]), processes)
    arguments = [(x, w1[:, part], b1[part], w2[part, :]) for part in slices]
    context = mp.get_context("spawn")
    started = time.perf_counter()
    output_queue = context.Queue()
    workers = [context.Process(target=_hidden_process, args=(index, argument, output_queue)) for index, argument in enumerate(arguments)]
    for worker in workers:
        worker.start()
    indexed = [output_queue.get() for _ in workers]
    for worker in workers:
        worker.join()
        if worker.exitcode != 0:
            raise RuntimeError("model-parallel worker failed")
    partials = [row[1] for row in sorted(indexed)]
    parallel_output = sum((row[0] for row in partials), start=np.zeros_like(serial_output)) + b2
    parallel_seconds = time.perf_counter() - started
    return {
        "form": "model_tensor_parallel",
        "serial_seconds": serial_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": serial_seconds / parallel_seconds,
        "max_absolute_error": float(np.max(np.abs(serial_output - parallel_output))),
        "serial_checksum": float(np.sum(serial_output)),
        "parallel_checksum": float(np.sum(parallel_output)),
        "worker_pids": sorted({row[1] for row in partials}),
        "processes": processes,
    }


def _pipeline_stage_one(input_queue, hidden_queue, w1: np.ndarray, b1: np.ndarray) -> None:
    while True:
        item = input_queue.get()
        if item is None:
            hidden_queue.put(None)
            return
        index, batch = item
        hidden_queue.put((index, np.maximum(0.0, batch @ w1 + b1), os.getpid()))


def _pipeline_stage_two(hidden_queue, output_queue, w2: np.ndarray, b2: np.ndarray) -> None:
    while True:
        item = hidden_queue.get()
        if item is None:
            output_queue.put(None)
            return
        index, hidden, stage_one_pid = item
        output_queue.put((index, hidden @ w2 + b2, stage_one_pid, os.getpid()))


def pipeline_parallel_forward(seed: int = 20261029, microbatches: int = 8) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    batches = [rng.normal(size=(32, 12)) for _ in range(microbatches)]
    w1, b1 = rng.normal(size=(12, 16)), rng.normal(size=16)
    w2, b2 = rng.normal(size=(16, 3)), rng.normal(size=3)
    started = time.perf_counter()
    serial = [np.maximum(0.0, batch @ w1 + b1) @ w2 + b2 for batch in batches]
    serial_seconds = time.perf_counter() - started

    context = mp.get_context("spawn")
    input_queue, hidden_queue, output_queue = context.Queue(2), context.Queue(2), context.Queue()
    stage_one = context.Process(target=_pipeline_stage_one, args=(input_queue, hidden_queue, w1, b1))
    stage_two = context.Process(target=_pipeline_stage_two, args=(hidden_queue, output_queue, w2, b2))
    started = time.perf_counter()
    stage_one.start()
    stage_two.start()
    for index, batch in enumerate(batches):
        input_queue.put((index, batch))
    input_queue.put(None)
    received = []
    while True:
        item = output_queue.get()
        if item is None:
            break
        received.append(item)
    stage_one.join()
    stage_two.join()
    if stage_one.exitcode or stage_two.exitcode:
        raise RuntimeError("pipeline worker failed")
    parallel_seconds = time.perf_counter() - started
    received.sort(key=lambda row: row[0])
    maximum_error = max(float(np.max(np.abs(expected - actual[1]))) for expected, actual in zip(serial, received))
    return {
        "form": "pipeline_parallel",
        "serial_seconds": serial_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": serial_seconds / parallel_seconds,
        "max_absolute_error": maximum_error,
        "serial_checksum": float(sum(np.sum(value) for value in serial)),
        "parallel_checksum": float(sum(np.sum(row[1]) for row in received)),
        "worker_pids": sorted({received[0][2], received[0][3]}),
        "processes": 2,
        "microbatches": microbatches,
    }


def run_parallel_forms(seed: int = 20261029) -> list[dict[str, object]]:
    return [data_parallel_gradient(seed), model_parallel_forward(seed), pipeline_parallel_forward(seed)]
