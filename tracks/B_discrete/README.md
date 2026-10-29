# Track B - Discrete optimization

Status: **implemented and verified; exact Chapter 6 syllabus coverage remains blocked.**

## Implemented scope

Greedy, SciPy HiGHS ILP, branch-and-bound, and dynamic programming solve identical 0/1 knapsack instances and are checked against exhaustive enumeration. A five-vertex weighted Max-Cut fixture verifies QUBO and Ising energies for every state, and a separate exactly-one QUBO demonstrates constraint-penalty strength.

The authoritative acceptance criteria are the Track B rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/B_discrete/implementation/`
- Benchmark runner/data preparation: `tracks/B_discrete/benchmarks/`
- Track-specific tests: `tracks/B_discrete/tests/`
- Raw and summarized track evidence: `tracks/B_discrete/results/`
- Configuration: `configs/tracks/B.toml`
- Prompt history: `prompts/B/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py B --plan
```

Generate all results and plots:

```bash
./scripts/run_track.py B
```

Run focused tests:

```bash
.venv/bin/python -m pytest tracks/B_discrete/tests
```

See `MATHEMATICS.md`, `results/manifest.json`, and `report/track_b.md`. B-06 remains blocked until the exact classroom syllabus is supplied.
