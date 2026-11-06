# Track G - xv6 operating-system optimization

Status: **implemented and verified as the required single-feature minimum**.

This track changes the official MIT `xv6-riscv` scheduler at pinned commit
`fa2ddcb7ca87a77af579380a6eafd5aff163b44f`. The feature is a three-level
priority scheduler with aging. No second kernel feature is claimed.

## Evidence layout

- Design, current behavior, affected locks/states, and limitations: `DESIGN.md`
- Canonical benchmark source and QEMU driver: `implementation/`
- Repeated-run collector and result generator: `benchmarks/`
- Reconstructible support-baseline, complete, and scheduler-only diffs: `patches/`
- QEMU transcripts, CSV summaries, environment, and plot: `results/`
- Host-side correctness tests: `tests/`
- Report: `report/track_g.md`
- AI record: `prompts/G/2026-11-06-track-g-implementation/`

The external checkout is intentionally ignored. Recreate it with:

```bash
git clone https://github.com/mit-pdos/xv6-riscv.git external/xv6-riscv
git -C external/xv6-riscv checkout --detach fa2ddcb7ca87a77af579380a6eafd5aff163b44f
git -C external/xv6-riscv apply --check "$PWD/tracks/G_xv6/patches/priority-scheduler.patch"
git -C external/xv6-riscv apply "$PWD/tracks/G_xv6/patches/priority-scheduler.patch"
make -C external/xv6-riscv TOOLPREFIX=riscv64-elf- CPUS=1 qemu
```

Regenerate tables and the plot from the archived console transcripts:

```bash
./scripts/run_track.py G
.venv/bin/python -m pytest tracks/G_xv6/tests
```

To collect a fresh optimized matrix from an already patched checkout:

```bash
.venv/bin/python tracks/G_xv6/benchmarks/collect.py \
  --checkout external/xv6-riscv \
  --scheduler priority \
  --results tracks/G_xv6/results/raw \
  --repeats 3 --rebuild-first
```

Fresh collection overwrites same-named raw logs; preserve or commit existing
evidence before intentionally replacing it.
