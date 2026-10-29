from __future__ import annotations

import subprocess
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


def test_unimplemented_track_refuses_to_claim_run() -> None:
    completed = subprocess.run(
        [str(ROOT / "scripts" / "run_track.py"), "B"],
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
