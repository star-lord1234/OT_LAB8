# Track E Mathematical Formulation

This is an offline discrete-event simulation of an inference-like request queue. It does not execute an LLM and its time units are not milliseconds or measured hardware time.

## Requests and decision variables

Request `i` has arrival `a_i`, estimated token length `l_i`, estimated processing cost `p_i`, and completion-deadline SLO `d_i`. For conceptual batch slots `b`:

- `x_ib ∈ {0,1}` assigns request `i` to batch `b`.
- `z_b ∈ {0,1}` activates batch `b`.
- `s_b ≥ 0` and `c_b ≥ 0` are batch start and completion times.
- `C_i = Σ_b x_ib c_b` is request completion.
- `u_i ≥ 0` is deadline tardiness.

The online implementations construct these decisions sequentially rather than materializing the full mixed-integer model.

## Service model

For batch `b`, let `n_b` be its request count and `P_b = max_{i∈b} p_i`. Simulated service is

`T_b = h + P_b [1 + ρ(n_b - 1)]`,

where fixed overhead `h=0.35` and parallel penalty `ρ=0.22`. This models amortized launch overhead and imperfect within-batch scaling. It is an explicit hypothetical model, not calibrated LLM/GPU performance.

## Objective

The reported minimization objective is

`J = mean_i(C_i-a_i) + λ mean_i(u_i) + μ (Σ_b T_b)/N`,

with `u_i = max(0, C_i-d_i)`, tardiness weight `λ=2`, compute weight `μ=0.15`, and `N` requests. Mean and p95/p99 latency, waiting time, throughput, makespan, deadline misses, and utilization are also reported separately so the scalar objective cannot hide trade-offs.

## Constraints

1. Exactly once: `Σ_b x_ib = 1` for every request.
2. Arrival: `s_b ≥ a_i x_ib` for every assigned request.
3. Count capacity: `Σ_i x_ib ≤ B z_b`, with `B=4` in the main grid.
4. Summed-token capacity: `Σ_i l_i x_ib ≤ M z_b`, for `M∈{384,512}`.
5. Padded-token capacity: `n_b max_{i∈b} l_i ≤ P`, where `P=M+128`.
6. Single server: batches do not overlap.
7. Formation latency: an optimization policy may intentionally hold an idle server for at most the configured window `w=0.8`; an oldest queued request also caps intentional holding at `a_i+2.0`. Congestion can still cause longer queueing.
8. Completion SLO: `C_i ≤ d_i+u_i`, with `u_i` penalized and reported. Deadlines are not falsely treated as hard-feasible under overload.

## Methods

FCFS immediately dispatches the largest feasible arrival-order prefix. Greedy anchors an overdue request when necessary, otherwise the shortest estimated job, then adds length-compatible requests. Dynamic programming solves a two-dimensional count/token knapsack exactly inside a 12-request online lookahead while enumerating possible maximum token lengths to enforce padded capacity. Its local score rewards request count, waiting urgency, and length compatibility. Exact local selection does not imply a globally optimal schedule.

A separate exhaustive solver enumerates all ordered feasible partitions for six simultaneous requests. It independently verifies the complete objective and supplies a global tiny-instance reference.
