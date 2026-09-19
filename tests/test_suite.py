"""The whole suite passes against the reference solvers."""

import pytest

from wg_benchmarks.runner import discover, run_benchmark

BENCHMARKS = discover()


@pytest.mark.parametrize("benchmark", BENCHMARKS, ids=[b.benchmark_id for b in BENCHMARKS])
def test_benchmark_passes(benchmark):
    outcome = run_benchmark(benchmark)
    assert outcome.passed, outcome.summary()


def test_expected_values_are_not_empty():
    for benchmark in BENCHMARKS:
        assert benchmark.expected.get("results"), benchmark.benchmark_id
        assert len(benchmark.expected.get("derivation", "")) >= 20, benchmark.benchmark_id
