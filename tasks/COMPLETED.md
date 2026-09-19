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
