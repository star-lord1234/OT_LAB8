# Track E - Main real-process case study

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Optimize a documented offline request-batching simulation using FIFO, greedy, and a tiny exact reference without claiming accelerator measurements.

The authoritative acceptance criteria are the Track E rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/E_case_study/implementation/`
- Benchmark runner/data preparation: `tracks/E_case_study/benchmarks/`
- Track-specific tests: `tracks/E_case_study/tests/`
- Raw and summarized track evidence: `tracks/E_case_study/results/`
- Configuration: `configs/tracks/E.toml`
- Prompt history: `prompts/E/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py E --plan
```

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
