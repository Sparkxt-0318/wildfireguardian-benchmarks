# Benchmark readiness

**Read this before the pass count.**

As of this writing the suite contains 43 benchmarks, all passing against the
reference solvers, with 24 of 24 injected bugs detected and 113 tests green.
None of those numbers is the answer to "is WildfireGuardian validated?" This
document answers the five questions that matter.

| | |
|---|---|
| benchmarks | 43 |
| hand-checkable | 43 / 43 |
| exact (analytic or exhaustive) | 42 / 43 |
| seeded stochastic | 1 / 43 |
| difficulty: basic / intermediate / adversarial | 11 / 11 / 21 |
| distinct failure modes targeted | 77 |
| mutations injected / detected | 24 / 24 |
| required third-party runtime dependencies | 0 |

---

## 1. Which scientific errors can these benchmarks detect?

Each of the following is caught by at least one benchmark and demonstrated by a
mutation that flips the benchmark from pass to fail. The full machine-generated
matrix is `reports/MUTATION_MATRIX.md`.

**Time and information**

| Error | Detected by |
|---|---|
| Future information leakage (latency ignored) | `WG-BM-014` |
| Information used after the decision deadline | `WG-BM-030`, `WG-BM-031`, `WG-BM-043` |
| Stale data presented as current | `WG-BM-015` |

**Hazard representation**

| Error | Detected by |
|---|---|
| Mid-edge hazard (entry-time-only edge safety) | `WG-BM-018`, `WG-BM-019`, `WG-BM-022`-`026` |
| Time-of-arrival collapsed to a final perimeter | `WG-BM-018`, `WG-BM-019`, `WG-BM-020`, `WG-BM-022`-`026` |
| Wind anisotropy dropped | `WG-BM-010` |
| Fuel heterogeneity averaged away | `WG-BM-011` |
| Spot fires ignored | `WG-BM-012` |

**Data quality**

| Error | Detected by |
|---|---|
| Missing imputed as zero | `WG-BM-004`, `WG-BM-015`, `WG-BM-016` |
| Informative missingness treated as missing-at-random | `WG-BM-016` |
| Non-detection treated as evidence of absence | `WG-BM-017` |

**Network and routing**

| Error | Detected by |
|---|---|
| One-way roads traversed in reverse | `WG-BM-008` |
| Unreachable destination selected by proximity | `WG-BM-007` |
| FIFO assumed on a non-FIFO network | `WG-BM-021` |

**Decision structure**

| Error | Detected by |
|---|---|
| Dispatch feasibility assumed monotone | `WG-BM-026` |
| On-scene service time ignored | `WG-BM-022`-`027` |
| Nearest responder base assumed best | `WG-BM-024` |
| Road capacity ignored for responder ingress | `WG-BM-027` |

**Forecast value and uncertainty**

| Error | Detected by |
|---|---|
| Forecast skill equated with decision value | `WG-BM-029`, `WG-BM-030`, `WG-BM-031`, `WG-BM-033`, `WG-BM-043` |
| Correlated hazards multiplied as independent | `WG-BM-034` |
| Scenario inputs averaged instead of outcomes | `WG-BM-035` |

**Statistics**

| Error | Detected by |
|---|---|
| Pseudoreplication (resident-level bootstrap) | `WG-BM-037` |
| Tail risk discarded in favour of the mean | `WG-BM-038` |
| Unpaired comparison across different world samples | `WG-BM-040` |

---

## 2. Which errors remain uncovered?

Fully enumerated in `reports/KNOWN_GAPS.md`. The three that would do the most
damage:

**Probabilistic forecast calibration.** Every information source in the suite
emits a deterministic signal. A system can be better by every deterministic
metric and worse at every boundary decision, and this suite would pass it. This
is the most consequential gap, because the G family is the part of the suite
most likely to be used to justify an investment.

**Multi-resident sequencing.** Every assisted-dispatch benchmark has one
resident and one vehicle. The triage question — who is collected first — is the
first genuinely operational question and is untested.

**A general treatment of informative missingness.** `WG-BM-016`'s correction is
exact *because the scenario stipulates the mechanism*. Nothing tests a mixed
mechanism where that correction is itself biased.

Also uncovered: directed-graph cut theory, the three traversal conventions
WG-BM-019 rejects, responder-on-responder conflict, terrain across a resolution
change, and ensemble-provenance reporting. And outside the scope of this
repository entirely: realistic fire behaviour, calibration, numerical accuracy
at scale, performance, traffic microsimulation and human factors.

---

## 3. Which benchmarks are mathematically exact?

**42 of 43.** Every benchmark is hand-checkable; the exactness class says what
kind of exactness.

**`exact_analytic` — 34 benchmarks.** A closed form derived by hand and written
out in the benchmark README. Slope on a plane is `atan(sqrt(0.02))`; the head
arrival of a wind-driven front at 200 m is `200 / 20`; the latest dispatch in
WG-BM-022 is `20 - (5 + 5 + 5)`. Checked to `1e-9`.

**`exact_enumeration` — 8 benchmarks.** A finite exhaustive enumeration with no
approximation: all simple paths (`WG-BM-005`-`008`), all departures on a
declared grid (`WG-BM-021`), all dispatch times with bisection-refined interval
endpoints (`WG-BM-026`), all burned cells on a declared grid (`WG-BM-012`), all
decision rules (`WG-BM-017`).

One caveat, stated in the benchmark itself: WG-BM-026's
`infeasible_dispatch_below_latest_min` is the first *sampled* failing dispatch
time and depends on the declared 1-minute grid. The *existence* of such a time
is exact and is asserted separately as an invariant.

**`seeded_stochastic` — 1 benchmark.** WG-BM-037's bootstrap intervals are Monte
Carlo estimates from 200 resamples of 10 worlds. Its analytic standard errors
and their ratio are exact and checked to `1e-9`; the bootstrap quantities are
checked against them within a declared band whose width is justified by the
Monte Carlo error.

Three independent derivations back every headline number: the authored value in
`tools/authoring/`, the primary solver, and a hand-written re-derivation in
`tests/test_analytic_identities.py`. Where a second brute-force solver exists
(`tools/analytic_solvers/`), that is a fourth.

---

## 4. Which rely on qualitative expectations?

No benchmark is classed `qualitative`: every one pins numbers. But several pin
numbers whose *magnitude* is a construction choice while the scientific content
is the **sign, the ordering, or the existence** of an effect. For those, the
invariants rather than the pinned values are the claim.

| Benchmark | Pinned, but the real claim is |
|---|---|
| `WG-BM-003` | slope `11.31°` on the flanks — the claim is that the two flanks face **opposite** ways and that exactly 3 crest cells show the zero-slope artefact |
| `WG-BM-017` | regret 95 — the claim is that trusting an unreliable non-detection is **strictly worse** |
| `WG-BM-026` | intervals `[0,4] u [20,34]` — the claim is that the feasible set is **not** an interval and that a failing dispatch **exists** below the latest feasible one |
| `WG-BM-029` | regret 92 — the claim is that a **smaller** error than WG-BM-028's produces a **larger** loss |
| `WG-BM-031` | values +5 / 0 / -40 — the claim is that the value ranking is the **reverse** of the skill ranking |
| `WG-BM-033` | `Delta J = -30` — the claim is that `Delta J < 0` for an 80%-accurate forecast |
| `WG-BM-036` | sup-regret 2 -> 10 — the claim is that expected loss barely moves while the worst-case recommendation **flips** on 0.2% of probability mass |
| `WG-BM-038` | mean 10 vs 12.8, CVaR 100 vs 20 — the claim is that the two criteria **disagree** |
| `WG-BM-040` | -10.33 vs +3 — the claim is the **sign flip** |
| `WG-BM-037` | bootstrap widths — the claim is the **order of magnitude** of the ratio, checked within a declared band |

The loss units throughout the G, H, I and J families are scenario-local and
dimensionless. A loss of 100 in one benchmark and a loss of 100 in another are
not the same quantity, and no benchmark compares them.

---

## 5. Which benchmarks should every WildfireGuardian repository pass before integration?

Three tiers. A repository states which it claims; the claim is checkable with
`wg-benchmarks validate-results`. Conformance levels are defined in
`docs/VALIDATION_STANDARD.md`.

### Tier 1 — Mandatory for every component that touches the relevant domain

Nothing downstream is meaningful until these pass. They are the semantics.

| Benchmark | Requirement it establishes |
|---|---|
| `WG-BM-001`, `WG-BM-002` | slope and aspect conventions, including `null` aspect on flat ground |
| `WG-BM-004` | missing terrain propagates as undefined and never becomes zero |
| `WG-BM-008` | one-way roads are not traversable in reverse |
| `WG-BM-013`, `WG-BM-014` | observation availability is `acquisition + latency`, and the present is not observable |
| `WG-BM-018`, `WG-BM-019` | edge safety is judged over the traversal interval, and the convention is declared |
| `WG-BM-022` | the assisted-dispatch chain includes on-scene time |
| `WG-BM-034` | joint hazard probabilities come from scenarios, not from multiplied marginals |
| `WG-BM-037` | uncertainty is quantified at the unit of randomisation |

### Tier 2 — Mandatory before a component informs a research decision

These are the adversarial cases. A component that fails one of them is not
merely imprecise; it is wrong in a way that will not announce itself.

`WG-BM-007` (unreachable destinations) · `WG-BM-012` (spotting) ·
`WG-BM-015`, `WG-BM-016`, `WG-BM-017` (outage, MNAR, false negatives) ·
`WG-BM-020`, `WG-BM-021` (waiting, non-FIFO) ·
`WG-BM-023`-`027` (service time, base and destination choice, **non-monotone
feasibility**, capacity) ·
`WG-BM-029`-`031`, `WG-BM-033` (skill is not value, timeliness, forecast harm) ·
`WG-BM-035` (no averaging of inputs) ·
`WG-BM-038`, `WG-BM-040` (tail risk, paired comparison) ·
`WG-BM-042`, `WG-BM-043` (realisable value of information)

If only one benchmark from this tier can be adopted, adopt **`WG-BM-026`**. A
system that reports a single "latest safe dispatch time" is wrong about a
16-minute window while displaying 24 minutes of margin, and no amount of
downstream care recovers from that.

### Tier 3 — Should pass, and a failure is a conversation rather than a defect

These pin conventions and calibration choices that a component may legitimately
have made differently. A failure means the two projects disagree about a
definition, and the right resolution is usually a **variant benchmark**, not a
code change.

`WG-BM-003` (the ridge artefact: whether a crest's zero slope is reported as an
artefact or as flat ground) · `WG-BM-005`, `WG-BM-006` (what counts as a single
point of failure) · `WG-BM-009`-`011` (the analytic fire models) ·
`WG-BM-028`, `WG-BM-032` (zero-value cases: a component that never reports zero
added value fails these and should) · `WG-BM-036` (the worst-case criterion) ·
`WG-BM-039` (the practical margin) · `WG-BM-041` (robust protectability)

---

## The honest summary

This suite establishes that a component **means the same thing by its terms as
this programme does**, on cases where the right answer is known. That is a
precondition for realistic work being meaningful, and it is the part that can be
established with certainty.

It establishes nothing about accuracy on a real landscape, about calibration,
about numerical behaviour at scale, or about anything downstream of the model.
Anyone writing "validated against the WildfireGuardian benchmark suite" should
write the narrow claim.

The single most likely way for this suite to mislead is for a component to pass
everything and then be deployed with a probabilistic forecast, multiple
residents per vehicle, and a sensor network that fails for several reasons at
once — the three severe gaps in section 2. Closing them is the work that would
most increase what a green run is worth.
