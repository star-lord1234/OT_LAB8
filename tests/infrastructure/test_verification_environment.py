from __future__ import annotations

import json
from pathlib import Path

import pytest

from optlab.common.environment import collect_environment_metadata
from optlab.common.verification import require_all, verify_close, verify_predicate


ROOT = Path(__file__).resolve().parents[2]


def test_correctness_verification_pass_and_failure() -> None:
    passing = verify_close("sum", 0.1 + 0.2, 0.3)
    assert passing.passed
    require_all([passing, verify_predicate("positive", 3 > 0, "3 > 0")])

    with pytest.raises(AssertionError, match="wrong"):
        require_all([verify_close("wrong", 1.0, 2.0)])


def test_environment_metadata_is_useful_and_privacy_safe() -> None:
    document = collect_environment_metadata(ROOT, package_names=("numpy", "missing-xyz"))
    assert document["platform"]["machine"] == "arm64"
    assert document["packages"]["numpy"]
    assert document["packages"]["missing-xyz"] is None
    serialized = json.dumps(document).lower()
    assert "serial_number" not in serialized
    assert "hardware_uuid" not in serialized
    assert "provisioning_udid" not in serialized
