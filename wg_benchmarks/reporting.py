"""Generated reports: catalogue, coverage matrix, mutation matrix, run results."""

from __future__ import annotations

from pathlib import Path

from . import mutations
from .runner import REPO_ROOT, discover, run_all, run_benchmark

GENERATED_NOTE = (
    "<!-- GENERATED FILE - regenerate with `python -m wg_benchmarks report`. "
    "Edits here will be overwritten. Generation is deterministic: no timestamps, "
    "no timings, so a regenerated report is a no-op diff unless something changed. -->"
)


# --------------------------------------------------------------------------
# mutation testing
# --------------------------------------------------------------------------


def mutation_matrix(only: list[str] | None = None) -> dict[str, dict]:
    """Run the suite once per mutation and record which benchmarks catch it.

    A benchmark *detects* a mutation when it passes on the clean solvers and
    fails with the mutation injected.  A benchmark that already fails is
    excluded, because a red test proves nothing.
    """
    benchmarks = discover()
    baseline = {r.benchmark.benchmark_id: r.passed for r in run_all(benchmarks)}
    matrix: dict[str, dict] = {}
    for mutation_id in (only or sorted(mutations.MUTATIONS)):
        detected: list[str] = []
        with mutations.activate(mutation_id):
            for benchmark in benchmarks:
                if not baseline.get(benchmark.benchmark_id):
                    continue
                if not run_benchmark(benchmark).passed:
                    detected.append(benchmark.benchmark_id)
        declared = [
            b.benchmark_id
            for b in benchmarks
            if mutation_id in (b.meta.get("mutations_expected_to_fail") or [])
        ]
        matrix[mutation_id] = {
            "detected_by": detected,
            "declared_detectors": declared,
            "declared_but_undetected": sorted(set(declared) - set(detected)),
            "mutation": mutations.MUTATIONS[mutation_id],
        }
    return matrix


# --------------------------------------------------------------------------
# reports
# --------------------------------------------------------------------------


def catalog_markdown() -> str:
    benchmarks = discover()
    lines = [
        GENERATED_NOTE,
        "",
        "# Benchmark catalogue",
        "",
        f"{len(benchmarks)} benchmarks.",
        "",
        "`exactness` says how much trust the expected answer deserves:",
        "",
        "| value | meaning |",
        "|---|---|",
        "| `exact_analytic` | closed form derived by hand in the benchmark README |",
        "| `exact_enumeration` | finite exhaustive enumeration; no approximation |",
        "| `seeded_stochastic` | deterministic given the seed, checked within a stated tolerance |",
        "| `qualitative` | an ordering, a sign or a flag rather than a number |",
        "",
        "| ID | Label | Category | Difficulty | Exactness | Hand-checkable | Title |",
        "|---|---|---|---|---|---|---|",
    ]
    for benchmark in benchmarks:
        lines.append(
            "| `{id}` | {label} | {category} | {difficulty} | `{exactness}` | {hand} | {title} |".format(
                id=benchmark.benchmark_id,
                label=benchmark.label,
                category=benchmark.category,
                difficulty=benchmark.meta["difficulty"],
                exactness=benchmark.meta["exactness"],
                hand="yes" if benchmark.meta.get("hand_checkable") else "no",
                title=benchmark.meta["title"],
            )
        )
    lines += ["", "## Purpose of each benchmark", ""]
    for benchmark in benchmarks:
        lines.append(
            f"- **{benchmark.benchmark_id} ({benchmark.label})** — {benchmark.meta['purpose']} "
            f"<br/>`{benchmark.directory}`"
        )
    return "\n".join(lines) + "\n"


def coverage_markdown(matrix: dict[str, dict] | None) -> str:
    benchmarks = discover()
    failure_modes: dict[str, list[str]] = {}
    for benchmark in benchmarks:
        for mode in benchmark.meta.get("detects", []):
            failure_modes.setdefault(mode, []).append(benchmark.benchmark_id)

    lines = [
        GENERATED_NOTE,
        "",
        "# Coverage",
        "",
        "## Failure mode coverage",
        "",
        "Each row is a scientific failure mode the project cares about and the "
        "benchmarks that are designed to expose it.",
        "",
        "| Failure mode | Benchmarks | Count |",
        "|---|---|---|",
    ]
    for mode in sorted(failure_modes):
        ids = ", ".join(f"`{i}`" for i in sorted(failure_modes[mode]))
        lines.append(f"| `{mode}` | {ids} | {len(failure_modes[mode])} |")

    lines += [
        "",
        "## Category coverage",
        "",
        "| Category | Benchmarks |",
        "|---|---|",
    ]
    by_category: dict[str, list[str]] = {}
    for benchmark in benchmarks:
        by_category.setdefault(benchmark.category, []).append(benchmark.benchmark_id)
    for category in sorted(by_category):
        lines.append(f"| {category} | {len(by_category[category])} |")

    if matrix is not None:
        detected = sum(1 for row in matrix.values() if row["detected_by"])
        lines += [
            "",
            "## Mutation coverage",
            "",
            f"{detected} of {len(matrix)} injected bugs are caught by at least one benchmark.",
            "",
            "| Mutation | Failure mode | Detected by |",
            "|---|---|---|",
        ]
        for mutation_id in sorted(matrix):
            row = matrix[mutation_id]
            detectors = ", ".join(f"`{i}`" for i in row["detected_by"]) or "**none**"
            lines.append(
                f"| `{mutation_id}` | `{row['mutation'].failure_mode}` | {detectors} |"
            )
    return "\n".join(lines) + "\n"


def mutation_markdown(matrix: dict[str, dict]) -> str:
    lines = [
        GENERATED_NOTE,
        "",
        "# Mutation test results",
        "",
        "Each mutation is a deliberate, plausible implementation bug injected into "
        "the reference solvers.  A benchmark *detects* a mutation when it passes "
        "clean and fails mutated.",
        "",
        "| Mutation | Description | Detected by | Declared but missed |",
        "|---|---|---|---|",
    ]
    for mutation_id in sorted(matrix):
        row = matrix[mutation_id]
        mutation = row["mutation"]
        detectors = ", ".join(f"`{i}`" for i in row["detected_by"]) or "**NONE**"
        missed = ", ".join(f"`{i}`" for i in row["declared_but_undetected"]) or "--"
        lines.append(f"| `{mutation_id}` | {mutation.title} | {detectors} | {missed} |")
    undetected = [m for m, row in matrix.items() if not row["detected_by"]]
    lines += [
        "",
        f"**{len(matrix) - len(undetected)} / {len(matrix)} mutations detected.**",
        "",
    ]
    if undetected:
        lines += ["Undetected mutations (coverage gaps):", ""]
        lines += [f"- `{m}` — {matrix[m]['mutation'].description}" for m in undetected]
        lines.append("")
    return "\n".join(lines) + "\n"


def results_markdown() -> str:
    outcomes = run_all(discover())
    passed = sum(1 for o in outcomes if o.passed)
    lines = [
        GENERATED_NOTE,
        "",
        "# Last recorded suite run",
        "",
        f"{passed}/{len(outcomes)} benchmarks pass against the reference solvers.",
        "",
        "| ID | Label | Status | Title |",
        "|---|---|---|---|",
    ]
    for outcome in outcomes:
        lines.append(
            f"| `{outcome.benchmark.benchmark_id}` | {outcome.benchmark.label} | "
            f"{outcome.status.upper()} | {outcome.benchmark.meta['title']} |"
        )
    failures = [o for o in outcomes if not o.passed]
    if failures:
        lines += ["", "## Failures", ""]
        for outcome in failures:
            lines.append(f"### {outcome.benchmark.benchmark_id}")
            lines.append("")
            lines.append("```")
            lines.append(outcome.summary())
            lines.append("```")
            lines.append("")
    return "\n".join(lines) + "\n"


def write_all(out: Path | None = None, run_mutations: bool = True) -> list[Path]:
    out = out or (REPO_ROOT / "reports")
    out.mkdir(parents=True, exist_ok=True)
    matrix = mutation_matrix() if run_mutations else None
    written = []
    documents = {
        "BENCHMARK_CATALOG.md": catalog_markdown(),
        "COVERAGE.md": coverage_markdown(matrix),
        "RESULTS.md": results_markdown(),
    }
    if matrix is not None:
        documents["MUTATION_MATRIX.md"] = mutation_markdown(matrix)
    for name, text in documents.items():
        path = out / name
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written
