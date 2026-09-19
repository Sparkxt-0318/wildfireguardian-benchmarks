"""Comparison of computed benchmark results against expected results.

Rules (deliberately strict — a benchmark that quietly rounds away a discrepancy
is worse than no benchmark):

* Types must match: ``True`` is not ``1``, ``None`` is not ``0.0``.
* Numbers compare with an absolute and a relative tolerance, both taken from the
  benchmark's ``tolerance`` block.  Default tolerance is ``1e-9`` absolute,
  ``0`` relative: exact benchmarks must be exact.
* Lists compare element-wise, in order, with equal length.
* Mappings compare on the *expected* keys only.  Extra keys in the computed
  result are allowed (a solver may report more than the benchmark pins down);
  missing keys are failures.
* A key ending in ``_unordered`` compares as a multiset.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DEFAULT_ABS_TOL = 1e-9
DEFAULT_REL_TOL = 0.0


@dataclass
class Difference:
    path: str
    expected: Any
    actual: Any
    reason: str

    def __str__(self) -> str:  # pragma: no cover - formatting only
        return f"{self.path}: expected {self.expected!r}, got {self.actual!r} ({self.reason})"


@dataclass
class ComparisonResult:
    passed: bool
    differences: list[Difference] = field(default_factory=list)
    checked: int = 0


def _tolerances(tolerance: dict | None, path: str) -> tuple[float, float]:
    """Resolve (abs_tol, rel_tol) for a given result path.

    ``tolerance`` may carry a ``default`` entry plus per-field overrides keyed by
    the leaf name (e.g. ``time_min``) or the full dotted path.
    """
    abs_tol, rel_tol = DEFAULT_ABS_TOL, DEFAULT_REL_TOL
    if not tolerance:
        return abs_tol, rel_tol

    def apply(entry: Any) -> tuple[float, float]:
        if isinstance(entry, dict):
            return (
                float(entry.get("abs", abs_tol)),
                float(entry.get("rel", rel_tol)),
            )
        return float(entry), rel_tol

    if "default" in tolerance:
        abs_tol, rel_tol = apply(tolerance["default"])
    leaf = path.rsplit(".", 1)[-1].split("[")[0]
    for key in (path, leaf):
        if key in tolerance:
            abs_tol, rel_tol = apply(tolerance[key])
            break
    return abs_tol, rel_tol


def _numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def compare(expected: Any, actual: Any, tolerance: dict | None = None) -> ComparisonResult:
    result = ComparisonResult(passed=True)
    _walk(expected, actual, "", tolerance or {}, result)
    result.passed = not result.differences
    return result


def _walk(expected: Any, actual: Any, path: str, tolerance: dict, result: ComparisonResult) -> None:
    label = path or "<root>"
    result.checked += 1

    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            result.differences.append(Difference(label, expected, actual, "type mismatch: expected mapping"))
            return
        for key, sub_expected in expected.items():
            sub_path = f"{path}.{key}" if path else str(key)
            if key not in actual:
                result.differences.append(Difference(sub_path, sub_expected, None, "missing key in result"))
                continue
            _walk(sub_expected, actual[key], sub_path, tolerance, result)
        return

    if isinstance(expected, list):
        if not isinstance(actual, list):
            result.differences.append(Difference(label, expected, actual, "type mismatch: expected sequence"))
            return
        if len(expected) != len(actual):
            result.differences.append(
                Difference(label, expected, actual, f"length mismatch: {len(expected)} != {len(actual)}")
            )
            return
        if label.endswith("_unordered"):
            remaining = list(actual)
            for item in expected:
                match = None
                for candidate in remaining:
                    probe = ComparisonResult(passed=True)
                    _walk(item, candidate, label, tolerance, probe)
                    if not probe.differences:
                        match = candidate
                        break
                if match is None:
                    result.differences.append(Difference(label, item, actual, "no matching element (unordered)"))
                else:
                    remaining.remove(match)
            return
        for index, (sub_expected, sub_actual) in enumerate(zip(expected, actual)):
            _walk(sub_expected, sub_actual, f"{path}[{index}]", tolerance, result)
        return

    if expected is None:
        if actual is not None:
            result.differences.append(Difference(label, expected, actual, "expected null"))
        return

    if isinstance(expected, bool):
        if not isinstance(actual, bool) or expected != actual:
            result.differences.append(Difference(label, expected, actual, "boolean mismatch"))
        return

    if _numeric(expected):
        if not _numeric(actual):
            result.differences.append(Difference(label, expected, actual, "type mismatch: expected number"))
            return
        abs_tol, rel_tol = _tolerances(tolerance, path)
        allowed = max(abs_tol, rel_tol * abs(float(expected)))
        if abs(float(expected) - float(actual)) > allowed:
            result.differences.append(
                Difference(label, expected, actual, f"|delta| = {abs(float(expected) - float(actual)):.6g} > {allowed:.6g}")
            )
        return

    if expected != actual:
        result.differences.append(Difference(label, expected, actual, "value mismatch"))
