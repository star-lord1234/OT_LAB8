import hashlib
import json
from itertools import product

import numpy as np

from tracks.B_discrete.implementation.maxcut import (
    VERTICES,
    binary_to_spin,
    cut_value,
    enumerate_maxcut,
    exactly_one_energy,
    exactly_one_qubo,
    ising_energy,
    make_track_c_fixture,
    maxcut_ising,
    maxcut_qubo,
    penalty_sweep,
    qubo_energy,
)


def test_qubo_and_ising_energies_equal_negative_cut_for_every_state():
    q = maxcut_qubo()
    offset, linear, coupling = maxcut_ising()
    for bits in product((0, 1), repeat=VERTICES):
        expected = -cut_value(bits)
        assert np.isclose(qubo_energy(bits, q), expected)
        assert np.isclose(ising_energy(binary_to_spin(bits), offset, linear, coupling), expected)


def test_classical_maxcut_optimum_is_exhaustively_verified():
    rows = enumerate_maxcut()
    fixture = make_track_c_fixture()
    optimum = max(row["cut_value"] for row in rows)
    assert fixture["enumerated_states"] == 2**VERTICES
    assert fixture["classical_optimum_cut"] == optimum == 8.0
    assert all(cut_value(map(int, bits)) == optimum for bits in fixture["optimal_bitstrings"])


def test_track_c_fixture_hash_covers_every_other_field():
    fixture = make_track_c_fixture()
    recorded = fixture.pop("sha256_without_hash_field")
    canonical = json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(canonical).hexdigest() == recorded


def test_exactly_one_penalty_qubo_matches_direct_formula_and_becomes_feasible():
    for penalty in (0.5, 2.0, 5.0):
        q, offset = exactly_one_qubo(penalty=penalty)
        for bits in product((0, 1), repeat=3):
            assert np.isclose(qubo_energy(bits, q, offset), exactly_one_energy(bits, penalty=penalty))
    sweep = penalty_sweep()
    assert sweep[0]["best_is_feasible"] is False
    assert sweep[-1]["best_is_feasible"] is True
    assert sweep[-1]["best_bits"] == "100"
