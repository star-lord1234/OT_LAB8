"""End-to-end SQLite index-selection experiment."""

from __future__ import annotations

import shutil
import sqlite3
import statistics
import tempfile
import time
import os
import platform
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

from optlab.common.config import ExperimentConfig
from optlab.common.results import write_csv, write_json

from .database import SCHEMA_SQL, connect_database, database_size, generate_database
from .models import CANDIDATE_INDEXES, QUERIES, CandidateIndex
from .selection import (
    SelectionResult,
    dynamic_programming_select,
    greedy_select,
    ilp_select,
)
from .workload import QueryMeasurement, measure_workload


ROOT = Path(__file__).resolve().parents[3]


def _evaluate_database(
    base_path: Path,
    target_path: Path,
    indexes: tuple[CandidateIndex, ...],
    *,
    warmups: int,
    repetitions: int,
) -> tuple[list[QueryMeasurement], float, float, int, int]:
    shutil.copy2(base_path, target_path)
    connection = connect_database(target_path)
    try:
        base_bytes, page_size, _ = database_size(connection)
        for index in indexes:
            connection.execute(index.ddl)
        connection.commit()
        indexed_bytes, actual_page_size, _ = database_size(connection)
        if actual_page_size != page_size:
            raise AssertionError("SQLite page size changed within one configuration")
        measurements, weighted_latency, throughput = measure_workload(
            connection, warmups=warmups, repetitions=repetitions
        )
        return measurements, weighted_latency, throughput, indexed_bytes - base_bytes, page_size
    finally:
        connection.close()


def _summary_query_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["configuration"]), str(row["query"])), []).append(row)
    output = []
    for (configuration, query), group in sorted(grouped.items()):
        latencies = [float(row["median_latency_seconds"]) for row in group]
        output.append(
            {
                "configuration": configuration,
                "query": query,
                "weight": int(group[0]["weight"]),
                "repeats": len(group),
                "median_latency_seconds_mean": statistics.fmean(latencies),
                "median_latency_seconds_std": statistics.pstdev(latencies),
                "result_rows": int(group[0]["result_rows"]),
                "result_sha256": str(group[0]["result_sha256"]),
                "all_results_equivalent": all(bool(row["result_equivalent"]) for row in group),
            }
        )
    return output


def _summary_workload_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["configuration"]), []).append(row)
    output = []
    for configuration, group in sorted(grouped.items()):
        latency = [float(row["weighted_mean_latency_seconds"]) for row in group]
        throughput = [float(row["workload_throughput_queries_per_second"]) for row in group]
        overhead = [int(row["index_storage_bytes"]) for row in group]
        output.append(
            {
                "configuration": configuration,
                "selected_indexes": str(group[0]["selected_indexes"]),
                "repeats": len(group),
                "weighted_mean_latency_seconds_mean": statistics.fmean(latency),
                "weighted_mean_latency_seconds_std": statistics.pstdev(latency),
                "workload_throughput_queries_per_second_mean": statistics.fmean(throughput),
                "workload_throughput_queries_per_second_std": statistics.pstdev(throughput),
                "index_storage_bytes_mean": statistics.fmean(overhead),
                "index_storage_pages": int(group[0]["index_storage_pages"]),
                "within_budget": all(bool(row["within_budget"]) for row in group),
                "all_results_equivalent": all(bool(row["all_results_equivalent"]) for row in group),
            }
        )
    return output


def _plots(
    output_dir: Path,
    query_summary: list[dict[str, object]],
    workload_summary: list[dict[str, object]],
    candidates: list[dict[str, object]],
    budget_pages: int,
) -> None:
    configurations = ["baseline", "greedy", "ilp", "dynamic_programming"]
    queries = [query.name for query in QUERIES]
    indexed = {
        (str(row["configuration"]), str(row["query"])): row for row in query_summary
    }
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    width = 0.19
    positions = list(range(len(queries)))
    for offset, configuration in enumerate(configurations):
        values = [
            1000 * float(indexed[(configuration, query)]["median_latency_seconds_mean"])
            for query in queries
        ]
        axes[0].bar(
            [position + (offset - 1.5) * width for position in positions],
            values,
            width,
            label=configuration,
        )
    axes[0].set_xticks(positions, [query.replace("_", "\n") for query in queries], fontsize=7)
    axes[0].set_ylabel("Median latency (ms)")
    axes[0].set_title("Identical SQLite workload")
    axes[0].legend(fontsize=7)

    workload_index = {str(row["configuration"]): row for row in workload_summary}
    throughput = [
        float(workload_index[configuration]["workload_throughput_queries_per_second_mean"])
        for configuration in configurations
    ]
    axes[1].bar(configurations, throughput)
    axes[1].tick_params(axis="x", rotation=18)
    axes[1].set_ylabel("Weighted workload queries / second")
    axes[1].set_title("Measured workload throughput")
    figure.suptitle("Track H: SQLite index configurations")
    figure.tight_layout()
    figure.savefig(output_dir / "plots" / "workload_performance.png", dpi=160)
    plt.close(figure)

    names = [str(row["index"]).replace("idx_", "") for row in candidates]
    costs = [int(row["storage_pages"]) for row in candidates]
    benefits = [1000 * float(row["estimated_benefit_seconds"]) for row in candidates]
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].bar(names, costs)
    axes[0].axhline(budget_pages, color="red", linestyle="--", label="budget")
    axes[0].tick_params(axis="x", rotation=25)
    axes[0].set_ylabel("Isolated index storage (pages)")
    axes[0].set_title("Measured storage cost")
    axes[0].legend()
    axes[1].bar(names, benefits)
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].set_ylabel("Estimated weighted benefit (ms)")
    axes[1].set_title("Single-index timing benefit")
    figure.tight_layout()
    figure.savefig(output_dir / "plots" / "candidate_indexes.png", dpi=160)
    plt.close(figure)


def run_experiment(config: ExperimentConfig) -> dict[str, object]:
    parameters = config.parameters
    customer_count = int(parameters.get("customers", 1200))
    product_count = int(parameters.get("products", 600))
    order_count = int(parameters.get("orders", 15000))
    warmups = int(parameters.get("warmups", 3))
    repetitions = int(parameters.get("query_repetitions", 15))
    estimation_repetitions = int(parameters.get("estimation_repetitions", 9))
    budget_pages = int(parameters.get("storage_budget_pages", 100))
    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "plots").mkdir(exist_ok=True)
    cache_dir = ROOT / ".cache"
    cache_dir.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="track-h-", dir=cache_dir) as temporary:
        work_dir = Path(temporary)
        base_path = work_dir / "baseline.sqlite"
        dataset = generate_database(
            base_path,
            seed=config.base_seed,
            customer_count=customer_count,
            product_count=product_count,
            order_count=order_count,
        )
        baseline_measurements, baseline_cost, baseline_throughput, _, page_size = _evaluate_database(
            base_path,
            work_dir / "estimate_baseline.sqlite",
            (),
            warmups=warmups,
            repetitions=estimation_repetitions,
        )
        baseline_digests = {
            measurement.query: measurement.result_sha256 for measurement in baseline_measurements
        }
        baseline_by_query = {
            measurement.query: measurement for measurement in baseline_measurements
        }
        total_query_weight = sum(query.weight for query in QUERIES)

        candidate_rows: list[dict[str, object]] = []
        candidate_costs: list[int] = []
        candidate_benefits: list[float] = []
        for candidate in CANDIDATE_INDEXES:
            measurements, weighted_cost, throughput, storage_bytes, candidate_page_size = _evaluate_database(
                base_path,
                work_dir / f"estimate_{candidate.name}.sqlite",
                (candidate,),
                warmups=warmups,
                repetitions=estimation_repetitions,
            )
            if candidate_page_size != page_size or storage_bytes % page_size != 0:
                raise AssertionError("candidate index storage was not page aligned")
            if any(baseline_digests[m.query] != m.result_sha256 for m in measurements):
                raise AssertionError(f"candidate {candidate.name} changed a logical result")
            cost_pages = storage_bytes // page_size
            used_by_queries = [
                measurement.query
                for measurement in measurements
                if any(candidate.name in plan_row[3] for plan_row in measurement.plan)
            ]
            benefit = sum(
                measurement.weight
                * max(
                    0.0,
                    baseline_by_query[measurement.query].median_latency_seconds
                    - measurement.median_latency_seconds,
                )
                for measurement in measurements
                if measurement.query in used_by_queries
            ) / total_query_weight
            candidate_costs.append(cost_pages)
            candidate_benefits.append(benefit)
            candidate_rows.append(
                {
                    "index": candidate.name,
                    "table": candidate.table,
                    "columns": ",".join(candidate.columns),
                    "ddl": candidate.ddl,
                    "rationale": candidate.rationale,
                    "used_by_queries": ";".join(used_by_queries),
                    "storage_bytes": storage_bytes,
                    "storage_pages": cost_pages,
                    "weighted_latency_seconds": weighted_cost,
                    "workload_throughput_queries_per_second": throughput,
                    "estimated_benefit_seconds": benefit,
                    "benefit_per_page_seconds": benefit / cost_pages,
                }
            )

        names = [candidate.name for candidate in CANDIDATE_INDEXES]
        selection_results = [
            SelectionResult("baseline", (), 0, 0.0, baseline_cost, 0.0, True),
            greedy_select(names, candidate_costs, candidate_benefits, budget_pages, baseline_cost),
            ilp_select(names, candidate_costs, candidate_benefits, budget_pages, baseline_cost),
            dynamic_programming_select(
                names, candidate_costs, candidate_benefits, budget_pages, baseline_cost
            ),
        ]
        candidate_by_name = {candidate.name: candidate for candidate in CANDIDATE_INDEXES}
        selection_rows = [
            {
                **asdict(result),
                "selected": ";".join(result.selected),
                "budget_pages": budget_pages,
                "within_budget": result.total_cost_pages <= budget_pages,
            }
            for result in selection_results
        ]

        query_rows: list[dict[str, object]] = []
        workload_rows: list[dict[str, object]] = []
        plans: dict[str, dict[str, list[dict[str, object]]]] = {}
        correctness: dict[str, object] = {"reference_digests": baseline_digests, "configurations": {}}
        for selection in selection_results:
            indexes = tuple(candidate_by_name[name] for name in selection.selected)
            plans[selection.method] = {}
            configuration_correct = True
            for repeat in range(1, config.repeats + 1):
                measurements, weighted_latency, throughput, storage_bytes, actual_page_size = _evaluate_database(
                    base_path,
                    work_dir / f"final_{selection.method}_{repeat}.sqlite",
                    indexes,
                    warmups=warmups,
                    repetitions=repetitions,
                )
                if storage_bytes % actual_page_size != 0:
                    raise AssertionError("configuration storage was not page aligned")
                repeat_correct = True
                for measurement in measurements:
                    equivalent = baseline_digests[measurement.query] == measurement.result_sha256
                    repeat_correct = repeat_correct and equivalent
                    query_rows.append(
                        {
                            "configuration": selection.method,
                            "repeat": repeat,
                            "query": measurement.query,
                            "weight": measurement.weight,
                            "median_latency_seconds": measurement.median_latency_seconds,
                            "mean_latency_seconds": measurement.mean_latency_seconds,
                            "latency_std_seconds": measurement.latency_std_seconds,
                            "min_latency_seconds": measurement.min_latency_seconds,
                            "result_rows": measurement.result_rows,
                            "result_sha256": measurement.result_sha256,
                            "result_equivalent": equivalent,
                        }
                    )
                    if repeat == 1:
                        plans[selection.method][measurement.query] = [
                            {"id": row[0], "parent": row[1], "not_used": row[2], "detail": row[3]}
                            for row in measurement.plan
                        ]
                configuration_correct = configuration_correct and repeat_correct
                workload_rows.append(
                    {
                        "configuration": selection.method,
                        "repeat": repeat,
                        "selected_indexes": ";".join(selection.selected),
                        "weighted_mean_latency_seconds": weighted_latency,
                        "workload_throughput_queries_per_second": throughput,
                        "index_storage_bytes": storage_bytes,
                        "index_storage_pages": storage_bytes // actual_page_size,
                        "storage_budget_pages": budget_pages,
                        "within_budget": storage_bytes // actual_page_size <= budget_pages,
                        "all_results_equivalent": repeat_correct,
                    }
                )
            correctness["configurations"][selection.method] = {
                "all_repeats_equivalent": configuration_correct,
                "selected_indexes": list(selection.selected),
            }

    query_summary = _summary_query_rows(query_rows)
    workload_summary = _summary_workload_rows(workload_rows)
    all_correct = all(
        bool(value["all_repeats_equivalent"])
        for value in correctness["configurations"].values()
    )
    write_json(output_dir / "dataset_manifest.json", asdict(dataset))
    (output_dir / "schema.sql").write_text(SCHEMA_SQL.strip() + "\n", encoding="utf-8")
    write_json(output_dir / "workload.json", [asdict(query) for query in QUERIES])
    write_csv(output_dir / "candidate_indexes.csv", candidate_rows)
    write_csv(output_dir / "selection_results.csv", selection_rows)
    write_csv(output_dir / "query_runs.csv", query_rows)
    write_csv(output_dir / "query_summary.csv", query_summary)
    write_csv(output_dir / "workload_runs.csv", workload_rows)
    write_csv(output_dir / "workload_summary.csv", workload_summary)
    write_json(output_dir / "query_plans.json", plans)
    write_json(output_dir / "correctness.json", correctness)
    write_json(
        output_dir / "environment.json",
        {
            "sqlite_version": sqlite3.sqlite_version,
            "python_sqlite_wrapper": "Python standard-library sqlite3",
            "page_size_bytes": dataset.page_size_bytes,
            "automatic_index": False,
            "timing_clock": "time.perf_counter_ns",
            "query_warmups": warmups,
            "query_repetitions": repetitions,
            "estimation_repetitions": estimation_repetitions,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "logical_cpus": os.cpu_count(),
        },
    )
    _plots(output_dir, query_summary, workload_summary, candidate_rows, budget_pages)
    manifest = {
        "track": "H",
        "status": "verified_sqlite_index_selection",
        "result_type": "measured SQLite CPU timings on synthetic data",
        "database_rows": dataset.customers + dataset.products + dataset.orders + dataset.order_items,
        "candidates": len(CANDIDATE_INDEXES),
        "queries": len(QUERIES),
        "configurations": [result.method for result in selection_results],
        "all_results_equivalent": all_correct,
        "all_configurations_within_budget": all(bool(row["within_budget"]) for row in workload_rows),
        "sqlite_optimizer_replaced": False,
        "artifacts": [
            "dataset_manifest.json", "schema.sql", "workload.json", "candidate_indexes.csv",
            "selection_results.csv", "query_runs.csv", "query_summary.csv",
            "workload_runs.csv", "workload_summary.csv", "query_plans.json",
            "correctness.json", "environment.json", "plots/workload_performance.png",
            "plots/candidate_indexes.png",
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest
