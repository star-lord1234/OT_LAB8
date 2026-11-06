# Track J External Source

- Project: `more-itertools`
- Official repository: <https://github.com/more-itertools/more-itertools>
- Pinned commit: `f42daddf205f335fea6e200dad46049f33e71221`
- Commit date: 2026-11-03
- License: MIT, copyright Erik Rose (2012)
- License digest: `09f1c8c9e941af3e584d59641ea9b87d83c0cb0fd007eb5ef391a7e2643c1a46`
- Measured size: 7,282 physical Python source lines; 5,402 nonblank, non-comment lines
- Runtime dependencies for this experiment: Python 3.12, pytest, coverage.py; no native extension or project installation

The source is not vendored into this submission. Prepare the exact detached checkout with:

```bash
./scripts/prepare_track_j.sh
```

The script initializes `external/more-itertools`, fetches only the pinned commit, and checks it out detached. If a different checkout already exists, it stops instead of overwriting or deleting it. The assignment repository ignores this external directory; `source_provenance.json` retains the verified commit, source size, license digest, and clean-state check.

The experiment does not modify upstream source or tests and does not open issues or submit changes to the external project.
