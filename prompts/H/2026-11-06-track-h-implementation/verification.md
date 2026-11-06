# Verification

- Fixed synthetic database: 69,541 rows; logical SHA-256 `60b061271f83180c8fbeb7d6eb51d98548ab401de5fef979c25c0c27f8ce8e36`.
- Five actual index costs: 48, 67, 132, 4, and 5 SQLite pages; fixed budget 180 pages.
- Greedy selected product lookup plus category/price (136 pages); MILP and DP selected product lookup plus customer/date (180 pages).
- Actual plans name selected indexes; the baseline plans scan the corresponding tables.
- Every query result hash matches the no-optional-index baseline for every configuration and repeat.
- Retained measured performance and optimization runtimes are linked from `report/track_h.md`; no production or SQLite-internal-optimizer claim is made.
- Focused Track H gate: 8/8 tests passed.
- Repository-wide gate: environment preflight 7/7, repository/prompt validation passed, and 97/97 tests passed.
- Implementation commit is filled only after the final content is committed.
