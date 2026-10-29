# Track C - Quantum optimization

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Use local simulation for QAOA, VQE, PQC/QNN, parameter-shift, SPSA, quantum natural gradient, shots, noise, barren-plateau proxy, and embedding limits.

The authoritative acceptance criteria are the Track C rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/C_quantum_optimization/implementation/`
- Benchmark runner/data preparation: `tracks/C_quantum_optimization/benchmarks/`
- Track-specific tests: `tracks/C_quantum_optimization/tests/`
- Raw and summarized track evidence: `tracks/C_quantum_optimization/results/`
- Configuration: `configs/tracks/C.toml`
- Prompt history: `prompts/C/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py C --plan
```

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
