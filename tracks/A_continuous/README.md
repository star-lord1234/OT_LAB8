# Track A - Continuous optimization

Status: **implemented and verified; exact Chapter 6 syllabus coverage remains blocked.**

## Implemented scope

The track compares batch GD, SGD, mini-batch SGD, Momentum, Nesterov, AdaGrad, RMSProp, Adam, Newton, Gauss-Newton, and BFGS. It includes independently checked gradients, a PyTorch backprop/update demonstration, exact/diagonal/Fisher/low-rank curvature evidence, three landscape classes, learning-rate sensitivity, noise, and regularization.

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

Generate every result and plot:

```bash
./scripts/run_track.py A
```

Run focused tests:

```bash
.venv/bin/python -m pytest tracks/A_continuous/tests
```

The result inventory is in `results/manifest.json`; the draft report is `report/track_a.md`. The missing classroom Chapter 6 topic list is a real blocker for A-07/SYL-01, even though the explicitly named methods are implemented.
