"""Generate Track E workloads, comparisons, exact evidence, and plots."""

from __future__ import annotations

import statistics
import time
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np

from optlab.common.config import ExperimentConfig
from optlab.common.environment import collect_environment_metadata
from optlab.common.results import write_csv, write_json

from .exact_reference import exhaustive_offline_schedule, tiny_reference_requests
from .models import SimulationConfig
from .simulator import simulate
from .strategies import STRATEGIES
from .workload import generate_workload, workload_digest


ROOT = Path(__file__).resolve().parents[3]
METRICS = (
    "objective", "mean_latency", "p95_latency", "p99_latency", "mean_waiting_time",
    "p95_waiting_time", "mean_tardiness", "deadline_miss_rate",
    "throughput_requests_per_time", "makespan", "total_busy_time", "server_utilization",
    "mean_batch_size", "mean_token_efficiency", "mean_token_capacity_utilization",
    "mean_padded_capacity_utilization", "simulation_runtime_seconds",
)


def strategy_selection_rows() -> list[dict[str, object]]:
    return [
        {
            "method": "FCFS immediate FIFO batching",
            "variable_type": "ordered discrete assignments",
            "problem_size": "any streamed workload",
            "exact_or_heuristic": "deterministic baseline heuristic",
            "constraints": "prefix batch obeys count, summed-token, padded-token capacities",
            "hardware": "single simulated server on CPU",
            "parallelism": "simulated within-batch service only",
            "convergence_or_optimality": "no optimality claim; deterministic prefix rule",
            "communication_cost": "none; in-process simulation",
            "selected_reason": "transparent no-intentional-wait baseline",
        },
        {
            "method": "greedy length-aware batching",
            "variable_type": "ordered discrete assignments",
            "problem_size": "large online queues",
            "exact_or_heuristic": "heuristic",
            "constraints": "capacity plus bounded formation wait and urgent-anchor rule",
            "hardware": "single simulated server on CPU",
            "parallelism": "simulated within-batch service only",
            "convergence_or_optimality": "no optimality guarantee",
            "communication_cost": "none; in-process simulation",
            "selected_reason": "low scheduling cost and padding awareness",
        },
        {
            "method": "dynamic-programming batch selection",
            "variable_type": "binary subset selection",
            "problem_size": "12-request online lookahead",
            "exact_or_heuristic": "exact local score; heuristic global schedule",
            "constraints": "2D count/token DP with enumerated padded-token maximum",
            "hardware": "single simulated server on CPU",
            "parallelism": "simulated within-batch service only",
            "convergence_or_optimality": "exact for local score within lookahead; no global guarantee",
            "communication_cost": "none; in-process simulation",
            "selected_reason": "Chapter 6-style exact local combinatorial optimization",
        },
        {
            "method": "offline exhaustive reference",
            "variable_type": "ordered set partitions",
            "problem_size": "at most 7 simultaneous requests",
            "exact_or_heuristic": "exact",
            "constraints": "all capacity constraints",
            "hardware": "single CPU",
            "parallelism": "none",
            "convergence_or_optimality": "global optimum by complete enumeration",
            "communication_cost": "none",
            "selected_reason": "independent tiny correctness and optimality reference",
        },
        {
            "method": "MILP (not selected)",
            "variable_type": "binary assignment plus continuous time",
            "problem_size": "small offline only",
            "exact_or_heuristic": "exact when solved to optimality",
            "constraints": "assignment, capacity, ordering, timing",
            "hardware": "CPU solver",
            "parallelism": "solver-dependent",
            "convergence_or_optimality": "global bound if solved to certified optimum",
            "communication_cost": "solver-internal only",
            "selected_reason": "rejected to avoid time-indexed model growth and extra machinery for an online study",
        },
    ]


def _summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[object, ...], list[dict[str, object]]] = {}
    keys = ("workload_size", "arrival_rate", "token_capacity", "padded_token_capacity", "strategy")
    for row in rows:
        groups.setdefault(tuple(row[key] for key in keys), []).append(row)
    output = []
    for group_key, group in sorted(groups.items()):
        summary = dict(zip(keys, group_key))
        summary["repeats"] = len(group)
        for metric in METRICS:
            values = [float(row[metric]) for row in group]
            summary[f"{metric}_mean"] = statistics.fmean(values)
            summary[f"{metric}_std"] = statistics.pstdev(values)
        summary["all_correct"] = all(bool(row["correct"]) for row in group)
        summary["simulated"] = True
        output.append(summary)
    return output


def _plots(output: Path, summaries: list[dict[str, object]]) -> None:
    plots = output / "plots"
    plots.mkdir(exist_ok=True)
    rates = sorted({float(row["arrival_rate"]) for row in summaries})
    capacities = sorted({int(row["token_capacity"]) for row in summaries})
    sizes = sorted({int(row["workload_size"]) for row in summaries})
    standard = [row for row in summaries if float(row["arrival_rate"]) == rates[-1] and int(row["token_capacity"]) == capacities[-1]]
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4), constrained_layout=True)
    for strategy in STRATEGIES:
        group = sorted((row for row in standard if row["strategy"] == strategy), key=lambda row: int(row["workload_size"]))
        axes[0].plot([row["workload_size"] for row in group], [row["mean_latency_mean"] for row in group], marker="o", label=f"{strategy}: mean")
        axes[0].plot([row["workload_size"] for row in group], [row["p95_latency_mean"] for row in group], marker="x", linestyle="--", label=f"{strategy}: p95")
        axes[1].plot([row["workload_size"] for row in group], [row["throughput_requests_per_time_mean"] for row in group], marker="o", label=strategy)
    axes[0].set(xlabel="Synthetic requests", ylabel="Simulated time units", title="Mean and tail latency")
    axes[1].set(xlabel="Synthetic requests", ylabel="Requests / simulated time unit", title="Throughput")
    for axis in axes: axis.grid(alpha=0.25); axis.legend(fontsize=7)
    figure.savefig(plots / "latency_throughput_by_size.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    largest = [row for row in summaries if int(row["workload_size"]) == sizes[-1] and int(row["token_capacity"]) == capacities[-1]]
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4), constrained_layout=True)
    x = np.arange(len(rates))
    width = 0.25
    for index, strategy in enumerate(STRATEGIES):
        group = sorted((row for row in largest if row["strategy"] == strategy), key=lambda row: float(row["arrival_rate"]))
        axes[0].bar(x + (index - 1) * width, [row["mean_latency_mean"] for row in group], width, label=strategy)
        axes[1].bar(x + (index - 1) * width, [row["mean_batch_size_mean"] for row in group], width, label=strategy)
    for axis in axes: axis.set_xticks(x, [f"rate {rate:g}" for rate in rates]); axis.grid(axis="y", alpha=0.25)
    axes[0].set(ylabel="Mean latency", title="Mean latency")
    axes[1].set(ylabel="Mean requests per batch", title="Mean batch size")
    axes[0].legend(fontsize=7)
    figure.savefig(plots / "batching_load_tradeoff.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    loaded = [row for row in summaries if int(row["workload_size"]) == sizes[-1] and float(row["arrival_rate"]) == rates[-1]]
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4), constrained_layout=True)
    for strategy in STRATEGIES:
        group = sorted((row for row in loaded if row["strategy"] == strategy), key=lambda row: int(row["token_capacity"]))
        axes[0].plot([row["token_capacity"] for row in group], [row["deadline_miss_rate_mean"] for row in group], marker="o", label=strategy)
        axes[1].plot([row["token_capacity"] for row in group], [row["mean_token_efficiency_mean"] for row in group], marker="o", label=strategy)
    axes[0].set(xlabel="Summed-token capacity", ylabel="Deadline-miss fraction", title="Latency SLO misses")
    axes[1].set(xlabel="Summed-token capacity", ylabel="Useful / padded tokens", title="Padding efficiency")
    for axis in axes: axis.grid(alpha=0.25); axis.legend(fontsize=7)
    figure.savefig(plots / "capacity_slo_efficiency.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)


def run_experiment(config: ExperimentConfig) -> dict[str, object]:
    output = config.output_dir
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    sizes = [int(value) for value in config.parameters.get("workload_sizes", [24, 64, 128])]
    arrival_rates = [float(value) for value in config.parameters.get("arrival_rates", [0.6, 1.2])]
    capacities = [int(value) for value in config.parameters.get("token_capacities", [384, 512])]
    base = SimulationConfig(
        max_batch_size=int(config.parameters.get("max_batch_size", 4)),
        batch_window=float(config.parameters.get("batch_window", 0.8)),
        max_batch_wait=float(config.parameters.get("max_batch_wait", 2.0)),
    )
    run_rows: list[dict[str, object]] = []
    batch_rows: list[dict[str, object]] = []
    request_rows: list[dict[str, object]] = []
    workload_rows: list[dict[str, object]] = []
    verification_rows: list[dict[str, object]] = []
    for size_index, size in enumerate(sizes):
        for rate_index, arrival_rate in enumerate(arrival_rates):
            for capacity in capacities:
                scenario_config = SimulationConfig(**{**asdict(base), "token_capacity": capacity, "padded_token_capacity": capacity + 128})
                for repeat, seed in enumerate(config.seeds):
                    workload_seed = seed + (size_index * len(arrival_rates) + rate_index) * 1009
                    requests = generate_workload(size, arrival_rate, workload_seed, scenario_config)
                    digest = workload_digest(requests)
                    workload_id = f"n{size}-r{arrival_rate:g}-c{capacity}-rep{repeat}"
                    workload_rows.append({
                        "workload_id": workload_id, "repeat": repeat, "seed": workload_seed,
                        "workload_size": size, "arrival_rate": arrival_rate,
                        "token_capacity": capacity, "padded_token_capacity": capacity + 128,
                        "sha256": digest, "simulated": True,
                    })
                    for request in requests:
                        request_rows.append({"workload_id": workload_id, **asdict(request), "simulated": True})
                    for strategy in STRATEGIES:
                        result = simulate(requests, strategy, scenario_config)
                        common = {
                            "workload_id": workload_id, "workload_sha256": digest, "repeat": repeat,
                            "seed": workload_seed, "workload_size": size, "arrival_rate": arrival_rate,
                            "token_capacity": capacity, "padded_token_capacity": capacity + 128,
                        }
                        run_rows.append({**common, **result["metrics"]})
                        batch_rows.extend({**common, **batch} for batch in result["batches"])
                        verification_rows.append({
                            **common, "strategy": strategy, "valid": result["verification"]["valid"],
                            "processed_count": result["verification"]["processed_count"],
                            "unique_processed_count": result["verification"]["unique_processed_count"],
                            "batch_count": result["verification"]["batch_count"],
                            "objective_absolute_error": result["verification"]["objective_absolute_error"],
                            "errors": "; ".join(result["verification"]["errors"]), "simulated": True,
                        })
    summaries = _summary(run_rows)
    write_csv(output / "workloads.csv", workload_rows)
    write_csv(output / "synthetic_requests.csv", request_rows)
    write_csv(output / "runs.csv", run_rows)
    write_csv(output / "summary.csv", summaries)
    write_csv(output / "batches.csv", batch_rows)
    write_csv(output / "verification.csv", verification_rows)
    selection = strategy_selection_rows()
    write_csv(output / "strategy_selection.csv", selection)

    tiny_config = SimulationConfig(max_batch_size=3, token_capacity=240, padded_token_capacity=330, batch_window=0.0)
    tiny_requests = tiny_reference_requests()
    exact = exhaustive_offline_schedule(tiny_requests, tiny_config)
    comparisons = []
    for strategy in STRATEGIES:
        result = simulate(tiny_requests, strategy, tiny_config)
        comparisons.append({"strategy": strategy, "objective": result["metrics"]["objective"], "gap_to_exact": result["metrics"]["objective"] - exact["objective"], "correct": result["metrics"]["correct"]})
    write_json(output / "tiny_exact_reference.json", {"requests": [asdict(request) for request in tiny_requests], "config": asdict(tiny_config), "exact": exact, "strategy_comparisons": comparisons, "simulated": True})
    _plots(output, summaries)
    write_json(output / "environment.json", collect_environment_metadata(ROOT))
    manifest = {
        "track": "E",
        "status": "verified_simulated_case_study",
        "result_type": "discrete-event simulation only; no LLM, GPU, accelerator, or production inference was measured",
        "runtime_seconds": time.perf_counter() - started,
        "workload_sizes": sizes,
        "arrival_rates": arrival_rates,
        "token_capacities": capacities,
        "repeats": config.repeats,
        "strategies": list(STRATEGIES),
        "all_runs_correct": all(bool(row["correct"]) for row in run_rows),
        "all_objective_checks_exact": all(float(row["objective_absolute_error"]) <= 1e-12 for row in verification_rows),
        "tiny_exact_objective": exact["objective"],
        "artifacts": sorted({"manifest.json", *(str(path.relative_to(output)) for path in output.rglob("*") if path.is_file() and not path.name.startswith("."))}),
    }
    write_json(output / "manifest.json", manifest)
    return manifest
