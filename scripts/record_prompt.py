#!/usr/bin/env python3
"""Create an honest prompt-record skeleton from supplied text files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
from _bootstrap import ensure_project_python

ensure_project_python(ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record_id", help="Lowercase identifier, for example 2026-10-29-a-gd")
    parser.add_argument("--scope", required=True, help="A-J or cross-track")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    arguments = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", arguments.record_id):
        parser.error("record_id must contain lowercase letters, digits, and hyphens")
    scope = arguments.scope.upper() if len(arguments.scope) == 1 else "_cross_track"
    if scope not in {*tuple("ABCDEFGHIJ"), "_cross_track"}:
        parser.error("scope must be A-J or cross-track")
    if not arguments.prompt_file.is_file():
        parser.error("prompt file does not exist")

    destination = ROOT / "prompts" / scope / arguments.record_id
    if destination.exists():
        parser.error(f"record already exists: {destination}")
    destination.mkdir(parents=True)
    (destination / "prompt.md").write_text(
        arguments.prompt_file.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (destination / "response.md").write_text(
        "# Relevant AI response excerpt\n\nPending: paste the actual response or relevant excerpt.\n",
        encoding="utf-8",
    )
    (destination / "verification.md").write_text(
        "# Verification\n\nPending: record commands, results, corrections, and commit URL/hash.\n",
        encoding="utf-8",
    )
    record = {
        "record_id": arguments.record_id,
        "date": date.today().isoformat(),
        "tool": arguments.tool,
        "model": arguments.model,
        "scope": arguments.scope,
        "purpose": arguments.purpose,
        "prompt_file": "prompt.md",
        "response_file": "response.md",
        "verification_file": "verification.md",
        "commit": None,
        "revisions": [],
    }
    (destination / "record.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
