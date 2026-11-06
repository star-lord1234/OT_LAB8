# Genuine AI-Assisted Failure Log

These are real cross-track setup/infrastructure failures observed on 2026-10-29. They are not manufactured examples. Future track failures should be appended with their prompt record, reproduction, regression test, fix, commit, and lesson.

## F-001 - Matplotlib cache path was not sandbox-safe

- **AI-generated artifact:** initial `scripts/preflight.sh`.
- **Failure:** PennyLane/matplotlib tried to create `/Users/biancasawant/.matplotlib`, which was not writable in the managed environment. The first preflight did not stream useful progress.
- **Evidence:** the captured warning stated that matplotlib created a temporary cache because the default path was not permitted.
- **Fix:** create ignored project cache directories and set `MPLCONFIGDIR`, `XDG_CACHE_HOME`, and `PYTHONUNBUFFERED=1` in the wrapper.
- **Verification:** the final preflight executes quantum checks without the permission warning and passes 7/7.
- **Lesson:** make cache locations explicit in reproducible/sandboxed workflows; an import check alone is insufficient.

## F-002 - Concurrent retries corrupted the same preflight log

- **AI action:** a retry started while the first long-running verifier was still active because its session identifier was not retained in the displayed output.
- **Failure:** two processes wrote `setup_logs/preflight-before-native.txt`, interleaving lines.
- **Evidence:** the corrupted file contained duplicated sections and a split ILP line. Its replacement carries an explicit reconstruction note.
- **Fix:** `scripts/preflight.sh` now acquires an atomic per-log lock directory and refuses a second writer.
- **Regression test:** `tests/infrastructure/test_cli.py::test_preflight_lock_prevents_interleaved_log`.
- **Lesson:** diagnostic tooling also needs concurrency protection and provenance; do not silently present repaired logs as originals.

## F-003 - Homebrew install command allowed automatic cleanup

- **AI-generated command:** the first native-tool install set `HOMEBREW_NO_AUTO_UPDATE=1` but omitted `HOMEBREW_NO_INSTALL_CLEANUP=1`.
- **Failure/safety impact:** Homebrew automatically removed an old `ca-certificates` Cellar version, cached bottles, logs, and temporary staging files after installation. No project data was removed, but the side effect exceeded the intended install-only scope.
- **Evidence:** the Homebrew output explicitly reported its automatic cleanup and every removed path category; `SETUP.md` preserves the event.
- **Fix:** all documented future Homebrew install commands include both no-auto-update and no-install-cleanup flags.
- **Verification:** `SETUP.md` documents the exact safe command and the observed side effect; no later cleanup command was issued.
- **Lesson:** package managers may perform implicit cleanup. Disable it proactively when the user requires approval for destructive actions.

## F-004 - Direct CLI commands used the wrong Python interpreter

- **AI-generated artifact:** Python CLI scripts with `#!/usr/bin/env python3` while dependencies were isolated in `.venv`.
- **Failure:** the README's direct command `./scripts/run_track.py A --plan` selected Homebrew Python 3.14 and failed with `ModuleNotFoundError: numpy`. The first infrastructure run reported 2 failed and 20 passed tests.
- **Fix:** added `scripts/_bootstrap.py`; every project CLI now re-executes with the unresolved `.venv/bin/python` path before importing project modules. The first attempted fix incorrectly resolved the symlink and still bypassed venv activation; the final guard compares `sys.prefix` instead.
- **Regression tests:** `tests/infrastructure/test_cli.py::test_track_plan_command` and `test_unimplemented_track_refuses_to_claim_run`.
- **Lesson:** executable Python scripts must not rely on the shell's generic `python3` when the project promises an isolated environment.

## F-005 - Scaffold-state tests became stale after Track A implementation

- **AI-generated artifact:** initial infrastructure tests hard-coded that every track, including A, must remain `scaffolded` and refuse execution.
- **Failure:** after Track A was correctly registered as implemented, the full run reported 3 failed and 28 passed tests even though the focused Track A suite passed 9/9.
- **Fix:** assert that A is implemented with its registered entry point, while using still-scaffolded Track B to preserve the refusal-to-claim-an-unimplemented-run regression check.
- **Regression tests:** `tests/infrastructure/test_cli.py::test_track_plan_command`, `test_unimplemented_track_refuses_to_claim_run`, and `tests/infrastructure/test_registry_prompts.py::test_registry_defines_all_tracks_and_existing_locations`.
- **Lesson:** lifecycle tests should preserve the invariant (implemented tracks run; scaffolded tracks refuse) rather than hard-code that a specific track can never advance.

## F-006 - Track test modules collided during pytest collection

- **AI-generated artifact:** Track A and Track B each contained a file named `test_experiment.py`, while their `tests/` directories lacked package markers.
- **Failure:** the first combined A+B run stopped during collection with an `import file mismatch`; pytest imported the B file using the already-loaded top-level module name from A.
- **Fix:** added `__init__.py` to both track test directories so their fully qualified module names are distinct.
- **Regression coverage:** the repository-wide `scripts/test_all.sh` collects both track suites in one invocation.
- **Lesson:** independently valid test folders can still collide when combined; multi-track test structure must be package-safe from the start.

## F-007 - QAOA optimizer result schemas differed

- **AI-generated artifact:** the first Track C QAOA exporter combined Adam and SPSA result mappings, but only Adam included a `learning_rate` field.
- **Failure:** the focused Track C smoke test stopped because the strict shared CSV writer rejects heterogeneous columns.
- **Fix:** record SPSA's explicit `a_k` and `c_k` gain schedules in the common learning-rate field.
- **Regression test:** `tracks/C_quantum_optimization/tests/test_experiment.py::test_track_c_smoke_experiment_writes_cross_track_evidence`.
- **Lesson:** optimizer-specific hyperparameters still need a uniform evidence schema for fair comparison and reproducible export.

## F-008 - Requested process count did not prove independent execution

- **AI-generated artifact:** initial Track D data- and model-parallel demonstrations used a two-worker `ProcessPoolExecutor` for exactly two very short tasks.
- **Failure:** correct numerical outputs were returned, but both tasks could finish on one worker before the second process completed spawning; the first real result file showed only one PID for each demonstration.
- **Fix:** explicitly create one spawn process per partition/stage, collect indexed results through queues, check every exit code, and retain both PIDs in the result.
- **Regression test:** `tracks/D_parallel_distributed/tests/test_parallel.py::test_data_model_and_pipeline_parallel_match_serial_results` asserts two distinct worker PIDs and serial equivalence.
- **Lesson:** a configured pool size is not evidence of independent execution. Record process identities and test the actual execution topology.

## F-009 - Sparse batching did not change whole-horizon throughput

- **AI-generated artifact:** the initial Track E sparse-traffic regression test asserted that delaying the first isolated request must lower overall throughput.
- **Failure:** latency and waiting increased, but throughput was identical because the server returned to idle long before the second request arrived.
- **Fix:** test the actual effect—higher mean waiting and latency, with throughput unchanged or worse—rather than requiring a nonexistent throughput regression.
- **Regression test:** `tracks/E_case_study/tests/test_simulator.py::test_intentional_batch_wait_can_worsen_sparse_latency`.
- **Lesson:** latency and throughput measure different time horizons; a latency regression need not change total makespan.

## F-010 - Capacity sweep initially used different workloads

- **AI-generated artifact:** the first Track E experiment runner included capacity in its scenario-based seed offset.
- **Failure/fairness impact:** method comparisons were fair, but the plotted 384-versus-512 capacity comparison would have mixed capacity effects with different generated requests.
- **Fix:** derive each seed only from workload size, arrival rate, and repeat, then reuse that workload across capacities and all strategies.
- **Regression test:** `tracks/E_case_study/tests/test_experiment.py::test_track_e_smoke_experiment_writes_verified_evidence` asserts one workload digest across the capacity sweep.
- **Lesson:** identical conditions must be enforced by data identity checks, not assumed from nearby loop structure.

## F-011 - Compiler optimization trace had heterogeneous columns

- **AI-generated artifact:** the first Track F trace recorded `instructions_removed` only after an optimization pass, not on the baseline row.
- **Failure:** the shared strict CSV exporter rejected the evidence table during the Track F smoke experiment.
- **Fix:** baseline trace rows now record `instructions_removed=0`, giving every row one explicit schema.
- **Regression test:** `tracks/F_compiler/tests/test_experiment.py::test_track_f_smoke_experiment_writes_complete_evidence` executes the complete exporter.
- **Lesson:** baseline and optimized evidence must share a uniform schema; an omitted field is ambiguous, not equivalent to a recorded zero.

## F-012 - Initial xv6 CPU workload was below timer resolution

- **AI-generated artifact:** the first `schedbench` CPU mode used eight million integer-mixing iterations per child, and the QEMU logger stopped at the summary prefix.
- **Failure:** five of six jobs completed in zero xv6 ticks, so turnaround could not meaningfully distinguish schedulers; the final summary line was truncated by the QEMU monitor escape.
- **Fix:** increase CPU work to eighty million iterations (and mixed bursts proportionally), then wait for a shell prompt after the expected marker before exiting QEMU.
- **Evidence:** the discarded run is retained as `tracks/G_xv6/results/raw/calibration_short_cpu.log`; accepted CPU jobs span 3-8 ticks and contain complete summaries.
- **Lesson:** calibrate work against the measured clock resolution, and do not terminate a console process on a partial marker.

## F-013 - Direct Track G collector lacked repository bootstrap

- **AI-generated artifact:** the first `tracks/G_xv6/benchmarks/collect.py` imported `tracks...` without adding the repository root to `sys.path`.
- **Failure:** direct execution stopped with `ModuleNotFoundError: No module named 'tracks'` before QEMU launched.
- **Fix:** resolve the repository root from the collector path and insert it before importing the QEMU driver.
- **Regression coverage:** the accepted collector then completed all 18 benchmark runs; `scripts/test_all.sh` imports and tests the Track G modules.
- **Lesson:** track-local CLIs need the same explicit bootstrap discipline as repository-level CLIs.

## F-014 - xv6 patch generation used the outer Git repository

- **AI command:** the first `git diff --output=... fa2ddcb..643d1fc` ran from the assignment repository rather than the ignored nested xv6 checkout.
- **Failure:** Git could not resolve the xv6 commit IDs and created empty output files; `git apply` correctly rejected them.
- **Fix:** run diff generation with `git -C external/xv6-riscv`; the resulting complete and scheduler-only patches contain 383 and 75 lines.
- **Verification:** the complete patch passed `git apply --check` at the pinned commit in a fresh local clone, applied, rebuilt, booted, and ran the benchmark.
- **Lesson:** nested repositories require an explicit Git context; always validate generated patch size and clean applicability.

## F-015 - Registry lifecycle test was stale after Track G

- **AI-generated artifact:** the infrastructure registry test still asserted that every track G-J must remain scaffolded.
- **Failure:** the first repository-wide Track G gate reported 1 failed and 87 passed tests even though G was correctly implemented and its 10 focused tests passed.
- **Fix:** assert G's implemented status and exact entry point, while retaining the scaffold refusal invariant for H-J.
- **Regression coverage:** `tests/infrastructure/test_registry_prompts.py::test_registry_defines_all_tracks_and_existing_locations` and the repository-wide gate.
- **Lesson:** lifecycle tests must advance with real track state while preserving the general implemented/scaffolded contract.

## F-016 - Direct Track H calibration omitted the src import path

- **AI command:** the first one-off Track H calibration invoked `.venv/bin/python -c ...` without the repository CLI bootstrap or `PYTHONPATH=src`.
- **Failure:** execution stopped immediately with `ModuleNotFoundError: No module named 'optlab'`; no SQLite database or result was produced.
- **Fix:** rerun the bounded calibration with `PYTHONPATH=src`; the registered `./scripts/run_track.py H` command uses the repository bootstrap and does not need this manual prefix.
- **Regression coverage:** the focused experiment test imports through pytest's configured path, and the registered command is exercised before completion.
- **Lesson:** one-off module commands must reproduce the same source-path setup as supported project entry points.

## F-017 - Initial index-benefit estimator credited unrelated timing noise

- **AI-generated artifact:** the first Track H estimator defined a candidate's benefit as the difference between two complete workload timings.
- **Failure/methodology impact:** a small catalog index could receive apparent benefit from unrelated queries' timing variation, causing its greedy rank to change across runs.
- **Fix:** credit positive latency reductions only for queries whose actual `EXPLAIN QUERY PLAN` names that candidate index. Increase estimation repetitions from 9 to 15 and retain per-candidate plan usage in `candidate_indexes.csv`.
- **Verification:** repeated calibration retained the same greedy and exact selections; tests assert real plan changes without logical-result changes.
- **Lesson:** physical-design benefit estimates should be tied to verified plan use, not correlated noise elsewhere in a workload.

## F-018 - Direct Track I probe omitted the src import path

- **AI command:** the first one-off quantum-algorithm probe invoked `.venv/bin/python` directly without the repository CLI bootstrap or `PYTHONPATH=src`.
- **Failure:** execution stopped with `ModuleNotFoundError: No module named 'optlab'`; no circuit ran and no result was retained.
- **Fix:** rerun the bounded probe with `PYTHONPATH=src`; the supported `./scripts/run_track.py I` command already applies the repository bootstrap.
- **Regression coverage:** the focused Track I tests import through pytest's configured path, and the registered Track I command completed its full artifact bundle.
- **Lesson:** direct diagnostic commands must reproduce the same source-path setup as supported project entry points.

## F-019 - Infrastructure lifecycle tests were stale after Track I

- **AI-generated artifact:** the infrastructure tests still required Track I to refuse execution and grouped I with scaffolded Track J.
- **Failure:** the first repository-wide Track I gate reported two failed lifecycle assertions while all 108 other tests passed.
- **Fix:** require Track I's implemented status and exact benchmark entry point; move the unimplemented-command refusal check to Track J.
- **Regression coverage:** `tests/infrastructure/test_cli.py::test_unimplemented_track_refuses_to_claim_run` and `tests/infrastructure/test_registry_prompts.py::test_registry_defines_all_tracks_and_existing_locations`.
- **Lesson:** repository lifecycle assertions must advance with a completed track while preserving refusal behavior for genuinely scaffolded work.

## F-020 - Visual-QA plot split changed the wrong constructor

- **AI-generated artifact:** while separating noise scale from plateau qubit count, the first patch changed the QML comparison figure to three axes but left the limitations figure at two.
- **Failure:** result regeneration stopped with `IndexError: index 2 is out of bounds`; the interrupted run was not accepted as final evidence.
- **Fix:** restore the QML comparison to two axes and make the training/noise/plateau figure explicitly three axes.
- **Regression coverage:** the Track I smoke experiment executes the complete plotting path, and the final figures were visually inspected after regeneration.
- **Lesson:** when several plotting calls have similar constructors, patch and review the exact local context before accepting regenerated evidence.
