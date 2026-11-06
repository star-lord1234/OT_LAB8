# Track H — SQLite Physical Index Selection

Status: **implemented and verified on a documented synthetic database**. This
track chooses optional physical indexes around SQLite; it does not replace,
modify, or claim superiority over SQLite's internal query optimizer.

## H.1 Schema, dataset, and workload

The four-table synthetic commerce database contains 1,200 customers, 600
products, 15,000 orders, and 52,741 order items: 69,541 rows total. Generation
uses a local fixed seed and produces logical SHA-256
`60b061271f83180c8fbeb7d6eb51d98548ab401de5fef979c25c0c27f8ce8e36`.
The vacuumed database is 2,134,016 bytes (521 × 4,096-byte pages). Full field,
constraint, distribution, and privacy details are in
[DATASET.md](../tracks/H_dbms/DATASET.md), the executable
[generator](../tracks/H_dbms/implementation/database.py), retained
[manifest](../tracks/H_dbms/results/dataset_manifest.json), and exported
[schema](../tracks/H_dbms/results/schema.sql).

Five parameterized queries cover customer order history, status-window
reporting, selected-product sales, category/price browsing, and regional
revenue. Frequency weights are 40, 10, 20, 200, and 10; the high catalog weight
models a read-heavy storefront. SQL text, parameters, purposes, and weights are
retained in [workload.json](../tracks/H_dbms/results/workload.json). Optional
automatic indexes are disabled consistently; SQLite's primary-key indexes
remain part of every configuration.

## H.2 Binary index-selection model

The five candidates are `orders(customer_id, order_day)`,
`orders(status, order_day)`, `order_items(product_id)`,
`products(category, price_cents)`, and `customers(region)`. Their isolated
costs are measured from real SQLite page-count growth: 48, 67, 132, 4, and 5
pages respectively ([candidate evidence](../tracks/H_dbms/results/candidate_indexes.csv)).

For each candidate `i`, binary `x_i` indicates whether the index is created,
`s_i` is measured pages, and `b_i` is its positive weighted median-latency
reduction only on queries whose actual plan names that index. With budget
`B = 180` pages, the model minimizes
`C_0 - Σ_i b_i x_i` subject to `Σ_i s_i x_i ≤ B` and `x_i ∈ {0,1}`.
This additive estimate is a selection surrogate; final achieved latency is
always re-measured because indexes can interact. The complete formulation and
assumptions are in [MATHEMATICS.md](../tracks/H_dbms/MATHEMATICS.md).

## H.3 Greedy, ILP, and dynamic programming

Greedy ranks benefit per page. It selected `order_items(product_id)` plus the
4-page product catalog index, using 136 pages. Its measured selection runtime
was 5.125 microseconds. Ratio-greedy leaves 44 pages—too little for the
48-page customer/date index.

The binary MILP and independent exact 0/1 knapsack DP both selected
`order_items(product_id)` plus `orders(customer_id, order_day)`, exactly filling
all 180 pages. MILP took 13.016 milliseconds; DP took 40.583 microseconds. Both
returned the same estimated benefit and cost, while the separate toy solver
test demonstrates a case where exact methods beat ratio-greedy. Selection
sets, budget checks, estimated objectives, and solver runtimes are in
[selection_results.csv](../tracks/H_dbms/results/selection_results.csv).

## H.4 Plans, latency, throughput, and storage

Every final configuration is rebuilt on a fresh copy of the identical database
and run three times. Each query receives three warm-ups followed by 15 measured
executions using `time.perf_counter_ns`. The baseline weighted mean latency was
0.420 ms with 2,379 weighted queries/s. Greedy measured 0.0950 ms and 10,529
queries/s: a 77.4% latency reduction and 4.43× throughput for this local fixed
workload. Its actual index overhead was 557,056 bytes (136 pages).

ILP's exact selection measured 0.0493 ms and 20,291 queries/s, an 88.3%
latency reduction and 8.53× baseline throughput, at 737,280 bytes (180 pages).
DP selected the identical physical design and measured 0.0495 ms and 20,188
queries/s; small ILP/DP differences are timing noise between identical index
sets, not algorithmic performance differences. Raw repetitions, mean and
standard deviations are retained in
[workload_runs.csv](../tracks/H_dbms/results/workload_runs.csv) and
[workload_summary.csv](../tracks/H_dbms/results/workload_summary.csv); per-query
values are in [query_summary.csv](../tracks/H_dbms/results/query_summary.csv).

Actual [`EXPLAIN QUERY PLAN` output](../tracks/H_dbms/results/query_plans.json)
shows the baseline scanning `orders` for customer history and `order_items` for
product sales. The exact configuration searches with
`idx_orders_customer_date` and `idx_items_product`. SQLite itself chose these
access paths; Track H only selected which indexes existed.

## H.5 Correctness, limits, and reproduction

Every ordered result is hashed. All five hashes match the no-optional-index
baseline for all four configurations and every repeat
([correctness evidence](../tracks/H_dbms/results/correctness.json)). All actual
configuration sizes satisfy the 180-page budget. Tests independently cover
deterministic generation, plan changes without result changes, MILP/DP equality,
a greedy counterexample, budget feasibility, and the complete exporter.

Run:

```bash
./scripts/run_track.py H
.venv/bin/python -m pytest tracks/H_dbms/tests
./scripts/test_all.sh
```

The dataset is synthetic, parameters and candidate indexes are hand-designed,
the additive benefit model omits index interactions, and warm-cache laptop
timings do not predict production latency. Writes and index-maintenance costs
are outside this read-workload study. SQLite page sizes and plans can change
with engine version. The [environment record](../tracks/H_dbms/results/environment.json)
and [manifest](../tracks/H_dbms/results/manifest.json) preserve these run
boundaries.
