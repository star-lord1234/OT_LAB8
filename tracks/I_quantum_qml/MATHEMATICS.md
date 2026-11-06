# Track I Mathematics and Experimental Protocol

All quantum results are local PennyLane simulations. There is no claim of execution on a physical quantum processor or annealer.

## 1. Textbook algorithms

Deutsch-Jozsa evaluates a promised constant or balanced Boolean oracle once and classifies it from whether the input register returns `0...0`. Bernstein-Vazirani uses phase kickback to recover an `n`-bit hidden string with one oracle query.

For one marked item among `N=2^n` possibilities, Grover starts from the uniform state and alternates a phase oracle with inversion about the mean. The experiment uses

\[
k=\left\lfloor\frac{\pi}{4}\sqrt{N}\right\rfloor
\]

oracle calls. Its theoretical query complexity is `O(sqrt(N))`, versus `O(N)` worst-case classical linear search. The retained simulator wall time is not a hardware quantum runtime and is analyzed separately.

The QFT is assembled from Hadamards, controlled phase shifts, and swaps; the test checks both uniform output magnitudes and `QFT^-1 QFT |x> = |x>`. QPE applies controlled powers of `U=PhaseShift(2*pi*phi)` to an eigenstate and the hand-written inverse QFT. The chosen `phi=1/4` is exactly representable with three counting qubits.

The Shor experiment uses four counting and four work qubits for `N=15`, `a=2`. Controlled modular multiplications are exact permutation matrices. QPE exposes order `r=4`; classical continued fractions and

\[
\gcd(a^{r/2}-1,N),\quad \gcd(a^{r/2}+1,N)
\]

recover 3 and 5. This is valid order finding, but matrix compilation costs exponential space and is not scalable modular arithmetic.

## 2. Annealing label and objective

The annealing proxy uses the unchanged five-variable weighted Max-Cut QUBO from Track B. It applies classical Metropolis updates with a geometric temperature schedule and maximizes cut value. The exact exhaustive optimum 8.0 is the reference. This does **not** simulate quantum tunnelling or a hardware annealing schedule. Track C's chain-strength enumeration separately demonstrates a minor-embedding limitation.

## 3. Variational classifier / QNN

The fixed binary Iris subset uses petal length and width. One split digest is shared by every model. Standardization is fitted on training data only; clipped features become rotation angles. The two-qubit feature map applies `RY` encoding, entanglement, and a product-dependent `RZ`. Two trainable layers contain eight angles. The expectation `z=<Z_0>` is classified by its sign and trained with parameter-shift Adam on

\[
L(\theta)=\frac{1}{m}\sum_i(z_\theta(x_i)-(2y_i-1))^2.
\]

This parameterized circuit with expectation readout is both a QNN and a variational quantum classifier. Track C retains a separate minimal QNN demonstration.

## 4. Quantum kernel

For feature-map state `|phi(x)>`, the kernel is

\[
K(x,z)=|\langle\phi(x)|\phi(z)\rangle|^2.
\]

The full symmetric training Gram matrix and test-versus-train matrix are evaluated by circuits, then supplied to a classical SVC. The quantum feature map has zero trainable circuit parameters; classical support-vector coefficients still exist. Tests verify symmetry, unit diagonal, and positive semidefiniteness to numerical tolerance. The matched baseline is an RBF SVC on the identical encoded features.

## 5. Noise, plateaus, and fair claims

The Track I noise model uses exact density-matrix simulation with gate-local depolarizing probabilities: reference 0.1% after one-qubit gates and 1% on each endpoint after an entangler. These are plausible relative magnitudes, not calibration data for a named device. Track C supplies repeated finite-shot evidence.

The barren-plateau diagnostic estimates one parameter's gradient variance for global and local costs at 2-8 qubits. It is a finite-size warning, not proof of asymptotic exponential concentration.

Track D's wall-clock process speedup and Grover's oracle-query complexity answer different questions. Neither is converted into the other, and classical simulation of a quantum circuit is never presented as quantum speedup.
