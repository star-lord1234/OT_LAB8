# Original user prompt

Now prepare my macOS development environment for this assignment.

First, inspect the actual machine and existing installations. Do not assume the Apple Silicon generation, CPU architecture, OS version, or installed packages.

Check:

- CPU architecture, macOS version, RAM, available disk space
- Python and available virtual environments
- Homebrew, Git, Xcode Command Line Tools
- QEMU and the RISC-V toolchain
- Existing ML and quantum libraries

Create an isolated Python virtual environment and reproducible dependency configuration. Install only the dependencies genuinely required by our implementation.

Use CPU-compatible libraries and Apple Silicon MPS only where reliable.

For xv6, use the appropriate RISC-V cross-compiler and QEMU setup for the detected machine.

Create `scripts/preflight.sh` and a Python environment verification script to test:

1. Numerical optimization libraries
2. PyTorch tensor operations and autograd
3. ILP solver availability
4. Quantum circuit execution
5. SQLite
6. Multiprocessing
7. QEMU and RISC-V tools

Do not install packages globally if an isolated installation works.

Before any system-level change, show me the commands, reasons, and potential side effects. Request approval for potentially disruptive commands. Never use destructive cleanup commands without explicit approval.

Execute the checks, record real outputs, and document unresolved problems in `SETUP.md`.

Do not claim setup is complete unless the checks actually pass.
