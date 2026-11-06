"""Regenerate Track G tables and figure from archived QEMU transcripts."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache" / "xdg"))

import matplotlib.pyplot as plt

from tracks.G_xv6.implementation.results import generate_outputs


def make_plot(results_dir: Path) -> None:
    with (results_dir / "benchmark_summary.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    index = {(row["scheduler"], row["workload"]): row for row in rows}
    workloads = ["cpu", "io", "mixed"]
    positions = list(range(len(workloads)))
    width = 0.2
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for offset, scheduler, priority, label in (
        (-1.5, "baseline", "high", "baseline high"),
        (-0.5, "baseline", "low", "baseline low"),
        (0.5, "priority", "high", "priority high"),
        (1.5, "priority", "low", "priority low"),
    ):
        values = [float(index[(scheduler, workload)][f"{priority}_mean_turnaround_ticks_mean"]) for workload in workloads]
        axes[0].bar([position + offset * width for position in positions], values, width, label=label)
    axes[0].set_xticks(positions, workloads)
    axes[0].set_ylabel("Mean turnaround (xv6 ticks)")
    axes[0].set_title("Priority separates completion time")
    axes[0].legend(fontsize=7)

    for scheduler, marker in (("baseline", "o"), ("priority", "s")):
        throughput = [float(index[(scheduler, workload)]["throughput_jobs_per_tick_mean"]) for workload in workloads]
        axes[1].plot(workloads, throughput, marker=marker, label=scheduler)
    axes[1].set_ylabel("Throughput (jobs / xv6 tick)")
    axes[1].set_title("System throughput")
    axes[1].legend()
    figure.suptitle("Track G: one-CPU xv6/QEMU scheduler benchmark")
    figure.tight_layout()
    output = results_dir / "plots" / "scheduler_metrics.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def main(_config: str | None = None) -> int:
    generated = generate_outputs(ROOT)
    make_plot(ROOT / "tracks" / "G_xv6" / "results")
    print(
        "Track G regenerated: "
        f"{len(generated['jobs'])} job records, "
        f"all_usertests_passed={generated['manifest']['all_usertests_passed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
