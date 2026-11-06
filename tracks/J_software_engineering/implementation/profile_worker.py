"""Run a real pytest suite under coverage contexts in an isolated process."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import coverage
import pytest


class ContextPlugin:
    def __init__(self, coverage_session: coverage.Coverage) -> None:
        self.coverage = coverage_session
        self.test_order: list[str] = []
        self.durations: defaultdict[str, float] = defaultdict(float)
        self.outcomes: dict[str, str] = {}

    def pytest_runtest_setup(self, item) -> None:
        nodeid = str(item.nodeid)
        self.coverage.switch_context(nodeid)
        if nodeid not in self.test_order:
            self.test_order.append(nodeid)

    def pytest_runtest_logreport(self, report) -> None:
        nodeid = str(report.nodeid)
        self.durations[nodeid] += float(report.duration)
        if report.when == "call":
            self.outcomes[nodeid] = str(report.outcome)


def run_profile(project: Path, nodes: list[str], output: Path) -> int:
    project = project.resolve()
    source = project / "more_itertools"
    if not source.is_dir():
        raise FileNotFoundError(f"missing more_itertools source at {source}")
    os.chdir(project)
    sys.path.insert(0, str(project))
    data_file = output.with_suffix(".coverage")
    session = coverage.Coverage(source=[str(source)], data_file=str(data_file))
    plugin = ContextPlugin(session)
    arguments = [*(nodes or ["tests"]), "-q", "--disable-warnings", "--rootdir=."]
    started = time.perf_counter()
    session.start()
    exit_code = int(pytest.main(arguments, plugins=[plugin]))
    session.stop()
    session.save()
    wall_time = time.perf_counter() - started

    data = session.get_data()
    context_lines: defaultdict[str, set[str]] = defaultdict(set)
    all_lines: set[str] = set()
    total_statements = 0
    measured_files = []
    for filename in sorted(data.measured_files()):
        path = Path(filename).resolve()
        if source not in path.parents and path != source:
            continue
        relative = str(path.relative_to(project))
        measured_files.append(relative)
        statements = set(session.analysis2(str(path))[1])
        total_statements += len(statements)
        line_contexts = data.contexts_by_lineno(str(path))
        for line, contexts in line_contexts.items():
            if line not in statements:
                continue
            line_id = f"{relative}:{line}"
            all_lines.add(line_id)
            for context in contexts:
                if context:
                    context_lines[context].add(line_id)
    document = {
        "exit_code": exit_code,
        "wall_time_seconds": wall_time,
        "test_order": plugin.test_order,
        "durations_seconds": dict(plugin.durations),
        "outcomes": plugin.outcomes,
        "context_lines": {key: sorted(value) for key, value in sorted(context_lines.items())},
        "overall_covered_lines": len(all_lines),
        "total_statements": total_statements,
        "source_coverage_percent": 100.0 * len(all_lines) / total_statements if total_statements else 0.0,
        "measured_files": measured_files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        data_file.unlink()
    except FileNotFoundError:
        pass
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--node", action="append", default=[])
    arguments = parser.parse_args()
    return run_profile(arguments.project, arguments.node, arguments.output)


if __name__ == "__main__":
    raise SystemExit(main())
