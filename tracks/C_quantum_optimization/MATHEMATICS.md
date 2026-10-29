# Track C Quantum Objectives and Simulation Protocol

All results in this track come from PennyLane's local `default.qubit` or `default.mixed` simulator. No physical quantum processor, cloud service, or paid quantum account was used.

## 1. QAOA using the unchanged Track B problem

Track C loads and verifies the SHA-256 digest of Track B's five-vertex weighted Max-Cut fixture. It does not regenerate or modify the graph. With Track B's spin convention `s_i=2x_i-1`, the minimized cost Hamiltonian is

\[
H_C=-\frac{1}{2}\sum_{(i,j)}w_{ij}I
+\frac{1}{2}\sum_{(i,j)}w_{ij}Z_iZ_j,
\]

whose computational-basis eigenvalue is exactly the negative cut value. The QAOA state at depth `p` is

\[
|\gamma,\beta\rangle=\prod_{k=1}^{p}e^{-i\beta_k\sum_iX_i}e^{-i\gamma_kH_C}|+\rangle^{\otimes 5}.
\]

The implementation realizes each weighted cost term as `MultiRZ(gamma*w)` and each mixer term as `RX(2*beta)`. It minimizes `E=<H_C>`; reported expected cut is `-E`. The classical reference is Track B's exhaustive optimum 8.0. A uniformly random partition has expected cut 5.0.

Adam uses simulator backpropagation to reduce local runtime. The report also records the parameter-shift circuit-evaluation count that the same parameter count would imply on gate-based hardware. SPSA estimates a stochastic gradient with two perturbed objective evaluations per update. These evaluation models are kept separate.

## 2. Parameter-shift

For a single-parameter Pauli rotation and expectation `f(theta)`, the exact parameter-shift rule is

\[
\frac{\partial f}{\partial\theta}=\frac{f(\theta+\pi/2)-f(\theta-\pi/2)}{2}.
\]

The one-qubit check uses `f(theta)=<Z>_{RY(theta)|0>}=cos(theta)` and compares parameter-shift with the analytic derivative `-sin(theta)` and central finite differences. The QNN is also trained with PennyLane's parameter-shift differentiation.

## 3. VQE and quantum natural gradient

The two-qubit VQE minimizes

\[
H=0.5Z_0+0.7Z_1+0.3X_0X_1+0.2Z_0Z_1
\]

using four `RY` parameters and one CNOT. Exact diagonalization of the 4-by-4 Hamiltonian provides the classical ground-energy reference. Ordinary gradient descent is compared with quantum natural gradient (QNG). QNG preconditions the gradient by the regularized block-diagonal Fubini–Study metric:

\[
\theta_{t+1}=\theta_t-\eta\,(G(\theta_t)+\lambda I)^{-1}\nabla E(\theta_t).
\]

The experiment is intentionally small enough that metric construction and exact diagonalization are both verifiable.

## 4. Parameterized circuit and QNN

The QNN angle-encodes two real features with `RY` gates, applies two CNOTs and three trainable `RY` rotations, and returns `<Z_0>`. It minimizes mean squared error on four labeled points using parameter-shift gradients and Adam. A classical `tanh(w^Tx+b)` model optimized with BFGS uses the same inputs, labels, MSE, and accuracy calculation.

## 5. Shots, noise, depth, and scaling proxy

Finite-shot estimates sample the best retained QAOA state 12 times each at 100, 1,000, and 10,000 shots and compare the sample-mean cut with the exact statevector expectation.

The noise experiment is a **simulation**, not a hardware run. The reference scale applies 0.1% one-qubit depolarizing probability after single-qubit gates and 1% local depolarizing probability to each endpoint after an entangling gate. Scales 0, 0.5, 1, and 2 expose degradation without claiming to model a particular commercial device.

QAOA depths 1–3 record gate count, circuit depth, simulator objective calls, and a parameter-shift hardware-evaluation estimate. The barren-plateau experiment is explicitly a finite-size proxy: for 2, 4, 6, 8, and 10 qubits, 32 random two-layer circuits estimate the variance of one parameter's gradient for a global parity cost and a local `Z_0` cost. It illustrates vanishing global gradients over these sizes but does not prove asymptotic exponential scaling.

## 6. Toy embedding limitation

To demonstrate a QUBO embedding limitation without annealing hardware, logical `K3` is embedded in a four-node physical square. One logical variable uses the chain `[q0,q1]`; the others use `q2` and `q3`. Exhaustive physical-spin enumeration shows that weak ferromagnetic chain strength 0.25 yields only broken-chain ground states, strength 1 produces mixed degeneracy, and strength 3 preserves the chain in every ground state. This is a simulator-only connectivity/chain-strength demonstration.

## 7. Track I reuse boundary

Reusable implementations live in `src/optlab/quantum/`:

- `maxcut.py`: fixture validation, QAOA, sampling, and noise evaluation;
- `variational.py`: parameter-shift, VQE/QNG, and the small QNN;
- `diagnostics.py`: plateau proxy and embedding demonstration.

Track I may reuse these circuits and utilities, but Track C's results cannot substitute for Track I's required algorithm inventory, hand-built circuit checks, QML/classical comparisons, and quantum-advantage analysis.
