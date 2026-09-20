# Completed work

## Phase 1 — Foundation

### Infrastructure

* **Benchmark schema** (`schemas/benchmark.schema.json`) and **expected-result
  schema** (`schemas/expected_result.schema.json`), draft 2020-12, with a
  built-in validator for the subset used so the suite needs no `jsonschema`.
* **Zero-dependency YAML layer** (`wg_benchmarks/yamlio.py`): PyYAML when
  present, a restricted-subset parser when absent, and a byte-stable dumper of
  our own so regenerating a benchmark produces a reviewable diff. Checked
  against PyYAML on every document in the repository by
  `tests/test_yamlio.py`.
* **Comparison semantics** (`wg_benchmarks/compare.py`): strict types, declared
  tolerances, extra keys permitted, missing keys fatal.
* **Runner, registry and CLI** with `list`, `run`, `run-category`, `validate`,
  `validate-results`, `report`, `mutate` and `figures`.

### Benchmarks

43 scenarios in ten families:

| Family | Ids | Subject |
|---|---|---|
| A | 001-004 | terrain preprocessing |
| B | 005-008 | road graphs |
| C | 009-012 | fire / hazard fields |
| D | 013-017 | observation |
| E | 018-021 | routing |
| F | 022-027 | assisted dispatch and the traffic conflict |
| G | 028-033 | forecast value |
| H | 034-036 | scenario uncertainty |
| I | 037-040 | statistics |
| J | 041-043 | robust protectability |

All expected values authored by hand in `tools/authoring/`, with the derivation
written out in each benchmark README.

### Solvers

* **Primary reference solvers** for terrain, graphs, fire, observation, routing,
  dispatch, decisions, scenarios and statistics.
* **Independent brute-force solvers** in `tools/analytic_solvers/`, sharing no
  code with the primary ones, cross-checked in `tests/test_cross_check.py`.

### Verification

* **24 mutations**, all detected; no benchmark claims a detection it does not
  achieve.
* **113 tests**, including `tests/test_analytic_identities.py`, a third
  independent derivation of every headline number.
* **Nine SVG figures**, generated from the solver output with no plotting
  dependency.

## Findings recorded during construction

**A benchmark caught a bug in its own reference solver.** WG-BM-036 failed on
first run. `analyse_ensemble` computed `worst_case_loss` as the maximum over the
entire shared loss table rather than over the ensemble's own scenarios, so
`policy_a`'s worst case in the five-member ensemble was reported as 300 — a
value that only exists in the seven-member one. The authored expectation was
right; the solver was fixed. This is the concrete justification for WG-D-002
(expected values are authored, never harvested).

**A benchmark was found to be overclaiming.** WG-BM-028 declared that it
detected the `skill_implies_value` mutation. It does not: with two equally
valuable forecasts, ranking by skill picks an equally good policy and the
benchmark's declared answer is unchanged. The declaration was removed and the
README now states the limitation explicitly (WG-D-012).

**Two conventions were forced into the open.** WG-BM-019 (mid-edge closure) has
no convention-free answer, and WG-BM-020 (waiting) has a different answer under
each waiting policy. Both now declare the suite's choice *and* report what the
alternative would have concluded.

---

## Phase 2 — Stochastic information, probabilistic forecasting and risk

### Benchmarks

23 new scenarios in three families, taking the suite from 43 to 66:

| Family | Ids | Subject |
|---|---|---|
| K | 044-058 | probabilistic forecasts, decision thresholds, coherent ensembles, posteriors, the value and timeliness of observations, correlated and duplicate evidence, informative missingness, detections and non-detections |
| L | 059-063 | expected loss against worst case and CVaR under a declared objective; state resolution and decision resolution as independent axes |
| M | 064-066 | reliability and the Murphy decomposition; overconfidence with a decision cost; aggregate calibration masking conditional failure |

51 of the 66 benchmarks are now `CLOSED_FORM` and 14 `FINITE_ENUMERATION`. No
benchmark uses Monte Carlo as truth.

### Machinery

* **Three new solvers** — `probabilistic.py` (predictive thresholds, Bayesian
  decision, coherent ensembles), `risk.py` (declared objectives, state and
  decision resolution), `calibration.py` (reliability and the Murphy
  decomposition).
* **Schema extension** — an `information_structure` block, three new categories,
  and the four-class `exactness` vocabulary. The only change to the 43
  deterministic benchmarks was that vocabulary rename; all 43 still pass.
* **15 new mutations**, taking the total to 39, all detected.
* **New independent solvers** — Bayes by enumeration, EVSI by enumerating every
  decision rule (which never forms a posterior), the normal tail by Simpson
  quadrature with a declared error bound, and the Brier score by per-case
  enumeration.
* **70 new tests**, taking the total to 183.
* **Four new figures**, including the K3 decision-threshold plot, which is the
  clearest picture in the repository of where `p*` comes from.

### Reports

* `reports/INTEGRATION_COVERAGE.md` — per-repository conformance requirements
  and the eight-benchmark OSSE gate.
* `reports/BENCHMARK_SELF_AUDIT.md` — every occasion on which this repository
  was wrong.
* `reports/V0_1_SCIENTIFIC_AUDIT.md` — the frozen v0.1.0 statement.

## Findings recorded during Phase 2

**A second overclaim, with a different right answer.** WG-BM-050 (K7) declared
that it detected `choose_by_information_gain` and did not: with one observation,
ranking by information and ranking by value select the same one. Unlike
WG-BM-028 (SA-2), whose claim had to be dropped, this benchmark's *subject* is
exactly what the mutation gets wrong — so the solver was changed to report
`observations_worth_acquiring` by operational EVSI rather than by information
gain. The clean solver now says "acquire nothing" and the mutated one says
"acquire". Recorded as WG-D-016; the two cases together are the reason
`reports/BENCHMARK_SELF_AUDIT.md` exists.

**Three machinery defects**, each caught by a test rather than by review: the
log-likelihood ratio of a perfectly discriminating sensor raising a domain
error, the schema's label pattern not covering the new families, and a float
comparison in a third-derivation test that had to be given a tolerance. All are
in the self-audit.
