# Original user prompt

Implement Track J as a software-engineering optimization experiment on a genuine, non-trivial codebase.

Prefer a stable public open-source Python project with at least approximately 1,000 lines of code, or another codebase consistent with `bm.md`.

Use test-suite selection or prioritization as the optimization problem, provided we can obtain real test execution times and coverage information.

Define:

- Candidate tests
- Execution cost per test
- Covered functions or lines
- A fixed testing time budget
- An objective such as maximizing coverage under the time budget

Compare:

1. A naive or original-order test selection baseline
2. A named Chapter 6 optimization method, preferably greedy maximum-coverage selection

Where feasible, compare against an exact solver on a smaller subset.

Profile the baseline before optimizing. Use measured coverage and execution costs, not invented values.

Run the selected test suites and report:

- Runtime
- Test selection cost
- Coverage achieved
- Any correctness or reliability trade-offs
- Maintainability implications

Do not confuse test selection with full regression testing. Explain the risk of omitting tests.

Ensure the selected project is runnable on my MacBook and has an appropriate license. Avoid large repositories and complex native build dependencies.

Provide reproducible scripts, source details, benchmark results, verification, plots, prompt logs, and the Track J report section.
