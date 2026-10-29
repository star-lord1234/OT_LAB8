"""Generate the complete small, simulated Track C evidence bundle."""

from __future__ import annotations

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pennylane as qml

from optlab.common.config import ExperimentConfig
from optlab.common.environment import collect_environment_metadata
from optlab.common.results import write_csv, write_json
from optlab.quantum.diagnostics import barren_plateau_proxy, embedding_chain_strength_demo
from optlab.quantum.maxcut import (
    apply_qaoa,
    distribution_metrics,
    load_maxcut_fixture,
    noisy_qaoa_probabilities,
    optimize_qaoa_adam,
    optimize_qaoa_spsa,
    qaoa_qnodes,
    sample_qaoa,
)
from optlab.quantum.variational import (
    QNN_FEATURES,
    apply_vqe_ansatz,
    classical_qnn_baseline,
    exact_vqe_ground_energy,
    optimize_qnn,
    optimize_vqe,
    parameter_shift_demo,
    qnn_qnode,
    vqe_qnode,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tracks" / "B_discrete" / "results" / "maxcut_track_c_fixture.json"


def _flatten_run(run: dict[str, object]) -> dict[str, object]:
    row = {key: value for key, value in run.items() if key not in {"history", "parameters"}}
    row.update({"backend": "PennyLane default.qubit local simulator", "physical_hardware": False})
    return row


def _run_qaoa(config: ExperimentConfig, output: Path):
    problem = load_maxcut_fixture(FIXTURE)
    steps = int(config.parameters.get("qaoa_steps", 60))
    spsa_steps = int(config.parameters.get("spsa_steps", 80))
    depths = tuple(int(value) for value in config.parameters.get("depths", [1, 2, 3]))
    runs, convergence = [], []
    full_runs = []
    for depth in depths:
        for repeat, seed in enumerate(config.seeds):
            run = optimize_qaoa_adam(problem, depth=depth, seed=seed, steps=steps)
            run["repeat"] = repeat
            full_runs.append(run)
            runs.append(_flatten_run(run))
            convergence.extend({"optimizer": "adam", "depth": depth, "repeat": repeat, "seed": seed, **row} for row in run["history"])
    for repeat, seed in enumerate(config.seeds):
        run = optimize_qaoa_spsa(problem, depth=1, seed=seed, steps=spsa_steps)
        run["repeat"] = repeat
        full_runs.append(run)
        runs.append(_flatten_run(run))
        convergence.extend({"optimizer": "spsa", "depth": 1, "repeat": repeat, "seed": seed, **row} for row in run["history"])
    write_csv(output / "qaoa_runs.csv", runs)
    write_csv(output / "qaoa_convergence.csv", convergence)
    best = max(full_runs, key=lambda row: float(row["expected_cut"]))
    best_document = {key: value for key, value in best.items() if key != "history"}
    best_document.update({
        "track_b_fixture": str(FIXTURE.relative_to(ROOT)),
        "track_b_fixture_sha256": problem.fixture_sha256,
        "classical_optimum_cut": problem.optimum_cut,
        "uniform_random_expected_cut": problem.uniform_expected_cut,
        "result_type": "local noiseless statevector simulation",
    })
    write_json(output / "qaoa_best.json", best_document)
    return problem, full_runs, best


def _shot_study(problem, best, config: ExperimentConfig, output: Path):
    repeats = int(config.parameters.get("shot_repeats", 12))
    shot_counts = (100, 1000, 10000)
    exact_energy, exact_probs = qaoa_qnodes(problem)
    parameters = np.asarray(best["parameters"])
    exact = distribution_metrics(problem, exact_probs(parameters))["expected_cut"]
    rows, summaries = [], []
    seeds = np.random.SeedSequence(config.base_seed + 101).spawn(len(shot_counts) * repeats)
    cursor = 0
    for shots in shot_counts:
        estimates = []
        for repeat in range(repeats):
            seed = int(seeds[cursor].generate_state(1)[0])
            cursor += 1
            samples = sample_qaoa(problem, parameters, shots=shots, seed=seed)
            estimate = float(np.mean([problem.cut_value(row) for row in samples]))
            estimates.append(estimate)
            rows.append({"shots": shots, "repeat": repeat, "seed": seed, "estimated_cut": estimate, "exact_expected_cut": exact, "absolute_error": abs(estimate - exact), "simulated": True})
        summaries.append({"shots": shots, "repeats": repeats, "exact_expected_cut": exact, "mean_estimated_cut": float(np.mean(estimates)), "estimate_variance": float(np.var(estimates)), "mean_absolute_error": float(np.mean(np.abs(np.asarray(estimates) - exact)))})
    write_csv(output / "finite_shots.csv", rows)
    write_csv(output / "finite_shots_summary.csv", summaries)
    return summaries


def _noise_study(problem, best, output: Path):
    parameters = np.asarray(best["parameters"])
    rows = []
    for scale in (0.0, 0.5, 1.0, 2.0):
        single_error, two_error = 0.001 * scale, 0.01 * scale
        probabilities = noisy_qaoa_probabilities(problem, parameters, single_qubit_error=single_error, two_qubit_error=two_error)
        metrics = distribution_metrics(problem, probabilities)
        rows.append({"noise_scale": scale, "single_qubit_depolarizing_probability": single_error, "post_entangler_local_depolarizing_probability": two_error, **metrics, "backend": "PennyLane default.mixed simulator", "physical_hardware": False})
    write_csv(output / "noise_simulation.csv", rows)
    return rows


def _run_vqe(config: ExperimentConfig, output: Path):
    steps = int(config.parameters.get("vqe_steps", 70))
    runs, convergence = [], []
    for method in ("gradient_descent", "quantum_natural_gradient"):
        for repeat, seed in enumerate(config.seeds):
            result = optimize_vqe(method, seed=seed, steps=steps)
            result["repeat"] = repeat
            row = {key: value for key, value in result.items() if key not in {"history", "parameters"}}
            row.update({"backend": "PennyLane default.qubit local simulator", "physical_hardware": False})
            runs.append(row)
            convergence.extend({"method": method, "repeat": repeat, "seed": seed, **row} for row in result["history"])
    exact_started = time.perf_counter()
    exact = exact_vqe_ground_energy()
    classical = {"method": "classical_exact_diagonalization", "ground_energy": exact, "runtime_seconds": time.perf_counter() - exact_started, "matrix_dimension": 4}
    write_csv(output / "vqe_runs.csv", runs)
    write_csv(output / "vqe_convergence.csv", convergence)
    write_json(output / "vqe_classical_reference.json", classical)
    return runs, convergence, classical


def _run_qnn(config: ExperimentConfig, output: Path):
    steps = int(config.parameters.get("qnn_steps", 60))
    runs, convergence = [], []
    for repeat, seed in enumerate(config.seeds):
        result = optimize_qnn(seed=seed, steps=steps)
        result["repeat"] = repeat
        row = {key: value for key, value in result.items() if key not in {"history", "weights", "predictions"}}
        row.update({"backend": "PennyLane default.qubit local simulator", "physical_hardware": False})
        runs.append(row)
        convergence.extend({"repeat": repeat, "seed": seed, **row} for row in result["history"])
    classical = classical_qnn_baseline()
    write_csv(output / "qnn_runs.csv", runs)
    write_csv(output / "qnn_convergence.csv", convergence)
    write_json(output / "qnn_classical_reference.json", classical)
    return runs, convergence, classical


def _circuit_diagrams(problem, best, output: Path) -> None:
    qaoa_energy, _ = qaoa_qnodes(problem)
    vqe_energy = vqe_qnode()
    qnn = qnn_qnode()
    parameters = np.asarray(best["parameters"])
    content = [
        "All diagrams are simulated circuits; no physical quantum hardware was used.",
        "\nQAOA circuit:\n" + qml.draw(qaoa_energy)(parameters),
        "\nVQE ansatz:\n" + qml.draw(vqe_energy)(np.asarray([0.1, 0.2, 0.3, 0.4])),
        "\nQNN circuit:\n" + qml.draw(qnn)(np.asarray([0.1, 0.2, 0.3]), QNN_FEATURES[0]),
    ]
    (output / "circuit_diagrams.txt").write_text("\n".join(content) + "\n", encoding="utf-8")


def _plots(output: Path, qaoa_runs, vqe_convergence, qnn_convergence, classical_qnn, shots, noise, plateau, embedding) -> None:
    plots = output / "plots"
    plots.mkdir(exist_ok=True)

    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    groups = {}
    for run in qaoa_runs:
        label = f"{run['optimizer']}, p={run['depth']}"
        groups.setdefault(label, []).append(run)
    for label, runs in sorted(groups.items()):
        length = min(len(run["history"]) for run in runs)
        axes[0].plot(range(length), [np.mean([run["history"][i]["expected_cut"] for run in runs]) for i in range(length)], label=label)
    axes[0].axhline(8.0, color="black", linestyle="--", label="classical optimum")
    axes[0].set(xlabel="Optimization iteration", ylabel="Expected cut", title="QAOA convergence (mean runs)")
    axes[0].legend(fontsize=7)
    adam = [run for run in qaoa_runs if run["optimizer"].startswith("adam")]
    depths = sorted(set(int(run["depth"]) for run in adam))
    axes[1].plot(depths, [np.mean([run["expected_cut"] for run in adam if run["depth"] == depth]) for depth in depths], marker="o", color="tab:blue", label="expected cut")
    axes[1].set(xlabel="QAOA depth p", ylabel="Expected cut", title="Depth, quality, and evaluation cost")
    cost_axis = axes[1].twinx()
    cost_axis.plot(depths, [np.mean([run["gate_count"] for run in adam if run["depth"] == depth]) for depth in depths], marker="s", color="tab:orange", label="gate count")
    cost_axis.plot(depths, [np.mean([run["parameter_shift_hardware_evaluation_estimate"] for run in adam if run["depth"] == depth]) for depth in depths], marker="^", color="tab:red", label="parameter-shift evaluations")
    cost_axis.set(ylabel="Count (log scale)", yscale="log")
    lines = axes[1].lines + cost_axis.lines
    axes[1].legend(lines, [line.get_label() for line in lines], fontsize=7, loc="center left")
    for axis in axes: axis.grid(alpha=0.25)
    figure.savefig(plots / "qaoa_convergence_depth.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for method in sorted(set(row["method"] for row in vqe_convergence)):
        method_rows = [row for row in vqe_convergence if row["method"] == method]
        iterations = sorted(set(int(row["iteration"]) for row in method_rows))
        axes[0].plot(iterations, [np.mean([row["energy"] for row in method_rows if row["iteration"] == iteration]) for iteration in iterations], label=method)
    axes[0].axhline(exact_vqe_ground_energy(), color="black", linestyle="--", label="exact diagonalization")
    axes[0].set(xlabel="Iteration", ylabel="Energy", title="VQE: GD versus QNG")
    axes[0].legend(fontsize=8)
    qnn_iterations = sorted(set(int(row["iteration"]) for row in qnn_convergence))
    axes[1].plot(qnn_iterations, [np.mean([row["loss"] for row in qnn_convergence if row["iteration"] == iteration]) for iteration in qnn_iterations], label="QNN mean loss")
    axes[1].axhline(classical_qnn["final_loss"], color="black", linestyle="--", label="classical tanh baseline")
    axes[1].set(xlabel="Iteration", ylabel="MSE", title="Two-qubit QNN training")
    axes[1].legend(fontsize=8)
    for axis in axes: axis.grid(alpha=0.25)
    figure.savefig(plots / "vqe_qnn_training.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    axes[0].plot([row["shots"] for row in shots], [row["mean_absolute_error"] for row in shots], marker="o", label="mean absolute error")
    axes[0].plot([row["shots"] for row in shots], [row["estimate_variance"] for row in shots], marker="o", label="estimate variance")
    axes[0].set(xscale="log", yscale="log", xlabel="Shots", title="Finite-shot simulation")
    axes[0].legend(fontsize=8)
    axes[1].plot([row["noise_scale"] for row in noise], [row["expected_cut"] for row in noise], marker="o", color="tab:blue", label="expected cut")
    axes[1].set(xlabel="Noise scale", ylabel="Expected cut", title="Depolarizing-noise simulation")
    probability_axis = axes[1].twinx()
    probability_axis.plot([row["noise_scale"] for row in noise], [row["optimal_probability"] for row in noise], marker="o", color="tab:orange", label="optimal probability")
    probability_axis.set(ylabel="Optimal-bitstring probability", ylim=(0, 1))
    lines = axes[1].lines + probability_axis.lines
    axes[1].legend(lines, [line.get_label() for line in lines], fontsize=8)
    for axis in axes: axis.grid(alpha=0.25)
    figure.savefig(plots / "shots_noise.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(11.5, 4), constrained_layout=True)
    axes[0].plot([row["qubits"] for row in plateau], [row["global_gradient_variance"] for row in plateau], marker="o", label="global cost")
    axes[0].plot([row["qubits"] for row in plateau], [row["local_gradient_variance"] for row in plateau], marker="o", label="local cost")
    axes[0].set(yscale="log", xlabel="Qubits", ylabel="Gradient variance", title="Gradient-variance proxy")
    axes[0].legend(fontsize=8)
    axes[1].plot([row["chain_strength"] for row in embedding], [row["broken_chain_fraction"] for row in embedding], marker="o")
    axes[1].set(xlabel="Ferromagnetic chain strength", ylabel="Broken fraction among ground states", title="Minor-embedding chain breaks")
    for axis in axes: axis.grid(alpha=0.25)
    figure.savefig(plots / "plateau_embedding.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)


def run_experiment(config: ExperimentConfig) -> dict[str, object]:
    output = config.output_dir
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    problem, qaoa_runs, best = _run_qaoa(config, output)
    shots = _shot_study(problem, best, config, output)
    noise = _noise_study(problem, best, output)
    vqe_runs, vqe_convergence, vqe_classical = _run_vqe(config, output)
    qnn_runs, qnn_convergence, qnn_classical = _run_qnn(config, output)
    shift = parameter_shift_demo()
    shift.update({"backend": "PennyLane default.qubit local simulator", "physical_hardware": False})
    write_json(output / "parameter_shift.json", shift)
    plateau = barren_plateau_proxy(repeats=int(config.parameters.get("plateau_repeats", 32)), seed=config.base_seed)
    embedding = embedding_chain_strength_demo()
    write_csv(output / "barren_plateau_proxy.csv", plateau)
    write_csv(output / "embedding_chain_strength.csv", embedding)
    _circuit_diagrams(problem, best, output)
    _plots(output, qaoa_runs, vqe_convergence, qnn_convergence, qnn_classical, shots, noise, plateau, embedding)
    write_json(output / "environment.json", collect_environment_metadata(ROOT))
    manifest = {
        "track": "C",
        "result_type": "local simulation only; no physical quantum hardware was used",
        "status": "verified_experiment_with_syllabus_gap",
        "runtime_seconds": time.perf_counter() - started,
        "track_b_fixture_sha256": problem.fixture_sha256,
        "track_b_classical_optimum_cut": problem.optimum_cut,
        "best_qaoa_expected_cut": best["expected_cut"],
        "best_qaoa_optimal_probability": best["optimal_probability"],
        "vqe_exact_ground_energy": vqe_classical["ground_energy"],
        "qnn_classical_accuracy": qnn_classical["accuracy"],
        "reusable_for_track_i": ["src/optlab/quantum/maxcut.py", "src/optlab/quantum/variational.py", "src/optlab/quantum/diagnostics.py"],
        "unresolved": "Exact Chapter 6 syllabus is unavailable; C-09 remains unresolved for any additional taught hybrid method.",
        "artifacts": sorted({"manifest.json", *(str(path.relative_to(output)) for path in output.rglob("*") if path.is_file() and not path.name.startswith("."))}),
    }
    write_json(output / "manifest.json", manifest)
    return manifest
