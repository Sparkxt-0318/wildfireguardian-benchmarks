"""Mutation testing: every injected bug is caught, and every claim is honoured."""

from wg_benchmarks.mutations import MUTATIONS
from wg_benchmarks.reporting import mutation_matrix

MATRIX = mutation_matrix()


def test_every_mutation_is_detected():
    undetected = sorted(m for m, row in MATRIX.items() if not row["detected_by"])
    assert not undetected, f"no benchmark detects: {undetected}"


def test_declared_detectors_actually_detect():
    broken = {
        mutation: row["declared_but_undetected"]
        for mutation, row in MATRIX.items()
        if row["declared_but_undetected"]
    }
    assert not broken, broken


def test_every_mutation_has_a_description():
    for mutation in MUTATIONS.values():
        assert len(mutation.description) > 40, mutation.mutation_id
        assert mutation.failure_mode
