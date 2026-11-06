# Track H index-selection formulation

## Boundary of the optimization

SQLite continues to parse SQL, enumerate access paths, and choose a query plan.
This track optimizes which optional physical indexes are made available to that
internal optimizer. It does not replace or modify SQLite's optimizer.

## Data and workload

The deterministic synthetic commerce schema contains customers, products,
orders, and order items. Primary-key indexes are part of the schema and are not
decision variables. `PRAGMA automatic_index=OFF` prevents transient automatic
indexes from obscuring the optional-index comparison.

Five fixed queries represent customer history, status reporting, product sales,
catalog ranges, and regional revenue. Query `q` has frequency weight `w_q`;
the catalog query has weight 200 to model a read-heavy storefront, while the
other weights are 40, 10, 20, and 10.
Every timing uses the same SQL, parameters, generated rows, and warm-cache
policy under every configuration.

## Binary model

For candidate index `i`, define:

- `x_i ∈ {0,1}`: create candidate index `i`;
- `s_i`: measured isolated storage cost in SQLite pages;
- `b_i`: sum of positive, frequency-weighted median-latency reductions for
  queries whose actual `EXPLAIN QUERY PLAN` names index `i`, divided by total
  workload weight;
- `B`: storage budget in pages.

The weighted baseline estimate is

`C_0 = (Σ_q w_q · median_latency(q, no_optional_index)) / Σ_q w_q`.

Plan-filtering prevents unrelated timing noise from being credited to an index.
The additive selection model is:

`minimize  C_hat(x) = C_0 - Σ_i b_i x_i`

subject to

`Σ_i s_i x_i ≤ B`, and `x_i ∈ {0,1}`.

Equivalently, maximize `Σ_i b_i x_i` under the same budget. Greedy orders by
`b_i / s_i`. The MILP uses binary integrality and the single storage inequality.
Dynamic programming solves the same 0/1 knapsack model exactly in
`O(number_of_indexes × B)` time.

The additive model cannot capture redundant indexes, correlated predicates, or
SQLite plan interactions. Therefore estimated objective values are not reported
as achieved latency. Each selected set is built on a fresh copy of the same
database and evaluated with actual `EXPLAIN QUERY PLAN` output and repeated
timings. Actual combined page growth is checked against `B`.

## Metrics and correctness

- Query latency: median and dispersion from `time.perf_counter_ns` repetitions.
- Workload throughput: `Σ_q w_q / Σ_q(w_q · median_latency_q)`.
- Storage: `(indexed page_count - baseline page_count) × page_size`.
- Optimization time: wall time for greedy, MILP, or DP selection only.
- Correctness: SHA-256 of every ordered logical result must match the baseline
  for every repeat and index configuration.
