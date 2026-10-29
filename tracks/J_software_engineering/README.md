# Track J - Software-engineering optimization

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Optimize test prioritization on a pinned realistic codebase using measured coverage/time and a named Chapter 6 method.

The authoritative acceptance criteria are the Track J rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/J_software_engineering/implementation/`
- Benchmark runner/data preparation: `tracks/J_software_engineering/benchmarks/`
- Track-specific tests: `tracks/J_software_engineering/tests/`
- Raw and summarized track evidence: `tracks/J_software_engineering/results/`
- Configuration: `configs/tracks/J.toml`
- Prompt history: `prompts/J/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py J --plan
```

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
