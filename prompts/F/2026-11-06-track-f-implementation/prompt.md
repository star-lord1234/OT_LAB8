# Original user prompt

Implement Track F with the smallest feasible toy-language compiler that satisfies the original assignment.

Build:
1. Lexer
2. Parser
3. Intermediate representation
4. Code generator or interpreter for the generated representation
5. Baseline unoptimized compilation
6. Optimization passes

Implement at least two passes:
- Constant folding and propagation
- Dead-code elimination

If the initial implementation is stable, add common subexpression elimination and strength reduction to meet the four-pass full-credit target.

Formulate at least one genuine compiler optimization decision, such as pass ordering, as a discrete optimization problem and solve it with a named Chapter 6 method.

Create several small programs with expressions, variables, assignments, and observable outputs.

Compare optimized versus unoptimized code for:
- Instruction count
- Execution runtime
- Code size
- Compilation time

Verify semantic equivalence across all test programs. Do not use fabricated timing improvements or treat fewer source-code lines as proof of runtime improvement.

Keep the language deliberately small. Do not build a production compiler, web interface, or unnecessary language features.

Produce compiler tests, sample programs, benchmarks, plots, report section, and AI prompt logs.
