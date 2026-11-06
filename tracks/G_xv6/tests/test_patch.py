from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "G_xv6"


def changed_files(patch: str) -> set[str]:
    files = set()
    for line in patch.splitlines():
        if line.startswith("diff --git a/"):
            files.add(line.split()[2].removeprefix("a/"))
    return files


def test_scheduler_only_diff_is_one_kernel_file() -> None:
    patch = (TRACK / "patches" / "scheduler-only.patch").read_text()
    assert changed_files(patch) == {"kernel/proc.c"}
    assert "PRIORITY_AGING_ROUNDS" in patch
    assert "selected->state = RUNNING" in patch


def test_complete_patch_contains_benchmark_and_syscall() -> None:
    patch = (TRACK / "patches" / "priority-scheduler.patch").read_text()
    files = changed_files(patch)
    assert "user/schedbench.c" in files
    assert "kernel/syscall.c" in files
    assert "kernel/proc.c" in files
    assert "setpriority" in patch


def test_support_baseline_excludes_scheduler_selection() -> None:
    patch = (TRACK / "patches" / "baseline-support.patch").read_text()
    files = changed_files(patch)
    assert "user/schedbench.c" in files
    assert "kernel/proc.c" in files
    assert "ksetpriority" in patch
    assert "PRIORITY_AGING_ROUNDS" not in patch


def test_canonical_workload_matches_patched_version() -> None:
    source = (TRACK / "implementation" / "xv6" / "user" / "schedbench.c").read_text()
    assert 'strcmp(workload, "cpu")' in source
    assert 'strcmp(workload, "io")' in source
    assert 'strcmp(workload, "mixed")' in source
    assert "#define JOBS 6" in source
    assert "80000000" in source
