# Track F - Compiler optimization

Status: **implemented and verified with four optimization passes.**

The track contains a lexer, recursive-descent parser, SSA-like three-address IR, IR interpreter, unoptimized compiler, constant folding/propagation, common subexpression elimination, strength reduction, and dead-code elimination. Five programs are checked before and after optimization.

The authoritative acceptance criteria are the Track F rows in `REQUIREMENTS.md`. Chapter 6 syllabus-dependent rows remain unresolved until classroom materials are supplied.

## Fixed locations

- Implementation: `tracks/F_compiler/implementation/`
- Benchmark runner: `tracks/F_compiler/benchmarks/`
- Tests: `tracks/F_compiler/tests/`
- Results and plots: `tracks/F_compiler/results/`
- Configuration: `configs/tracks/F.toml`
- Prompt history: `prompts/F/`
- Language/optimization model: `tracks/F_compiler/LANGUAGE_AND_OPTIMIZATION.md`
- Samples: `tracks/F_compiler/samples/`
- Report: `report/track_f.md`

Generate the complete evidence bundle:

```bash
./scripts/run_track.py F
```

Run focused tests:

```bash
.venv/bin/python -m pytest tracks/F_compiler/tests
```

Runtime results measure the Python IR interpreter, and code size is serialized IR bytes. Neither is presented as native-code performance.
