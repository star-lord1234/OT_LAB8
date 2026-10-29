"""Curvature products and deliberately small approximations."""

from __future__ import annotations

import time

import numpy as np
from numpy.typing import ArrayLike

from ..objectives import LogisticObjective, finite_difference_hvp


def analyze_curvature(objective: LogisticObjective, weights: ArrayLike) -> dict[str, object]:
    point = np.asarray(weights, dtype=float)
    vector = np.linspace(0.5, 1.0, objective.dimension)
    started = time.perf_counter()
    hessian = objective.hessian(point)
    exact_hvp = hessian @ vector
    numerical_hvp = finite_difference_hvp(objective.gradient, point, vector)
    diagonal = np.diag(np.diag(hessian))
    per_sample = objective.sample_gradients(point)
    fisher = per_sample.T @ per_sample / len(per_sample)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    top = np.argmax(eigenvalues)
    low_rank = eigenvalues[top] * np.outer(eigenvectors[:, top], eigenvectors[:, top])

    def relative_error(approximation: np.ndarray) -> float:
        denominator = max(float(np.linalg.norm(exact_hvp)), 1e-15)
        return float(np.linalg.norm(approximation @ vector - exact_hvp) / denominator)

    return {
        "point": point.tolist(),
        "probe_vector": vector.tolist(),
        "hessian": hessian.tolist(),
        "eigenvalues": eigenvalues.tolist(),
        "hvp_relative_error": float(np.linalg.norm(numerical_hvp - exact_hvp) / np.linalg.norm(exact_hvp)),
        "diagonal_hvp_relative_error": relative_error(diagonal),
        "empirical_fisher_hvp_relative_error": relative_error(fisher),
        "rank1_hvp_relative_error": relative_error(low_rank),
        "runtime_seconds": time.perf_counter() - started,
        "notes": "HVP is checked independently by finite differences. Diagonal, empirical Fisher, and rank-1 matrices are approximations and need not match the exact Hessian.",
    }
