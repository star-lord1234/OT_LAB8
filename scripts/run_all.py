#!/usr/bin/env python3
"""Run every implemented track in dependency-aware registry order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
from _bootstrap import ensure_project_python

ensure_project_python(ROOT)
sys.path.insert(0, str(ROOT / "src"))

from optlab.common.registry import load_registry  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plans", action="store_true", help="Print all track plans")
    arguments = parser.parse_args()

    registry = load_registry(ROOT / "experiments" / "registry.json")
    if arguments.plans:
        for track_id in registry:
            subprocess.run(
                [str(ROOT / "scripts" / "run_track.py"), track_id, "--plan"],
                check=True,
            )
        return 0

    implemented = [track for track in registry.values() if track.status == "implemented"]
    if not implemented:
        print("No tracks are marked implemented; nothing was run.")
        return 0

    for track in implemented:
        completed = subprocess.run(
            [str(ROOT / "scripts" / "run_track.py"), track.track_id], check=False
        )
        if completed.returncode:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
