#!/usr/bin/env python3
"""Regenerate every benchmark figure.

Equivalent to ``python -m wg_benchmarks figures``; kept here so the tools/
layout matches the documented repository structure.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from wg_benchmarks import plotting  # noqa: E402


def main() -> int:
    for path in plotting.write_all():
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
