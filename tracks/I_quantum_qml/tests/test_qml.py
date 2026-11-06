import numpy as np

from optlab.quantum.qml_models import (
    fidelity_kernel_matrices,
    iris_binary_split,
    train_logistic_baseline,
    train_quantum_kernel,
    train_variational_classifier,
)


def test_dataset_split_is_reproducible_balanced_and_shared():
    first = iris_binary_split(seed=31, samples_per_class=10)
    second = iris_binary_split(seed=31, samples_per_class=10)
    assert first.digest == second.digest
    assert np.array_equal(first.train_indices, second.train_indices)
    assert set(first.train_indices).isdisjoint(set(first.test_indices))
    assert sorted(np.bincount(first.train_labels)) == [7, 8]
    assert sorted(np.bincount(first.test_labels)) == [2, 3]


def test_quantum_fidelity_kernel_is_symmetric_unit_diagonal_and_psd():
    split = iris_binary_split(seed=17, samples_per_class=6)
    train, test, evaluations, _ = fidelity_kernel_matrices(split)
    assert train.shape == (9, 9)
    assert test.shape == (3, 9)
    assert np.allclose(train, train.T)
    assert np.allclose(np.diag(train), 1.0)
    assert np.linalg.eigvalsh(train).min() > -1e-9
    assert evaluations == 45 + 27


def test_vqc_qnn_and_classical_baseline_use_identical_split():
    split = iris_binary_split(seed=19, samples_per_class=6)
    quantum, history, predictions = train_variational_classifier(split, seed=3, steps=2)
    classical, classical_predictions = train_logistic_baseline(split, seed=3)
    assert quantum["dataset_digest"] == classical["dataset_digest"] == split.digest
    assert quantum["train_samples"] == classical["train_samples"]
    assert quantum["test_samples"] == classical["test_samples"]
    assert quantum["trainable_parameter_count"] == 8
    assert quantum["circuit_evaluations"] > 0
    assert classical["circuit_evaluations"] == 0
    assert len(history) == 2
    assert len(predictions) == len(classical_predictions) == len(split.test_labels)


def test_quantum_kernel_classifier_has_no_trainable_circuit_angles():
    split = iris_binary_split(seed=23, samples_per_class=6)
    result, predictions, diagram = train_quantum_kernel(split)
    assert result["dataset_digest"] == split.digest
    assert result["trainable_parameter_count"] == 0
    assert result["circuit_evaluations"] > 0
    assert len(predictions) == len(split.test_labels)
    assert "RY" in diagram
