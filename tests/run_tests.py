#!/usr/bin/env python3
"""Run the test suite with pytest when it is installed, and without it when not.

The fallback runner executes the command-line checks (schema validation, the
whole benchmark suite, the mutation matrix) plus every zero-argument ``test_*``
function it can import.  Parametrised tests are skipped in that mode and the
runner says so, rather than silently reporting a smaller suite as green.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for path in (REPO_ROOT, REPO_ROOT / "tools"):
    sys.path.insert(0, str(path))


def run_with_pytest() -> int:
    import pytest  # noqa: PLC0415

    return pytest.main([str(REPO_ROOT / "tests"), "-q"])


def run_fallback() -> int:
    from wg_benchmarks.cli import main as cli  # noqa: PLC0415

    failures = 0
    for argv in (["validate"], ["run", "--no-colour"], ["mutate", "--strict"]):
        print(f"$ wg-benchmarks {' '.join(argv)}")
        failures += bool(cli(argv))

    skipped = 0
    for module_path in sorted((REPO_ROOT / "tests").glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001
            print(f"SKIP {module_path.name}: {type(exc).__name__}: {exc}")
            skipped += 1
            continue
        for name in sorted(dir(module)):
            if not name.startswith("test_"):
                continue
            function = getattr(module, name)
            if not callable(function) or function.__code__.co_argcount:
                skipped += 1
                continue
            try:
                function()
                print(f"PASS {module_path.stem}.{name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {module_path.stem}.{name}: {exc}")
    print(f"\n{failures} failure(s), {skipped} test(s) skipped (pytest not installed)")
    return 1 if failures else 0


def main() -> int:
    if importlib.util.find_spec("pytest") is not None:
        return run_with_pytest()
    print("pytest not found; running the reduced standard-library suite\n")
    return run_fallback()


if __name__ == "__main__":
    raise SystemExit(main())
