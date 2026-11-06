"""Load the five fixed representative toy-language programs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


SAMPLES = Path(__file__).resolve().parents[1] / "samples"


@dataclass(frozen=True)
class ProgramSpec:
    name: str
    source: str
    inputs: dict[str, int]
    expected: tuple[int, ...]


def load_programs() -> list[ProgramSpec]:
    records = json.loads((SAMPLES / "manifest.json").read_text(encoding="utf-8"))
    return [
        ProgramSpec(
            name=record["name"],
            source=(SAMPLES / record["file"]).read_text(encoding="utf-8"),
            inputs={str(key): int(value) for key, value in record["inputs"].items()},
            expected=tuple(int(value) for value in record["expected"]),
        )
        for record in records
    ]
