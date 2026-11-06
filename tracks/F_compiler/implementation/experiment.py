"""Benchmark baseline versus four-pass optimized toy compilation."""

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

from .ir import code_size_bytes, compile_source, execute, serialize
from .pass_order import branch_and_bound_pass_order, exhaustive_pass_order
from .passes import FULL_PASS_ORDER, apply_passes, optimization_trace
from .programs import load_programs


ROOT = Path(__file__).resolve().parents[3]


def _timed_compile(source: str, optimized: bool, iterations: int) -> float:
    started = time.perf_counter()
    for _ in range(iterations):
        instructions = compile_source(source)
        if optimized:
            instructions = apply_passes(instructions)
    return (time.perf_counter() - started) / iterations


def _timed_execute(instructions, inputs, iterations: int) -> float:
    execute(instructions, inputs)
    started = time.perf_counter()
    for _ in range(iterations):
        execute(instructions, inputs)
    return (time.perf_counter() - started) / iterations


def _summaries(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for program in sorted({str(row["program"]) for row in rows}):
        for mode in ("baseline", "optimized_four_pass"):
            group = [row for row in rows if row["program"] == program and row["mode"] == mode]
            output.append({
                "program": program,
                "mode": mode,
                "repeats": len(group),
                "instruction_count": int(group[0]["instruction_count"]),
                "code_size_bytes": int(group[0]["code_size_bytes"]),
                "execution_seconds_mean": statistics.fmean(float(row["execution_seconds_per_run"]) for row in group),
                "execution_seconds_std": statistics.pstdev(float(row["execution_seconds_per_run"]) for row in group),
                "compilation_seconds_mean": statistics.fmean(float(row["compilation_seconds_per_run"]) for row in group),
                "compilation_seconds_std": statistics.pstdev(float(row["compilation_seconds_per_run"]) for row in group),
                "semantic_equivalent": all(bool(row["semantic_equivalent"]) for row in group),
            })
    return output


def _plots(output: Path, summaries: list[dict[str, object]]) -> None:
    plots = output / "plots"
    plots.mkdir(exist_ok=True)
    programs = sorted({str(row["program"]) for row in summaries})
    x = np.arange(len(programs))
    width = 0.36
    figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for index, mode in enumerate(("baseline", "optimized_four_pass")):
        group = [next(row for row in summaries if row["program"] == program and row["mode"] == mode) for program in programs]
        axes[0].bar(x + (index - 0.5) * width, [row["instruction_count"] for row in group], width, label=mode)
        axes[1].bar(x + (index - 0.5) * width, [row["code_size_bytes"] for row in group], width, label=mode)
    axes[0].set(ylabel="IR instructions", title="Static instruction count")
    axes[1].set(ylabel="Serialized IR bytes", title="Generated code size")
    for axis in axes: axis.set_xticks(x, [name.replace("_", "\n") for name in programs]); axis.grid(axis="y", alpha=0.25); axis.legend(fontsize=8)
    figure.savefig(plots / "instruction_count_code_size.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for mode in ("baseline", "optimized_four_pass"):
        group = [next(row for row in summaries if row["program"] == program and row["mode"] == mode) for program in programs]
        axes[0].plot(programs, [row["execution_seconds_mean"] * 1e6 for row in group], marker="o", label=mode)
        axes[1].plot(programs, [row["compilation_seconds_mean"] * 1e6 for row in group], marker="o", label=mode)
    axes[0].set(ylabel="Microseconds / execution", title="IR interpreter runtime")
    axes[1].set(ylabel="Microseconds / compilation", title="Compilation cost")
    for axis in axes: axis.tick_params(axis="x", rotation=20); axis.grid(alpha=0.25); axis.legend(fontsize=8)
    figure.savefig(plots / "runtime_compile_time.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)


def run_experiment(config: ExperimentConfig) -> dict[str, object]:
    output = config.output_dir
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    programs = load_programs()
    execution_iterations = int(config.parameters.get("execution_iterations", 5000))
    compilation_iterations = int(config.parameters.get("compilation_iterations", 500))
    rows: list[dict[str, object]] = []
    traces: list[dict[str, object]] = []
    semantic_rows: list[dict[str, object]] = []
    snapshots = []
    suite = {}
    for program in programs:
        baseline = compile_source(program.source)
        optimized = apply_passes(baseline)
        suite[program.name] = baseline
        baseline_output = execute(baseline, program.inputs)
        optimized_output = execute(optimized, program.inputs)
        equivalent = baseline_output == optimized_output == program.expected
        semantic_rows.append({
            "program": program.name, "inputs": program.inputs, "expected": list(program.expected),
            "baseline_output": list(baseline_output), "optimized_output": list(optimized_output),
            "semantic_equivalent": equivalent,
        })
        snapshots.append({
            "program": program.name, "source": program.source,
            "baseline_ir": serialize(baseline), "optimized_ir": serialize(optimized),
            "baseline_instruction_count": len(baseline), "optimized_instruction_count": len(optimized),
        })
        traces.extend({"program": program.name, **point} for point in optimization_trace(baseline))
        for repeat, seed in enumerate(config.seeds):
            del seed
            for mode, instructions, optimized_flag in (
                ("baseline", baseline, False),
                ("optimized_four_pass", optimized, True),
            ):
                rows.append({
                    "program": program.name,
                    "mode": mode,
                    "repeat": repeat,
                    "passes": "none" if not optimized_flag else ";".join(FULL_PASS_ORDER),
                    "instruction_count": len(instructions),
                    "code_size_bytes": code_size_bytes(instructions),
                    "execution_seconds_per_run": _timed_execute(instructions, program.inputs, execution_iterations),
                    "compilation_seconds_per_run": _timed_compile(program.source, optimized_flag, compilation_iterations),
                    "execution_iterations": execution_iterations,
                    "compilation_iterations": compilation_iterations,
                    "output": list(execute(instructions, program.inputs)),
                    "semantic_equivalent": equivalent,
                })
    summaries = _summaries(rows)
    branch = branch_and_bound_pass_order(suite, int(config.parameters.get("pass_effort_budget", 8)))
    exhaustive = exhaustive_pass_order(suite, int(config.parameters.get("pass_effort_budget", 8)))
    decision = {
        "formulation": "choose an ordered subset of passes, each at most once, minimizing total suite instruction count subject to sum of pass effort costs <= budget",
        "pass_costs": {"constant_folding_propagation": 3, "common_subexpression_elimination": 3, "strength_reduction": 2, "dead_code_elimination": 3},
        "branch_and_bound": branch,
        "exhaustive_reference": exhaustive,
        "verified_equal": branch["selected_order"] == exhaustive["selected_order"] and branch["optimized_instruction_count"] == exhaustive["optimized_instruction_count"],
    }
    write_csv(output / "benchmark_runs.csv", rows)
    write_csv(output / "benchmark_summary.csv", summaries)
    write_csv(output / "optimization_trace.csv", traces)
    write_json(output / "semantic_equivalence.json", semantic_rows)
    write_json(output / "ir_snapshots.json", snapshots)
    write_json(output / "pass_order_decision.json", decision)
    _plots(output, summaries)
    write_json(output / "environment.json", collect_environment_metadata(ROOT))
    manifest = {
        "track": "F",
        "status": "verified_four_pass_toy_compiler",
        "runtime_seconds": time.perf_counter() - started,
        "programs": [program.name for program in programs],
        "passes": list(FULL_PASS_ORDER),
        "all_semantically_equivalent": all(row["semantic_equivalent"] for row in semantic_rows),
        "pass_order_verified_exact": decision["verified_equal"],
        "selected_budgeted_order": branch["selected_order"],
        "artifacts": sorted({"manifest.json", *(str(path.relative_to(output)) for path in output.rglob("*") if path.is_file() and not path.name.startswith("."))}),
    }
    write_json(output / "manifest.json", manifest)
    return manifest
