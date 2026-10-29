# Dependency Rationale and Reproduction

`pyproject.toml` contains direct dependency ranges; `uv.lock` contains the exact resolved environment. `SETUP.md` records the measured Mac and installed native tools.

## Direct Python dependencies

| Dependency | Why it is required | Replaces/avoids |
|---|---|---|
| NumPy | Arrays, deterministic fixtures, exact references | Repeated custom numeric code |
| SciPy | Continuous methods and HiGHS MILP | Separate PuLP/CBC installation |
| matplotlib | Static plots | Web/dashboard stack |
| scikit-learn | Small classical baselines and datasets | Large datasets/frameworks |
| PyTorch | Autograd and tiny multi-task/distributed models | GPU-only frameworks |
| PennyLane | Circuits, gradients, noise, QAOA/VQE/QML | Separate Qiskit and Aer stack |
| NetworkX | Small graph fixtures | Custom graph framework |
| pytest / pytest-cov | Verification and Track J coverage | Ad hoc test scripts |

Not installed: pandas, Jupyter, MPI, Docker, web frameworks, CUDA, paid APIs, or cloud SDKs. Add a dependency only when a traced requirement and failing test justify it, then update both `pyproject.toml` and `uv.lock`.

Recreate exactly:

```bash
UV_PYTHON_INSTALL_DIR="$PWD/.python" uv sync --locked --python 3.12
```

Verify the lock without network access when the uv cache is available:

```bash
uv lock --check --offline
```

Native tools required for xv6 are QEMU and the `riscv64-elf-` GCC/binutils toolchain. Their approved install command and observed side effects are documented in `SETUP.md`.
