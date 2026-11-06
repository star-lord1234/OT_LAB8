"""FIFO, length-aware greedy, and exact local 0/1-DP batch selectors."""

from __future__ import annotations

from itertools import combinations

from .models import Request, SimulationConfig, batch_feasible


STRATEGIES = ("fcfs", "greedy_length", "dynamic_programming")


def _urgent_request(pending: list[Request], dispatch_time: float, config: SimulationConfig) -> Request | None:
    overdue = [request for request in pending if request.arrival_time + config.max_batch_wait <= dispatch_time + 1e-12]
    return min(overdue, key=lambda request: (request.deadline, request.arrival_time, request.request_id)) if overdue else None


def choose_fcfs(pending: list[Request], dispatch_time: float, config: SimulationConfig) -> list[Request]:
    del dispatch_time
    ordered = sorted(pending, key=lambda request: (request.arrival_time, request.request_id))
    chosen: list[Request] = []
    for request in ordered:
        if batch_feasible([*chosen, request], config):
            chosen.append(request)
        else:
            break
    return chosen


def choose_greedy(pending: list[Request], dispatch_time: float, config: SimulationConfig) -> list[Request]:
    urgent = _urgent_request(pending, dispatch_time, config)
    anchor = urgent or min(pending, key=lambda request: (request.processing_cost, request.token_length, request.deadline, request.request_id))
    chosen = [anchor]
    candidates = [request for request in pending if request.request_id != anchor.request_id]
    candidates.sort(key=lambda request: (
        abs(request.token_length - anchor.token_length),
        request.deadline,
        request.processing_cost,
        request.request_id,
    ))
    for request in candidates:
        if batch_feasible([*chosen, request], config):
            chosen.append(request)
    return chosen


def batch_selection_score(requests: list[Request], dispatch_time: float, config: SimulationConfig) -> float:
    if not batch_feasible(requests, config):
        return float("-inf")
    maximum = max(request.token_length for request in requests)
    score = 0.0
    for request in requests:
        waiting_ratio = min(3.0, max(0.0, dispatch_time - request.arrival_time) / config.max_batch_wait)
        compatibility = request.token_length / maximum
        score += 1.0 + 2.0 * waiting_ratio + 0.35 * compatibility
    return score


def _selection_key(requests: list[Request], dispatch_time: float, config: SimulationConfig) -> tuple[float, int, int, tuple[int, ...]]:
    return (
        batch_selection_score(requests, dispatch_time, config),
        len(requests),
        -sum(request.token_length for request in requests),
        tuple(-request.request_id for request in sorted(requests, key=lambda item: item.request_id)),
    )


def choose_dp(pending: list[Request], dispatch_time: float, config: SimulationConfig) -> list[Request]:
    """Solve the local batch-selection score exactly within a bounded online lookahead."""
    candidates = sorted(pending, key=lambda request: (request.arrival_time, request.request_id))[: config.dp_lookahead]
    urgent = _urgent_request(pending, dispatch_time, config)
    if urgent is not None and all(request.request_id != urgent.request_id for request in candidates):
        candidates[-1] = urgent
    forced_id = urgent.request_id if urgent is not None else None
    by_id = {request.request_id: request for request in candidates}
    best: list[Request] | None = None
    for maximum in sorted({request.token_length for request in candidates}):
        eligible = [request for request in candidates if request.token_length <= maximum]
        if forced_id is not None and (forced_id not in by_id or by_id[forced_id].token_length > maximum):
            continue
        count_limit = min(config.max_batch_size, config.padded_token_capacity // maximum)
        states: dict[tuple[int, int, bool], tuple[float, tuple[int, ...]]] = {(0, 0, False): (0.0, ())}
        for request in eligible:
            value = 1.0 + 2.0 * min(3.0, max(0.0, dispatch_time - request.arrival_time) / config.max_batch_wait) + 0.35 * request.token_length / maximum
            updates = dict(states)
            for (tokens, count, contains), (score, ids) in states.items():
                new_tokens, new_count = tokens + request.token_length, count + 1
                if new_tokens > config.token_capacity or new_count > count_limit:
                    continue
                key = (new_tokens, new_count, contains or request.request_id == forced_id)
                candidate = (score + value, (*ids, request.request_id))
                if key not in updates or candidate[0] > updates[key][0] + 1e-12 or (abs(candidate[0] - updates[key][0]) <= 1e-12 and candidate[1] < updates[key][1]):
                    updates[key] = candidate
            states = updates
        for (tokens, count, contains), (_, ids) in states.items():
            del tokens
            if count == 0 or (forced_id is not None and not contains):
                continue
            selection = [by_id[request_id] for request_id in ids]
            if batch_feasible(selection, config) and (best is None or _selection_key(selection, dispatch_time, config) > _selection_key(best, dispatch_time, config)):
                best = selection
    if best is None:
        fallback = urgent or min(candidates, key=lambda request: (request.arrival_time, request.request_id))
        return [fallback]
    return sorted(best, key=lambda request: request.request_id)


def exhaustive_best_batch(pending: list[Request], dispatch_time: float, config: SimulationConfig) -> list[Request]:
    if len(pending) > 16:
        raise ValueError("exhaustive selector is limited to 16 candidates")
    urgent = _urgent_request(pending, dispatch_time, config)
    best: list[Request] | None = None
    for size in range(1, min(config.max_batch_size, len(pending)) + 1):
        for subset in combinations(pending, size):
            selection = list(subset)
            if urgent is not None and all(request.request_id != urgent.request_id for request in selection):
                continue
            if batch_feasible(selection, config) and (best is None or _selection_key(selection, dispatch_time, config) > _selection_key(best, dispatch_time, config)):
                best = selection
    if best is None:
        raise AssertionError("at least one request must be individually feasible")
    return sorted(best, key=lambda request: request.request_id)


def select_batch(strategy: str, pending: list[Request], dispatch_time: float, config: SimulationConfig) -> list[Request]:
    if strategy == "fcfs":
        return choose_fcfs(pending, dispatch_time, config)
    if strategy == "greedy_length":
        return choose_greedy(pending, dispatch_time, config)
    if strategy == "dynamic_programming":
        return choose_dp(pending, dispatch_time, config)
    raise ValueError(f"unknown strategy: {strategy}")
