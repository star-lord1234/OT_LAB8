# Assignment 8 Progress and Dependency Plan

Last updated: 2026-11-06

Current phase: **Tracks A-H implemented and verified; Tracks I-J remain to be implemented.**

## 1. Status legend

| Status | Meaning |
|---|---|
|   |
| PLANNED | Scope and acceptance criteria are defined; no implementation yet. |
| BLOCKED | Cannot be closed without an external input or prerequisite. |
| IN PROGRESS | Work has begun but acceptance criteria are not all met. |
| NOT STARTED | No work beyond the global plan. |

## 2. Overall status

| Area | Status | Evidence/next action |
|---|---|---|
| Authoritative PDF review | COMPLETE | All seven pages read and visually checked. |
| `bm.md` review | COMPLETE | All 244 lines audited against the PDF. |
| Requirement classification | COMPLETE | See `REQUIREMENTS.md` Sections 2-4. |
| Traceability plan | COMPLETE | Global, foundations, A-J, and syllabus matrices defined. |
| Repository architecture | COMPLETE | The Section 9 architecture is now scaffolded with explicit A-J evidence locations. |
| Repository infrastructure | COMPLETE | A-J paths, shared utilities, registry, CLIs, prompt records, and 22 passing infrastructure tests are present. |
| Exact Chapter 6 syllabus audit | BLOCKED | Obtain lecture notes/slides or official topic list and resolve `SYL-01` through `SYL-08`. |
| Environment/version capture | COMPLETE | Real machine/tool/package state and final 7/7 preflight are documented in `SETUP.md`. |
| Algorithm implementation | IN PROGRESS | Tracks A-H implemented; Tracks I-J remain. |
| Experiments/results/report | IN PROGRESS | A-H have results, plots, prompt history, and draft report sections; C and E are explicitly simulation-only and G is QEMU-only. |

## 3. Track status

| Track | Planned minimum | Status | Hard prerequisites | Completion gate |
|---|---|---|---|---|
| A | Tiny objectives/model; all named first-order optimizers, Newton, Gauss-Newton, backprop, curvature, tuning/noise | IMPLEMENTED / VERIFIED / syllabus-blocked | Exact Chapter 6 list | A-01 through A-06 have code, tests, raw results, figures, and report links. A-07/SYL-01 remains unresolved. |
| B | Knapsack exact/heuristic comparison; Max-Cut QUBO/Ising; separate constrained penalty QUBO | IMPLEMENTED / VERIFIED / syllabus-blocked | Exact Chapter 6 list | B-01 through B-05 have code, exhaustive tests, raw results, plots, report links, and a hashed C fixture. B-06 remains unresolved. |
| C | QAOA, VQE, PQC/QNN, parameter-shift, SPSA, QNG, shots/noise/plateau, embedding limits | IMPLEMENTED / VERIFIED SIMULATION / syllabus-blocked | Exact Chapter 6 list | C-01 through C-08 and C-10 have tests, results, plots, report links, and explicit simulator labels. C-09 remains unresolved. |
| D | Maximum coverage; scheduling/parallel forms; FedAvg; MGDA; GradNorm | IMPLEMENTED / VERIFIED / syllabus-blocked | Exact Chapter 6 list | D-01 through D-07 have code, spawn-safe tests, real results, plots, PIDs, and report links. D-08 remains unresolved. |
| E | Offline batching simulation; FCFS, greedy, local DP, exact tiny solver | IMPLEMENTED / VERIFIED SIMULATION | None | E-01 through E-05 have formulation, identical repeated workloads, tests, results, plots, strategy table, exact reference, and report links. |
| F | Toy compiler; folding/propagation, CSE, strength reduction, DCE; pass-order optimization | IMPLEMENTED / VERIFIED / FOUR-PASS TARGET | None | Five samples preserve outputs; B&B matches enumeration; instruction/runtime/size/compile metrics and report exist. |
| G | xv6 priority scheduler; CPU/sleep/mixed workloads | IMPLEMENTED / VERIFIED / ONE FEATURE | None | Pinned pristine/support/optimized commits; 3 full usertests passes; 18 benchmark runs/108 jobs; clean-patch boot; report and provenance. |
| H | SQLite storage-budgeted index selection using two methods plus default baseline | IMPLEMENTED / VERIFIED | None | 69,541 deterministic rows; 5 queries/indexes; baseline/greedy/MILP/DP; real plans/pages/timings; all hashes equal. |
| I | Every taught quantum algorithm; two hand-coded circuits; QML/classical comparison; advantage analysis | PLANNED / syllabus-blocked | C quantum utilities; D speedup results; Chapter 6 list | Exact taught list covered; expected circuit outputs; matched QML/classical data; D contrast. |
| J | Public Python codebase test prioritization/minimization | PLANNED | Select/pin licensed project; shared greedy/exact utilities | Baseline profile; formal budgeted objective; real tests/coverage; measured quality and maintenance risk. |

No track may be marked COMPLETE merely because its script runs. Its formulation, baseline, fair comparison, correctness evidence, results, prompt history, and report links must all pass.

## 4. Cross-track dependency map

| Producer | Consumer | Reused artifact | Boundary that prevents accidental double-counting |
|---|---|---|---|
| Global setup | A-J | Seeds, validation, timing, CSV schema, plotting, environment capture | Every track still needs domain-specific formulation, baseline, correctness, and results. |
| A | D | Tiny shared model, gradient utilities, optimizer/result plotting | D must independently demonstrate FedAvg, MGDA, GradNorm, and genuine parallelism. |
| B | C | Canonical Max-Cut QUBO/Ising fixture and brute-force optimum | C must implement quantum optimization and shots/noise/plateau evidence. |
| B | E/H/F/J | Greedy, DP/ILP, enumeration, feasibility helpers | Each consumer must formulate and test its own domain problem; copied charts do not count. |
| C | I | SDK setup, circuits, measurement, noise, parameter-shift utilities | I must add every taught algorithm, two hand-written circuits, QML/classical comparison, and advantage analysis. |
| D | I | Measured classical parallel speedup/overhead | I must explicitly contrast measured D results with quantum theory/simulator results. |
| E | J | Benchmark harness only, if useful | J must use a realistic codebase and a separate software-engineering objective. E results cannot substitute for J. |
| F/G/H/I | Report/demo | Compiler passes, xv6 patch/logs, DB plans, quantum circuits | Named artifacts must be linked directly from their report sections. |
| Chapter 6 syllabus | A-D/I and final coverage | Exact method list | These tracks cannot be declared complete while any taught method is unmapped. |
| Prompt logging/Git conventions | A-J | AI provenance | Must be active before the first substantive code commit; history cannot be reconstructed dishonestly later. |

## 5. Critical path

1. Obtain the exact Chapter 6 materials and resolve `SYL-01` through `SYL-08`.
2. Initialize Git and establish README AI-register, prompt-folder, commit-prefix, secret-redaction, and environment-capture conventions **before substantive code**.
3. Probe the Mac for Python, CPU/core count, QEMU, RISC-V toolchain, and compatible quantum SDK. Pin only versions that actually work.
4. Scaffold the lightweight architecture and shared evidence schema.
5. Establish high-risk environments early: xv6/QEMU and the quantum simulator.
6. Implement B before C; A before D; C and D before I; B helpers before H/F/E/J.
7. Run each experiment from a fixed config and retain raw results before preparing plots/report prose.
8. Close the global evidence, AI disclosure, demo, final-question, and clean-clone reproduction gates before publishing.

## 6. Cross-cutting work queue

| Priority | Work item | Status | Exit criterion |
|---|---|---|---|
| 0 | Acquire Chapter 6 syllabus | BLOCKED | Instructor material stored/referenced and every taught method mapped. |
| 1 | Initialize repository/provenance workflow | COMPLETE | Initial verified commit `648899c` is tagged `setup-v1`; prompt schema, README register, ignore rules, and tests are active. |
| 1 | Capture real environment | COMPLETE | Actual hardware/OS/tool versions recorded in `SETUP.md`; final preflight passes 7/7. |
| 1 | Choose one quantum stack | COMPLETE | PennyLane statevector and mixed-state noise circuits execute locally on CPU. |
| 1 | Verify xv6 toolchain | COMPLETE | QEMU/RISC-V tools pass preflight; pinned pristine, support baseline, and priority scheduler build/boot/full `usertests` pass; fresh patch boots. |
| 2 | Scaffold shared experiment contract | COMPLETE | Seeds, config, timing/memory, repeats, exports, plotting, verification, environment metadata, registry, and prompt validation have 22 passing tests. |
| 2 | Select Track J codebase | NOT STARTED | Public license, pinned commit, >1,000-line conservative target, passing tests, and usable coverage data. |
| 3 | Implement A and B | COMPLETE EXCEPT SYLLABUS AUDIT | A-01 through A-06 and B-01 through B-05 pass; A-07/B-06 await the syllabus. |
| 4 | Implement C and D | COMPLETE EXCEPT SYLLABUS AUDIT | C reuses B's hashed fixture; D has real process/distributed results; C-09/D-08 await the syllabus. |
| 5 | Implement F, G, H | COMPLETE | F four-pass compiler, G priority scheduler, and H SQLite physical-design study are verified. |
| 6 | Complete E, I, J | IN PROGRESS | E complete as a simulation-only case study; I and J remain. |
| 7 | Consolidate report/demo/evidence | NOT STARTED | Clean-clone run, coverage checker, report links, AI logs, Q1-Q10, and demo pass. |
| 8 | Publish | NOT STARTED | Public GitHub URL, secrets scan clean, final report and demo accessible. |

## 7. Risk and uncertainty register

| Risk | Impact | Mitigation | Current state |
|---|---|---|---|
| Missing exact syllabus | Mandatory methods may be omitted or unnecessary work added. | Treat as a release blocker; conservatively plan all named PDF methods. | OPEN/BLOCKED. |
| Quantum package compatibility on Apple Silicon | C/I delay or oversized environment. | Select one SDK after a tiny compatibility probe; use local statevector/noise simulation and tiny circuits. | OPEN. |
| xv6 baseline compatibility | Future upstream or toolchain versions may differ. | Pin `fa2ddcb7`; retain pristine/baseline/optimized transcripts and cleanly applicable patch. | RESOLVED FOR PINNED REVISION. |
| Scope density | Superficial or unverifiable tracks. | Keep toy instances, share infrastructure, require evidence gates, and defer only explicit full-credit extensions. | CONTROLLED. |
| Timing noise on a laptop | Weak speedup/latency claims. | Warm-up, repeat, report variability, minimize background load, and allow honest negative results. | OPEN. |
| AI provenance reconstructed after the fact | Academic-misconduct risk. | Start prompt and Git traceability before code; never fabricate failures or history. | CRITICAL/PREVENTIVE. |
| Cross-track reuse becomes double-counting | A track may lack an independent experiment. | Reuse infrastructure/fixtures only; retain separate formulation, run, correctness, and report evidence for each track. | CONTROLLED. |
| Max-Cut lacks constraints | Would miss the explicit penalty-term requirement. | Add a separate constrained QUBO with exhaustive penalty verification. | RESOLVED IN PLAN. |
| Full-credit extensions consume mandatory-track time | Other mandatory rows may remain incomplete. | Two compiler passes and one xv6 feature first; add extensions after global mandatory closure. | CONTROLLED. |

## 8. Planned reusable components

- One experiment result schema, seed manager, timer, environment capture, plotting style, and evidence validator for all tracks.
- One small ML model family for A and D, with quantum analogues sharing data splits where appropriate in C/I.
- One discrete solver interface for B, E, F, H, and J.
- One canonical Max-Cut/QUBO/Ising fixture from B for C.
- One quantum backend/measurement/noise layer for C and I.
- One report section template and one prompt-log template for A-J.
- One clean-run command per track and one repository-wide verification command.

Reuse does **not** mean reusing the same result as evidence for multiple tracks. Each track retains its own objective, baseline, comparison, correctness check, measured output, and report section.

## 9. Immediate next gate

No algorithm work should begin until the user authorizes implementation. The first implementation turn should: (1) incorporate the actual Chapter 6 syllabus if available, (2) initialize the repository and provenance scaffolding, and (3) probe the Mac environment without installing unnecessary infrastructure.
