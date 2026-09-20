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

---

## WG-D-014 — The exactness vocabulary is the four uppercase classes
**Status:** accepted, supersedes the lower-case vocabulary used in v0.0

`exactness` now takes `CLOSED_FORM`, `FINITE_ENUMERATION`, `NUMERIC_REFERENCE`
or `SEEDED_STOCHASTIC_VALIDATION`. The mapping from the previous vocabulary was
mechanical (`exact_analytic` → `CLOSED_FORM`, `exact_enumeration` →
`FINITE_ENUMERATION`, `seeded_stochastic` → `SEEDED_STOCHASTIC_VALIDATION`), and
the unused `qualitative` value was dropped.

This is the **only** change made to the 43 deterministic benchmarks in the v0.1
extension. No expected value, input, convention or tolerance was touched, and
all 43 still pass; the diff is 43 single-token lines. `NUMERIC_REFERENCE` is new
and carries the rule that a Monte Carlo estimate is never described as exact.

---

## WG-D-015 — Expected values for stochastic benchmarks come from four sources only
**Status:** accepted

Closed-form probability, exact finite enumeration, an independently implemented
brute force, or analytically justified numerical integration with a declared
tolerance. Monte Carlo is not permitted as truth where an exact answer exists,
and a Monte Carlo approximation is never described as exact.

In practice 51 of the 66 benchmarks are `CLOSED_FORM`, 14 are
`FINITE_ENUMERATION`, and one — WG-BM-037's bootstrap — is
`SEEDED_STOCHASTIC_VALIDATION` with its analytic counterparts pinned exactly
alongside.

---

## WG-D-016 — Acquisition is recommended by decision value, not information gain
**Status:** accepted

`recommended_observation` is the observation with the greatest **operational**
EVSI, and it is `null` when no observation has positive operational value.
`observations_worth_acquiring` lists those that do.

*How this was arrived at:* WG-BM-050 (K7) originally declared that it detected
the `choose_by_information_gain` mutation, and `tests/test_mutations.py` showed
that it did not — with a single observation, ranking by information and ranking
by value select the same one. Rather than drop the claim, the solver was changed
so that it answers the question the benchmark is actually about: *should this be
acquired at all?* The clean solver now says no (EVSI is exactly zero) and the
mutated one says yes. The detection is real, and the solver is better.

---

## WG-D-017 — A benchmark family may span more than one authoring script
**Status:** accepted

The K family has fifteen members and is authored in
`author_probabilistic_forecast.py` (K1-K5) and `author_bayesian_inference.py`
(K6-K15). The split is by subject, and the family label remains the unit of
reference.

---

## WG-D-018 — The suite is frozen at v0.1.0
**Status:** accepted

After this extension the suite stops growing. A new benchmark is added only when
a real project failure exposes a missing case — not because a family looks
asymmetric or a category looks thin. The reason is that an unused benchmark
still has to be maintained, still has to be kept honest about what it detects,
and still dilutes the coverage reports it appears in.
