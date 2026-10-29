# Track D - Submodular, parallel, distributed, and multi-task optimization

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Measure submodular greedy quality, makespan/speedup/efficiency, parallel forms, FedAvg, MGDA, and GradNorm against verified baselines.

The authoritative acceptance criteria are the Track D rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/D_parallel_distributed/implementation/`
- Benchmark runner/data preparation: `tracks/D_parallel_distributed/benchmarks/`
- Track-specific tests: `tracks/D_parallel_distributed/tests/`
- Raw and summarized track evidence: `tracks/D_parallel_distributed/results/`
- Configuration: `configs/tracks/D.toml`
- Prompt history: `prompts/D/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py D --plan
```

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
