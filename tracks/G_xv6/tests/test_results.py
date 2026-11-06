from __future__ import annotations

import json
from pathlib import Path

import pytest

from tracks.G_xv6.implementation.results import (
    aggregate_runs,
    comparisons,
    load_matrix,
    parse_log,
    validate_usertest_log,
)


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "G_xv6"


def test_each_archived_run_conserves_jobs_and_priorities() -> None:
    for scheduler in ("baseline", "priority"):
        for workload in ("cpu", "io", "mixed"):
            for repeat in range(1, 4):
                jobs, makespan = parse_log(
                    TRACK / "results" / "raw" / f"{scheduler}_{workload}_r{repeat}.log"
                )
                assert len(jobs) == 6
                assert makespan == max(job.turnaround for job in jobs)
                assert sorted(job.priority for job in jobs) == [0, 0, 0, 2, 2, 2]


def test_same_work_is_executed_under_both_schedulers() -> None:
    jobs, _ = load_matrix(TRACK / "results" / "raw")
    checksums: dict[tuple[str, int], set[int]] = {}
    for job in jobs:
        checksums.setdefault((job.workload, job.job), set()).add(job.checksum)
    assert len(jobs) == 108
    assert all(len(values) == 1 for values in checksums.values())


def test_measured_cpu_priority_effect_and_progress() -> None:
    _, runs = load_matrix(TRACK / "results" / "raw")
    comparison = {row["workload"]: row for row in comparisons(aggregate_runs(runs))}
    cpu = comparison["cpu"]
    assert cpu["priority_high_mean_turnaround_ticks"] < cpu["baseline_high_mean_turnaround_ticks"]
    assert cpu["priority_low_mean_turnaround_ticks"] > 0
    assert cpu["priority_makespan_ticks"] <= cpu["baseline_makespan_ticks"]


@pytest.mark.parametrize(
    "filename",
    ["pristine_usertests.log", "baseline_usertests.log", "priority_usertests.log"],
)
def test_archived_full_usertests_pass(filename: str) -> None:
    status = validate_usertest_log(TRACK / "results" / "raw" / filename)
    assert status["booted"] is True
    assert status["all_tests_passed"] is True
    assert status["explicit_failed_lines"] == []


def test_manifest_does_not_claim_second_feature() -> None:
    manifest = json.loads((TRACK / "results" / "manifest.json").read_text())
    assert manifest["status"] == "verified_single_feature"
    assert manifest["all_jobs_completed"] is True
    assert manifest["all_usertests_passed"] is True
    assert manifest["second_feature_attempted"] is False
