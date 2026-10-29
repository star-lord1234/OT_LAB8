"""Small deterministic FedAvg versus centralized logistic-regression study."""

from __future__ import annotations

import time

import numpy as np


Client = tuple[np.ndarray, np.ndarray]


def sigmoid(values: np.ndarray) -> np.ndarray:
    return np.where(values >= 0, 1.0 / (1.0 + np.exp(-values)), np.exp(values) / (1.0 + np.exp(values)))


def make_clients(seed: int = 20261029, clients: int = 4, examples: int = 80) -> list[Client]:
    rng = np.random.default_rng(seed)
    true_weights = np.asarray([1.4, -1.1, 0.8, -0.5])
    result = []
    for client in range(clients):
        shift = np.zeros(4)
        shift[client % 4] = (client - 1.5) * 0.6
        x = rng.normal(size=(examples, 4)) + shift
        logits = x @ true_weights - 0.15 + rng.normal(scale=0.35, size=examples)
        # Client-specific feature shifts yield non-identical class balances.
        y = (logits > 0.0).astype(float)
        result.append((x, y))
    return result


def loss_accuracy(weights: np.ndarray, bias: float, x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    probabilities = np.clip(sigmoid(x @ weights + bias), 1e-12, 1.0 - 1e-12)
    loss = float(-np.mean(y * np.log(probabilities) + (1.0 - y) * np.log(1.0 - probabilities)))
    accuracy = float(np.mean((probabilities >= 0.5) == y))
    return loss, accuracy


def gradient(weights: np.ndarray, bias: float, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    error = sigmoid(x @ weights + bias) - y
    return x.T @ error / len(x), float(np.mean(error))


def weighted_average(models: list[tuple[np.ndarray, float]], sizes: list[int]) -> tuple[np.ndarray, float]:
    total = sum(sizes)
    weights = sum((model[0] * size for model, size in zip(models, sizes)), start=np.zeros_like(models[0][0])) / total
    bias = sum(model[1] * size for model, size in zip(models, sizes)) / total
    return weights, float(bias)


def _combined(clients: list[Client]) -> Client:
    return np.concatenate([client[0] for client in clients]), np.concatenate([client[1] for client in clients])


def train_centralized(clients: list[Client], steps: int, learning_rate: float = 0.25) -> dict[str, object]:
    x, y = _combined(clients)
    weights, bias = np.zeros(x.shape[1]), 0.0
    history = []
    started = time.perf_counter()
    for step in range(steps):
        grad_w, grad_b = gradient(weights, bias, x, y)
        weights -= learning_rate * grad_w
        bias -= learning_rate * grad_b
        loss, accuracy = loss_accuracy(weights, bias, x, y)
        history.append({"step": step + 1, "loss": loss, "accuracy": accuracy})
    runtime = time.perf_counter() - started
    return {"weights": weights, "bias": bias, "history": history, "runtime_seconds": runtime, "loss": history[-1]["loss"], "accuracy": history[-1]["accuracy"]}


def train_fedavg(clients: list[Client], rounds: int, local_steps: int, learning_rate: float = 0.25) -> dict[str, object]:
    dimensions = clients[0][0].shape[1]
    weights, bias = np.zeros(dimensions), 0.0
    sizes = [len(client[0]) for client in clients]
    x_all, y_all = _combined(clients)
    history = []
    started = time.perf_counter()
    for round_index in range(rounds):
        local_models = []
        for x, y in clients:
            local_weights, local_bias = weights.copy(), bias
            for _ in range(local_steps):
                grad_w, grad_b = gradient(local_weights, local_bias, x, y)
                local_weights -= learning_rate * grad_w
                local_bias -= learning_rate * grad_b
            local_models.append((local_weights, local_bias))
        weights, bias = weighted_average(local_models, sizes)
        loss, accuracy = loss_accuracy(weights, bias, x_all, y_all)
        history.append({"round": round_index + 1, "loss": loss, "accuracy": accuracy})
    runtime = time.perf_counter() - started
    parameter_bytes = (dimensions + 1) * 8
    return {
        "weights": weights,
        "bias": bias,
        "history": history,
        "runtime_seconds": runtime,
        "loss": history[-1]["loss"],
        "accuracy": history[-1]["accuracy"],
        "communication_bytes": rounds * len(clients) * 2 * parameter_bytes,
    }


def run_federated_grid(seed: int = 20261029) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    clients = make_clients(seed)
    rows: list[dict[str, object]] = []
    histories: list[dict[str, object]] = []
    initial_loss, initial_accuracy = loss_accuracy(np.zeros(4), 0.0, *_combined(clients))
    for rounds, local_steps in ((5, 1), (10, 1), (5, 3), (10, 3)):
        total_steps = rounds * local_steps
        central = train_centralized(clients, total_steps)
        fedavg = train_fedavg(clients, rounds, local_steps)
        common = {"rounds": rounds, "local_steps": local_steps, "matched_update_steps": total_steps}
        rows.append({"method": "centralized", **common, "loss": central["loss"], "accuracy": central["accuracy"], "runtime_seconds": central["runtime_seconds"], "communication_bytes": 0})
        rows.append({"method": "fedavg", **common, "loss": fedavg["loss"], "accuracy": fedavg["accuracy"], "runtime_seconds": fedavg["runtime_seconds"], "communication_bytes": fedavg["communication_bytes"]})
        histories.extend({"method": "centralized", **common, **point} for point in central["history"])
        histories.extend({"method": "fedavg", **common, "step": point["round"], "loss": point["loss"], "accuracy": point["accuracy"]} for point in fedavg["history"])
    metadata = {
        "clients": len(clients),
        "examples_per_client": [len(client[0]) for client in clients],
        "class_fraction_per_client": [float(np.mean(client[1])) for client in clients],
        "initial_loss": initial_loss,
        "initial_accuracy": initial_accuracy,
        "comparison_note": "Centralized full-batch steps equal rounds times local steps; FedAvg performs that many local steps per client and communicates once per round.",
    }
    return rows, histories, metadata
