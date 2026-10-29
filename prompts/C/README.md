# Track C AI prompt history

A real Track C implementation interaction is recorded under `2026-10-29-track-c-implementation/`. Do not add synthetic entries.

For each real AI interaction, create a dated subdirectory containing:

- `record.json`: tool, actual model label, purpose, revisions, and commit reference.
- `prompt.md`: original and revised prompts exactly as used.
- `response.md`: the actual response or a clearly labeled relevant excerpt.
- `verification.md`: checks, corrections, result, and commit/URL.
- Chat export or screenshot when available, with secrets and private data removed.

Use `scripts/record_prompt.py` to create a blank record from a real prompt file. Complete it immediately after the interaction; never reconstruct or invent history.
