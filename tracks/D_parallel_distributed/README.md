# Track D - Submodular, parallel, distributed, and multi-task optimization

Status: **implemented and experimentally verified on local CPU processes; exact Chapter 6 syllabus coverage remains blocked.**

This track contains independently verifiable maximum-coverage, CPU scheduling/overhead, data/model/pipeline parallel, federated-learning, and two-task optimization experiments. Process work uses macOS-safe `spawn`; results retain worker PIDs and negative speedups.

The authoritative acceptance criteria are the Track D rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/D_parallel_distributed/implementation/`
- Benchmark runner: `tracks/D_parallel_distributed/benchmarks/`
- Tests: `tracks/D_parallel_distributed/tests/`
- Results and plots: `tracks/D_parallel_distributed/results/`
- Configuration: `configs/tracks/D.toml`
- Prompt history: `prompts/D/`
- Report: `report/track_d.md`

Run the full evidence bundle:

```bash
./scripts/run_track.py D
```

Run focused tests:

```bash
.venv/bin/python -m pytest tracks/D_parallel_distributed/tests
```

The real dynamic scheduler is a central shared queue. A separate discrete-event local-deque simulation provides the work-stealing investigation and is explicitly not reported as wall-clock performance. D-08 remains unresolved until the classroom syllabus confirms whether additional distributed or multi-task methods were taught.
