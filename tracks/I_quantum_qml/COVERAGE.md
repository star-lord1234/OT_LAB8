# Track I Coverage Audit

## Authoritative source

The authoritative seven-page Assignment 8 PDF was extracted page by page and visually checked. Section 5 requires QAOA, VQE, QNNs/PQCs, parameter-shift, SPSA, quantum natural gradient, relevant taught hybrid methods, every other taught quantum algorithm, and taught QML methods. Its example algorithm list is:

- Deutsch-Jozsa
- Bernstein-Vazirani
- Grover
- Quantum Fourier Transform (QFT)
- Quantum Phase Estimation (QPE)
- Shor
- quantum annealing

It explicitly names variational classifiers and quantum kernels, and requires barren-plateau, finite-shot, hardware-noise, and annealing-embedding-limit studies. Track I separately requires at least two self-written circuits, a hardware or hardware-noise experiment where access allows, matched QML/classical data, parameter/evaluation/time/accuracy comparisons, and a query/gate plus wall-time advantage comparison.

The generated, executable mapping is `results/coverage_checklist.csv`.

## Classroom-material audit

No file identifiable as the actual Chapter 6 classroom quantum material was supplied. The following nearby files were inspected and rejected as evidence:

- `AIDSET-FINAL-SYLLABUS.pdf`: modern cybersecurity and foundations of data science;
- `AIDSET_CC_FINAL_SYLLABUS.pdf`: foundations of data science;
- `CC Syllabus for AIDSET.pdf`: cybersecurity and introductory data science;
- `VR CC SYLLABUS.pdf`: engineering motorsports and electric systems;
- prior optimization assignments found by name: no quantum-algorithm teaching list.

Consequently, the PDF's complete named list is implemented, but “every other quantum algorithm taught” and any additional taught QML/hybrid method remain **UNRESOLVED**. Supply the actual Chapter 6 lecture notes, slides, or instructor-approved topic list to close `SYL-04`, `SYL-05`, `SYL-06`, and `SYL-08`.

## Reuse boundary

Track C's executable QAOA, VQE, QNN/PQC, parameter-shift, SPSA, QNG, shot, noise, plateau, and annealer-embedding experiments remain the canonical implementations. Track I adds the named algorithm inventory, four directly constructed circuits, matched QML/classical comparison, Grover query study, and Track D contrast. `results/coverage_checklist.csv` links each reused row to its code, tests, and retained result.
