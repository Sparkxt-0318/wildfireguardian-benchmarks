"""``wg-benchmarks`` command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import reporting, yamlio
from .compare import compare
from .mutations import MUTATIONS
from .runner import REPO_ROOT, discover, run_all, run_benchmark, select, validate_benchmark

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


def _colour(text: str, colour: str, enabled: bool) -> str:
    return f"{colour}{text}{RESET}" if enabled else text


def _status_colour(status: str) -> str:
    return {"pass": GREEN, "fail": RED, "error": YELLOW}.get(status, "")


def cmd_list(args) -> int:
    benchmarks = select(discover(), ids=args.id, categories=args.category, labels=args.label)
    if args.json:
        print(json.dumps([b.meta for b in benchmarks], indent=2))
        return 0
    print(f"{'ID':<11} {'LBL':<4} {'CATEGORY':<21} {'EXACTNESS':<18} TITLE")
    for benchmark in benchmarks:
        print(
            f"{benchmark.benchmark_id:<11} {benchmark.label:<4} {benchmark.category:<21} "
            f"{benchmark.meta['exactness']:<18} {benchmark.meta['title']}"
        )
    print(f"\n{len(benchmarks)} benchmark(s)")
    return 0


def cmd_run(args) -> int:
    colour = sys.stdout.isatty() and not args.no_colour
    benchmarks = select(discover(), ids=args.id, categories=args.category, labels=args.label)
    if not benchmarks:
        print("no benchmarks matched", file=sys.stderr)
        return 2
    failures = 0
    for benchmark in benchmarks:
        outcome = run_benchmark(benchmark)
        failures += not outcome.passed
        tag = _colour(outcome.status.upper(), _status_colour(outcome.status), colour)
        print(f"{benchmark.benchmark_id} {benchmark.label:<3} {tag:<16} {benchmark.meta['title']}")
        if not outcome.passed:
            for difference in (outcome.comparison.differences if outcome.comparison else [])[:10]:
                print(f"    - {difference}")
            for invariant in outcome.invariant_failures:
                print(f"    - invariant: {invariant}")
            if outcome.error:
                print(f"    - error: {outcome.error}")
        if args.verbose and outcome.result is not None:
            print(yamlio.dumps(outcome.result))
    total = len(benchmarks)
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


def cmd_run_category(args) -> int:
    args.id, args.label, args.category = [], [], [args.category_name]
    return cmd_run(args)


def cmd_validate(args) -> int:
    benchmarks = discover()
    problems = 0
    for benchmark in benchmarks:
        errors = validate_benchmark(benchmark)
        if errors:
            problems += 1
            print(f"{benchmark.benchmark_id} ({benchmark.directory})")
            for error in errors:
                print(f"    - {error}")
    print(f"\n{len(benchmarks) - problems}/{len(benchmarks)} benchmark descriptors valid")
    return 1 if problems else 0


def cmd_validate_results(args) -> int:
    """Check an external implementation's result documents against the suite."""
    directory = Path(args.path)
    if not directory.is_dir():
        print(f"{directory} is not a directory", file=sys.stderr)
        return 2
    benchmarks = {b.benchmark_id: b for b in discover()}
    checked = failures = 0
    missing = []
    for benchmark_id, benchmark in sorted(benchmarks.items()):
        candidates = [
            directory / f"{benchmark_id}.yaml",
            directory / f"{benchmark_id}.yml",
            directory / f"{benchmark_id}.json",
        ]
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            missing.append(benchmark_id)
            continue
        checked += 1
        if path.suffix == ".json":
            with open(path, "r", encoding="utf-8") as handle:
                document = json.load(handle)
        else:
            document = yamlio.load(path)
        payload = document.get("results", document)
        comparison = compare(
            benchmark.expected.get("results", {}), payload, benchmark.meta.get("tolerance")
        )
        status = "PASS" if comparison.passed else "FAIL"
        failures += not comparison.passed
        print(f"{benchmark_id} {status}")
        for difference in comparison.differences[:10]:
            print(f"    - {difference}")
    print(f"\n{checked - failures}/{checked} submitted result(s) match the expected answers")
    if missing:
        print(f"{len(missing)} benchmark(s) had no submitted result: {', '.join(missing[:10])}"
              + (" ..." if len(missing) > 10 else ""))
    return 1 if failures or not checked else 0


def cmd_report(args) -> int:
    out = Path(args.out) if args.out else REPO_ROOT / "reports"
    written = reporting.write_all(out, run_mutations=not args.skip_mutations)
    for path in written:
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def cmd_mutate(args) -> int:
    ids = args.mutation or sorted(MUTATIONS)
    matrix = reporting.mutation_matrix(only=ids)
    undetected = [m for m, row in matrix.items() if not row["detected_by"]]
    for mutation_id, row in matrix.items():
        detectors = ", ".join(row["detected_by"]) or "-- NOT DETECTED --"
        print(f"{mutation_id:<34} {detectors}")
    print(f"\n{len(matrix) - len(undetected)}/{len(matrix)} mutations detected")
    if undetected:
        print("undetected: " + ", ".join(undetected))
    return 1 if undetected and args.strict else 0


def cmd_figures(args) -> int:
    from . import plotting

    written = plotting.write_all()
    for path in written:
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wg-benchmarks",
        description="WildfireGuardian benchmark suite: small, transparent, hand-checkable cases.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_filters(sub):
        sub.add_argument("id", nargs="*", help="benchmark ids, e.g. WG-BM-001")
        sub.add_argument("--category", "-c", action="append", default=[], help="filter by category")
        sub.add_argument("--label", "-l", action="append", default=[], help="filter by family label, e.g. F5")

    listing = subparsers.add_parser("list", help="list benchmarks")
    add_filters(listing)
    listing.add_argument("--json", action="store_true")
    listing.set_defaults(func=cmd_list)

    running = subparsers.add_parser("run", help="run benchmarks against the reference solvers")
    add_filters(running)
    running.add_argument("--verbose", "-v", action="store_true", help="print the full result document")
    running.add_argument("--no-colour", action="store_true")
    running.set_defaults(func=cmd_run)

    by_category = subparsers.add_parser("run-category", help="run every benchmark in one category")
    by_category.add_argument("category_name")
    by_category.add_argument("--verbose", "-v", action="store_true")
    by_category.add_argument("--no-colour", action="store_true")
    by_category.set_defaults(func=cmd_run_category)

    validating = subparsers.add_parser("validate", help="schema-validate every benchmark descriptor")
    validating.set_defaults(func=cmd_validate)

    external = subparsers.add_parser(
        "validate-results",
        help="compare an external implementation's results directory against the expected answers",
    )
    external.add_argument("path")
    external.set_defaults(func=cmd_validate_results)

    reporting_parser = subparsers.add_parser("report", help="regenerate the reports/ directory")
    reporting_parser.add_argument("--out", default=None)
    reporting_parser.add_argument("--skip-mutations", action="store_true")
    reporting_parser.set_defaults(func=cmd_report)

    mutating = subparsers.add_parser("mutate", help="run the mutation tests")
    mutating.add_argument("--mutation", "-m", action="append", default=[])
    mutating.add_argument("--strict", action="store_true", help="exit non-zero if a mutation is undetected")
    mutating.set_defaults(func=cmd_mutate)

    figures = subparsers.add_parser("figures", help="regenerate benchmark figures")
    figures.set_defaults(func=cmd_figures)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
