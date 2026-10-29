# Track D — Submodular, Parallel, Distributed, and Multi-task Optimization

Status: **implemented and experimentally verified on local CPU processes; additional Chapter 6 methods remain syllabus-dependent**. Measurements used the recorded Apple M5 MacBook Air (10 logical cores, 16 GB RAM), Python 3.12.13, and the `spawn` multiprocessing context.

## D.1 Submodular maximum coverage

The objective is `f(S)=|union of the selected sets|` over six fixed subsets of a ten-element universe with cardinality budget two. Exhaustive property checks evaluated 729 subset-containment pairs for monotonicity, 1,458 marginal-gain comparisons for diminishing returns, and all 4,096 subset pairs for the submodular inequality; no violation occurred ([definition and verifier](../tracks/D_parallel_distributed/implementation/submodular.py), [result](../tracks/D_parallel_distributed/results/submodular.json)).

Greedy first chose the unique five-element set, then added a set with marginal gain two, covering seven elements. Exact enumeration of all 15 feasible pairs selected sets 1 and 2 and covered eight, so the observed greedy ratio was `7/8 = 0.875` ([plot](../tracks/D_parallel_distributed/results/plots/submodular_coverage.png)). The standard `1-1/e` guarantee applies because this objective is normalized, nonnegative, monotone, and submodular under a cardinality constraint. It would not automatically apply after adding arbitrary costs, non-monotone terms, or different feasibility constraints.

## D.2 CPU scheduling, makespan, and scaling laws

All schedulers ran the same twelve deterministic CPU-bound integer tasks and produced the same aggregate checksum. Three repetitions retained raw makespan, per-PID compute load, imbalance, speedup, efficiency, and overhead ([raw runs](../tracks/D_parallel_distributed/results/parallel_runs.csv), [summary](../tracks/D_parallel_distributed/results/parallel_summary.csv)). The median serial time was 0.1953 s.

Contiguous static scheduling was slower: 0.2800 s at two processes (`0.697x`, efficiency `0.349`) and 0.2309 s at four (`0.846x`, efficiency `0.211`). Its median imbalance ratios were 1.56 and 2.11 because heavy tasks were clustered. The real central shared-queue scheduler reduced imbalance to 1.002 and 1.083. It still slowed to 0.2173 s at two processes (`0.899x`, efficiency `0.449`) but narrowly improved in the median to 0.1835 s at four (`1.065x`, efficiency `0.266`); at least one four-process repeat was still slower than serial. Every parallel configuration observed the requested number of independent worker PIDs. These are laptop measurements, not universal performance claims.

The separate local-deque work-stealing simulation is intentionally labeled non-wall-clock evidence. Three steals reduce modeled cost from 885,000 to 600,000 units at two workers and from 600,000 to 350,000 at four; all task IDs are checked exactly once ([simulation and full schedule](../tracks/D_parallel_distributed/results/work_stealing_simulation.json)). This explains load balancing but does not replace the real process measurements.

Inverting Amdahl's law from the measured two-process slowdown gives an impossible raw serial fraction of 1.225 because startup/scheduling overhead violates the simple fixed-work model; it is retained and clamped to one rather than hidden. With that overhead-dominated fit, both Amdahl and Gustafson predict no useful scaling. Gustafson's result would become relevant only if the useful workload grew with processor count, whereas these fixed tiny tasks expose overhead ([law calculations](../tracks/D_parallel_distributed/results/scaling_laws.json), [plot](../tracks/D_parallel_distributed/results/plots/parallel_scaling.png)).

## D.3 Locality, synchronization, communication, and parallel forms

Controlled variants preserved outputs ([overhead results](../tracks/D_parallel_distributed/results/overhead_experiments.json)). Row-major traversal took 0.0283 s versus 0.0445 s column-major (`1.57x` slower). Two processes incrementing a locked shared counter took 0.3387 s versus 0.1177 s for independent local counts plus reduction, an added 0.2210 s. In a warmed two-process pool, acknowledging four 250,000-integer payloads took 0.0189 s versus 0.000588 s for compact equivalent size messages: `32.21x`, or 0.0183 s measured communication overhead. The compact tasks were so short that one worker handled them; the transferred payloads used both PIDs. The comparison measures IPC/serialization, not network latency.

Data parallelism splits one linear-regression batch and aggregates exact sufficient statistics; its gradient differs from the serial gradient by at most `4.44e-16`. Tensor/model parallelism splits hidden units and sums partial outputs (`1.42e-14` maximum error). Pipeline parallelism runs the two layers in two persistent processes over eight microbatches with zero observed error. Each used two explicit spawned PIDs ([results](../tracks/D_parallel_distributed/results/parallel_forms.csv), [plot](../tracks/D_parallel_distributed/results/plots/parallel_forms_overheads.png)). Because the serial kernels take about `0.0001` s while process startup takes about `0.11` s, speedups were only `0.00139`, `0.000706`, and `0.000810`. These negative results identify the granularity threshold rather than claiming an improvement.

## D.4 Federated averaging

Four deterministic non-IID clients each contain 80 logistic-regression examples; their positive-class fractions range from 0.2875 to 0.55. Every comparison starts at zero weights and matches centralized gradient steps to `rounds × local_steps` ([metadata](../tracks/D_parallel_distributed/results/federated_metadata.json), [results](../tracks/D_parallel_distributed/results/federated_comparison.csv), [plot](../tracks/D_parallel_distributed/results/plots/federated_comparison.png)).

With one local step, FedAvg exactly equals centralized full-batch gradient descent: loss 0.5400 after five rounds and 0.4597 after ten. With three local steps, client drift creates small differences: at five rounds centralized/FedAvg losses were 0.41064/0.41126; at ten they were 0.33345/0.33380. Accuracy matched at 0.9281 and 0.9438 respectively. Communication was 1,600 bytes for five rounds and 3,200 for ten under the explicit two-way parameter-count model; centralized training records zero federated communication. This is an in-process federated simulation, not a network deployment or privacy guarantee.

## D.5 Equal weighting, MGDA, and GradNorm

All methods reuse the same data and initial weights for a two-head model with a shared two-unit tanh bottleneck. Initial task losses were 3.8670 and 3.8151. After 120 full-batch epochs, equal weighting reached losses 0.3674/0.4279 (mean 0.3977). GradNorm adapted weights to 0.812/1.188 and reached 0.4144/0.3921 (mean 0.4032), a more balanced pair. Two-gradient MGDA's minimum-norm weight converged to 1.978/0.022 and reached 0.2169/2.1846 (mean 1.2007), exposing a task trade-off rather than dominating equal weighting ([results](../tracks/D_parallel_distributed/results/multitask_comparison.csv), [training history](../tracks/D_parallel_distributed/results/multitask_history.csv), [plot](../tracks/D_parallel_distributed/results/plots/multitask_comparison.png)).

MGDA is implemented as the closed-form minimum-norm convex combination of the two shared gradients. GradNorm updates positive task weights toward equalized weighted gradient norms adjusted by relative training rates. This small case demonstrates mechanics and failure modes; it does not establish which method is generally best.

## D.6 Reproduction, verification, and syllabus blocker

Run:

```bash
./scripts/run_track.py D
.venv/bin/python -m pytest tracks/D_parallel_distributed/tests
```

Tests cover exhaustive submodularity, the known greedy counterexample, serial/parallel checksums, work-stealing task conservation, explicit PID independence, serial equivalence of three parallel forms, FedAvg aggregation/training, and all three multi-task methods. The [manifest](../tracks/D_parallel_distributed/results/manifest.json) indexes the generated evidence. D-08 remains **UNRESOLVED** until the actual Chapter 6 syllabus confirms whether FedProx, SCAFFOLD, PCGrad, CAGrad, or another distributed/multi-task method was taught.
