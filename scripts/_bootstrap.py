"""Re-execute project CLIs with the isolated interpreter when necessary."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def ensure_project_python(root: Path) -> None:
    environment = (root / ".venv").resolve()
    expected = root / ".venv" / "bin" / "python"
    if Path(sys.prefix).resolve() == environment:
        return
    if not expected.is_file():
        raise SystemExit(f"Project Python is missing at {expected}; follow SETUP.md first.")
    os.execv(str(expected), [str(expected), *sys.argv])
