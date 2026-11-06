# Verification

- Five unoptimized and optimized programs exactly match fixed expected outputs.
- Four passes are present and independently tested, including negative/zero/positive strength-reduction inputs.
- Four-pass suite instructions: 42 → 23; serialized IR bytes: 587 → 308.
- Measured summed mean interpreter time: 3.947 → 2.383 microseconds; summed mean compilation time: 97.36 → 149.64 microseconds. These are Python IR-interpreter measurements, not native-code claims.
- Budget-8 branch-and-bound selected folding/propagation then DCE, effort 6, objective 25 instructions; exhaustive enumeration of 35 feasible orders returned the identical solution.
- Focused Track F gate: 9/9 tests passed.
- Repository-wide gate: environment preflight 7/7, repository/prompt validation passed, and 78/78 tests passed.
- Commit linkage is added only after the implementation commit exists.
