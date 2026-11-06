#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CHECKOUT="$PROJECT_ROOT/external/more-itertools"
REMOTE="https://github.com/more-itertools/more-itertools.git"
PIN="f42daddf205f335fea6e200dad46049f33e71221"

if [ -e "$CHECKOUT" ]; then
    actual=$(git -C "$CHECKOUT" rev-parse HEAD 2>/dev/null || true)
    if [ "$actual" != "$PIN" ]; then
        echo "Existing checkout is not the pinned revision: $CHECKOUT" >&2
        echo "Expected $PIN, found ${actual:-not-a-git-repository}." >&2
        echo "Move it aside explicitly, then rerun this script; no automatic cleanup is performed." >&2
        exit 2
    fi
else
    mkdir -p "$PROJECT_ROOT/external"
    git init "$CHECKOUT"
    git -C "$CHECKOUT" remote add origin "$REMOTE"
    git -C "$CHECKOUT" fetch --depth 1 origin "$PIN"
    git -C "$CHECKOUT" checkout --detach FETCH_HEAD
fi

echo "Track J source ready: $CHECKOUT"
echo "Pinned commit: $(git -C "$CHECKOUT" rev-parse HEAD)"
echo "No global package was installed."
