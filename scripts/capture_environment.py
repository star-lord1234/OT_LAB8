#!/usr/bin/env python3
"""Capture privacy-safe environment metadata as JSON."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
from _bootstrap import ensure_project_python

ensure_project_python(ROOT)
sys.path.insert(0, str(ROOT / "src"))

from optlab.common.environment import collect_environment_metadata  # noqa: E402
from optlab.common.results import write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", default=str(ROOT / "results" / "environment.json")
    )
    arguments = parser.parse_args()
    target = write_json(arguments.output, collect_environment_metadata(ROOT))
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
