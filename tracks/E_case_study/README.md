# Track E - Main real-process case study

Status: **implemented and verified as a synthetic discrete-event simulation.**

This track optimizes a documented inference-like request queue using immediate FCFS, greedy length-aware batching, and dynamic-programming batch selection, with a tiny exhaustive reference. It does not execute an LLM or measure accelerator performance.

The authoritative acceptance criteria are the Track E rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/E_case_study/implementation/`
- Benchmark runner: `tracks/E_case_study/benchmarks/`
- Tests: `tracks/E_case_study/tests/`
- Results and plots: `tracks/E_case_study/results/`
- Configuration: `configs/tracks/E.toml`
- Prompt history: `prompts/E/`
- Formulation: `tracks/E_case_study/MATHEMATICS.md`
- Strategy table: `tracks/E_case_study/STRATEGY_SELECTION.md`
- Report: `report/track_e.md`

Generate the complete evidence bundle:

```bash
./scripts/run_track.py E
```

Run focused tests:

```bash
.venv/bin/python -m pytest tracks/E_case_study/tests
```

All comparisons use identical hashed workloads for a given size, rate, repeat, and capacity sweep. The results are simulated time units and must not be quoted as real inference gains.
