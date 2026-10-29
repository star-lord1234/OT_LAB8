# Relevant AI response excerpt

The actual machine was detected as an arm64 Apple M5 MacBook Air running macOS 26.5.2 with 16 GB RAM. A project-local CPython 3.12.13 environment was created and exactly locked with uv. QEMU 11.1.1, RISC-V GCC 16.2.0, and Binutils 2.47 were installed through Homebrew after approval.

The final preflight executed numerical optimization, PyTorch autograd, SciPy/HiGHS ILP, PennyLane circuits/noise, SQLite, multiprocessing, QEMU machine discovery, and RV64 compilation/disassembly. It passed 7/7. MPS was compiled in but unavailable, so CPU remained the required baseline. xv6 itself was explicitly left unclaimed until a pinned source build, boot, and `usertests` run.
