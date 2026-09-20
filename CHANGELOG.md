# Changelog

## v0.1.0 — frozen

**66 benchmarks. 39 mutations, all detected. 183 tests. No required runtime
dependencies.**

> Passing all benchmarks establishes semantic consistency with these reference
> cases. It does not establish real-world model validity.

The suite is frozen here. A benchmark is added only when a real project failure
exposes a missing case (WG-D-018).

### Added — stochastic information, probabilistic forecasting and risk

Three families, 23 benchmarks, closing the largest gap recorded in the initial
suite: every information source had been a deterministic signal, so a system
could be better by every deterministic metric and worse at every boundary
decision and the suite would have passed it.

**Family K — probabilistic forecasts (WG-BM-044..058).** Keeps five things apart
that are routinely treated as one: a point prediction, a predictive
distribution, a scenario ensemble, a posterior belief and a decision.

* two forecasts with the same mean requiring opposite actions; a forecast with a
  third of another's location error and five units more regret;
* decision thresholds derived from the loss matrix — `p* = Lc/Lf` and
  `p* = Lc/(Lc+Lf)`, neither of them 0.5, and 0.01 at a 99:1 loss ratio;
* coherent ensembles with admissibility and renormalisation;
* the posterior-to-decision chain, exact EVSI by enumeration, an observation
  with 0.0131 bits of information and an EVSI of exactly zero;
* statistical against operational value — the same sensor worth 22 and 0 — and a
  weak timely sensor beating a perfect late one 13 to 0;
* correlated sensors, duplicate evidence, informative missingness, false
  negatives and false positives.

**Family L — decision risk (WG-BM-059..063).** Expected loss against worst case
and CVaR with the objective as a declared input; `report_only` declines to name
a winner. State resolution and decision resolution as independent axes: an
almost uniform ensemble with `EVPI = 0`, and a 97%-resolved world whose
recommendation turns on 0.21 of expected loss.

**Family M — calibration (WG-BM-064..066).** Reliability and the Murphy
decomposition; overconfidence with a decision cost; aggregate calibration
masking a 0.3 error in every stratum.

### Added — machinery

* three solvers (`probabilistic`, `risk`, `calibration`);
* 15 mutations, taking the total to 39;
* independent Bayes-by-enumeration, EVSI by enumerating every decision rule,
  Simpson quadrature against `erf`, and per-case Brier scores;
* four figures, including the K3 decision-threshold plot;
* `reports/INTEGRATION_COVERAGE.md`, `reports/BENCHMARK_SELF_AUDIT.md`,
  `reports/V0_1_SCIENTIFIC_AUDIT.md`.

### Changed

* **Exactness vocabulary** is now `CLOSED_FORM`, `FINITE_ENUMERATION`,
  `NUMERIC_REFERENCE` and `SEEDED_STOCHASTIC_VALIDATION`. This was the **only**
  change to the 43 deterministic benchmarks: 43 single-token lines, no expected
  value, input, convention or tolerance touched, and all 43 still pass.
* **Acquisition follows decision value.** `recommended_observation` is now the
  observation with the greatest operational EVSI and is `null` when none is
  worth acquiring (WG-D-016).

### Fixed

* the log-likelihood ratio of a perfectly discriminating sensor raised a domain
  error rather than being reported as absent;
* the schema's `label` pattern did not cover the new families.

Both are in `reports/BENCHMARK_SELF_AUDIT.md` with the seven earlier
corrections.

---

## Initial suite

43 benchmarks in families A–J: terrain, road graphs, analytic fire fields,
observation, time-dependent routing, assisted dispatch and the traffic conflict,
forecast value, scenario uncertainty, statistics and robust protectability. 24
mutations, all detected. Two independent solver implementations and a third
hand-written derivation of every headline number.

Notable at the time: WG-BM-036 failed on its first run and the bug was in the
reference solver, not the expected value — the concrete justification for
WG-D-002, that expected values are authored and never harvested.

---

## Tagging

The `v0.1.0` tag marks the commit that introduced this entry. It was not pushed
from the environment that produced it: the git relay there returns HTTP 403 on
tag refs while permitting branch pushes. To create it:

```bash
git tag -a v0.1.0 <commit> -m "v0.1.0 - WildfireGuardian benchmark suite"
git push origin v0.1.0
```
