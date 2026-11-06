# Track G — xv6 Priority Scheduling

Status: **implemented and verified for the mandatory one-feature scope**. The
experiment uses QEMU simulation of a RISC-V machine; it does not measure the
macOS scheduler or physical RISC-V hardware.

## G.1 Baseline behavior and objective

The official MIT `xv6-riscv` source is pinned at
`fa2ddcb7ca87a77af579380a6eafd5aff163b44f`. Its preemptive scheduler scans the
fixed process table in slot order, acquiring one process lock at a time and
running each `RUNNABLE` process encountered. Timer interrupts call `yield()`;
there is no priority field or priority API. The complete control-flow, process
states, locks, and invariants are documented in
[DESIGN.md](../tracks/G_xv6/DESIGN.md).

The optimization objective is to reduce high-priority job turnaround on one
QEMU CPU while preserving work conservation and completion of every
low-priority job. The experiment also reports makespan, jobs per xv6 tick, and
a Jain index over inverse turnaround, so prioritization costs are visible. A
separate response-time or waiting-time syscall was not added; the available
turnaround metrics are not mislabeled as those quantities.

## G.2 Kernel feature and correctness invariants

The complete [patch](../tracks/G_xv6/patches/priority-scheduler.patch) contains
the fixed user benchmark, a bounded `setpriority(int)` API, and the scheduler.
The [support-baseline diff](../tracks/G_xv6/patches/baseline-support.patch)
reconstructs the unoptimized comparison image from pristine upstream.
The [scheduler-only diff](../tracks/G_xv6/patches/scheduler-only.patch) is 75
lines and changes only `kernel/proc.c`. Base priority is 0, 1, or 2 (lower is
higher). Every eight runnable scheduling rounds, aging improves a waiting
process's effective priority by one level; the longest-waiting process wins a
tie. Base priority itself is not mutated.

The scheduler reads or changes state, priority, and wait rounds only while
holding `p->lock`; revalidates the selected process after the scan; switches
only `RUNNABLE → RUNNING`; and enters `swtch` holding only the selected process
lock. Existing timer preemption remains intact. The scan/revalidation design
avoids retaining multiple process locks and safely retries if another CPU takes
the candidate, although controlled measurements use one CPU.

Three recoverable xv6 commits separate concerns: pristine upstream
`fa2ddcb7`, comparison support `51265fa`, and scheduler behavior `643d1fc`.
The support baseline and optimized image contain identical `schedbench`
binaries, priority fields, syscall plumbing, workload sizes, and measurements;
only scheduler selection differs.

## G.3 Workloads and measured results

Each fixed mode spawns six jobs behind the same ready/start pipe barrier: three
priority-0 and three priority-2 jobs. CPU mode performs deterministic integer
mixing; the I/O-heavy mode is explicitly a timer-blocked sleep surrogate; mixed
mode alternates compute and sleep. This is not a disk-I/O benchmark. Each child
reports a deterministic checksum, common release tick, completion tick, and
turnaround. Three independent QEMU boots were retained for every
scheduler/workload pair ([108 job records](../tracks/G_xv6/results/benchmark_jobs.csv),
[run table](../tracks/G_xv6/results/benchmark_runs.csv)).

For CPU-bound work, priority scheduling reduced high-priority mean turnaround
from 6.0 to 3.0 ticks (50%). Low-priority mean turnaround was 6.89 ticks under
the baseline and 6.78 under priority; every low-priority job completed. Mean
makespan moved from 7.33 to 7.0 ticks and mean throughput from 0.821 to 0.857
jobs/tick, changes small enough to treat cautiously at tick resolution. The
Jain inverse-turnaround index fell from 0.993 to 0.870, correctly exposing the
responsiveness inequality introduced by prioritization.

The I/O surrogate was unchanged: both schedulers had 30-tick high/low
turnaround, 30-tick makespan, and 0.2 jobs/tick. Mixed work was also unchanged
at 10 ticks and 0.6 jobs/tick. Thus the evidence supports a CPU-contention
priority effect, not a general throughput claim. The complete values and
standard deviations are in the [summary](../tracks/G_xv6/results/benchmark_summary.csv),
[direct comparison](../tracks/G_xv6/results/scheduler_comparison.csv), and
[plot](../tracks/G_xv6/results/plots/scheduler_metrics.png).

## G.4 Boot, usertests, progress, and patch verification

The pristine upstream kernel built and booted, then full `usertests` ended in
`ALL TESTS PASSED` ([transcript](../tracks/G_xv6/results/raw/pristine_usertests.log)).
After benchmark/API support, the unoptimized scheduler again passed the full
suite ([baseline transcript](../tracks/G_xv6/results/raw/baseline_usertests.log)).
After the scheduler change, the full suite passed a third time
([optimized transcript](../tracks/G_xv6/results/raw/priority_usertests.log)).
Expected negative-test page faults appear in the raw upstream output and are
not suppressed.

Every one of the 18 benchmark runs booted and completed six unique PIDs, three
per priority. Checksums for each workload/job are identical across repeats and
schedulers. This provides a bounded no-starvation observation, not a proof for
arbitrary workloads. The complete patch passed `git apply --check` against a
fresh clone at the pinned commit, applied, rebuilt, booted, and executed the CPU
benchmark ([patch verification](../tracks/G_xv6/results/raw/patch_verification.log)).
Machine-readable gate status is retained in
[usertests_status.json](../tracks/G_xv6/results/usertests_status.json).

## G.5 Limitations and reproduction

Run the host-side evidence checks with:

```bash
./scripts/run_track.py G
.venv/bin/python -m pytest tracks/G_xv6/tests
./scripts/test_all.sh
```

The experiment uses one emulated CPU, three repeats, six jobs, coarse xv6
ticks, QEMU 11.1.1, and RISC-V GCC 16.2.0. Console output and dynamic
translation can perturb timing. The fairness metric measures equality of
inverse turnaround, not CPU-share fairness. Aging demonstrated progress in
these finite workloads, but formal starvation bounds under all arrivals are not
claimed. Only one kernel feature was implemented; the optional second-feature
full-credit extension was deliberately not attempted before the mandatory
tracks are complete. The [manifest](../tracks/G_xv6/results/manifest.json) and
[environment record](../tracks/G_xv6/results/environment.json) index the
evidence.

The external base is MIT's xv6-riscv, used under its permissive MIT license
(copyright Frans Kaashoek, Robert Morris, Russ Cox, and MIT, 2006-2024). The
Track G benchmark, scheduler changes, host parser, tests, and documentation are
project additions generated with the disclosed AI-assisted workflow.
