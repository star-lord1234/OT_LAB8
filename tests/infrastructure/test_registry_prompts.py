from __future__ import annotations

import json
from pathlib import Path

from optlab.common.prompts import validate_prompt_record
from optlab.common.registry import load_registry, validate_registry_paths


ROOT = Path(__file__).resolve().parents[2]


def test_registry_defines_all_tracks_and_existing_locations() -> None:
    tracks = load_registry(ROOT / "experiments" / "registry.json")
    assert tuple(tracks) == tuple("ABCDEFGHIJ")
    assert validate_registry_paths(tracks) == []
    assert tracks["C"].dependencies == ("B",)
    assert tracks["I"].dependencies == ("C", "D")
    assert tracks["A"].status == "implemented"
    assert tracks["A"].entrypoint == "tracks.A_continuous.benchmarks.run:main"
    assert tracks["B"].status == "implemented"
    assert tracks["B"].entrypoint == "tracks.B_discrete.benchmarks.run:main"
    assert tracks["C"].status == "implemented"
    assert tracks["C"].entrypoint == "tracks.C_quantum_optimization.benchmarks.run:main"
    assert tracks["D"].status == "implemented"
    assert tracks["D"].entrypoint == "tracks.D_parallel_distributed.benchmarks.run:main"
    assert tracks["E"].status == "implemented"
    assert tracks["E"].entrypoint == "tracks.E_case_study.benchmarks.run:main"
    assert tracks["F"].status == "implemented"
    assert tracks["F"].entrypoint == "tracks.F_compiler.benchmarks.run:main"
    assert tracks["G"].status == "implemented"
    assert tracks["G"].entrypoint == "tracks.G_xv6.benchmarks.run:main"
    assert tracks["H"].status == "implemented"
    assert tracks["H"].entrypoint == "tracks.H_dbms.benchmarks.run:main"
    assert all(tracks[track_id].status == "scaffolded" for track_id in "IJ")


def test_prompt_record_validation(tmp_path: Path) -> None:
    for name in ("prompt.md", "response.md", "verification.md"):
        (tmp_path / name).write_text(name, encoding="utf-8")
    record = {
        "record_id": "example",
        "date": "2026-10-29",
        "tool": "Example tool",
        "model": "Example model",
        "scope": "cross-track",
        "purpose": "schema test",
        "prompt_file": "prompt.md",
        "response_file": "response.md",
        "verification_file": "verification.md",
        "commit": None,
        "revisions": [],
    }
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    assert validate_prompt_record(path) == []


def test_prompt_record_reports_missing_evidence(tmp_path: Path) -> None:
    record = {
        "record_id": "example",
        "date": "2026-10-29",
        "tool": "Example tool",
        "model": "Example model",
        "scope": "cross-track",
        "purpose": "schema test",
        "prompt_file": "missing.md",
        "response_file": "missing-response.md",
        "verification_file": "missing-verification.md",
        "commit": None,
        "revisions": [],
    }
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    assert len(validate_prompt_record(path)) == 3
