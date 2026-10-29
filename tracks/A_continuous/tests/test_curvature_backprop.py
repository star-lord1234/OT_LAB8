from tracks.A_continuous.implementation.curvature import analyze_curvature
from tracks.A_continuous.implementation.pytorch_demo import run_backprop_demo
from tracks.A_continuous.objectives import make_logistic_objective


def test_hessian_vector_product_matches_independent_finite_difference():
    objective = make_logistic_objective(samples=60)
    result = analyze_curvature(objective, [0.1, -0.2, 0.05])
    assert result["hvp_relative_error"] < 1e-8
    assert len(result["eigenvalues"]) == objective.dimension
    assert result["diagonal_hvp_relative_error"] >= 0
    assert result["empirical_fisher_hvp_relative_error"] >= 0
    assert result["rank1_hvp_relative_error"] >= 0


def test_backprop_computes_gradient_and_optimizer_performs_update():
    result = run_backprop_demo(seed=11, epochs=100)
    assert result["gradient_absolute_error"] < 1e-8
    assert result["backward_changed_parameters"] is False
    assert result["optimizer_step_changed_parameters"] is True
    assert result["accuracy"] == 1.0
    assert result["final_loss"] < 0.1
