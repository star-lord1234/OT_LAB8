"""Atomic JSON and CSV result export."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


def _mapping(value: Any) -> dict[str, Any]:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError("result rows must be mappings or dataclass instances")


def _atomic_text_write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    return path


def write_json(path: str | Path, value: Any) -> Path:
    target = Path(path)
    content = json.dumps(value, indent=2, sort_keys=True, default=str) + "\n"
    return _atomic_text_write(target, content)


def write_csv(path: str | Path, rows: Iterable[Any]) -> Path:
    mappings = [_mapping(row) for row in rows]
    if not mappings:
        raise ValueError("at least one row is required")
    fieldnames = list(mappings[0])
    if any(set(row) != set(fieldnames) for row in mappings):
        raise ValueError("all CSV rows must have identical fields")

    import io

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(mappings)
    return _atomic_text_write(Path(path), buffer.getvalue())
