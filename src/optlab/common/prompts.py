"""Validation for honest AI prompt/revision records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "record_id",
    "date",
    "tool",
    "model",
    "scope",
    "purpose",
    "prompt_file",
    "response_file",
    "verification_file",
    "commit",
)


@dataclass(frozen=True)
class PromptRecord:
    record_id: str
    date: str
    tool: str
    model: str
    scope: str
    purpose: str
    prompt_file: str
    response_file: str
    verification_file: str
    commit: str | None
    revisions: tuple[dict[str, Any], ...]


def load_prompt_record(path: str | Path) -> PromptRecord:
    record_path = Path(path)
    with record_path.open(encoding="utf-8") as stream:
        document = json.load(stream)
    missing = [field for field in REQUIRED_FIELDS if field not in document]
    if missing:
        raise ValueError(f"prompt record missing fields: {', '.join(missing)}")
    return PromptRecord(
        record_id=str(document["record_id"]),
        date=str(document["date"]),
        tool=str(document["tool"]),
        model=str(document["model"]),
        scope=str(document["scope"]),
        purpose=str(document["purpose"]),
        prompt_file=str(document["prompt_file"]),
        response_file=str(document["response_file"]),
        verification_file=str(document["verification_file"]),
        commit=document["commit"],
        revisions=tuple(document.get("revisions", [])),
    )


def validate_prompt_record(path: str | Path) -> list[str]:
    record_path = Path(path).resolve()
    record = load_prompt_record(record_path)
    problems: list[str] = []
    if not record.tool.strip() or not record.model.strip():
        problems.append("tool and model must be recorded")
    if not record.purpose.strip():
        problems.append("purpose must be recorded")
    for label, relative in (
        ("prompt", record.prompt_file),
        ("response", record.response_file),
        ("verification", record.verification_file),
    ):
        if not (record_path.parent / relative).is_file():
            problems.append(f"missing {label} file: {relative}")
    return problems
