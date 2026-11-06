from __future__ import annotations

import subprocess
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_track_plan_command() -> None:
    completed = subprocess.run(
        [str(ROOT / "scripts" / "run_track.py"), "A", "--plan"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Track A: Continuous optimization" in completed.stdout
    assert "status: implemented" in completed.stdout


def test_scaffolded_registry_entry_refuses_to_claim_run(tmp_path: Path) -> None:
    registry = json.loads((ROOT / "experiments" / "registry.json").read_text())
    for track in registry["tracks"]:
        for key in ("directory", "config", "implementation", "benchmark", "tests", "results"):
            track[key] = str((ROOT / track[key]).resolve())
    track_j = next(track for track in registry["tracks"] if track["id"] == "J")
    track_j["status"] = "scaffolded"
    track_j["entrypoint"] = None
    temporary_registry = tmp_path / "registry.json"
    temporary_registry.write_text(json.dumps(registry), encoding="utf-8")
    completed = subprocess.run(
        [str(ROOT / "scripts" / "run_track.py"), "J", "--registry", str(temporary_registry)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    assert "no experiment was run" in completed.stderr


def test_preflight_lock_prevents_interleaved_log(tmp_path: Path) -> None:
    log_path = tmp_path / "preflight.txt"
    lock_path = Path(f"{log_path}.lock")
    lock_path.mkdir()
    completed = subprocess.run(
        [str(ROOT / "scripts" / "preflight.sh"), str(log_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    assert "Another preflight" in completed.stderr
