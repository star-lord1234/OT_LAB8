from __future__ import annotations

import numpy as np

from tracks.D_parallel_distributed.implementation.federated import (
    make_clients,
    train_centralized,
    train_fedavg,
    weighted_average,
)
from tracks.D_parallel_distributed.implementation.multitask import run_multitask_comparison


def test_fedavg_weighted_aggregation() -> None:
    models = [(np.asarray([1.0, 3.0]), 2.0), (np.asarray([5.0, 7.0]), 6.0)]
    weights, bias = weighted_average(models, [1, 3])
    assert np.allclose(weights, [4.0, 6.0])
    assert bias == 5.0


def test_fedavg_and_centralized_training_improve_from_log_two() -> None:
    clients = make_clients()
    centralized = train_centralized(clients, steps=8)
    federated = train_fedavg(clients, rounds=4, local_steps=2)
    assert centralized["loss"] < np.log(2.0)
    assert federated["loss"] < np.log(2.0)
    assert federated["communication_bytes"] > 0


def test_multitask_methods_share_valid_two_task_protocol() -> None:
    rows, history, metadata = run_multitask_comparison(epochs=25)
    assert [row["method"] for row in rows] == ["equal", "mgda", "gradnorm"]
    assert metadata["shared_initialization"]
    assert len(history) == 75
    for row in rows:
        assert np.isfinite(row["final_mean_loss"])
        assert row["final_mean_loss"] < (row["initial_task_one_loss"] + row["initial_task_two_loss"]) / 2
        assert np.isclose(row["final_weight_one"] + row["final_weight_two"], 2.0)
