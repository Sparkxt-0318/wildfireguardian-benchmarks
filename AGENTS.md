# AGENTS.md — how work is done in this repository

This file is the working agreement for anyone — human or agent — adding to the
suite. It exists because the value of a benchmark collapses the moment its
expected answer is derived from the thing it is supposed to test.

## The one rule

> **Expected values are authored from the scenario. They are never copied out of
> a solver run — least of all a production implementation's.**

Everything below is machinery for keeping that rule true under pressure.

---

## The three roles

Work on a benchmark family passes through three roles. They may be three people,
three agents, or one person on three days, but the **order matters** and the
separation is the point.

### Agent A — Benchmark Designer

Constructs the scenario and derives the expected behaviour mathematically.

* Writes the scenario, the README derivation and the authored expected values,
  in `tools/authoring/author_<family>.py`.
* **Does not look at any production implementation's output first.** A benchmark
  designed after seeing what an implementation produces will be designed around
  its bugs — the expected answer drifts towards the observed one, and the
  benchmark records behaviour instead of testing it.
* Writes the expected value as a closed form where one exists
  (`math.degrees(math.atan(...))`), not as a rounded literal, so the derivation
  stays visible in the source.
* Declares every convention the answer depends on in the `assumptions` block,
  and adds it to `docs/ASSUMPTIONS.md` if it is new.

### Agent B — Independent Analytic Solver

Implements a second, tiny reference solver, favouring brute force and clarity
over speed.

* Lives in `tools/analytic_solvers/`, imports nothing from
  `wg_benchmarks.solvers`, and uses different internal representations on
  purpose.
* Enumerates: all routes, all dispatch times on a grid, all decision rules, all
  equal-probability atoms. If there is a clever way and a stupid way, take the
  stupid way.
* Cross-checks run in `tests/test_cross_check.py`. When the two solvers
  disagree, the suite cannot say which is right — a human has to look, and that
  is the correct outcome.

### Agent C — Adversarial Tester

Tries to build cases where a naive implementation fails, and tries to break the
benchmarks themselves.

* Adds a mutation to `wg_benchmarks/mutations.py` for every plausible bug, with
  a `# MUTATION HOOK` comment at each injection site so the injected branches
  stay auditable and deletable.
* Confirms the mutation is caught: `python -m wg_benchmarks mutate -m <id>`.
* **Confirms that a benchmark does not overclaim.** If a benchmark's declared
  answer does not change under a bug, it does not detect that bug and must not
  say it does. WG-BM-028 is the worked example: it documents the skill/value
  conflation and explicitly declines to claim detection.

---

## Adding a benchmark: the checklist

1. **Pick the failure mode first.** It should be in `docs/FAILURE_MODES.md`; if
   it is not, add it there and explain why it is consequential.
2. **Make it as small as it can be.** Five nodes, not fifty. If the derivation
   does not fit in a README section, the scenario is too big.
3. **Write the derivation before the code.** Prose and arithmetic, in the
   benchmark README, reproducible by a reader who runs nothing.
4. **Author it** in `tools/authoring/author_<family>.py`, taking the next free
   `WG-BM-0NN`. Ids are permanent and never reused.
5. **Add at least one invariant** stating the *point* of the benchmark as a
   relation over the result document. A pinned number can be satisfied for the
   wrong reason; `r['shortest_route'] not in r['feasible_routes']` cannot.
6. **Add a third derivation** to `tests/test_analytic_identities.py`, written
   from the README rather than copied from the authoring script.
7. **Run it.** If the solver disagrees, *stop*. Find out which side is wrong
   before touching either. Record the outcome in `docs/DECISIONS.md` if it was
   interesting.
8. **Declare the mutations it detects** and verify both directions:
   `python -m wg_benchmarks mutate --strict` and `pytest tests/test_mutations.py`.
9. **Regenerate** reports and figures: `python -m wg_benchmarks report && python -m wg_benchmarks figures`.
10. **Update** `reports/KNOWN_GAPS.md` if the new benchmark closes a gap, and
    `tasks/COMPLETED.md`.

## Things that are not allowed

* Adjusting an expected value to make a solver pass.
* Loosening a tolerance without a stated reason in the benchmark's `notes`.
* A benchmark whose answer depends on an undeclared convention.
* A benchmark that claims to detect a mutation it does not detect.
* Recording a previous run's output as truth. Regression tests of that kind are
  legitimate and belong in the implementation's own repository, not here.
* Importing a production WildfireGuardian package anywhere in this repository.
* Adding a required third-party runtime dependency (see `docs/DECISIONS.md`,
  WG-D-007).

## Conventions for the code

* Reference solvers favour clarity over speed, everywhere, without exception.
* Mutation injection sites carry a `# MUTATION HOOK` comment.
* Counterfactual conventions are *reported*, never silently chosen: see
  `feasible_under_entry_time_semantics` in the routing solver and
  `free_flow_counterfactual` in the dispatch solver.
* New solvers register in `wg_benchmarks/registry.py` under a
  `family.method` identifier.

## Definition of done for a work item

A change is done when all of these are true:

```bash
python tools/validators/validate_benchmarks.py   # 43/43, 0 repository problems
python -m wg_benchmarks run                      # all pass
python -m wg_benchmarks mutate --strict          # every mutation detected
python -m pytest tests -q                        # green
git diff --exit-code reports/ benchmarks/        # after regenerating reports and figures
```

and `reports/BENCHMARK_READINESS.md` still says something true.
