# Original user prompt

Implement Track G using xv6-riscv and QEMU, following the existing setup documentation.

First verify that unmodified xv6 boots and that its usertests pass.

For the minimum implementation, modify one kernel feature, preferably a simple scheduling-related optimization such as a priority-based scheduler, provided the selected xv6 version supports a safe, verifiable implementation.

Before modifying the kernel:
1. Explain the current scheduling behavior.
2. Define the optimization objective.
3. Identify affected kernel functions, locks, process states, and invariants.
4. Create three user-level benchmark workloads.
5. Measure the original scheduler.

Implement the smallest kernel modification necessary, with optional measurement system calls only if needed.

Benchmark at least three workload types, for example CPU-bound, I/O-heavy, and mixed processes.

Measure turnaround time, waiting time, response time, throughput, or fairness as appropriate to the selected optimization.

Maintain identical workload definitions between baseline and optimized configurations.

After every significant change, rebuild, boot, and test xv6.

Verify:
- The kernel boots successfully
- No obvious scheduling deadlocks or starvation issues
- Existing usertests pass
- Benchmark programs execute correctly

Preserve the baseline commit and produce a clean patch/diff.

A second kernel feature is only necessary if pursuing the assignment's full-credit extension. Do not add it unless the first feature is fully verified.

Do not silently alter xv6 kernel internals, suppress failing tests, or claim performance improvements unsupported by measurements.

Record actual benchmark output, limitations, patch details, AI prompts, and the Track G report section.
