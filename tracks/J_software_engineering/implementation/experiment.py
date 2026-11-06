"""End-to-end Track J experiment on a pinned public Python project."""

from __future__ import annotations

import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np

from optlab.common.config import ExperimentConfig
from optlab.common.environment import collect_environment_metadata
from optlab.common.results import write_csv, write_json

from .selection import (
    Selection,
    TestCandidate,
    cumulative_schedule,
    exhaustive_maximum_coverage,
    greedy_maximum_coverage,
    original_order_select,
)


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "external" / "more-itertools"
PINNED_COMMIT = "f42daddf205f335fea6e200dad46049f33e71221"
REMOTE = "https://github.com/more-itertools/more-itertools.git"


def _command(*arguments: str, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _verify_source() -> dict[str, object]:
    if not (PROJECT / ".git").is_dir():
        raise FileNotFoundError(
            "Track J checkout is missing. Run ./scripts/prepare_track_j.sh first."
        )
    commit = _command("git", "rev-parse", "HEAD", cwd=PROJECT)
    if commit != PINNED_COMMIT:
        raise RuntimeError(f"Track J requires {PINNED_COMMIT}, found {commit}")
    license_path = PROJECT / "LICENSE"
    license_text = license_path.read_text(encoding="utf-8")
    if "Permission is hereby granted, free of charge" not in license_text:
        raise RuntimeError("pinned checkout no longer has the expected MIT license text")
    source_files = sorted((PROJECT / "more_itertools").glob("*.py"))
    physical_lines = 0
    nonblank_noncomment = 0
    for path in source_files:
        lines = path.read_text(encoding="utf-8").splitlines()
        physical_lines += len(lines)
        nonblank_noncomment += sum(
            bool(line.strip()) and not line.lstrip().startswith("#") for line in lines
        )
    return {
        "project": "more-itertools",
        "remote": REMOTE,
        "commit": commit,
        "commit_date": _command("git", "show", "-s", "--format=%cI", "HEAD", cwd=PROJECT),
        "commit_subject": _command("git", "show", "-s", "--format=%s", "HEAD", cwd=PROJECT),
        "license": "MIT",
        "license_sha256": hashlib.sha256(license_path.read_bytes()).hexdigest(),
        "python_source_files": [str(path.relative_to(PROJECT)) for path in source_files],
        "python_physical_lines": physical_lines,
        "python_nonblank_noncomment_lines": nonblank_noncomment,
        "checkout_dirty": bool(_command("git", "status", "--porcelain", cwd=PROJECT)),
        "installation": "not installed; source imported through an isolated PYTHONPATH",
    }


def _pytest_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def _plain_pytest(nodes: list[str] | None = None) -> dict[str, object]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        *(nodes or ["tests"]),
        "-q",
        "--disable-warnings",
        "--rootdir=.",
    ]
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=PROJECT,
        env=_pytest_environment(),
        check=False,
        capture_output=True,
        text=True,
    )
    wall_time = time.perf_counter() - started
    summary = (completed.stdout + "\n" + completed.stderr).strip().splitlines()
    final_line = next((line for line in reversed(summary) if " passed" in line or " failed" in line), summary[-1] if summary else "")
    match = re.search(r"(\d+) passed", final_line)
    if completed.returncode != 0 or not match:
        raise RuntimeError(f"external pytest run failed: {final_line}")
    return {
        "return_code": completed.returncode,
        "passed_tests": int(match.group(1)),
        "wall_time_seconds": wall_time,
        "pytest_summary": final_line,
    }


def _profile(nodes: list[str], target: Path) -> dict[str, object]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join((str(ROOT), str(ROOT / "src")))
    command = [
        sys.executable,
        "-m",
        "tracks.J_software_engineering.implementation.profile_worker",
        "--project",
        str(PROJECT),
        "--output",
        str(target),
    ]
    for node in nodes:
        command.extend(("--node", node))
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"coverage worker failed: {completed.stdout}\n{completed.stderr}")
    return json.loads(target.read_text(encoding="utf-8"))


def _candidate_group(nodeid: str) -> str:
    parts = nodeid.split("::")
    return "::".join(parts[:2]) if len(parts) >= 3 else nodeid


def _stratified_positions(size: int, count: int) -> tuple[int, ...]:
    if count > size:
        raise ValueError(f"requested {count} candidates from only {size} test classes")
    positions = []
    for raw in np.linspace(0, size - 1, count):
        position = int(round(float(raw)))
        if position not in positions:
            positions.append(position)
    cursor = 0
    while len(positions) < count:
        if cursor not in positions:
            positions.append(cursor)
        cursor += 1
    return tuple(sorted(positions[:count]))


def _build_candidates(profile: dict[str, object], count: int) -> tuple[TestCandidate, ...]:
    order = [str(value) for value in profile["test_order"]]
    durations = {str(key): float(value) for key, value in profile["durations_seconds"].items()}
    context_lines = {
        str(key): frozenset(map(str, value))
        for key, value in profile["context_lines"].items()
    }
    group_order: list[str] = []
    group_tests: dict[str, list[str]] = {}
    for nodeid in order:
        group = _candidate_group(nodeid)
        if group not in group_tests:
            group_order.append(group)
            group_tests[group] = []
        group_tests[group].append(nodeid)
    eligible = []
    for original_order, group in enumerate(group_order):
        lines = frozenset().union(*(context_lines.get(node, frozenset()) for node in group_tests[group]))
        cost = sum(durations.get(node, 0.0) for node in group_tests[group])
        if lines and cost > 0:
            eligible.append((original_order, group, lines, cost, len(group_tests[group])))
    selected_positions = _stratified_positions(len(eligible), count)
    return tuple(
        TestCandidate(
            candidate_id=eligible[position][1],
            original_order=eligible[position][0],
            covered_lines=eligible[position][2],
            cost_seconds=max(eligible[position][3], 1e-6),
            test_count=eligible[position][4],
        )
        for position in selected_positions
    )


def _candidate_rows(candidates: tuple[TestCandidate, ...], exact_ids: set[str]) -> list[dict[str, object]]:
    universe = frozenset().union(*(candidate.covered_lines for candidate in candidates))
    rows = []
    for candidate in candidates:
        other_lines = frozenset().union(*(
            other.covered_lines for other in candidates if other.candidate_id != candidate.candidate_id
        ))
        rows.append({
            "candidate_id": candidate.candidate_id,
            "original_order": candidate.original_order,
            "contained_tests": candidate.test_count,
            "measured_test_duration_seconds": candidate.cost_seconds,
            "covered_line_count": len(candidate.covered_lines),
            "lines_unique_within_candidate_pool": len(candidate.covered_lines - other_lines),
            "candidate_universe_line_count": len(universe),
            "included_in_exact_subset": candidate.candidate_id in exact_ids,
        })
    return rows


def _actual_context_lines(profile: dict[str, object]) -> frozenset[str]:
    return frozenset().union(*(
        frozenset(map(str, lines)) for lines in profile["context_lines"].values()
    ))


def _run_selection(
    selection: Selection,
    *,
    repeats: int,
    profile_target: Path,
    universe: frozenset[str],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    nodes = [candidate.candidate_id for candidate in selection.selected]
    if not nodes:
        raise AssertionError(f"{selection.method} selected no tests")
    runs = []
    for repeat in range(repeats):
        run = _plain_pytest(nodes)
        runs.append({"method": selection.method, "repeat": repeat, **run})
    profile = _profile(nodes, profile_target)
    actual_lines = _actual_context_lines(profile)
    predicted_lines = selection.covered_lines
    summary = {
        "method": selection.method,
        "selected_candidates": len(selection.selected),
        "selected_tests": sum(candidate.test_count for candidate in selection.selected),
        "profiled_selection_cost_seconds": selection.cost_seconds,
        "budget_seconds": selection.budget_seconds,
        "objective_covered_lines": len(predicted_lines),
        "candidate_universe_lines": len(universe),
        "objective_coverage_fraction": len(predicted_lines) / len(universe),
        "actual_context_covered_lines": len(actual_lines),
        "profile_prediction_matches_rerun": actual_lines == predicted_lines,
        "actual_source_covered_lines_including_imports": int(profile["overall_covered_lines"]),
        "actual_total_source_statements": int(profile["total_statements"]),
        "actual_source_coverage_percent_including_imports": float(profile["source_coverage_percent"]),
        "actual_wall_time_seconds_median": statistics.median(float(run["wall_time_seconds"]) for run in runs),
        "actual_wall_time_seconds_min": min(float(run["wall_time_seconds"]) for run in runs),
        "actual_wall_time_seconds_max": max(float(run["wall_time_seconds"]) for run in runs),
        "all_selected_runs_passed": all(int(run["return_code"]) == 0 for run in runs),
    }
    return summary, runs


def _plots(output: Path, schedule_rows: list[dict[str, object]], summaries: list[dict[str, object]]) -> None:
    plots = output / "plots"
    plots.mkdir(exist_ok=True)
    figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for method in ("original_order", "greedy_coverage_per_second"):
        rows = [row for row in schedule_rows if row["method"] == method]
        axes[0].step(
            [0.0, *[float(row["cumulative_profiled_cost_seconds"]) for row in rows]],
            [0, *[int(row["cumulative_covered_lines"]) for row in rows]],
            where="post",
            marker="o",
            label=method,
        )
    axes[0].set(xlabel="Profiled test duration (seconds)", ylabel="Unique source lines", title="Coverage acquired within fixed budget")
    axes[0].legend(fontsize=8)
    main = [row for row in summaries if row["method"] != "exact_exhaustive"]
    labels = [str(row["method"]).replace("greedy_coverage_per_second", "greedy").replace("original_order", "original") for row in main]
    axes[1].bar(labels, [float(row["objective_coverage_fraction"]) for row in main], color=["tab:gray", "tab:blue"])
    axes[1].set(ylim=(0, 1.05), ylabel="Fraction of candidate coverage universe", title="Budgeted selection quality")
    for axis in axes:
        axis.grid(alpha=0.25)
    figure.savefig(plots / "coverage_vs_budget.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    axes[0].bar(labels, [float(row["actual_wall_time_seconds_median"]) for row in main], color=["tab:gray", "tab:blue"])
    axes[0].set(ylabel="Median wall time (seconds)", title="Executed selected suites")
    axes[1].bar(labels, [int(row["selected_tests"]) for row in main], color=["tab:gray", "tab:blue"])
    axes[1].set(ylabel="Individual tests retained", title="Reliability checks retained")
    for axis in axes:
        axis.grid(alpha=0.25)
    figure.savefig(plots / "runtime_and_tests_retained.png", dpi=150, metadata={"Software": "OTLab_8"})
    plt.close(figure)


def run_experiment(config: ExperimentConfig) -> dict[str, object]:
    output = config.output_dir
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    source = _verify_source()
    write_json(output / "source_provenance.json", source)
    candidate_count = int(config.parameters.get("candidate_count", 24))
    exact_count = int(config.parameters.get("exact_candidate_count", 14))
    budget_fraction = float(config.parameters.get("budget_fraction", 0.35))
    if not 0 < budget_fraction < 1:
        raise ValueError("budget_fraction must lie strictly between zero and one")
    if not 1 <= exact_count <= candidate_count:
        raise ValueError("exact_candidate_count must be in [1, candidate_count]")

    baseline_runs = []
    for repeat in range(config.repeats):
        baseline_runs.append({"repeat": repeat, **_plain_pytest()})
    write_csv(output / "baseline_runs.csv", baseline_runs)

    with tempfile.TemporaryDirectory(prefix="track-j-") as temporary:
        temporary_path = Path(temporary)
        full_profile = _profile([], temporary_path / "full_profile.json")
        if int(full_profile["exit_code"]) != 0:
            raise AssertionError("instrumented full suite did not pass")
        candidates = _build_candidates(full_profile, candidate_count)
        exact_candidates = candidates[:exact_count]
        exact_ids = {candidate.candidate_id for candidate in exact_candidates}
        write_csv(output / "candidate_profile.csv", _candidate_rows(candidates, exact_ids))
        write_json(output / "candidate_coverage.json", {
            "line_id_definition": "repository-relative source path plus executable line number",
            "candidate_lines": {
                candidate.candidate_id: sorted(candidate.covered_lines)
                for candidate in candidates
            },
        })
        universe = frozenset().union(*(candidate.covered_lines for candidate in candidates))
        total_cost = sum(candidate.cost_seconds for candidate in candidates)
        budget = total_cost * budget_fraction
        original = original_order_select(candidates, budget)
        greedy = greedy_maximum_coverage(candidates, budget)
        exact_universe = frozenset().union(*(candidate.covered_lines for candidate in exact_candidates))
        exact_budget = sum(candidate.cost_seconds for candidate in exact_candidates) * budget_fraction
        exact = exhaustive_maximum_coverage(exact_candidates, exact_budget)
        small_original = original_order_select(exact_candidates, exact_budget)
        small_greedy = greedy_maximum_coverage(exact_candidates, exact_budget)

        summaries = []
        selected_runs = []
        for selection, scope_universe in ((original, universe), (greedy, universe), (exact, exact_universe)):
            summary, runs = _run_selection(
                selection,
                repeats=config.repeats,
                profile_target=temporary_path / f"{selection.method}.json",
                universe=scope_universe,
            )
            summaries.append(summary)
            selected_runs.extend(runs)

    write_csv(output / "selection_summary.csv", summaries)
    write_csv(output / "selected_suite_runs.csv", selected_runs)
    schedule_rows = [*cumulative_schedule(original), *cumulative_schedule(greedy), *cumulative_schedule(exact)]
    write_csv(output / "selected_tests.csv", schedule_rows)
    baseline_profile = {
        "profiled_before_optimization": True,
        "full_suite_passed_tests": len(full_profile["outcomes"]),
        "all_full_suite_tests_passed": all(value == "passed" for value in full_profile["outcomes"].values()),
        "instrumented_wall_time_seconds": full_profile["wall_time_seconds"],
        "covered_source_lines_including_imports": full_profile["overall_covered_lines"],
        "total_source_statements": full_profile["total_statements"],
        "source_coverage_percent": full_profile["source_coverage_percent"],
        "candidate_class_count_available": len({_candidate_group(node) for node in full_profile["test_order"]}),
        "candidate_class_count_profiled": len(candidates),
        "individual_test_count": len(full_profile["test_order"]),
        "slowest_profiled_candidates": sorted(
            (
                {"candidate_id": candidate.candidate_id, "duration_seconds": candidate.cost_seconds}
                for candidate in candidates
            ),
            key=lambda row: float(row["duration_seconds"]),
            reverse=True,
        )[:5],
    }
    write_json(output / "baseline_profile.json", baseline_profile)
    exact_reference = {
        "scope": f"first {exact_count} candidates from the measured {candidate_count}-candidate pool",
        "budget_seconds": exact_budget,
        "candidate_universe_lines": len(exact_universe),
        "exact_objective_lines": len(exact.covered_lines),
        "greedy_objective_lines": len(small_greedy.covered_lines),
        "original_order_objective_lines": len(small_original.covered_lines),
        "greedy_optimality_gap_lines": len(exact.covered_lines) - len(small_greedy.covered_lines),
        "original_order_optimality_gap_lines": len(exact.covered_lines) - len(small_original.covered_lines),
        "exact_selected_candidates": [candidate.candidate_id for candidate in exact.selected],
    }
    write_json(output / "exact_subset_reference.json", exact_reference)
    _plots(output, schedule_rows, summaries)
    write_json(output / "environment.json", collect_environment_metadata(ROOT, package_names=("pytest", "coverage", "pytest-cov")))

    original_summary = next(row for row in summaries if row["method"] == "original_order")
    greedy_summary = next(row for row in summaries if row["method"] == "greedy_coverage_per_second")
    manifest = {
        "track": "J",
        "status": "verified",
        "runtime_seconds": time.perf_counter() - started,
        "source_commit": PINNED_COMMIT,
        "source_license": "MIT",
        "source_python_physical_lines": source["python_physical_lines"],
        "full_suite_tests": len(full_profile["test_order"]),
        "full_suite_passed": baseline_profile["all_full_suite_tests_passed"],
        "candidate_count": candidate_count,
        "budget_fraction": budget_fraction,
        "budget_seconds": budget,
        "original_objective_lines": original_summary["objective_covered_lines"],
        "greedy_objective_lines": greedy_summary["objective_covered_lines"],
        "greedy_line_improvement": int(greedy_summary["objective_covered_lines"]) - int(original_summary["objective_covered_lines"]),
        "all_selected_suites_passed": all(bool(row["all_selected_runs_passed"]) for row in summaries),
        "coverage_predictions_verified": all(bool(row["profile_prediction_matches_rerun"]) for row in summaries),
        "claim_limit": "selected suites are budgeted risk-reduction subsets, not substitutes for the full regression suite",
    }
    artifacts = sorted(str(path.relative_to(output)) for path in output.rglob("*") if path.is_file() and not path.name.startswith("."))
    manifest["artifacts"] = sorted({"manifest.json", *artifacts})
    write_json(output / "manifest.json", manifest)
    return manifest
