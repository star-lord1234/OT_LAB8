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
