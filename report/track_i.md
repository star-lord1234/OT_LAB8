# Track I — Quantum Algorithms and QML Advantage

Status: **the assignment PDF's named scope is implemented and verified on local CPU simulators; exact classroom-syllabus certification remains blocked.** No physical quantum or annealing hardware was used.

## I.1 Source audit and coverage

The authoritative PDF's named list and all Track I acceptance criteria are mapped in the generated [coverage checklist](../tracks/I_quantum_qml/results/coverage_checklist.csv); the audit rationale is in [COVERAGE.md](../tracks/I_quantum_qml/COVERAGE.md). The named list is Deutsch-Jozsa, Bernstein-Vazirani, Grover, QFT, QPE, Shor, and quantum annealing. QAOA, VQE, QNN/PQC, parameter-shift, SPSA, QNG, finite shots, noise, barren plateaus, and annealer embedding limits reuse tested Track C implementations and results.

Four circuits exceed the “at least two” construction requirement: Deutsch-Jozsa, Bernstein-Vazirani, Grover's oracle/diffuser, and QFT are assembled directly from primitive gates in `src/optlab/quantum/algorithms.py`. Text diagrams are retained in [circuit_diagrams.txt](../tracks/I_quantum_qml/results/circuit_diagrams.txt).

No supplied file could be identified as the actual Chapter 6 classroom material. The nearby syllabi were for cybersecurity, introductory data science, and motorsports. Therefore any additional taught algorithm or QML method remains explicitly `blocked-awaiting-syllabus`; it was not silently omitted or guessed.

## I.2 Algorithm demonstrations

The [algorithm table](../tracks/I_quantum_qml/results/algorithm_results.csv) records instance, expected and observed outputs, success probability, oracle queries, gate count, depth, and measured simulator time. Both DJ instances classified correctly; BV recovered secret `101`; one-iteration Grover recovered `10`; the three-qubit QFT round-trip returned `101`; and QPE returned phase 0.25. Each had simulated success probability effectively 1.

The eight-qubit Shor order-finding circuit for `N=15`, base 2, found order 4 from the nontrivial quarter-phase peaks and recovered factors 3 and 5 ([full result](../tracks/I_quantum_qml/results/shor_order_finding.json)). Its reported useful-phase probability is 0.5. Controlled modular multiplication is represented by exact 16-by-16 permutation matrices, so this is a valid tiny order-finding circuit but **not** a scalable implementation of modular arithmetic.

Three classical annealing-proxy runs on Track B's unchanged Max-Cut QUBO all reached the exhaustive optimum 8.0 ([runs](../tracks/I_quantum_qml/results/annealing_runs.csv)). This is classical simulated annealing over a quantum-compatible objective—not quantum annealing. It does not model tunnelling, hardware topology, calibration, or a physical annealing schedule. Track C's chain-strength experiment remains the separate embedding-limit demonstration.

## I.3 Matched QML and classical models

The [retained split](../tracks/I_quantum_qml/results/dataset_split.csv) contains 30 training and 10 test points from a fixed two-class Iris subset using petal length and width. Every row in the [comparison](../tracks/I_quantum_qml/results/qml_comparison.csv) carries the same split digest `14175b0f8ef973f44340103a4ed832f19dd7bfed66898671123e51405c0cfddb`.

Across three seeds, all four models scored 1.00 test accuracy. That tie is important: the quantum models provided no accuracy advantage.

- The eight-parameter VQC/QNN took a median 6.81 seconds and 13,510 tracked circuit executions for 25 parameter-shift steps.
- Three-parameter logistic regression took a median 0.000728 seconds and no circuits.
- The fixed, zero-trainable-circuit-parameter quantum fidelity kernel took a median 0.262 seconds and 765 circuit executions. Its SVC used four classical support vectors.
- The RBF SVC took a median 0.000227 seconds; its reported six fitted coefficients/intercept values are not directly equivalent to circuit angles.

The VQC convergence traces and all predictions are retained in [qml_training.csv](../tracks/I_quantum_qml/results/qml_training.csv) and [qml_predictions.csv](../tracks/I_quantum_qml/results/qml_predictions.csv). Tests independently verify that the quantum Gram matrix is symmetric, has unit diagonal, and is positive semidefinite. The [comparison plot](../tracks/I_quantum_qml/results/plots/qml_classical_comparison.png) makes the accuracy tie and simulation-cost difference visible.

## I.4 Grover query complexity versus measured runtime

For `N=4,8,16`, Grover used 1, 2, and 3 oracle queries, while worst-case linear search used 4, 8, and 16. The corresponding simulated success probabilities were 1.000, 0.945, and 0.961 ([query results](../tracks/I_quantum_qml/results/grover_query_comparison.csv)). These counts illustrate the `O(sqrt(N))` versus `O(N)` theoretical query relationship.

The wall-time result points in the opposite practical direction at this scale: Grover statevector simulation took approximately 0.00041-0.00153 seconds, while the tiny Python search took roughly `5.5e-8`-`1.5e-7` seconds per search. The simulator was about four orders of magnitude slower. This is not a contradiction: query complexity ignores state preparation, gates, error correction, readout, and the fact that the “quantum” experiment itself ran on a classical CPU.

## I.5 Noise, barren plateaus, data loading, and Track D

The gate-local density-matrix model reduced two-qubit Grover success from 1.000 without noise to 0.960 at the reference 0.1%/1% one-/two-qubit rates and 0.815 at five times those rates ([noise results](../tracks/I_quantum_qml/results/noise_model.csv)). This is a phenomenological hardware-noise model, not named-device calibration. No real-device credentials were supplied, and the project constraints avoid paid services; the PDF permits a hardware-noise model where access allows.

The global-cost gradient-variance proxy fell from 0.288 at two qubits to 0.00691 at eight, while local-cost variance fell more mildly from 0.462 to 0.253 ([plateau results](../tracks/I_quantum_qml/results/barren_plateau_proxy.csv)). This supports a finite-size trainability warning but cannot establish asymptotic barren-plateau scaling. Track C's repeated shot study separately shows measurement error/variance falling as shots increase.

Data encoding consumed one circuit per quantum-kernel pair and was part of the 765 evaluations; loading arbitrary larger classical data can erase an algorithmic benefit. The tiny models are also classically simulable, so their results do not extrapolate to advantage at useful scale.

Track D's best measured local process result was only 1.0645x median speedup at 26.6% parallel efficiency, and negative speedups occurred for other configurations ([cross-track record](../tracks/I_quantum_qml/results/cross_track_comparison.json)). That is a measured wall-clock result with communication/spawn overhead. Grover's result is instead a theoretical oracle-query advantage. Neither experiment demonstrates physical quantum advantage.

## I.6 Reproduction and remaining blocker

Run:

```bash
./scripts/run_track.py I
MPLCONFIGDIR="$PWD/.cache/matplotlib" XDG_CACHE_HOME="$PWD/.cache/xdg" \
  .venv/bin/python -m pytest tracks/I_quantum_qml/tests
```

The [manifest](../tracks/I_quantum_qml/results/manifest.json) labels all results as local simulation and links reused Track C evidence. The only Track I completion blocker is external: obtain the actual Chapter 6 materials and compare them line by line with the final `blocked-awaiting-syllabus` coverage row.
