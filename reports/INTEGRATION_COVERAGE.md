# Cross-repository integration coverage

**This document specifies future conformance requirements. No repository is
integrated yet**, and nothing here should be read as a claim that any of them
passes anything.

Integration, when it happens, is file-based and one-way: a repository writes one
result document per benchmark and this suite reads them with
`wg-benchmarks validate-results`, importing nothing from the implementation. The
mechanics are in `benchmarks/integration_future/README.md`.

---

## Family map

| Family | Subject | Primary consumer |
|---|---|---|
| A (001-004) | terrain preprocessing | assisted-dispatch |
| B (005-008) | road graphs | assisted-dispatch |
| C (009-012) | analytic fire fields | osse |
| D (013-017) | observation availability and missingness | **osse** |
| E (018-021) | time-dependent routing | assisted-dispatch |
| F (022-027) | assisted dispatch, traffic conflict | **assisted-dispatch** |
| G (028-033) | forecast skill versus decision value | **forecast-value** |
| H (034-036) | scenario uncertainty | forecast-value, evaluation |
| I (037-040) | statistics of policy comparison | **evaluation** |
| J (041-043) | robust protectability | forecast-value |
| K (044-058) | probabilistic forecasts and Bayesian belief | **osse**, forecast-value |
| L (059-063) | decision risk and robustness | **evaluation** |
| M (064-066) | forecast calibration | forecast-value, **alert-audit** |

---

## Per-repository conformance requirements

### `wildfireguardian-osse`

An observing-system simulation experiment stands or falls on whether its
information accounting is honest, so this is the largest requirement set.

**Mandatory**

| Benchmarks | Requirement |
|---|---|
| `WG-BM-013`-`017` (D) | observation availability, staleness, outage, fire-correlated dropout, false negatives |
| `WG-BM-049`-`051` (K6-K8) | posterior update, information with no decision value, exact EVSI |
| `WG-BM-052`, `053` (K9, K10) | acquisition time, availability time and deadline kept distinct |
| `WG-BM-054`-`056` (K11-K13) | correlated observations, duplicate evidence, informative missingness |
| `WG-BM-057`, `058` (K14, K15) | detections and non-detections as likelihood ratios, not certainties |
| `WG-BM-061` (L3) | an unresolved state does not imply a need for observation |
| `WG-BM-009`-`012` (C) | the synthetic hazard fields it simulates observations of |

**Expected**

`WG-BM-034` (correlated hazards), `WG-BM-048` (coherent ensembles),
`WG-BM-063` (poor skill, stable decision).

**Rationale.** An OSSE's output is a ranking of observing systems. Every failure
mode in K9-K13 changes that ranking, and three of them — timeliness, correlation
and informative missingness — change it in the direction of recommending more
sensors than are useful.

---

### `wildfireguardian-forecast-value`

**Mandatory**

| Benchmarks | Requirement |
|---|---|
| `WG-BM-028`-`033` (G) | skill is not value; timeliness; strong baselines; forecast harm |
| `WG-BM-041`-`043` (J) | EVPI, realisable value, and information that arrives too late |
| `WG-BM-044`-`047` (K1-K4) | predictive distributions and loss-derived decision thresholds |
| `WG-BM-064`-`066` (M) | reliability, overconfidence, conditional calibration |

**Expected**

`WG-BM-048` (ensemble coherence), `WG-BM-050` (zero-value information),
`WG-BM-063` (poor skill, stable decision), `WG-BM-035`, `WG-BM-036`.

**Rationale.** The repository's product is a value claim. `WG-BM-032` and
`WG-BM-041` are the ones to insist on: a system that never reports zero added
value cannot be believed when it reports a positive one.

---

### `wildfireguardian-assisted-dispatch`

**Mandatory**

| Benchmarks | Requirement |
|---|---|
| `WG-BM-001`-`004` (A) | slope, aspect and no-data conventions |
| `WG-BM-005`-`008` (B) | egress redundancy, reachability, one-way roads |
| `WG-BM-018`-`021` (E) | interval safety, waiting, non-FIFO travel |
| `WG-BM-022`-`027` (F) | the dispatch arithmetic, **including WG-BM-026** |
| `WG-BM-046`, `047` (K3, K4) | when dispatch is triggered on a probability, the threshold is derived from loss |

**Expected**

`WG-BM-059`, `WG-BM-060` (the objective behind a dispatch ranking),
`WG-BM-062` (report the margin, not just the recommendation).

**Rationale.** `WG-BM-026` is the single most important requirement in this
table. A dispatch tool that reports one "latest safe dispatch time" is wrong
about a 16-minute window while displaying 24 minutes of margin.

---

### `wildfireguardian-evaluation`

**Mandatory**

| Benchmarks | Requirement |
|---|---|
| `WG-BM-037`-`040` (I) | pseudoreplication, tail risk, practical equivalence, paired comparison |
| `WG-BM-059`, `060` (L1, L2) | the objective is declared, and the recommendation follows it |
| `WG-BM-036` (H3) | sup-regret moves with ensemble size; report the provenance |
| `WG-BM-064`-`066` (M) | calibration assessed conditionally, not only in aggregate |

**Expected**

`WG-BM-061`-`063` (state resolution and decision stability reported separately),
`WG-BM-032` (comparison against the best simple baseline).

**Rationale.** `WG-BM-037` and `WG-BM-040` are the two that most often make a
published comparison meaningless: one inflates confidence by a factor of 33, the
other reverses both the sign and the magnitude of the effect.

---

### `wildfireguardian-alert-audit`

**Mandatory**

| Benchmarks | Requirement |
|---|---|
| `WG-BM-057`, `058` (K14, K15) | a detection is not proof and a non-detection is not absence |
| `WG-BM-064`-`066` (M) | alert probabilities are calibrated, and conditionally so |
| `WG-BM-046`, `047` (K3, K4) | the alert threshold is derived from the loss matrix |
| `WG-BM-014` (D2) | an alert cannot use information it could not have had |
| `WG-BM-017` (D5) | absence of detection is not a safety claim |

**Expected**

`WG-BM-055` (one incident report arriving twice must not raise confidence),
`WG-BM-056` (a station going quiet is an alert condition, not a data gap).

**Rationale.** An audit of alerts is an audit of thresholds and base rates.
`WG-BM-058` is the standing risk: the same detector supports a 22% or a 78%
posterior depending only on the base rate, and an alert issued without it has
discarded the input doing most of the work.

---

## The OSSE gate

**Before forecast-value experiments in `wildfireguardian-osse` scale beyond the
minimum viable experiment, the following must pass.** These eight are the
minimum at which an OSSE's information accounting can be believed; each
corresponds to a way the experiment would otherwise recommend the wrong
observing system.

| Benchmark | | Without it, the OSSE would |
|---|---|---|
| `WG-BM-049` | K6 posterior update | not have a correct belief update at all |
| `WG-BM-050` | K7 information without decision value | recommend acquiring information that cannot change an action |
| `WG-BM-052` | K9 late information | credit a sensor that reports after the deadline |
| `WG-BM-053` | K10 timely weaker information | rank an eight-times-more-informative sensor above a usable one |
| `WG-BM-054` | K11 correlated observations | overstate the value of adding co-located sensors |
| `WG-BM-056` | K13 informative missingness | treat sensor loss as a data gap rather than as evidence |
| `WG-BM-057` | K14 non-detection | read a clear sweep as an all-clear |
| `WG-BM-061` | L3 robust action despite an unresolved state | demand observation whenever the ensemble disagrees |

Four of the eight (K9, K10, K13, L3) are about the **usefulness** of information
rather than its quantity, which is the axis an OSSE built on information-theoretic
scores does not have.

**Gate condition:** all eight pass under `wg-benchmarks validate-results`, with
the results produced by the OSSE's own pipeline rather than by a harness written
for the gate.

---

## What this document does not do

It does not integrate anything, it does not claim any repository passes
anything, and it does not constrain how a repository produces its result
documents. It records which benchmarks each repository will be asked to satisfy,
so that the requirement is known before anybody is under pressure to ship.
