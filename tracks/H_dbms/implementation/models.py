"""Fixed schema objects for the Track H physical-design experiment."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateIndex:
    name: str
    table: str
    columns: tuple[str, ...]
    rationale: str

    @property
    def ddl(self) -> str:
        columns = ", ".join(self.columns)
        return f"CREATE INDEX {self.name} ON {self.table} ({columns})"


@dataclass(frozen=True)
class QuerySpec:
    name: str
    sql: str
    parameters: tuple[object, ...]
    weight: int
    purpose: str


CANDIDATE_INDEXES = (
    CandidateIndex(
        "idx_orders_customer_date",
        "orders",
        ("customer_id", "order_day"),
        "customer history and region-to-orders join",
    ),
    CandidateIndex(
        "idx_orders_status_date",
        "orders",
        ("status", "order_day"),
        "status-window reporting",
    ),
    CandidateIndex(
        "idx_items_product",
        "order_items",
        ("product_id",),
        "product sales lookup",
    ),
    CandidateIndex(
        "idx_products_category_price",
        "products",
        ("category", "price_cents"),
        "category catalog range and ordering",
    ),
    CandidateIndex(
        "idx_customers_region",
        "customers",
        ("region",),
        "regional customer filtering",
    ),
)


QUERIES = (
    QuerySpec(
        "customer_recent_orders",
        """
        SELECT id, order_day, status, total_cents
        FROM orders
        WHERE customer_id = ? AND order_day BETWEEN ? AND ?
        ORDER BY order_day DESC, id DESC
        LIMIT 50
        """,
        (42, 250, 730),
        40,
        "interactive customer order history",
    ),
    QuerySpec(
        "status_window_summary",
        """
        SELECT status, COUNT(*), SUM(total_cents), AVG(total_cents)
        FROM orders
        WHERE status = ? AND order_day >= ?
        GROUP BY status
        """,
        ("shipped", 365),
        10,
        "operational status report",
    ),
    QuerySpec(
        "selected_product_sales",
        """
        SELECT p.id, p.name, SUM(oi.quantity),
               SUM(oi.quantity * oi.unit_price_cents)
        FROM order_items AS oi
        JOIN products AS p ON p.id = oi.product_id
        WHERE oi.product_id IN (?, ?, ?, ?, ?)
        GROUP BY p.id, p.name
        ORDER BY p.id
        """,
        (5, 17, 101, 233, 501),
        20,
        "product-level sales analysis",
    ),
    QuerySpec(
        "category_price_catalog",
        """
        SELECT id, name, price_cents
        FROM products
        WHERE category = ? AND price_cents BETWEEN ? AND ?
        ORDER BY price_cents, id
        LIMIT 100
        """,
        ("electronics", 2500, 25000),
        200,
        "category catalog range query",
    ),
    QuerySpec(
        "regional_revenue",
        """
        SELECT c.region, COUNT(DISTINCT o.id), SUM(o.total_cents)
        FROM customers AS c
        JOIN orders AS o ON o.customer_id = c.id
        WHERE c.region = ? AND o.order_day >= ?
        GROUP BY c.region
        """,
        ("west", 365),
        10,
        "regional revenue report with a join",
    ),
)
