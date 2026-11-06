# Track F — Toy-language Compiler Optimization

Status: **implemented and verified with the four-pass full-credit target**. This is a teaching compiler and IR interpreter, not a production or native-code compiler.

## F.1 Frontend, IR, and baseline execution

The language supports integer expressions, external integer inputs, `let` declarations, reassignment, and observable `print` statements. The complete grammar and semantic assumptions are in [LANGUAGE_AND_OPTIMIZATION.md](../tracks/F_compiler/LANGUAGE_AND_OPTIMIZATION.md). The pipeline is:

1. regex lexer with source offsets and comments;
2. recursive-descent parser with multiplication/division precedence and unary minus;
3. SSA-like three-address IR lowering;
4. deterministic IR text serialization;
5. IR interpreter with truncation-toward-zero division.

The five fixed [sample programs](../tracks/F_compiler/samples/manifest.json) cover constants, dead calculations, repeated expressions, power-of-two multiplication, reassignment, multiple inputs, and multiple outputs. Baseline expected outputs are 40; 16; 81; 59; and `[249,11]` ([semantic evidence](../tracks/F_compiler/results/semantic_equivalence.json), [before/after IR](../tracks/F_compiler/results/ir_snapshots.json)).

## F.2 Four optimization passes

The implementation in [passes.py](../tracks/F_compiler/implementation/passes.py) includes:

- constant folding and propagation;
- common subexpression elimination;
- safe strength reduction of multiplication by positive powers of two to shifts;
- backward-liveness dead-code elimination.

All five optimized programs exactly match baseline and expected outputs. CSE removes one instruction from both the repeated-expression and mixed samples. Folding exposes constants, strength reduction changes eligible `MUL` opcodes without pretending an instruction-count reduction, and DCE removes 5, 4, 0, 2, and 6 instructions respectively after the earlier passes ([per-pass trace](../tracks/F_compiler/results/optimization_trace.csv)). Tests exercise negative/zero/positive strength-reduction inputs, parser errors, unbound variables, and every sample.

## F.3 Budgeted pass-order optimization

Pass ordering is a genuine discrete decision: choose an ordered subset, use each pass at most once, minimize total suite instruction count, and keep nominal effort at most 8. Costs are folding 3, CSE 3, strength reduction 2, and DCE 3.

Branch-and-bound visited 35 nodes and pruned 24 over-budget branches. It selected folding/propagation followed by DCE at effort 6, reducing the suite from 42 to 25 instructions. Independent complete enumeration of all 35 budget-feasible ordered subsets selected the identical order and objective ([decision evidence](../tracks/F_compiler/results/pass_order_decision.json)). The lower bound did not prune a node, so the evidence does not exaggerate search efficiency. The full benchmark still uses all four passes (nominal effort 11) to satisfy the extension; the budgeted experiment answers a separate resource-constrained compiler decision.

## F.4 Required measurements

Across the five-program suite, four-pass optimization reduced static IR instructions from 42 to 23 (45.2%) and serialized IR size from 587 to 308 bytes (47.5%). Per-program reductions and three-repeat measurements are in [benchmark_summary.csv](../tracks/F_compiler/results/benchmark_summary.csv) and [instruction/code-size plot](../tracks/F_compiler/results/plots/instruction_count_code_size.png).

The sum of per-program mean interpreter times fell from 3.947 to 2.383 microseconds, approximately 39.6%. The sum of mean compilation times increased from 97.36 to 149.64 microseconds, approximately 53.7%, because the optimized compiler performs four extra traversals. Every timing is generated from 5,000 executions or 500 compilations per repeat, over three repeats ([raw timing runs](../tracks/F_compiler/results/benchmark_runs.csv), [timing plot](../tracks/F_compiler/results/plots/runtime_compile_time.png)). These sub-microsecond execution results are Python-interpreter measurements; they do not demonstrate native CPU instruction speedups. Static counts and code bytes remain the stronger evidence for this toy scale.

## F.5 Verification, limitations, and reproduction

Run:

```bash
./scripts/run_track.py F
.venv/bin/python -m pytest tracks/F_compiler/tests
```

The [manifest](../tracks/F_compiler/results/manifest.json) indexes the complete evidence. The compiler intentionally omits types beyond integers, control flow, functions, memory, register allocation, machine code, error recovery, and cross-basic-block dataflow. CSE safety relies on pure SSA-like values; DCE treats only `print` as observable. Code size is IR text, not executable bytes, and timing is susceptible to Python/runtime noise. Those boundaries keep the implementation explainable and prevent production-compiler claims.
