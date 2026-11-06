# Original user prompt

Implement Track I, reusing the quantum simulator infrastructure and suitable circuits from Track C.

First retrieve the exact quantum algorithms and quantum ML topics required by the original assignment and any supplied Chapter 6 teaching material.

Create a coverage checklist and provide executable demonstrations for every algorithm taught.

Include the relevant algorithms listed in the assignment, such as:

- Deutsch–Jozsa
- Bernstein–Vazirani
- Grover
- Quantum Fourier Transform
- Quantum Phase Estimation
- Shor's algorithm
- Quantum annealing
- Variational quantum classifiers
- Quantum neural networks
- Quantum kernels

For algorithms whose full-scale implementations are impractical, use very small valid textbook instances and clearly explain the limitations. For annealing, distinguish a classical simulation or equivalent demonstration from physical annealing hardware.

Construct at least two quantum algorithm circuits yourself rather than exclusively using prebuilt library implementations.

For quantum ML:

1. Choose a small classical dataset.
2. Use exactly the same train/test split for classical and quantum models.
3. Train a small quantum classifier or QNN.
4. Train an appropriate classical baseline.
5. Compare accuracy, parameter count, training time, and circuit evaluation count.

Demonstrate algorithmic query complexity using Grover versus classical linear search or another valid example.

Compare theoretical query complexity separately from measured simulation runtime. Include a noise-model experiment where real hardware is unavailable and where permitted by the assignment.

Investigate limitations including data encoding, noise, simulation overhead, and barren plateaus.

Relate findings to Track D's measured parallel performance, distinguishing quantum algorithmic complexity from classical parallel speedup.

Use reusable implementations and avoid unnecessary duplicate code with Track C.

Deliver tests, circuits, comparison tables, plots, AI prompt logs, and a complete Track I report section.

Flag any taught quantum method that remains uncovered instead of silently declaring completion.
