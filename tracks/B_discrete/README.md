# Track B - Discrete optimization

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Compare greedy, ILP, branch-and-bound, and dynamic programming; produce verified QUBO/Ising and constrained-penalty fixtures for Track C.

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

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
