# Track B Mathematical Formulation

## 1. Binary selection benchmark

For item `i`, let the binary decision variable be

\[
x_i = \begin{cases}1 & \text{item i is selected}\\0 & \text{otherwise.}\end{cases}
\]

Given integer value `v_i`, integer weight `w_i`, and capacity `C`, every solver receives the same 0/1 knapsack model:

\[
\max_{x\in\{0,1\}^n} \sum_i v_i x_i
\quad\text{subject to}\quad
\sum_i w_i x_i \le C.
\]

Greedy sorts by decreasing `v_i/w_i` and takes any item that still fits. It is a feasible heuristic, not an exact algorithm. The classic three-item instance proves the distinction: greedy obtains 160 while exhaustive enumeration verifies the optimum is 220.

The ILP submits the displayed binary model to SciPy's HiGHS MILP solver. Dynamic programming uses

\[
D[i,c]=\max(D[i-1,c],\;D[i-1,c-w_i]+v_i)
\]

when `w_i <= c`, with complexity `O(nC)` for integer capacity. Branch-and-bound orders items by value density and uses the fractional-knapsack relaxation as an admissible upper bound. Exhaustive enumeration evaluates all `2^n` bitstrings independently and supplies the reported optimum and gap:

\[
\text{gap}(x)=100\frac{f^*-f(x)}{f^*}\%.
\]

## 2. Weighted Max-Cut QUBO

For vertex `i`, `x_i in {0,1}` gives its partition. For weighted edge `(i,j)`, the edge crosses the cut exactly when the bits differ:

\[
x_i\oplus x_j=x_i+x_j-2x_i x_j.
\]

The weighted cut is

\[
C(x)=\sum_{(i,j)\in E}w_{ij}(x_i+x_j-2x_i x_j).
\]

Maximizing `C` is equivalent to minimizing `E_Q(x)=-C(x)=x^TQx`. This repository uses a symmetric matrix whose off-diagonal contribution is counted twice. Therefore

\[
Q_{ii}=-\sum_{j:(i,j)\in E}w_{ij},\qquad
Q_{ij}=Q_{ji}=w_{ij}\quad((i,j)\in E).
\]

There is no constraint penalty in ordinary Max-Cut: every binary partition is feasible.

## 3. Binary-to-spin transformation

Use `s_i=2x_i-1`, hence `x_i=(s_i+1)/2` and

\[
x_i\oplus x_j=\frac{1-s_i s_j}{2}.
\]

The same minimization energy becomes

\[
E_I(s)=-\frac{1}{2}\sum_{(i,j)}w_{ij}
+\frac{1}{2}\sum_{(i,j)}w_{ij}s_i s_j.
\]

Thus the Ising offset is `-sum(w)/2`, every linear field `h_i` is zero, and `J_ij=w_ij/2`. All 32 states of the five-vertex fixture are enumerated to verify

\[
x^TQx=E_I(2x-1)=-C(x)
\]

with zero observed numerical error. The verified classical optimum cut is 8.0, with four complementary/symmetric optimal bitstrings.

## 4. Explicit constraint penalty

Because unconstrained Max-Cut has no penalty, a separate three-choice exactly-one model demonstrates penalty construction. With values `v=(4,3,2)`, minimize

\[
E(x)=-v^Tx+A\left(\sum_i x_i-1\right)^2.
\]

Using `x_i^2=x_i`, its symmetric-QUBO coefficients are

\[
Q_{ii}=-v_i-A,\qquad Q_{ij}=Q_{ji}=A,\qquad \text{offset}=A.
\]

Exhaustive results show `A=0.5` and `A=2` permit infeasible ground states, whereas `A=5` makes `x=100` the feasible ground state. This demonstrates why a penalty must dominate the objective benefit of violating the constraint rather than being chosen arbitrarily.

## 5. Reusable Track C fixture

[`results/maxcut_track_c_fixture.json`](results/maxcut_track_c_fixture.json) records the graph, bit order, QUBO convention and matrix, Ising coefficients, all classical optima, enumeration count, and a SHA-256 digest over every other fixture field. Track C must preserve these conventions when comparing QAOA with the classical reference.
