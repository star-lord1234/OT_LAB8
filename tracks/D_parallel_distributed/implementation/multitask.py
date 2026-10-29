"""Two-task equal weighting, MGDA, and GradNorm comparison."""

from __future__ import annotations

import copy
import time

import numpy as np
import torch
from torch import nn


class TwoTaskModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.shared = nn.Linear(3, 2)
        self.head_one = nn.Linear(2, 1)
        self.head_two = nn.Linear(2, 1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        representation = torch.tanh(self.shared(x))
        return self.head_one(representation).squeeze(-1), self.head_two(representation).squeeze(-1)


def make_multitask_data(seed: int = 20261029) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    generator = torch.Generator().manual_seed(seed)
    x = torch.randn((128, 3), generator=generator, dtype=torch.float64)
    noise_one = 0.05 * torch.randn(128, generator=generator, dtype=torch.float64)
    noise_two = 0.05 * torch.randn(128, generator=generator, dtype=torch.float64)
    y_one = 1.7 * x[:, 0] - 0.8 * x[:, 1] + 0.4 * x[:, 2] + noise_one
    y_two = -0.5 * x[:, 0] + 1.5 * x[:, 1] + 1.1 * x[:, 2] + noise_two
    return x, y_one, y_two


def _flat_gradient(loss: torch.Tensor, parameters: list[nn.Parameter]) -> torch.Tensor:
    gradients = torch.autograd.grad(loss, parameters, retain_graph=True, allow_unused=False)
    return torch.cat([gradient.reshape(-1) for gradient in gradients])


def mgda_weight(gradient_one: torch.Tensor, gradient_two: torch.Tensor) -> float:
    """Closed-form minimum-norm convex combination for two gradients."""
    difference = gradient_one - gradient_two
    denominator = torch.dot(difference, difference)
    if float(denominator) < 1e-20:
        return 0.5
    alpha = torch.dot(gradient_two, gradient_two - gradient_one) / denominator
    return float(torch.clamp(alpha, 0.0, 1.0))


def _losses(model: TwoTaskModel, data) -> tuple[torch.Tensor, torch.Tensor]:
    x, y_one, y_two = data
    prediction_one, prediction_two = model(x)
    return torch.mean((prediction_one - y_one) ** 2), torch.mean((prediction_two - y_two) ** 2)


def train_method(method: str, initial_state: dict[str, torch.Tensor], data, epochs: int = 120, learning_rate: float = 0.04) -> dict[str, object]:
    if method not in {"equal", "mgda", "gradnorm"}:
        raise ValueError(f"unknown multi-task method: {method}")
    model = TwoTaskModel().double()
    model.load_state_dict(copy.deepcopy(initial_state))
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.2)
    shared_parameters = list(model.shared.parameters())
    weights = np.asarray([1.0, 1.0])
    gradnorm_lr, gradnorm_alpha = 0.025, 1.0
    with torch.no_grad():
        initial = [float(value) for value in _losses(model, data)]
    history = []
    started = time.perf_counter()
    for epoch in range(epochs):
        optimizer.zero_grad()
        loss_one, loss_two = _losses(model, data)
        gradient_one = _flat_gradient(loss_one, shared_parameters)
        gradient_two = _flat_gradient(loss_two, shared_parameters)
        cosine = float(torch.dot(gradient_one, gradient_two) / (torch.linalg.vector_norm(gradient_one) * torch.linalg.vector_norm(gradient_two) + 1e-20))
        if method == "equal":
            weights = np.asarray([1.0, 1.0])
        elif method == "mgda":
            alpha = mgda_weight(gradient_one, gradient_two)
            weights = np.asarray([2.0 * alpha, 2.0 * (1.0 - alpha)])
        else:
            base_norms = np.asarray([float(torch.linalg.vector_norm(gradient_one)), float(torch.linalg.vector_norm(gradient_two))])
            current_losses = np.asarray([float(loss_one.detach()), float(loss_two.detach())])
            relative = current_losses / np.maximum(np.asarray(initial), 1e-12)
            inverse_rate = relative / np.mean(relative)
            weighted_norms = weights * base_norms
            target = np.mean(weighted_norms) * inverse_rate**gradnorm_alpha
            weight_gradient = np.sign(weighted_norms - target) * base_norms
            weights = np.maximum(0.05, weights - gradnorm_lr * weight_gradient)
            weights *= 2.0 / np.sum(weights)
        total_loss = (float(weights[0]) * loss_one + float(weights[1]) * loss_two) / 2.0
        total_loss.backward()
        optimizer.step()
        history.append({
            "epoch": epoch + 1,
            "task_one_loss": float(loss_one.detach()),
            "task_two_loss": float(loss_two.detach()),
            "mean_loss": float((loss_one.detach() + loss_two.detach()) / 2.0),
            "weight_one": float(weights[0]),
            "weight_two": float(weights[1]),
            "shared_gradient_cosine": cosine,
        })
    final_one, final_two = _losses(model, data)
    return {
        "method": method,
        "initial_task_one_loss": initial[0],
        "initial_task_two_loss": initial[1],
        "final_task_one_loss": float(final_one.detach()),
        "final_task_two_loss": float(final_two.detach()),
        "final_mean_loss": float((final_one.detach() + final_two.detach()) / 2.0),
        "final_weight_one": float(weights[0]),
        "final_weight_two": float(weights[1]),
        "runtime_seconds": time.perf_counter() - started,
        "epochs": epochs,
        "history": history,
    }


def run_multitask_comparison(seed: int = 20261029, epochs: int = 120) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    torch.manual_seed(seed)
    data = make_multitask_data(seed)
    initial_model = TwoTaskModel().double()
    initial_state = copy.deepcopy(initial_model.state_dict())
    results = [train_method(method, initial_state, data, epochs=epochs) for method in ("equal", "mgda", "gradnorm")]
    rows, histories = [], []
    for result in results:
        rows.append({key: value for key, value in result.items() if key != "history"})
        histories.extend({"method": result["method"], **point} for point in result["history"])
    metadata = {
        "model": "three inputs -> shared two-unit tanh bottleneck -> two task-specific scalar heads",
        "shared_initialization": True,
        "examples": len(data[0]),
        "mgda_definition": "minimum-norm convex combination of the two shared-parameter gradients",
        "gradnorm_definition": "adaptive positive task weights targeting equalized shared-gradient norms and relative training rates",
    }
    return rows, histories, metadata
