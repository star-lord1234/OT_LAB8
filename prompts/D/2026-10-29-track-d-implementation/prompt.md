# Original user prompt

Implement Track D as several small, independently verifiable experiments sharing the same benchmark infrastructure.

Part 1: Submodular optimization

- Choose a simple set-coverage objective.
- Verify monotonicity, submodularity, and diminishing returns on small instances.
- Compare greedy selection with exact enumeration.
- Discuss any approximation guarantee and its assumptions.

Part 2: Parallel optimization

- Use CPU-bound workloads.
- Compare serial execution with process-based parallel execution.
- Investigate load balancing, work stealing or a defensible small work-stealing simulation, locality, synchronization, and communication overhead.
- Demonstrate data, model, and pipeline parallelism at a minimal but meaningful scale.
- Measure makespan, speedup, and parallel efficiency.
- Interpret results using Amdahl's and Gustafson's laws.

Part 3: Distributed optimization

- Simulate federated learning with FedAvg against centralized training.
- Vary communication rounds and local training steps.
- On a small two-task model, compare equal loss weighting against MGDA and GradNorm.

Respect macOS multiprocessing requirements and ensure parallel methods actually execute independently.

Use identical workloads wherever comparison is claimed, record overhead, and report negative speedups honestly.

Implement tests, plots, benchmark exports, prompt logs, and the Track D report section.

Do not replace mandatory experiments with purely theoretical explanations.
