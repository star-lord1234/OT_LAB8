# macOS Development Environment

Environment inventory verified: 2026-10-29; xv6 validation updated: 2026-11-06
(Asia/Kolkata)

Environment status: **the requested development preflight passes 7/7, and the
pinned xv6 source has now been built, booted, and tested under QEMU.** Track G
retains pristine, support-baseline, and optimized full-`usertests` transcripts.

## 1. Measured machine inventory

No hardware generation, architecture, OS version, or package was assumed. The following values came from `uname`, `sw_vers`, `system_profiler`, `df`, and tool version commands on this machine.

| Item | Measured value |
|---|---|
| Machine | MacBook Air, model identifier Mac17,3 |
| Chip | Apple M5 |
| Architecture | arm64 |
| CPU cores | 10 total: 4 performance and 6 efficiency |
| RAM | 16 GB |
| macOS | 26.5.2, build 25F84 |
| Darwin kernel | 25.5.0 |
| Available disk before setup | Approximately 290 GiB |
| Available disk after setup | Approximately 288 GiB |

Serial numbers, UUIDs, and device identifiers are intentionally not recorded in the repository.

## 2. Pre-existing tools

| Tool | State before project setup |
|---|---|
| Homebrew | 6.0.22 under `/opt/homebrew` |
| Git | Apple Git 2.50.1 at `/usr/bin/git` |
| Xcode Command Line Tools | Installed at `/Library/Developer/CommandLineTools` |
| Apple Clang | 21.0.0, arm64 target |
| `make` | Available from Command Line Tools |
| Homebrew Python | 3.14.6 |
| System Python | 3.9.6 |
| `uv` | 0.11.25, arm64 |
| Active virtual environment | None |
| Project virtual environment | None |
| QEMU RISC-V system emulator | Not installed |
| RISC-V GCC/binutils | Not installed |

The Homebrew Python 3.14 installation initially had none of the relevant project packages installed: NumPy, SciPy, matplotlib, scikit-learn, PyTorch, PuLP, Qiskit, PennyLane, NetworkX, pytest, coverage, or pytest-cov.

## 3. Python environment decision

The project uses **CPython 3.12.13 arm64** in an isolated `.venv`. Python 3.12 was selected because the only pre-existing Homebrew interpreter was Python 3.14 and the scientific, PyTorch, and quantum ecosystem is more reliably wheel-compatible with Python 3.12.

The interpreter itself is stored in the ignored project directory `.python/`; dependencies are stored in `.venv/`. Nothing was installed into the Homebrew or system Python environments.

Reproducibility files:

- `pyproject.toml`: direct dependency ranges and Python constraint.
- `.python-version`: requests Python 3.12.
- `uv.lock`: exact transitive dependency lock.

To recreate the environment without altering global Python packages:

```bash
cd /path/to/OTLab_8
UV_PYTHON_INSTALL_DIR="$PWD/.python" \
  uv sync --locked --python 3.12
```

If the default uv cache location is not writable, use a temporary cache:

```bash
UV_CACHE_DIR="${TMPDIR:-/tmp}/otlab8-uv-cache" \
  UV_PYTHON_INSTALL_DIR="$PWD/.python" \
  uv sync --locked --python 3.12
```

Activation is optional because all scripts can call `.venv/bin/python` directly:

```bash
source .venv/bin/activate
```

## 4. Minimal Python dependency set

| Direct dependency | Verified version | Assignment use |
|---|---:|---|
| NumPy | 2.5.4 | Arrays, objectives, exact reference calculations |
| SciPy | 1.18.1 | Continuous optimization and built-in HiGHS MILP solver |
| matplotlib | 3.11.2 | Reproducible figures |
| scikit-learn | 1.9.1 | Small datasets and classical ML baselines |
| PyTorch | 2.15.0 | Autograd, tiny ML models, distributed/multi-task demonstrations |
| PennyLane | 0.45.1 | Local quantum circuits, gradients, noise, QAOA/VQE/QML |
| NetworkX | 3.7 | Small graph/Max-Cut instances |
| pytest | 9.2.0 | Correctness tests |
| pytest-cov | 7.1.0 | Coverage evidence and Track J instrumentation |

SciPy's bundled HiGHS backend replaces the proposed PuLP dependency for ILP. PennyLane replaces a larger Qiskit plus Aer installation. pandas, MPI, Jupyter, web frameworks, Docker, and GPU-specific packages were not installed because the current minimum implementation does not require them.

The lock contains required transitive packages such as `pennylane-lightning`, `coverage`, `rustworkx`, and PyTorch dependencies. Use `uv.lock` rather than manually reproducing that list.

Local environment sizes after installation:

- `.python/`: approximately 71 MB.
- `.venv/`: approximately 956 MB.

## 5. CPU and MPS policy

The PyTorch build reports that MPS support was compiled in, but `torch.backends.mps.is_available()` returned `False` in the verified environment. Therefore:

- CPU is the required and reproducible baseline for every experiment.
- No experiment may require MPS.
- MPS may be re-probed later, but it remains opt-in and results must not be mixed with CPU baselines without explicit labeling.
- CUDA packages are not applicable to this arm64 Mac and were not installed.

## 6. QEMU and RISC-V toolchain

The current Homebrew catalog exposes separate Apple Silicon formulae, so the installed command was:

```bash
HOMEBREW_NO_AUTO_UPDATE=1 \
HOMEBREW_NO_INSTALL_CLEANUP=1 \
  /opt/homebrew/bin/brew install qemu riscv64-elf-gcc
```

`riscv64-elf-gcc` pulls in `riscv64-elf-binutils`. Verified tools:

| Tool | Verified version |
|---|---:|
| `qemu-system-riscv64` | 11.1.1 |
| `riscv64-elf-gcc` | GCC 16.2.0 |
| `riscv64-elf-objdump` | GNU Binutils 2.47 |

For xv6 commands, explicitly use the detected prefix when needed:

```bash
make TOOLPREFIX=riscv64-elf- qemu
```

Track G pins MIT xv6-riscv commit
`fa2ddcb7ca87a77af579380a6eafd5aff163b44f`. The pristine source built and
booted with `CPUS=1`, and full `usertests` reported `ALL TESTS PASSED`. The
support-only comparison baseline and priority scheduler also passed the full
suite; links are in `report/track_g.md`.

### Homebrew side effect observed

The installation that was actually executed set `HOMEBREW_NO_AUTO_UPDATE=1` but did not set `HOMEBREW_NO_INSTALL_CLEANUP=1`. Homebrew automatically ran its post-install cleanup because cleanup had not run in 30 days. It removed an old `ca-certificates` Cellar version, cached bottles, Homebrew logs, and temporary Homebrew staging directories. No project data was removed. No explicit `brew cleanup` command was issued, and no further cleanup or restoration has been attempted.

All future documented install commands include `HOMEBREW_NO_INSTALL_CLEANUP=1` to prevent this behavior.

## 7. Verification scripts

Run the complete preflight from the repository root:

```bash
./scripts/preflight.sh
```

The shell wrapper keeps matplotlib/XDG caches inside the ignored project `.cache/` directory, runs the project interpreter, streams results, and writes `setup_logs/preflight-latest.txt`.

The underlying Python verifier is:

```bash
.venv/bin/python scripts/verify_environment.py
```

It tests actual operations rather than imports alone:

1. NumPy linear algebra and SciPy BFGS minimization.
2. PyTorch CPU tensors and autograd; MPS is reported separately.
3. A binary ILP solved by SciPy/HiGHS.
4. PennyLane Bell-state and mixed-state noise circuit execution.
5. SQLite in-memory queries and `EXPLAIN QUERY PLAN`.
6. Two-worker macOS spawn-based multiprocessing.
7. QEMU RISC-V `virt`-machine discovery plus an actual RV64 compile and disassembly using RISC-V GCC and objdump.

## 8. Recorded final preflight output

The final run is stored at `setup_logs/preflight-latest.txt` and reported:

```text
[PASS] 1. Numerical optimization libraries
[PASS] 2. PyTorch tensor operations and autograd
[PASS] 3. ILP solver availability
[PASS] 4. Quantum circuit execution
[PASS] 5. SQLite
[PASS] 6. Multiprocessing
[PASS] 7. QEMU and RISC-V tools
Summary: 7/7 checks passed
```

Key measured values from that run:

- Python 3.12.13, arm64, 10 logical CPUs.
- NumPy 2.5.4 and SciPy 1.18.1 returned zero linear residual and a near-zero test objective.
- PyTorch 2.15.0 returned the expected gradient `[2.0, 4.0, 6.0]` on CPU.
- SciPy/HiGHS returned the expected binary solution `[1, 0]`, objective `3.0`.
- PennyLane returned Bell probabilities approximately `[0.5, 0, 0, 0.5]` and the expected noisy value `-0.5`.
- SQLite 3.53.1 executed both a query and an explain plan.
- Multiprocessing returned `[1, 4, 9, 16]` using the macOS `spawn` method.
- QEMU reported the RISC-V `virt` machine, and GCC/objdump successfully compiled and disassembled a temporary RV64 object.

The earlier pre-native-tools run is retained at `setup_logs/preflight-before-native.txt`; it passed 6/7 and correctly reported QEMU, RISC-V GCC, and objdump as missing. Its contents were reconstructed verbatim from the captured tool output because two cache-fix retries briefly interleaved writes to the original file; the log carries that provenance note.

## 9. Unresolved items and honest limitations

- **xv6 validated for Track G's pinned revision:** pristine, support-baseline,
  optimized, and fresh-patch boot evidence is archived. This does not imply
  compatibility with future upstream revisions.
- **MPS unavailable:** CPU works and is the supported baseline. This is not a blocker for the planned toy-scale experiments.
- **Timing stability:** laptop power state and background tasks can affect benchmarks. Experiments must use warm-ups, repeated runs, variability, and consistent power/background conditions.
- **Exact Chapter 6 syllabus missing:** this blocks final method coverage, not environment readiness.
- **Real quantum hardware not configured:** the assignment permits an applicable hardware-noise model when access allows; the local PennyLane mixed-state backend passed.

The setup is **preflight-complete and xv6-validated for the pinned Track G
revision**. The assignment remains incomplete while Tracks H-J and the exact
Chapter 6 syllabus audit remain open.
