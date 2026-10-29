"""Deterministic seed handling for Python, NumPy, and PyTorch."""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np


UINT32_MAX = 2**32 - 1


@dataclass(frozen=True)
class SeedState:
    seed: int
    torch_seeded: bool


def validate_seed(seed: int) -> int:
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    if not 0 <= seed <= UINT32_MAX:
        raise ValueError(f"seed must be between 0 and {UINT32_MAX}")
    return seed


def seed_everything(seed: int) -> SeedState:
    """Seed available RNGs without requiring accelerators."""

    validated = validate_seed(seed)
    random.seed(validated)
    np.random.seed(validated)

    torch_seeded = False
    try:
        import torch
    except ImportError:
        pass
    else:
        torch.manual_seed(validated)
        torch_seeded = True

    return SeedState(seed=validated, torch_seeded=torch_seeded)


def spawned_seeds(base_seed: int, count: int) -> tuple[int, ...]:
    """Derive deterministic, independent uint32 seeds from one base seed."""

    validate_seed(base_seed)
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("count must be an integer")
    if count < 1:
        raise ValueError("count must be at least 1")

    sequence = np.random.SeedSequence(base_seed)
    return tuple(
        int(child.generate_state(1, dtype=np.uint32)[0])
        for child in sequence.spawn(count)
    )
