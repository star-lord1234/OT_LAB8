"""Generate the deterministic Track H SQLite database without running timings."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tracks.H_dbms.implementation.database import generate_database


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261029)
    parser.add_argument("--customers", type=int, default=1200)
    parser.add_argument("--products", type=int, default=600)
    parser.add_argument("--orders", type=int, default=15000)
    arguments = parser.parse_args()
    manifest = generate_database(
        arguments.output,
        seed=arguments.seed,
        customer_count=arguments.customers,
        product_count=arguments.products,
        order_count=arguments.orders,
    )
    print(json.dumps(asdict(manifest), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
