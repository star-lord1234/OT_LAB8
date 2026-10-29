import numpy as np

from tracks.A_continuous.implementation.optimizers import (
    FIRST_ORDER_METHODS,
    bfgs,
    gauss_newton,
    newton_logistic,
    optimize_logistic,
)
from tracks.A_continuous.objectives import ExponentialLeastSquares, make_logistic_objective


SETTINGS = {
    "batch_gd": (0.2, 80),
    "sgd": (0.015, 1),
    "mini_batch_sgd": (0.08, 16),
    "momentum": (0.035, 16),
    "nesterov": (0.035, 16),
    "adagrad": (0.15, 16),
    "rmsprop": (0.02, 16),
    "adam": (0.03, 16),
}


def test_every_required_first_order_method_improves_logistic_objective():
    objective = make_logistic_objective(samples=80)
    for method in FIRST_ORDER_METHODS:
        learning_rate, batch_size = SETTINGS[method]
        result = optimize_logistic(objective, method, seed=7, learning_rate=learning_rate, batch_size=batch_size, epochs=30)
        assert result.final_objective < result.history[0]["objective"] - 0.05, method
        assert np.isfinite(result.parameters).all()


def test_newton_and_bfgs_agree_on_logistic_optimum():
    objective = make_logistic_objective(samples=80)
    newton = newton_logistic(objective)
    quasi_newton = bfgs(objective.value, objective.gradient, np.zeros(objective.dimension))
    assert newton.final_objective < 0.5
    assert abs(newton.final_objective - quasi_newton.final_objective) < 1e-8


def test_gauss_newton_recovers_synthetic_parameters():
    result = gauss_newton(ExponentialLeastSquares.synthetic())
    assert result.converged
    assert np.allclose(result.parameters, [1.5, -0.8], atol=1e-7)
