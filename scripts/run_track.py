#!/usr/bin/env python3
"""Inspect or run one registered track without pretending scaffolds are complete."""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
from _bootstrap import ensure_project_python

ensure_project_python(ROOT)
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from optlab.common.registry import load_registry, validate_registry_paths  # noqa: E402


def print_plan(track: object) -> None:
    print(f"Track {track.track_id}: {track.name}")
    print(f"status: {track.status}")
    print(f"implementation: {track.implementation}")
    print(f"benchmark: {track.benchmark}")
    print(f"tests: {track.tests}")
    print(f"results: {track.results}")
    print(f"config: {track.config}")
    print(f"report: {track.report_section}")
    print(f"dependencies: {', '.join(track.dependencies) if track.dependencies else 'none'}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("track", nargs="?", help="Track letter A-J")
    parser.add_argument("--plan", action="store_true", help="Show paths and status only")
    parser.add_argument("--list", action="store_true", help="List all registered tracks")
    parser.add_argument(
        "--registry", default=str(ROOT / "experiments" / "registry.json")
    )
    arguments = parser.parse_args()

    registry = load_registry(arguments.registry)
    problems = validate_registry_paths(registry)
    if problems:
        print("Registry path validation failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    if arguments.list:
        for track in registry.values():
            print(f"{track.track_id}\t{track.status}\t{track.name}")
        return 0

    if not arguments.track:
        parser.error("provide a track letter or use --list")
    track_id = arguments.track.upper()
    if track_id not in registry:
        parser.error("track must be one of A-J")
    track = registry[track_id]
    print_plan(track)

    if arguments.plan:
        return 0
    if track.status != "implemented" or not track.entrypoint:
        print(
            "Track is scaffolded but not implemented; no experiment was run. "
            "Use --plan to inspect it.",
            file=sys.stderr,
        )
        return 2

    module_name, function_name = track.entrypoint.split(":", 1)
    function = getattr(importlib.import_module(module_name), function_name)
    return int(function(track.config) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
