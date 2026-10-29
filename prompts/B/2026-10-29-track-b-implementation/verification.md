# Verification

- Initial focused Track B result: 11/11 tests passed.
- Real benchmark command `./scripts/run_track.py B` completed successfully.
- All exact knapsack methods matched exhaustive enumeration on all three benchmark instances.
- Greedy remained feasible but had independently verified gaps of 27.27%, 11.36%, and 1.20%.
- All 32 Max-Cut states satisfy `QUBO energy = Ising energy = -cut` with zero observed mismatch.
- Classical maximum cut: 8.0; four optimal bitstrings recorded.
- Exactly-one QUBO matched its direct formula for all states; penalty 5.0 produced a feasible ground state while 0.5 and 2.0 did not.
- The first combined A+B run stopped at collection because duplicate `test_experiment.py` names were not package-qualified; fixed with test-package markers and logged as F-006.
- Final repository-wide gate: preflight 7/7, repository validation passed, and 42/42 tests passed.
- Verified implementation commit: `e2b80847e9436d73a54620442c1e74a6fffc2c5c` (`[AI:Codex] Implement Track B discrete optimization`).
