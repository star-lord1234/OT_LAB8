# Track G scheduler design

## Pinned baseline

- Upstream: MIT `xv6-riscv`
- Commit: `fa2ddcb7ca87a77af579380a6eafd5aff163b44f`
- QEMU CPUs for all comparisons: one
- Tool prefix: `riscv64-elf-`

The one-CPU choice makes the ordering policy measurable and avoids presenting
multi-core parallelism as a scheduler benefit. It is a benchmark control, not a
claim that xv6 only supports one CPU.

## Existing behavior

At the pinned commit, timer interrupts call `yield()`. The process becomes
`RUNNABLE`, enters `sched()`, and returns to the per-CPU `scheduler()` context.
The scheduler scans the fixed `proc[]` table from its first slot to its last,
acquiring one `p->lock` at a time. Every `RUNNABLE` process encountered is
changed to `RUNNING` and context-switched. There is no priority field or
priority-setting system call. This is a simple preemptive table-scan policy,
often described as round-robin-like, although table order affects selection.

## Objective and controlled comparison

The optimization objective is to reduce mean turnaround ticks for explicitly
high-priority jobs while retaining work conservation and eventual completion of
all low-priority jobs. Throughput, makespan, and a Jain fairness index over
inverse turnaround are reported as trade-offs; an improvement is not assumed.

Both comparison images contain the same `schedbench` binary, process priority
field, `setpriority(int)` API, workload sizes, and measurement calls. The
unoptimized comparison scheduler deliberately ignores the stored priority. The
optimized scheduler is the only behavioral difference. Separately, the pristine
upstream commit is built, booted, and subjected to full `usertests` before this
support code is applied.

## Affected kernel surface

- `kernel/proc.h`: bounded base priority and scheduler wait-round state.
- `kernel/proc.c`: initialization/reset, priority setter, and scheduler choice.
- `kernel/defs.h`: internal setter declaration.
- `kernel/sysproc.c`, `kernel/syscall.c`, `kernel/syscall.h`: syscall plumbing.
- `user/user.h`, `user/usys.pl`: user API and generated stub.
- `Makefile`: include the benchmark binary in the file-system image.

No virtual-memory, file-system, interrupt, or context-switch assembly is
changed.

## Locks, states, and invariants

1. A process's `state`, `priority`, and wait-round counter are read or changed
   only while holding its `p->lock`.
2. Only `RUNNABLE` processes are candidates; selection changes exactly one to
   `RUNNING` before `swtch`.
3. `scheduler()` enters `swtch` holding only the selected `p->lock`, preserving
   xv6's existing `sched()` contract and avoiding a second process lock across
   a context switch.
4. Timer preemption remains unchanged.
5. Priority is restricted to 0 (highest), 1 (default), or 2 (lowest).
6. Aging lowers the effective priority of a waiting process after fixed numbers
   of scheduler rounds. Long-waiting processes win ties, providing a bounded
   progress mechanism rather than strict-priority starvation.
7. The scheduler retries if another CPU changes a candidate after the scan;
   even though measurements use one CPU, the selection code must remain safe
   for xv6's default multi-CPU build.

## Workloads

One user program exposes three fixed modes and spawns six simultaneous jobs:
three at priority 0 and three at priority 2. A ready/start pipe barrier keeps
the release protocol identical.

- `cpu`: eighty million deterministic integer-mixing iterations per job.
- `io`: thirty short compute bursts separated by one-tick sleeps. This is a
  timer-blocked I/O surrogate, not a disk benchmark.
- `mixed`: ten five-million-iteration compute bursts separated by one-tick
  sleeps.

Every child writes a fixed result record to the parent. The parent reports the
same fields under both schedulers: job ID, PID, priority, release tick,
completion tick, turnaround, and checksum. Every run must produce six unique
jobs, three per priority, and nonzero deterministic checksums.

## Metrics and limitations

Turnaround is `completion_tick - common_release_tick`. Makespan is the latest
completion minus the release tick. Throughput is jobs per xv6 tick. The fairness
index is computed over `1 / turnaround`, so a value near one means similar
completion responsiveness; it is not CPU-share fairness. Tick granularity,
QEMU translation, console activity, and the tiny fixed workload limit external
validity. Results are xv6/QEMU measurements, not macOS scheduler measurements.
