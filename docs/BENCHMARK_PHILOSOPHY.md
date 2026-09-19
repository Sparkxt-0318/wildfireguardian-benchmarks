# Benchmark philosophy

## The fundamental rule

> A complicated simulation producing plausible-looking maps is not validation.

A 50,000-node realistic evacuation network produces an answer nobody can check.
When it is wrong, it is wrong plausibly: the map still looks like a map, the
routes still look like routes, and the error is discovered — if at all — by an
incident commander. A five-node graph produces an answer that a competent
reviewer can verify on paper in two minutes, and when it is wrong, it is
obviously wrong.

**Prefer a 5-node graph with a known answer to a 50,000-node graph with an
unknowable one.**

## The five properties

Every benchmark in this repository aims at all five.

### Small

Small enough that the whole scenario fits on one screen and the whole derivation
fits in one README section. The largest road network in the suite has five
nodes; the largest raster is 7x7; the largest scenario set has seven members.

Smallness is not a limitation being tolerated. It is the property that makes
the answer knowable.

### Transparent

Every input is visible and every assumption is declared. There are no
calibrated coefficients, no fitted parameters, no "typical values for this fuel
type". Where a benchmark needs a number — a spread rate, a pickup duration, a
congested travel time — that number is a stipulated input, not the output of a
model the reader would also have to check.

### Hand-checkable

The expected answer is reproducible with pen and paper. This is asserted per
benchmark via the `hand_checkable` flag and enforced socially by requiring the
derivation in the README to be complete: a reader must be able to get the
number without running anything.

Where a quantity is not hand-computable — a bootstrap confidence interval, an
exhaustive interval refinement — the benchmark says so through its `exactness`
field, and an exactly computable companion quantity is pinned alongside it.

### Adversarial

A benchmark that every reasonable implementation passes teaches nothing. The
suite is built around cases where the *natural* implementation is wrong:

* the shortest route is the infeasible one;
* the nearest destination is unreachable;
* the nearest base gives the least time;
* the more accurate forecast is the harmful one;
* the better average has the worse tail;
* leaving later arrives earlier;
* feasibility is not monotone in the dispatch time.

Mutation testing makes this concrete: `reports/MUTATION_MATRIX.md` records, for
each plausible bug, which benchmarks catch it. A mutation nothing catches is a
coverage hole.

### Reproducible

No network access, no third-party dependencies at runtime, no wall-clock
dependence, no unseeded randomness. The single stochastic benchmark
(WG-BM-037) uses `random.Random` with a fixed seed and pins its analytic
counterparts exactly.

## What follows from the rule

**Expected answers are authored, never harvested.** The values in
`expected/expected.yaml` are written by hand in `tools/authoring/*.py`, derived
from the scenario. A solver that disagrees is a finding, and the finding might
be in either place. This actually happened during the construction of the suite:
WG-BM-036 failed on first run and the bug was in the reference solver, not in
the expected value.

**Every answer that depends on a convention states the convention.** WG-BM-019
(mid-edge closure) has no convention-free answer. Rather than pick one quietly,
it declares interval safety as the suite's convention *and* reports what the
alternative convention would conclude, so a reader can see which rule produced
which number.

**Zero is a legitimate expected answer.** WG-BM-032 expects a forecast to add
exactly nothing, and WG-BM-041 expects perfect information to be worth exactly
nothing. Without such cases a suite silently rewards complexity: any system
whose sophisticated component reports a positive value passes everything.

**A benchmark does not claim to detect what it cannot.** WG-BM-028 documents the
skill/value conflation and explicitly does not claim to catch it, because under
that bug its declared answer does not change.

## What this philosophy costs

Realism. Nothing in this suite resembles an actual fire. A system that passes
every benchmark here has demonstrated that its semantics are right on cases
where the answer is known; it has demonstrated nothing about its behaviour on a
real landscape, its calibration, or its numerical accuracy at scale.

That trade is deliberate. Semantic correctness is a precondition for the
realistic work being meaningful, and it is the part that can be established
with certainty.
