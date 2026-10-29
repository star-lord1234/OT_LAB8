from optlab.quantum.diagnostics import barren_plateau_proxy, embedding_chain_strength_demo


def test_plateau_proxy_reports_declining_global_gradient_variance():
    rows = barren_plateau_proxy(qubit_counts=(2, 6), repeats=20, seed=9)
    assert rows[1]["global_gradient_variance"] < rows[0]["global_gradient_variance"]
    assert all(row["local_gradient_variance"] >= 0 for row in rows)


def test_embedding_requires_sufficient_chain_strength():
    rows = embedding_chain_strength_demo()
    assert rows[0]["broken_chain_fraction"] == 1.0
    assert rows[-1]["broken_chain_fraction"] == 0.0
    assert all(row["simulated"] is True for row in rows)
