#!/usr/bin/env python3
"""Schema- and structure-validate every benchmark in the repository.

Checks performed:

1. ``benchmark.yaml`` validates against ``schemas/benchmark.schema.json``;
2. ``expected/expected.yaml`` validates against
   ``schemas/expected_result.schema.json``;
3. the headline ``expected_behavior`` block agrees with the machine-checked
   ``results`` block (so the human-readable summary cannot drift);
4. every declared input file exists and every benchmark has a README;
5. benchmark ids are unique, contiguous and match their directory name;
6. family labels are unique;
7. every registered mutation is claimed by at least one benchmark.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from wg_benchmarks.mutations import MUTATIONS  # noqa: E402
from wg_benchmarks.registry import SOLVERS  # noqa: E402
from wg_benchmarks.runner import discover, validate_benchmark  # noqa: E402


def check_repository(benchmarks) -> list[str]:
    problems = []
    ids = [b.benchmark_id for b in benchmarks]
    labels = [b.label for b in benchmarks]
    if len(set(ids)) != len(ids):
        problems.append("benchmark ids are not unique")
    if len(set(labels)) != len(labels):
        problems.append("family labels are not unique")
    numbers = sorted(int(i.rsplit("-", 1)[1]) for i in ids)
    if numbers != list(range(1, len(numbers) + 1)):
        problems.append(f"benchmark ids are not contiguous from 001: {numbers}")
    for benchmark in benchmarks:
        directory = benchmark.path.parent.name
        if not directory.startswith(benchmark.benchmark_id):
            problems.append(f"{benchmark.benchmark_id}: directory {directory} does not start with its id")
        if not re.match(rf"^{benchmark.benchmark_id}_{benchmark.label}_", directory):
            problems.append(f"{benchmark.benchmark_id}: directory name does not encode the label {benchmark.label}")
        if benchmark.meta["solver"] not in SOLVERS:
            problems.append(f"{benchmark.benchmark_id}: unknown solver {benchmark.meta['solver']}")
        for mutation in benchmark.meta.get("mutations_expected_to_fail") or []:
            if mutation not in MUTATIONS:
                problems.append(f"{benchmark.benchmark_id}: unknown mutation {mutation}")
    claimed = {
        mutation
        for benchmark in benchmarks
        for mutation in (benchmark.meta.get("mutations_expected_to_fail") or [])
    }
    for mutation in sorted(set(MUTATIONS) - claimed):
        problems.append(f"mutation {mutation} is not claimed by any benchmark")
    return problems


def main() -> int:
    benchmarks = discover()
    failures = 0
    for benchmark in benchmarks:
        errors = validate_benchmark(benchmark)
        if errors:
            failures += 1
            print(f"FAIL {benchmark.benchmark_id} ({benchmark.directory})")
            for error in errors:
                print(f"       {error}")
    problems = check_repository(benchmarks)
    for problem in problems:
        print(f"FAIL repository: {problem}")
    total = len(benchmarks)
    print(f"\n{total - failures}/{total} descriptors valid, {len(problems)} repository problem(s)")
    return 1 if failures or problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
