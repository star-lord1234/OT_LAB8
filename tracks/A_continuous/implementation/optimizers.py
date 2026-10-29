"""Minimal reference implementations used by the Track A experiments."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import minimize

from ..objectives import ExponentialLeastSquares, LogisticObjective


Vector = NDArray[np.float64]


@dataclass
class OptimizationResult:
    method: str
    parameters: Vector
    history: list[dict[str, float | int]]
    elapsed_seconds: float
    iterations: int
    converged: bool
    stopping_condition: str

    @property
    def final_objective(self) -> float:
        return float(self.history[-1]["objective"])


FIRST_ORDER_METHODS = (
    "batch_gd",
    "sgd",
    "mini_batch_sgd",
    "momentum",
    "nesterov",
    "adagrad",
    "rmsprop",
    "adam",
)


def optimize_logistic(
    objective: LogisticObjective,
    method: str,
    *,
    seed: int,
    learning_rate: float,
    epochs: int = 60,
    batch_size: int = 16,
    tolerance: float = 1e-6,
    momentum: float = 0.9,
    epsilon: float = 1e-8,
) -> OptimizationResult:
    if method not in FIRST_ORDER_METHODS:
        raise ValueError(f"unknown method: {method}")
    rng = np.random.default_rng(seed)
    weights = np.zeros(objective.dimension)
    velocity = np.zeros_like(weights)
    accumulator = np.zeros_like(weights)
    second_moment = np.zeros_like(weights)
    first_moment = np.zeros_like(weights)
    update = 0
    history: list[dict[str, float | int]] = []
    started = time.perf_counter()
    stopping = f"max_epochs={epochs}"
    converged = False

    for epoch in range(epochs + 1):
        full_gradient = objective.gradient(weights)
        history.append(
            {
                "iteration": epoch,
                "objective": objective.value(weights),
                "gradient_norm": float(np.linalg.norm(full_gradient)),
                "accuracy": objective.accuracy(weights),
                "updates": update,
                "samples_processed": epoch * len(objective.labels),
            }
        )
        if np.linalg.norm(full_gradient) <= tolerance:
            stopping = f"gradient_norm<={tolerance}"
            converged = True
            break
        if epoch == epochs:
            break

        if method == "batch_gd":
            batches = [np.arange(len(objective.labels))]
        else:
            order = rng.permutation(len(objective.labels))
            size = 1 if method == "sgd" else batch_size
            batches = [order[start : start + size] for start in range(0, len(order), size)]

        for indices in batches:
            update += 1
            if method == "nesterov":
                gradient = objective.gradient(weights + momentum * velocity, indices)
                velocity = momentum * velocity - learning_rate * gradient
                weights += velocity
                continue

            gradient = objective.gradient(weights, indices)
            if method in {"batch_gd", "sgd", "mini_batch_sgd"}:
                weights -= learning_rate * gradient
            elif method == "momentum":
                velocity = momentum * velocity - learning_rate * gradient
                weights += velocity
            elif method == "adagrad":
                accumulator += gradient * gradient
                weights -= learning_rate * gradient / (np.sqrt(accumulator) + epsilon)
            elif method == "rmsprop":
                second_moment = 0.9 * second_moment + 0.1 * gradient * gradient
                weights -= learning_rate * gradient / (np.sqrt(second_moment) + epsilon)
            elif method == "adam":
                first_moment = 0.9 * first_moment + 0.1 * gradient
                second_moment = 0.999 * second_moment + 0.001 * gradient * gradient
                corrected_first = first_moment / (1.0 - 0.9**update)
                corrected_second = second_moment / (1.0 - 0.999**update)
                weights -= learning_rate * corrected_first / (np.sqrt(corrected_second) + epsilon)

    return OptimizationResult(
        method,
        weights,
        history,
        time.perf_counter() - started,
        len(history) - 1,
        converged,
        stopping,
    )


def gradient_descent(
    value: Callable[[Vector], float],
    gradient: Callable[[Vector], Vector],
    initial: ArrayLike,
    *,
    learning_rate: float,
    max_iterations: int = 100,
    tolerance: float = 1e-8,
    noise_std: float = 0.0,
    seed: int = 0,
    method: str = "gradient_descent",
) -> OptimizationResult:
    rng = np.random.default_rng(seed)
    point = np.asarray(initial, dtype=float).copy()
    history: list[dict[str, float | int]] = []
    started = time.perf_counter()
    stopping = f"max_iterations={max_iterations}"
    converged = False
    for iteration in range(max_iterations + 1):
        true_gradient = gradient(point)
        objective = value(point)
        history.append(
            {
                "iteration": iteration,
                "objective": objective,
                "gradient_norm": float(np.linalg.norm(true_gradient)),
            }
        )
        if not np.isfinite(objective) or abs(objective) > 1e12:
            stopping = "diverged"
            break
        if np.linalg.norm(true_gradient) <= tolerance:
            stopping = f"gradient_norm<={tolerance}"
            converged = True
            break
        if iteration == max_iterations:
            break
        noisy_gradient = true_gradient + rng.normal(0.0, noise_std, size=point.shape)
        point -= learning_rate * noisy_gradient
    return OptimizationResult(
        method,
        point,
        history,
        time.perf_counter() - started,
        len(history) - 1,
        converged,
        stopping,
    )


def newton_logistic(
    objective: LogisticObjective,
    *,
    max_iterations: int = 25,
    tolerance: float = 1e-9,
) -> OptimizationResult:
    weights = np.zeros(objective.dimension)
    history: list[dict[str, float | int]] = []
    started = time.perf_counter()
    converged = False
    stopping = f"max_iterations={max_iterations}"
    for iteration in range(max_iterations + 1):
        gradient = objective.gradient(weights)
        history.append({"iteration": iteration, "objective": objective.value(weights), "gradient_norm": float(np.linalg.norm(gradient))})
        if np.linalg.norm(gradient) <= tolerance:
            converged = True
            stopping = f"gradient_norm<={tolerance}"
            break
        if iteration == max_iterations:
            break
        weights -= np.linalg.solve(objective.hessian(weights), gradient)
    return OptimizationResult("newton", weights, history, time.perf_counter() - started, len(history) - 1, converged, stopping)


def gauss_newton(
    objective: ExponentialLeastSquares,
    *,
    initial: ArrayLike = (1.0, -0.2),
    max_iterations: int = 30,
    tolerance: float = 1e-10,
) -> OptimizationResult:
    parameters = np.asarray(initial, dtype=float).copy()
    history: list[dict[str, float | int]] = []
    started = time.perf_counter()
    converged = False
    stopping = f"max_iterations={max_iterations}"
    for iteration in range(max_iterations + 1):
        gradient = objective.gradient(parameters)
        history.append({"iteration": iteration, "objective": objective.value(parameters), "gradient_norm": float(np.linalg.norm(gradient))})
        if np.linalg.norm(gradient) <= tolerance:
            converged = True
            stopping = f"gradient_norm<={tolerance}"
            break
        if iteration == max_iterations:
            break
        step = np.linalg.solve(objective.gauss_newton_hessian(parameters), gradient)
        parameters -= step
    return OptimizationResult("gauss_newton", parameters, history, time.perf_counter() - started, len(history) - 1, converged, stopping)


def bfgs(
    value: Callable[[Vector], float],
    gradient: Callable[[Vector], Vector],
    initial: ArrayLike,
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 100,
) -> OptimizationResult:
    history: list[dict[str, float | int]] = []
    started = time.perf_counter()

    def callback(point: Vector) -> None:
        history.append({"iteration": len(history), "objective": value(point), "gradient_norm": float(np.linalg.norm(gradient(point)))})

    point = np.asarray(initial, dtype=float)
    history.append({"iteration": 0, "objective": value(point), "gradient_norm": float(np.linalg.norm(gradient(point)))})
    outcome = minimize(value, point, jac=gradient, method="BFGS", callback=callback, options={"gtol": tolerance, "maxiter": max_iterations})
    if not np.allclose(np.asarray(history[-1]["objective"]), value(outcome.x)):
        callback(outcome.x)
    return OptimizationResult(
        "bfgs",
        np.asarray(outcome.x),
        history,
        time.perf_counter() - started,
        int(outcome.nit),
        bool(outcome.success),
        str(outcome.message),
    )
