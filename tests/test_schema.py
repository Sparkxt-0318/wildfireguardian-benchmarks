"""Every benchmark descriptor is schema-valid and structurally consistent."""

from wg_benchmarks.runner import discover, validate_benchmark

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validators.validate_benchmarks import check_repository  # type: ignore  # noqa: E402


def test_every_benchmark_validates():
    failures = {}
    for benchmark in discover():
        errors = validate_benchmark(benchmark)
        if errors:
            failures[benchmark.benchmark_id] = errors
    assert not failures, failures


def test_repository_is_consistent():
    assert check_repository(discover()) == []


def test_suite_is_large_enough():
    # The project's definition of done requires at least 25 benchmark scenarios.
    assert len(discover()) >= 25


def test_every_category_is_populated():
    categories = {b.category for b in discover()}
    required = {
        "terrain",
        "road_graph",
        "fire",
        "observation",
        "routing",
        "assisted_dispatch",
        "traffic",
        "forecast_value",
        "scenario_uncertainty",
        "statistics",
        "protectability",
    }
    assert required <= categories, required - categories
