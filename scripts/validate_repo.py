#!/usr/bin/env python3
"""Validate repository structure, registry, and prompt-log records."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
from _bootstrap import ensure_project_python

ensure_project_python(ROOT)
sys.path.insert(0, str(ROOT / "src"))

from optlab.common.prompts import validate_prompt_record  # noqa: E402
from optlab.common.registry import load_registry, validate_registry_paths  # noqa: E402


def main() -> int:
    problems: list[str] = []
    tracks = load_registry(ROOT / "experiments" / "registry.json")
    problems.extend(validate_registry_paths(tracks))

    for track_id in tracks:
        prompt_dir = ROOT / "prompts" / track_id
        if not prompt_dir.is_dir():
            problems.append(f"missing prompt directory: {prompt_dir}")

    for record in (ROOT / "prompts").glob("**/record.json"):
        problems.extend(f"{record}: {problem}" for problem in validate_prompt_record(record))

    for required in (
        ROOT / "logs" / "ai_tools_register.csv",
        ROOT / "logs" / "failures.md",
        ROOT / "logs" / "tool_comparison.md",
        ROOT / "coverage_matrix.csv",
    ):
        if not required.is_file():
            problems.append(f"missing required artifact: {required}")

    if problems:
        print("Repository validation failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print(f"Repository validation passed: {len(tracks)} tracks and prompt records are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
