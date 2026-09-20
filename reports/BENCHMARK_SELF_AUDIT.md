# Benchmark self-audit

Every case in which **this repository was wrong** and had to be corrected.

It is kept because the two failure modes it records are the ones a benchmark
suite is least able to detect in itself:

* a reference implementation can be wrong, and if its output had been used as
  the expected answer the bug would have become the specification;
* a benchmark can claim to detect something it does not, and a green mutation
  matrix will not say so unless the claim is checked in both directions.

Nothing here is hidden or summarised away. A suite that reports only its
successes is asking to be trusted rather than checked.

---

## A. The reference solver was wrong and the benchmark caught it

### SA-1 — WG-BM-036: `worst_case_loss` maximised over the wrong set

**Found:** on the first run of WG-BM-036 (H3, ensemble size trap), during
construction of the deterministic suite.

**Symptom:**

```
ensembles.base.worst_case_loss.policy_a: expected 10.0, got 300.0
```

**Cause:** `analyse_ensemble` computed `worst_case_loss` as
`max(losses[action].values())` — the maximum over the entire shared loss table,
which also carries rows for scenarios belonging to a *different* ensemble. The
five-member ensemble's worst case for `policy_a` was therefore reported as 300,
a value that only exists in the seven-member one.

**Resolution:** the maximum is now taken over the ensemble's own scenarios. The
authored expectation was right; the solver was fixed.

**Why it matters:** this is the concrete justification for WG-D-002. Had the
expected value been harvested from a solver run — the normal way to build a
regression suite — the bug would have been enshrined as the expected answer and
the benchmark would have passed for ever while asserting something false.

---

## B. A benchmark claimed a detection it did not achieve

### SA-2 — WG-BM-028 overclaimed `skill_implies_value`

**Found:** by `tests/test_mutations.py::test_declared_detectors_actually_detect`,
which checks the `mutations_expected_to_fail` list in both directions.

**Cause:** WG-BM-028 (G1) has two forecasts of equal decision value and
different skill. Ranking by skill selects an *equally good* policy, so the
benchmark's declared answer does not change and the bug produces no failure.

**Resolution:** the declaration was removed and the benchmark's README now says
explicitly that it documents the conflation without detecting it. Recorded as
WG-D-012.

**Why it matters:** the overclaim was plausible — the benchmark is *about* the
skill/value distinction — and it would have inflated the coverage matrix with a
detection nobody had. A coverage report is only worth reading if the claims in
it are checked.

### SA-3 — WG-BM-050 overclaimed `choose_by_information_gain`

**Found:** by the same test, during the v0.1 stochastic extension.

**Cause:** WG-BM-050 (K7) has a single observation. Ranking observations by
information and by value selects the same one when there is only one, so the
mutation changed nothing.

**Resolution:** *different from SA-2.* The benchmark's subject — an observation
with positive information and zero decision value — is exactly what the mutation
gets wrong, so instead of dropping the claim the solver was changed to answer
the question the benchmark is actually about. It now reports
`observations_worth_acquiring`, an observation qualifying when its **operational
EVSI** is positive rather than its mutual information. The clean solver says
"acquire nothing"; the mutated one says "acquire". Recorded as WG-D-016.

**Why it matters:** the two overclaims had opposite right answers. SA-2's
benchmark genuinely could not detect the bug and the claim had to go; SA-3's
could, once the solver reported the right quantity. Distinguishing the two
required looking at each case rather than applying a rule.

---

## C. Defects in the machinery, caught by the suite's own tests

These are engineering bugs rather than scientific ones. They are listed because
each one would have silently corrupted results.

### SA-4 — YAML round-trip: numeric-looking mapping keys

**Found:** by WG-BM-023 (F2), whose results are keyed by pickup duration.

**Cause:** the dumper wrote `2: 8.0`, which the loader read back as the integer
`2`, while the solver produced the string `"2"`. The comparison reported every
key missing.

**Resolution:** mapping keys that would round-trip as a non-string are quoted.
Covered by `tests/test_yamlio.py`.

### SA-5 — YAML round-trip: nested block sequences

**Found:** by `tests/test_yamlio.py::test_fallback_parser_matches_pyyaml_on_every_repository_document`,
which compares the dependency-free fallback parser against PyYAML on every
document in the repository.

**Cause:** a list of lists (`feasible_intervals: [[0, 4], [20, 34]]`) was emitted
in nested block form, which the fallback parser read as the string `"- 0.0"`.
PyYAML and the fallback disagreed, so the suite would have behaved differently
depending on whether an optional dependency happened to be installed.

**Resolution:** scalar-only sub-lists are emitted inline, and the fallback parser
learned nested block sequences anyway.

### SA-6 — Invariant expressions could not see their own variable

**Found:** immediately, by WG-BM-002 through WG-BM-004.

**Cause:** invariants are evaluated with `eval`, and a comprehension inside the
expression creates its own scope that cannot see `eval`'s *locals*. Every
invariant containing a comprehension raised `NameError`.

**Resolution:** the result document is bound in globals. Had this failed
silently rather than raising, every comprehension invariant would have been
vacuous.

### SA-7 — Tie-breaking separated analytically simultaneous events

**Found:** by WG-BM-010 (C2), which has three probe points that arrive at
exactly 10 minutes by construction.

**Cause:** the three arrival times came out of different algebraic routes and
differed in the last bit, so the ordering tie-break by identifier never
triggered.

**Resolution:** arrival orderings round to `1e-9` minutes before comparing, and
the convention is documented in `docs/ASSUMPTIONS.md`.

### SA-8 — Log-likelihood ratio of a perfectly discriminating sensor

**Found:** by WG-BM-053 (K10), whose "perfect, late" observation has a zero
likelihood leg.

**Cause:** `log2(0)` — a domain error rather than a wrong answer, so the
benchmark reported ERROR rather than FAIL.

**Resolution:** the ratio is reported only when both legs are positive; an
infinite ratio is absent rather than fabricated.

### SA-9 — Schema label pattern did not cover the new families

**Found:** by `tools/validators/validate_benchmarks.py` when the M family was
added.

**Cause:** the `label` pattern was `^[A-J][0-9]+$`.

**Resolution:** widened to `^[A-M][0-9]+$`. Minor, and included because the
structural validator earning its keep is worth recording.

---

## What the pattern says

Nine corrections. Three of them (SA-1, SA-2, SA-3) concern what the suite
*claims*, and all three were found by the two mechanisms built specifically to
find them: authoring expected values independently of the solver, and checking
detection claims in both directions. Neither mechanism is free, and both paid
for themselves inside one build.

The remaining six are ordinary software defects, and every one was found by a
test rather than by review. The two that would have been most damaging — SA-5
and SA-6 — were both *silent*: one made behaviour depend on an optional
dependency, the other made a class of assertions vacuous.

**Standing conclusion:** the benchmarks are not more trustworthy than the code
that runs them, and the only reason to believe either is that they disagree with
each other when one is wrong.
