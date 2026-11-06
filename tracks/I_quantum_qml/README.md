# Track I - Quantum algorithms and QML advantage

Status: **implemented and verified on local CPU simulators; exact classroom-syllabus coverage remains blocked.** No physical gate-based or annealing hardware was used.

## Implemented scope

The track executes the assignment PDF's named Deutsch-Jozsa, Bernstein-Vazirani, Grover, QFT, QPE, Shor, and annealing demonstrations. Deutsch-Jozsa, Bernstein-Vazirani, Grover's oracle/diffuser, and QFT are constructed directly from primitive gates. Track C's QAOA, VQE, PQC/QNN, parameter-shift, SPSA, QNG, finite-shot, noise, barren-plateau, and annealer-embedding evidence is mapped rather than duplicated.

A two-qubit variational classifier/QNN and a fidelity quantum kernel use exactly the same fixed binary Iris split as logistic-regression and RBF-SVC baselines. Query counts for Grover and worst-case linear search are reported separately from measured simulator/Python wall time.

## Commands

```bash
./scripts/run_track.py I --plan
./scripts/run_track.py I
MPLCONFIGDIR="$PWD/.cache/matplotlib" XDG_CACHE_HOME="$PWD/.cache/xdg" \
  .venv/bin/python -m pytest tracks/I_quantum_qml/tests
```

The formal definitions and scope labels are in `MATHEMATICS.md`; the authoritative/source audit is in `COVERAGE.md`; generated evidence is in `results/`; and the report is `report/track_i.md`.

## Scope boundary

The assignment's named algorithms are covered. No actual Chapter 6 lecture notes, slides, or instructor topic list were supplied. Nearby files named “syllabus” were for cybersecurity, introductory data science, and motorsports, so they were not used to infer quantum content. The final coverage row therefore remains `blocked-awaiting-syllabus` rather than making a false completion claim.
