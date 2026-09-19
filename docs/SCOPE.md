# Scope

## In scope

| Area | What the suite covers |
|---|---|
| Terrain preprocessing | slope and aspect conventions, ridge artefacts, no-data propagation |
| Road graphs | egress redundancy, articulation points, reachability, one-way semantics |
| Fire / hazard fields | analytic arrival times, wind anisotropy, fuel boundaries, spotting |
| Observation | latency, staleness, outage, informative missingness, false negatives |
| Routing | time-dependent feasibility, mid-edge hazard, waiting, non-FIFO travel |
| Assisted dispatch | latest feasible dispatch, service time, base and destination choice, non-monotone feasibility |
| Traffic interaction | ingress competing with egress on a shared corridor |
| Forecast value | skill versus decision value, timeliness, strong baselines, forecast harm |
| Scenario uncertainty | correlation, mutually exclusive scenarios, ensemble-size effects |
| Statistics | pseudoreplication, tail risk, practical equivalence, selection bias |
| Protectability | robust action existence, value of information, information that arrives too late |

## Explicitly out of scope

These are not oversights. Each is excluded for a reason, and the reasons are
worth keeping.

**Realistic fire behaviour models.** Rothermel, FARSITE, level-set and
cellular-automaton spread are all out of scope. Their outputs cannot be checked
by hand, which is the property the suite is built on. The fire models here are
closed forms whose only job is to be right.

**Calibration and parameter estimation.** No benchmark asks whether a spread
rate is realistic. Every rate is a stipulated input.

**Numerical accuracy at scale.** Grid convergence, solver conditioning and
floating-point accumulation over long integrations are real concerns and not
ones a 7x7 raster can address.

**Performance.** Every reference solver here is deliberately the slowest
obviously-correct implementation. Nothing in this repository should be taken as
guidance about how to compute anything efficiently.

**Traffic microsimulation.** WG-BM-027 models a capacity conflict with two
stipulated travel times. Queue formation, shockwaves and signal control are out
of scope, because a benchmark requiring a queueing model to state its expected
answer is no longer hand-checkable.

**Human behaviour.** Compliance rates, notification response, shadow evacuation
and household preparation time do not appear. They are decisive in practice and
there is no scenario small enough to make their correct answer knowable.

**Integration with production WildfireGuardian repositories.** Out of scope for
now by explicit instruction; `benchmarks/integration_future/` records what the
integration benchmarks should eventually be.

**Full intervention optimisation.** The J family contains mathematical examples
of protectability, not an optimiser over interventions.

## Boundary cases

Some things sit on the edge and have been decided one way:

* **Probabilistic forecasts** are in scope conceptually but currently
  unrepresented: every information source in the G and J families emits a
  deterministic signal. Calibration benchmarks are a recorded gap.
* **Directed-graph connectivity theory** is partially in scope: WG-BM-008 checks
  directed reachability, but articulation points and cuts are computed on the
  undirected support only. Recorded as a gap.
* **Multi-resident, multi-vehicle dispatch** is out of scope for now. Every F
  benchmark has one resident and one vehicle, because the combinatorics of more
  would defeat hand-checking. A small two-resident case is on the roadmap.
