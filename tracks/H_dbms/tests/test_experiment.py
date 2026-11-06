from __future__ import annotations

import json
from pathlib import Path

from optlab.common.config import ExperimentConfig
from tracks.H_dbms.implementation.experiment import run_experiment


ROOT = Path(__file__).resolve().parents[3]


def test_track_h_smoke_experiment_writes_verified_evidence(tmp_path: Path) -> None:
    config = ExperimentConfig.from_mapping(
        {
            "track": "H",
            "experiment": "sqlite_smoke",
            "repeats": 1,
            "base_seed": 77,
            "output_dir": str(tmp_path / "results"),
            "parameters": {
                "customers": 100,
                "products": 520,
                "orders": 700,
                "storage_budget_pages": 1000,
                "warmups": 0,
                "query_repetitions": 2,
                "estimation_repetitions": 1,
            },
        }
    )
    manifest = run_experiment(config)
    assert manifest["status"] == "verified_sqlite_index_selection"
    assert manifest["all_results_equivalent"] is True
    assert manifest["all_configurations_within_budget"] is True
    assert manifest["sqlite_optimizer_replaced"] is False
    correctness = json.loads((config.output_dir / "correctness.json").read_text())
    assert all(
        item["all_repeats_equivalent"]
        for item in correctness["configurations"].values()
    )


def test_final_results_use_real_plans_and_match_logical_results() -> None:
    results = ROOT / "tracks" / "H_dbms" / "results"
    manifest = json.loads((results / "manifest.json").read_text())
    plans = json.loads((results / "query_plans.json").read_text())
    correctness = json.loads((results / "correctness.json").read_text())
    assert manifest["all_results_equivalent"] is True
    assert manifest["all_configurations_within_budget"] is True
    assert "SCAN orders" in " ".join(
        row["detail"] for row in plans["baseline"]["customer_recent_orders"]
    )
    assert "idx_orders_customer_date" in " ".join(
        row["detail"] for row in plans["ilp"]["customer_recent_orders"]
    )
    assert "idx_items_product" in " ".join(
        row["detail"] for row in plans["ilp"]["selected_product_sales"]
    )
    assert all(
        item["all_repeats_equivalent"]
        for item in correctness["configurations"].values()
    )
