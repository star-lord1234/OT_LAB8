# Verification

- Authoritative Assignment 8 pages 2-4 were extracted and visually checked; four unrelated syllabus PDFs were rejected as Chapter 6 evidence.
- Direct probes recovered the expected DJ/BV/Grover/QFT/QPE outputs and Shor factors 3 and 5.
- Three configured VQC/QNN runs and three quantum-kernel evaluations used the same retained Iris split as both classical baselines; all scored 1.00 test accuracy.
- The final retained VQC/QNN median runtime was 6.81 seconds with 13,510 tracked circuit executions; logistic regression's median was 0.000728 seconds with zero circuits.
- Three explicitly classical annealing-proxy runs matched Track B's exhaustive optimum 8.0.
- Grover query counts were separated from simulator wall time; no quantum-advantage claim was made.
- Gate-local noise degraded success, and the plateau study remained labeled a finite-size proxy.
- Focused Track I gate: 13/13 tests passed.
- Final repository-wide gate: preflight 7/7, repository/prompt validation passed, and 110/110 tests passed.
- All three retained plots were visually inspected; the first misleading shared-axis draft was replaced and the regeneration bug is recorded in `logs/failures.md`.
- Verified implementation commit: pending final Git commit.
