"""SQLite plan capture, result hashing, and repeated query measurement."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import statistics
import time
from dataclasses import dataclass

from .models import QUERIES, QuerySpec


@dataclass(frozen=True)
class QueryMeasurement:
    query: str
    weight: int
    median_latency_seconds: float
    mean_latency_seconds: float
    latency_std_seconds: float
    min_latency_seconds: float
    result_rows: int
    result_sha256: str
    plan: tuple[tuple[int, int, int, str], ...]


def result_digest(rows: list[tuple[object, ...]]) -> str:
    payload = json.dumps(rows, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def query_plan(connection: sqlite3.Connection, query: QuerySpec) -> tuple[tuple[int, int, int, str], ...]:
    rows = connection.execute("EXPLAIN QUERY PLAN " + query.sql, query.parameters).fetchall()
    return tuple((int(row[0]), int(row[1]), int(row[2]), str(row[3])) for row in rows)


def execute_query(connection: sqlite3.Connection, query: QuerySpec) -> list[tuple[object, ...]]:
    return connection.execute(query.sql, query.parameters).fetchall()


def measure_query(
    connection: sqlite3.Connection,
    query: QuerySpec,
    *,
    warmups: int,
    repetitions: int,
) -> QueryMeasurement:
    for _ in range(warmups):
        execute_query(connection, query)
    durations: list[float] = []
    rows: list[tuple[object, ...]] = []
    for _ in range(repetitions):
        started = time.perf_counter_ns()
        rows = execute_query(connection, query)
        durations.append((time.perf_counter_ns() - started) / 1e9)
    return QueryMeasurement(
        query=query.name,
        weight=query.weight,
        median_latency_seconds=statistics.median(durations),
        mean_latency_seconds=statistics.fmean(durations),
        latency_std_seconds=statistics.pstdev(durations),
        min_latency_seconds=min(durations),
        result_rows=len(rows),
        result_sha256=result_digest(rows),
        plan=query_plan(connection, query),
    )


def measure_workload(
    connection: sqlite3.Connection,
    *,
    warmups: int,
    repetitions: int,
) -> tuple[list[QueryMeasurement], float, float]:
    measurements = [
        measure_query(connection, query, warmups=warmups, repetitions=repetitions)
        for query in QUERIES
    ]
    weighted_seconds = sum(
        measurement.weight * measurement.median_latency_seconds
        for measurement in measurements
    )
    total_weight = sum(measurement.weight for measurement in measurements)
    weighted_mean = weighted_seconds / total_weight
    throughput = total_weight / weighted_seconds
    return measurements, weighted_mean, throughput
