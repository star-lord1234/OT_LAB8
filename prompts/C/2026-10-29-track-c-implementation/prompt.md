# Original prompt

Implement Track C using the shared quantum simulation environment.

Reuse the exact Max-Cut/QUBO instance from Track B. Do not create a different benchmark just to make quantum results look better.

Implement:

- QAOA for the Track B Max-Cut problem
- VQE on a small suitable Hamiltonian
- Parameterized quantum circuits and a minimal QNN
- Parameter-shift gradient estimation
- SPSA
- Quantum natural gradient, using an appropriately small circuit
- Classical comparisons for each relevant optimization task

Investigate:

- Finite-shot measurement variance
- A realistic simulator noise model
- Optimization convergence
- Circuit depth and evaluation cost
- Barren plateau behavior across feasible circuit sizes

Use small circuits and controlled numerical experiments suitable for a 16 GB MacBook Air.

Provide correct quantum objective definitions, circuit diagrams where useful, training curves, measurement statistics, and repeated-run comparisons.

Explicitly distinguish simulated results from physical quantum hardware results.

Coordinate with Track I so that quantum algorithm implementations and infrastructure can be reused without omitting either track's requirements.

Create tests, results, plots, prompt logs, and a Track C report section. Verify QAOA output against the exact classical solution.

Do not claim quantum advantage solely because an algorithm is quantum.
