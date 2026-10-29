# Assignment 8 — Optimize Anything: Minimum Viable Completion Blueprint

**Purpose:** Complete the entire 14-day Optimization Techniques lab assignment with the smallest *defensible, reproducible* experiments, rather than building ten large products.

**Non-negotiable:** Tracks **A–J are all compulsory**. Each needs (1) an optimization objective and constraints, (2) a baseline, (3) at least one meaningful comparison, (4) a correctness check, and (5) measured results. Every Chapter 6 technique actually taught must be mapped to a runnable demonstration. “Minimum” here means small problem sizes and reuse, **not omitting required methods**.

**Source:** *Assignment 8: Optimize Anything — The 14-Day Vibe-Coding Challenge*, especially Sections 5–9 (pp. 2–6). **Syllabus caveat:** The handout references methods “where covered” and “every other ... taught.” Before final submission, cross-check the exact Chapter 6 lecture material and extend the coverage matrix accordingly. Do not silently mark a technique complete based on theory alone.

## 0. One-repository strategy

Use **Python 3.11**, NumPy/SciPy, PyTorch, matplotlib/pandas, `scipy.optimize` and/or PuLP, SQLite, Qiskit or PennyLane, and optional `mpi4py`. Use **xv6-riscv + QEMU** as a separate submodule/fork with a reproducible patch. The compiler experiment can use Python to implement a toy-language optimizer rather than LLVM. Record actual versions in `requirements.txt` / environment files; never invent benchmarks.

```text
optimize-anything/
├── README.md
├── bm.md                      # this blueprint
├── requirements.txt
├── environment.md             # hardware, OS, dependency versions, seeds
├── coverage_matrix.csv        # chapter topic -> script -> figure -> verification
├── common/
│   ├── metrics.py             # time, quality, speedup, repeated runs
│   ├── seeds.py
│   └── plotting.py
├── tracks/
│   ├── A_continuous/
│   ├── B_discrete/
│   ├── C_quantum_optimization/
│   ├── D_submodular_parallel_distributed/
│   ├── E_case_study/
│   ├── F_compiler/
│   ├── G_xv6/
│   ├── H_dbms/
│   ├── I_quantum_algorithms_qml/
│   └── J_software_engineering/
├── prompts/
│   ├── A/  ... J/              # original prompt, response, revisions, screenshots
├── logs/
│   ├── ai_tools_register.csv
│   ├── failures.md           # >= 3 real AI-generated failures + fixes
│   └── tool_comparison.md    # >= 2 AI tools on identical task
├── results/                   # CSVs, figures, plans, benchmark outputs
├── tests/
└── report/
    └── report.md              # sections for A–J; export to PDF if desired
```

**Evidence contract for EVERY track:** `README.md` (what/why/run), executable source, at least one sanity test, `results.csv` with raw measures and seeds, one figure/table, a short discussion of limitations, and a corresponding `prompts/<track>/` history. Prefer 3–5 seeded runs for stochastic experiments where feasible; state when a run is too expensive.

## 1. Track-by-track minimum implementation

### A — Continuous optimization

**Smallest useful experiment:** Train a 2-feature logistic-regression model on a synthetic binary dataset, plus optimize two 2D toy functions: a strongly convex quadratic and a non-convex function with a saddle point/local minima (e.g. Rosenbrock plus `f(x,y)=x²−y²`, with the saddle analysis clearly separated because the latter is unbounded). Reuse the same initial conditions and evaluation budget for valid comparisons.

**Implement/run:**
- GD, SGD, mini-batch SGD, Momentum, NAG, AdaGrad, RMSProp, Adam.
- Newton and Gauss–Newton (on suitable small least-squares objectives; **Gauss–Newton need not be applied to logistic loss**).
- Backpropagation in a tiny PyTorch model; distinguish gradient computation from update rules.
- At least one verifiable curvature approximation: Hessian–vector product, diagonal Hessian or Fisher approximation; map other explicitly taught curvature variants (Fisher / low-rank) to miniature demos as needed.
- Plot convergence for convex/strongly convex and non-convex objectives; learning-rate sensitivity and gradient noise. Illustrate parameter/loss/regularization, continuous vs discrete, local/global minima, saddle point; basic quantum ideas can link forward to C/I.

**Minimum outputs:** optimizer convergence curves, final loss + runtime table, curvature/backprop gradient sanity check (compare to finite differences), seed/config record, a plot or numerical check of a saddle point.

**Do not shortcut:** An Adam-only comparison is insufficient; the handout names all these methods.

### B — Discrete optimization

**Smallest useful experiment:** A single **0/1 knapsack** instance with 12–18 items; compare greedy value/weight heuristic, exact ILP (PuLP), custom branch-and-bound, and dynamic programming (if covered). Check solutions exhaustively for a tiny 8-item variant.

**Shared with C:** Create a separate 4–6-vertex weighted **Max-Cut** problem. Build its QUBO and Ising representations, show binary-to-spin conversion (`s=2x−1` or consistent convention), identify and explain any penalty terms for an additional constrained example (standard Max-Cut does not need constraints/penalties), and solve via brute force as Track C's classical reference.

**Minimum outputs:** knapsack objective/runtime comparisons; QUBO/Ising energy matching enumerated Max-Cut scores; explicit variable domains, constraints, feasibility tests; short justification of exact vs heuristic trade-offs.

### C — Quantum optimization

**Smallest useful experiment:** Use a **local simulator**, no paid quantum account needed. Reuse B's tiny Max-Cut QUBO. Make a 4-qubit QAOA circuit (`p=1` initially), optimize parameters, compare best/expected cut value with classical brute force; use small VQE Hamiltonian and 1–2 qubit PQC/QNN toy task.

**Also demonstrate explicitly:** parameter-shift gradients vs finite differences, SPSA vs an ordinary classical parameter optimizer, and quantum natural gradient on a very small variational circuit. Compare exact statevector results with finite-shot results (e.g. 100/1,000/10,000 shots), noisy simulation and increasing circuit size / depth for a **barren-plateau proxy** (measure gradient magnitude or variance with repeated random initializations; do not claim proof of exponential scaling from a few qubits).

**Minimum outputs:** circuit drawings, QAOA-vs-classical objective table, VQE energy convergence, gradient-method comparisons, shots/noise/barren-plateau plots. Identify every result as *simulation*, not quantum hardware.

**Reuse:** Track I may reuse circuit infrastructure and measurement/noise utilities but must supply the additional algorithms and classical-QML comparisons required there.

### D — Submodular, parallel and distributed optimization

**Four small experiments in one track:**
1. **Submodular:** Maximum coverage of 10–20 sets under cardinality `k`; run greedy and brute-force optimum for a tiny case; verify diminishing returns numerically and state which guarantee assumptions apply.
2. **Parallel:** CPU-bound independent tasks or a large array reduction with serial vs 2/4-process execution; report wall-clock, speedup `T1/Tp`, efficiency `T1/(pTp)`, overhead, Amdahl/Gustafson interpretation; include a work-stealing/dynamic-queue vs static-chunk comparison and a locality/synchronization/communication observation. Hardware constraints must be disclosed.
3. **Data/model/pipeline parallelism:** Use a deliberately tiny, traceable demonstration of each (e.g. partitioned batch gradients; a two-stage small network across processes; micro-batch pipeline scheduling), including overhead and limitations. It is okay if tiny workloads get slower, but a descriptive paragraph without an experiment does not satisfy the handout.
4. **Distributed/multi-task:** Simulate FedAvg on a partitioned small dataset versus centralized training across varying local steps and communication rounds. For a two-head, two-task shared model, implement equal task weights vs **MGDA** vs **GradNorm**; report each loss and overall trade-off.

**Minimum outputs:** coverage objective, speedup/efficiency curves, FedAvg metrics vs rounds, per-task loss curves, correctness checks against serial calculations.

### E — Main process case study (our chosen focus)

**Recommended project:** **Optimize CPU/LLM inference request batching under latency and memory constraints**. Keep it an offline **simulation** to avoid paid APIs or GPUs. Generate reproducible requests with arrival time, sequence/token length, deadline, and estimated memory footprint.

**Formulation:** decision variables = batch assignment / processing order; objective = minimize mean latency or weighted late requests plus compute cost; constraints = maximum batch size, memory/token budget, single-server availability, deadlines if treated as hard constraints. Specify an explicit service-time model (with fixed batching overhead + token-dependent cost), not unexplained invented timings.

**Compare at least two actual methods:** FIFO fixed batch baseline vs greedy shortest-job/earliest-deadline batching and an ILP on a small sample (or DP for a reduced formulation). Evaluate different arrival rates and memory budgets. Use a tiny brute-force case to validate solver outputs.

**Outputs:** formal model, assumptions, strategy-selection table (variable types, size, exact/heuristic, hardware, parallelism), latency/p95/throughput/deadline-miss metrics, quality-versus-runtime trade-offs. **Label simulated gains as simulated**, never as actual accelerator performance.

**Reason for choice:** Different enough from compiler/xv6/DBMS tracks, independent of internet/API costs, and reusable code for J if J operates on a *real* codebase with a distinct optimization decision.

### F — Compiler optimization

**Minimum-credit path:** Build a *small toy-language pipeline* that accepts arithmetic assignments and print statements: lexer, parser, simple intermediate representation (IR), interpreter or code generator. Implement **two optimization passes**: constant folding/propagation and dead-code elimination. **For full credit, implement four passes** by adding common subexpression elimination and strength reduction (only where algebraically sound).

**Required optimization formulation:** Select pass order over 2–4 passes to minimize instruction count/code size subject to a maximum compilation effort; solve by brute force or DP/greedy and explain why the selected method fits. Execute 5 representative programs both ways and verify identical results (including edge cases).

**Outputs:** before/after IR, correctness tests, instruction count, code size, runtime and compile-time measurements. Note interpreter overhead if it hides runtime differences.

### G — xv6 operating-system optimization

**Minimum-credit path:** Clone **xv6-riscv** and use **QEMU**. Implement **one simple kernel feature**, preferably a **priority-based scheduler** (with explicit default priorities and an aging/fairness note). Add lightweight user-space workload generators (CPU-bound, I/O/sleep-heavy, mixed). Benchmark **three workload types**, capture baseline *unmodified* xv6 before making changes, then rerun identically.

**Required correctness:** xv6 boots, standard `usertests` pass (as applicable to the fork), concurrent processes make progress, scheduling decisions match expectations. Save a `.patch` / `git diff`; measure turnaround/response time, throughput and fairness where valid.

**Full-credit extension:** a second independent feature such as scheduling-statistics syscall (check whether instructor counts this as a second optimization feature; do not assume a statistics-only syscall qualifies).

**Risk:** Kernel bugs are high-impact. Change one small file at a time and keep recoverable commits. If running xv6 on a Mac, use QEMU or a reproducible Linux VM; document architecture.

### H — DBMS optimization

**Minimum path:** SQLite on a synthetic `orders/customers/products` dataset (e.g. 10k–100k rows, fixed seed) with real analytical queries. Formulate **index selection**: binary variable per candidate index, maximize total measured workload benefit subject to a storage budget. Compare **greedy**, **knapsack DP / ILP**, and **SQLite's default configuration**; the two Chapter 6 methods must solve the *same* selection objective. SQLite's normal query planner remains enabled for actual query execution.

**Required:** use `EXPLAIN QUERY PLAN` (SQLite equivalent of EXPLAIN), report measured latency, throughput and index storage, plus before/after query outputs or checksums. Show that merely adding one index is not the experiment; the comparison is an optimization of *which indexes to create* under a budget.

**Minimum outputs:** workload generator, candidate index measurements, optimal/greedy selection results, plans, timing/size charts, result-equivalence tests.

### I — Quantum algorithms and QML advantage

**Minimum path:** Reuse the same simulator stack as C but make one very small circuit demonstration for **every quantum algorithm taught in the course**. The assignment examples include: **Deutsch–Jozsa, Bernstein–Vazirani, Grover, QFT, Quantum Phase Estimation, Shor, quantum annealing**, plus QML **variational classifier and quantum kernels**. Confirm the exact taught list; if Shor is required, use a toy factorization demonstration on a simulator and explain the restrictions. For annealing, use a software annealing simulator and state its distinction from physical hardware.

**Hand-code at least TWO circuits** (e.g. Deutsch–Jozsa and 2-qubit Grover) rather than invoking canned algorithm wrappers exclusively. Compare Grover query count to classical linear search, *and* compare simulator wall time to avoid claiming a false practical speedup.

**QML comparison:** Train a tiny variational quantum classifier or quantum-kernel SVM **and** a comparable classical logistic regression/RBF SVM on the same low-dimensional dataset; report held-out accuracy, training time, parameter count and number of circuit evaluations. Include a shot/noise model experiment or real-hardware measurement if access permits; contrast limitations with D's classical parallel speedups.

**Minimum outputs:** circuit correctness tests (expected bitstrings/probabilities), algorithm demonstration table with gate/query counts, QML-vs-classical metrics, honest limitations. **The method list here may need expansion after checking lecture slides.**

### J — Software-engineering optimization

**Minimum path:** Use a **real public codebase of >1,000 lines** (or another clearly non-trivial codebase) with a reproducible test suite. Recommended task: **test-case prioritization/minimization** under a total execution-time budget. Measure each test's execution time and covered statements or functions; choose tests using greedy coverage-per-second vs a naive original-order baseline (optionally ILP optimum on a small subset).

**Objective:** maximize unique coverage (or fault detection using a documented proxy) under time budget. **Correctness constraint:** selected tests must still run/pass; disclose any coverage reduction or lost checks. Use actual coverage instrumentation (`coverage.py` or `pytest-cov`) and a real project's test suite; do **not** fabricate a large codebase or use only a synthetic array benchmark.

**Outputs:** profile/bottleneck report, test-selection schedule, coverage-vs-time plot, test results, trade-off in readability/maintenance and coverage risk. If Track E batching simulator grows into a sufficiently large *realistic* codebase, J may use its test suite, but J must be a **separately formulated software-engineering optimization experiment**, not a reused E chart.

## 2. What is optional vs required

| Item | Minimum requirement | Extension / option |
|---|---|---|
| All ten tracks | **Required** | None may be skipped |
| Exact Chapter 6 syllabus coverage | **Required** | Extra non-taught algorithms optional |
| Compiler passes | **2 minimum** | **4 for full credit** |
| xv6 kernel features | **1 benchmarked over 3 workloads minimum** | **2 for full credit** |
| Quantum hardware | Simulator acceptable; include applicable noise-model experiment | Real-hardware experiments if available |
| DBMS | Existing SQLite/PostgreSQL/MySQL acceptable | Build own DBMS unnecessary |
| Main case-study domain | One chosen domain, at least 2 methods | Original research-level system unnecessary |
| Frontend, API, dashboard, deployment | **Not specified as required** | Optional |
| Dataset size | Small but meaningful, documented | Scale-up optional unless needed to test claims |
| Negative optimization results | Acceptable if correct and justified | Do not claim improvement without measurement |
| AI-generated implementation | **Compulsory in every track** | Choice of tools is flexible |
| AI tool comparison | **2 tools on one task** | More tools optional |
| Failure log | **At least 3 genuine cases** | Additional cases optional |

## 3. Shared work to minimize duplication

- **B → C:** Same weighted Max-Cut QUBO and brute-force optimal cut become the QAOA baseline.
- **C ↔ I:** Same quantum SDK, circuit simulator, shot/noise utilities, and gradient functions. C covers *optimization methods*; I adds *all taught algorithms*, QML/classical comparison and advantage analysis.
- **A → D:** Reuse simple PyTorch model and plotting; D adds genuine FedAvg/MGDA/GradNorm algorithms.
- **B → H:** Reuse knapsack DP/ILP/greedy frameworks for storage-constrained index selection, but execute and verify actual database queries.
- **B → F/J:** Reuse greedy/ILP or DP formulation logic; each track still needs domain-specific tests/benchmarks.
- **E ↔ J:** Reuse infrastructure only if J addresses a separate optimization decision on a substantial codebase.
- **All tracks:** Reuse time measurement, seed setting, configuration capture and CSV/figure generation.

## 4. Fourteen-day execution order

| Days | Work | Exit criterion |
|---|---|---|
| 1–2 | Repo scaffolding, syllabus checklist, tooling, Track E problem formulation and baseline, collect J codebase, establish xv6 baseline | Reproducible environments; E baseline; xv6 boots |
| 3–4 | A continuous + B discrete | All assigned optimizers have tests and output; QUBO baseline saved |
| 5–6 | C quantum optimization + I quantum algorithm small demos | QAOA matches B Hamiltonian; required circuits run; QML comparison underway |
| 7–8 | D parallel/submodular/distributed | Greedy, parallel, FedAvg, MGDA and GradNorm experiments run |
| 9 | F compiler | Two passes, before/after, semantics preserved, pass-selection optimization |
| 10 | G xv6 | Kernel feature, 3 workload benchmarks, patch and test evidence |
| 11 | H DBMS | Two methods vs default, actual query-plan/latency/storage proof |
| 12 | E full study + J codebase optimization | 2+ E methods, J formulation, results and correctness |
| 13 | Missing lecture algorithms, repeat runs, failure documentation, two-tool comparison | Chapter 6 matrix complete; all evidence files present |
| 14 | Report, prompt archive, README, verification and demo | Public repo + technical report + runnable demonstrations |

**Scheduling caution:** This is a very dense 14-day plan. Start the xv6 and quantum environments on Day 1, and complete quantum/I incrementally. If something breaks, downscale problem size instead of silently skipping a named compulsory technique.

## 5. Exactly what to record for every experiment

Use one standard results schema where applicable:

```csv
track,experiment,algorithm,seed,instance_size,hardware,objective,objective_unit,runtime_seconds,correct,notes
```

For every method, record:

1. **Objective & decision variables:** mathematical definition and why the method applies.
2. **Baseline:** unchanged process/classical or naive method, fixed dataset/input/hardware and configuration.
3. **Optimization:** exact algorithm, settings, number of iterations/queries/shots/processes, constraints.
4. **Correctness:** compare known optimum, reference implementation, test outputs or invariants; report pass/fail.
5. **Evidence:** numeric improvement or regression, runtime, compute/memory/communication cost as relevant; repeated runs for randomness.
6. **Caveat:** simulation versus measured hardware, overheads, failures and when the result won't generalize.

## 6. Mandatory AI-assisted development evidence

The PDF requires **strict vibe coding**, not just saying ChatGPT was used:

- `README.md` table of every AI tool and **model version actually used**, dates, tracks and purpose.
- `prompts/A/` through `prompts/J/`: original prompts, relevant generated responses, revised prompts, resulting commit links, verification notes and chat exports/screenshots; **redact secrets**.
- Distinguish AI-assisted commits, e.g. `[AI:ChatGPT]`, from manual edits; do not fabricate commit history.
- `logs/failures.md`: **three real** AI-generated mistakes with reproduction, fix, test and lesson learned. Do not deliberately invent failures for the report.
- `logs/tool_comparison.md`: compare **two AI tools** on exactly one same bounded task, logging correctness, hallucinations, elapsed time and prompt iterations.
- In viva: explain and modify your own code without an AI tool; unsupported code may receive no credit.

## 7. Completion checklist

- [ ] Confirm exact Chapter 6 lecture topics and mark all “where covered” techniques.
- [ ] A: all taught continuous optimizers, backprop, curvature, landscapes and comparisons.
- [ ] B: greedy, ILP, B&B, DP where covered, QUBO/Ising with penalties example.
- [ ] C: VQE, QAOA, PQC/QNN, parameter-shift, SPSA, quantum natural gradient, shots/noise/barren plateaus.
- [ ] D: submodularity, work-stealing/parallel forms, speedup/efficiency, FedAvg, MGDA, GradNorm.
- [ ] E: selected process, formal optimization, baseline, 2+ methods, results.
- [ ] F: compiler pipeline, >=2 passes, mathematical pass decision, identical outputs, timings.
- [ ] G: >=1 xv6 kernel change, >=3 workloads, QEMU tests, patch.
- [ ] H: >=2 Chapter 6 methods vs default DBMS optimizer; real plans, latency, storage and same query outputs.
- [ ] I: *all taught* quantum algorithms, 2 hand-built circuits, QML vs classical, query/gate and time comparisons.
- [ ] J: significant real codebase, named optimization method, profiling, test/correctness and trade-off analysis.
- [ ] Per-track prompts + tests + raw metrics + plots + report sections.
- [ ] AI register, >=3 real failures, 2-tool comparison, attributable commits.
- [ ] Public repository, detailed README, technical report and short demo.

## 8. Priorities if time runs short

**Never delete a compulsory track.** Instead: shrink to toy instances, run simulators rather than hardware, use established libraries while explaining and testing them, share algorithms across tracks, minimize UI work, and favor one clean experiment per required method over elaborate but unverified code. A bad or null optimization result is acceptable **if measured honestly and explained**.

**Grading caution:** The PDF explicitly reserves full-credit treatment for four compiler passes and a second xv6 feature. Also, its Chapter 6 list is exceptionally broad; this blueprint specifies *minimum-sized experiments*, not a promise that every experiment is trivial or that implementing only the headline algorithm for each track guarantees full marks.
