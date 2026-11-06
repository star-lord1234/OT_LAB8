"""Parse and validate archived xv6 scheduler benchmark transcripts."""

from __future__ import annotations

import csv
import json
import math
import platform
import re
import statistics
import subprocess
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


RESULT_PATTERN = re.compile(
    r"^GRESULT workload=(?P<workload>\w+) repeat=(?P<repeat>\d+) "
    r"job=(?P<job>\d+) pid=(?P<pid>\d+) priority=(?P<priority>\d+) "
    r"start=(?P<start>\d+) end=(?P<end>\d+) "
    r"turnaround=(?P<turnaround>\d+) checksum=(?P<checksum>-?\d+)$"
)
SUMMARY_PATTERN = re.compile(
    r"^GBENCH_DONE workload=(?P<workload>\w+) repeat=(?P<repeat>\d+) "
    r"jobs=(?P<jobs>\d+) makespan=(?P<makespan>\d+)$"
)
FILE_PATTERN = re.compile(
    r"(?P<scheduler>baseline|priority)_(?P<workload>cpu|io|mixed)_r(?P<repeat>\d+)\.log"
)


@dataclass(frozen=True)
class JobResult:
    scheduler: str
    workload: str
    repeat: int
    job: int
    pid: int
    priority: int
    start: int
    end: int
    turnaround: int
    checksum: int
    source_log: str


def parse_log(path: Path) -> tuple[list[JobResult], int]:
    match = FILE_PATTERN.fullmatch(path.name)
    if not match:
        raise ValueError(f"unexpected benchmark filename: {path.name}")
    scheduler = match.group("scheduler")
    expected_workload = match.group("workload")
    expected_repeat = int(match.group("repeat"))
    jobs: list[JobResult] = []
    summary: re.Match[str] | None = None
    text = path.read_text(encoding="utf-8")
    if "# booted=true" not in text or "# expected_seen=true" not in text:
        raise ValueError(f"QEMU success metadata missing: {path}")
    for line in text.splitlines():
        result_match = RESULT_PATTERN.fullmatch(line.strip())
        if result_match:
            values = {key: int(value) if key != "workload" else value
                      for key, value in result_match.groupdict().items()}
            jobs.append(
                JobResult(
                    scheduler=scheduler,
                    workload=str(values["workload"]),
                    repeat=int(values["repeat"]),
                    job=int(values["job"]),
                    pid=int(values["pid"]),
                    priority=int(values["priority"]),
                    start=int(values["start"]),
                    end=int(values["end"]),
                    turnaround=int(values["turnaround"]),
                    checksum=int(values["checksum"]),
                    source_log=path.name,
                )
            )
        summary_match = SUMMARY_PATTERN.fullmatch(line.strip())
        if summary_match:
            summary = summary_match

    if len(jobs) != 6 or summary is None:
        raise ValueError(f"expected six jobs and one complete summary: {path}")
    if {job.job for job in jobs} != set(range(6)):
        raise ValueError(f"job conservation failed: {path}")
    if len({job.pid for job in jobs}) != 6:
        raise ValueError(f"PID uniqueness failed: {path}")
    if sorted(job.priority for job in jobs) != [0, 0, 0, 2, 2, 2]:
        raise ValueError(f"priority allocation failed: {path}")
    if any(
        job.workload != expected_workload or job.repeat != expected_repeat
        for job in jobs
    ):
        raise ValueError(f"filename/payload mismatch: {path}")
    if len({job.start for job in jobs}) != 1:
        raise ValueError(f"release barrier mismatch: {path}")
    if any(job.turnaround != job.end - job.start or job.turnaround <= 0 for job in jobs):
        raise ValueError(f"turnaround arithmetic failed: {path}")
    if int(summary.group("jobs")) != 6:
        raise ValueError(f"summary job count failed: {path}")
    makespan = int(summary.group("makespan"))
    if makespan != max(job.turnaround for job in jobs):
        raise ValueError(f"summary makespan failed: {path}")
    return jobs, makespan


def load_matrix(raw_dir: Path, repeats: int = 3) -> tuple[list[JobResult], list[dict[str, float | int | str]]]:
    all_jobs: list[JobResult] = []
    runs: list[dict[str, float | int | str]] = []
    checksum_reference: dict[tuple[str, int], int] = {}
    for scheduler in ("baseline", "priority"):
        for workload in ("cpu", "io", "mixed"):
            for repeat in range(1, repeats + 1):
                path = raw_dir / f"{scheduler}_{workload}_r{repeat}.log"
                jobs, makespan = parse_log(path)
                for job in jobs:
                    key = (job.workload, job.job)
                    previous = checksum_reference.setdefault(key, job.checksum)
                    if previous != job.checksum:
                        raise ValueError(f"checksum changed for {key}: {path}")
                turnarounds = [job.turnaround for job in jobs]
                inverse = [1.0 / value for value in turnarounds]
                fairness = sum(inverse) ** 2 / (len(inverse) * sum(x * x for x in inverse))
                high = [job.turnaround for job in jobs if job.priority == 0]
                low = [job.turnaround for job in jobs if job.priority == 2]
                runs.append(
                    {
                        "scheduler": scheduler,
                        "workload": workload,
                        "repeat": repeat,
                        "jobs_completed": len(jobs),
                        "mean_turnaround_ticks": statistics.mean(turnarounds),
                        "high_mean_turnaround_ticks": statistics.mean(high),
                        "low_mean_turnaround_ticks": statistics.mean(low),
                        "priority_separation_ticks": statistics.mean(low) - statistics.mean(high),
                        "makespan_ticks": makespan,
                        "throughput_jobs_per_tick": len(jobs) / makespan,
                        "jain_inverse_turnaround": fairness,
                        "all_jobs_completed": True,
                    }
                )
                all_jobs.extend(jobs)
    return all_jobs, runs


def aggregate_runs(runs: list[dict[str, float | int | str]]) -> list[dict[str, float | int | str]]:
    grouped: dict[tuple[str, str], list[dict[str, float | int | str]]] = defaultdict(list)
    for run in runs:
        grouped[(str(run["scheduler"]), str(run["workload"]))].append(run)
    metrics = (
        "mean_turnaround_ticks",
        "high_mean_turnaround_ticks",
        "low_mean_turnaround_ticks",
        "priority_separation_ticks",
        "makespan_ticks",
        "throughput_jobs_per_tick",
        "jain_inverse_turnaround",
    )
    rows: list[dict[str, float | int | str]] = []
    for (scheduler, workload), items in sorted(grouped.items()):
        row: dict[str, float | int | str] = {
            "scheduler": scheduler,
            "workload": workload,
            "repeats": len(items),
            "jobs_completed_total": sum(int(item["jobs_completed"]) for item in items),
        }
        for metric in metrics:
            values = [float(item[metric]) for item in items]
            row[f"{metric}_mean"] = statistics.mean(values)
            row[f"{metric}_std"] = statistics.pstdev(values)
        rows.append(row)
    return rows


def comparisons(summary: list[dict[str, float | int | str]]) -> list[dict[str, float | str]]:
    indexed = {(str(row["scheduler"]), str(row["workload"])): row for row in summary}
    rows: list[dict[str, float | str]] = []
    for workload in ("cpu", "io", "mixed"):
        baseline = indexed[("baseline", workload)]
        priority = indexed[("priority", workload)]
        row: dict[str, float | str] = {"workload": workload}
        for metric in (
            "high_mean_turnaround_ticks_mean",
            "low_mean_turnaround_ticks_mean",
            "makespan_ticks_mean",
            "throughput_jobs_per_tick_mean",
            "jain_inverse_turnaround_mean",
        ):
            base_value = float(baseline[metric])
            priority_value = float(priority[metric])
            stem = metric.removesuffix("_mean")
            row[f"baseline_{stem}"] = base_value
            row[f"priority_{stem}"] = priority_value
            row[f"delta_{stem}"] = priority_value - base_value
            row[f"percent_change_{stem}"] = (
                math.nan if base_value == 0 else 100.0 * (priority_value - base_value) / base_value
            )
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def validate_usertest_log(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    return {
        "log": path.name,
        "booted": "# booted=true" in text,
        "all_tests_passed": "ALL TESTS PASSED" in text,
        "explicit_failed_lines": [line for line in text.splitlines() if "FAILED" in line],
    }


def generate_outputs(root: Path) -> dict[str, object]:
    track = root / "tracks" / "G_xv6"
    results = track / "results"
    jobs, runs = load_matrix(results / "raw")
    summary = aggregate_runs(runs)
    comparison = comparisons(summary)
    write_csv(results / "benchmark_jobs.csv", [asdict(job) for job in jobs])
    write_csv(results / "benchmark_runs.csv", runs)
    write_csv(results / "benchmark_summary.csv", summary)
    write_csv(results / "scheduler_comparison.csv", comparison)

    test_status = {
        label: validate_usertest_log(results / "raw" / filename)
        for label, filename in {
            "pristine": "pristine_usertests.log",
            "comparison_baseline": "baseline_usertests.log",
            "priority_scheduler": "priority_usertests.log",
        }.items()
    }
    test_status["all_passed"] = all(
        bool(status["booted"] and status["all_tests_passed"] and not status["explicit_failed_lines"])
        for status in test_status.values()
        if isinstance(status, dict)
    )
    (results / "usertests_status.json").write_text(
        json.dumps(test_status, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    environment = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "qemu": subprocess.check_output(["qemu-system-riscv64", "--version"], text=True).splitlines()[0],
        "riscv_gcc": subprocess.check_output(["riscv64-elf-gcc", "--version"], text=True).splitlines()[0],
        "qemu_cpus": 1,
        "upstream_commit": "fa2ddcb7ca87a77af579380a6eafd5aff163b44f",
        "comparison_baseline_commit": "51265fa284f82bd630fa44dc385e5e90ded4a001",
        "priority_scheduler_commit": "643d1fc3590e4fd3639ff7b95814c53c7a94ea81",
    }
    (results / "environment.json").write_text(
        json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    manifest = {
        "track": "G",
        "status": "verified_single_feature",
        "feature": "priority scheduler with aging",
        "workloads": ["cpu", "io", "mixed"],
        "repeats_per_configuration": 3,
        "jobs_per_run": 6,
        "all_jobs_completed": len(jobs) == 108,
        "all_usertests_passed": bool(test_status["all_passed"]),
        "second_feature_attempted": False,
        "artifacts": [
            "benchmark_jobs.csv",
            "benchmark_runs.csv",
            "benchmark_summary.csv",
            "scheduler_comparison.csv",
            "environment.json",
            "usertests_status.json",
            "plots/scheduler_metrics.png",
            "../patches/baseline-support.patch",
            "../patches/priority-scheduler.patch",
            "../patches/scheduler-only.patch",
            "raw/pristine_usertests.log",
            "raw/baseline_usertests.log",
            "raw/priority_usertests.log",
            "raw/patch_verification.log",
        ],
    }
    (results / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {"jobs": jobs, "runs": runs, "summary": summary, "comparison": comparison, "manifest": manifest}
