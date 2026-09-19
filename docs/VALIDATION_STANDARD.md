# Validation standard

## The claim a passing suite supports

> On a set of scenarios whose correct answers are known by derivation, this
> implementation reproduces them under the declared conventions, and the
> deliberate bugs catalogued in `reports/MUTATION_MATRIX.md` would have been
> caught.

That is a real claim and a narrow one. It is a statement about **semantics**:
the implementation means by "feasible route", "latest dispatch", "available
observation" and "value of a forecast" what this programme means by them.

## The claim it does not support

A passing suite says nothing about:

* accuracy on a real landscape;
* calibration of any parameter;
* numerical behaviour at realistic scale;
* performance;
* human factors, compliance, or anything downstream of the model.

Anyone writing "validated against the WildfireGuardian benchmark suite" should
write the narrow claim, not the broad one.

## Levels

The suite defines three levels of conformance. A repository states which it
claims and the claim is checkable.

### Level 1 — Semantics

Passes every `basic` and `intermediate` benchmark in the categories the
component touches.

This is the minimum before a component's output on a realistic problem is worth
looking at. It establishes that units, conventions and definitions are right.

### Level 2 — Adversarial

Additionally passes every `adversarial` benchmark in those categories, and the
mutation matrix shows the component's own test suite catching the corresponding
bugs.

This is the level at which a component may be used to produce numbers that
inform a decision in research.

### Level 3 — Cross-checked

Additionally, the component's results are produced by a pipeline that is
independent of this repository (via `wg-benchmarks validate-results`), and any
component-specific benchmarks it adds are accompanied by a second, independent
solver as in `tools/analytic_solvers/`.

This is the level at which a component's claims should be published.

## The procedure

```bash
# 1. the component writes one result document per benchmark
#    results/WG-BM-018.yaml, results/WG-BM-022.yaml, ...

# 2. the suite checks them without importing anything from the component
wg-benchmarks validate-results results/
```

A result document is either the result mapping itself or a mapping with a
`results` key holding it. Only the pinned keys are compared, so a component may
report whatever additional detail it likes.

## Rules for the suite itself

1. **An expected value is never changed to make a solver pass.** If they
   disagree, the disagreement is investigated and the outcome recorded in
   `docs/DECISIONS.md`.
2. **A benchmark may not claim a detection it does not achieve.** Enforced by
   `tests/test_mutations.py`.
3. **Every mutation must be detected by at least one benchmark.** Enforced by
   `tools/validators/validate_benchmarks.py`; an undetected mutation is a
   coverage hole and is reported in `reports/KNOWN_GAPS.md`.
4. **A benchmark whose answer depends on a convention must declare it** in its
   `assumptions` block, and the convention must appear in `docs/ASSUMPTIONS.md`.
5. **Green is not evidence of coverage.** The suite reports both what it can
   detect and what it cannot; `reports/BENCHMARK_READINESS.md` is the honest
   summary and should be read before the pass count.

## What to do when a benchmark and an implementation disagree

In order:

1. Re-read the benchmark's `assumptions`. A large fraction of disagreements are
   convention mismatches, and the convention may well be the implementation's
   to choose — in which case the right outcome is a *new* benchmark stating the
   other convention, not a weakened existing one.
2. Check the derivation in the README by hand. It is short on purpose.
3. Run `tests/test_cross_check.py`: if the two independent solvers here disagree
   with each other, the fault is in this repository.
4. Only then look for the bug in the implementation.
