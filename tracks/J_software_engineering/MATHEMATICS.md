# Track J Test-Selection Model

## 1. Candidate units and measured inputs

Each candidate `i` is one pytest test class from the pinned external project. Its measured cost `t_i > 0` is the sum of pytest setup, call, and teardown durations for its contained tests during the baseline coverage-context run. Its coverage set `C_i` contains repository-relative executable source-line identifiers attributed to those tests by coverage.py.

The complete suite is profiled before selection. It contains 771 tests across 167 test classes and executes all 2,233 coverage.py statements. To keep the optimization small and reproducible, 24 candidate classes are taken at equal intervals across the original class collection order. Their union contains 271 attributed executable lines. This candidate universe is not the whole regression suite.

## 2. Binary maximum-coverage formulation

For binary variable `x_i`, where `x_i=1` selects candidate class `i`, and binary `y_l`, where `y_l=1` indicates source line `l` is covered:

\[
\max \sum_{l\in U} y_l
\]

subject to

\[
\sum_i t_i x_i \le B,
\qquad
y_l \le \sum_{i:l\in C_i}x_i,
\qquad
x_i,y_l\in\{0,1\}.
\]

The fixed main budget `B=0.0445009792` seconds is 10% of the 24 candidates' measured test duration. The budget excludes pytest process startup because it is common to every selected suite; actual end-to-end wall time is measured separately.

## 3. Compared strategies

- **Original order:** scan candidates in their real collection order and select each candidate that still fits.
- **Greedy maximum coverage:** repeatedly choose the feasible candidate with greatest marginal uncovered lines per measured second. Deterministic ties prefer greater marginal coverage, lower cost, then earlier original order.
- **Exact enumeration:** inspect every subset of the first 14 measured candidates under a separately scaled 10% budget. Maximize union size; ties prefer lower cost and then original order.

Retained `candidate_coverage.json` permits independent recomputation of every set union. Selected suites are executed three times without instrumentation, and once again with coverage contexts to verify predicted line sets.

## 4. Scope and reliability

Line coverage is a test-selection proxy, not fault-detection probability. Two tests covering the same line may assert different behavior, and an uncovered line may be irrelevant to a change while a covered line may still contain an untested path. The optimization has no mutation-testing or historical-failure data and cannot prove defect detection.

The selected suites are appropriate only for a fast feedback stage. Full regression remains the release gate. A source change, test change, Python version change, or material timing change invalidates the profile and requires rerunning the experiment.
