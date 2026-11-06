# Track J - Software-engineering optimization

Status: **implemented and verified on a pinned public codebase.** Selected suites are risk-reduction subsets, never replacements for full regression testing.

## Experiment

The real target is the MIT-licensed `more-itertools` project at commit `f42daddf205f335fea6e200dad46049f33e71221`: 7,282 physical Python source lines and an untouched 771-test/21,203-subtest suite. The checkout is isolated under `external/` and imported through `PYTHONPATH`; nothing is installed globally.

Pytest test classes are candidate scheduling units. A baseline coverage-context profile measures per-test duration and executed source statements before optimization. From 167 available classes, 24 are selected at deterministic equal intervals across collection order. The fixed budget is 10% of their total measured duration. Original-order selection is compared with greedy marginal coverage per second; exhaustive enumeration verifies a 14-candidate subset.

## Commands

```bash
./scripts/prepare_track_j.sh
./scripts/run_track.py J
.venv/bin/python -m pytest tracks/J_software_engineering/tests
```

The full experiment takes about two minutes because context-attributed coverage is intentionally measured rather than estimated. See `SOURCE.md`, `MATHEMATICS.md`, `results/manifest.json`, and `report/track_j.md`.
