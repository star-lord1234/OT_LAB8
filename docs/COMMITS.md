# Commit Traceability

## Initial infrastructure commit

- Commit: `648899cfc0b8a3064d78f39986a722d95d5f562f`
- Message: `[AI:Codex] Scaffold reproducible experiment infrastructure`
- Scope: requirements/setup documents, locked environment, A-J repository structure, shared infrastructure, tests, registry, and honest AI provenance records.
- Stable local annotated tag: `setup-v1`.
- Resolve locally: `git rev-parse setup-v1^{commit}`.
- Public GitHub commit URL: pending repository publication.
- Verification before commit: preflight 7/7; repository validation passed; pytest 22/22.

This hash was recorded in a follow-up documentation commit because a commit cannot contain its own final hash.

## Track D implementation commit

- Commit: `fc1465de94ef784f3cc5d9d6903cdecc1ad1b057`
- Message: `[AI:Codex] Implement Track D parallel and distributed optimization`
- Scope: maximum coverage, real CPU process scheduling, work-stealing simulation, controlled overheads, three parallel forms, FedAvg, MGDA/GradNorm, tests, results, plots, report, and honest prompt/failure records.
- Verification before commit: preflight 7/7; repository validation passed; focused Track D 10/10; repository-wide 62/62.

The implementation hash is linked by a follow-up documentation commit because a commit cannot contain its own final hash.

## Track H implementation commit

- Commit: `277e907ea89c0e441668ad3c06599e3dae286741`
- Message: `[AI:Codex] Implement Track H SQLite index selection`
- Scope: deterministic four-table synthetic database, five weighted queries and candidate indexes, measured page costs, 180-page binary model, baseline/greedy/MILP/DP comparison, actual SQLite plans, repeated timings, result hashes, plots, tests, report, and honest prompt/failure records.
- Verification before commit: standalone generator reproduced the exact digest; focused Track H 8/8; preflight 7/7; repository validation passed; repository-wide 97/97; every query/configuration/repeat hash matched baseline.

The implementation hash is linked by a follow-up documentation commit because a commit cannot contain its own final hash.

## Track G implementation commit

- Commit: `ec147bb2b58ca6ff7035a9758e76e780bdc937c9`
- Message: `[AI:Codex] Implement Track G xv6 priority scheduler`
- Scope: pinned official xv6-riscv, pristine/support/optimized checkpoints, one priority scheduler with aging, three identical workloads, 18 QEMU runs, 108 job records, clean patches, full usertests transcripts, tests, plot, report, and honest prompt/failure records.
- Verification before commit: pristine, support-baseline, and optimized full `usertests` passed; fresh patch applied/built/booted; preflight 7/7; repository validation passed; focused Track G 11/11; repository-wide 89/89.

The implementation hash is linked by a follow-up documentation commit because a commit cannot contain its own final hash.

## Track F implementation commit

- Commit: `0298aff857eb7c7e8e5400eb52ce1cd45fa91d2e`
- Message: `[AI:Codex] Implement Track F toy compiler optimization`
- Scope: lexer, parser, SSA-like IR, interpreter, five samples, four passes, branch-and-bound pass ordering, exact reference, four required metrics, tests, plots, report, and prompt/failure records.
- Verification before commit: preflight 7/7; repository validation passed; focused Track F 9/9; repository-wide 78/78; all five programs semantically equivalent.

The implementation hash is linked by a follow-up documentation commit because a commit cannot contain its own final hash.

## Track E implementation commit

- Commit: `b028ce709e19276c6660daf7260f1322fb821d84`
- Message: `[AI:Codex] Implement Track E inference batching case study`
- Scope: synthetic workloads, FCFS/greedy/DP scheduling, capacity and latency constraints, exact tiny reference, repeated results, strategy matrices, plots, tests, report, and honest prompt/failure records.
- Verification before commit: preflight 7/7; repository validation passed; focused Track E 7/7; repository-wide 69/69; 108/108 schedules verified.

The implementation hash is linked by a follow-up documentation commit because a commit cannot contain its own final hash.
