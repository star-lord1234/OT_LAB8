#!/usr/bin/env python3
"""Verify the project-local Python stack and required native tools.

This script is deliberately small and deterministic. It tests capabilities the
assignment will use; it does not benchmark machine performance or install
anything.
"""

from __future__ import annotations

import math
import multiprocessing as mp
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from collections.abc import Callable
from pathlib import Path


CHECKS: list[tuple[str, Callable[[], str]]] = []


def check(name: str) -> Callable[[Callable[[], str]], Callable[[], str]]:
    def register(function: Callable[[], str]) -> Callable[[], str]:
        CHECKS.append((name, function))
        return function

    return register


def run_version(executable: str) -> str:
    completed = subprocess.run(
        [executable, "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    output = completed.stdout.strip() or completed.stderr.strip()
    return output.splitlines()[0]


def square(value: int) -> int:
    """Top-level worker so macOS's spawn start method can pickle it."""

    return value * value


@check("1. Numerical optimization libraries")
def verify_numerical() -> str:
    import numpy as np
    import scipy
    from scipy.optimize import minimize

    matrix = np.array([[3.0, 1.0], [1.0, 2.0]])
    target = np.array([9.0, 8.0])
    solution = np.linalg.solve(matrix, target)
    if not np.allclose(matrix @ solution, target, atol=1e-10):
        raise AssertionError("NumPy linear solve failed its residual check")

    result = minimize(
        lambda x: float((x[0] - 1.5) ** 2 + 2.0 * (x[1] + 0.5) ** 2),
        x0=np.array([4.0, 3.0]),
        method="BFGS",
    )
    expected = np.array([1.5, -0.5])
    if not result.success or not np.allclose(result.x, expected, atol=1e-5):
        raise AssertionError(f"SciPy minimization failed: {result.message}")

    return (
        f"numpy={np.__version__}, scipy={scipy.__version__}, "
        f"linear_residual={np.linalg.norm(matrix @ solution - target):.3e}, "
        f"optimizer_objective={result.fun:.3e}"
    )


@check("2. PyTorch tensor operations and autograd")
def verify_torch() -> str:
    import torch

    x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
    loss = (x.square()).sum()
    loss.backward()
    expected = torch.tensor([2.0, 4.0, 6.0])
    if x.grad is None or not torch.allclose(x.grad, expected):
        raise AssertionError(f"Unexpected autograd result: {x.grad}")

    mps_built = torch.backends.mps.is_built()
    mps_available = torch.backends.mps.is_available()
    mps_note = "not used; CPU is the required baseline"
    if mps_available:
        probe = torch.arange(4, dtype=torch.float32, device="mps")
        if not torch.allclose(probe.cpu() * 2, torch.tensor([0.0, 2.0, 4.0, 6.0])):
            raise AssertionError("MPS tensor probe returned an unexpected value")
        mps_note = "basic tensor probe passed; use remains opt-in per experiment"

    return (
        f"torch={torch.__version__}, cpu_autograd_gradient={x.grad.tolist()}, "
        f"mps_built={mps_built}, mps_available={mps_available}, {mps_note}"
    )


@check("3. ILP solver availability")
def verify_ilp() -> str:
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp

    # Maximize 3x + 2y subject to 2x + y <= 2, x/y binary.
    result = milp(
        c=np.array([-3.0, -2.0]),
        integrality=np.ones(2),
        bounds=Bounds(np.zeros(2), np.ones(2)),
        constraints=LinearConstraint(np.array([[2.0, 1.0]]), -np.inf, 2.0),
        options={"time_limit": 10.0},
    )
    if not result.success or result.x is None:
        raise AssertionError(f"SciPy/HiGHS MILP failed: {result.message}")
    rounded = np.rint(result.x).astype(int)
    if rounded.tolist() != [1, 0] or not math.isclose(-result.fun, 3.0):
        raise AssertionError(f"Unexpected MILP solution: x={result.x}, objective={-result.fun}")

    return f"solver=SciPy HiGHS MILP, solution={rounded.tolist()}, objective={-result.fun:.1f}"


@check("4. Quantum circuit execution")
def verify_quantum() -> str:
    import numpy as np
    import pennylane as qml

    statevector_device = qml.device("default.qubit", wires=2, shots=None)

    @qml.qnode(statevector_device)
    def bell_state() -> np.ndarray:
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.probs(wires=[0, 1])

    probabilities = np.asarray(bell_state(), dtype=float)
    expected = np.array([0.5, 0.0, 0.0, 0.5])
    if not np.allclose(probabilities, expected, atol=1e-8):
        raise AssertionError(f"Unexpected Bell-state probabilities: {probabilities}")

    mixed_device = qml.device("default.mixed", wires=1, shots=None)

    @qml.qnode(mixed_device)
    def noisy_probe() -> float:
        qml.PauliX(wires=0)
        qml.BitFlip(0.25, wires=0)
        return qml.expval(qml.PauliZ(0))

    noisy_value = float(noisy_probe())
    if not math.isclose(noisy_value, -0.5, abs_tol=1e-8):
        raise AssertionError(f"Unexpected mixed-state noise result: {noisy_value}")

    return (
        f"pennylane={qml.__version__}, bell_probs={probabilities.tolist()}, "
        f"default.mixed_bitflip_expectation={noisy_value:.3f}"
    )


@check("5. SQLite")
def verify_sqlite() -> str:
    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE values_table (value INTEGER NOT NULL)")
        connection.executemany(
            "INSERT INTO values_table(value) VALUES (?)", [(1,), (2,), (3,)]
        )
        total = connection.execute("SELECT SUM(value) FROM values_table").fetchone()[0]
        plan = connection.execute(
            "EXPLAIN QUERY PLAN SELECT * FROM values_table WHERE value = 2"
        ).fetchall()
    if total != 6 or not plan:
        raise AssertionError("SQLite query or EXPLAIN QUERY PLAN failed")
    return f"sqlite={sqlite3.sqlite_version}, in_memory_sum={total}, plan_rows={len(plan)}"


@check("6. Multiprocessing")
def verify_multiprocessing() -> str:
    context = mp.get_context("spawn")
    with context.Pool(processes=2) as pool:
        values = pool.map(square, [1, 2, 3, 4])
    if values != [1, 4, 9, 16]:
        raise AssertionError(f"Unexpected multiprocessing output: {values}")
    return f"start_method=spawn, workers=2, output={values}"


@check("7. QEMU and RISC-V tools")
def verify_native_tools() -> str:
    qemu = shutil.which("qemu-system-riscv64")
    compiler = next(
        (
            path
            for name in (
                "riscv64-unknown-elf-gcc",
                "riscv64-elf-gcc",
                "riscv64-linux-gnu-gcc",
            )
            if (path := shutil.which(name)) is not None
        ),
        None,
    )
    objdump = next(
        (
            path
            for name in (
                "riscv64-unknown-elf-objdump",
                "riscv64-elf-objdump",
                "riscv64-linux-gnu-objdump",
            )
            if (path := shutil.which(name)) is not None
        ),
        None,
    )
    missing = [
        label
        for label, value in (
            ("qemu-system-riscv64", qemu),
            ("RISC-V GCC", compiler),
            ("RISC-V objdump", objdump),
        )
        if value is None
    ]
    if missing:
        raise RuntimeError("Missing native tools: " + ", ".join(missing))

    machine_help = subprocess.run(
        [qemu, "-machine", "help"],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    ).stdout
    if "virt" not in machine_help:
        raise AssertionError("QEMU RISC-V machine list does not contain the virt machine")

    with tempfile.TemporaryDirectory(prefix="otlab8-riscv-") as directory:
        source_path = Path(directory) / "probe.c"
        object_path = Path(directory) / "probe.o"
        source_path.write_text("int answer(void) { return 42; }\n", encoding="utf-8")
        subprocess.run(
            [
                compiler,
                "-march=rv64gc",
                "-mabi=lp64d",
                "-c",
                str(source_path),
                "-o",
                str(object_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        disassembly = subprocess.run(
            [objdump, "-d", str(object_path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        ).stdout
        if "<answer>" not in disassembly:
            raise AssertionError("RISC-V objdump did not find the compiled answer symbol")

    return (
        f"qemu={run_version(qemu)}, compiler={run_version(compiler)}, "
        f"objdump={run_version(objdump)}, qemu_virt_machine=yes, "
        "rv64_compile_and_disassemble=yes"
    )


def main() -> int:
    print("Assignment 8 environment verification")
    print(f"python={sys.version.split()[0]}")
    print(f"executable={sys.executable}")
    print(f"platform={platform.platform()}")
    print(f"architecture={platform.machine()}")
    print(f"logical_cpus={os.cpu_count()}")
    print()

    failures = 0
    for name, function in CHECKS:
        try:
            detail = function()
        except Exception as error:  # noqa: BLE001 - preflight must report all failures
            failures += 1
            print(f"[FAIL] {name}")
            print(f"       {type(error).__name__}: {error}")
            if os.environ.get("OTLAB_PREFLIGHT_TRACEBACK") == "1":
                traceback.print_exc()
        else:
            print(f"[PASS] {name}")
            print(f"       {detail}")

    print()
    print(f"Summary: {len(CHECKS) - failures}/{len(CHECKS)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
