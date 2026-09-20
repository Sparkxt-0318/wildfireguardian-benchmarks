"""Author the D family: observation benchmarks (WG-BM-013..017)."""

from __future__ import annotations

from common import report, write_benchmark

SCRIPT = "author_observation.py"
TOLERANCE = {"default": 1.0e-09}


def truth_value(minutes: float) -> float:
    """Ground truth used by D1-D3: distance from the fire front, 1000 - 20 t metres."""
    return 1000.0 - 20.0 * minutes


TRUTH = [{"time_min": float(t), "value": truth_value(t)} for t in range(0, 61, 5)]


def main() -> None:
    written = []

    # ------------------------------------------------------------------ D1
    written.append(write_benchmark(
        directory="benchmarks/observations/WG-BM-013_D1_zero_latency",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-013",
            "label": "D1",
            "title": "Zero-latency perfect observation equals contemporaneous truth",
            "category": "observation",
            "difficulty": "basic",
            "purpose": "Positive control for the observation pipeline: with no latency and no "
                       "outage, the available observation is exactly the current truth.",
            "solver": "observation.availability",
            "assumptions": {
                "latency_min": 0,
                "observation_error": False,
                "availability_rule": "acquisition_time + latency <= query_time",
            },
            "expected_behavior": {
                "queries": {"q10": {"value": 800.0, "matches_truth": True}},
            },
            "tolerance": TOLERANCE,
            "exactness": "CLOSED_FORM",
            "detects": ["observation_pipeline_offset"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "If this fails, nothing else in the D family means anything.",
        },
        inputs={
            "observations": {
                "description": "One perfect sensor reporting every 5 minutes with no latency. "
                               "Truth is the distance from the fire front, 1000 - 20t metres.",
                "max_staleness_min": 5.0,
                "truth": TRUTH,
                "sensors": [
                    {
                        "id": "s_perfect",
                        "latency_min": 0.0,
                        "records": [
                            {"acquisition_time_min": float(t), "value": truth_value(t)}
                            for t in range(0, 61, 5)
                        ],
                    }
                ],
                "queries": [
                    {"id": "q10", "sensor": "s_perfect", "at_time_min": 10.0},
                    {"id": "q25", "sensor": "s_perfect", "at_time_min": 25.0},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-013",
            "source": "hand_derivation",
            "derivation": (
                "Latency is zero, so a record acquired at time t is available from time t. At a "
                "query time that coincides with an acquisition the latest available record is the "
                "one acquired at that instant, staleness is 0 and the value equals the truth. "
                "truth(10) = 1000 - 200 = 800 m; truth(25) = 1000 - 500 = 500 m. The error is "
                "exactly zero in both cases."
            ),
            "results": {
                "queries": {
                    "q10": {
                        "latest_acquisition_time_min": 10.0,
                        "value": 800.0,
                        "truth_value": 800.0,
                        "error": 0.0,
                        "matches_truth": True,
                        "staleness_min": 0.0,
                        "stale": False,
                        "status": "current",
                        "available_records": 3,
                    },
                    "q25": {
                        "latest_acquisition_time_min": 25.0,
                        "value": 500.0,
                        "truth_value": 500.0,
                        "error": 0.0,
                        "matches_truth": True,
                        "staleness_min": 0.0,
                        "stale": False,
                        "status": "current",
                        "available_records": 6,
                    },
                }
            },
            "invariants": [
                {
                    "expression": "all(q['error'] == 0.0 for q in r['queries'].values())",
                    "description": "a perfect zero-latency sensor has zero error at every query",
                }
            ],
        },
        readme="""
# WG-BM-013 (D1) — Zero-latency perfect observation

## Scenario

One sensor, reporting every 5 minutes, latency zero, no measurement error. The
truth it measures is the distance from the fire front,
`truth(t) = 1000 - 20 t` metres.

## Derivation

An observation acquired at `t_a` with latency `L` is available at query time `t`
when `t_a + L <= t`. With `L = 0` and a query at an acquisition instant, the
latest available record is the one acquired at that instant:

```
q10:  latest acquisition = 10 min, value = truth(10) = 800 m, staleness 0
q25:  latest acquisition = 25 min, value = truth(25) = 500 m, staleness 0
```

The number of available records is the count of acquisitions at or before the
query: 3 at `t = 10` (0, 5, 10) and 6 at `t = 25` (0, 5, 10, 15, 20, 25).

## Purpose

This is a positive control. It asserts the *absence* of an accidental offset:
no off-by-one in the record index, no half-interval shift, no silent
interpolation. If a system fails here it will fail every other benchmark in the
D family for reasons that have nothing to do with latency, outage or
missingness, and the diagnosis would be confusing without this case to isolate
it.
""",
    ))

    # ------------------------------------------------------------------ D2
    written.append(write_benchmark(
        directory="benchmarks/observations/WG-BM-014_D2_fixed_latency",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-014",
            "label": "D2",
            "title": "Ten-minute acquisition latency makes the present unobservable",
            "category": "observation",
            "difficulty": "adversarial",
            "purpose": "The decision maker at time t may only see observations acquired at or "
                       "before t - 10. Future information leakage is the single most common way "
                       "an offline evaluation flatters a forecasting system.",
            "solver": "observation.availability",
            "assumptions": {
                "latency_min": 10,
                "availability_rule": "acquisition_time + latency <= query_time",
                "no_nowcast_extrapolation": True,
            },
            "expected_behavior": {
                "queries": {
                    "q25": {"latest_acquisition_time_min": 15.0, "value": 700.0},
                },
            },
            "tolerance": TOLERANCE,
            "exactness": "CLOSED_FORM",
            "detects": ["future_information_leakage", "latency_ignored"],
            "mutations_expected_to_fail": ["observation_future_leak"],
            "hand_checkable": True,
        },
        inputs={
            "observations": {
                "description": "One sensor reporting every 5 minutes with a fixed 10-minute "
                               "acquisition-to-availability latency.",
                "max_staleness_min": 15.0,
                "truth": TRUTH,
                "sensors": [
                    {
                        "id": "s_delayed",
                        "latency_min": 10.0,
                        "records": [
                            {"acquisition_time_min": float(t), "value": truth_value(t)}
                            for t in range(0, 61, 5)
                        ],
                    }
                ],
                "queries": [
                    {"id": "q05", "sensor": "s_delayed", "at_time_min": 5.0},
                    {"id": "q25", "sensor": "s_delayed", "at_time_min": 25.0},
                    {"id": "q40", "sensor": "s_delayed", "at_time_min": 40.0},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-014",
            "source": "hand_derivation",
            "derivation": (
                "With latency 10 a record acquired at t_a is available from t_a + 10. "
                "At t = 5 the only candidate acquisitions are 0 and 5, available from 10 and 15 "
                "respectively, so nothing is available and the query returns no_data. "
                "At t = 25 the available acquisitions are those with t_a <= 15, so the latest is "
                "15 with value truth(15) = 700 m, staleness 10 min. The contemporaneous truth is "
                "truth(25) = 500 m, so the available observation is in error by +200 m: the fire "
                "is 200 m closer than the newest available report says. "
                "At t = 40 the latest available acquisition is 30, value truth(30) = 400 m, "
                "against a contemporaneous truth of 200 m."
            ),
            "results": {
                "queries": {
                    "q05": {
                        "available_records": 0,
                        "latest_acquisition_time_min": None,
                        "value": None,
                        "status": "no_data",
                        "stale": True,
                    },
                    "q25": {
                        "available_records": 4,
                        "latest_acquisition_time_min": 15.0,
                        "value": 700.0,
                        "truth_value": 500.0,
                        "error": 200.0,
                        "matches_truth": False,
                        "staleness_min": 10.0,
                        "stale": False,
                        "status": "current",
                    },
                    "q40": {
                        "available_records": 7,
                        "latest_acquisition_time_min": 30.0,
                        "value": 400.0,
                        "truth_value": 200.0,
                        "error": 200.0,
                        "matches_truth": False,
                        "staleness_min": 10.0,
                        "stale": False,
                        "status": "current",
                    },
                },
            },
            "invariants": [
                {
                    "expression": "all(q['latest_acquisition_time_min'] is None or q['staleness_min'] >= 10.0 for q in r['queries'].values())",
                    "description": "no observation is ever fresher than the 10 minute latency allows",
                },
                {
                    "expression": "r['queries']['q25']['latest_acquisition_time_min'] <= 15.0",
                    "description": "the 20 and 25 minute acquisitions are not visible at t = 25",
                },
            ],
        },
        readme="""
# WG-BM-014 (D2) — Fixed 10-minute latency

## Scenario

The same 5-minute reporting sensor as WG-BM-013, but every acquisition takes
10 minutes to become usable: downlink, geolocation, cloud/smoke screening,
ingest.

```
available(t) = { records with t_acquisition + 10 <= t }
```

## Derivation

| Query time | Latest usable acquisition | Value | Contemporaneous truth | Error |
|---|---|---|---|---|
| 5 min | none (0 is available from 10) | `null` | 900 m | — |
| 25 min | 15 min | 700 m | 500 m | **+200 m** |
| 40 min | 30 min | 400 m | 200 m | **+200 m** |

At `t = 25` the acquisitions at 20 and 25 minutes exist in the archive and are
**not available**. A retrospective evaluation that loads the whole archive and
filters on `acquisition_time <= t` will use them, and will report a system that
is 200 m better informed than any real-time deployment can be.

Note the sign. The available observation always says the fire is *further away*
than it is, by `latency x rate of approach = 10 min x 20 m/min = 200 m`. Latency
does not add noise; it adds a systematic optimistic bias. Averaged over many
cases it does not cancel.

## What this catches

The mutation `observation_future_leak` sets the latency to zero while leaving
everything else intact — the one-character change of filtering on
`acquisition_time <= t` instead of `acquisition_time + latency <= t`. This
benchmark is its declared detector, and it is the reason the D family exists.

Leakage of this kind is not usually a deliberate choice. It appears when:

* an archive is joined on acquisition timestamp because that is the column that
  exists;
* a "latest observation" view is materialised without a validity interval;
* a nowcast product is back-filled into the archive under its valid time rather
  than its issue time.

Each of these produces a system that scores well offline and degrades
inexplicably in deployment.

## Expected

| Quantity | Value |
|---|---|
| latest usable acquisition at t = 25 | 15 min |
| value at t = 25 | 700 m |
| error against truth at t = 25 | +200 m |
| available records at t = 5 | 0 |
""",
    ))

    # ------------------------------------------------------------------ D3
    outage_records = [
        {"acquisition_time_min": float(t), "value": truth_value(t)}
        for t in list(range(0, 16, 5)) + list(range(45, 61, 5))
    ]
    written.append(write_benchmark(
        directory="benchmarks/observations/WG-BM-015_D3_sensor_outage",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-015",
            "label": "D3",
            "title": "A sensor outage stays missing and is never imputed or carried forward",
            "category": "observation",
            "difficulty": "adversarial",
            "purpose": "During a 30-minute outage the correct answer is 'unknown, last seen 30 "
                       "minutes ago', not zero and not the stale value presented as current.",
            "solver": "observation.availability",
            "assumptions": {
                "latency_min": 0,
                "max_staleness_min": 5,
                "stale_value_is_not_current_value": True,
                "missing_is_not_zero": True,
            },
            "expected_behavior": {
                "queries": {"q30": {"value": None, "staleness_min": 15.0, "stale": True}},
            },
            "tolerance": TOLERANCE,
            "exactness": "CLOSED_FORM",
            "detects": ["missing_treated_as_zero", "stale_data_presented_as_current"],
            "mutations_expected_to_fail": ["missing_as_zero", "silent_carry_forward"],
            "hand_checkable": True,
        },
        inputs={
            "observations": {
                "description": "Sensor reports every 5 minutes, then goes silent from 20 to 40 "
                               "minutes inclusive, then resumes at 45.",
                "max_staleness_min": 5.0,
                "truth": TRUTH,
                "sensors": [
                    {
                        "id": "s_intermittent",
                        "latency_min": 0.0,
                        "outage_min": [[20.0, 40.0]],
                        "records": outage_records,
                    }
                ],
                "queries": [
                    {"id": "q15", "sensor": "s_intermittent", "at_time_min": 15.0},
                    {"id": "q30", "sensor": "s_intermittent", "at_time_min": 30.0},
                    {"id": "q50", "sensor": "s_intermittent", "at_time_min": 50.0},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-015",
            "source": "hand_derivation",
            "derivation": (
                "Latency is zero and the declared freshness requirement is 5 minutes. "
                "At t = 15 the sensor is still reporting: the latest acquisition is 15, staleness "
                "0, value truth(15) = 700 m, current. "
                "At t = 30 the sensor has been silent since 15, so the latest acquisition is "
                "still 15 and staleness is 30 - 15 = 15 min, which exceeds the 5-minute "
                "requirement. The reported value is therefore null with status 'stale'; the last "
                "known value, 700 m, is retained separately so that a caller who explicitly wants "
                "it must ask for it. The contemporaneous truth is truth(30) = 400 m, so the stale "
                "value is 300 m optimistic. "
                "At t = 50 the sensor has resumed: latest acquisition 50, staleness 0, value "
                "truth(50) = 0 m, current."
            ),
            "results": {
                "queries": {
                    "q15": {
                        "latest_acquisition_time_min": 15.0,
                        "value": 700.0,
                        "staleness_min": 0.0,
                        "stale": False,
                        "status": "current",
                    },
                    "q30": {
                        "latest_acquisition_time_min": 15.0,
                        "value": None,
                        "last_known_value": 700.0,
                        "staleness_min": 15.0,
                        "stale": True,
                        "status": "stale",
                        "truth_value": 400.0,
                        "matches_truth": False,
                    },
                    "q50": {
                        "latest_acquisition_time_min": 50.0,
                        "value": 0.0,
                        "staleness_min": 0.0,
                        "stale": False,
                        "status": "current",
                    },
                },
            },
            "invariants": [
                {
                    "expression": "r['queries']['q30']['value'] is None and r['queries']['q30']['last_known_value'] == 700.0",
                    "description": "during the outage the current value is unknown but the last known value is retained",
                },
                {
                    "expression": "r['queries']['q30']['value'] != 0.0",
                    "description": "missing is not zero",
                },
            ],
        },
        readme="""
# WG-BM-015 (D3) — Sensor outage

## Scenario

A sensor reports every 5 minutes, goes silent between 20 and 40 minutes, and
resumes at 45. Latency is zero. The declared freshness requirement is 5 minutes:
an observation older than that is not a current observation.

## Derivation

| Query | Latest acquisition | Staleness | Reported value | Status |
|---|---|---|---|---|
| t = 15 | 15 | 0 min | 700 m | current |
| t = 30 | 15 | **15 min** | `null` | **stale** |
| t = 50 | 50 | 0 min | 0 m | current |

At `t = 30` the last known value, 700 m, is kept in a separate field. A caller
may ask for it, but must ask for it by name — it is never returned as if it were
a current reading. The contemporaneous truth at `t = 30` is 400 m, so the stale
value is **300 m optimistic**.

## Two failure modes, both detected here

**Imputation as zero.** `missing_as_zero` replaces the unknown with `0.0`. In
this scenario the quantity is distance from the fire front, so zero means *the
fire is here*. The imputed value is not merely wrong, it is the most alarming
possible value, and a system that panics on sensor outages is a system whose
alarms get switched off. (Reverse the variable — say, fuel moisture — and the
same bug becomes silently reassuring instead.) The general point is that the
numeric consequence of imputing zero depends on the variable's semantics, which
is exactly why the imputation cannot be done generically in a data layer.

**Silent carry-forward.** `silent_carry_forward` returns 700 m with
`stale: false`. This is the more dangerous bug, because the output is
*plausible*: it is a real measurement, it was correct 15 minutes ago, and
nothing downstream can distinguish it from a fresh one. Every consumer then
treats a 15-minute-old belief as current. Carrying a value forward is sometimes
the right operational choice; doing it without marking the staleness never is.

## Expected

| Quantity | Value |
|---|---|
| value at t = 30 | `null` |
| last known value at t = 30 | 700 m |
| staleness at t = 30 | 15 min |
| status at t = 30 | `stale` |
""",
    ))

    # ------------------------------------------------------------------ D4
    mnar_sensors = []
    for sensor_id, hazard in (("s1", 20.0), ("s2", 30.0), ("s3", 40.0), ("s4", 90.0), ("s5", 120.0)):
        last = int((hazard - 1) // 5) * 5
        mnar_sensors.append({
            "id": sensor_id,
            "latency_min": 0.0,
            "hazard_arrival_min": hazard,
            "records": [
                {"acquisition_time_min": float(t), "value": 0.0} for t in range(0, last + 1, 5)
            ],
        })
    written.append(write_benchmark(
        directory="benchmarks/observations/WG-BM-016_D4_fire_correlated_failure",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-016",
            "label": "D4",
            "title": "Sensors fail because the fire reaches them (missing not at random)",
            "category": "observation",
            "difficulty": "adversarial",
            "purpose": "Dropout is caused by the hazard, so averaging the surviving sensors "
                       "estimates the hazard at zero. Silence is evidence, not absence of "
                       "evidence.",
            "solver": "observation.availability",
            "assumptions": {
                "dropout_cause": "hazard arrival destroys the sensor",
                "missingness_mechanism": "MNAR",
                "burning_value": 1,
                "unburnt_value": 0,
            },
            "expected_behavior": {
                "mnar": {
                    "observed_mean": 0.0,
                    "true_mean": 0.6,
                    "missingness_informative": True,
                },
            },
            "tolerance": TOLERANCE,
            "exactness": "CLOSED_FORM",
            "detects": ["informative_missingness", "survivorship_bias"],
            "mutations_expected_to_fail": ["ignore_informative_missingness"],
            "hand_checkable": True,
        },
        inputs={
            "observations": {
                "description": "Five field sensors reporting burn state. Each stops reporting "
                               "exactly when the fire reaches it.",
                "max_staleness_min": 10.0,
                "sensors": mnar_sensors,
                "queries": [
                    {"id": "q_s1_at_60", "sensor": "s1", "at_time_min": 60.0},
                    {"id": "q_s5_at_60", "sensor": "s5", "at_time_min": 60.0},
                ],
                "mnar_query": {
                    "at_time_min": 60.0,
                    "burning_value": 1.0,
                    "unburnt_value": 0.0,
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-016",
            "source": "hand_derivation",
            "derivation": (
                "Fire reaches s1 at 20, s2 at 30, s3 at 40, s4 at 90 and s5 at 120 minutes, and "
                "each sensor is destroyed on arrival. At t = 60 the silent sensors are s1, s2 and "
                "s3 and the reporting ones are s4 and s5. Every reporting sensor reports 0 "
                "(unburnt), so the mean over reporting sensors is 0.0. The true fraction burnt is "
                "3/5 = 0.6, so the naive estimate is biased by -0.6: it is the maximum possible "
                "error, and it is achieved with data that contain no contradictory value at all. "
                "An estimator that treats 'silent after hazard arrival' as evidence of burning "
                "recovers (3 * 1 + 2 * 0)/5 = 0.6 exactly. Individually, s1's last record is at "
                "15 minutes (the last 5-minute slot before its hazard arrival at 20), so at t = 60 "
                "it is 45 minutes stale and its current value is unknown."
            ),
            "results": {
                "mnar": {
                    "at_time_min": 60.0,
                    "reporting_sensors": ["s4", "s5"],
                    "silent_sensors": ["s1", "s2", "s3"],
                    "observed_mean": 0.0,
                    "true_mean": 0.6,
                    "naive_bias": -0.6,
                    "dropout_aware_mean": 0.6,
                    "dropout_aware_bias": 0.0,
                    "missingness_informative": True,
                },
                "queries": {
                    "q_s1_at_60": {
                        "latest_acquisition_time_min": 15.0,
                        "value": None,
                        "staleness_min": 45.0,
                        "stale": True,
                        "status": "stale",
                    },
                    "q_s5_at_60": {
                        "latest_acquisition_time_min": 60.0,
                        "value": 0.0,
                        "staleness_min": 0.0,
                        "stale": False,
                        "status": "current",
                    },
                },
            },
            "invariants": [
                {
                    "expression": "r['mnar']['observed_mean'] < r['mnar']['true_mean']",
                    "description": "the complete-case estimate understates the hazard",
                },
                {
                    "expression": "abs(r['mnar']['dropout_aware_bias']) < 1e-12",
                    "description": "treating dropout as evidence recovers the truth exactly here",
                },
            ],
        },
        readme="""
# WG-BM-016 (D4) — Fire-correlated sensor failure

## Scenario

Five field sensors report burn state (`0` unburnt, `1` burning). Each is
destroyed at the moment the fire reaches it:

| Sensor | Fire arrives |
|---|---|
| s1 | 20 min |
| s2 | 30 min |
| s3 | 40 min |
| s4 | 90 min |
| s5 | 120 min |

The question is asked at **t = 60 min**.

## Derivation

At `t = 60`, sensors s1, s2 and s3 are silent and s4, s5 are reporting. Every
sensor that is still reporting reports `0`, because a sensor that could report
`1` has already been destroyed. Therefore:

```
mean over reporting sensors  = (0 + 0) / 2            = 0.0
true fraction burnt          = 3 / 5                  = 0.6
naive bias                   = 0.0 - 0.6              = -0.6
```

The complete-case estimate is **maximally wrong**, and it is wrong using data
that contain no contradictory observation whatsoever. There is nothing in the
reporting record to notice.

An estimator that treats *silence after the modelled hazard arrival* as evidence
of burning recovers the truth exactly:

```
(3 * 1 + 2 * 0) / 5 = 0.6
```

## Why this is the MNAR case and not a nuisance

Missingness here is caused by the variable being measured. That is the textbook
definition of **missing not at random**, and it has three consequences that a
wildfire system must handle explicitly:

1. **No imputation from observed data can fix it.** Mean imputation, regression
   imputation and multiple imputation all condition on the observed
   distribution, which contains no burning sensors. Every one of them imputes
   towards zero.
2. **The bias grows as the situation worsens.** The more of the area that burns,
   the more sensors are destroyed and the more confidently the surviving network
   reports calm. The estimator is least reliable exactly when it matters most.
3. **Silence is a measurement.** The dropout pattern carries the information the
   destroyed sensors would have reported. Discarding "sensors with no data"
   discards the signal.

The mutation `ignore_informative_missingness` performs the complete-case
analysis and reports it as the answer; this benchmark is its declared detector.

## A caveat on the correction

The dropout-aware estimate here is exact *because the scenario stipulates that
dropout is caused by hazard arrival and by nothing else*. Real sensor networks
also lose nodes to battery failure, communications outage and vandalism. The
correct general treatment is a model of the dropout mechanism, not the
substitution used here. This benchmark pins the sign and the magnitude of the
naive error; it does not endorse a universal correction, and that limitation is
recorded in `reports/KNOWN_GAPS.md`.
""",
    ))

    # ------------------------------------------------------------------ D5
    written.append(write_benchmark(
        directory="benchmarks/observations/WG-BM-017_D5_false_negative",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-017",
            "label": "D5",
            "title": "A false negative: fire exists, the detector reports nothing",
            "category": "observation",
            "difficulty": "adversarial",
            "purpose": "Absence of detection is not detection of absence. The route chosen by "
                       "trusting a non-detection through an unreliable detector is fatal; the "
                       "precautionary route costs 5.",
            "solver": "observation.availability",
            "assumptions": {
                "detector_reliability_is_known": True,
                "non_detection_over_unreliable_cell": "unknown, not clear",
                "loss_units": "arbitrary but consistent",
            },
            "expected_behavior": {
                "detection": {
                    "route_trusting_detections": "route_south",
                    "route_precautionary": "route_north",
                    "regret_of_trusting": 95.0,
                },
            },
            "tolerance": TOLERANCE,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["false_negative_treated_as_negative", "unverified_clear_claim"],
            "mutations_expected_to_fail": ["assume_missing_is_safe"],
            "hand_checkable": True,
        },
        inputs={
            "observations": {
                "description": "Two candidate corridors. The northern cell was overflown five "
                               "minutes ago and is confirmed clear. The southern cell is under "
                               "thick smoke: the detector returned nothing, and its detection "
                               "probability there is known to be poor. There is in fact fire in "
                               "the southern cell.",
                "sensors": [],
                "detection_query": {
                    "cells": [
                        {
                            "id": "c_north",
                            "true_fire": False,
                            "detected": False,
                            "detection_reliable": True,
                            "note": "clear-air overflight five minutes ago",
                        },
                        {
                            "id": "c_south",
                            "true_fire": True,
                            "detected": False,
                            "detection_reliable": False,
                            "note": "smoke-obscured; detector sensitivity unknown",
                        },
                    ],
                    "routes": [
                        {
                            "id": "route_north",
                            "cells": ["c_north"],
                            "loss_if_clear": 5.0,
                            "loss_if_hazardous": 100.0,
                        },
                        {
                            "id": "route_south",
                            "cells": ["c_south"],
                            "loss_if_clear": 0.0,
                            "loss_if_hazardous": 100.0,
                        },
                    ],
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-017",
            "source": "exhaustive_enumeration",
            "derivation": (
                "Under the rule 'no detection means no fire', both cells look clear, so "
                "route_south is chosen for its believed loss of 0 against route_north's 5. In "
                "truth c_south is on fire, so the realised loss of route_south is 100. "
                "Under the rule 'a non-detection is informative only where the detector is "
                "reliable', c_north is clear (loss 5) and c_south is unknown, hence treated as "
                "possibly hazardous (believed loss 100); route_north is chosen and its realised "
                "loss is 5, because c_north really is clear. The regret of trusting the "
                "unreliable non-detection is 100 - 5 = 95."
            ),
            "results": {
                "detection": {
                    "true_fire_cells": ["c_south"],
                    "detected_cells": [],
                    "false_negative_cells": ["c_south"],
                    "reliably_clear_cells": ["c_north"],
                    "false_negative_present": True,
                    "route_trusting_detections": "route_south",
                    "loss_trusting_detections": 100.0,
                    "route_precautionary": "route_north",
                    "loss_precautionary": 5.0,
                    "regret_of_trusting": 95.0,
                },
            },
            "invariants": [
                {
                    "expression": "r['detection']['loss_trusting_detections'] > r['detection']['loss_precautionary']",
                    "description": "trusting the unreliable non-detection is strictly worse",
                },
                {
                    "expression": "r['detection']['detected_cells'] == []",
                    "description": "no detection anywhere: the difference comes entirely from reliability",
                },
            ],
        },
        readme="""
# WG-BM-017 (D5) — False negative

## Scenario

Two candidate corridors, one cell each.

| Cell | Truth | Detector output | Detector reliable here? |
|---|---|---|---|
| `c_north` | no fire | no detection | **yes** — clear-air overflight 5 min ago |
| `c_south` | **fire** | no detection | **no** — thick smoke, sensitivity unknown |

Losses: the northern corridor is longer, costing 5 if clear. The southern
corridor is direct, costing 0 if clear. Either costs 100 if it runs through
fire.

**Both cells return "no detection".** The entire difference between the two
decisions comes from whether that non-detection carries information.

## Derivation

**Rule A — no detection means no fire.**

```
believed loss(route_north) = 5     believed loss(route_south) = 0
choose route_south
realised loss = 100                (c_south is on fire)
```

**Rule B — a non-detection is informative only where the detector is reliable.**

```
c_north: reliably clear          -> believed loss(route_north) = 5
c_south: unknown, treat as hazard-> believed loss(route_south) = 100
choose route_north
realised loss = 5                 (c_north really is clear)
```

**Regret of Rule A = 100 - 5 = 95.**

## The distinction this benchmark forces

Rule B is not "assume the worst everywhere". If it were, the northern corridor
would also be treated as hazardous and the system would be paralysed — which is
its own failure mode, and the reason `c_north` is in the scenario at all. Rule B
uses the non-detection at `c_north` and declines to use the one at `c_south`,
because the two observations have different evidential weight despite being the
same value.

That distinction requires the detector's per-cell reliability to be carried
alongside the detection, which many pipelines discard early: a detection product
is reduced to a boolean raster, the smoke/cloud mask is dropped, and by the time
the router sees the data a confirmed clear cell and an unobservable cell are
byte-identical.

The mutation `assume_missing_is_safe` erases that distinction and this benchmark
is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| false negative present | `true` |
| route under Rule A | `route_south`, realised loss 100 |
| route under Rule B | `route_north`, realised loss 5 |
| regret of trusting non-detection | 95 |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
