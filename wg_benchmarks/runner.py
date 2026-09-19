"""Benchmark discovery and execution."""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from . import yamlio
from .compare import ComparisonResult, compare
from .registry import get_solver
from .schema import load_schema, validate

REPO_ROOT = Path(__file__).resolve().parent.parent
BENCHMARK_ROOT = REPO_ROOT / "benchmarks"

_SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "len": len,
    "max": max,
    "min": min,
    "round": round,
    "sorted": sorted,
    "sum": sum,
    "set": set,
    "list": list,
}


@dataclass
class Benchmark:
    path: Path
    meta: dict
    expected: dict

    @property
    def benchmark_id(self) -> str:
        return str(self.meta["benchmark_id"])

    @property
    def label(self) -> str:
        return str(self.meta["label"])

    @property
    def category(self) -> str:
        return str(self.meta["category"])

    @property
    def directory(self) -> str:
        return str(self.path.parent.relative_to(REPO_ROOT))

    def load_inputs(self) -> dict[str, Any]:
        inputs = {}
        for name, relative in (self.meta.get("inputs") or {}).items():
            inputs[str(name)] = yamlio.load(self.path.parent / relative)
        return inputs


@dataclass
class RunResult:
    benchmark: Benchmark
    status: str  # pass | fail | error
    comparison: ComparisonResult | None = None
    invariant_failures: list[str] = field(default_factory=list)
    error: str | None = None
    duration_s: float = 0.0
    result: dict | None = None

    @property
    def passed(self) -> bool:
        return self.status == "pass"

    def summary(self) -> str:
        if self.status == "pass":
            return "PASS"
        if self.status == "error":
            return f"ERROR {self.error}"
        parts = [str(d) for d in (self.comparison.differences if self.comparison else [])]
        parts += [f"invariant failed: {i}" for i in self.invariant_failures]
        return "FAIL " + "; ".join(parts[:6])


def discover(root: Path | None = None) -> list[Benchmark]:
    root = root or BENCHMARK_ROOT
    benchmarks = []
    for meta_path in sorted(root.rglob("benchmark.yaml")):
        meta = yamlio.load(meta_path)
        expected_path = meta_path.parent / "expected" / "expected.yaml"
        expected = yamlio.load(expected_path) if expected_path.exists() else {}
        benchmarks.append(Benchmark(path=meta_path, meta=meta, expected=expected))
    benchmarks.sort(key=lambda b: b.benchmark_id)
    return benchmarks


def select(
    benchmarks: Iterable[Benchmark],
    ids: Iterable[str] = (),
    categories: Iterable[str] = (),
    labels: Iterable[str] = (),
) -> list[Benchmark]:
    ids, categories, labels = set(ids), set(categories), set(labels)
    if not ids and not categories and not labels:
        return list(benchmarks)
    selected = []
    for benchmark in benchmarks:
        if benchmark.benchmark_id in ids or benchmark.category in categories or benchmark.label in labels:
            selected.append(benchmark)
    return selected


def check_invariants(expected: dict, result: dict) -> list[str]:
    failures = []
    for invariant in expected.get("invariants", []) or []:
        expression = invariant["expression"]
        try:
            # `r` must live in globals, not locals: a comprehension inside the
            # expression creates its own scope and cannot see eval() locals.
            ok = bool(eval(expression, {"__builtins__": _SAFE_BUILTINS, "r": result}, {}))
        except Exception as exc:  # noqa: BLE001 - report, do not crash the run
            failures.append(f"{expression} raised {type(exc).__name__}: {exc}")
            continue
        if not ok:
            failures.append(f"{expression} ({invariant['description']})")
    return failures


def run_benchmark(benchmark: Benchmark) -> RunResult:
    started = time.perf_counter()
    try:
        solver = get_solver(str(benchmark.meta["solver"]))
        inputs = benchmark.load_inputs()
        result = solver(inputs)
    except Exception:  # noqa: BLE001 - a solver crash is a benchmark error
        return RunResult(
            benchmark=benchmark,
            status="error",
            error=traceback.format_exc(limit=4).strip().splitlines()[-1],
            duration_s=time.perf_counter() - started,
        )
    comparison = compare(
        benchmark.expected.get("results", {}), result, benchmark.meta.get("tolerance")
    )
    invariant_failures = check_invariants(benchmark.expected, result)
    status = "pass" if comparison.passed and not invariant_failures else "fail"
    return RunResult(
        benchmark=benchmark,
        status=status,
        comparison=comparison,
        invariant_failures=invariant_failures,
        duration_s=time.perf_counter() - started,
        result=result,
    )


def run_all(benchmarks: Iterable[Benchmark]) -> list[RunResult]:
    return [run_benchmark(b) for b in benchmarks]


def validate_benchmark(benchmark: Benchmark) -> list[str]:
    """Schema-validate a benchmark descriptor and its expected result."""
    errors = [f"benchmark.yaml: {e}" for e in validate(benchmark.meta, load_schema("benchmark.schema.json"))]
    if not benchmark.expected:
        errors.append("expected/expected.yaml: missing")
        return errors
    errors += [
        f"expected.yaml: {e}"
        for e in validate(benchmark.expected, load_schema("expected_result.schema.json"))
    ]
    if benchmark.expected.get("benchmark_id") != benchmark.meta.get("benchmark_id"):
        errors.append("expected.yaml: benchmark_id does not match benchmark.yaml")
    # The headline values in benchmark.yaml must not drift from the machine
    # checked expectations.
    headline = benchmark.meta.get("expected_behavior") or {}
    results = benchmark.expected.get("results") or {}
    for key, value in headline.items():
        comparison = compare({key: value}, results, benchmark.meta.get("tolerance"))
        if not comparison.passed:
            errors.append(
                f"expected_behavior.{key} disagrees with expected/expected.yaml results"
            )
    for name, relative in (benchmark.meta.get("inputs") or {}).items():
        if not (benchmark.path.parent / relative).exists():
            errors.append(f"inputs.{name}: file {relative} not found")
    readme = benchmark.path.parent / "README.md"
    if not readme.exists():
        errors.append("README.md: missing")
    return errors
