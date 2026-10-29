# Track C — Quantum Optimization

Status: **implemented and experimentally verified on local simulators; no physical quantum hardware was used**. Any additional hybrid method actually taught in Chapter 6 remains syllabus-dependent.

## C.1 QAOA against Track B's exact Max-Cut solution

Track C reads the unchanged, hash-verified [Track B fixture](../tracks/B_discrete/results/maxcut_track_c_fixture.json), whose exact maximum weighted cut is 8.0. The fixture digest remains `baf60a299f2a2be478511dd30f8de470621aee8103b1e16424912b1cab90a530`. Tests verify the QAOA cost Hamiltonian equals the negative cut on every one of its 32 computational basis states.

Across three fixed initializations, mean Adam expected cut increased from approximately 6.09 at depth 1 to 6.57 at depth 2 and 6.87 at depth 3. The best retained run was depth 3 with expected cut 7.2723, approximation ratio 0.9090, and 49.4% total probability on exact-optimal bitstrings. Its most likely bitstring, `00110`, is an exact Track B optimum. This verifies that QAOA can produce the optimum with substantial simulated probability; it does not mean the expected objective equals the optimum ([runs](../tracks/C_quantum_optimization/results/qaoa_runs.csv), [best run](../tracks/C_quantum_optimization/results/qaoa_best.json), [plot](../tracks/C_quantum_optimization/results/plots/qaoa_convergence_depth.png)).

SPSA was run at depth 1 for the same three seeds. It used 241 simulator objective calls per run and showed the same initialization sensitivity as Adam: final expected cuts ranged from 5.208 to 6.908. Adam's local statevector-backprop runs used 61 objective calls, but a gate-hardware parameter-shift estimate rises from 300 evaluations at depth 1 to 780 at depth 3. Gate count rose from 17 to 41 and circuit depth from 9 to 21. These accounting categories are not interchangeable.

The classical exhaustive solver already returns the exact optimum for this five-vertex case. QAOA is less accurate, requires parameter optimization, and is simulated classically here. Therefore these results provide **no evidence of quantum advantage**.

## C.2 VQE, QNG, and parameter-shift

The two-qubit Hamiltonian and ansatz are defined in [MATHEMATICS.md](../tracks/C_quantum_optimization/MATHEMATICS.md). Classical diagonalization gives ground energy −1.0369316877. After 70 steps, ordinary gradient descent had absolute errors between `1.0e-4` and `4.7e-4`; block-diagonal quantum natural gradient reached errors from zero to `2.2e-14` across the same three seeds ([VQE runs](../tracks/C_quantum_optimization/results/vqe_runs.csv), [classical reference](../tracks/C_quantum_optimization/results/vqe_classical_reference.json)). This tiny simulator result demonstrates the geometry-aware update, not a general runtime advantage: QNG also took longer because it constructs a metric tensor.

For `RY(theta)|0>`, manual parameter-shift agreed with `−sin(theta)` to `5.55e-17`; central finite differences differed by `4.23e-11` ([parameter_shift.json](../tracks/C_quantum_optimization/results/parameter_shift.json)).

## C.3 Parameterized circuit and QNN

The two-qubit QNN uses angle encoding, two entanglers, three trainable rotations, parameter-shift gradients, and Adam. All three runs reached 100% accuracy with final MSE approximately 0.026 on four points. The matched classical tanh-linear BFGS baseline also reached 100% accuracy, with MSE `1.70e-6` in about 0.0023 seconds versus roughly 0.85 seconds for each simulated QNN run ([QNN runs](../tracks/C_quantum_optimization/results/qnn_runs.csv), [classical baseline](../tracks/C_quantum_optimization/results/qnn_classical_reference.json), [training plot](../tracks/C_quantum_optimization/results/plots/vqe_qnn_training.png)). The classical model is clearly preferable for this toy task.

Text diagrams for QAOA, VQE, and the QNN are saved in [circuit_diagrams.txt](../tracks/C_quantum_optimization/results/circuit_diagrams.txt).

## C.4 Finite shots, noise, and plateau proxy

The best QAOA state's exact simulated expected cut was 7.2723. Across 12 repeated shot runs, mean absolute estimation error fell from 0.0988 at 100 shots to 0.0316 at 1,000 and 0.00954 at 10,000; estimator variance fell from 0.0147 to 0.00109 and 0.000126 ([shot summary](../tracks/C_quantum_optimization/results/finite_shots_summary.csv), [raw samples](../tracks/C_quantum_optimization/results/finite_shots.csv)).

Under the local depolarizing simulator, expected cut declined from 7.2723 without noise to 6.8040 at the reference noise scale and 6.4295 at twice that scale. Exact-optimum probability declined from 0.494 to 0.404 and 0.337 respectively ([noise results](../tracks/C_quantum_optimization/results/noise_simulation.csv), [shared plot](../tracks/C_quantum_optimization/results/plots/shots_noise.png)). This is a generic realistic-magnitude model, not calibration data from a named device.

For the finite-size plateau proxy, global-cost gradient variance fell from 0.285 at 2 qubits to `9.03e-4` at 10 qubits, while local-cost variance remained between roughly 0.29 and 0.46. This pattern is consistent with a global-cost barren-plateau warning over the tested sizes, but it is not proof of asymptotic exponential scaling ([raw proxy](../tracks/C_quantum_optimization/results/barren_plateau_proxy.csv), [plot](../tracks/C_quantum_optimization/results/plots/plateau_embedding.png)).

## C.5 Embedding limitation, reproduction, and scope

A toy logical triangle embedded in a four-node physical square demonstrates chain-strength sensitivity. At strength 0.25 all physical ground states break the logical chain; at 1.0, 25% do; at 3.0, none do ([embedding results](../tracks/C_quantum_optimization/results/embedding_chain_strength.csv)). This is exhaustive classical simulation of an annealing-embedding issue, not execution on an annealer.

Run:

```bash
./scripts/run_track.py C
.venv/bin/python -m pytest tracks/C_quantum_optimization/tests
```

The [manifest](../tracks/C_quantum_optimization/results/manifest.json) labels the entire track as local simulation. Shared quantum code is under `src/optlab/quantum/` for Track I reuse, but Track I must still produce its own required algorithm and comparison evidence. C-09 remains **UNRESOLVED** until the actual Chapter 6 syllabus confirms whether other hybrid quantum-classical methods were taught.
