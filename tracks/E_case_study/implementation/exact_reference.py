"""Tiny exhaustive offline schedule reference for independent validation."""

from __future__ import annotations

from itertools import combinations

from .models import Request, SimulationConfig, batch_feasible, simulated_service_time


def evaluate_plan(requests: list[Request], plan: list[tuple[int, ...]], config: SimulationConfig) -> dict[str, object]:
    by_id = {request.request_id: request for request in requests}
    flattened = [request_id for batch in plan for request_id in batch]
    if sorted(flattened) != sorted(by_id) or len(flattened) != len(set(flattened)):
        raise ValueError("plan must process every request exactly once")
    current = min(request.arrival_time for request in requests)
    total_latency = 0.0
    total_tardiness = 0.0
    total_busy = 0.0
    rows = []
    for batch_ids in plan:
        batch = [by_id[request_id] for request_id in batch_ids]
        if not batch_feasible(batch, config):
            raise ValueError("plan contains an infeasible batch")
        current = max(current, max(request.arrival_time for request in batch))
        service = simulated_service_time(batch, config)
        current += service
        total_busy += service
        for request in batch:
            latency = current - request.arrival_time
            tardiness = max(0.0, current - request.deadline)
            total_latency += latency
            total_tardiness += tardiness
            rows.append({"request_id": request.request_id, "completion_time": current, "latency": latency, "tardiness": tardiness})
    objective = total_latency / len(requests) + config.tardiness_penalty * total_tardiness / len(requests) + config.compute_weight * total_busy / len(requests)
    return {"objective": objective, "total_busy_time": total_busy, "rows": rows, "plan": [list(batch) for batch in plan]}


def exhaustive_offline_schedule(requests: list[Request], config: SimulationConfig) -> dict[str, object]:
    if len(requests) > 7:
        raise ValueError("offline exhaustive reference is limited to seven requests")
    if any(abs(request.arrival_time - requests[0].arrival_time) > 1e-12 for request in requests):
        raise ValueError("tiny reference requires simultaneous arrivals")
    by_id = {request.request_id: request for request in requests}
    best: dict[str, object] | None = None

    def search(remaining: tuple[int, ...], plan: list[tuple[int, ...]]) -> None:
        nonlocal best
        if not remaining:
            result = evaluate_plan(requests, plan, config)
            if best is None or float(result["objective"]) < float(best["objective"]) - 1e-12 or (abs(float(result["objective"]) - float(best["objective"])) <= 1e-12 and result["plan"] < best["plan"]):
                best = result
            return
        for size in range(1, min(config.max_batch_size, len(remaining)) + 1):
            for ids in combinations(remaining, size):
                if not batch_feasible([by_id[request_id] for request_id in ids], config):
                    continue
                chosen = set(ids)
                search(tuple(request_id for request_id in remaining if request_id not in chosen), [*plan, tuple(ids)])

    search(tuple(sorted(by_id)), [])
    if best is None:
        raise AssertionError("no feasible exhaustive schedule")
    best["evaluated_as_exact"] = True
    best["simulated"] = True
    return best


def tiny_reference_requests() -> list[Request]:
    lengths = (20, 24, 96, 100, 32, 104)
    return [Request(index, 0.0, length, 0.015 * length, 4.0 + 0.04 * length) for index, length in enumerate(lengths)]
