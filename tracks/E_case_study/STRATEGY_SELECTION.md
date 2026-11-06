# Track E Strategy Selection

The machine-readable required table is [results/strategy_selection.csv](results/strategy_selection.csv). It records variable type, scale, exact-versus-heuristic status, constraints, hardware, parallelism, convergence/optimality, communication cost, and selection rationale.

FCFS is retained as the transparent baseline. Greedy is selected for scalable online decisions and direct padding awareness. Dynamic programming is selected as a Chapter 6-style discrete method that exactly solves the bounded local subset score. Exhaustive enumeration is validation-only because ordered partitions grow combinatorially. A full time-indexed MILP was considered but rejected for the minimal online implementation: it would add model size and solver machinery without representing future unknown arrivals any better.

No row claims actual hardware parallelism. “Within-batch parallelism” refers only to the simulated service equation.
