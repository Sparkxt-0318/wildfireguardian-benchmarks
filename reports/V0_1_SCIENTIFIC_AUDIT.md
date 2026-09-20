# v0.1.0 scientific audit

The state of the suite at the point it is frozen.

> **Passing all benchmarks establishes semantic consistency with these reference
> cases. It does not establish real-world model validity.**

That sentence is the conclusion of this document and is stated first so that it
cannot be lost behind the numbers.

---

## Headline

| | |
|---|---|
| benchmarks | **66** |
| hand-checkable | 66 / 66 |
| `CLOSED_FORM` | **51** |
| `FINITE_ENUMERATION` | **14** |
| `NUMERIC_REFERENCE` | 0 |
| `SEEDED_STOCHASTIC_VALIDATION` | **1** |
| difficulty: basic / intermediate / adversarial | 16 / 16 / 34 |
| distinct failure-mode identifiers | 115 |
| injected mutations / detected | **39 / 39** |
| tests | 183 |
| required third-party runtime dependencies | 0 |

---

## 1. How many benchmarks exist?

**66**, in thirteen families across fourteen categories.

| Family | Ids | Count | Subject |
|---|---|---|---|
| A | 001-004 | 4 | terrain preprocessing |
| B | 005-008 | 4 | road graphs |
| C | 009-012 | 4 | analytic fire fields |
| D | 013-017 | 5 | observation availability and missingness |
| E | 018-021 | 4 | time-dependent routing |
| F | 022-027 | 6 | assisted dispatch and the traffic conflict |
| G | 028-033 | 6 | forecast skill versus decision value |
| H | 034-036 | 3 | scenario uncertainty |
| I | 037-040 | 4 | statistics of policy comparison |
| J | 041-043 | 3 | robust protectability |
| K | 044-058 | 15 | probabilistic forecasts and Bayesian belief |
| L | 059-063 | 5 | decision risk and robustness |
| M | 064-066 | 3 | forecast calibration |

23 of the 66 carry an `information_structure` block declaring which of point
prediction, predictive distribution, scenario ensemble, posterior belief and
decision they are about.

## 2. How many are closed-form?

**51.** An analytic expression derived by hand and written out in the benchmark
README — elementary arithmetic, `atan`, `erf`, `log2` — exact to machine
precision and checked at `1e-9` or, for the probabilistic families, `1e-12`.

Examples: `atan(sqrt(0.02))` for the slope of a plane; `200/20` for the head
arrival of a wind-driven front; `Phi((800-1000)/300)` for a tail probability;
`0.09/0.27` for a posterior; `5/(5+495)` for a decision threshold;
`reliability - resolution + uncertainty` for a Brier score.

## 3. How many are exhaustive finite enumeration?

**14.** A finite set enumerated completely, with no approximation: all simple
paths (`WG-BM-005`-`008`), all departure times on a declared grid
(`WG-BM-021`), all dispatch times with bisection-refined interval endpoints
(`WG-BM-026`), all burned cells on a declared grid (`WG-BM-012`), all decision
rules (`WG-BM-017`), all ensemble members and actions (`WG-BM-048`,
`WG-BM-059`-`063`).

One caveat, stated in the benchmark itself: WG-BM-026's
`infeasible_dispatch_below_latest_min` is the first *sampled* failing dispatch
time and depends on the declared one-minute grid. The *existence* of such a time
is exact and is asserted separately as an invariant.

## 4. How many are stochastic validation only?

**One: WG-BM-037.** Its bootstrap confidence intervals are Monte Carlo estimates
from 200 resamples of 10 worlds, reproducible given the seed and checked against
the analytic standard errors within a declared band. Its analytic quantities —
`analytic_world_se`, `analytic_resident_se`, their ratio — are exact and checked
at `1e-9`.

**No benchmark uses Monte Carlo as truth.** Where a closed form exists it is the
expected value; where an enumeration exists it is the cross-check. The one
numerical procedure in the repository, Simpson quadrature of the normal density
in `tools/analytic_solvers`, is used only to cross-check the `erf` closed form
and carries an error bound far below the comparison tolerance.

## 5. Which failure modes are covered?

115 distinct failure-mode identifiers; the generated mapping is
`reports/COVERAGE.md` and the prose catalogue is `docs/FAILURE_MODES.md`. The
deterministic groups, unchanged from v0.0:

* **time and information** — future leakage, stale-as-current;
* **hazard representation** — mid-edge hazard, arrival time collapsed to a final
  perimeter, anisotropy dropped, fuel averaged, spotting ignored;
* **data quality** — missing imputed as zero, MNAR dropout, false negatives;
* **network semantics** — one-way roads reversed, unreachable destinations
  selected, non-FIFO travel, false single-egress claims;
* **decision structure** — non-monotone dispatch feasibility, service time
  ignored, greedy base selection, static destinations, capacity ignored;
* **forecasts** — skill/value conflation, error/consequence correlation, weak
  baselines;
* **uncertainty** — correlation ignored, the average-of-inputs fallacy,
  worst-case criterion instability;
* **statistics** — pseudoreplication, tail risk ignored, significance mistaken
  for importance, selection bias.

## 6. Which stochastic-information failures are now covered?

New in v0.1, and the reason for the extension:

| Failure | Benchmark | Sharpest number |
|---|---|---|
| forecast uncertainty discarded | `WG-BM-044` | same mean, opposite actions |
| deterministic skill mistaken for decision value | `WG-BM-045` | 16 m error, regret 5; 46 m error, regret 0 |
| decision threshold not derived from loss | `WG-BM-046`, `047` | `p* = 0.01`, not 0.5 |
| scenario weights normalised incorrectly | `WG-BM-048` | three answers from one file |
| posterior computed and not used | `WG-BM-049` | action stays `stay` at a posterior of 1/3 |
| likelihood discarded | `WG-BM-049` | posterior collapses to the prior |
| information gain mistaken for decision value | `WG-BM-050` | 0.0131 bits, EVSI exactly 0 |
| EVSI miscomputed | `WG-BM-051` | 22 against an EVPI of 40 |
| observation timeliness ignored | `WG-BM-052`, `053` | worth 22 statistically, 0 operationally |
| information quality and timing not evaluated jointly | `WG-BM-053` | 8x the information, 0 of the value |
| observation correlation ignored | `WG-BM-054` | 0.174 becomes 0.059; the action flips |
| duplicate evidence double counted | `WG-BM-055` | −2 bits becomes −4 bits |
| informative missingness | `WG-BM-056` | silence carries 3.58 bits |
| non-detection read as absence | `WG-BM-057` | `P(fire)` is 0.073, not 0 |
| detection read as certainty | `WG-BM-058` | `P(fire)` is 0.22, not 1 |
| base-rate neglect | `WG-BM-058` | same detector, 0.22 or 0.78 |
| undeclared risk attitude | `WG-BM-059` | no winner declared |
| declared objective ignored | `WG-BM-060` | CVaR 160 against 29 |
| uncertainty conflated with indecision | `WG-BM-061`, `063` | max weight 0.34, EVPI exactly 0 |
| state certainty mistaken for decision confidence | `WG-BM-062` | 97% resolved, margin 0.21 |
| overconfidence unmeasured | `WG-BM-065` | the whole Brier penalty is reliability |
| aggregate calibration masking regime failure | `WG-BM-066` | aggregate ECE 0, stratified 0.3 |

All 15 new mutations are detected, and no benchmark claims a detection it does
not achieve (`tests/test_mutations.py` enforces both directions).

## 7. Which important failures remain uncovered?

Fully enumerated in `reports/KNOWN_GAPS.md`. The four that would do most damage:

**Continuous-space and sequential inference.** Every Bayesian benchmark has two
hypotheses and at most four outcomes. Filtering over time, a continuous state, or
a sequence of correlated observations is untested, and sequential updating is
where correlation errors compound rather than merely occur once.

**Multi-resident dispatch sequencing.** Every F benchmark has one resident and
one vehicle. Triage — who is collected first — is the first genuinely operational
question and has no benchmark.

**Estimating the likelihoods.** WG-BM-056's missingness likelihood and
WG-BM-054's joint are *stipulated*. Nothing tests a system that has to estimate
them, which is the case where MNAR corrections go wrong in the opposite
direction.

**Alert fatigue and dynamic credibility.** WG-BM-058 shows one over-escalation.
The cost of the *next* warning being believed less is real, dynamic, and absent
from every loss matrix here.

Also uncovered: directed-graph cut theory, the three traversal conventions
WG-BM-019 rejects, responder-on-responder conflict, terrain across a resolution
change, ensemble-provenance reporting, and proper scoring rules beyond Brier.
Outside the scope of this repository entirely: realistic fire behaviour,
calibration of physical parameters, numerical accuracy at scale, performance,
traffic microsimulation and human factors.

## 8. Which benchmarks are mandatory before the OSSE scales?

The eight-benchmark gate, specified with rationale in
`reports/INTEGRATION_COVERAGE.md`:

```
WG-BM-049  K6   posterior update
WG-BM-050  K7   information with no decision value
WG-BM-052  K9   late information
WG-BM-053  K10  timely weaker information
WG-BM-054  K11  correlated observations
WG-BM-056  K13  informative missingness
WG-BM-057  K14  non-detection is not absence
WG-BM-061  L3   robust action despite an unresolved state
```

Four of the eight (K9, K10, K13, L3) concern the **usefulness** of information
rather than its quantity — the axis an OSSE built on information-theoretic
scores does not have, and the axis on which its recommendations are most likely
to be wrong.

## 9. Which benchmarks are mandatory before integration?

Per repository in `reports/INTEGRATION_COVERAGE.md`. Across all of them, the
ten that no WildfireGuardian component touching the relevant domain should be
integrated without:

| Benchmark | Requirement |
|---|---|
| `WG-BM-004` | missing data propagates as undefined, never as zero |
| `WG-BM-014` | availability time, not acquisition time |
| `WG-BM-019` | edge safety over the traversal interval, convention declared |
| `WG-BM-022` | the dispatch chain includes on-scene time |
| `WG-BM-026` | dispatch feasibility is a set, not a scalar |
| `WG-BM-034` | joint hazard probabilities come from scenarios |
| `WG-BM-037` | uncertainty quantified at the unit of randomisation |
| `WG-BM-047` | the decision threshold is derived from the loss matrix |
| `WG-BM-049` | observation, posterior, decision, in that order |
| `WG-BM-057` | a non-detection is a likelihood ratio, not a certainty |

If only one can be adopted, adopt **WG-BM-026**: a system reporting a single
latest-safe-dispatch time is wrong about a 16-minute window while displaying 24
minutes of margin, and no downstream care recovers from that.

## 10. What can benchmark success NOT establish?

**Passing all benchmarks establishes semantic consistency with these reference
cases. It does not establish real-world model validity.**

Specifically, a green run says nothing about:

* **accuracy on a real landscape.** The largest network here has five nodes and
  the largest raster is 7x7.
* **calibration of any physical parameter.** Every spread rate, travel time,
  pickup duration, likelihood and loss is a stipulated input. Nothing asks
  whether any of them resembles a fire.
* **the loss matrices.** Half the K and L results turn on a threshold derived
  from losses that were invented for the benchmark. Whether an entrapment is 99
  times worse than a delay is a question for an incident commander.
* **numerical behaviour at scale.** Grid convergence, conditioning, accumulation
  over long integrations.
* **performance.** Every reference solver here is deliberately the slowest
  obviously-correct implementation.
* **composition.** Each benchmark exercises one component. Two components that
  each pass can still disagree about units across their interface; that is what
  `benchmarks/integration_future/` is for, and it is empty.
* **human factors.** Compliance, notification response, shadow evacuation,
  household preparation time, and the alert fatigue that WG-BM-058's
  over-escalation would cause.
* **that the suite itself is right.** `reports/BENCHMARK_SELF_AUDIT.md` records
  nine occasions on which it was not, including a reference solver that was
  wrong and two benchmarks that claimed detections they did not have.

What a green run does establish is narrow and real: **the component means by
"feasible route", "latest dispatch", "available observation", "posterior",
"decision threshold" and "value of information" what this programme means by
them**, on cases where the right answer is known by derivation. That is a
precondition for the realistic work being meaningful, and it is the part that can
be established with certainty.

Anyone writing "validated against the WildfireGuardian benchmark suite" should
write the narrow claim.
