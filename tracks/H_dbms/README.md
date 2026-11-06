# Track H - SQLite physical index selection

Status: **implemented and verified**.

Track H selects optional SQLite indexes under a measured 180-page storage
budget. It compares no optional indexes, benefit-per-page greedy selection,
binary MILP through SciPy/HiGHS, and exact 0/1 knapsack dynamic programming.
SQLite's internal query optimizer remains unchanged and chooses plans from the
physical indexes made available by each configuration.

## Evidence

- Formal model: `MATHEMATICS.md`
- Dataset documentation: `DATASET.md`
- Generator/schema: `implementation/database.py`, `benchmarks/generate_database.py`
- Workload and candidates: `implementation/models.py`
- Solvers: `implementation/selection.py`
- Benchmark/plan capture: `implementation/experiment.py`
- Tests: `tests/`
- Results, actual plans, and plots: `results/`
- Report: `report/track_h.md`
- AI record: `prompts/H/2026-11-06-track-h-implementation/`

Run the complete retained experiment:

```bash
./scripts/run_track.py H
.venv/bin/python -m pytest tracks/H_dbms/tests
```

Generate only the fixed database:

```bash
.venv/bin/python tracks/H_dbms/benchmarks/generate_database.py \
  --output data/generated/track_h.sqlite
```

Fresh timings can vary with power state, cache state, and background load. The
runner replaces Track H's generated result files, so preserve committed evidence
before intentionally collecting a new run.
