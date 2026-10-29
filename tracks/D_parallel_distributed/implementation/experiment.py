"""Generate the complete Track D benchmark, verification, and plot bundle."""

from __future__ import annotations

import statistics
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np

from optlab.common.config import ExperimentConfig
from optlab.common.environment import collect_environment_metadata
from optlab.common.results import write_csv, write_json

from .federated import run_federated_grid
from .multitask import run_multitask_comparison
from .parallel_cpu import default_workload, run_parallel_scaling, simulate_work_stealing
from .parallel_forms import run_parallel_forms
from .parallel_overheads import run_overhead_experiments
from .submodular import run_submodular_experiment


ROOT = Path(__file__).resolve().parents[3]


def _parallel_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, int], list[dict[str, object]]] = {}
    for row in rows:
        groups.setdefault((str(row["method"]), int(row["processes"])), []).append(row)
    summaries = []
    for (method, processes), group in sorted(groups.items()):
        summaries.append({
            "method": method,
            "processes": processes,
            "repeats": len(group),
            "makespan_seconds_median": statistics.median(float(row["makespan_seconds"]) for row in group),
            "makespan_seconds_mean": statistics.fmean(float(row["makespan_seconds"]) for row in group),
            "speedup_median": statistics.median(float(row["speedup"]) for row in group),
            "parallel_efficiency_median": statistics.median(float(row["parallel_efficiency"]) for row in group),
            "load_imbalance_ratio_median": statistics.median(float(row["load_imbalance_ratio"]) for row in group),
            "parallel_overhead_seconds_median": statistics.median(float(row["parallel_overhead_seconds"]) for row in group),
            "negative_speedup_observed": processes > 1 and any(float(row["speedup"]) < 1.0 for row in group),
            "minimum_observed_worker_count": min(int(row["worker_count_observed"]) for row in group),
        })
    return summaries


def _plot_results(output: Path, submodular, parallel_summary, overheads, forms, federated, multitask_history) -> None:
    plots = output / "plots"
    plots.mkdir(exist_ok=True)

    figure, axes = plt.subplots(1, 2, figsize=(9.5, 3.8), constrained_layout=True)
    axes[0].bar(["greedy", "exact"], [submodular["greedy"]["objective"], submodular["exact"]["objective"]], color=["tab:blue", "tab:orange"])
    axes[0].axhline((1 - 1 / np.e) * submodular["exact"]["objective"], color="black", linestyle="--", label="(1-1/e) OPT")
    axes[0].set(ylabel="Covered elements", title="Maximum coverage (budget 2)", ylim=(0, 10))
    axes[0].legend(fontsize=8)
    trace = submodular["greedy"]["trace"]
    axes[1].step([0] + [point["step"] for point in trace], [0] + [point["value"] for point in trace], where="post", marker="o")
    axes[1].set(xlabel="Greedy selection step", ylabel="Coverage", title="Greedy marginal progress", xticks=[0, 1, 2])
    for axis in axes: axis.grid(alpha=0.25)
    figure.savefig(plots / "submodular_coverage.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for method in ("static_contiguous", "dynamic_shared_queue"):
        group = [row for row in parallel_summary if row["method"] == method]
        axes[0].plot([row["processes"] for row in group], [row["speedup_median"] for row in group], marker="o", label=method)
        axes[1].plot([row["processes"] for row in group], [row["parallel_efficiency_median"] for row in group], marker="o", label=method)
    axes[0].plot([1, 2, 4], [1, 2, 4], color="black", linestyle="--", label="ideal")
    axes[0].set(xlabel="Processes", ylabel="Speedup", title="Measured makespan speedup")
    axes[1].axhline(1.0, color="black", linestyle="--", label="ideal")
    axes[1].set(xlabel="Processes", ylabel="Parallel efficiency", title="Speedup / processes")
    for axis in axes: axis.grid(alpha=0.25); axis.legend(fontsize=7)
    figure.savefig(plots / "parallel_scaling.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4), constrained_layout=True)
    form_names = [str(row["form"]).replace("_", "\n") for row in forms]
    axes[0].bar(form_names, [row["speedup"] for row in forms], color="tab:purple")
    axes[0].axhline(1.0, color="black", linestyle="--")
    axes[0].set(ylabel="Speedup (log scale)", title="Parallel forms: startup dominates", yscale="log", ylim=(5e-4, 2.0))
    overhead_labels, overhead_values = [], []
    for row in overheads:
        if row["experiment"] == "locality":
            overhead_labels.append("column / row\nlocality")
            overhead_values.append(row["column_over_row_ratio"])
        elif row["experiment"] == "synchronization":
            overhead_labels.append("locked / local\nsynchronization")
            overhead_values.append(row["locked_shared_counter_seconds"] / row["local_then_reduce_seconds"])
        else:
            overhead_labels.append("large / compact\ncommunication")
            overhead_values.append(row["large_over_compact_ratio"])
    axes[1].bar(overhead_labels, overhead_values, color="tab:red")
    axes[1].axhline(1.0, color="black", linestyle="--")
    axes[1].set(ylabel="Runtime ratio", title="Controlled overhead ratios")
    for axis in axes: axis.grid(axis="y", alpha=0.25); axis.tick_params(axis="x", labelsize=8)
    figure.savefig(plots / "parallel_forms_overheads.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for method in ("centralized", "fedavg"):
        group = [row for row in federated if row["method"] == method]
        labels = [f"r{row['rounds']}/l{row['local_steps']}" for row in group]
        axes[0].plot(labels, [row["loss"] for row in group], marker="o", label=method)
        axes[1].plot(labels, [row["accuracy"] for row in group], marker="o", label=method)
    axes[0].set(ylabel="Final logistic loss", title="FedAvg versus centralized")
    axes[1].set(ylabel="Training accuracy", title="Communication rounds / local steps", ylim=(0, 1.05))
    for axis in axes: axis.set_xlabel("rounds/local steps"); axis.grid(alpha=0.25); axis.legend(fontsize=8)
    figure.savefig(plots / "federated_comparison.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for method in ("equal", "mgda", "gradnorm"):
        group = [row for row in multitask_history if row["method"] == method]
        axes[0].plot([row["epoch"] for row in group], [row["mean_loss"] for row in group], label=method)
        axes[1].plot([row["epoch"] for row in group], [row["weight_one"] for row in group], label=f"{method}: task 1")
    axes[0].set(xlabel="Epoch", ylabel="Mean task MSE", title="Two-task convergence", yscale="log")
    axes[1].set(xlabel="Epoch", ylabel="Task-one weight (sum=2)", title="Adaptive weighting")
    for axis in axes: axis.grid(alpha=0.25); axis.legend(fontsize=8)
    figure.savefig(plots / "multitask_comparison.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)


def run_experiment(config: ExperimentConfig) -> dict[str, object]:
    output = config.output_dir
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    submodular = run_submodular_experiment()
    write_json(output / "submodular.json", submodular)

    parallel_rows, laws = run_parallel_scaling(config.repeats, int(config.parameters.get("workload_scale", 1)))
    parallel_summary = _parallel_summary(parallel_rows)
    write_csv(output / "parallel_runs.csv", parallel_rows)
    write_csv(output / "parallel_summary.csv", parallel_summary)
    write_json(output / "scaling_laws.json", laws)
    stealing = [simulate_work_stealing(default_workload(int(config.parameters.get("workload_scale", 1))), processes) for processes in (2, 4)]
    write_json(output / "work_stealing_simulation.json", stealing)

    overheads = run_overhead_experiments()
    write_json(output / "overhead_experiments.json", overheads)
    forms = run_parallel_forms(config.base_seed)
    normalized_forms = [{**row, "microbatches": row.get("microbatches", "")} for row in forms]
    write_csv(output / "parallel_forms.csv", normalized_forms)

    federated, federated_history, federated_metadata = run_federated_grid(config.base_seed)
    write_csv(output / "federated_comparison.csv", federated)
    write_csv(output / "federated_history.csv", federated_history)
    write_json(output / "federated_metadata.json", federated_metadata)

    multitask, multitask_history, multitask_metadata = run_multitask_comparison(config.base_seed, int(config.parameters.get("multitask_epochs", 120)))
    write_csv(output / "multitask_comparison.csv", multitask)
    write_csv(output / "multitask_history.csv", multitask_history)
    write_json(output / "multitask_metadata.json", multitask_metadata)
    _plot_results(output, submodular, parallel_summary, overheads, normalized_forms, federated, multitask_history)
    write_json(output / "environment.json", collect_environment_metadata(ROOT))

    manifest = {
        "track": "D",
        "status": "verified_experiment_with_syllabus_gap",
        "runtime_seconds": time.perf_counter() - started,
        "repeats": config.repeats,
        "multiprocessing_start_method": "spawn",
        "submodular_observed_ratio": submodular["approximation_ratio_observed"],
        "submodular_exact_verified": not submodular["verification"]["violations"],
        "parallel_negative_speedups_retained": any(row["negative_speedup_observed"] for row in parallel_summary if row["processes"] > 1),
        "parallel_forms_max_error": max(float(row["max_absolute_error"]) for row in forms),
        "federated_grid": [[row["rounds"], row["local_steps"]] for row in federated if row["method"] == "fedavg"],
        "multitask_methods": [row["method"] for row in multitask],
        "unresolved": "Exact Chapter 6 syllabus is unavailable; D-08 remains unresolved for any additional taught distributed or multi-task method.",
        "artifacts": sorted({"manifest.json", *(str(path.relative_to(output)) for path in output.rglob("*") if path.is_file() and not path.name.startswith("."))}),
    }
    write_json(output / "manifest.json", manifest)
    return manifest
