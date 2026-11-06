# Assignment 8 - Optimize Anything

Lightweight, reproducible implementation workspace for the compulsory Tracks A-J. The authoritative requirements and current status are in `REQUIREMENTS.md` and `PROGRESS.md`.

Current state: **Tracks A-H implemented and experimentally verified; Tracks I-J remain scaffolded.** Track E is a simulation-only case study and Track G is measured under RISC-V QEMU. Exact Chapter 6 coverage for A-D remains blocked until the classroom syllabus is supplied.

## Quick start

The verified macOS setup is documented in `SETUP.md`.

```bash
UV_PYTHON_INSTALL_DIR="$PWD/.python" uv sync --locked --python 3.12
./scripts/preflight.sh
./scripts/test_all.sh
```

## Track commands

List tracks:

```bash
./scripts/run_track.py --list
```

Inspect one track's registered locations without running it:

```bash
./scripts/run_track.py A --plan
```

Run an implemented track:

```bash
./scripts/run_track.py A
```

Until a track has a tested entry point and its registry status is `implemented`, the last command deliberately exits with status 2 and states that no experiment ran.

Inspect every plan or run every implemented track:

```bash
./scripts/run_all.py --plans
./scripts/run_all.py
```

Capture privacy-safe environment metadata:

```bash
.venv/bin/python scripts/capture_environment.py
```

Run infrastructure tests and all currently available checks:

```bash
./scripts/test_all.sh
```

Run pytest alone:

```bash
MPLCONFIGDIR="$PWD/.cache/matplotlib" \
XDG_CACHE_HOME="$PWD/.cache/xdg" \
  .venv/bin/python -m pytest tests
```

Validate structure, registry, and prompt records:

```bash
.venv/bin/python scripts/validate_repo.py
```

## Repository map

- `src/optlab/common/`: shared experiment infrastructure.
- `tracks/A_*` through `tracks/J_*`: explicit implementation, benchmark, test, and result locations.
- `configs/tracks/`: per-track configuration placeholders.
- `experiments/registry.json`: single track registry and dependency map.
- `tests/infrastructure/`: infrastructure regression tests.
- `prompts/A` through `prompts/J`: honest track AI histories; A-H currently contain implementation records.
- `prompts/_cross_track/`: actual requirements, setup, and scaffolding interactions.
- `logs/`: AI tools register, genuine failure log, and tool-comparison template.
- `report/`: technical-report, demo, and viva scaffolds.
- `setup_logs/`: retained real preflight outputs.

## Evidence rules

- Raw measurements are retained; plots/tables must be generated from them.
- Random experiments use explicit seeds and repeated runs.
- Simulation, theory, and measured hardware results must be labeled separately.
- A script running is not enough: formulation, baseline, comparison, correctness, results, prompts, and report links are all required.
- Prompt, response, failure, tool, model, timing, and commit records must be real. Unknown model snapshots are recorded as unknown rather than guessed.

## AI tools register

The assignment requires this table in the README. The machine-readable source is `logs/ai_tools_register.csv`.

| Date | Tool | Model | Scope | Work |
|---|---|---|---|---|
| 2026-10-29 to 2026-11-06 | OpenAI Codex | GPT-5 family; exact deployed snapshot not exposed | Cross-track and Tracks A-H | Requirements audit, environment/setup, implementation, debugging, experiments, testing, plots, and documentation |

No second AI tool comparison has occurred yet; that mandatory cross-tool comparison remains open and will not be fabricated.

## Important blockers

- Obtain the exact Chapter 6 classroom syllabus before Tracks A-D or I can be declared complete.
- Complete Tracks I-J and the global report/demo evidence gates.
- Select a real public codebase for Track J before implementing its benchmark.
