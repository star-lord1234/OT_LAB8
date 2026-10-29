# Track A - Continuous optimization

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Compare named first- and second-order methods, backpropagation, curvature approximations, tuning, and noisy objectives on tiny verified models/functions.

The authoritative acceptance criteria are the Track A rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/A_continuous/implementation/`
- Benchmark runner/data preparation: `tracks/A_continuous/benchmarks/`
- Track-specific tests: `tracks/A_continuous/tests/`
- Raw and summarized track evidence: `tracks/A_continuous/results/`
- Configuration: `configs/tracks/A.toml`
- Prompt history: `prompts/A/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py A --plan
```

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
