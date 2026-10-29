"""Environment metadata capture without hardware identifiers or secrets."""

from __future__ import annotations

import importlib.metadata as metadata
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_PACKAGES = (
    "numpy",
    "scipy",
    "matplotlib",
    "scikit-learn",
    "torch",
    "pennylane",
    "networkx",
)


def _command(*arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            arguments,
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip() or completed.stderr.strip() or None


def _safe_hardware() -> dict[str, str]:
    values: dict[str, str] = {}
    output = _command("system_profiler", "SPHardwareDataType")
    if not output:
        return values
    allowed = {"Model Name", "Model Identifier", "Chip", "Total Number of Cores", "Memory"}
    for raw_line in output.splitlines():
        if ":" not in raw_line:
            continue
        key, value = (part.strip() for part in raw_line.split(":", 1))
        if key in allowed:
            values[key.lower().replace(" ", "_")] = value
    return values


def _git_metadata(project_root: Path) -> dict[str, Any]:
    commit = _command("git", "-C", str(project_root), "rev-parse", "HEAD")
    status = _command("git", "-C", str(project_root), "status", "--porcelain")
    return {"commit": commit, "dirty": bool(status) if commit else None}


def collect_environment_metadata(
    project_root: str | Path,
    *,
    package_names: tuple[str, ...] = DEFAULT_PACKAGES,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    disk = shutil.disk_usage(root)
    packages: dict[str, str | None] = {}
    for name in package_names:
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = None

    return {
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
            "implementation": platform.python_implementation(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "mac_version": platform.mac_ver()[0],
            "logical_cpus": os.cpu_count(),
        },
        "hardware": _safe_hardware(),
        "disk": {
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
        },
        "packages": packages,
        "tools": {
            "git": _command("git", "--version"),
            "qemu_riscv64": _command("qemu-system-riscv64", "--version"),
            "riscv64_elf_gcc": _command("riscv64-elf-gcc", "--version"),
        },
        "git": _git_metadata(root),
    }
