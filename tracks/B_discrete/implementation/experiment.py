"""Generate all Track B benchmark tables, fixtures, and shared plots."""

from __future__ import annotations

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np

from optlab.common.config import ExperimentConfig
from optlab.common.environment import collect_environment_metadata
from optlab.common.measurement import measure_call
from optlab.common.results import write_csv, write_json

from .maxcut import enumerate_maxcut, make_track_c_fixture, maxcut_ising, maxcut_qubo, penalty_sweep
from .models import benchmark_instances
from .solvers import SOLVERS, solve_exhaustive


ROOT = Path(__file__).resolve().parents[3]


def _run_knapsack(config: ExperimentConfig, output: Path):
    runs, summaries, references, instance_documents = [], [], [], []
    for instance in benchmark_instances():
        reference, reference_measurement = measure_call(solve_exhaustive, instance)
        references.append({
            "instance": instance.name,
            "items": instance.size,
            "capacity": instance.capacity,
            "optimal_objective": reference.objective,
            "selected": "".join(map(str, reference.selected)),
            "total_weight": reference.total_weight,
            "runtime_seconds": reference.runtime_seconds,
            "states_enumerated": reference.nodes_or_states,
            "peak_python_bytes": reference_measurement.peak_python_bytes,
        })
        instance_documents.append({
            "name": instance.name,
            "binary_variables": [f"x_{index}" for index in range(instance.size)],
            "domain": "x_i in {0,1}",
            "objective": "maximize sum_i value_i * x_i",
            "constraint": "sum_i weight_i * x_i <= capacity",
            "weights": list(instance.weights),
            "values": list(instance.values),
            "capacity": instance.capacity,
            "exhaustive_optimum": reference.objective,
        })
        for method, solver in SOLVERS.items():
            method_rows = []
            for repeat in range(config.repeats):
                solution, measurement = measure_call(solver, instance)
                gap = 100.0 * (reference.objective - solution.objective) / reference.objective
                row = {
                    "instance": instance.name,
                    "items": instance.size,
                    "capacity": instance.capacity,
                    "method": method,
                    "repeat": repeat,
                    "seed": config.seeds[repeat],
                    "selected": "".join(map(str, solution.selected)),
                    "total_weight": solution.total_weight,
                    "feasible": solution.feasible,
                    "objective": solution.objective,
                    "verified_optimum": solution.objective == reference.objective,
                    "optimality_gap_percent": gap,
                    "runtime_seconds": solution.runtime_seconds,
                    "peak_python_bytes": measurement.peak_python_bytes,
                    "process_max_rss_bytes": measurement.process_max_rss_bytes,
                    "status": solution.status,
                    "nodes_or_states": solution.nodes_or_states,
                }
                runs.append(row)
                method_rows.append(row)
            runtimes = np.asarray([row["runtime_seconds"] for row in method_rows])
            summaries.append({
                "instance": instance.name,
                "items": instance.size,
                "method": method,
                "objective": method_rows[0]["objective"],
                "optimal_objective": reference.objective,
                "optimality_gap_percent": method_rows[0]["optimality_gap_percent"],
                "feasible": method_rows[0]["feasible"],
                "verified_optimum": method_rows[0]["verified_optimum"],
                "runtime_seconds_mean": float(runtimes.mean()),
                "runtime_seconds_std": float(runtimes.std()),
                "runs": len(method_rows),
            })
    write_csv(output / "knapsack_runs.csv", runs)
    write_csv(output / "knapsack_summary.csv", summaries)
    write_csv(output / "knapsack_references.csv", references)
    write_json(output / "knapsack_instances.json", instance_documents)
    return summaries


def _plot_knapsack(rows, output: Path) -> None:
    instances = list(dict.fromkeys(str(row["instance"]) for row in rows))
    methods = list(SOLVERS)
    positions = np.arange(len(instances))
    width = 0.19
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    for offset_index, method in enumerate(methods):
        subset = [next(row for row in rows if row["instance"] == instance and row["method"] == method) for instance in instances]
        offset = (offset_index - 1.5) * width
        axes[0].bar(positions + offset, [row["objective"] for row in subset], width, label=method)
        axes[1].bar(positions + offset, [max(float(row["runtime_seconds_mean"]), 1e-7) for row in subset], width, label=method)
    axes[0].set(ylabel="Selected value", title="Solution quality")
    axes[1].set(ylabel="Mean runtime (seconds, log scale)", title="Runtime over 3 repeats", yscale="log")
    for axis in axes:
        axis.set_xticks(positions, [name.replace("_", "\n") for name in instances], fontsize=8)
        axis.grid(axis="y", alpha=0.25)
    axes[0].legend(fontsize=7)
    figure.suptitle("Identical 0/1 knapsack instances and constraints")
    figure.savefig(output / "plots" / "knapsack_comparison.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)


def _run_qubo(output: Path):
    rows = enumerate_maxcut()
    fixture = make_track_c_fixture()
    penalties = penalty_sweep()
    write_csv(output / "maxcut_energies.csv", rows)
    write_json(output / "maxcut_track_c_fixture.json", fixture)
    write_csv(output / "penalty_sweep.csv", penalties)
    qubo = maxcut_qubo()
    offset, linear, coupling = maxcut_ising()
    write_json(output / "qubo_ising_coefficients.json", {
        "maxcut_qubo_matrix": qubo.tolist(),
        "maxcut_ising_offset": offset,
        "maxcut_ising_linear": linear.tolist(),
        "maxcut_ising_coupling": coupling.tolist(),
        "energy_identity": "x^T Q x = Ising(s=2x-1) = -weighted_cut(x)",
        "constrained_example": "minimize -[4,3,2].x + A(sum(x)-1)^2; A=5 makes the exhaustive optimum feasible",
    })

    figure, axes = plt.subplots(1, 2, figsize=(10, 4.0), constrained_layout=True)
    state_index = np.arange(len(rows))
    axes[0].plot(state_index, [row["negative_cut"] for row in rows], label="-cut", linewidth=2)
    axes[0].scatter(state_index, [row["qubo_energy"] for row in rows], label="QUBO", marker="x", s=20)
    axes[0].scatter(state_index, [row["ising_energy"] for row in rows], label="Ising", marker="+", s=20)
    axes[0].set(xlabel="Enumerated bitstring index", ylabel="Energy", title="Max-Cut energy equivalence")
    axes[0].legend(fontsize=8)
    axes[1].plot([row["penalty"] for row in penalties], [row["best_feasible_energy"] for row in penalties], marker="o", label="best feasible")
    axes[1].plot([row["penalty"] for row in penalties], [row["best_infeasible_energy"] for row in penalties], marker="o", label="best infeasible")
    axes[1].set(xlabel="Penalty A", ylabel="Minimum energy", title="Exactly-one penalty threshold")
    axes[1].legend(fontsize=8)
    for axis in axes:
        axis.grid(alpha=0.25)
    figure.savefig(output / "plots" / "qubo_ising_penalty.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)
    return fixture, penalties


def run_experiment(config: ExperimentConfig) -> dict[str, object]:
    output = config.output_dir
    (output / "plots").mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    summaries = _run_knapsack(config, output)
    _plot_knapsack(summaries, output)
    fixture, penalties = _run_qubo(output)
    write_json(output / "environment.json", collect_environment_metadata(ROOT))
    manifest = {
        "track": "B",
        "status": "verified_experiment_with_syllabus_gap",
        "runtime_seconds": time.perf_counter() - started,
        "repeats": config.repeats,
        "seeds_recorded_for_timing_runs": list(config.seeds),
        "knapsack_methods": list(SOLVERS),
        "maxcut_classical_optimum": fixture["classical_optimum_cut"],
        "track_c_fixture_sha256": fixture["sha256_without_hash_field"],
        "safe_penalty_demonstrated": any(row["best_is_feasible"] for row in penalties),
        "unresolved": "Exact Chapter 6 syllabus is unavailable; B-06 remains unresolved for any additional taught discrete method or application.",
        "artifacts": sorted({"manifest.json", *(str(path.relative_to(output)) for path in output.rglob("*") if path.is_file() and not path.name.startswith("."))}),
    }
    write_json(output / "manifest.json", manifest)
    return manifest
