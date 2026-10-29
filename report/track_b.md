# Track B — Discrete Optimization

Status: **implemented and experimentally verified, with any additional Chapter 6 discrete techniques still syllabus-dependent**.

## B.1 Selection model and protocol

Track B uses three deterministic 0/1 knapsack instances. Each item has a binary selection variable, and the objective maximizes total value subject to one capacity constraint. The complete formulation, solver recurrences, QUBO convention, spin conversion, and penalty derivation are in [MATHEMATICS.md](../tracks/B_discrete/MATHEMATICS.md). The actual arrays and exhaustive optima are in [knapsack_instances.json](../tracks/B_discrete/results/knapsack_instances.json).

Greedy, integer linear programming, branch-and-bound, and dynamic programming receive identical items, values, weights, and capacities. Each is timed three times. Exhaustive enumeration is a separate oracle, not a competing heuristic, and checks feasibility and optimality independently. Raw selections, objectives, weights, solver status, memory, runtimes, and verified gaps are retained in [knapsack_runs.csv](../tracks/B_discrete/results/knapsack_runs.csv).

## B.2 Solution quality and runtime

The density-greedy baseline was feasible on every instance but did not attain any verified optimum. Its gaps were 27.27% on the classic three-item counterexample (160 versus 220), 11.36% on the eight-item project selection (39 versus 44), and 1.20% on the fourteen-item allocation (82 versus 83). ILP, branch-and-bound, and dynamic programming matched exhaustive enumeration on all instances ([summary](../tracks/B_discrete/results/knapsack_summary.csv), [exhaustive references](../tracks/B_discrete/results/knapsack_references.csv)).

On these tiny instances, greedy took roughly 22–33 microseconds and the transparent branch-and-bound implementation roughly 41–100 microseconds. Dynamic programming took roughly 0.30–1.46 milliseconds, while HiGHS MILP startup/solve overhead was roughly 1.8–6.6 milliseconds. These measurements show small-instance overhead, not general asymptotic superiority. DP is pseudo-polynomial in capacity, branch-and-bound has exponential worst-case behavior, and ILP provides a flexible model for constraints beyond this one-capacity case. The [shared comparison plot](../tracks/B_discrete/results/plots/knapsack_comparison.png) presents quality and log-scale runtime together.

## B.3 Max-Cut QUBO and Ising reference

The separate weighted five-vertex Max-Cut graph has seven edges. With binary partition variables `x_i`, the cut contribution of edge `(i,j)` is `w_ij(x_i+x_j−2x_ix_j)`. The minimized symmetric QUBO is `x^TQx = −cut(x)`. Under `s_i=2x_i−1`, the Ising energy has offset `−sum(w)/2`, zero linear terms, and couplings `J_ij=w_ij/2`.

All 32 states were enumerated. For every state, QUBO energy and Ising energy equal the negative weighted cut with zero observed error ([state table](../tracks/B_discrete/results/maxcut_energies.csv), [coefficients](../tracks/B_discrete/results/qubo_ising_coefficients.json)). The verified maximum cut is 8.0 at bitstrings `00110`, `01100`, `10011`, and `11001`. The immutable-convention [Track C fixture](../tracks/B_discrete/results/maxcut_track_c_fixture.json) includes the graph, matrices, bit ordering, optimum, and SHA-256 digest `baf60a299f2a2be478511dd30f8de470621aee8103b1e16424912b1cab90a530`.

## B.4 Constraint penalties

Ordinary Max-Cut is unconstrained and therefore needs no penalty. To demonstrate the required construction honestly, a separate exactly-one selection minimizes `−[4,3,2]·x + A(sum(x)−1)²`. State-by-state checks prove that its QUBO coefficients reproduce the direct formula exactly. Penalties 0.5 and 2.0 leave infeasible ground states; at 5.0, the ground state `100` is feasible and has energy −4.0, below the best infeasible energy −2.0 ([penalty sweep](../tracks/B_discrete/results/penalty_sweep.csv), [plot](../tracks/B_discrete/results/plots/qubo_ising_penalty.png)).

## B.5 Verification, reproduction, and limitations

Run from the repository root:

```bash
./scripts/run_track.py B
.venv/bin/python -m pytest tracks/B_discrete/tests
```

Tests compare all exact knapsack methods with exhaustive enumeration, preserve a known greedy failure case, verify feasibility, check all 32 QUBO/Ising states, recompute the Track C fixture hash, and enumerate the constraint-penalty example. The [manifest](../tracks/B_discrete/results/manifest.json) lists the evidence and records environment/repeat metadata.

Requirement B-06 remains **UNRESOLVED** because the actual Chapter 6 classroom syllabus is unavailable. Feature selection or any other additional taught discrete application must be added if it appears in those materials. The named mandatory B-01 through B-05 requirements are implemented and verified.
