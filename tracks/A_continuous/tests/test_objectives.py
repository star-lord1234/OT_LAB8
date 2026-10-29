import numpy as np

from tracks.A_continuous.objectives import (
    ExponentialLeastSquares,
    QuadraticObjective,
    TiltedDoubleWell,
    finite_difference_gradient,
    make_logistic_objective,
)


def test_all_analytic_gradients_match_finite_differences():
    cases = [
        (QuadraticObjective.strongly_convex(), np.array([0.4, -0.2])),
        (QuadraticObjective.convex_not_strong(), np.array([0.4, -0.2])),
        (TiltedDoubleWell(), np.array([0.4, -0.2])),
        (make_logistic_objective(samples=40), np.array([0.2, -0.1, 0.05])),
        (ExponentialLeastSquares.synthetic(), np.array([1.1, -0.4])),
    ]
    for objective, point in cases:
        error = np.max(np.abs(objective.gradient(point) - finite_difference_gradient(objective.value, point)))
        assert error < 2e-6


def test_objective_classes_have_expected_curvature():
    assert np.min(np.linalg.eigvalsh(QuadraticObjective.strongly_convex().hessian())) > 0
    assert np.isclose(np.min(np.linalg.eigvalsh(QuadraticObjective.convex_not_strong().hessian())), 0.0)
    assert np.min(np.linalg.eigvalsh(TiltedDoubleWell().hessian([0.0, 0.0]))) < 0


def test_gauss_newton_matrix_is_jacobian_product():
    objective = ExponentialLeastSquares.synthetic()
    point = np.array([1.2, -0.5])
    jacobian = objective.jacobian(point)
    assert np.allclose(objective.gauss_newton_hessian(point), jacobian.T @ jacobian / len(objective.x))
