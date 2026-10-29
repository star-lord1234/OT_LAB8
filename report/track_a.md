# Track A — Continuous Optimization

Status: **implemented and experimentally verified, with the exact Chapter 6 syllabus still unresolved**.

## A.1 Objective, baselines, and protocol

The main comparison minimizes mean binary logistic loss with L2 regularization on a deterministic 160-row, two-feature synthetic classification set (plus a bias parameter):

\[
f(w)=\frac{1}{n}\sum_i\left[\log(1+e^{x_i^T w})-y_i x_i^T w\right]+\frac{\lambda}{2}\lVert w\rVert_2^2,
\qquad \lambda=0.1.
\]

Batch gradient descent is the baseline. SGD, mini-batch SGD, Momentum, Nesterov accelerated gradient, AdaGrad, RMSProp, and Adam use the same data, initialization, 60 data passes, and three fixed seeds. This matches data exposure, although it does not make Python update overhead identical: batch GD performs one update per pass, SGD performs 160, and the other stochastic methods perform ten. Every run records its exact hyperparameters, seed, stopping condition, runtime, memory measurements, convergence state, and final objective in [method_runs.csv](../tracks/A_continuous/results/method_runs.csv); means and standard deviations are in [method_summary.csv](../tracks/A_continuous/results/method_summary.csv).

The first-order mean final objectives were 0.391433 (batch GD), 0.391133 (SGD), 0.391126 (mini-batch), 0.391156 (Momentum), 0.391153 (Nesterov), 0.391127 (AdaGrad), 0.391148 (RMSProp), and 0.391192 (Adam). All reduced the initial objective. None met the deliberately strict gradient-norm tolerance within 60 passes, so the evidence labels them `budget_exhausted`, not converged. The [shared convergence plot](../tracks/A_continuous/results/plots/optimizer_convergence.png) reports means over all three runs rather than selecting a favorable seed.

## A.2 Gradients, backpropagation, and curvature

The analytical logistic gradient agrees with central finite differences to a maximum absolute error of `7.38e-11` ([gradient_check.json](../tracks/A_continuous/results/gradient_check.json)). In the separate 2–4–1 tanh PyTorch XOR model, the selected autodiff gradient agrees with finite differences within `1.23e-11`. The recorded before/after checks show that `loss.backward()` populated gradients without changing parameters, whereas `optimizer.step()` changed them. The model reached 100% accuracy and final loss 0.00435 on the four training cases ([backprop.json](../tracks/A_continuous/results/backprop.json)). This demonstrates that backpropagation computes derivatives; it is not itself the update rule.

Newton's method on the logistic objective reached 0.39112605 with gradient norm `3.3e-17`. BFGS, included as a provisional quasi-Newton extension, reached the same objective to displayed precision. Gauss–Newton was applied to the appropriate nonlinear least-squares model `a exp(bx)` and recovered the planted parameters `[1.5, -0.8]` within `2e-11` ([second_order_checks.json](../tracks/A_continuous/results/second_order_checks.json), [convergence plot](../tracks/A_continuous/results/plots/second_order_convergence.png)). These runtimes are illustrative laptop measurements on tiny problems, not claims that second-order methods are universally faster.

At the logistic origin, an explicit Hessian-vector product agrees with an independent finite-difference gradient product to relative error `4.90e-11`. The diagonal Hessian, empirical Fisher, and rank-1 Hessian approximations have probe-vector relative errors 0.194, 0.248, and 0.649 respectively. Their nonzero error is an experimental trade-off, not a failed check; only the exact HVP is expected to match ([curvature.json](../tracks/A_continuous/results/curvature.json)).

## A.3 Convexity, non-convexity, and sensitivity

Three analytic landscapes provide interpretable controls ([landscapes.json](../tracks/A_continuous/results/landscapes.json), [shared plot](../tracks/A_continuous/results/plots/landscape_convergence.png)):

- A rank-deficient quadratic has Hessian eigenvalues `[0, 2]`, so it is convex but not strongly convex.
- A quadratic with Hessian `diag(1, 10)` is strongly convex.
- The tilted double well `(x²−1)² + 0.2x + 0.5y²` has a global minimum near `(-1.024, 0)`, a higher local minimum near `(0.974, 0)`, and a saddle near `(0.0501, 0)`. Stationarity and classification are checked from gradient roots and Hessian eigenvalues.

For the strongly convex quadratic, the theoretical fixed-step stability condition is `learning_rate < 2/L = 0.2`. Rates 0.01, 0.08, and 0.18 remained stable, while 0.22 diverged beyond `1e12` ([sensitivity.json](../tracks/A_continuous/results/sensitivity.json), [plot](../tracks/A_continuous/results/plots/step_size_sensitivity.png)). Three seeded runs with additive Gaussian gradient noise show the expected nonzero oscillating error floor ([noisy_objective.json](../tracks/A_continuous/results/noisy_objective.json), [plot](../tracks/A_continuous/results/plots/noisy_objective.png)).

## A.4 Regularization and trade-offs

Increasing L2 regularization from 0 to 0.1 to 1.0 reduced the weight norm from 2.494 to 1.369 to 0.368 while training accuracy changed from 0.938 to 0.931 to 0.931 ([regularization.json](../tracks/A_continuous/results/regularization.json), [plot](../tracks/A_continuous/results/plots/regularization_effect.png)). The regularized objectives are not numerically comparable as unregularized data losses because their definitions differ; this experiment is about the parameter/fit trade-off.

## A.5 Reproduction, limitations, and syllabus blocker

Run from the repository root:

```bash
./scripts/run_track.py A
.venv/bin/python -m pytest tracks/A_continuous/tests
```

The configuration is [A.toml](../configs/tracks/A.toml), the runnable entry point is [run.py](../tracks/A_continuous/benchmarks/run.py), and the generated [manifest](../tracks/A_continuous/results/manifest.json) enumerates the evidence. The tests independently check analytical derivatives, objective curvature, every required first-order method, Newton/BFGS agreement, Gauss–Newton recovery, HVP accuracy, and backprop/update semantics.

The assignment also requires every curvature or continuous method actually taught in Chapter 6. Those classroom materials have not been provided. Newton, Gauss–Newton, BFGS, exact Hessian/HVP, diagonal Hessian, empirical Fisher, and rank-1 curvature are demonstrated, but methods such as natural gradient, K-FAC, L-BFGS, conjugate gradient, or others must not be claimed absent from the syllabus. Requirement A-07 and SYL-01 therefore remain **UNRESOLVED** until the actual syllabus is audited.
