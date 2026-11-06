"""Collect the fixed Track G workload matrix from a prepared xv6 checkout."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tracks.G_xv6.implementation.qemu_runner import run_qemu_command


WORKLOADS = ("cpu", "io", "mixed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--scheduler", choices=("baseline", "priority"), required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--rebuild-first", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    arguments = parser.parse_args()

    first = True
    for workload in WORKLOADS:
        for repeat in range(1, arguments.repeats + 1):
            log_path = arguments.results / f"{arguments.scheduler}_{workload}_r{repeat}.log"
            if arguments.skip_existing and log_path.exists():
                print(f"[SKIP] {log_path}")
                continue
            command = f"schedbench {workload} {repeat}"
            result = run_qemu_command(
                checkout=arguments.checkout.resolve(),
                command=command,
                expected="GBENCH_DONE",
                timeout_seconds=arguments.timeout,
                rebuild=arguments.rebuild_first and first,
            )
            first = False
            header = (
                f"# scheduler={arguments.scheduler}\n"
                f"# checkout={arguments.checkout.resolve()}\n"
                f"# command={command}\n"
                f"# elapsed_seconds={result.elapsed_seconds:.6f}\n"
                f"# booted={str(result.booted).lower()}\n"
                f"# expected_seen={str(result.expected_seen).lower()}\n"
                f"# qemu_returncode={result.returncode}\n"
            )
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(header + result.transcript, encoding="utf-8")
            passed = result.booted and result.expected_seen and result.returncode == 0
            print(f"[{'PASS' if passed else 'FAIL'}] {log_path}")
            if not passed:
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
