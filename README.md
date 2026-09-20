# wildfireguardian-benchmarks

**A unit-test laboratory for wildfire decision science.**

Sixty-six small, transparent, hand-checkable scenarios whose scientifically
correct answers are known by derivation, together with reference solvers,
adversarial variants, mutation tests and a conformance CLI.

**Frozen at `v0.1.0`** (see `CHANGELOG.md`). The suite stops growing here; a
benchmark is added only when a real project failure exposes a missing case.

```
> A complicated simulation producing plausible-looking maps is not validation.
```

This repository exists to answer one question:

> Can we construct simple wildfire-decision scenarios where the expected
> behaviour is known, so that future models can be tested for **semantic
> correctness** before they are trusted on large realistic simulations?

It is independent of every production WildfireGuardian repository by design —
see `docs/PROJECT_CONTEXT.md` for why that independence is a scientific
requirement rather than a packaging preference.

---

## Quick start

No installation and no third-party dependencies are required.

```bash
python -m wg_benchmarks list                  # 66 benchmarks
python -m wg_benchmarks run                   # run them all
python -m wg_benchmarks run WG-BM-026 -v      # one benchmark, full result document
python -m wg_benchmarks run-category dispatch # one category
python -m wg_benchmarks validate              # schema + structural checks
python -m wg_benchmarks mutate                # inject 24 bugs, see which are caught
python -m wg_benchmarks report                # regenerate reports/
python -m wg_benchmarks figures               # regenerate the SVG figures
python tests/run_tests.py                     # the test suite (uses pytest if present)
```

Installing the package gives you the `wg-benchmarks` entry point:

```bash
pip install -e .
wg-benchmarks run
```

## Checking your own implementation

The integration path is file-based and imports nothing from your code. Write one
result document per benchmark and hand the directory over:

```bash
wg-benchmarks validate-results path/to/results/
```

Each file is `WG-BM-0NN.yaml` (or `.yml` / `.json`) holding either the result
mapping or a mapping with a `results` key. Only the keys a benchmark pins down
are compared, so you may report as much extra detail as you like.

`docs/VALIDATION_STANDARD.md` defines the three conformance levels and — more
importantly — states precisely what a passing suite does and does not establish.

## What is in here

| Family | Benchmarks | Subject |
|---|---|---|
| **A** | WG-BM-001..004 | terrain: slope, aspect, ridges, no-data |
| **B** | WG-BM-005..008 | road graphs: egress redundancy, reachability, one-way roads |
| **C** | WG-BM-009..012 | fire: radial, wind-driven, fuel boundaries, spotting |
| **D** | WG-BM-013..017 | observation: latency, outage, MNAR dropout, false negatives |
| **E** | WG-BM-018..021 | routing: mid-edge hazard, waiting, non-FIFO travel |
| **F** | WG-BM-022..027 | assisted dispatch: the latest-dispatch arithmetic and where it breaks |
| **G** | WG-BM-028..033 | forecast value: skill is not value |
| **H** | WG-BM-034..036 | uncertainty: correlation, mutual exclusivity, ensemble size |
| **I** | WG-BM-037..040 | statistics: pseudoreplication, tail risk, equivalence, selection bias |
| **J** | WG-BM-041..043 | protectability: when information is worth something |
| **K** | WG-BM-044..058 | probabilistic forecasts: distributions, thresholds, posteriors, the value of an observation |
| **L** | WG-BM-059..063 | decision risk: expected loss, CVaR, and when a decision is resolved |
| **M** | WG-BM-064..066 | forecast calibration: reliability, overconfidence, conditional failure |

Full listing with purposes: `reports/BENCHMARK_CATALOG.md`.

### Five benchmarks worth reading first

**[WG-BM-026 (F5)](benchmarks/dispatch/WG-BM-026_F5_non_monotone_feasibility/)** —
the ingress corridor is overrun at minute 10 and reopened at minute 20, so the
feasible dispatch set is `[0, 4] u [20, 34]`. The latest feasible dispatch is 34
and **dispatching at minute 10 fails**. Any system that reports a single
"latest safe dispatch time" is wrong about a 16-minute window, while displaying
24 minutes of margin.

**[WG-BM-030 (G3)](benchmarks/forecast_value/WG-BM-030_G3_accurate_but_late/)** —
a forecast with skill 0.98 and 10 m spatial error, issued at minute 30 for a
decision that must be taken by minute 20. EVPI is 5; realisable value is 0; the
realised value of waiting for it is **-90**. Skill, EVPI, realisable value and
realised value are four different numbers and only the last two describe what
happens to the people in the scenario.

**[WG-BM-016 (D4)](benchmarks/observations/WG-BM-016_D4_fire_correlated_failure/)** —
five sensors, each destroyed when the fire reaches it. At minute 60 every
surviving sensor reports "unburnt", so the complete-case estimate of the burnt
fraction is 0.0 against a truth of 0.6. The estimate is maximally wrong, and
there is nothing in the reporting record to notice.

**[WG-BM-050 (K7)](benchmarks/probabilistic_forecast/WG-BM-050_K7_information_without_decision_value/)** —
an observation with **0.0131 bits** of mutual information and an EVSI of
**exactly zero**. It tells you something and it cannot change what you do.
Perfect information would still be worth 1.0, so the zero belongs to this sensor
rather than to the decision. The counterexample to "we are uncertain, therefore
we should observe more".

**[WG-BM-061 (L3)](benchmarks/risk/WG-BM-061_L3_unresolved_state_resolved_decision/)** —
an almost uniform three-way ensemble, and one action that is optimal in every
member. The world is as unresolved as it can be and `EVPI = 0`. Read next to
**WG-BM-062**, where the world is 97% resolved and the recommendation turns on
0.21 of expected loss.

## Layout

```
docs/          the conventions, the philosophy, the decision log, the glossary
benchmarks/    66 benchmark directories: benchmark.yaml, README.md, inputs/, expected/, figures/
schemas/       JSON Schema for benchmark descriptors and expected results
wg_benchmarks/ the primary reference solvers, runner, CLI, mutation registry, plotting
tools/
  authoring/       the scripts that generate benchmarks/ — where expected values are authored
  analytic_solvers/ independent brute-force solvers, used only to cross-check the primary ones
  validators/      schema and structural checks, and the external-results checker
  plotting/        figure generation
reports/       generated catalogue, coverage and mutation matrix; the v0.1.0 audit,
               the self-audit, the known gaps and the integration requirements
tasks/         roadmap, current work, completed work
tests/         183 tests, including a third independent derivation of every headline number
```

## How a benchmark is put together

Every benchmark directory holds:

```
benchmark.yaml   metadata, declared assumptions, headline expected values, tolerances
README.md        the scenario and the full derivation, checkable by hand
inputs/          the scenario, as data
expected/        the machine-checked answer plus its derivation and invariants
figures/         SVG, where a picture earns its place
```

The rule that makes it worth anything:

> **Expected values are authored by hand from the scenario. They are never
> copied out of a solver run.**

Expected answers come from one of four sources only — a closed-form probability,
an exact finite enumeration, an independently implemented brute force, or
numerical integration with a declared error bound. **Monte Carlo is never used as
truth where an exact answer exists**, and a Monte Carlo approximation is never
described as exact. Every benchmark declares which class it is in:
`CLOSED_FORM` (51), `FINITE_ENUMERATION` (14), `NUMERIC_REFERENCE` (0) or
`SEEDED_STOCHASTIC_VALIDATION` (1).

This is not ceremony. During construction, WG-BM-036 failed on its first run;
the authored value was right and the reference solver was wrong. Had the
expected value been harvested, the bug would have become the expected answer.
`reports/BENCHMARK_SELF_AUDIT.md` records that and eight other occasions on
which this repository was wrong, including two benchmarks that claimed
detections they did not have.

## Mutation testing

Thirty-nine plausible implementation bugs can be injected into the reference
solvers — entry-time edge safety, latency dropped, missing imputed as zero,
marginals multiplied, residents bootstrapped, pickup ignored, one-way roads
reversed, forecast skill mistaken for value, posteriors replaced by priors,
duplicate evidence double counted, non-detections read as absence, acquisition
judged by information gain, the declared risk objective ignored. **All 39 are
caught**, and the suite fails if any benchmark claims a detection it does not
achieve.

```bash
python -m wg_benchmarks mutate --strict
```

Results: `reports/MUTATION_MATRIX.md`.

## Honest limitations

> **Passing all benchmarks establishes semantic consistency with these reference
> cases. It does not establish real-world model validity.**

Read `reports/V0_1_SCIENTIFIC_AUDIT.md` before the pass count. In short: nothing
here resembles a real fire, nothing is calibrated, nothing tests numerical
behaviour at scale, and human factors are absent entirely. A component that
passes everything has demonstrated that its **semantics** are right on cases
where the answer is known — which is a precondition for the realistic work being
meaningful, and is the part that can be established with certainty.

Known gaps are enumerated in `reports/KNOWN_GAPS.md`; the future conformance
requirements for each WildfireGuardian repository, including the eight-benchmark
gate before the OSSE scales, are in `reports/INTEGRATION_COVERAGE.md`.

## Contributing

`AGENTS.md` describes the three-role workflow (designer, independent solver,
adversarial tester) and the rules a new benchmark must follow.
