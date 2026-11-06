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
