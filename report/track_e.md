# Track E — Simulated Inference-request Batching and Scheduling

Status: **implemented and verified as a discrete-event simulation**. No LLM, GPU, accelerator, production server, energy use, or real inference latency was measured.

## E.1 Process, workload, and optimization need

The case study models a single inference-like server receiving requests with arrival time, estimated token length, processing cost, and completion-deadline SLO. Synthetic arrivals are exponential at rates 0.6 and 1.2 requests per simulated time unit. Token lengths use a documented short/medium/long mixture, processing cost is length times a seeded factor in `[0.012,0.018]`, and deadlines equal arrival plus `3 + 0.04 × tokens` ([generator](../tracks/E_case_study/implementation/workload.py), [raw requests](../tracks/E_case_study/results/synthetic_requests.csv)).

The grid uses 24, 64, and 128 requests, summed-token capacities 384 and 512, three fixed seeds, and the same workload digest for every method and both capacity settings at a given size/rate/repeat ([workload register](../tracks/E_case_study/results/workloads.csv)). At 128 requests, rate 1.2, and capacity 512, immediate FCFS had simulated mean latency 12.911, p95 24.390, throughput 1.025 requests/time-unit, and a 73.4% deadline-miss rate. This overloaded baseline establishes a simulated scheduling bottleneck; it is not evidence about an actual LLM deployment.

## E.2 Formulation, constraints, and service model

The full formulation is in [MATHEMATICS.md](../tracks/E_case_study/MATHEMATICS.md). Binary assignment variables map each request to exactly one ordered batch. Hard constraints cover request-count capacity, summed tokens, padded tokens, arrival precedence, single-server non-overlap, and bounded intentional batch-formation wait. Completion deadlines use explicit nonnegative tardiness slack because overload can make them infeasible.

For batch `b`, simulated service is `T_b = 0.35 + max(p_i)[1 + 0.22(n_b-1)]`. The objective is mean latency plus twice mean tardiness plus `0.15 × busy-time/request`. Mean/p95/p99 latency, mean/p95 wait, throughput, makespan, deadline misses, server utilization, batch size, token-capacity use, and useful-to-padded token efficiency remain separate outputs. The equation is hypothetical and reproducible, not hardware calibration.

## E.3 Strategy selection

The required [strategy-selection table](../tracks/E_case_study/results/strategy_selection.csv) records variable types, scale, exact/heuristic status, constraints, hardware, parallelism, convergence/optimality, communication cost, and rationale. A readable discussion is in [STRATEGY_SELECTION.md](../tracks/E_case_study/STRATEGY_SELECTION.md), and the assignment-wide matrix is in [report/strategy_selection.md](strategy_selection.md).

FCFS immediately dispatches a feasible arrival-order prefix and intentionally waits zero time. Greedy holds for at most 0.8 time units when more arrivals may form a batch, anchors overdue requests when necessary, otherwise selects the shortest estimated job, then adds length-compatible requests. Dynamic programming exactly maximizes a count/urgency/compatibility score inside a 12-request lookahead using count/token knapsack states and enumerated maximum lengths. That local exactness does not make the complete online schedule globally optimal. A full MILP was rejected for this minimal online study; a six-request exhaustive ordered-partition solver supplies the global tiny reference instead.

## E.4 Repeated comparison and crossover

All 108 method runs passed request-conservation, capacity, event-order, service-time, and objective-recalculation checks ([raw runs](../tracks/E_case_study/results/runs.csv), [verification](../tracks/E_case_study/results/verification.csv), [summary](../tracks/E_case_study/results/summary.csv)). Standard deviations across the three workloads are retained rather than reporting only a favorable run.

At sparse rate 0.6, 128 requests, capacity 512, immediate FCFS was best: mean latency 3.186 versus 3.914 greedy and 4.023 DP. Its mean wait was 1.016 versus 1.475 and 1.518. Throughput was essentially equal near 0.585, so deliberate batch formation added latency without useful throughput gain. This is the requested circumstance in which batching is worse.

At loaded rate 1.2 on the same size/capacity, greedy was strongest: mean latency 7.116, p95 15.992, throughput 1.131, makespan 113.435, and 47.9% misses. FCFS produced 12.911, 24.390, 1.025, 124.986, and 73.4%; DP produced 8.936, 17.166, 1.102, 116.270, and 68.5%. Greedy's mean batch size was 3.30 and padding efficiency 0.757. Its server utilization (0.956) was lower than FCFS (0.994) because it completed the modeled work with less busy time; high utilization alone was not the goal ([size plot](../tracks/E_case_study/results/plots/latency_throughput_by_size.png), [load plot](../tracks/E_case_study/results/plots/batching_load_tradeoff.png)).

Increasing summed-token capacity from 384 to 512 at the loaded 128-request setting improved greedy throughput from 1.084 to 1.131 and mean latency from 7.650 to 7.116. Deadline misses changed only from 48.2% to 47.9%, showing that capacity alone does not remove an offered-load/SLO mismatch ([capacity plot](../tracks/E_case_study/results/plots/capacity_slo_efficiency.png)).

## E.5 Exact reference and correctness

For six simultaneous requests, exhaustive enumeration found objective 2.577813 with batches `[0,1,4]`, `[2,3]`, and `[5]` ([exact reference](../tracks/E_case_study/results/tiny_exact_reference.json)). Greedy happened to match that optimum. The online DP selector scored 2.593243, a 0.01543 global gap, because it optimizes a local selection score rather than the report's full future completion objective. FCFS scored 3.847300. This counterexample prevents an unsupported claim that “DP” automatically means global schedule optimality.

Tests independently verify workload reproducibility, FCFS prefix behavior, DP equality with exhaustive subset scoring, every-request-exactly-once processing, capacity and event invariants, objective recomputation, sparse-traffic latency regression, capacity-sweep workload identity, and exhaustive-plan consistency.

## E.6 Reproduction, trade-offs, and scope

Run:

```bash
./scripts/run_track.py E
.venv/bin/python -m pytest tracks/E_case_study/tests
```

The [manifest](../tracks/E_case_study/results/manifest.json) indexes 13 artifacts. The service model excludes prefill/decode separation, KV-cache behavior, cancellation, priorities, multi-server routing, network transfer, real memory allocation, and prediction error. Greedy can starve long jobs without the urgent-anchor rule; DP costs more scheduling time and can optimize the wrong local surrogate; waiting windows hurt sparse traffic. Therefore the results demonstrate optimization methodology and trade-offs only—not actual inference acceleration.
