"""Deterministic single-server discrete-event scheduling simulation."""

from __future__ import annotations

import time
from dataclasses import asdict

import numpy as np

from .models import BatchRecord, Request, SimulationConfig, batch_feasible, simulated_service_time
from .strategies import STRATEGIES, select_batch
from .workload import validate_workload


def _dispatch_time(strategy: str, current_time: float, pending: list[Request], config: SimulationConfig, has_future_arrivals: bool) -> float:
    if strategy == "fcfs" or len(pending) >= config.max_batch_size or not has_future_arrivals:
        return current_time
    oldest_hold_limit = min(request.arrival_time + config.max_batch_wait for request in pending)
    return max(current_time, min(current_time + config.batch_window, oldest_hold_limit))


def objective_from_request_rows(request_rows: list[dict[str, object]], total_busy_time: float, config: SimulationConfig) -> float:
    mean_latency = float(np.mean([float(row["latency"]) for row in request_rows]))
    mean_tardiness = float(np.mean([float(row["tardiness"]) for row in request_rows]))
    return mean_latency + config.tardiness_penalty * mean_tardiness + config.compute_weight * total_busy_time / len(request_rows)


def verify_schedule(requests: list[Request], batches: list[BatchRecord], request_rows: list[dict[str, object]], config: SimulationConfig) -> dict[str, object]:
    expected_ids = {request.request_id for request in requests}
    processed_ids = [request_id for batch in batches for request_id in batch.request_ids]
    row_ids = [int(row["request_id"]) for row in request_rows]
    request_by_id = {request.request_id: request for request in requests}
    errors: list[str] = []
    if len(processed_ids) != len(set(processed_ids)):
        errors.append("a request was processed more than once")
    if set(processed_ids) != expected_ids or set(row_ids) != expected_ids:
        errors.append("processed request IDs differ from the workload")
    previous_end = float("-inf")
    for batch in batches:
        selected = [request_by_id[request_id] for request_id in batch.request_ids]
        if not batch_feasible(selected, config):
            errors.append(f"batch {batch.batch_id} violates capacity")
        if batch.start_time + 1e-12 < previous_end:
            errors.append(f"batch {batch.batch_id} overlaps its predecessor")
        if any(batch.start_time + 1e-12 < request.arrival_time for request in selected):
            errors.append(f"batch {batch.batch_id} starts before an arrival")
        expected_service = simulated_service_time(selected, config)
        if abs(expected_service - batch.service_time) > 1e-10 or abs(batch.end_time - batch.start_time - batch.service_time) > 1e-10:
            errors.append(f"batch {batch.batch_id} has inconsistent service time")
        if batch.formation_wait < -1e-12 or batch.formation_wait > config.batch_window + 1e-10:
            errors.append(f"batch {batch.batch_id} violates the formation-window constraint")
        previous_end = batch.end_time
    rows_by_id = {int(row["request_id"]): row for row in request_rows}
    for request in requests:
        row = rows_by_id.get(request.request_id)
        if row is None:
            continue
        if abs(float(row["waiting_time"]) - (float(row["start_time"]) - request.arrival_time)) > 1e-10:
            errors.append(f"request {request.request_id} has an incorrect waiting time")
        if abs(float(row["latency"]) - (float(row["completion_time"]) - request.arrival_time)) > 1e-10:
            errors.append(f"request {request.request_id} has an incorrect latency")
        expected_tardiness = max(0.0, float(row["completion_time"]) - request.deadline)
        if abs(float(row["tardiness"]) - expected_tardiness) > 1e-10:
            errors.append(f"request {request.request_id} has incorrect tardiness")
    return {
        "valid": not errors,
        "request_count": len(requests),
        "processed_count": len(processed_ids),
        "unique_processed_count": len(set(processed_ids)),
        "batch_count": len(batches),
        "errors": errors,
        "capacity_constraints_checked": True,
        "formation_wait_constraint_checked": True,
        "objective_components_checked": True,
    }


def simulate(requests: list[Request], strategy: str, config: SimulationConfig) -> dict[str, object]:
    if strategy not in STRATEGIES:
        raise ValueError(f"strategy must be one of {STRATEGIES}")
    validate_workload(requests, config)
    started = time.perf_counter()
    ordered = list(requests)
    next_index = 0
    pending: list[Request] = []
    batches: list[BatchRecord] = []
    request_rows: list[dict[str, object]] = []
    current_time = ordered[0].arrival_time
    while next_index < len(ordered) or pending:
        if not pending and next_index < len(ordered):
            current_time = max(current_time, ordered[next_index].arrival_time)
        while next_index < len(ordered) and ordered[next_index].arrival_time <= current_time + 1e-12:
            pending.append(ordered[next_index])
            next_index += 1
        decision_time = current_time
        dispatch_time = _dispatch_time(strategy, current_time, pending, config, next_index < len(ordered))
        while next_index < len(ordered) and ordered[next_index].arrival_time <= dispatch_time + 1e-12:
            pending.append(ordered[next_index])
            next_index += 1
        selected = select_batch(strategy, pending, dispatch_time, config)
        selected_ids = {request.request_id for request in selected}
        pending = [request for request in pending if request.request_id not in selected_ids]
        service = simulated_service_time(selected, config)
        completion = dispatch_time + service
        token_sum = sum(request.token_length for request in selected)
        padded_tokens = len(selected) * max(request.token_length for request in selected)
        batch_id = len(batches)
        batches.append(BatchRecord(
            batch_id=batch_id,
            strategy=strategy,
            request_ids=tuple(request.request_id for request in selected),
            decision_time=decision_time,
            start_time=dispatch_time,
            end_time=completion,
            service_time=service,
            formation_wait=dispatch_time - decision_time,
            request_count=len(selected),
            token_sum=token_sum,
            padded_tokens=padded_tokens,
            token_capacity=config.token_capacity,
            padded_token_capacity=config.padded_token_capacity,
            token_efficiency=token_sum / padded_tokens,
            token_capacity_utilization=token_sum / config.token_capacity,
            padded_capacity_utilization=padded_tokens / config.padded_token_capacity,
        ))
        for request in selected:
            waiting = dispatch_time - request.arrival_time
            latency = completion - request.arrival_time
            tardiness = max(0.0, completion - request.deadline)
            request_rows.append({
                "request_id": request.request_id,
                "batch_id": batch_id,
                "strategy": strategy,
                "arrival_time": request.arrival_time,
                "token_length": request.token_length,
                "processing_cost": request.processing_cost,
                "deadline": request.deadline,
                "start_time": dispatch_time,
                "completion_time": completion,
                "waiting_time": waiting,
                "latency": latency,
                "tardiness": tardiness,
                "deadline_met": tardiness <= 1e-12,
            })
        current_time = completion
    request_rows.sort(key=lambda row: int(row["request_id"]))
    total_busy = sum(batch.service_time for batch in batches)
    makespan = batches[-1].end_time - requests[0].arrival_time
    latencies = np.asarray([float(row["latency"]) for row in request_rows])
    waiting = np.asarray([float(row["waiting_time"]) for row in request_rows])
    tardiness = np.asarray([float(row["tardiness"]) for row in request_rows])
    verification = verify_schedule(requests, batches, request_rows, config)
    objective = objective_from_request_rows(request_rows, total_busy, config)
    metrics = {
        "strategy": strategy,
        "simulated": True,
        "requests": len(requests),
        "batches": len(batches),
        "objective": objective,
        "mean_latency": float(np.mean(latencies)),
        "p95_latency": float(np.percentile(latencies, 95)),
        "p99_latency": float(np.percentile(latencies, 99)),
        "mean_waiting_time": float(np.mean(waiting)),
        "p95_waiting_time": float(np.percentile(waiting, 95)),
        "mean_tardiness": float(np.mean(tardiness)),
        "deadline_misses": int(np.sum(tardiness > 1e-12)),
        "deadline_miss_rate": float(np.mean(tardiness > 1e-12)),
        "throughput_requests_per_time": len(requests) / makespan,
        "makespan": makespan,
        "total_busy_time": total_busy,
        "server_utilization": total_busy / makespan,
        "mean_batch_size": float(np.mean([batch.request_count for batch in batches])),
        "mean_token_efficiency": float(np.mean([batch.token_efficiency for batch in batches])),
        "mean_token_capacity_utilization": float(np.mean([batch.token_capacity_utilization for batch in batches])),
        "mean_padded_capacity_utilization": float(np.mean([batch.padded_capacity_utilization for batch in batches])),
        "simulation_runtime_seconds": time.perf_counter() - started,
        "correct": verification["valid"],
        "batch_window_used": 0.0 if strategy == "fcfs" else config.batch_window,
    }
    recalculated = objective_from_request_rows(request_rows, total_busy, config)
    verification["reported_objective"] = objective
    verification["recalculated_objective"] = recalculated
    verification["objective_absolute_error"] = abs(objective - recalculated)
    return {
        "metrics": metrics,
        "batches": [batch.to_mapping() for batch in batches],
        "request_rows": request_rows,
        "verification": verification,
        "config": asdict(config),
    }
