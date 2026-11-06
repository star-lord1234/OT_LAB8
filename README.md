# Optimization Techniques Lab — Assignment 8

**Optimize Anything: The 14-Day Vibe-Coding Challenge**  
VJTI, Mumbai · Academic Year 2026–2027  
Student: Bianca Sawant · Registration No.: 241071067

This repository contains the requirements audit, macOS setup, shared experiment utilities, implementations and evidence for Assignment 8 Tracks A–J, plus the final academic report. Experiments are intentionally small and reproducible for a 16 GB Apple Silicon MacBook Air. Where a result is simulated, the report labels it as simulated; no physical quantum hardware or real LLM inference service is represented.

## Start here

| Document | What it contains |
|---|---|
| [`Assignment_8_Bianca_Sawant_Report.pdf`](Assignment_8_Bianca_Sawant_Report.pdf) | Typeset 33-page academic report with track formulations, methods, results, figures, limitations, references and appendices. |
| [`REQUIREMENTS.md`](REQUIREMENTS.md) | Requirement classification and traceability to code, tests, results and report sections. |
| [`PROGRESS.md`](PROGRESS.md) | Track status, evidence gates and cross-track dependencies. |
| [`SETUP.md`](SETUP.md) | Measured machine inventory, isolated environment setup, preflight details and limitations. |
| [`DEPENDENCIES.md`](DEPENDENCIES.md) | Dependency purpose and installation notes. |
| [`bm.md`](bm.md) | Proposed implementation blueprint reviewed against the assignment PDF. |

## Current status and academic caveats

All ten tracks have implementations, benchmark artifacts and per-track report material in the repository. The overall submission still has two open academic items that require external inputs:

1. The instructor's actual Chapter 6 syllabus or teaching material is not present. The report maps the methods named by the assignment and explicitly leaves syllabus-dependent coverage unresolved; A–D and I should not be called fully syllabus-verified until that material is checked.
2. Only OpenAI Codex is recorded as an AI tool. The assignment's comparison between two AI tools remains open; no comparison results are invented.

Track J uses the pinned public MIT-licensed `more-itertools` codebase. Track C and I quantum experiments are simulator results, Track E is a synthetic scheduling simulation, and Track G runs xv6 under RISC-V QEMU. Track E does not claim real LLM serving improvements, and the report does not claim quantum advantage. See [`PROGRESS.md`](PROGRESS.md) for the detailed per-track gates and [`logs/tool_comparison.md`](logs/tool_comparison.md) for the open AI tool comparison.

## Reproducing the environment

The verified setup uses an isolated CPython 3.12 environment managed by `uv`; dependencies are pinned in `uv.lock`. The setup instructions and the actual hardware/tool inventory are in [`SETUP.md`](SETUP.md).

```bash
cd /path/to/OTLab_8
UV_PYTHON_INSTALL_DIR="$PWD/.python" uv sync --locked --python 3.12
./scripts/preflight.sh
```

The environment setup avoids installing Python packages globally. The preflight checks numerical optimization, PyTorch/autograd, ILP, quantum simulation, SQLite, multiprocessing, QEMU and RISC-V tools. System-level prerequisites and any unresolved platform caveats are documented in `SETUP.md`.

## Verification

Run the repository validation and test suite:

```bash
./scripts/test_all.sh
```

This runs the environment preflight, repository/registry validation and pytest across `tests/` and `tracks/`. To run only pytest after setup:

```bash
MPLCONFIGDIR="$PWD/.cache/matplotlib" \
XDG_CACHE_HOME="$PWD/.cache/xdg" \
  .venv/bin/python -m pytest tests tracks
```

Run structural and provenance checks separately:

```bash
.venv/bin/python scripts/validate_repo.py
```

## Running experiments

List the registered tracks and their status:

```bash
./scripts/run_track.py --list
```

Inspect a track's implementation, benchmark, tests, result directory, configuration and dependencies without running it:

```bash
./scripts/run_track.py A --plan
```

Run one track using its registered entry point:

```bash
./scripts/run_track.py A
```

Run all tracks in dependency-aware registry order, or print all plans first:

```bash
./scripts/run_all.py --plans
./scripts/run_all.py
```

Track runs may regenerate or overwrite artifacts in their result directories. Check the track README and configuration before rerunning a benchmark. Results use fixed seeds where applicable, and the CSV/JSON artifacts retain raw or summarized measurements.

## Track map

| Track | Experiment | Implementation and evidence |
|---|---|---|
| A | Continuous optimization, curvature methods, autograd, sensitivity and noise | [`tracks/A_continuous/`](tracks/A_continuous/) · [`report/track_a.md`](report/track_a.md) |
| B | Knapsack method comparison and reusable Max-Cut QUBO/Ising fixture | [`tracks/B_discrete/`](tracks/B_discrete/) · [`report/track_b.md`](report/track_b.md) |
| C | QAOA, VQE, variational circuits, shots, noise and simulator diagnostics | [`tracks/C_quantum_optimization/`](tracks/C_quantum_optimization/) · [`report/track_c.md`](report/track_c.md) |
| D | Submodular maximization, process parallelism and federated/multi-task optimization | [`tracks/D_parallel_distributed/`](tracks/D_parallel_distributed/) · [`report/track_d.md`](report/track_d.md) |
| E | Inference-request batching and scheduling using a synthetic discrete-event workload | [`tracks/E_case_study/`](tracks/E_case_study/) · [`report/track_e.md`](report/track_e.md) |
| F | Toy compiler with four optimization passes and optimized pass ordering | [`tracks/F_compiler/`](tracks/F_compiler/) · [`report/track_f.md`](report/track_f.md) |
| G | xv6 priority scheduling experiment in RISC-V QEMU | [`tracks/G_xv6/`](tracks/G_xv6/) · [`report/track_g.md`](report/track_g.md) |
| H | SQLite physical index selection under a storage budget | [`tracks/H_dbms/`](tracks/H_dbms/) · [`report/track_h.md`](report/track_h.md) |
| I | Textbook quantum algorithms, quantum ML, query complexity and noise experiments | [`tracks/I_quantum_qml/`](tracks/I_quantum_qml/) · [`report/track_i.md`](report/track_i.md) |
| J | Test prioritization on pinned `more-itertools`, using measured coverage and test costs | [`tracks/J_software_engineering/`](tracks/J_software_engineering/) · [`report/track_j.md`](report/track_j.md) |

Each track directory separates implementation, benchmarks, tests and results. The central registry is [`experiments/registry.json`](experiments/registry.json); shared experiment utilities live under [`src/optlab/common/`](src/optlab/common/).

## Repository layout

```text
configs/                 Experiment defaults and per-track settings
docs/                    Repository process and commit notes
experiments/             Track registry and dependency order
logs/                    AI tool register, failure log and comparison template
prompts/                 Recorded prompts, responses and verification notes
report/                  Track report drafts, demo/viva notes and method matrix
results/                 Shared environment metadata and result guidance
scripts/                 Setup, preflight, validation, experiment and report tools
src/optlab/common/       Shared seeds, config, measurement, plots and verification
src/optlab/quantum/      Quantum circuit and optimization utilities shared by C/I
tests/                   Shared infrastructure regression tests
tracks/A_* ... J_*       Track-specific implementations, benchmarks, tests, results
```

## Reproducibility and interpretation

- Use the committed `uv.lock` and the documented Python version for the tested environment.
- Randomized experiments record seeds and repeated runs where practical; generated workloads and source projects are documented in their track evidence.
- Results distinguish exact references, measured local runtime, theory and simulator output. A simulation is not evidence of physical hardware performance.
- Negative speedups and cases where an optimization adds overhead are retained and discussed.
- Prompt logs and failures are historical records; unknown model snapshots are labeled unknown rather than inferred.
- Do not interpret this repository's `implemented` registry status as proof that the instructor's Chapter 6 syllabus has been fully audited.

## AI-assisted development register

The assignment requests an AI tools table in the project README. The detailed record is maintained in [`logs/ai_tools_register.csv`](logs/ai_tools_register.csv), with per-task records under `prompts/`.

| Date | Tool | Model label available in session | Scope |
|---|---|---|---|
| 2026-10-29 to 2026-11-06 | OpenAI Codex | GPT-5 family; exact deployed snapshot not exposed | Requirements, setup, shared infrastructure and Tracks A–J |
| 2026-11-06 | OpenAI Codex | GPT-6 family; exact deployed snapshot not exposed | Repository audit, academic report preparation and visual verification |

These are two recorded Codex sessions, not two distinct AI tools. A second-tool comparison has not been performed. See [`logs/tool_comparison.md`](logs/tool_comparison.md) and [`logs/failures.md`](logs/failures.md).

## License and external material

Track J's external project and its pinned revision/license are recorded in [`tracks/J_software_engineering/SOURCE.md`](tracks/J_software_engineering/SOURCE.md). Direct dependencies and their purposes are listed in [`DEPENDENCIES.md`](DEPENDENCIES.md). See [`REQUIREMENTS.md`](REQUIREMENTS.md) for the assignment's traceability matrix and [`report/report.md`](report/report.md) for supporting cross-track report material.
