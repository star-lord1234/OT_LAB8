# Track C - Quantum optimization

Status: **implemented and verified on local simulators; exact Chapter 6 syllabus coverage remains blocked.**

## Implemented scope

The track reuses Track B's exact Max-Cut fixture for QAOA and adds VQE, a two-qubit QNN, parameter-shift, SPSA, quantum natural gradient, finite-shot and depolarizing-noise experiments, depth/evaluation accounting, a finite-size barren-plateau proxy, and a toy embedding chain-strength experiment. Every result is labeled local simulation; no physical hardware was used.

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

Generate all results:

```bash
./scripts/run_track.py C
```

Run focused tests:

```bash
.venv/bin/python -m pytest tracks/C_quantum_optimization/tests
```

Shared quantum utilities live in `src/optlab/quantum/` for Track I reuse. Track I retains independent acceptance criteria. See `MATHEMATICS.md`, `results/manifest.json`, and `report/track_c.md`.
