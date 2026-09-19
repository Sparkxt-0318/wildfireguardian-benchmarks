"""Comparison semantics: strict types, explicit tolerances, extra keys allowed."""

from wg_benchmarks.compare import compare


def test_types_are_strict():
    assert not compare({"a": True}, {"a": 1}).passed
    assert not compare({"a": None}, {"a": 0.0}).passed
    assert not compare({"a": 1.0}, {"a": "1.0"}).passed


def test_default_tolerance_is_tight():
    assert compare({"a": 1.0}, {"a": 1.0 + 1e-12}).passed
    assert not compare({"a": 1.0}, {"a": 1.0 + 1e-6}).passed


def test_named_tolerance_overrides_default():
    tolerance = {"default": 1e-9, "width": 0.5}
    assert compare({"width": 10.0}, {"width": 10.4}, tolerance).passed
    assert not compare({"width": 10.0}, {"width": 10.6}, tolerance).passed


def test_extra_keys_allowed_missing_keys_fail():
    assert compare({"a": 1}, {"a": 1, "b": 2}).passed
    assert not compare({"a": 1, "b": 2}, {"a": 1}).passed


def test_nested_structures():
    expected = {"outer": {"inner": [1.0, 2.0]}}
    assert compare(expected, {"outer": {"inner": [1.0, 2.0]}}).passed
    assert not compare(expected, {"outer": {"inner": [1.0, 2.0, 3.0]}}).passed
