# Track F - Compiler optimization

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Build a toy compiler pipeline, implement at least two semantics-preserving passes, optimize a compiler decision, and measure four required costs.

The authoritative acceptance criteria are the Track F rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/F_compiler/implementation/`
- Benchmark runner/data preparation: `tracks/F_compiler/benchmarks/`
- Track-specific tests: `tracks/F_compiler/tests/`
- Raw and summarized track evidence: `tracks/F_compiler/results/`
- Configuration: `configs/tracks/F.toml`
- Prompt history: `prompts/F/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py F --plan
```

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
