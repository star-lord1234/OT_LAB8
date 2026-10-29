"""Tiny PyTorch demo separating backpropagation from parameter updates."""

from __future__ import annotations

import time

import numpy as np
import torch


def run_backprop_demo(seed: int = 20261029, epochs: int = 120) -> dict[str, object]:
    torch.manual_seed(seed)
    features = torch.tensor([[-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]], dtype=torch.float64)
    labels = torch.tensor([[0.0], [1.0], [1.0], [0.0]], dtype=torch.float64)
    model = torch.nn.Sequential(torch.nn.Linear(2, 4), torch.nn.Tanh(), torch.nn.Linear(4, 1)).double()
    loss_function = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.05)

    before_backward = [parameter.detach().clone() for parameter in model.parameters()]
    loss = loss_function(model(features), labels)
    loss.backward()
    after_backward = [parameter.detach().clone() for parameter in model.parameters()]
    backward_changed_parameters = any(not torch.equal(a, b) for a, b in zip(before_backward, after_backward))
    selected = next(model.parameters())
    analytic = float(selected.grad[0, 0])
    original = float(selected.data[0, 0])
    epsilon = 1e-5
    with torch.no_grad():
        selected.data[0, 0] = original + epsilon
        plus = float(loss_function(model(features), labels))
        selected.data[0, 0] = original - epsilon
        minus = float(loss_function(model(features), labels))
        selected.data[0, 0] = original
    numerical = (plus - minus) / (2.0 * epsilon)
    optimizer.step()
    after_step = [parameter.detach().clone() for parameter in model.parameters()]
    step_changed_parameters = any(not torch.equal(a, b) for a, b in zip(after_backward, after_step))

    started = time.perf_counter()
    history = []
    for epoch in range(epochs):
        optimizer.zero_grad()
        training_loss = loss_function(model(features), labels)
        training_loss.backward()
        optimizer.step()
        if epoch % 10 == 0 or epoch == epochs - 1:
            history.append({"iteration": epoch + 1, "objective": float(training_loss.detach())})
    elapsed = time.perf_counter() - started
    with torch.no_grad():
        final_loss = float(loss_function(model(features), labels))
        predictions = (model(features) >= 0.0).to(torch.float64)
        accuracy = float((predictions == labels).to(torch.float64).mean())
    return {
        "model": "2-4-1 tanh MLP on four XOR examples",
        "loss": "binary cross-entropy with logits",
        "optimizer": "Adam(lr=0.05)",
        "epochs": epochs,
        "gradient_parameter": "first layer weight[0,0]",
        "analytic_gradient": analytic,
        "finite_difference_gradient": numerical,
        "gradient_absolute_error": abs(analytic - numerical),
        "backward_changed_parameters": backward_changed_parameters,
        "optimizer_step_changed_parameters": step_changed_parameters,
        "final_loss": final_loss,
        "accuracy": accuracy,
        "runtime_seconds": elapsed,
        "history": history,
        "explanation": "loss.backward() computes and accumulates .grad without updating parameters; optimizer.step() consumes those gradients to update parameters.",
        "torch_version": torch.__version__,
        "device": "cpu",
    }
