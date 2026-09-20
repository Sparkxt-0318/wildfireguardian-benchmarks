# Known gaps

What this suite does **not** cover. Maintained by hand; an entry is removed only
when a benchmark closes it.

Gaps are ordered by how much damage the uncovered failure mode could do if it
reached an operational decision.

**Closed since v0.0:** probabilistic forecast calibration (now the K1, K2 and M
families), and the absence of any posterior/decision chain (now K6-K15).

---

## Severe — a wrong answer here would not be caught

### G-1. Continuous and sequential inference

Every Bayesian benchmark in the K family has **two hypotheses and at most four
outcomes**, and every update is a single step. Untested:

* a continuous state (front position, spread rate) rather than a binary
  hypothesis;
* **sequential** updating over a stream of observations, which is where
  correlation errors compound rather than merely occur once — WG-BM-054's
  −2-bit error applied ten times running is an 18-bit error;
* the interaction between a filter's process model and the observation
  likelihood.

**Consequence if uncovered:** a filter can be exactly right on every single-step
case here and drift into certainty over a sequence, which is the normal way
operational filters fail.

### G-2. Multi-resident dispatch sequencing

Every F benchmark has one resident and one vehicle. Triage — **which resident is
collected first** — is the first genuinely operational question, and it is the
one where the loss function's shape, and whose tail it measures, does the most
work.

**Consequence if uncovered:** a dispatcher correct on every single-resident case
can still be systematically wrong about who is reached.

### G-3. Estimating the likelihoods, rather than being given them

`WG-BM-056`'s missingness likelihood, `WG-BM-054`'s joint and `WG-BM-057`'s
false-negative rate are all **stipulated inputs**. Nothing tests a system that
must estimate them from data, and that is precisely the case where:

* an MNAR correction can be biased in the *opposite* direction, because ordinary
  outages are attributed to the hazard;
* a joint likelihood estimated from a short record understates the correlation;
* a false-negative rate estimated on clear-air cases does not transfer to smoke.

**Consequence if uncovered:** an implementation could adopt WG-BM-056's exact
correction as a general rule and over-report hazard wherever sensors fail for
ordinary reasons.

### G-4. Alert fatigue and dynamic credibility

`WG-BM-058` shows one over-escalation costing 31 against 11. The cost of the
**next** warning being believed less is real, dynamic, and absent from every loss
matrix in the suite, because a static loss matrix cannot express it.

**Consequence if uncovered:** a threshold tuned benchmark-by-benchmark will be
too conservative in aggregate, and the system's own history of false alarms will
not appear anywhere in its recommendations.

---

## Moderate — partially covered, or covered only in one direction

### G-5. Proper scoring rules beyond Brier

The M family uses the Brier score and its Murphy decomposition. The logarithmic
score, CRPS for continuous forecasts, and the general notion of propriety are
absent — so nothing catches a system that optimises an improper score.

### G-6. Where the loss matrix comes from

Half the K and L results turn on a threshold derived from losses that were
invented for the benchmark. `WG-BM-062` shows a recommendation turning on 0.21
of expected loss, and states that re-elicitation rather than observation is the
productive response — but there is no benchmark for **elicitation quality**, and
no treatment of a loss matrix given as a range rather than a number.

### G-7. Directed-graph connectivity theory

`WG-BM-008` checks directed reachability. Articulation points, bridges and
minimum cuts are computed on the **undirected support** and are therefore not
asserted for directed networks. Strong articulation points and directed cuts are
the right notions for a contraflow network and are not implemented.

### G-8. Alternative traversal conventions

`WG-BM-019` enumerates four defensible conventions for mid-edge closure and pins
one. The other three — entry-time-only, partial traversal with a
stranded-vehicle model, and reversible with a detection model — have no
benchmarks, so an implementation that chose one of them has nothing to conform
to beyond "you must declare it".

### G-9. Responder-on-responder interaction

`WG-BM-027` has one responder against an evacuation flow. Two responders
competing for the same corridor, or one delayed by another's mission, is
untested.

### G-10. Terrain across a resolution change

A-family benchmarks use one cell size. The interesting terrain failure — a ridge
that exists at 10 m and vanishes at 90 m, taking its aspect discontinuity with
it — needs a multi-resolution benchmark and does not have one.

### G-11. Cross-checking coverage is uneven

`tests/test_cross_check.py` checks graphs, dispatch, decisions, CVaR, Bayesian
posteriors, EVSI, normal tails and Brier scores against independent
implementations. The **observation (D)** and **statistics (I)** solvers are
checked against authored expectations and the third derivations in
`tests/test_analytic_identities.py`, but not against a second implementation. A
shared conceptual error in those two families would not be caught by
cross-checking.

### G-12. Ensemble provenance

`WG-BM-036` quantifies how sup-regret moves with ensemble size, and `WG-BM-048`
requires excluded scenarios to be reported. Nothing checks that an
implementation reports the ensemble's **size and provenance** alongside a
worst-case number, which is the requirement those two benchmarks jointly imply.

---

## Out of scope by decision, recorded for completeness

These are not going to be closed here. They are listed so that nobody mistakes a
green suite for coverage of them. See `docs/SCOPE.md`.

* **Realistic fire behaviour.** No Rothermel, no FARSITE, no level sets.
* **Production probabilistic machinery.** No Bayesian filters, ensemble
  forecasting systems, calibration models, particle filters or neural
  uncertainty estimators. Only the tiny exact mathematics needed to test one.
* **Calibration of physical parameters.** No benchmark asks whether a spread
  rate is plausible.
* **Numerical accuracy at scale.** Grid convergence, conditioning, accumulation.
* **Performance.** Every reference solver is deliberately the slowest
  obviously-correct implementation.
* **Traffic microsimulation.** `WG-BM-027` stipulates two congested travel times.
* **Human behaviour.** Compliance, notification response, shadow evacuation,
  household preparation time.
* **Full intervention optimisation.** The J family is mathematical examples of
  protectability, not an optimiser.
* **Integration with production repositories.** Deferred by instruction;
  requirements specified in `reports/INTEGRATION_COVERAGE.md` and mechanics in
  `benchmarks/integration_future/README.md`.

---

## Gaps in the machinery rather than the science

* **Interval endpoints depend on a declared grid.** Dispatch feasible intervals
  are found by grid sampling plus bisection, with every edge-window endpoint
  forced into the sample. A feasible window narrower than the grid step *and*
  not bounded by a window endpoint would be missed. No current benchmark has
  one, and nothing detects it if one is added.
* **No property-based fuzzing.** The two solver implementations are compared on
  the 66 fixed inputs, not on randomly generated tiny problems.
* **Difficulty labels are asserted, not measured.** A benchmark is labelled
  `adversarial` by its author. Nothing confirms that a plausible naive
  implementation actually fails it, beyond the mutations we chose to write.
* **`NUMERIC_REFERENCE` is defined and unused.** No benchmark currently needs a
  numerical procedure for its expected value; the class exists so that if one
  ever does, it cannot be labelled exact. The Simpson quadrature in
  `tools/analytic_solvers` is a cross-check, not an expected value.
