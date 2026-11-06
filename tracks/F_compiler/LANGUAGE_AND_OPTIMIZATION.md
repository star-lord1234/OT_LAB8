# Track F Language and Optimization Model

## Tiny language

The grammar is deliberately limited to signed integer arithmetic, variables, assignments, external integer inputs, and observable prints:

```text
program    := statement*
statement  := "input" IDENT ";"
            | "let" IDENT "=" expression ";"
            | IDENT "=" expression ";"
            | "print" expression ";"
expression := term (("+" | "-") term)*
term       := factor (("*" | "/") factor)*
factor     := NUMBER | IDENT | "-" factor | "(" expression ")"
```

Integer division truncates toward zero. A variable must be assigned before use. `print` is the only observable output. The lowerer maps each assignment to a new SSA-like temporary, so later reassignment cannot invalidate an earlier common subexpression.

## Intermediate representation

The three-address IR has `INPUT`, `CONST`, `ADD`, `SUB`, `MUL`, `DIV`, `SHL`, and `PRINT`. An interpreter executes this generated representation. Serialized IR text supplies the code-size metric; it is not native object code.

## Four optimization passes

1. **Constant folding and propagation:** replaces known operands and evaluates safe constant operations. Constant division by zero remains a runtime operation so optimization does not change error timing.
2. **Common subexpression elimination:** aliases repeated pure binary expressions. Commutative `ADD`/`MUL` operands are canonicalized.
3. **Strength reduction:** replaces `x * 2^k` with `x << k` only for positive powers of two. Tests include negative, zero, and positive `x`.
4. **Dead-code elimination:** backward liveness retains values that reach `PRINT`; unused pure computations and inputs are removed.

The benchmark uses all four in the order above. Every sample is executed before and after optimization and compared with a fixed expected output.

## Budgeted pass-order decision

Let `P` be the four passes, `c_p` their effort costs, and `π` an ordered sequence containing each selected pass at most once. For baseline program suite `R`, let `I(π,R)` be the total IR instruction count after applying `π`.

```text
minimize    I(π, R)
subject to  Σ_{p in π} c_p ≤ 8
            each p appears at most once
```

Costs are 3 for folding/propagation, 3 for CSE, 2 for strength reduction, and 3 for DCE. Branch-and-bound explores ordered subsets, prunes over-budget branches, and retains a deterministic incumbent. Complete enumeration independently checks the result. The selected order is folding/propagation then DCE, effort 6, reducing the suite from 42 to 25 instructions under the budget. This budgeted decision is separate from the full-credit four-pass benchmark, whose total nominal effort is 11.
