"""Run one xv6 command under QEMU and retain an exact console transcript."""

from __future__ import annotations

import argparse
import os
import select
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


BOOT_MARKER = "init: starting sh"
SHELL_PROMPT = "$ "


@dataclass(frozen=True)
class QemuResult:
    transcript: str
    elapsed_seconds: float
    booted: bool
    expected_seen: bool
    returncode: int


def run_qemu_command(
    checkout: Path,
    command: str | None,
    expected: str,
    timeout_seconds: float,
    rebuild: bool = False,
) -> QemuResult:
    """Boot xv6, optionally run one shell command, and stop after a marker."""

    make_command = [
        "make",
        "TOOLPREFIX=riscv64-elf-",
        "CPUS=1",
    ]
    if rebuild:
        make_command.append("-B")
    make_command.append("qemu")

    started = time.monotonic()
    process = subprocess.Popen(
        make_command,
        cwd=checkout,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    assert process.stdin is not None
    assert process.stdout is not None

    output = bytearray()
    sent_command = False
    booted = False
    expected_seen = False
    expected_offset = -1
    deadline = started + timeout_seconds

    try:
        while time.monotonic() < deadline:
            readable, _, _ = select.select([process.stdout], [], [], 0.25)
            if readable:
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    break
                output.extend(chunk)

            text = output.decode("utf-8", errors="replace")
            booted = BOOT_MARKER in text and SHELL_PROMPT in text
            if booted and not sent_command:
                if command:
                    process.stdin.write((command + "\n").encode())
                    process.stdin.flush()
                sent_command = True

            if sent_command and expected in text:
                expected_seen = True
                expected_offset = text.find(expected)
                # Wait for the shell prompt after the marker so the final
                # result line is not truncated by the monitor escape.
                if SHELL_PROMPT in text[expected_offset:]:
                    break
            if process.poll() is not None:
                break

        # QEMU's nographic monitor escape exits cleanly without modifying source.
        if process.poll() is None:
            process.stdin.write(b"\x01x")
            process.stdin.flush()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=5)
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)

    # Drain bytes emitted during QEMU shutdown.
    remainder = process.stdout.read()
    if remainder:
        output.extend(remainder)
    elapsed = time.monotonic() - started
    return QemuResult(
        transcript=output.decode("utf-8", errors="replace"),
        elapsed_seconds=elapsed,
        booted=booted,
        expected_seen=expected_seen,
        returncode=int(process.returncode or 0),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--command", default=None)
    parser.add_argument("--expect", required=True)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--rebuild", action="store_true")
    arguments = parser.parse_args()

    result = run_qemu_command(
        checkout=arguments.checkout.resolve(),
        command=arguments.command,
        expected=arguments.expect,
        timeout_seconds=arguments.timeout,
        rebuild=arguments.rebuild,
    )
    header = (
        f"# checkout={arguments.checkout.resolve()}\n"
        f"# command={arguments.command or '<boot-only>'}\n"
        f"# expected={arguments.expect}\n"
        f"# elapsed_seconds={result.elapsed_seconds:.6f}\n"
        f"# booted={str(result.booted).lower()}\n"
        f"# expected_seen={str(result.expected_seen).lower()}\n"
        f"# qemu_returncode={result.returncode}\n"
    )
    arguments.log.parent.mkdir(parents=True, exist_ok=True)
    arguments.log.write_text(header + result.transcript, encoding="utf-8")
    print(header, end="")
    print(f"# log={arguments.log}")
    return 0 if result.booted and result.expected_seen else 1


if __name__ == "__main__":
    raise SystemExit(main())
