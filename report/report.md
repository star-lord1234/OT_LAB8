# Assignment 8 Technical Report

Status: all Tracks A-J have linked experimental evidence. Global report/demo consolidation and exact Chapter 6 syllabus closure remain.

## Executive summary

Pending.

## Experimental setup and shared methodology

Pending. Link `SETUP.md`, environment metadata, seeds, repeated-run policy, measurement limitations, and claim labels.

## Chapter 6 coverage and method selection

Pending exact syllabus.

## Track A - Continuous optimization

Implemented and verified, subject to the unresolved Chapter 6 syllabus audit. See the full [Track A report section](track_a.md), raw [method table](../tracks/A_continuous/results/method_runs.csv), and generated [evidence manifest](../tracks/A_continuous/results/manifest.json).

## Track B - Discrete optimization

Implemented and verified, subject to the unresolved Chapter 6 syllabus audit. See the full [Track B report section](track_b.md), [knapsack summary](../tracks/B_discrete/results/knapsack_summary.csv), and reusable [Track C Max-Cut fixture](../tracks/B_discrete/results/maxcut_track_c_fixture.json).

## Track C - Quantum optimization

Implemented and verified on local simulators, subject to the unresolved Chapter 6 syllabus audit. See the full [Track C report section](track_c.md), [QAOA result](../tracks/C_quantum_optimization/results/qaoa_best.json), and simulation-only [evidence manifest](../tracks/C_quantum_optimization/results/manifest.json).

## Track D - Submodular, parallel, and distributed optimization

Implemented and verified with real local spawned processes, subject to the unresolved Chapter 6 syllabus audit. See the full [Track D report section](track_d.md), [parallel summary](../tracks/D_parallel_distributed/results/parallel_summary.csv), and [evidence manifest](../tracks/D_parallel_distributed/results/manifest.json).

## Track E - Main case study

Implemented and verified as a synthetic discrete-event simulation. See the full [Track E report section](track_e.md), [summary](../tracks/E_case_study/results/summary.csv), [mathematical formulation](../tracks/E_case_study/MATHEMATICS.md), and [evidence manifest](../tracks/E_case_study/results/manifest.json). No actual LLM inference performance is claimed.

## Track F - Compiler optimization

Implemented and verified with the four-pass target. See the full [Track F report section](track_f.md), [language and optimization model](../tracks/F_compiler/LANGUAGE_AND_OPTIMIZATION.md), [benchmark summary](../tracks/F_compiler/results/benchmark_summary.csv), and [evidence manifest](../tracks/F_compiler/results/manifest.json).

## Track G - xv6 optimization

Implemented and verified as one priority-scheduler feature with aging. See the
full [Track G report section](track_g.md), complete
[patch](../tracks/G_xv6/patches/priority-scheduler.patch),
[benchmark comparison](../tracks/G_xv6/results/scheduler_comparison.csv), and
[full usertests status](../tracks/G_xv6/results/usertests_status.json). Results
come from RISC-V QEMU simulation, not physical hardware or the macOS scheduler.

## Track H - DBMS optimization

Implemented and verified as storage-budgeted optional-index selection around
SQLite's unchanged optimizer. See the full [Track H report section](track_h.md),
[formal model](../tracks/H_dbms/MATHEMATICS.md), actual
[query plans](../tracks/H_dbms/results/query_plans.json), and
[workload summary](../tracks/H_dbms/results/workload_summary.csv).

## Track I - Quantum algorithms and QML

Implemented and verified on local CPU simulators, subject to the unresolved exact Chapter 6 classroom list. See the full [Track I report section](track_i.md), generated [coverage checklist](../tracks/I_quantum_qml/results/coverage_checklist.csv), [QML comparison](../tracks/I_quantum_qml/results/qml_comparison.csv), and simulation-only [evidence manifest](../tracks/I_quantum_qml/results/manifest.json). No physical quantum or annealing hardware result is claimed.

## Track J - Software-engineering optimization

Implemented and verified on the pinned MIT `more-itertools` project. See the full [Track J report section](track_j.md), [source provenance](../tracks/J_software_engineering/results/source_provenance.json), [selection summary](../tracks/J_software_engineering/results/selection_summary.csv), and [evidence manifest](../tracks/J_software_engineering/results/manifest.json). Selected tests are explicitly a fast-feedback subset, not full regression testing.

## Failures, limitations, trade-offs, and next steps

Pending.

## AI-assisted development and disclosure

Pending. Link README register, prompt records, genuine failure log, and real two-tool comparison when completed.

## Final questions

1. What process was chosen, and what evidence showed it needed optimization? Pending.
2. How were the objective function and constraints formulated? Pending.
3. Which Chapter 6 methods were tested and why were they appropriate? Pending.
4. How did optimized solutions compare with baselines? Pending.
5. What trade-offs, failures, or limitations were discovered? Pending.
6. What evidence demonstrates correctness and reproducibility? Pending.
7. How would the approach adapt to changed scale, data, constraints, or hardware? Pending.
8. What compiler, xv6, and DBMS optimization was implemented and how was correctness preserved? Pending.
9. What advantages and limits did QML, quantum algorithms, and parallel computing reveal? Pending.
10. Which AI tools were used, how did outputs differ, and which AI-generated errors were fixed? Pending.

## Acknowledgements and external components

Track G uses MIT xv6-riscv at its recorded pinned commit. Track J measures the MIT-licensed `more-itertools` project at commit `f42daddf205f335fea6e200dad46049f33e71221` without modifying or redistributing its checkout; full license and source metadata are recorded in `tracks/J_software_engineering/SOURCE.md`. Python dependencies and AI assistance are disclosed in `pyproject.toml`, `README.md`, and `prompts/`.
