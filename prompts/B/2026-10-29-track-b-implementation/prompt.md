# Original prompt

Implement Track B using a small combinatorial optimization benchmark, preferably a selection or allocation problem that supports several competing solution methods.

Compare:

- Greedy
- Integer linear programming
- Branch-and-Bound
- Dynamic programming where taught and applicable

Use identical problem instances and constraints, and report solution quality, objective value, runtime, and optimality gap where known.

Also create a small Max-Cut benchmark for the QUBO/Ising requirement.

Derive and document:

1. Binary decision variables
2. Objective function
3. Constraint penalties where applicable
4. QUBO representation
5. Binary-to-spin transformation
6. Classical exact or brute-force solution

Save the Max-Cut instance and classical optimum as a reusable benchmark for Track C.

Include correctness tests against exhaustive enumeration for small instances. Do not claim a heuristic found the optimum without verification.

Produce results, plots, tests, mathematical documentation, AI prompt logs, and the Track B report section.

Run the complete Track B test suite before stopping.
