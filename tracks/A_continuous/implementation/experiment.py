"""Orchestrate the complete, small Track A evidence bundle."""

from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import root_scalar

from optlab.common.environment import collect_environment_metadata
from optlab.common.measurement import measure_call
from optlab.common.results import write_csv, write_json
from optlab.common.config import ExperimentConfig

from ..objectives import (
    ExponentialLeastSquares,
    QuadraticObjective,
    TiltedDoubleWell,
    finite_difference_gradient,
    make_logistic_objective,
)
from .curvature import analyze_curvature
from .optimizers import (
    FIRST_ORDER_METHODS,
    OptimizationResult,
    bfgs,
    gauss_newton,
    gradient_descent,
    newton_logistic,
    optimize_logistic,
)
from .pytorch_demo import run_backprop_demo


ROOT = Path(__file__).resolve().parents[3]
METHOD_SETTINGS = {
    "batch_gd": {"learning_rate": 0.20, "batch_size": 160},
    "sgd": {"learning_rate": 0.015, "batch_size": 1},
    "mini_batch_sgd": {"learning_rate": 0.08, "batch_size": 16},
    "momentum": {"learning_rate": 0.035, "batch_size": 16, "momentum": 0.9},
    "nesterov": {"learning_rate": 0.035, "batch_size": 16, "momentum": 0.9},
    "adagrad": {"learning_rate": 0.15, "batch_size": 16},
    "rmsprop": {"learning_rate": 0.02, "batch_size": 16},
    "adam": {"learning_rate": 0.03, "batch_size": 16},
}


def _summary_row(
    result: OptimizationResult,
    *,
    objective: str,
    hyperparameters: dict[str, object],
    seed: int,
    repeat: int,
    peak_python_bytes: int,
    process_max_rss_bytes: int,
) -> dict[str, object]:
    return {
        "method": result.method,
        "objective": objective,
        "hyperparameters": json.dumps(hyperparameters, sort_keys=True),
        "seed": seed,
        "repeat": repeat,
        "stopping_condition": result.stopping_condition,
        "iterations": result.iterations,
        "runtime_seconds": result.elapsed_seconds,
        "peak_python_bytes": peak_python_bytes,
        "process_max_rss_bytes": process_max_rss_bytes,
        "converged": result.converged,
        "convergence_behavior": "converged" if result.converged else ("diverged" if result.stopping_condition == "diverged" else "budget_exhausted"),
        "final_objective": result.final_objective,
        "final_gradient_norm": result.history[-1]["gradient_norm"],
    }


def _plot_lines(rows, output: Path, *, title: str, ylog: bool = False, ylabel: str = "Objective") -> None:
    figure, axis = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["series"]), []).append(row)
    for label, group in sorted(grouped.items()):
        ordered = sorted(group, key=lambda item: float(item["iteration"]))
        axis.plot([item["iteration"] for item in ordered], [item["objective"] for item in ordered], label=label)
    axis.set(title=title, xlabel="Iteration / epoch", ylabel=ylabel)
    if ylog:
        axis.set_yscale("log")
    axis.grid(alpha=0.25)
    axis.legend(fontsize=8, ncol=2)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)


def _first_order(config: ExperimentConfig, output: Path):
    objective = make_logistic_objective(seed=config.base_seed, l2=0.1)
    summaries, convergence = [], []
    results: dict[str, list[OptimizationResult]] = {}
    epochs = int(config.parameters.get("epochs", 60))
    for method in FIRST_ORDER_METHODS:
        results[method] = []
        settings = METHOD_SETTINGS[method]
        for repeat, seed in enumerate(config.seeds):
            call = lambda: optimize_logistic(objective, method, seed=seed, epochs=epochs, **settings)
            result, measurement = measure_call(call)
            results[method].append(result)
            summaries.append(_summary_row(result, objective="L2-regularized binary logistic loss", hyperparameters={**settings, "epochs": epochs, "tolerance": 1e-6}, seed=seed, repeat=repeat, peak_python_bytes=measurement.peak_python_bytes, process_max_rss_bytes=measurement.process_max_rss_bytes))
            for row in result.history:
                convergence.append({"method": method, "repeat": repeat, "seed": seed, **row})

    mean_plot = []
    for method, method_results in results.items():
        common = min(len(item.history) for item in method_results)
        for index in range(common):
            mean_plot.append({"series": method, "iteration": index, "objective": float(np.mean([item.history[index]["objective"] for item in method_results]))})
    _plot_lines(mean_plot, output / "plots" / "optimizer_convergence.png", title="First-order optimizers (mean of 3 runs)", ylog=True)
    return objective, summaries, convergence


def _landscapes(output: Path, base_seed: int):
    rows, evidence = [], {}
    convex = QuadraticObjective.convex_not_strong()
    strong = QuadraticObjective.strongly_convex()
    nonconvex = TiltedDoubleWell()
    cases = [
        ("convex_not_strong", convex, [3.0, 2.0], 0.2),
        ("strongly_convex", strong, [3.0, 2.0], 0.08),
        ("nonconvex_left_basin", nonconvex, [-0.2, 0.5], 0.04),
        ("nonconvex_right_basin", nonconvex, [0.2, 0.5], 0.04),
    ]
    for label, objective, initial, rate in cases:
        result = gradient_descent(objective.value, objective.gradient, initial, learning_rate=rate, max_iterations=150, seed=base_seed, method=label)
        evidence[label] = {"initial": initial, "final_parameters": result.parameters.tolist(), "final_objective": result.final_objective, "hessian_eigenvalues_at_final": np.linalg.eigvalsh(objective.hessian(result.parameters)).tolist(), "stopping_condition": result.stopping_condition}
        best_observed = min(float(row["objective"]) for row in result.history)
        rows.extend({"series": label, "iteration": row["iteration"], "objective": max(float(row["objective"]) - best_observed, 1e-14)} for row in result.history)

    stationary = []
    for bracket in [(-2.0, -0.2), (-0.2, 0.2), (0.2, 2.0)]:
        root = root_scalar(lambda x: nonconvex.gradient([x, 0.0])[0], bracket=bracket).root
        eigenvalues = np.linalg.eigvalsh(nonconvex.hessian([root, 0.0]))
        stationary.append({"point": [root, 0.0], "objective": nonconvex.value([root, 0.0]), "hessian_eigenvalues": eigenvalues.tolist(), "classification": "local minimum" if np.all(eigenvalues > 0) else "saddle point"})
    evidence["nonconvex_stationary_points"] = stationary
    evidence["definitions"] = {
        "convex_not_strong": "0.5*(x-target)^T [[1,1],[1,1]] (x-target); Hessian eigenvalues 0,2",
        "strongly_convex": "0.5*(x-target)^T diag(1,10) (x-target)",
        "nonconvex": "(x^2-1)^2 + 0.2x + 0.5y^2",
    }
    _plot_lines(rows, output / "plots" / "landscape_convergence.png", title="Convex, strongly convex, and non-convex objectives", ylog=True, ylabel="Objective gap to best observed")
    return evidence


def _sensitivity_and_noise(output: Path, seeds: tuple[int, ...]):
    objective = QuadraticObjective.strongly_convex()
    sensitivity, evidence = [], []
    for rate in [0.01, 0.08, 0.18, 0.22]:
        result = gradient_descent(objective.value, objective.gradient, [3.0, 2.0], learning_rate=rate, max_iterations=80, method=f"lr={rate}")
        sensitivity.extend({"series": f"lr={rate}", "iteration": row["iteration"], "objective": max(float(row["objective"]), 1e-14)} for row in result.history)
        evidence.append({"learning_rate": rate, "final_objective": result.final_objective, "stopping_condition": result.stopping_condition, "theoretical_stability_threshold": 0.2})
    _plot_lines(sensitivity, output / "plots" / "step_size_sensitivity.png", title="Step-size sensitivity (stability requires lr < 2/L = 0.2)", ylog=True)

    noisy_rows, noisy_summary = [], []
    for seed in seeds:
        result = gradient_descent(objective.value, objective.gradient, [3.0, 2.0], learning_rate=0.06, max_iterations=100, noise_std=0.2, seed=seed, method="noisy_gradient_descent")
        noisy_rows.extend({"series": f"seed={seed}", "iteration": row["iteration"], "objective": max(float(row["objective"]), 1e-14)} for row in result.history)
        noisy_summary.append({"seed": seed, "noise_std": 0.2, "final_objective": result.final_objective, "runtime_seconds": result.elapsed_seconds, "stopping_condition": result.stopping_condition})
    _plot_lines(noisy_rows, output / "plots" / "noisy_objective.png", title="Controlled additive gradient noise (3 seeds)", ylog=True)
    return evidence, noisy_summary


def _second_order(logistic, output: Path, seed: int):
    least_squares = ExponentialLeastSquares.synthetic()
    jobs = [
        (lambda: newton_logistic(logistic), "regularized logistic loss", {"max_iterations": 25, "tolerance": 1e-9}),
        (lambda: gauss_newton(least_squares), "mean exponential least-squares loss", {"initial": [1.0, -0.2], "max_iterations": 30, "tolerance": 1e-10}),
        (lambda: bfgs(logistic.value, logistic.gradient, np.zeros(logistic.dimension)), "regularized logistic loss", {"max_iterations": 100, "tolerance": 1e-9}),
    ]
    summaries, plot_rows, parameter_checks = [], [], {}
    for call, objective_name, hyperparameters in jobs:
        result, measurement = measure_call(call)
        summaries.append(_summary_row(result, objective=objective_name, hyperparameters=hyperparameters, seed=seed, repeat=0, peak_python_bytes=measurement.peak_python_bytes, process_max_rss_bytes=measurement.process_max_rss_bytes))
        plot_rows.extend({"series": result.method, "iteration": row["iteration"], "objective": max(float(row["objective"]), 1e-14)} for row in result.history)
        parameter_checks[result.method] = result.parameters.tolist()
    parameter_checks["gauss_newton_true_parameters"] = [1.5, -0.8]
    _plot_lines(plot_rows, output / "plots" / "second_order_convergence.png", title="Newton, Gauss-Newton, and BFGS", ylog=True)
    return summaries, parameter_checks


def _regularization(output: Path, seed: int):
    rows = []
    for strength in [0.0, 0.1, 1.0]:
        objective = make_logistic_objective(seed=20261029, l2=strength)
        result = optimize_logistic(objective, "batch_gd", seed=seed, learning_rate=0.2, epochs=100, batch_size=160)
        rows.append({"l2": strength, "final_objective": result.final_objective, "weight_norm": float(np.linalg.norm(result.parameters)), "accuracy": objective.accuracy(result.parameters), "runtime_seconds": result.elapsed_seconds})
    figure, axes = plt.subplots(1, 2, figsize=(7.5, 3.6), constrained_layout=True)
    axes[0].plot([row["l2"] for row in rows], [row["weight_norm"] for row in rows], marker="o")
    axes[1].plot([row["l2"] for row in rows], [row["accuracy"] for row in rows], marker="o")
    axes[0].set(xlabel="L2 coefficient", ylabel="Weight norm")
    axes[1].set(xlabel="L2 coefficient", ylabel="Training accuracy")
    for axis in axes:
        axis.grid(alpha=0.25)
    figure.suptitle("Regularization changes parameter magnitude and fit")
    figure.savefig(output / "plots" / "regularization_effect.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)
    return rows


def run_experiment(config: ExperimentConfig) -> dict[str, object]:
    output = config.output_dir
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    logistic, first_order_summary, convergence = _first_order(config, output)
    landscape = _landscapes(output, config.base_seed)
    sensitivity, noise = _sensitivity_and_noise(output, config.seeds)
    second_order_summary, parameter_checks = _second_order(logistic, output, config.seeds[0])
    regularization = _regularization(output, config.seeds[0])
    curvature = analyze_curvature(logistic, np.zeros(logistic.dimension))
    backprop = run_backprop_demo(config.base_seed)

    finite_difference = finite_difference_gradient(logistic.value, np.array([0.2, -0.1, 0.05]))
    gradient_check = {
        "point": [0.2, -0.1, 0.05],
        "analytic": logistic.gradient([0.2, -0.1, 0.05]).tolist(),
        "finite_difference": finite_difference.tolist(),
        "maximum_absolute_error": float(np.max(np.abs(logistic.gradient([0.2, -0.1, 0.05]) - finite_difference))),
    }
    all_summary = first_order_summary + second_order_summary
    write_csv(output / "method_runs.csv", all_summary)
    aggregate = []
    for method in dict.fromkeys(str(row["method"]) for row in all_summary):
        method_rows = [row for row in all_summary if row["method"] == method]
        objectives = np.asarray([row["final_objective"] for row in method_rows], dtype=float)
        runtimes = np.asarray([row["runtime_seconds"] for row in method_rows], dtype=float)
        aggregate.append(
            {
                "method": method,
                "objective": method_rows[0]["objective"],
                "runs": len(method_rows),
                "final_objective_mean": float(objectives.mean()),
                "final_objective_std": float(objectives.std()),
                "runtime_seconds_mean": float(runtimes.mean()),
                "runtime_seconds_std": float(runtimes.std()),
                "hyperparameters": method_rows[0]["hyperparameters"],
                "stopping_conditions": "; ".join(sorted({str(row["stopping_condition"]) for row in method_rows})),
                "convergence_behaviors": "; ".join(sorted({str(row["convergence_behavior"]) for row in method_rows})),
            }
        )
    write_csv(output / "method_summary.csv", aggregate)
    write_csv(output / "convergence.csv", convergence)
    write_json(output / "landscapes.json", landscape)
    write_json(output / "sensitivity.json", sensitivity)
    write_json(output / "noisy_objective.json", noise)
    write_json(output / "second_order_checks.json", parameter_checks)
    write_json(output / "regularization.json", regularization)
    write_json(output / "curvature.json", curvature)
    write_json(output / "backprop.json", backprop)
    write_json(output / "gradient_check.json", gradient_check)
    write_json(output / "environment.json", collect_environment_metadata(ROOT))
    manifest = {
        "track": "A",
        "status": "verified_experiment_with_syllabus_gap",
        "runtime_seconds": time.perf_counter() - started,
        "seeds": list(config.seeds),
        "methods": list(FIRST_ORDER_METHODS) + ["newton", "gauss_newton", "bfgs"],
        "artifacts": sorted(str(path.relative_to(output)) for path in output.rglob("*") if path.is_file() and not path.name.startswith(".")),
        "unresolved": "Exact Chapter 6 classroom syllabus has not been supplied; additional taught curvature methods may still be required.",
    }
    write_json(output / "manifest.json", manifest)
    return manifest
