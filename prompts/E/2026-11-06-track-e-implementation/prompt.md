# Original user prompt

Implement Track E, our main real-process case study, using inference-request batching and scheduling as the optimization problem.

We want to investigate how batching and scheduling affect inference throughput, latency, waiting time, and resource utilization.

Use a documented synthetic request workload with varying arrival times, estimated token lengths, and processing costs. State clearly that the workload is simulated and do not claim actual LLM inference improvements.

Implement:

1. A naive first-come-first-served baseline
2. At least two optimization strategies, such as greedy length-aware batching and dynamic programming or another justified Chapter 6 method
3. Explicit capacity and latency constraints
4. A reproducible discrete-event or equivalent scheduling simulation
5. Performance comparisons across several workload sizes

Mathematically define decision variables, objectives, constraints, and assumptions.

Create the assignment's required strategy-selection table covering variable types, problem size, exact versus heuristic methods, hardware, and parallelism.

Report mean and tail latency, throughput, makespan, and any chosen resource-utilization metric.

Verify that every request is processed exactly once, batch capacity constraints are satisfied, and objective calculations are correct.

Run repeated workloads under identical conditions. Explain trade-offs and circumstances in which batching makes latency worse.

If the provided `bm.md` chooses a different main case study, inspect that choice first and preserve it unless there is a strong reason to change it.

Create a complete Track E report section, tests, plots, prompt logs, and benchmark results.
