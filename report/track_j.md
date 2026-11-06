# Track J — Software-Engineering Optimization

Status: **implemented and verified on a genuine pinned public codebase.** The selected suites are not substitutes for full regression testing.

## J.1 Source, license, and untouched baseline

The target is the production Python library `more-itertools`, pinned at commit `f42daddf205f335fea6e200dad46049f33e71221`. It is MIT-licensed and contains 7,282 physical Python source lines (5,402 nonblank/non-comment). [SOURCE.md](../tracks/J_software_engineering/SOURCE.md) records the official repository, commit, license digest, isolated checkout procedure, and dependency boundary. No upstream code or tests were modified and no global package was installed.

The untouched suite passed 771 tests plus 21,203 unittest subtests in all three runs. Median end-to-end wall time was 7.105 seconds ([baseline runs](../tracks/J_software_engineering/results/baseline_runs.csv)). The coverage-context run also passed all 771 tests and executed all 2,233 source statements, but took 89.58 seconds. That overhead belongs to profiling and is not presented as ordinary test runtime.

## J.2 Baseline profile and bottleneck

Coverage and setup/call/teardown durations were collected **before** selection. The project exposes 167 test classes. Twenty-four deterministic, evenly spaced classes form the bounded optimization pool, covering a union of 271 attributed executable lines. The slowest sampled class was `TestSynchronized` at 0.3303 measured seconds; the next was `DerangementsTests` at 0.0449 seconds ([profile](../tracks/J_software_engineering/results/baseline_profile.json), [candidate table](../tracks/J_software_engineering/results/candidate_profile.csv)).

The large synchronization-class cost makes original ordering particularly sensitive under a tight CI budget. This profile motivated a fixed 10% candidate-duration budget, `B=0.044501` seconds. The mathematical model and the distinction between profiled test duration and process wall time are defined in [MATHEMATICS.md](../tracks/J_software_engineering/MATHEMATICS.md).

## J.3 Original order versus greedy maximum coverage

The original-order baseline selected 11 classes containing 50 individual tests. Its profiled cost was 0.044431 seconds, and it covered 126 of the 271 candidate-universe lines (46.5%).

Greedy marginal coverage per second selected 18 classes containing 71 tests for a slightly lower profiled cost, 0.043445 seconds. It covered 232 lines (85.6%): 106 more lines and a 39.1 percentage-point improvement under the same budget ([summary](../tracks/J_software_engineering/results/selection_summary.csv), [schedule](../tracks/J_software_engineering/results/selected_tests.csv), [coverage plot](../tracks/J_software_engineering/results/plots/coverage_vs_budget.png)). The exact candidate line sets are retained in [candidate_coverage.json](../tracks/J_software_engineering/results/candidate_coverage.json); tests recompute all three reported union objectives from that file.

Both selected suites passed three uninstrumented executions. Median end-to-end wall time was 0.1330 seconds for original order and 0.1333 seconds for greedy. The similar wall times are an honest result: interpreter and pytest startup dominate these tiny selections, even though greedy retains more checks and coverage at essentially the same measured wall time. Relative to the 7.105-second full suite, both provide much faster feedback, but neither is a release-quality replacement.

Including import-time source execution, rerun coverage was 21.36% for original order and 25.79% for greedy. The optimization objective is instead context-attributed candidate lines, because common import-time lines do not distinguish candidates. For every method, the rerun context set exactly matched the predicted union.

## J.4 Exact small-subset verification

Exhaustive enumeration considered all `2^14=16,384` subsets of the first 14 candidates under its 0.010378-second budget. The exact optimum covered 86 of 164 subset-universe lines using six classes and 27 tests. Greedy also covered 86, giving a zero-line optimality gap; original order covered 61, a 25-line gap ([exact reference](../tracks/J_software_engineering/results/exact_subset_reference.json)). The exact selected suite passed all three executions.

This proves greedy optimality only for that measured 14-candidate instance, not for maximum coverage in general.

## J.5 Reliability, maintainability, and reproduction

Coverage does not equal correctness. Omitted tests may exercise different assertions on the same lines, exception behavior, concurrency, platform-specific cases, or faults not represented by line coverage. The 24-candidate pool itself is only a deterministic sample of 167 classes. A fast greedy suite can be used for change feedback, but the complete 771-test suite must remain the merge/release gate.

Maintainability costs include retaining the profiler, refreshing durations/coverage after source or environment changes, reviewing why a test disappeared, and preventing the optimized list from becoming a silently stale allow-list. The benefit is a transparent, reproducible schedule with explicit marginal coverage rather than a hand-maintained “fast tests” list.

Run:

```bash
./scripts/prepare_track_j.sh
./scripts/run_track.py J
.venv/bin/python -m pytest tracks/J_software_engineering/tests
```

The complete [manifest](../tracks/J_software_engineering/results/manifest.json) indexes source, baseline, candidate, selection, verification, plot, and environment evidence. A fresh measurement takes about two minutes because context-attributed coverage is intentionally collected and selected suites are actually rerun.
