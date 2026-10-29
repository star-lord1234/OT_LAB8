# Track G - xv6 operating-system optimization

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Benchmark a priority-scheduler kernel change over three workloads under QEMU, retain baseline/usertest logs, and publish a reproducible patch.

The authoritative acceptance criteria are the Track G rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/G_xv6/implementation/`
- Benchmark runner/data preparation: `tracks/G_xv6/benchmarks/`
- Track-specific tests: `tracks/G_xv6/tests/`
- Raw and summarized track evidence: `tracks/G_xv6/results/`
- Configuration: `configs/tracks/G.toml`
- Prompt history: `prompts/G/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py G --plan
```

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
