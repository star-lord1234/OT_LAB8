"""Matched tiny quantum/classical classification experiments for Track I."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

import numpy as np
import pennylane as qml
from pennylane import numpy as qnp
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


@dataclass(frozen=True)
class DatasetSplit:
    train_features: np.ndarray
    test_features: np.ndarray
    train_labels: np.ndarray
    test_labels: np.ndarray
    train_indices: np.ndarray
    test_indices: np.ndarray
    digest: str


def iris_binary_split(*, seed: int, samples_per_class: int = 20, test_fraction: float = 0.25) -> DatasetSplit:
    """Fixed binary Iris split using petal length/width and no network access."""

    if not 6 <= samples_per_class <= 50:
        raise ValueError("samples_per_class must be between 6 and 50")
    iris = load_iris()
    features = np.asarray(iris.data[:100, 2:4], dtype=float)
    labels = np.asarray(iris.target[:100], dtype=int)
    rng = np.random.default_rng(seed)
    selected = np.concatenate([
        rng.choice(np.flatnonzero(labels == label), size=samples_per_class, replace=False)
        for label in (0, 1)
    ])
    selected.sort()
    train_indices, test_indices = train_test_split(
        selected,
        test_size=test_fraction,
        random_state=seed,
        stratify=labels[selected],
    )
    scaler = StandardScaler().fit(features[train_indices])
    train_features = np.clip(scaler.transform(features[train_indices]), -2.0, 2.0) * (np.pi / 2.0)
    test_features = np.clip(scaler.transform(features[test_indices]), -2.0, 2.0) * (np.pi / 2.0)
    train_labels = labels[train_indices]
    test_labels = labels[test_indices]
    digest_payload = np.concatenate([
        train_indices.astype(float),
        test_indices.astype(float),
        train_features.ravel(),
        test_features.ravel(),
        train_labels.astype(float),
        test_labels.astype(float),
    ]).tobytes()
    return DatasetSplit(
        train_features,
        test_features,
        train_labels,
        test_labels,
        train_indices,
        test_indices,
        hashlib.sha256(digest_payload).hexdigest(),
    )


def apply_feature_map(features) -> None:
    qml.RY(features[0], wires=0)
    qml.RY(features[1], wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RZ(features[0] * features[1] / np.pi, wires=1)


def apply_variational_layers(weights) -> None:
    for layer in range(weights.shape[0]):
        for wire in range(2):
            qml.RY(weights[layer, wire, 0], wires=wire)
            qml.RZ(weights[layer, wire, 1], wires=wire)
        qml.CNOT(wires=[0, 1])
        qml.CNOT(wires=[1, 0])


def train_variational_classifier(
    split: DatasetSplit,
    *,
    seed: int,
    steps: int = 30,
    learning_rate: float = 0.12,
    layers: int = 2,
) -> tuple[dict[str, object], list[dict[str, object]], np.ndarray]:
    """Train a two-qubit QNN/VQC using parameter-shift and full-batch MSE."""

    device = qml.device("default.qubit", wires=2)

    @qml.qnode(device, interface="autograd", diff_method="parameter-shift")
    def circuit(weights, features):
        apply_feature_map(features)
        apply_variational_layers(weights)
        return qml.expval(qml.PauliZ(0))

    train_x = qnp.array(split.train_features, requires_grad=False)
    train_y = qnp.array(2 * split.train_labels - 1, requires_grad=False)

    def loss(weights):
        predictions = qnp.stack([circuit(weights, row) for row in train_x])
        return qnp.mean((predictions - train_y) ** 2)

    weights = qnp.array(
        np.random.default_rng(seed).normal(0.0, 0.15, size=(layers, 2, 2)),
        requires_grad=True,
    )
    optimizer = qml.AdamOptimizer(learning_rate)
    history: list[dict[str, object]] = []
    started = time.perf_counter()
    with qml.Tracker(device) as tracker:
        for step in range(steps):
            weights, previous = optimizer.step_and_cost(loss, weights)
            train_scores = np.asarray([circuit(weights, row) for row in split.train_features], dtype=float)
            history.append({
                "model": "variational_quantum_classifier_qnn",
                "step": step + 1,
                "loss": float(previous),
                "train_accuracy": float(np.mean((train_scores >= 0).astype(int) == split.train_labels)),
            })
        test_scores = np.asarray([circuit(weights, row) for row in split.test_features], dtype=float)
    runtime = time.perf_counter() - started
    predictions = (test_scores >= 0).astype(int)
    executions = int(tracker.totals.get("executions", 0))
    result = {
        "model": "variational_quantum_classifier_qnn",
        "model_family": "quantum",
        "accuracy": float(accuracy_score(split.test_labels, predictions)),
        "training_time_seconds": runtime,
        "trainable_parameter_count": int(weights.size),
        "circuit_evaluations": executions,
        "dataset_digest": split.digest,
        "train_samples": len(split.train_labels),
        "test_samples": len(split.test_labels),
        "notes": "two-qubit angle/product encoding; parameter-shift; same fixed split as all baselines",
    }
    return result, history, predictions


def train_logistic_baseline(split: DatasetSplit, *, seed: int) -> tuple[dict[str, object], np.ndarray]:
    started = time.perf_counter()
    model = LogisticRegression(random_state=seed, max_iter=1000).fit(split.train_features, split.train_labels)
    runtime = time.perf_counter() - started
    predictions = model.predict(split.test_features)
    return {
        "model": "classical_logistic_regression",
        "model_family": "classical",
        "accuracy": float(accuracy_score(split.test_labels, predictions)),
        "training_time_seconds": runtime,
        "trainable_parameter_count": int(model.coef_.size + model.intercept_.size),
        "circuit_evaluations": 0,
        "dataset_digest": split.digest,
        "train_samples": len(split.train_labels),
        "test_samples": len(split.test_labels),
        "notes": "linear classical baseline; identical standardized features and split",
    }, predictions


def fidelity_kernel_matrices(split: DatasetSplit) -> tuple[np.ndarray, np.ndarray, int, str]:
    device = qml.device("default.qubit", wires=2)

    @qml.qnode(device)
    def overlap(left, right):
        apply_feature_map(left)
        qml.adjoint(apply_feature_map)(right)
        return qml.probs(wires=[0, 1])

    train_count = len(split.train_features)
    test_count = len(split.test_features)
    train_kernel = np.empty((train_count, train_count), dtype=float)
    evaluations = 0
    for row in range(train_count):
        for column in range(row, train_count):
            value = float(np.asarray(overlap(split.train_features[row], split.train_features[column]))[0])
            train_kernel[row, column] = value
            train_kernel[column, row] = value
            evaluations += 1
    test_kernel = np.empty((test_count, train_count), dtype=float)
    for row in range(test_count):
        for column in range(train_count):
            test_kernel[row, column] = float(
                np.asarray(overlap(split.test_features[row], split.train_features[column]))[0]
            )
            evaluations += 1
    diagram = qml.draw(overlap)(split.train_features[0], split.train_features[1])
    return train_kernel, test_kernel, evaluations, diagram


def train_quantum_kernel(split: DatasetSplit) -> tuple[dict[str, object], np.ndarray, str]:
    started = time.perf_counter()
    train_kernel, test_kernel, evaluations, diagram = fidelity_kernel_matrices(split)
    model = SVC(kernel="precomputed", C=1.0).fit(train_kernel, split.train_labels)
    predictions = model.predict(test_kernel)
    runtime = time.perf_counter() - started
    return {
        "model": "quantum_fidelity_kernel_svc",
        "model_family": "quantum",
        "accuracy": float(accuracy_score(split.test_labels, predictions)),
        "training_time_seconds": runtime,
        "trainable_parameter_count": 0,
        "circuit_evaluations": evaluations,
        "dataset_digest": split.digest,
        "train_samples": len(split.train_labels),
        "test_samples": len(split.test_labels),
        "notes": f"fixed two-qubit feature map; {len(model.support_)} classical support vectors; no trainable circuit angles",
    }, predictions, diagram


def train_rbf_kernel_baseline(split: DatasetSplit) -> tuple[dict[str, object], np.ndarray]:
    started = time.perf_counter()
    model = SVC(kernel="rbf", C=1.0, gamma="scale").fit(split.train_features, split.train_labels)
    runtime = time.perf_counter() - started
    predictions = model.predict(split.test_features)
    return {
        "model": "classical_rbf_kernel_svc",
        "model_family": "classical",
        "accuracy": float(accuracy_score(split.test_labels, predictions)),
        "training_time_seconds": runtime,
        "trainable_parameter_count": int(len(model.dual_coef_.ravel()) + len(model.intercept_)),
        "circuit_evaluations": 0,
        "dataset_digest": split.digest,
        "train_samples": len(split.train_labels),
        "test_samples": len(split.test_labels),
        "notes": "RBF SVC baseline; parameter count reports fitted dual coefficients plus intercept",
    }, predictions


def variational_circuit_diagram(layers: int = 2) -> str:
    device = qml.device("default.qubit", wires=2)

    @qml.qnode(device)
    def circuit(weights, features):
        apply_feature_map(features)
        apply_variational_layers(weights)
        return qml.expval(qml.PauliZ(0))

    return qml.draw(circuit)(np.zeros((layers, 2, 2)), np.asarray([0.2, -0.4]))
