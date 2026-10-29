# Track H - DBMS optimization

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Select SQLite indexes under a storage budget with two Chapter 6 methods and verify plans, latency, throughput, storage, and identical results.

The authoritative acceptance criteria are the Track H rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/H_dbms/implementation/`
- Benchmark runner/data preparation: `tracks/H_dbms/benchmarks/`
- Track-specific tests: `tracks/H_dbms/tests/`
- Raw and summarized track evidence: `tracks/H_dbms/results/`
- Configuration: `configs/tracks/H.toml`
- Prompt history: `prompts/H/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py H --plan
```

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
