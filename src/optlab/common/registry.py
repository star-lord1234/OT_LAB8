"""Load and validate the A-J experiment registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TrackSpec:
    track_id: str
    name: str
    status: str
    directory: Path
    config: Path
    implementation: Path
    benchmark: Path
    tests: Path
    results: Path
    report_section: str
    entrypoint: str | None
    dependencies: tuple[str, ...]


def load_registry(path: str | Path) -> dict[str, TrackSpec]:
    registry_path = Path(path).resolve()
    with registry_path.open(encoding="utf-8") as stream:
        document: dict[str, Any] = json.load(stream)
    root = registry_path.parent.parent
    raw_tracks = document.get("tracks")
    if not isinstance(raw_tracks, list):
        raise ValueError("registry must contain a tracks list")

    tracks: dict[str, TrackSpec] = {}
    for item in raw_tracks:
        track_id = str(item["id"]).upper()
        if track_id in tracks or track_id not in tuple("ABCDEFGHIJ"):
            raise ValueError(f"invalid or duplicate track id: {track_id}")
        tracks[track_id] = TrackSpec(
            track_id=track_id,
            name=str(item["name"]),
            status=str(item["status"]),
            directory=(root / item["directory"]).resolve(),
            config=(root / item["config"]).resolve(),
            implementation=(root / item["implementation"]).resolve(),
            benchmark=(root / item["benchmark"]).resolve(),
            tests=(root / item["tests"]).resolve(),
            results=(root / item["results"]).resolve(),
            report_section=str(item["report_section"]),
            entrypoint=item.get("entrypoint"),
            dependencies=tuple(item.get("dependencies", [])),
        )
    if set(tracks) != set("ABCDEFGHIJ"):
        raise ValueError("registry must define every track A-J exactly once")
    return tracks


def validate_registry_paths(tracks: dict[str, TrackSpec]) -> list[str]:
    problems: list[str] = []
    for track in tracks.values():
        for label, path in (
            ("directory", track.directory),
            ("config", track.config),
            ("implementation", track.implementation),
            ("benchmark", track.benchmark),
            ("tests", track.tests),
            ("results", track.results),
        ):
            if not path.exists():
                problems.append(f"Track {track.track_id} missing {label}: {path}")
    return problems
