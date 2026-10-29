"""Small TOML experiment configuration with explicit validation."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .seeds import spawned_seeds, validate_seed


VALID_TRACKS = tuple("ABCDEFGHIJ")


@dataclass(frozen=True)
class ExperimentConfig:
    track: str
    experiment: str
    repeats: int
    base_seed: int
    seeds: tuple[int, ...]
    output_dir: Path
    parameters: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(
        cls, mapping: dict[str, Any], *, base_dir: Path | None = None
    ) -> "ExperimentConfig":
        track = str(mapping.get("track", "")).upper()
        if track not in VALID_TRACKS:
            raise ValueError(f"track must be one of {VALID_TRACKS}, got {track!r}")

        experiment = str(mapping.get("experiment", "")).strip()
        if not experiment:
            raise ValueError("experiment must be a non-empty string")

        repeats = mapping.get("repeats", 3)
        if isinstance(repeats, bool) or not isinstance(repeats, int) or repeats < 1:
            raise ValueError("repeats must be a positive integer")

        base_seed = validate_seed(mapping.get("base_seed", 20261029))
        raw_seeds = mapping.get("seeds")
        if raw_seeds is None:
            seeds = spawned_seeds(base_seed, repeats)
        else:
            if not isinstance(raw_seeds, list) or len(raw_seeds) != repeats:
                raise ValueError("seeds must be a list with exactly repeats entries")
            seeds = tuple(validate_seed(seed) for seed in raw_seeds)

        output = Path(str(mapping.get("output_dir", f"results/raw/{track}")))
        if not output.is_absolute() and base_dir is not None:
            output = (base_dir / output).resolve()

        parameters = mapping.get("parameters", {})
        if not isinstance(parameters, dict):
            raise ValueError("parameters must be a TOML table")

        return cls(
            track=track,
            experiment=experiment,
            repeats=repeats,
            base_seed=base_seed,
            seeds=seeds,
            output_dir=output,
            parameters=dict(parameters),
        )


def load_experiment_config(path: str | Path) -> ExperimentConfig:
    config_path = Path(path).resolve()
    with config_path.open("rb") as stream:
        mapping = tomllib.load(stream)
    return ExperimentConfig.from_mapping(mapping, base_dir=config_path.parent)
