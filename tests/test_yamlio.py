"""The fallback YAML parser agrees with PyYAML on everything the suite writes."""

from pathlib import Path

from wg_benchmarks import yamlio

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_without_pyyaml(text):
    original = yamlio._pyyaml
    yamlio._pyyaml = None
    try:
        return yamlio.loads(text)
    finally:
        yamlio._pyyaml = original


def test_round_trip_of_awkward_values():
    data = {
        "numeric_keys": {"2": 8.0, "15": None},
        "floats": [1e-06, 0.1, -2.5e20, 3.0],
        "flags": {"yes_like": "true", "real": True},
        "nested": [{"id": "a", "sub": {"x": [1, 2]}}, {"id": "b", "sub": None}],
        "text": "a plain string with spaces",
    }
    text = yamlio.dumps(data)
    assert yamlio.loads(text) == data
    assert _load_without_pyyaml(text) == data


def test_fallback_parser_matches_pyyaml_on_every_repository_document():
    if yamlio._pyyaml is None:  # pragma: no cover - PyYAML absent
        return
    documents = sorted((REPO_ROOT / "benchmarks").rglob("*.yaml"))
    assert documents, "no benchmark documents found"
    for path in documents:
        text = path.read_text(encoding="utf-8")
        assert yamlio.loads(text) == _load_without_pyyaml(text), path
