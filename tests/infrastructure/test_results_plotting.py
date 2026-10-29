from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from optlab.common.plotting import plot_metric
from optlab.common.results import write_csv, write_json


def test_json_and_csv_exports(tmp_path: Path) -> None:
    rows = [
        {"algorithm": "a", "seed": 1, "objective": 2.0},
        {"algorithm": "b", "seed": 2, "objective": 1.0},
    ]
    json_path = write_json(tmp_path / "nested" / "result.json", rows)
    csv_path = write_csv(tmp_path / "nested" / "result.csv", rows)
    assert json.loads(json_path.read_text()) == rows
    with csv_path.open(newline="") as stream:
        exported = list(csv.DictReader(stream))
    assert exported[0]["algorithm"] == "a"
    assert exported[1]["objective"] == "1.0"
    assert not list((tmp_path / "nested").glob("*.tmp"))


def test_csv_rejects_mismatched_fields(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="identical fields"):
        write_csv(tmp_path / "bad.csv", [{"a": 1}, {"b": 2}])


def test_plot_generation_is_headless(tmp_path: Path) -> None:
    rows = [
        {"iteration": 0, "objective": 3.0, "algorithm": "one"},
        {"iteration": 1, "objective": 2.0, "algorithm": "one"},
        {"iteration": 0, "objective": 4.0, "algorithm": "two"},
        {"iteration": 1, "objective": 1.5, "algorithm": "two"},
    ]
    target = plot_metric(
        rows,
        x_key="iteration",
        y_key="objective",
        group_key="algorithm",
        title="Infrastructure test",
        output_path=tmp_path / "plot.png",
    )
    assert target.is_file()
    assert target.stat().st_size > 1000
