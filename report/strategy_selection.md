# Repository-wide Optimization Strategy Selection

This matrix is provisional where the exact Chapter 6 syllabus or a future track implementation is still missing.

| Track | Variables and constraints | Scale/method choice | Hardware and parallelism | Convergence, optimality, and communication |
|---|---|---|---|---|
| A | Real parameters; unconstrained/regularized objectives | First/second-order methods on tiny objectives and model | CPU; MPS unavailable | Stationarity/convergence measured; stochastic variability repeated; no communication |
| B | Binary selections; capacity and QUBO penalties | Greedy, exact ILP, branch-and-bound, DP | CPU | Exact methods verified by enumeration; no communication |
| C | Circuit angles and measured quantum objectives | Small QAOA/VQE/QNN simulations | Local CPU quantum simulators | Exact classical references; shot/noise cost reported; no hardware claim |
| D | Sets, process tasks, model weights | Greedy/exact coverage, spawned processes, FedAvg, MGDA, GradNorm | CPU processes; simulated federation | Checksums/exact coverage; FedAvg communication counted |
| E | Binary batch assignments, order, start times; count/token/SLO constraints | Immediate FCFS, scalable greedy, exact local DP, tiny exhaustive reference | Single CPU discrete-event simulation; modeled batch parallelism only | DP exact only for bounded local score; exhaustive tiny global optimum; no interprocess/network communication |
| F | Ordered pass subset under effort budget | Branch-and-bound with exhaustive reference; full four-pass benchmark | CPU toy compiler/interpreter | Exact equality on 35 feasible orders; no communication |
| G | Discrete runnable-process choice; priority 0-2; lock/state invariants; aging | Table-scan baseline versus lowest effective priority with aging | One emulated RISC-V CPU under QEMU; 3 workloads × 3 repeats | All jobs and checksums verified; priority improves CPU high-class turnaround, not I/O/mixed; fairness cost reported |
| H | Five binary optional-index choices; actual page costs; 180-page budget | No optional index baseline, benefit/page greedy, binary MILP, exact 0/1 knapsack DP | Local CPU, SQLite 3.53.1; no parallelism | MILP/DP exact for additive surrogate; final SQLite plans/timings re-measured; all result hashes equal |
| I | Planned discrete/continuous quantum and QML parameters | Exact circuits plus matched classical baselines | Local simulator unless access changes | Not implemented; quantum advantage cannot be claimed |
| J | Planned binary test selection under time budget | Greedy/exact small reference on pinned public code | CPU | Not implemented; coverage/runtime trade-off to be measured |

Track-specific detail and rejected alternatives for the main case study are in [Track E's strategy table](../tracks/E_case_study/STRATEGY_SELECTION.md).
