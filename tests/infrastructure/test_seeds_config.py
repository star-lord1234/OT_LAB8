from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pytest

from optlab.common.config import ExperimentConfig, load_experiment_config
from optlab.common.seeds import seed_everything, spawned_seeds


ROOT = Path(__file__).resolve().parents[2]


def test_seed_everything_repeats_python_and_numpy() -> None:
    seed_everything(1234)
    first = (random.random(), np.random.random())
    seed_everything(1234)
    second = (random.random(), np.random.random())
    assert first == second


def test_spawned_seeds_are_repeatable_and_distinct() -> None:
    assert spawned_seeds(99, 4) == spawned_seeds(99, 4)
    assert len(set(spawned_seeds(99, 4))) == 4


@pytest.mark.parametrize("seed", [-1, 2**32, True, 1.5])
def test_invalid_seed_is_rejected(seed: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        seed_everything(seed)  # type: ignore[arg-type]


def test_track_config_loads_and_resolves_output() -> None:
    config = load_experiment_config(ROOT / "configs" / "tracks" / "A.toml")
    assert config.track == "A"
    assert config.repeats == 3
    assert len(config.seeds) == 3
    assert config.output_dir == ROOT / "tracks" / "A_continuous" / "results"


def test_config_requires_known_track() -> None:
    with pytest.raises(ValueError, match="track must be"):
        ExperimentConfig.from_mapping({"track": "Z", "experiment": "bad"})
