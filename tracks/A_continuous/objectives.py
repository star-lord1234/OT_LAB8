"""Small differentiable objectives with independently checkable derivatives."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


Vector = NDArray[np.float64]


def finite_difference_gradient(function, point: ArrayLike, epsilon: float = 1e-6) -> Vector:
    x = np.asarray(point, dtype=float).copy()
    gradient = np.empty_like(x)
    for index in range(x.size):
        step = np.zeros_like(x)
        step[index] = epsilon
        gradient[index] = (function(x + step) - function(x - step)) / (2.0 * epsilon)
    return gradient


def finite_difference_hvp(gradient, point: ArrayLike, vector: ArrayLike, epsilon: float = 1e-5) -> Vector:
    x = np.asarray(point, dtype=float)
    v = np.asarray(vector, dtype=float)
    return (gradient(x + epsilon * v) - gradient(x - epsilon * v)) / (2.0 * epsilon)


@dataclass(frozen=True)
class QuadraticObjective:
    matrix: NDArray[np.float64]
    target: Vector

    @classmethod
    def strongly_convex(cls) -> "QuadraticObjective":
        return cls(np.diag([1.0, 10.0]), np.array([1.0, -1.0]))

    @classmethod
    def convex_not_strong(cls) -> "QuadraticObjective":
        matrix = np.array([[1.0, 1.0], [1.0, 1.0]])
        return cls(matrix, np.array([0.5, 0.5]))

    def value(self, point: ArrayLike) -> float:
        delta = np.asarray(point, dtype=float) - self.target
        return float(0.5 * delta @ self.matrix @ delta)

    def gradient(self, point: ArrayLike) -> Vector:
        return self.matrix @ (np.asarray(point, dtype=float) - self.target)

    def hessian(self, point: ArrayLike | None = None) -> NDArray[np.float64]:
        return self.matrix.copy()


class TiltedDoubleWell:
    """Bounded non-convex objective with two minima and one saddle."""

    tilt = 0.2

    def value(self, point: ArrayLike) -> float:
        x, y = np.asarray(point, dtype=float)
        return float((x * x - 1.0) ** 2 + self.tilt * x + 0.5 * y * y)

    def gradient(self, point: ArrayLike) -> Vector:
        x, y = np.asarray(point, dtype=float)
        return np.array([4.0 * x * (x * x - 1.0) + self.tilt, y])

    def hessian(self, point: ArrayLike) -> NDArray[np.float64]:
        x, _ = np.asarray(point, dtype=float)
        return np.diag([12.0 * x * x - 4.0, 1.0])


@dataclass(frozen=True)
class LogisticObjective:
    features: NDArray[np.float64]
    labels: Vector
    l2: float = 0.1

    @property
    def dimension(self) -> int:
        return self.features.shape[1]

    def value(self, weights: ArrayLike) -> float:
        w = np.asarray(weights, dtype=float)
        logits = self.features @ w
        data_loss = np.mean(np.logaddexp(0.0, logits) - self.labels * logits)
        return float(data_loss + 0.5 * self.l2 * np.dot(w, w))

    def gradient(self, weights: ArrayLike, indices: ArrayLike | None = None) -> Vector:
        w = np.asarray(weights, dtype=float)
        x = self.features if indices is None else self.features[np.asarray(indices)]
        y = self.labels if indices is None else self.labels[np.asarray(indices)]
        logits = np.clip(x @ w, -40.0, 40.0)
        probability = 1.0 / (1.0 + np.exp(-logits))
        return x.T @ (probability - y) / len(y) + self.l2 * w

    def hessian(self, weights: ArrayLike) -> NDArray[np.float64]:
        w = np.asarray(weights, dtype=float)
        logits = np.clip(self.features @ w, -40.0, 40.0)
        probability = 1.0 / (1.0 + np.exp(-logits))
        variance = probability * (1.0 - probability)
        return (self.features.T * variance) @ self.features / len(self.labels) + self.l2 * np.eye(self.dimension)

    def sample_gradients(self, weights: ArrayLike) -> NDArray[np.float64]:
        w = np.asarray(weights, dtype=float)
        logits = np.clip(self.features @ w, -40.0, 40.0)
        probability = 1.0 / (1.0 + np.exp(-logits))
        return self.features * (probability - self.labels)[:, None] + self.l2 * w

    def accuracy(self, weights: ArrayLike) -> float:
        predictions = (self.features @ np.asarray(weights) >= 0.0).astype(float)
        return float(np.mean(predictions == self.labels))


def make_logistic_objective(seed: int = 17, l2: float = 0.1, samples: int = 160) -> LogisticObjective:
    rng = np.random.default_rng(seed)
    class_zero = rng.normal(loc=(-1.0, -0.8), scale=(0.9, 0.8), size=(samples // 2, 2))
    class_one = rng.normal(loc=(1.0, 0.8), scale=(0.9, 0.8), size=(samples - samples // 2, 2))
    raw = np.vstack([class_zero, class_one])
    labels = np.concatenate([np.zeros(len(class_zero)), np.ones(len(class_one))])
    order = rng.permutation(samples)
    raw, labels = raw[order], labels[order]
    standardized = (raw - raw.mean(axis=0)) / raw.std(axis=0)
    features = np.column_stack([standardized, np.ones(samples)])
    return LogisticObjective(features.astype(float), labels.astype(float), l2)


@dataclass(frozen=True)
class ExponentialLeastSquares:
    x: Vector
    y: Vector

    @classmethod
    def synthetic(cls) -> "ExponentialLeastSquares":
        x = np.linspace(0.0, 1.0, 20)
        return cls(x, 1.5 * np.exp(-0.8 * x))

    def residuals(self, parameters: ArrayLike) -> Vector:
        amplitude, rate = np.asarray(parameters, dtype=float)
        return amplitude * np.exp(rate * self.x) - self.y

    def jacobian(self, parameters: ArrayLike) -> NDArray[np.float64]:
        amplitude, rate = np.asarray(parameters, dtype=float)
        exponential = np.exp(rate * self.x)
        return np.column_stack([exponential, amplitude * self.x * exponential])

    def value(self, parameters: ArrayLike) -> float:
        residual = self.residuals(parameters)
        return float(0.5 * np.mean(residual * residual))

    def gradient(self, parameters: ArrayLike) -> Vector:
        return self.jacobian(parameters).T @ self.residuals(parameters) / len(self.x)

    def gauss_newton_hessian(self, parameters: ArrayLike) -> NDArray[np.float64]:
        jacobian = self.jacobian(parameters)
        return jacobian.T @ jacobian / len(self.x)
