# Original user prompt

Implement Track H using SQLite and Python, with a small but meaningful synthetic database.

Choose index selection under a storage budget as the primary optimization problem.

Create:
- A reproducible relational schema
- A documented synthetic dataset
- A representative workload of multiple SQL queries
- Candidate indexes with measurable storage costs

Mathematically formulate index selection:
- Binary decision variables
- Objective minimizing workload execution cost
- Storage budget constraint

Compare:
1. No additional indexes as the baseline
2. Greedy index selection
3. ILP-based index selection

Where practical, incorporate or compare a dynamic-programming approach.

Use actual SQLite EXPLAIN QUERY PLAN output and measured query timings to estimate index benefits.

Evaluate each selected index configuration against the same dataset and query workload.

Report:
- Query latency
- Workload throughput
- Index storage overhead
- Query plans
- Optimization runtime

Verify that queries return exactly the same logical results before and after optimization.

Do not claim to have replaced SQLite's internal query optimizer. Explain that we are optimizing physical index selection around it.

Create tests, reproducible database generation scripts, query-plan exports, results, plots, prompt logs, and the Track H report section.
