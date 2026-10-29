# Track I - Quantum algorithms and QML advantage

Status: **scaffolded; no algorithm implementation or result exists yet.**

## Minimum planned scope

Run every taught quantum algorithm, hand-code two circuits, compare QML with classical models, and contrast evidence with Track D.

The authoritative acceptance criteria are the Track I rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/I_quantum_qml/implementation/`
- Benchmark runner/data preparation: `tracks/I_quantum_qml/benchmarks/`
- Track-specific tests: `tracks/I_quantum_qml/tests/`
- Raw and summarized track evidence: `tracks/I_quantum_qml/results/`
- Configuration: `configs/tracks/I.toml`
- Prompt history: `prompts/I/`
- Report destination: see `experiments/registry.json`

Inspect this plan without running an experiment:

```bash
./scripts/run_track.py I --plan
```

A normal run intentionally exits non-zero until the registry status is changed to `implemented` and a tested entry point is registered.
