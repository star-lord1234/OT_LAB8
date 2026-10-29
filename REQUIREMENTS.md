# Assignment 8 Requirements and Traceability Plan

Status: planning baseline; no algorithms have been implemented.

This document reconciles the authoritative Assignment 8 PDF with the proposed `bm.md` minimum-implementation blueprint. The PDF controls whenever the two differ. Page and section references below refer to the seven-page PDF.

## 1. Source authority and unresolved input

1. **Authoritative source:** `Assignment_8_Optimize_Anything_Vibe_Coding_Challenge.pdf`.
2. **Implementation proposal:** `bm.md`. It may narrow an experiment, but it cannot waive a PDF requirement.
3. **Still required from the student/instructor:** the exact Chapter 6 lecture notes, slides, or an official topic list. The PDF repeatedly requires every technique actually taught and uses phrases such as "where covered." Those requirements cannot be closed from the PDF alone.
4. **Conservative rule until the syllabus arrives:** implement every specifically named method in the PDF at a toy scale, while keeping a separate syllabus-dependent register for any additional taught methods.

## 2. Classification legend

| Code | Meaning | Treatment |
|---|---|---|
| M | Mandatory and unconditional | Must be implemented and evidenced. |
| MS | Mandatory if taught in the actual Chapter 6 syllabus | Blocked until the syllabus is checked; never silently omit. |
| MC | Mandatory when the stated condition applies | Record why the condition did or did not apply. |
| FC | Explicit full-credit extension | Not needed for the smallest defensible submission, but omission may cap marks. |
| O | Genuinely optional choice | May be omitted without violating the written PDF. |
| P | Process expectation rather than a standalone artifact | Follow and document where useful. |

## 3. Requirement classification summary

### 3.1 Mandatory

- Complete all Tracks A-J; each track needs an objective, baseline, fair comparison, correctness check, and measured results.
- Follow the seven-step workflow: discover, baseline, formulate, select, AI-assist, compare, and analyze trade-offs.
- Cover every specifically taught Chapter 6 technique with a valid implementation, library experiment, or other verifiable experimental demonstration. A theory-only mention is insufficient.
- Use strict, disclosed AI-assisted development for substantial implementation in every track.
- Maintain the AI register, per-track prompt histories, attributable commits, three genuine AI failure cases, and a two-tool comparison.
- Publish a public GitHub repository, technical report, tests, reproducible settings, results, plots/tables, coverage checklist, and short demonstration.
- Answer all ten final questions in the report or a linked appendix.

### 3.2 Conditional or syllabus-dependent

- Every additional continuous, curvature, combinatorial, hybrid quantum-classical, distributed, multi-task, quantum algorithm, and QML method actually taught in Chapter 6.
- Feature selection or other combinatorial applications included in the course.
- Real quantum hardware or a hardware noise model "where access allows." This project will use a local hardware noise model; real hardware remains conditional on free access.
- Repeated stochastic runs "where feasible." The default will be at least three seeds; any exception needs a cost justification.
- Reusing an F-J domain for Track E is allowed only if Track E goes substantially deeper. The proposed batching simulation avoids this condition.
- A non-listed Track J domain requires instructor approval. The proposed test-prioritization domain is already listed and needs no approval.

### 3.3 Full-credit extensions

- Track F: four compiler optimization passes. Two passes are the written minimum.
- Track G: a second kernel feature. One kernel feature benchmarked over at least three workloads is the written minimum.

For a smallest defensible implementation, plan two compiler passes and one xv6 feature first. Add the full-credit extensions only after every mandatory row in this matrix is closed.

### 3.4 Genuinely optional choices

- The Track E application domain, provided it satisfies the real-process workflow.
- The permitted compiler framework (toy compiler, LLVM, GCC plugin, or similar).
- The permitted DBMS (SQLite, PostgreSQL, MySQL, similar, or a student engine).
- The quantum SDK/simulator (Qiskit, PennyLane, Cirq, or similar).
- The specific xv6 feature, Track J task, datasets, and benchmark instances, within the stated constraints.
- Extra algorithms not taught in Chapter 6, a web UI, API, dashboard, Docker, cloud deployment, paid services, large datasets, and research-scale experiments.
- PDF export of the technical report unless the instructor separately specifies a format. The technical report itself is mandatory.

The 14-day schedule is the assignment duration and a process plan. The exact day-by-day ordering is suggested pacing, not a separate submission artifact.

## 4. Audit of `bm.md` against the PDF

| Audit ID | Blueprint finding | Authoritative interpretation and correction |
|---|---|---|
| BM-01 | Correctly keeps all ten tracks and their evidence contract. | Retain. The PDF expressly requires objective, baseline, fair comparison, correctness, and measured results for every track. |
| BM-02 | Correctly treats the exact classroom syllabus as unresolved. | Make this a release blocker, not a final-day reminder. Obtain the syllabus before declaring A-D or I complete. |
| BM-03 | The Max-Cut plan notes that unconstrained Max-Cut needs no penalty and suggests an unspecified constrained example. | The PDF explicitly asks for a QUBO/Ising model **with penalty terms**. Add one concrete constrained QUBO, such as exactly-one selection, and verify feasible/infeasible energies exhaustively. |
| BM-04 | Track A proposes at least one curvature approximation and defers other variants to the syllabus. | Potential underscope. HVP is explicitly named, and Fisher/diagonal/low-rank variants may all have been taught. Implement HVP plus one small Fisher/diagonal demonstration now; keep the remaining variants blocked on the syllabus. |
| BM-05 | Track C says "PQC/QNN toy task," which can be read as either/or. | The PDF names PQCs **and** QNNs. Use a QNN whose trainable model is a PQC, but produce separate evidence for circuit parameterization and QNN training so both are traceable. |
| BM-06 | Relevant hybrid quantum-classical methods are not enumerated beyond the named optimizers. | Add a syllabus-dependent row for every hybrid method taught; QAOA/VQE outer-loop optimization alone must not be assumed to exhaust the lecture list. |
| BM-07 | Annealing is discussed in Track I, but limits of embedding QUBO problems on annealing hardware are not a concrete output. | Add a documented toy embedding/chain-strength or connectivity analysis, or another verifiable demonstration supported by the selected SDK. Label it as simulated. |
| BM-08 | Track D records speedup, efficiency, overhead, load balancing, work stealing, locality, synchronization, and communication, but does not explicitly make makespan an output. | Add makespan to the static-versus-dynamic scheduling experiment and result schema. |
| BM-09 | Strategy selection is explicit for Track E only. | Track E's table is mandatory, but Section 5 also lists strategy selection as Chapter 6 coverage. Add a concise repository-wide method-selection matrix covering variable type, constraints, size, hardware, convergence, and communication cost. |
| BM-10 | Foundations may be handled as illustrations linked to later tracks. | Ensure each named foundation has a runnable/verifiable example. A prose link to C/I is not enough for a method that was explicitly taught. |
| BM-11 | `logs/ai_tools_register.csv` is proposed as the central register. | The PDF requires the AI-tools table **in README.md**. A CSV may be the source, but the rendered table must also be present in the README and kept consistent. |
| BM-12 | Per-track evidence asks for "at least one sanity test." | Strengthen this to edge cases, known examples, independent objective/constraint verification, and domain invariants as applicable. One smoke test alone does not meet Section 8. |
| BM-13 | The final checklist mentions a short demo but the architecture has no demo artifact. | Add `report/DEMO.md` with a reproducible 5-10 minute walkthrough, commands, expected outputs, and links to evidence. |
| BM-14 | The ten mandatory final questions are not mapped to report sections. | Add a dedicated report appendix answering Questions 1-10 with links back to the track evidence. |
| BM-15 | External libraries are listed as dependencies, but acknowledgements are not an explicit artifact. | Add an acknowledgements/dependency section recording external libraries, copied/adapted material, licenses, and AI-generated components. |
| BM-16 | Track I lists the PDF's example algorithms as its minimum. | Reasonable conservative plan, but the authoritative set is "every algorithm taught." Keep the listed set provisional until compared with lecture material; add anything missing. |
| BM-17 | Track I treats simulator plus noise as sufficient and real hardware as optional. | Correct only because the PDF says real hardware **or a hardware noise model where access allows**. Record the access decision and do not imply a real-device run. |
| BM-18 | Track F chooses two passes first and four for full credit; Track G chooses one feature first and two for full credit. | Correct. These are explicit minimum/full-credit distinctions in the PDF. |
| BM-19 | The recommended Python 3.11 stack and optional `mpi4py` are implementation choices. | Do not claim versions until measured on the Mac. Prefer the fewest packages; use `multiprocessing` before adding MPI unless the syllabus requires MPI. |
| BM-20 | Track J treats a public codebase over 1,000 lines as a hard minimum. | The PDF says "for example at least 1,000 lines or a public open-source project." Using a public project over 1,000 lines is a safe conservative choice, but 1,000 is illustrative rather than an absolute textual threshold. |

## 5. Global traceability matrix

All paths below are proposed. "Result" names the evidence that must exist before the row can be marked complete.

| ID | Class | Requirement | Planned implementation/artifact | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| G-01 | M | Complete Tracks A-J. | `tracks/A_*` through `tracks/J_*`. | `tools/verify_all.py` checks every track manifest. | Ten complete manifests and zero missing evidence links. | Executive summary; A-J. |
| G-02 | M | Every track states objective, baseline, fair comparison, correctness check, and metrics. | Standard `track.yaml` plus per-track README template. | Schema validation and link checks. | Completed evidence contract for every track. | Methodology; A-J. |
| G-03 | M | Discover process; define variables, objective, constraints, assumptions, and success metric. | Per-track formulation section; full treatment in E. | Hand-check formulas on tiny instances. | Formulation linked to executable inputs and metrics. | Methodology; E; relevant track. |
| G-04 | M | State dataset, assumptions, hardware, and evaluation conditions. | `environment.md`, configs, generated-data manifests. | Environment capture command and deterministic regeneration. | Machine/OS/package versions, seeds, and input hashes. | Experimental setup. |
| G-05 | M | Justify method; compare alternatives, costs, assumptions, and limitations. | Global method-selection matrix plus per-track rationale. | Review against variable types and constraints. | Selection/rejection rationale without unsupported guarantees. | Method selection. |
| G-06 | M | Fair baseline-versus-optimized experiments. | Shared benchmark harness and fixed configs. | Same data, budgets, stopping rules, and hardware; exceptions disclosed. | Raw objective, runtime, resource/quality measurements. | Experimental setup; A-J. |
| G-07 | M | Analyze trade-offs, overhead, scaling, and failure cases. | Standard discussion template. | Result assertions checked against raw data. | Positive, null, or negative result explained honestly. | Discussion; A-J. |
| G-08 | M/MS | Map every taught Chapter 6 method to experiment, code, and result. | `coverage_matrix.csv` generated/checked against this document. | Compare with official Chapter 6 materials. | No unaccounted taught method. | Chapter 6 coverage appendix. |
| G-09 | M | Small testable implementations with input validation, deterministic seeds, and explanatory comments. | Shared validation/seeding helpers and documented APIs. | Invalid-input tests and repeatability tests. | Deterministic outputs where applicable; clear failure messages. | Reproducibility. |
| G-10 | M | Edge cases, known examples, and independent verification of objectives/constraints. | Unit and property-style tests under `tests/`. | Reference, exhaustive, checksum, invariant, or finite-difference checks. | Correctness evidence per experiment. | Verification methodology; A-J. |
| G-11 | MC | Repeat stochastic runs where feasible and report variability, not only the best run. | Default three or more seeds in configs. | Aggregate mean/standard deviation and retain raw runs. | Variability table/plot or documented cost exception. | Experimental setup; results. |
| G-12 | M | No unsupported improvement, guarantee, quantum-speedup, or parallel-speedup claim. | Claim-evidence checklist. | Report review against raw results and assumptions. | Each claim labeled theoretical, simulated, or measured. | Limitations and validity. |
| G-13 | M | Public GitHub repo with README, setup, dependencies, and commands. | Root README and pinned environment files. | Clean-clone reproduction on macOS. | Public URL and successful documented setup. | Reproducibility appendix. |
| G-14 | M | Source and tests for all experiments; acknowledge libraries and AI components. | `src/`, `tests/`, README acknowledgements. | Inventory dependencies/licenses and generated components. | Complete acknowledgement table. | Acknowledgements. |
| G-15 | M | Tables/plots with units and reproducible settings. | Standard CSV schema and plotting helpers. | Figures regenerated from committed raw/summary data. | Labeled, non-misleading tables and plots. | Results; A-J. |
| G-16 | M | Technical report covers outcomes, failures, limitations, trade-offs, and next steps. | `report/report.md` and final export if required. | Report link/evidence checker. | Complete technical report. | Entire report. |
| G-17 | M | Short demonstration of problem, method, improvement evidence, and lessons. | `report/DEMO.md` and a single demo command. | Dry-run on clean environment. | Timed walkthrough with expected outputs. | Demo appendix. |
| G-18 | M | Report section for every track linked to code/results, including named artifacts. | A-J sections with stable repository links. | Link checker. | Compiler passes, xv6 patch, DB plans, QML and parallel comparisons linked. | A-J. |
| G-19 | M | Answer all ten final questions. | `report/report.md#final-questions`. | Checklist Q1-Q10. | Ten evidence-linked answers. | Final questions appendix. |
| AI-01 | M | Substantial implementation in every track is AI-prompt-driven and disclosed. | Prompt-first workflow before each material code change. | Compare prompt logs with Git history. | A-J all have matching prompts and commits. | AI-assisted development. |
| AI-02 | M | README register names every tool/model, tracks, dates, and work type. | README table, optionally generated from `logs/ai_tools_register.csv`. | Consistency check against prompt folders and commits. | Complete AI tool register in README. | AI disclosure. |
| AI-03 | M | Per-track prompt log contains original/revised prompts, response/excerpt, code-change link, verification note, and exports/screenshots. | `prompts/A/` through `prompts/J/`. | Folder schema and secret scan. | Complete ten-track prompt archive. | AI disclosure appendix. |
| AI-04 | M | Separate AI-assisted and manual commits. | `[AI:tool-name]` and `[MANUAL]` commit convention. | Git log audit. | Traceable repository history. | AI disclosure. |
| AI-05 | M | At least three genuine AI failures with fix and lesson. | `logs/failures.md`. | Reproduce failure and passing regression test. | Three real, non-fabricated cases. | Failures and lessons. |
| AI-06 | M | Compare at least two AI tools on the same task. | `logs/tool_comparison.md`. | Identical prompt/task; record correctness, hallucinations, time, iterations. | Side-by-side comparison with raw evidence. | AI tool comparison. |
| AI-07 | M | Remove secrets and private data before publishing. | `.gitignore`, redaction checklist, secret scan. | Repository scan before push. | No keys/tokens/private data. | Ethics/reproducibility. |
| AI-08 | M | Student can explain and modify code live. | `report/VIVA_NOTES.md` with concise explanations and modification drills. | Manual rehearsal without AI. | Explainability checklist. | Viva preparation; not claimed as grading proof. |

## 6. Chapter foundations and strategy traceability

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| FDN-01 | M | ML as optimization: parameters, loss, and regularization. | Tiny logistic model in A with regularized/unregularized objectives. | Analytical/finite-difference gradient checks. | Objective definitions and comparable runs. | Foundations; A. |
| FDN-02 | M | Continuous versus discrete optimization. | Contrast A's real-valued model with B's binary decisions. | Type/domain checks in both tiny examples. | Side-by-side formulation. | Foundations. |
| FDN-03 | M | Convex/non-convex landscapes; local/global minima and saddle points. | Small plotted/numerically evaluated functions in A. | Known stationary points and Hessian/eigenvalue checks. | Verified examples for every landscape concept. | Foundations; A. |
| FDN-04 | M | Basic quantum concepts and optimization in QML. | Minimal state/gate/measurement demo in I linked to variational optimization in C/I. | Expected-state/probability tests. | Runnable conceptual evidence, not prose only. | Foundations; C; I. |
| STR-01 | M | Select methods using variable type, constraints, size, hardware, convergence, and communication cost. | Global strategy matrix plus Track E table. | Each selected/rejected method has a reason. | Complete method-selection table. | Method selection; E. |

## 7. Track traceability matrices

### Track A - Continuous optimization

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| A-01 | M | Compare GD, SGD, mini-batch SGD, Momentum, NAG, AdaGrad, RMSProp, and Adam. | `tracks/A_continuous/implementation/optimizers.py`; shared regularized logistic objective. | `tracks/A_continuous/tests/test_optimizers.py`; equal data passes and three fixed seeds. | `method_runs.csv`, `method_summary.csv`, `optimizer_convergence.png`. | `report/track_a.md` A.1. |
| A-02 | M | Newton and Gauss-Newton. | Newton on logistic loss; Gauss-Newton on planted exponential least squares; provisional BFGS extension. | Newton/BFGS objective agreement and planted-parameter recovery tests. | `second_order_checks.json`, `second_order_convergence.png`, method tables. | `report/track_a.md` A.2. |
| A-03 | M | Backpropagation distinct from the optimizer. | `pytorch_demo.py`; 2-4-1 tanh XOR model with before/after parameter snapshots. | Autodiff gradient versus central finite differences; backward/step assertions. | `backprop.json`. | `report/track_a.md` A.2. |
| A-04 | M/MS | Curvature approximations: HVP and taught Fisher/diagonal/low-rank variants. | Exact Hessian/HVP plus diagonal, empirical Fisher, and rank-1 approximations in `curvature.py`. | Exact HVP versus finite-difference gradient HVP; approximation errors recorded rather than asserted zero. | `curvature.json`. | `report/track_a.md` A.2 and A.5. |
| A-05 | M | Convergence for convex, strongly convex, and non-convex cases; local minima/saddle behavior. | Rank-deficient/positive-definite quadratics and tilted double well in `objectives.py`. | Finite-difference derivatives; Hessian eigenvalues and stationary-root classification. | `landscapes.json`, `landscape_convergence.png`. | `report/track_a.md` A.3. |
| A-06 | M | Step-size/optimizer tuning and noisy objectives. | Fixed learning-rate grid and three seeded additive-gradient-noise runs. | Known `2/L=0.2` stability boundary and fixed budgets. | `sensitivity.json`, `noisy_objective.json`, two shared plots. | `report/track_a.md` A.3-A.4. |
| A-07 | MS | Any additional continuous/second-order technique taught. | BFGS added provisionally; exact classroom list unavailable. | **UNRESOLVED until the Chapter 6 syllabus is supplied.** | Visible blocker in manifest, coverage matrix, progress, and report. | `report/track_a.md` A.5; syllabus appendix. |

### Track B - Discrete optimization

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| B-01 | M | Selection/scheduling/allocation/combinatorial formulation. | Three fixed 0/1 knapsack instances in `models.py`; formal model in `MATHEMATICS.md`. | Exhaustive feasibility and optimum checks. | `knapsack_instances.json`, `knapsack_references.csv`. | `report/track_b.md` B.1. |
| B-02 | M | Greedy, ILP, Branch-and-Bound, and dynamic programming; exact versus heuristic comparison. | Four solvers in `implementation/solvers.py` receive identical instances/constraints. | Every exact result compared with independent enumeration; known greedy counterexample retained. | `knapsack_runs.csv`, `knapsack_summary.csv`, comparison plot. | `report/track_b.md` B.2. |
| B-03 | M | QUBO and Ising formulation with binary-to-spin conversion. | Five-vertex weighted Max-Cut in `implementation/maxcut.py`; full derivation in `MATHEMATICS.md`. | All 32 states prove QUBO = Ising = negative cut. | `maxcut_energies.csv`, `qubo_ising_coefficients.json`, plot. | `report/track_b.md` B.3. |
| B-04 | M | Explicit penalty terms for constraints. | Exactly-one three-choice QUBO with `A(sum(x)-1)^2`. | All eight states and three penalty strengths enumerated; direct/QUBO error zero. | `penalty_sweep.csv`, shared penalty plot. | `report/track_b.md` B.4. |
| B-05 | M | Classical QUBO solution becomes Track C baseline. | Versioned fixture containing graph, conventions, coefficients, optima, and digest. | Hash recomputation and exhaustive optimum test. | `maxcut_track_c_fixture.json`; optimum cut 8.0. | `report/track_b.md` B.3; C.1. |
| B-06 | MS | Feature selection or other combinatorial applications taught. | **UNRESOLVED until the Chapter 6 syllabus is supplied.** | Syllabus-specific reference test. | Visible blocker in manifest, coverage matrix, progress, and report. | `report/track_b.md` B.5; syllabus appendix. |

### Track C - Quantum optimization

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| C-01 | M | Solve B's QUBO with QAOA and compare with classical baseline. | Small local-simulator QAOA. | Hamiltonian/bit-order tests against B enumeration. | Approximation/expected cut, runtime, circuit evaluations. | C.1-C.2. |
| C-02 | M | Demonstrate VQE. | Tiny known Hamiltonian on local simulator. | Ground energy against exact eigensolver. | Energy convergence/error table. | C.2. |
| C-03 | M | Demonstrate parameterized circuits and a QNN. | Tiny PQC used as trainable QNN. | Shape/probability/gradient and tiny-label tests. | Separate PQC structure and QNN training evidence. | C.2-C.3. |
| C-04 | M | Parameter-shift. | Shared quantum gradient utility. | Compare against finite differences/statevector reference. | Gradient error table. | C.3. |
| C-05 | M | SPSA and quantum natural gradient; compare optimizers. | Optimize the same tiny circuit under matched budgets. | Seeded convergence and reference objective. | Quality/evaluation-count/runtime comparison. | C.3. |
| C-06 | M | Finite-shot measurement cost. | 100/1,000/10,000-shot runs. | Exact statevector reference and repeated seeds. | Error/variance versus shots. | C.4. |
| C-07 | M/MC | Hardware noise and clear simulation/hardware labeling. | Local hardware noise model; real hardware only if freely accessible. | Noisy versus noiseless reference. | Noise degradation plot labeled simulated. | C.4. |
| C-08 | M | Barren-plateau behavior as circuit size grows. | Gradient-variance proxy over small sizes/depths. | Repeated random initializations; avoid asymptotic proof claim. | Gradient magnitude/variance trend with caveat. | C.4. |
| C-09 | M/MS | Hybrid quantum-classical methods taught. | QAOA/VQE outer loops plus any additional syllabus method. | Method-specific reference test. | Complete syllabus mapping. | C; syllabus appendix. |
| C-10 | M | Limits of embedding QUBO on annealing hardware. | Tiny connectivity/minor-embedding or chain-strength simulation/analysis. | Verify logical versus embedded solution on toy graph if SDK permits. | Verifiable embedding limitation evidence. | C.5 or I.4. |

### Track D - Submodular, parallel, distributed, and multi-task optimization

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| D-01 | M | Diminishing returns, assumptions, greedy selection, and guarantee conditions. | Small maximum-coverage instance. | Numerical diminishing-return checks and brute-force optimum. | Greedy objective/gap and valid guarantee statement. | D.1. |
| D-02 | M | Load balancing, makespan, and work stealing/dynamic scheduling. | Static chunks versus dynamic task queue. | Same task set/output; repeated timings. | Makespan, imbalance, speedup, and overhead. | D.2. |
| D-03 | M | Locality, synchronization, and communication overhead. | Controlled variants within the scheduling/array experiment. | Output equivalence and component timings. | Quantified or directly measured overhead observations. | D.2. |
| D-04 | M | Speedup and efficiency on multiple cores/processes; Amdahl and Gustafson interpretation. | Serial, 2-process, and up-to-4-process runs subject to Mac core count. | Same work and correct aggregate. | `T1/Tp`, `T1/(pTp)`, overhead, law-based interpretation. | D.2. |
| D-05 | M | Data, model, and pipeline parallelism. | Tiny traceable demonstration of each. | Compare output/gradients with serial model. | Timing, correctness, and overhead for all three forms. | D.3. |
| D-06 | M | FedAvg versus centralized training with varied local steps and communication rounds. | Small partitioned dataset simulation. | Centralized reference, deterministic partitions. | Accuracy/loss/communication-round table. | D.4. |
| D-07 | M | MGDA and GradNorm versus equal weighting on a two-task model. | Shared two-head toy model. | Per-task gradient/loss checks. | Per-task losses and trade-off comparison. | D.5. |
| D-08 | MS | Other distributed/multi-task methods taught. | Minimal syllabus-specific demo. | Reference/invariant test. | Added coverage evidence. | D; syllabus appendix. |

### Track E - Main real-process case study

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| E-01 | M | Choose a real process and show evidence it needs optimization. | Offline CPU/LLM request-batching simulation with documented service model. | Validate generated arrivals/lengths/deadlines and baseline behavior. | Baseline latency, p95, throughput, misses, and cost. | E.1. |
| E-02 | M | Define variables, objective, constraints, assumptions, and success metric. | Batch/order decisions with size, token/memory, server, and deadline constraints. | Tiny exhaustive feasibility/objective check. | Complete mathematical formulation. | E.2. |
| E-03 | M | Strategy-selection table. | Compare exact/heuristic choices by type, size, hardware, and parallelism. | Rationale review against model. | Required short table. | E.3. |
| E-04 | M | Compare at least two methods. | FIFO fixed-batch baseline, greedy batching, and small-sample ILP/DP if feasible. | Identical workload; brute-force tiny reference. | Quality/runtime trade-off across arrival/memory settings. | E.4-E.5. |
| E-05 | M | Label simulation and avoid hardware-performance claims. | Explicit service-model and scope labels. | Claim audit. | Results consistently marked simulated. | E.5-E.6. |

### Track F - Compiler optimization

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| F-01 | M | Build mini-compiler pipeline or equivalent framework. | Toy lexer, parser, IR, and interpreter/code generator. | Parser/codegen tests and known programs. | Runnable unoptimized pipeline. | F.1. |
| F-02 | M | At least two optimizations. | Constant folding/propagation and dead-code elimination. | Before/after semantic equivalence on edge cases. | Optimized IR and preserved outputs. | F.2. |
| F-03 | FC | Four passes for full credit. | Add CSE and safe strength reduction after mandatory closure. | Algebraic safety and semantic regression tests. | Four verified passes. | F.2. |
| F-04 | M | Formulate a compiler decision and solve with a Chapter 6 method. | Pass ordering under compilation-effort budget. | Exhaustive tiny ordering reference. | Selected order, objective, and constraint evidence. | F.3. |
| F-05 | M | Measure instruction count, runtime, code size, and compile time. | Shared benchmark over representative programs. | Same outputs optimized/unoptimized. | All four metrics with units. | F.4. |

### Track G - xv6 operating-system optimization

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| Gx-01 | M | Modify at least one xv6 kernel feature and explain the OS concept/objective. | Priority scheduler on pinned `xv6-riscv`. | Build/boot and scheduler invariant tests. | Patch plus concept/objective explanation. | G.1-G.2. |
| Gx-02 | M | Benchmark one feature over at least three workloads. | CPU-bound, sleep/I/O-heavy, and mixed user workloads. | Same binaries/config before and after. | Turnaround/response/throughput/fairness metrics as valid. | G.3. |
| Gx-03 | M | Test after every change because kernel state may corrupt. | Record build/boot/usertest checkpoints in prompt/commit log. | Per-commit check evidence. | Recoverable, traceable kernel changes. | G.2; AI failures if applicable. |
| Gx-04 | M | xv6 boots and passes `usertests`; concurrent processes progress. | QEMU test script and workload assertions. | Baseline and modified runs. | Boot log, `usertests` status, no starvation evidence. | G.3-G.4. |
| Gx-05 | M | Submit patch/diff. | `tracks/G_xv6/patches/priority-scheduler.patch` against pinned commit. | Apply patch to clean clone and rerun checks. | Reproducible patch and base commit. | G appendix. |
| Gx-06 | FC | Second kernel feature for full credit. | Add only after all mandatory tracks close. A stats syscall alone is not assumed to qualify. | Independent benchmark/correctness check. | Second-feature evidence if attempted. | G.5. |

### Track H - DBMS optimization

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| H-01 | M | Optimize a real DBMS workload and formulate variables, objective, and storage/time constraint. | SQLite index selection under storage budget. | Recreate fixed-seed database and candidates. | Formal binary model and baseline workload. | H.1-H.2. |
| H-02 | M | Compare at least two Chapter 6 methods with the default optimizer; one added index is insufficient. | Greedy versus knapsack DP/ILP, plus no-selected-index/default SQLite baseline. | Same candidate benefits/budget/workload. | Selection objective/runtime and actual DB execution comparison. | H.3. |
| H-03 | M | Use accepted benchmark or documented synthetic data of stated size. | Small generated orders/customers/products dataset. | Row counts, constraints, deterministic hash. | Dataset manifest and generator. | H.1. |
| H-04 | M | Compare plans, latency, throughput, and storage cost. | `EXPLAIN QUERY PLAN`, repeated query timings, index file-size accounting. | Warm-up/cache policy documented. | All required DB metrics before/after. | H.4. |
| H-05 | M | Query results must be identical. | Stable sorted results/checksums. | Baseline versus every index set. | Equivalence tests pass. | H.4-H.5. |

### Track I - Quantum algorithms and QML advantage

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| I-01 | M/MS | Run every quantum algorithm taught. Provisional list: Deutsch-Jozsa, Bernstein-Vazirani, Grover, QFT, QPE, Shor, and quantum annealing. | One minimal local simulation per algorithm; extend after syllabus audit. | Expected bitstrings/probabilities/factors/energies. | Algorithm table with gates, queries, runtime, and labels. | I.1-I.2; syllabus appendix. |
| I-02 | M | Hand-write circuits for at least two algorithms. | Deutsch-Jozsa and small Grover circuit without canned algorithm wrappers. | State/probability and oracle checks. | Source links and circuit diagrams. | I.2. |
| I-03 | MC | At least one real-hardware or hardware-noise experiment where access allows. | Reuse local noise model; record that no paid/real access was used unless this changes. | Noisy/noiseless comparison. | Access decision and measured simulated result. | I.2; limitations. |
| I-04 | M/MS | Run taught QML methods, including variational classifier and quantum kernels if taught. | Tiny variational classifier and quantum-kernel model; add syllabus methods. | Train/test split, deterministic preprocessing, circuit-count instrumentation. | QML accuracy, time, parameters, evaluations. | I.3. |
| I-05 | M | Compare QML with equivalent classical model on same data. | Logistic/RBF baseline matched to low-dimensional data. | Same split/metrics. | Accuracy, time, parameter/circuit evaluation table. | I.3. |
| I-06 | M | Compare known quantum advantage with classical counterpart using query/gate counts and wall time. | Grover versus linear search at tiny sizes. | Correct target recovery; count queries/gates. | Theoretical-count comparison plus simulator timing caveat. | I.4. |
| I-07 | M | Explain when quantum helps/does not and contrast with Track D parallel speedups. | Cross-track analysis of noise, simulation, data loading, barren plateaus, and measured CPU speedup. | Claim audit against C/D/I results. | Honest advantage/limitation analysis. | I.5. |

### Track J - Software-engineering optimization

| ID | Class | Requirement | Planned implementation | Verification/test | Required result/evidence | Report section |
|---|---|---|---|---|---|---|
| J-01 | M | Use a realistic, non-trivial codebase in an allowed domain. | Pin a public Python project with a reproducible pytest suite; target over 1,000 lines as conservative evidence. | Record commit, line count, license, baseline test run. | Codebase provenance and baseline. | J.1. |
| J-02 | M | Profile baseline and identify bottleneck. | Measure per-test time and function/statement coverage. | Repeat baseline and validate coverage collection. | Profile identifying selection/prioritization opportunity. | J.2. |
| J-03 | M | Formulate variables, objective, constraints and use a named Chapter 6 method versus naive baseline. | Select tests to maximize unique coverage under time budget; greedy coverage/time versus original order. | Tiny exhaustive/ILP reference on subset. | Formal model and quality/runtime comparison. | J.3-J.4. |
| J-04 | M | Measure gain and costs in correctness, readability, or maintainability. | Coverage-versus-time curve and selected-suite execution. | Selected tests pass; quantify lost coverage/checks. | Measured trade-off and risk discussion. | J.4-J.5. |

## 8. Syllabus-dependent register - release blockers

These rows must remain `UNRESOLVED` until the actual Chapter 6 material is supplied and compared line by line.

| ID | PDF wording | Provisional coverage | Question requiring syllabus evidence |
|---|---|---|---|
| SYL-01 | Second-order or curvature-based methods "covered in the course." | Newton, Gauss-Newton, HVP, diagonal/Fisher demo. | Were quasi-Newton/BFGS, natural gradient, K-FAC, low-rank Hessians, or other methods taught? |
| SYL-02 | Fisher, diagonal or low-rank, Hessian-vector products. | HVP plus diagonal/Fisher planned. | Does "or" describe alternatives, or were multiple variants explicitly taught and therefore all required? |
| SYL-03 | Dynamic programming "where covered" and combinatorial applications included in the course. | Knapsack DP planned regardless. | Were feature selection, scheduling, portfolio, or other specific applications taught? |
| SYL-04 | Relevant hybrid quantum-classical methods covered. | QAOA/VQE/QNN outer-loop optimization. | Were additional named hybrid algorithms taught? |
| SYL-05 | "Every other quantum algorithm taught," with examples. | All seven algorithms listed in the PDF planned. | What is the exact lecture list, including any algorithms not listed in the PDF? |
| SYL-06 | Quantum machine-learning methods taught. | Variational classifier and quantum kernels planned. | Were additional encodings, QNN forms, or kernels taught? |
| SYL-07 | Other distributed or multi-task methods explicitly included, "such as MGDA and GradNorm where covered." | FedAvg, MGDA, and GradNorm planned because Track D explicitly names them. | Were FedProx, SCAFFOLD, PCGrad, CAGrad, or other methods taught? |
| SYL-08 | Exact final checklist must match the Chapter 6 syllabus. | `coverage_matrix.csv` planned. | Obtain instructor-approved Chapter 6 topic list before implementation is declared complete. |

## 9. Proposed lightweight repository architecture

```text
OTLab_8/
├── README.md
├── REQUIREMENTS.md
├── PROGRESS.md
├── pyproject.toml                 # one pinned Python environment
├── environment.md                # measured Mac/OS/tool versions and seeds
├── coverage_matrix.csv           # requirement -> code -> test -> result -> report
├── configs/                       # small TOML/JSON experiment configs
├── src/optlab/
│   ├── common/                    # timing, seeds, CSV schema, validation, plotting
│   ├── continuous/               # A; reused by D
│   ├── discrete/                 # B; reused by E/F/H/J
│   ├── quantum/                  # C; reused by I
│   ├── parallel/                 # D shared harness
│   └── models/                   # tiny shared ML models for A/D/C/I
├── tracks/
│   ├── A_continuous/             # thin runner, config, README
│   ├── B_discrete/
│   ├── C_quantum_optimization/
│   ├── D_parallel_distributed/
│   ├── E_case_study/
│   ├── F_compiler/               # domain-specific compiler code stays here
│   ├── G_xv6/                    # setup script, pinned base, patch, workloads, logs
│   ├── H_dbms/                   # schema, generator, queries, plans
│   ├── I_quantum_qml/
│   └── J_software_engineering/
├── tests/
│   ├── unit/                     # shared algorithm/reference tests
│   └── integration/              # per-track end-to-end smoke/evidence checks
├── data/
│   ├── fixtures/                 # tiny committed reference instances
│   └── generated/                # reproducible small datasets; no large downloads
├── results/
│   ├── raw/                      # machine-readable measurements
│   ├── summaries/                # aggregated CSV/JSON
│   ├── figures/                  # regenerated from summaries
│   └── logs/                     # plans, QEMU output, environment capture
├── prompts/{A,B,C,D,E,F,G,H,I,J}/
├── logs/
│   ├── ai_tools_register.csv
│   ├── failures.md
│   └── tool_comparison.md
├── report/
│   ├── report.md
│   ├── DEMO.md
│   └── VIVA_NOTES.md
└── tools/
    ├── run_track.py              # stable per-track entry point
    ├── verify_all.py             # evidence/coverage/link checks
    └── capture_environment.py
```

Architecture principles:

- Keep algorithm implementations in small reusable `src/optlab` modules; track directories contain domain adapters and experiment runners, not copied solver code.
- Use one quantum SDK, one plotting stack, SQLite from Python's standard library, and `multiprocessing` before considering MPI.
- Generate small synthetic data from fixed seeds. Commit tiny fixtures and summary results, not bulky databases or simulator caches.
- Keep xv6 external: clone a pinned upstream commit into an ignored work directory, apply a committed patch, and archive QEMU/test logs. This avoids vendoring a second repository.
- Use standard CSV/JSON/TOML files instead of a database, dashboard, web service, Docker, or workflow platform.
- Preserve raw measurements and derive every plot/table from them. Never hand-edit result summaries.

## 10. Minimum defensible scope decision

The initial completion target is: all mandatory rows, all provisional specifically named Chapter 6 methods, two compiler passes, one xv6 feature over three workloads, a local quantum simulator/noise model, small generated datasets, and no paid/cloud dependency. The four-pass compiler and second xv6 feature are deferred full-credit extensions. Nothing in this decision waives the unresolved syllabus rows.
