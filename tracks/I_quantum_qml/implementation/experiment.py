"""Generate the complete, simulation-only Track I evidence bundle."""

from __future__ import annotations

import csv
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np

from optlab.common.config import ExperimentConfig
from optlab.common.environment import collect_environment_metadata
from optlab.common.results import write_csv, write_json
from optlab.quantum.algorithms import (
    algorithm_circuits,
    bernstein_vazirani,
    deutsch_jozsa,
    grover_search,
    noisy_grover_success,
    phase_estimation,
    qft_roundtrip,
    shor_order_finding_15,
    simulated_quantum_annealing_proxy,
)
from optlab.quantum.diagnostics import barren_plateau_proxy
from optlab.quantum.qml_models import (
    iris_binary_split,
    train_logistic_baseline,
    train_quantum_kernel,
    train_rbf_kernel_baseline,
    train_variational_classifier,
    variational_circuit_diagram,
)


ROOT = Path(__file__).resolve().parents[3]
MAXCUT_FIXTURE = ROOT / "tracks" / "B_discrete" / "results" / "maxcut_track_c_fixture.json"
TRACK_C_RESULTS = ROOT / "tracks" / "C_quantum_optimization" / "results"
TRACK_D_SUMMARY = ROOT / "tracks" / "D_parallel_distributed" / "results" / "parallel_summary.csv"


def _algorithm_row(result: dict[str, object]) -> dict[str, object]:
    keys = (
        "algorithm",
        "instance",
        "expected",
        "observed",
        "success_probability",
        "query_count",
        "gate_count",
        "circuit_depth",
        "runtime_seconds",
        "hand_written_circuit",
        "simulator",
    )
    return {key: result[key] for key in keys}


def _run_algorithms(output: Path) -> list[dict[str, object]]:
    results = [
        deutsch_jozsa(oracle="constant_zero", input_qubits=2),
        deutsch_jozsa(oracle="balanced", input_qubits=2),
        bernstein_vazirani("101"),
        grover_search("10"),
        qft_roundtrip("101"),
        phase_estimation(phase=0.25, counting_qubits=3),
    ]
    shor = shor_order_finding_15()
    results.append(shor)
    write_csv(output / "algorithm_results.csv", [_algorithm_row(result) for result in results])
    write_json(output / "shor_order_finding.json", shor)
    return results


def _run_annealing(config: ExperimentConfig, output: Path) -> list[dict[str, object]]:
    sweeps = int(config.parameters.get("annealing_sweeps", 1200))
    rows = [
        simulated_quantum_annealing_proxy(MAXCUT_FIXTURE, seed=seed, sweeps=sweeps)
        for seed in config.seeds
    ]
    write_csv(output / "annealing_runs.csv", rows)
    return rows


def _classical_linear_search(items: int, target: int, repetitions: int = 2000) -> tuple[int, float]:
    started = time.perf_counter()
    observed = -1
    queries = 0
    for _ in range(repetitions):
        for candidate in range(items):
            queries = candidate + 1
            if candidate == target:
                observed = candidate
                break
    elapsed = (time.perf_counter() - started) / repetitions
    if observed != target:
        raise AssertionError("classical search failed")
    return queries, elapsed


def _grover_comparison(config: ExperimentConfig, output: Path) -> list[dict[str, object]]:
    qubit_counts = tuple(int(value) for value in config.parameters.get("grover_qubits", [2, 3, 4]))
    rows = []
    for qubits in qubit_counts:
        items = 2**qubits
        target = "1" * qubits
        quantum = grover_search(target)
        classical_queries, classical_seconds = _classical_linear_search(items, items - 1)
        rows.append({
            "qubits": qubits,
            "items": items,
            "target": target,
            "grover_oracle_queries": quantum["query_count"],
            "classical_worst_case_queries": classical_queries,
            "query_ratio_classical_over_grover": classical_queries / int(quantum["query_count"]),
            "grover_success_probability": quantum["success_probability"],
            "grover_gate_count": quantum["gate_count"],
            "grover_simulator_seconds": quantum["runtime_seconds"],
            "classical_python_seconds": classical_seconds,
            "quantum_query_complexity": "O(sqrt(N))",
            "classical_query_complexity": "O(N)",
            "wall_time_claim": "none: local quantum simulation is classical work and is slower at these sizes",
        })
    write_csv(output / "grover_query_comparison.csv", rows)
    return rows


def _noise_study(output: Path) -> list[dict[str, object]]:
    rows = []
    for scale in (0.0, 0.5, 1.0, 2.0, 5.0):
        single = 0.001 * scale
        two = 0.01 * scale
        rows.append({
            "noise_scale": scale,
            "single_qubit_depolarizing_probability": single,
            "two_qubit_gate_local_depolarizing_probability": two,
            "grover_success_probability": noisy_grover_success(
                single_qubit_error=single, two_qubit_error=two
            ),
            "backend": "PennyLane default.mixed density-matrix simulator",
            "physical_hardware": False,
            "model_scope": "phenomenological gate-local errors; plausible relative rates but not calibrated to a named device",
        })
    write_csv(output / "noise_model.csv", rows)
    return rows


def _dataset_rows(split) -> list[dict[str, object]]:
    rows = []
    for subset, indices, features, labels in (
        ("train", split.train_indices, split.train_features, split.train_labels),
        ("test", split.test_indices, split.test_features, split.test_labels),
    ):
        rows.extend({
            "subset": subset,
            "original_iris_index": int(index),
            "encoded_petal_length": float(feature[0]),
            "encoded_petal_width": float(feature[1]),
            "label": int(label),
            "dataset_digest": split.digest,
        } for index, feature, label in zip(indices, features, labels))
    return rows


def _run_qml(config: ExperimentConfig, output: Path):
    samples_per_class = int(config.parameters.get("samples_per_class", 20))
    steps = int(config.parameters.get("vqc_steps", 25))
    split = iris_binary_split(seed=config.base_seed, samples_per_class=samples_per_class)
    write_csv(output / "dataset_split.csv", _dataset_rows(split))
    comparisons: list[dict[str, object]] = []
    history: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    kernel_diagram = ""
    for repeat, seed in enumerate(config.seeds):
        vqc, run_history, vqc_predictions = train_variational_classifier(
            split, seed=seed, steps=steps
        )
        logistic, logistic_predictions = train_logistic_baseline(split, seed=seed)
        quantum_kernel, kernel_predictions, kernel_diagram = train_quantum_kernel(split)
        rbf, rbf_predictions = train_rbf_kernel_baseline(split)
        for row in (vqc, logistic, quantum_kernel, rbf):
            comparisons.append({"repeat": repeat, "seed": seed, **row})
        history.extend({"repeat": repeat, "seed": seed, **row} for row in run_history)
        for model, model_predictions in (
            (vqc["model"], vqc_predictions),
            (logistic["model"], logistic_predictions),
            (quantum_kernel["model"], kernel_predictions),
            (rbf["model"], rbf_predictions),
        ):
            predictions.extend({
                "repeat": repeat,
                "seed": seed,
                "model": model,
                "test_position": position,
                "original_iris_index": int(split.test_indices[position]),
                "expected": int(split.test_labels[position]),
                "predicted": int(prediction),
                "correct": bool(prediction == split.test_labels[position]),
                "dataset_digest": split.digest,
            } for position, prediction in enumerate(model_predictions))
    write_csv(output / "qml_comparison.csv", comparisons)
    write_csv(output / "qml_training.csv", history)
    write_csv(output / "qml_predictions.csv", predictions)
    return split, comparisons, history, kernel_diagram


def _cross_track_analysis(output: Path) -> dict[str, object]:
    with TRACK_D_SUMMARY.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    parallel = [row for row in rows if row["method"] != "serial"]
    best = max(parallel, key=lambda row: float(row["speedup_median"]))
    result = {
        "track_d_result": str(TRACK_D_SUMMARY.relative_to(ROOT)),
        "best_measured_parallel_method": best["method"],
        "processes": int(best["processes"]),
        "median_speedup": float(best["speedup_median"]),
        "median_parallel_efficiency": float(best["parallel_efficiency_median"]),
        "negative_speedup_observed_in_track_d": any(row["negative_speedup_observed"] == "True" for row in parallel),
        "interpretation": "Track D speedup is measured wall-clock acceleration from classical processes; Grover's advantage is an oracle-query asymptotic result. A classically simulated quantum circuit does not turn that query advantage into hardware speedup.",
    }
    write_json(output / "cross_track_comparison.json", result)
    return result


def _coverage_rows() -> list[dict[str, object]]:
    return [
        {"topic": "QAOA", "source": "PDF Section 5", "implementation": "src/optlab/quantum/maxcut.py", "test": "tracks/C_quantum_optimization/tests/test_qaoa.py", "result": "tracks/C_quantum_optimization/results/qaoa_best.json", "status": "verified-reused-simulation", "limitation": "Track C local simulator"},
        {"topic": "VQE", "source": "PDF Section 5", "implementation": "src/optlab/quantum/variational.py", "test": "tracks/C_quantum_optimization/tests/test_variational.py", "result": "tracks/C_quantum_optimization/results/vqe_runs.csv", "status": "verified-reused-simulation", "limitation": "two-qubit Hamiltonian"},
        {"topic": "PQC / QNN", "source": "PDF Section 5", "implementation": "src/optlab/quantum/qml_models.py; src/optlab/quantum/variational.py", "test": "tracks/I_quantum_qml/tests/test_qml.py", "result": "tracks/I_quantum_qml/results/qml_comparison.csv", "status": "verified-simulation", "limitation": "two-qubit VQC is the trained QNN; separate Track C QNN also retained"},
        {"topic": "parameter-shift", "source": "PDF Section 5", "implementation": "src/optlab/quantum/variational.py", "test": "tracks/C_quantum_optimization/tests/test_variational.py", "result": "tracks/C_quantum_optimization/results/parameter_shift.json", "status": "verified-reused-simulation", "limitation": "analytic simulator"},
        {"topic": "SPSA", "source": "PDF Section 5", "implementation": "src/optlab/quantum/maxcut.py", "test": "tracks/C_quantum_optimization/tests/test_qaoa.py", "result": "tracks/C_quantum_optimization/results/qaoa_runs.csv", "status": "verified-reused-simulation", "limitation": "small QAOA"},
        {"topic": "quantum natural gradient", "source": "PDF Section 5", "implementation": "src/optlab/quantum/variational.py", "test": "tracks/C_quantum_optimization/tests/test_variational.py", "result": "tracks/C_quantum_optimization/results/vqe_runs.csv", "status": "verified-reused-simulation", "limitation": "block-diagonal metric"},
        {"topic": "Deutsch-Jozsa", "source": "PDF Section 5 example list", "implementation": "src/optlab/quantum/algorithms.py", "test": "tracks/I_quantum_qml/tests/test_algorithms.py", "result": "tracks/I_quantum_qml/results/algorithm_results.csv", "status": "verified-hand-written-simulation", "limitation": "two-input oracle"},
        {"topic": "Bernstein-Vazirani", "source": "PDF Section 5 example list", "implementation": "src/optlab/quantum/algorithms.py", "test": "tracks/I_quantum_qml/tests/test_algorithms.py", "result": "tracks/I_quantum_qml/results/algorithm_results.csv", "status": "verified-hand-written-simulation", "limitation": "three-bit secret"},
        {"topic": "Grover", "source": "PDF Section 5 example list", "implementation": "src/optlab/quantum/algorithms.py", "test": "tracks/I_quantum_qml/tests/test_algorithms.py", "result": "tracks/I_quantum_qml/results/grover_query_comparison.csv", "status": "verified-hand-written-simulation", "limitation": "one marked item; 2-4 qubits"},
        {"topic": "Quantum Fourier Transform", "source": "PDF Section 5 example list", "implementation": "src/optlab/quantum/algorithms.py", "test": "tracks/I_quantum_qml/tests/test_algorithms.py", "result": "tracks/I_quantum_qml/results/algorithm_results.csv", "status": "verified-hand-written-simulation", "limitation": "three-qubit round-trip"},
        {"topic": "Quantum Phase Estimation", "source": "PDF Section 5 example list", "implementation": "src/optlab/quantum/algorithms.py", "test": "tracks/I_quantum_qml/tests/test_algorithms.py", "result": "tracks/I_quantum_qml/results/algorithm_results.csv", "status": "verified-simulation", "limitation": "exactly representable phase"},
        {"topic": "Shor", "source": "PDF Section 5 example list", "implementation": "src/optlab/quantum/algorithms.py", "test": "tracks/I_quantum_qml/tests/test_algorithms.py", "result": "tracks/I_quantum_qml/results/shor_order_finding.json", "status": "verified-compiled-simulation", "limitation": "N=15 matrix-compiled modular unitary; not scalable"},
        {"topic": "quantum annealing", "source": "PDF Section 5 example list", "implementation": "src/optlab/quantum/algorithms.py", "test": "tracks/I_quantum_qml/tests/test_algorithms.py", "result": "tracks/I_quantum_qml/results/annealing_runs.csv", "status": "verified-classical-proxy", "limitation": "classical simulated annealing, no physical annealer; embedding study reused from Track C"},
        {"topic": "variational classifier", "source": "PDF Section 5", "implementation": "src/optlab/quantum/qml_models.py", "test": "tracks/I_quantum_qml/tests/test_qml.py", "result": "tracks/I_quantum_qml/results/qml_comparison.csv", "status": "verified-simulation", "limitation": "tiny binary Iris subset"},
        {"topic": "quantum kernel", "source": "PDF Section 5", "implementation": "src/optlab/quantum/qml_models.py", "test": "tracks/I_quantum_qml/tests/test_qml.py", "result": "tracks/I_quantum_qml/results/qml_comparison.csv", "status": "verified-simulation", "limitation": "fixed two-qubit fidelity kernel"},
        {"topic": "shots, noise, barren plateaus", "source": "PDF Section 5 / Track I", "implementation": "src/optlab/quantum/diagnostics.py; src/optlab/quantum/algorithms.py", "test": "tracks/I_quantum_qml/tests/test_experiment.py", "result": "tracks/I_quantum_qml/results/noise_model.csv; tracks/I_quantum_qml/results/barren_plateau_proxy.csv; tracks/C_quantum_optimization/results/finite_shots_summary.csv", "status": "verified-simulation", "limitation": "finite-size proxies and phenomenological noise"},
        {"topic": "any additional classroom-only quantum/QML method", "source": "PDF says every method taught; actual Chapter 6 material not supplied", "implementation": "UNRESOLVED", "test": "UNRESOLVED", "result": "UNRESOLVED", "status": "blocked-awaiting-syllabus", "limitation": "cannot infer an exact lecture list from unrelated syllabus PDFs"},
    ]


def _write_diagrams(output: Path, kernel_diagram: str) -> None:
    content = [
        "All diagrams are local simulator circuits. No physical quantum hardware was used.",
        "The labels below identify which circuits were built from primitive gates.",
    ]
    for name, diagram in algorithm_circuits().items():
        content.append(f"\n{name}:\n{diagram}")
    content.append("\nVariational classifier / QNN:\n" + variational_circuit_diagram())
    content.append("\nQuantum fidelity kernel overlap circuit:\n" + kernel_diagram)
    (output / "circuit_diagrams.txt").write_text("\n".join(content) + "\n", encoding="utf-8")


def _plots(output: Path, algorithms, grover_rows, qml_rows, qml_history, noise, plateau) -> None:
    plots = output / "plots"
    plots.mkdir(exist_ok=True)

    figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    names = [
        f"Deutsch-Jozsa ({'constant' if 'constant' in row['instance'] else 'balanced'})"
        if row["algorithm"] == "Deutsch-Jozsa"
        else row["algorithm"]
        for row in algorithms
    ]
    axes[0].barh(names, [row["success_probability"] for row in algorithms], color="tab:blue")
    axes[0].set(xlim=(0, 1.05), xlabel="Success probability", title="Tiny textbook instances")
    axes[1].plot([row["items"] for row in grover_rows], [row["classical_worst_case_queries"] for row in grover_rows], marker="o", label="classical worst case")
    axes[1].plot([row["items"] for row in grover_rows], [row["grover_oracle_queries"] for row in grover_rows], marker="o", label="Grover oracle queries")
    axes[1].set(xscale="log", yscale="log", xlabel="Search-space size N", ylabel="Queries", title="Theory/counts, not wall-time speedup")
    axes[1].legend()
    for axis in axes: axis.grid(alpha=0.25)
    figure.savefig(plots / "algorithms_and_queries.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    model_names = sorted(set(row["model"] for row in qml_rows))
    accuracies = [np.mean([row["accuracy"] for row in qml_rows if row["model"] == model]) for model in model_names]
    runtimes = [np.median([row["training_time_seconds"] for row in qml_rows if row["model"] == model]) for model in model_names]
    short = [name.replace("variational_quantum_classifier_qnn", "VQC/QNN").replace("classical_logistic_regression", "logistic").replace("quantum_fidelity_kernel_svc", "quantum kernel").replace("classical_rbf_kernel_svc", "RBF SVC") for name in model_names]
    axes[0].bar(short, accuracies, color=["tab:gray" if "classical" in name else "tab:purple" for name in model_names])
    axes[0].set(ylim=(0, 1.05), ylabel="Held-out accuracy", title="Identical Iris split")
    axes[0].tick_params(axis="x", rotation=20)
    axes[1].bar(short, runtimes, color=["tab:gray" if "classical" in name else "tab:purple" for name in model_names])
    axes[1].set(yscale="log", ylabel="Median training/evaluation seconds", title="Local CPU simulation overhead")
    axes[1].tick_params(axis="x", rotation=20)
    for axis in axes: axis.grid(alpha=0.25)
    figure.savefig(plots / "qml_classical_comparison.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)
    for repeat in sorted(set(int(row["repeat"]) for row in qml_history)):
        rows = [row for row in qml_history if int(row["repeat"]) == repeat]
        axes[0].plot([row["step"] for row in rows], [row["loss"] for row in rows], label=f"repeat {repeat}")
    axes[0].set(xlabel="Training step", ylabel="MSE", title="VQC/QNN convergence")
    axes[0].legend(fontsize=8)
    axes[1].plot([row["noise_scale"] for row in noise], [row["grover_success_probability"] for row in noise], marker="o", label="Grover success")
    axes[1].set(xlabel="Noise scale", ylabel="Success probability", title="Gate-local depolarizing model", ylim=(0, 1.05))
    axes[1].legend(fontsize=8)
    axes[2].plot([row["qubits"] for row in plateau], [row["global_gradient_variance"] for row in plateau], marker="s", color="tab:red", label="global cost")
    axes[2].plot([row["qubits"] for row in plateau], [row["local_gradient_variance"] for row in plateau], marker="o", color="tab:green", label="local cost")
    axes[2].set(xlabel="Qubits", ylabel="Gradient variance", title="Finite-size plateau proxy", yscale="log")
    axes[2].legend(fontsize=8)
    for axis in axes: axis.grid(alpha=0.25)
    figure.savefig(plots / "training_noise_plateau.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)


def run_experiment(config: ExperimentConfig) -> dict[str, object]:
    output = config.output_dir
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    algorithms = _run_algorithms(output)
    annealing = _run_annealing(config, output)
    grover_rows = _grover_comparison(config, output)
    noise = _noise_study(output)
    split, qml_rows, qml_history, kernel_diagram = _run_qml(config, output)
    plateau = barren_plateau_proxy(
        qubit_counts=tuple(int(value) for value in config.parameters.get("plateau_qubits", [2, 4, 6, 8])),
        repeats=int(config.parameters.get("plateau_repeats", 24)),
        seed=config.base_seed,
    )
    write_csv(output / "barren_plateau_proxy.csv", plateau)
    cross_track = _cross_track_analysis(output)
    coverage = _coverage_rows()
    write_csv(output / "coverage_checklist.csv", coverage)
    _write_diagrams(output, kernel_diagram)
    _plots(output, algorithms, grover_rows, qml_rows, qml_history, noise, plateau)
    write_json(output / "environment.json", collect_environment_metadata(ROOT))
    vqc_rows = [row for row in qml_rows if row["model"] == "variational_quantum_classifier_qnn"]
    kernel_rows = [row for row in qml_rows if row["model"] == "quantum_fidelity_kernel_svc"]
    manifest = {
        "track": "I",
        "status": "verified_simulation_with_syllabus_gap",
        "result_type": "local CPU simulation only; no physical quantum or annealing hardware was used",
        "runtime_seconds": time.perf_counter() - started,
        "authoritative_named_algorithm_count": 7,
        "named_algorithms_executed": [row["algorithm"] for row in algorithms] + ["annealing proxy"],
        "hand_written_circuits": ["Deutsch-Jozsa", "Bernstein-Vazirani", "Grover oracle/diffuser", "QFT"],
        "dataset": "binary Iris subset (petal length and width); bundled with scikit-learn",
        "dataset_digest": split.digest,
        "mean_vqc_accuracy": float(np.mean([row["accuracy"] for row in vqc_rows])),
        "mean_quantum_kernel_accuracy": float(np.mean([row["accuracy"] for row in kernel_rows])),
        "annealing_exact_hits": sum(float(row["optimality_gap"]) == 0.0 for row in annealing),
        "track_d_best_measured_speedup": cross_track["median_speedup"],
        "physical_hardware_access_decision": "Not used: the project constraint avoids paid services and no authorized free-device credentials were supplied; the PDF permits a hardware-noise model where access allows.",
        "reused_track_c_evidence": {
            "QAOA": "tracks/C_quantum_optimization/results/qaoa_best.json",
            "VQE_QNG": "tracks/C_quantum_optimization/results/vqe_runs.csv",
            "parameter_shift": "tracks/C_quantum_optimization/results/parameter_shift.json",
            "finite_shots": "tracks/C_quantum_optimization/results/finite_shots_summary.csv",
            "annealer_embedding_limits": "tracks/C_quantum_optimization/results/embedding_chain_strength.csv",
        },
        "unresolved": "The actual Chapter 6 classroom material was not supplied. The PDF's named list is covered, but additional taught quantum/QML methods cannot be certified and remain explicitly blocked.",
    }
    artifacts = sorted(str(path.relative_to(output)) for path in output.rglob("*") if path.is_file() and not path.name.startswith("."))
    manifest["artifacts"] = sorted({"manifest.json", *artifacts})
    write_json(output / "manifest.json", manifest)
    return manifest
