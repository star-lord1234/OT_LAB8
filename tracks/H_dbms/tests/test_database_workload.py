from __future__ import annotations

from pathlib import Path

from tracks.H_dbms.implementation.database import connect_database, generate_database
from tracks.H_dbms.implementation.models import CANDIDATE_INDEXES, QUERIES
from tracks.H_dbms.implementation.workload import measure_workload, query_plan


def test_database_generation_is_reproducible(tmp_path: Path) -> None:
    first = generate_database(
        tmp_path / "first.sqlite", seed=1234, customer_count=100,
        product_count=520, order_count=600,
    )
    second = generate_database(
        tmp_path / "second.sqlite", seed=1234, customer_count=100,
        product_count=520, order_count=600,
    )
    assert first.logical_sha256 == second.logical_sha256
    assert first.order_items == second.order_items
    assert first.page_size_bytes == 4096
    assert first.automatic_indexes is False


def test_optional_index_changes_plan_not_results(tmp_path: Path) -> None:
    path = tmp_path / "database.sqlite"
    generate_database(
        path, seed=2026, customer_count=100, product_count=520, order_count=1000
    )
    connection = connect_database(path)
    try:
        query = next(item for item in QUERIES if item.name == "selected_product_sales")
        before, _, _ = measure_workload(connection, warmups=0, repetitions=1)
        before_digest = {measurement.query: measurement.result_sha256 for measurement in before}
        baseline_plan = query_plan(connection, query)
        candidate = next(index for index in CANDIDATE_INDEXES if index.name == "idx_items_product")
        connection.execute(candidate.ddl)
        connection.commit()
        after, _, _ = measure_workload(connection, warmups=0, repetitions=1)
        after_digest = {measurement.query: measurement.result_sha256 for measurement in after}
        indexed_plan = query_plan(connection, query)
    finally:
        connection.close()
    assert before_digest == after_digest
    assert not any("idx_items_product" in row[3] for row in baseline_plan)
    assert any("idx_items_product" in row[3] for row in indexed_plan)
