#!/usr/bin/env python3
"""Check an external implementation's results against the expected answers.

Usage::

    python tools/validators/validate_results.py path/to/results/

The directory should contain one document per benchmark, named
``WG-BM-0NN.yaml`` (or ``.yml`` / ``.json``).  Each document is either the
result mapping itself or a mapping with a ``results`` key holding it.  Only the
keys the benchmark pins down are compared; extra keys are ignored, so an
implementation may report as much additional detail as it likes.

This is the integration entry point for a WildfireGuardian repository: it never
imports the implementation under test, it only reads what that implementation
wrote.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from wg_benchmarks.cli import main as cli_main  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        return 2
    return cli_main(["validate-results", argv[0]])


if __name__ == "__main__":
    raise SystemExit(main())
