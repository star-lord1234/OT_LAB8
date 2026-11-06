# Track H synthetic commerce dataset

The dataset is generated locally; it is not a real customer or transaction
dataset. No external download, account, or paid service is used.

## Tables

- `customers(id, name, region, segment)`: 1,200 rows across six regions and
  three segments.
- `products(id, name, category, price_cents)`: 600 rows across eight categories.
- `orders(id, customer_id, order_day, status, total_cents)`: 15,000 rows over
  day numbers 0-730 and five statuses.
- `order_items(order_id, line_no, product_id, quantity, unit_price_cents)`:
  52,741 rows in the retained run, with two to five unique products per order.

Foreign keys and positive/range checks are enabled during generation. Orders'
totals are derived from their generated item quantities and unit prices. The
only baseline indexes are those SQLite creates for integer primary keys and the
`order_items(order_id, line_no)` primary key. `PRAGMA automatic_index=OFF` is
used during the experiment so transient automatic indexes cannot blur the
physical-design comparison.

## Reproducibility

The generator uses a private `random.Random(20261029)` instance. It does not
depend on process hash order or global random state. Every logical row is fed to
a canonical SHA-256 stream; the retained digest is
`60b061271f83180c8fbeb7d6eb51d98548ab401de5fef979c25c0c27f8ce8e36`.
The vacuumed baseline is 521 pages × 4,096 bytes = 2,134,016 bytes.

Generate a standalone copy:

```bash
.venv/bin/python tracks/H_dbms/benchmarks/generate_database.py \
  --output data/generated/track_h.sqlite
```

The generated database is intentionally ignored by Git. The committed
`results/schema.sql`, dataset manifest, workload definition, and generator are
the reproducibility artifacts.
