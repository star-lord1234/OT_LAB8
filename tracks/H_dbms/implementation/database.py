"""Deterministic SQLite database generation and physical-size helpers."""

from __future__ import annotations

import hashlib
import json
import random
import sqlite3
from dataclasses import dataclass
from pathlib import Path


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    segment TEXT NOT NULL
);
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents > 0)
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_day INTEGER NOT NULL CHECK (order_day BETWEEN 0 AND 730),
    status TEXT NOT NULL,
    total_cents INTEGER NOT NULL CHECK (total_cents > 0)
);
CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders(id),
    line_no INTEGER NOT NULL,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 5),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents > 0),
    PRIMARY KEY (order_id, line_no)
);
"""


@dataclass(frozen=True)
class DatasetManifest:
    seed: int
    customers: int
    products: int
    orders: int
    order_items: int
    logical_sha256: str
    database_bytes: int
    page_size_bytes: int
    page_count: int
    automatic_indexes: bool


def connect_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA automatic_index = OFF")
    return connection


def database_size(connection: sqlite3.Connection) -> tuple[int, int, int]:
    page_size = int(connection.execute("PRAGMA page_size").fetchone()[0])
    page_count = int(connection.execute("PRAGMA page_count").fetchone()[0])
    return page_count * page_size, page_size, page_count


def _digest_rows(groups: list[tuple[str, list[tuple[object, ...]]]]) -> str:
    digest = hashlib.sha256()
    for table, rows in groups:
        digest.update(table.encode())
        for row in rows:
            digest.update(json.dumps(row, separators=(",", ":")).encode())
            digest.update(b"\n")
    return digest.hexdigest()


def generate_database(
    path: Path,
    *,
    seed: int,
    customer_count: int,
    product_count: int,
    order_count: int,
) -> DatasetManifest:
    """Create the fixed synthetic commerce database from a local RNG."""

    if min(customer_count, product_count, order_count) <= 0:
        raise ValueError("all row counts must be positive")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    rng = random.Random(seed)
    regions = ("north", "south", "east", "west", "central", "coastal")
    segments = ("consumer", "small_business", "enterprise")
    categories = (
        "electronics", "home", "books", "sports",
        "office", "garden", "toys", "grocery",
    )
    statuses = ("pending", "paid", "shipped", "delivered", "cancelled")

    customers = [
        (identifier, f"Customer {identifier:04d}", regions[(identifier * 7) % len(regions)],
         segments[(identifier * 5) % len(segments)])
        for identifier in range(1, customer_count + 1)
    ]
    products = []
    prices: dict[int, int] = {}
    for identifier in range(1, product_count + 1):
        category = categories[(identifier * 11) % len(categories)]
        price = 500 + ((identifier * 7919 + rng.randrange(5000)) % 49500)
        prices[identifier] = price
        products.append((identifier, f"Product {identifier:04d}", category, price))

    orders: list[tuple[object, ...]] = []
    items: list[tuple[object, ...]] = []
    for order_id in range(1, order_count + 1):
        customer_id = 1 + ((order_id * 37 + rng.randrange(customer_count)) % customer_count)
        order_day = (order_id * 17 + rng.randrange(731)) % 731
        status = statuses[(order_id + rng.randrange(10)) % len(statuses)]
        line_count = 2 + rng.randrange(4)
        total = 0
        used_products: set[int] = set()
        for line_no in range(1, line_count + 1):
            product_id = 1 + rng.randrange(product_count)
            while product_id in used_products:
                product_id = 1 + rng.randrange(product_count)
            used_products.add(product_id)
            quantity = 1 + rng.randrange(5)
            unit_price = prices[product_id]
            total += quantity * unit_price
            items.append((order_id, line_no, product_id, quantity, unit_price))
        orders.append((order_id, customer_id, order_day, status, total))

    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA journal_mode = OFF")
        connection.execute("PRAGMA synchronous = OFF")
        connection.executescript(SCHEMA_SQL)
        with connection:
            connection.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)
            connection.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)
            connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)
            connection.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", items)
        connection.execute("VACUUM")
        size, page_size, page_count = database_size(connection)
    finally:
        connection.close()

    logical_digest = _digest_rows(
        [("customers", customers), ("products", products), ("orders", orders), ("order_items", items)]
    )
    return DatasetManifest(
        seed=seed,
        customers=len(customers),
        products=len(products),
        orders=len(orders),
        order_items=len(items),
        logical_sha256=logical_digest,
        database_bytes=size,
        page_size_bytes=page_size,
        page_count=page_count,
        automatic_indexes=False,
    )
