# What "expected behavior" means here

## Two places, one answer

Every benchmark states its answer twice, deliberately:

* `benchmark.yaml` -> `expected_behavior` — a handful of **headline values**, so
  that a reader skimming the descriptor sees the point of the case;
* `expected/expected.yaml` -> `results` — the **machine-checked answer**, plus
  the `derivation` that justifies it and any relational `invariants`.

The two must agree. `wg-benchmarks validate` compares every headline key against
the machine-checked block and fails if they have drifted, so the readable
summary cannot rot.

## What is compared, and how

The runner compares the `results` mapping against the solver's output with these
rules:

* **Types are strict.** `true` is not `1`; `null` is not `0.0`; `"9"` is not `9`.
* **Numbers use the declared tolerance.** Default `1e-9` absolute and `0`
  relative. Per-field overrides live in the benchmark's `tolerance` block, keyed
  by leaf name or dotted path.
* **Only the pinned keys are checked.** A solver may report as much extra detail
  as it likes; a missing pinned key is a failure.
* **Lists compare in order and by length**, unless the key ends in
  `_unordered`, in which case they compare as multisets.
* **Invariants are Python expressions** over the result document, evaluated in a
  restricted namespace with the result bound as `r`. They express relations —
  "the shortest route is not among the feasible ones", "the two comparisons have
  opposite signs" — that a pinned number cannot.

Invariants matter for a specific reason: a pinned number can be satisfied by an
implementation that happens to produce it for the wrong reason, whereas
`r['shortest_route'] not in r['feasible_routes']` is the claim itself.

## Exactness classes

Every benchmark declares how much its expected answer is worth:

| Class | Meaning | Tolerance |
|---|---|---|
| `exact_analytic` | closed form derived by hand in the README | `1e-9` or tighter |
| `exact_enumeration` | finite exhaustive enumeration; no approximation | `1e-9`, or the declared grid resolution |
| `seeded_stochastic` | deterministic given the seed, checked within a stated Monte Carlo band | declared per field, with justification |
| `qualitative` | an ordering, a sign or a flag rather than a number | exact on the flag |

Current distribution is in `reports/BENCHMARK_CATALOG.md`. Everything in the
suite is currently `exact_analytic` or `exact_enumeration` except WG-BM-037,
which is `seeded_stochastic` and pins its analytic counterparts exactly
alongside the bootstrap ones.

## What a passing benchmark does and does not establish

**Does establish:** on this input, under these declared conventions, the
implementation produces the derived answer, and it does so for reasons
consistent with the stated invariants.

**Does not establish:** that the implementation is correct on any other input;
that its conventions match the user's; that its model is physically realistic;
that it is numerically stable at scale; that it is fast enough to be useful.

`docs/VALIDATION_STANDARD.md` is the statement of what a *set* of passing
benchmarks is worth.

## Adding an expected answer

1. Derive it from the scenario. Write the derivation down first, in prose and
   arithmetic, in the benchmark README.
2. Put the number in the authoring script as the closed form where one exists
   (`math.degrees(math.atan(...))`), not as a rounded literal.
3. Run the solver. If it disagrees, **do not adjust the expected value until you
   know which side is wrong.**
4. Add at least one invariant that states the point of the benchmark as a
   relation.
5. Add the third derivation to `tests/test_analytic_identities.py`, written
   independently of the authoring script.
