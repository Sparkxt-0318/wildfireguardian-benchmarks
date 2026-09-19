# Known gaps

What this suite does **not** cover. Maintained by hand; an entry is removed only
when a benchmark closes it.

Gaps are ordered by how much damage the uncovered failure mode could do if it
reached an operational decision.

---

## Severe — a wrong answer here would not be caught

### G-1. Probabilistic forecast calibration

Every information source in the G and J families emits a **deterministic**
signal. WG-BM-029 shows a 20 m deterministic error costing 92, and notes in
passing that a forecast reporting "1010 m, sigma 300 m" would have supported the
right action. Nothing tests that.

Missing: a benchmark where a *worse-scoring but well-calibrated* probabilistic
forecast beats a better-scoring deterministic one because it reports its own
uncertainty near a decision boundary; and a benchmark that catches an
overconfident forecast whose point estimates are excellent.

**Consequence if uncovered:** a system can be built that is better by every
deterministic metric and worse at every boundary decision, and this suite would
pass it.

### G-2. Multi-resident sequencing

Every F benchmark has one resident and one vehicle. The first genuinely
operational question — *which resident do we collect first?* — is untested, and
it is the question where the loss function's shape (mean versus tail, and whose
tail) does the most work.

**Consequence if uncovered:** a dispatcher that is correct on every single-
resident case can still be systematically wrong about triage.

### G-3. General correction for informative missingness

WG-BM-016's dropout-aware estimator recovers the truth **exactly**, and only
because the scenario stipulates that hazard arrival is the sole cause of
dropout. A real network also loses nodes to battery, comms and vandalism. The
benchmark says so in its README, but nothing tests a correction under a mixed
mechanism — where the naive correction is itself biased, in the opposite
direction.

**Consequence if uncovered:** an implementation could adopt the substitution
used here as a general rule and over-report hazard wherever sensors fail for
ordinary reasons.

---

## Moderate — partially covered, or covered only qualitatively

### G-4. Directed-graph connectivity theory

WG-BM-008 checks directed **reachability**. Articulation points, bridges and
minimum cuts are computed on the **undirected support** of the graph and are
therefore not asserted for directed networks. Strong articulation points and
directed cuts are the right notions for a contraflow network and are not
implemented.

### G-5. Alternative traversal conventions

WG-BM-019 enumerates four defensible conventions for mid-edge closure and pins
one (interval safety). The other three — entry-time-only, partial traversal with
a stranded-vehicle model, and reversible with a detection model — have no
benchmarks. An implementation that chose one of them has nothing to conform to
beyond "you must declare it".

### G-6. Responder-on-responder interaction

WG-BM-027 has one responder against an evacuation flow. Two responders competing
for the same corridor, or a responder delayed by another responder's mission, is
untested.

### G-7. Terrain across a resolution change

A-family benchmarks use one cell size. The interesting terrain failure —
a ridge that exists at 10 m and vanishes at 90 m, taking its aspect
discontinuity with it — needs a multi-resolution benchmark and does not have one.

### G-8. Observation and statistics have only one solver

`tests/test_cross_check.py` cross-checks graphs, dispatch, decisions and CVaR
against independent brute-force implementations. The observation (D) and
statistics (I) solvers are checked against authored expectations and against the
third derivations in `tests/test_analytic_identities.py`, but not against a
second implementation. A shared conceptual error in those two families would not
be caught by cross-checking.

### G-9. Ensemble provenance

WG-BM-036 quantifies how sup-regret moves with ensemble size. Nothing checks
that an implementation *reports* the ensemble size and provenance alongside a
worst-case number, which is the actual requirement the benchmark implies.

---

## Out of scope by decision, recorded for completeness

These are not going to be closed here. They are listed so that nobody mistakes
a green suite for coverage of them. See `docs/SCOPE.md`.

* **Realistic fire behaviour.** No Rothermel, no FARSITE, no level sets. The
  fire models here are closed forms chosen so the answer is checkable.
* **Calibration.** No benchmark asks whether a spread rate is plausible.
* **Numerical accuracy at scale.** Grid convergence, conditioning and
  floating-point accumulation over long integrations.
* **Performance.** Every reference solver here is deliberately the slowest
  obviously-correct implementation.
* **Traffic microsimulation.** WG-BM-027 stipulates two congested travel times.
* **Human behaviour.** Compliance, notification response, shadow evacuation,
  household preparation time. Decisive in practice; no scenario small enough to
  make the answer knowable.
* **Full intervention optimisation.** The J family is mathematical examples of
  protectability, not an optimiser.
* **Integration with production repositories.** Deferred by instruction;
  specified in `benchmarks/integration_future/README.md`.

---

## Gaps in the machinery rather than the science

* **Interval endpoints depend on a declared grid.** Dispatch feasible intervals
  are found by grid sampling plus bisection, with every edge-window endpoint
  forced into the sample. A feasible window narrower than the grid step *and*
  not bounded by a window endpoint would be missed. No current benchmark has
  one, and nothing detects it if one is added.
* **No property-based fuzzing.** The two solver implementations are compared on
  the 43 fixed inputs, not on randomly generated tiny networks.
* **Difficulty labels are asserted, not measured.** A benchmark is labelled
  `adversarial` by its author. Nothing confirms that a plausible naive
  implementation actually fails it, beyond the mutations we chose to write.
