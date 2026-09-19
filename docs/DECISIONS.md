# Decision log

Numbered, dated, and kept even when superseded. A decision that is reversed gets
a new entry; the old one stays with a pointer.

---

## WG-D-001 — The repository is independent of production code
**Status:** accepted

Expected answers derived with the implementation's own code are not independent
tests of it. Nothing here imports a WildfireGuardian production package, and the
only integration path is the file-based `validate-results` command.

---

## WG-D-002 — Expected values are authored, never harvested
**Status:** accepted

Every value in `expected/expected.yaml` is written by hand in
`tools/authoring/*.py` from the scenario definition. No value is copied from a
solver run.

*Evidence that this matters:* during construction, WG-BM-036 failed on its first
run. The authored value was right and the reference solver was wrong — it
maximised `worst_case_loss` over the whole shared loss table rather than over the
ensemble's own scenarios. Had the expected value been harvested, the bug would
have been enshrined as the expected answer.

---

## WG-D-003 — Interval safety (WG-SEM-1) is the suite's traversal convention
**Status:** accepted

A traversal is feasible only if the whole interval fits in one open window. The
alternatives (entry-time-only, partial traversal, reversible) are defensible and
rejected, and WG-BM-019 reports what the entry-time rule would have concluded so
that the choice is visible rather than buried.

---

## WG-D-004 — Waiting is opt-in per scenario
**Status:** accepted

Both answers are always reported (`feasible_with_waiting`,
`feasible_without_waiting`); the declared one is whichever the scenario says.
Waiting is a real operational instruction and requires a survivable holding
point, so it cannot be a global default.

---

## WG-D-005 — Dispatch feasibility is a set, not a scalar
**Status:** accepted

Reporting only a latest feasible dispatch time asserts monotonicity, which is
false whenever a corridor reopens. See WG-BM-026.

---

## WG-D-006 — Zero and negative expected answers are first-class
**Status:** accepted

WG-BM-032 expects a forecast to add exactly nothing; WG-BM-041 expects perfect
information to be worth nothing; WG-BM-033 and WG-BM-030 expect negative value.
Without these a suite rewards complexity.

---

## WG-D-007 — No required third-party dependencies at runtime
**Status:** accepted

PyYAML is used when present and a restricted-subset parser is used when it is
not; the JSON Schema validator falls back to a built-in subset implementation;
figures are hand-written SVG. `pytest` is a development dependency only.

Cost: two parsers and two validators to keep in agreement. Mitigation:
`tests/test_yamlio.py` checks the fallback parser against PyYAML on every
document in the repository.

---

## WG-D-008 — Two independent solver implementations
**Status:** accepted

`wg_benchmarks/solvers/` holds the primary reference solvers. `tools/analytic_solvers/`
holds slower, cruder, independently written enumerators. `tests/test_cross_check.py`
runs them against each other. Where they disagree the suite cannot say which is
right, and that is the correct outcome: a human has to look.

---

## WG-D-009 — Mutation testing is part of the suite, not an extra
**Status:** accepted

Twenty-four plausible bugs are injectable through a registry, and every one must
be detected by at least one benchmark. A benchmark may not declare a detection
it does not achieve (`tests/test_mutations.py` enforces both directions).

---

## WG-D-010 — Benchmark ids are permanent
**Status:** accepted

`WG-BM-0NN` ids are never reused and never renumbered. Family labels (`F5`) are
a convenience and may be reorganised; the id is the reference.

---

## WG-D-011 — Aspect is the bearing of steepest descent, `null` on flat ground
**Status:** accepted

Both halves matter. Reporting the ascent bearing inverts every aspect-dependent
correction; reporting `0` on flat ground biases them on exactly the terrain
where they should be absent.

---

## WG-D-012 — A benchmark may not overclaim its detection power
**Status:** accepted

WG-BM-028 originally declared that it detected `skill_implies_value`. It does
not: with two equally valuable forecasts, a skill-based recommendation picks an
equally good policy and the declared answer does not change. The declaration was
removed and the README now says so explicitly.

---

## WG-D-013 — The traffic benchmark stipulates congested travel times
**Status:** accepted

WG-BM-027 takes two congested travel times as inputs rather than deriving them
from a queueing model. A benchmark that needs a traffic model to state its
expected answer is no longer hand-checkable, and the scientific content here is
that ingress and egress share a road, not how congestion forms.
