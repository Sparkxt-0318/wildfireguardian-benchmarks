"""Author the G family: forecast-value benchmarks (WG-BM-028..033)."""

from __future__ import annotations

from common import report, write_benchmark

SCRIPT = "author_forecast_value.py"
TOLERANCE = {"default": 1.0e-09}


def main() -> None:
    written = []

    # ------------------------------------------------------------------ G1
    written.append(write_benchmark(
        directory="benchmarks/forecast_value/WG-BM-028_G1_error_without_decision_impact",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-028",
            "label": "G1",
            "title": "A 500 m forecast error that changes no decision and costs nothing",
            "category": "forecast_value",
            "difficulty": "basic",
            "purpose": "Degrading forecast accuracy from 0 m to 500 m leaves every action and "
                       "every loss unchanged, because the error does not cross the decision "
                       "boundary. Skill fell; value did not.",
            "solver": "decision.value_of_information",
            "assumptions": {
                "decision_boundary_at_m": 2000,
                "loss_units": "arbitrary but consistent",
                "signals_deterministic": True,
                "both_forecasts_timely": True,
            },
            "expected_behavior": {
                "skill_and_value_agree": False,
                "evpi": 6.3,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["skill_value_conflation", "accuracy_treated_as_the_objective"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "This benchmark documents the skill/value conflation but deliberately does "
                     "not claim to detect it: with the two forecasts equally valuable, a "
                     "skill-based recommendation picks an equally good policy and does no harm. "
                     "Detection happens in WG-BM-031 and WG-BM-033, where the rankings differ in "
                     "consequence and not only in justification.",
        },
        inputs={
            "decision": {
                "description": "Choose the valley road or the ridge road. The valley road is "
                               "quick but unusable if the front comes within 2 km. Two forecasts "
                               "are available, one exact and one displaced by 500 m; both put the "
                               "front on the correct side of the 2 km boundary in both scenarios.",
                "scenarios": [
                    {"id": "s_far", "probability": 0.9, "note": "front stays beyond 2 km"},
                    {"id": "s_near", "probability": 0.1, "note": "front comes inside 2 km"},
                ],
                "actions": ["route_valley", "route_ridge"],
                "loss": {
                    "route_valley": {"s_far": 1.0, "s_near": 100.0},
                    "route_ridge": {"s_far": 8.0, "s_near": 8.0},
                },
                "decision_deadline_min": 20.0,
                "default_action": "route_ridge",
                "truth_scenario": "s_far",
                "information_sources": [
                    {
                        "id": "forecast_exact",
                        "available_at_min": 5.0,
                        "signal": {"s_far": "far", "s_near": "near"},
                        "skill_score": 1.0,
                        "spatial_error_m": 0.0,
                    },
                    {
                        "id": "forecast_displaced",
                        "available_at_min": 5.0,
                        "signal": {"s_far": "far", "s_near": "near"},
                        "skill_score": 0.6,
                        "spatial_error_m": 500.0,
                    },
                ],
                "policies": [
                    {"id": "baseline_ridge", "type": "fixed", "action": "route_ridge"},
                    {"id": "forecast_aware_exact", "type": "informed", "source": "forecast_exact"},
                    {"id": "forecast_aware_displaced", "type": "informed", "source": "forecast_displaced"},
                ],
                "baseline_policy": "baseline_ridge",
            }
        },
        expected={
            "benchmark_id": "WG-BM-028",
            "source": "hand_derivation",
            "derivation": (
                "Both forecasts place the front on the correct side of the 2 km decision "
                "boundary in both scenarios, so both produce the same signal map and therefore "
                "the same actions: take the valley on 'far' (loss 1 beats 8) and the ridge on "
                "'near' (loss 8 beats 100). Each forecast-aware policy has expected loss "
                "0.9 * 1 + 0.1 * 8 = 1.7 against the baseline's 8, so each is worth "
                "8 - 1.7 = 6.3. The clairvoyant expected loss is also 1.7, so EVPI = 6.3 and both "
                "forecasts capture all of it. The exact forecast scores 1.0 on skill and the "
                "displaced one 0.6, yet their decision value is identical to the last decimal: "
                "the ranking by skill and the ranking by value disagree. In the realised scenario "
                "s_far both forecast policies lose 1 against the baseline's 8."
            ),
            "results": {
                "truth_scenario": "s_far",
                "baseline_policy": "baseline_ridge",
                "expected_loss_by_policy": {
                    "baseline_ridge": 8.0,
                    "forecast_aware_exact": 1.7,
                    "forecast_aware_displaced": 1.7,
                },
                "value_by_policy": {
                    "baseline_ridge": 0.0,
                    "forecast_aware_exact": 6.3,
                    "forecast_aware_displaced": 6.3,
                },
                "realised_loss_by_policy": {
                    "baseline_ridge": 8.0,
                    "forecast_aware_exact": 1.0,
                    "forecast_aware_displaced": 1.0,
                },
                "clairvoyant_expected_loss": 1.7,
                "best_fixed_action": "route_ridge",
                "best_fixed_expected_loss": 8.0,
                "evpi": 6.3,
                "realizable_value_of_information": 6.3,
                "timely_information_sources": ["forecast_displaced", "forecast_exact"],
                "late_information_sources": [],
                "ranked_by_skill": [
                    "forecast_aware_exact",
                    "forecast_aware_displaced",
                    "baseline_ridge",
                ],
                "skill_and_value_agree": False,
            },
            "invariants": [
                {
                    "expression": "abs(r['value_by_policy']['forecast_aware_exact'] - r['value_by_policy']['forecast_aware_displaced']) < 1e-12",
                    "description": "a 500 m degradation in accuracy changes the decision value by exactly zero",
                },
                {
                    "expression": "r['policies']['forecast_aware_exact']['action_by_scenario'] == r['policies']['forecast_aware_displaced']['action_by_scenario']",
                    "description": "both forecasts drive identical actions in every scenario",
                },
            ],
        },
        readme="""
# WG-BM-028 (G1) — Forecast error with no decision impact

## Scenario

A community chooses between the valley road (fast, but unusable if the front
comes within 2 km) and the ridge road (slow, always usable).

| | front stays far (p = 0.9) | front comes near (p = 0.1) |
|---|---|---|
| `route_valley` | 1 | 100 |
| `route_ridge` | 8 | 8 |

Two forecasts are available before the 20-minute decision deadline:

| Forecast | Spatial error | Skill score |
|---|---|---|
| `forecast_exact` | 0 m | 1.00 |
| `forecast_displaced` | 500 m | 0.60 |

The decision boundary is at **2 km**. Both forecasts put the front on the
correct side of it in both scenarios.

## Derivation

Because both forecasts classify both scenarios correctly, both produce the same
actions: valley on "far" (1 beats 8), ridge on "near" (8 beats 100).

```
expected loss, either forecast policy = 0.9 * 1 + 0.1 * 8 = 1.7
expected loss, baseline (always ridge) = 8
value of either forecast                = 8 - 1.7 = 6.3
clairvoyant expected loss               = 1.7
EVPI                                    = 8 - 1.7 = 6.3
```

Both forecasts capture the **entire** value of perfect information. Their
decision value is identical to the last decimal, while their skill scores differ
by 40 points.

## The lesson

Forecast accuracy is a property of the forecast. Decision value is a property of
the *pair* (forecast, decision). A 500 m error matters enormously when the
decision boundary is 500 m away (see WG-BM-029, where a 20 m error costs 92) and
not at all when the boundary is 2 km away, as here.

The practical consequence: **a forecast improvement programme cannot be
evaluated on forecast metrics alone.** Reducing mean position error from 500 m
to 0 m is a genuine scientific achievement and, in this decision, is worth
nothing. Resources spent on it were resources not spent on the decisions where
the boundary is tight.

## What this benchmark does not claim

It does **not** detect the `skill_implies_value` mutation. Ranking by skill here
recommends `forecast_aware_exact` over `forecast_aware_displaced`, and since the
two are worth exactly the same, that recommendation is harmless: the conflation
is visible in the reasoning and absent from the outcome. Benchmarks whose
declared answer would not change under a bug must not claim to catch it, so the
`mutations_expected_to_fail` list here is empty. WG-BM-031 and WG-BM-033 are
where the conflation changes what actually happens.

## Expected

| Quantity | Value |
|---|---|
| value of the exact forecast | 6.3 |
| value of the 500 m-displaced forecast | **6.3** |
| EVPI | 6.3 |
| skill ranking agrees with value ranking | `false` |
""",
    ))

    # ------------------------------------------------------------------ G2
    written.append(write_benchmark(
        directory="benchmarks/forecast_value/WG-BM-029_G2_tiny_error_large_impact",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-029",
            "label": "G2",
            "title": "A 20 m forecast error on a decision boundary costs 92",
            "category": "forecast_value",
            "difficulty": "adversarial",
            "purpose": "The mirror image of WG-BM-028: an error 25 times smaller, sitting on the "
                       "decision boundary, flips the route choice and produces a realised regret "
                       "of 92.",
            "solver": "decision.value_of_information",
            "assumptions": {
                "decision_boundary_at_m": 1000,
                "forecast_taken_at_face_value": True,
                "signals_deterministic": True,
            },
            "expected_behavior": {
                "realised_regret_by_policy": {"forecast_aware": 92.0},
                "value_by_policy": {"forecast_aware": -42.5},
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["skill_value_conflation", "decision_boundary_sensitivity"],
            "mutations_expected_to_fail": ["skill_implies_value"],
            "hand_checkable": True,
        },
        inputs={
            "decision": {
                "description": "The front is 990 m from the valley road; the road is unusable "
                               "inside 1000 m. The forecast puts it at 1010 m - a 20 m error, on "
                               "the wrong side of the boundary - so it reports the valley road as "
                               "usable in both scenarios.",
                "scenarios": [
                    {"id": "s_near", "probability": 0.5, "note": "front at 990 m: valley unusable"},
                    {"id": "s_far", "probability": 0.5, "note": "front well beyond 1 km"},
                ],
                "actions": ["route_valley", "route_ridge"],
                "loss": {
                    "route_valley": {"s_far": 1.0, "s_near": 100.0},
                    "route_ridge": {"s_far": 8.0, "s_near": 8.0},
                },
                "decision_deadline_min": 20.0,
                "default_action": "route_ridge",
                "truth_scenario": "s_near",
                "information_sources": [
                    {
                        "id": "forecast_20m",
                        "available_at_min": 5.0,
                        "signal": {"s_near": "clear", "s_far": "clear"},
                        "skill_score": 0.98,
                        "spatial_error_m": 20.0,
                    }
                ],
                "policies": [
                    {"id": "baseline_ridge", "type": "fixed", "action": "route_ridge"},
                    {
                        "id": "forecast_aware",
                        "type": "signal_map",
                        "source": "forecast_20m",
                        "map": {"clear": "route_valley"},
                    },
                ],
                "baseline_policy": "baseline_ridge",
            }
        },
        expected={
            "benchmark_id": "WG-BM-029",
            "source": "hand_derivation",
            "derivation": (
                "The forecast is 20 m in error and that error lands on the wrong side of the "
                "1000 m decision boundary, so it reports 'clear' in both scenarios and the "
                "forecast-aware policy takes the valley road in both. Its expected loss is "
                "0.5 * 1 + 0.5 * 100 = 50.5 against the baseline's 8, so the forecast is worth "
                "8 - 50.5 = -42.5: strongly negative. In the realised scenario s_near the valley "
                "road costs 100 while the best available action, the ridge road, costs 8, so the "
                "realised regret is 92. For comparison the clairvoyant expected loss is "
                "0.5 * 1 + 0.5 * 8 = 4.5 and EVPI is 8 - 4.5 = 3.5, so a forecast that resolved "
                "this boundary correctly would have been worth 3.5; the one that missed it by "
                "20 m is worth -42.5."
            ),
            "results": {
                "truth_scenario": "s_near",
                "expected_loss_by_policy": {"baseline_ridge": 8.0, "forecast_aware": 50.5},
                "value_by_policy": {"baseline_ridge": 0.0, "forecast_aware": -42.5},
                "realised_loss_by_policy": {"baseline_ridge": 8.0, "forecast_aware": 100.0},
                "realised_regret_by_policy": {"baseline_ridge": 0.0, "forecast_aware": 92.0},
                "best_loss_in_truth_scenario": 8.0,
                "clairvoyant_expected_loss": 4.5,
                "best_fixed_action": "route_ridge",
                "evpi": 3.5,
                "realizable_value_of_information": -42.5,
                "recommended_policy": "baseline_ridge",
                "skill_and_value_agree": False,
                "action_in_truth_by_policy": {
                    "baseline_ridge": "route_ridge",
                    "forecast_aware": "route_valley",
                },
            },
            "invariants": [
                {
                    "expression": "r['value_by_policy']['forecast_aware'] < 0",
                    "description": "a 0.98-skill forecast has negative decision value here",
                },
                {
                    "expression": "r['realised_regret_by_policy']['forecast_aware'] == 92.0",
                    "description": "a 20 m error produces a realised regret of 92",
                },
            ],
        },
        readme="""
# WG-BM-029 (G2) — Tiny error, large decision impact

## Scenario

The valley road is unusable if the front is within **1000 m**. In the realised
world the front is at **990 m** — inside the boundary. The forecast puts it at
**1010 m**: an error of **20 metres**, on the wrong side.

| | front near, 990 m (p = 0.5) | front far (p = 0.5) |
|---|---|---|
| `route_valley` | 100 | 1 |
| `route_ridge` | 8 | 8 |

The forecast is taken at face value: "clear" means take the valley road.

## Derivation

The forecast reports "clear" in **both** scenarios, so the forecast-aware policy
takes the valley road in both.

```
expected loss, forecast-aware = 0.5 * 1 + 0.5 * 100 = 50.5
expected loss, baseline       = 8
value of the forecast         = 8 - 50.5 = -42.5
```

In the realised world (`s_near`) the valley road costs **100** while the best
available action costs **8**:

```
realised regret = 100 - 8 = 92
```

For contrast, a forecast that resolved this boundary correctly would have been
worth `EVPI = 8 - 4.5 = 3.5`.

## Read this next to WG-BM-028

| | WG-BM-028 (G1) | WG-BM-029 (G2) |
|---|---|---|
| spatial error | 500 m | **20 m** |
| skill score | 0.60 | **0.98** |
| distance to decision boundary | 2000 m | **10 m** |
| decision value | **+6.3** | **-42.5** |
| realised regret | 0 | **92** |

The forecast with 25 times less error and a far better skill score is the one
that causes the catastrophe. Error magnitude carries no information about
decision impact on its own; what matters is the error *relative to the distance
to the nearest decision boundary*.

## What follows for evaluation practice

* Aggregate skill scores cannot rank forecasts for a decision. A mean absolute
  error averaged over a domain is dominated by the majority of locations where
  no decision boundary is nearby.
* Forecast evaluation should be **stratified by proximity to a decision
  boundary**, and the cases that matter are precisely the rare ones where the
  forecast is nearly right.
* A well-calibrated *probabilistic* forecast would have helped here, not by
  being more accurate, but by reporting that the front position was within its
  own uncertainty of the boundary. A deterministic 1010 m cannot express that;
  "1010 m, sigma 300 m" can. This suite does not yet contain a benchmark for
  calibration under boundary proximity, and that gap is recorded in
  `reports/KNOWN_GAPS.md`.
""",
    ))

    # ------------------------------------------------------------------ G3
    written.append(write_benchmark(
        directory="benchmarks/forecast_value/WG-BM-030_G3_accurate_but_late",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-030",
            "label": "G3",
            "title": "An almost-perfect forecast that arrives after the last useful decision time",
            "category": "forecast_value",
            "difficulty": "adversarial",
            "purpose": "Skill 0.98, spatial error 10 m, issued at minute 30 for a decision that "
                       "must be made by minute 20. Decision value is negative, not merely zero, "
                       "because waiting for it forfeits the action.",
            "solver": "decision.value_of_information",
            "assumptions": {
                "decision_deadline_min": 20,
                "forecast_issue_time_min": 30,
                "waiting_forfeits_the_action": True,
                "no_partial_early_release": True,
            },
            "expected_behavior": {
                "evpi": 5.0,
                "realizable_value_of_information": 0.0,
                "value_by_policy": {"wait_for_forecast": -40.0},
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["timeliness_ignored", "skill_value_conflation"],
            "mutations_expected_to_fail": ["forecast_always_trusted"],
            "hand_checkable": True,
            "notes": "Conceptually the most important benchmark in the G family.",
        },
        inputs={
            "decision": {
                "description": "Evacuate now at a known cost, or shelter in place. An excellent "
                               "forecast exists but is issued at minute 30, ten minutes after the "
                               "last time an evacuation could be started.",
                "scenarios": [
                    {"id": "s_hit", "probability": 0.5},
                    {"id": "s_miss", "probability": 0.5},
                ],
                "actions": ["evacuate", "shelter_in_place"],
                "loss": {
                    "evacuate": {"s_hit": 10.0, "s_miss": 10.0},
                    "shelter_in_place": {"s_hit": 100.0, "s_miss": 0.0},
                },
                "decision_deadline_min": 20.0,
                "default_action": "shelter_in_place",
                "truth_scenario": "s_hit",
                "information_sources": [
                    {
                        "id": "forecast_accurate_late",
                        "available_at_min": 30.0,
                        "signal": {"s_hit": "hit", "s_miss": "miss"},
                        "skill_score": 0.98,
                        "spatial_error_m": 10.0,
                    }
                ],
                "policies": [
                    {"id": "baseline_trigger", "type": "fixed", "action": "evacuate"},
                    {
                        "id": "wait_for_forecast",
                        "type": "informed",
                        "source": "forecast_accurate_late",
                        "fallback_action": "shelter_in_place",
                    },
                ],
                "baseline_policy": "baseline_trigger",
            }
        },
        expected={
            "benchmark_id": "WG-BM-030",
            "source": "hand_derivation",
            "derivation": (
                "The forecast becomes available at minute 30 and the decision must be taken by "
                "minute 20, so it cannot influence the action at all. A policy that waits for it "
                "has, by minute 20, taken no evacuation decision, which is the shelter-in-place "
                "outcome; its expected loss is 0.5 * 100 + 0.5 * 0 = 50 against the baseline "
                "trigger's 10, so its value is 10 - 50 = -40. In the realised scenario s_hit it "
                "loses 100 against the baseline's 10, a realised value of -90 and a realised "
                "regret of 90. "
                "The information itself is genuinely valuable: the clairvoyant expected loss is "
                "0.5 * 10 + 0.5 * 0 = 5 against the best fixed action's 10, so EVPI = 5. None of "
                "it is realisable here, because no timely policy can use it: "
                "realizable_value_of_information = 0. High skill, positive EVPI, zero realisable "
                "value and negative realised value, all at once."
            ),
            "results": {
                "truth_scenario": "s_hit",
                "expected_loss_by_policy": {"baseline_trigger": 10.0, "wait_for_forecast": 50.0},
                "value_by_policy": {"baseline_trigger": 0.0, "wait_for_forecast": -40.0},
                "realised_loss_by_policy": {"baseline_trigger": 10.0, "wait_for_forecast": 100.0},
                "realised_value_by_policy": {"baseline_trigger": 0.0, "wait_for_forecast": -90.0},
                "realised_regret_by_policy": {"baseline_trigger": 0.0, "wait_for_forecast": 90.0},
                "timely_information_sources": [],
                "late_information_sources": ["forecast_accurate_late"],
                "clairvoyant_expected_loss": 5.0,
                "best_fixed_action": "evacuate",
                "best_fixed_expected_loss": 10.0,
                "evpi": 5.0,
                "realizable_value_of_information": 0.0,
                "recommended_policy": "baseline_trigger",
            },
            "invariants": [
                {
                    "expression": "r['evpi'] > 0 and r['realizable_value_of_information'] == 0.0",
                    "description": "the information is valuable in principle and worthless in practice",
                },
                {
                    "expression": "r['policies']['wait_for_forecast']['information_timely'] is False",
                    "description": "the forecast is explicitly marked untimely",
                },
            ],
        },
        readme="""
# WG-BM-030 (G3) — Accurate but late

## Scenario

Evacuate now at a fixed cost of 10, or shelter in place: free if the fire misses,
catastrophic (100) if it hits. Prior 50/50.

An **excellent** forecast exists — skill score 0.98, spatial error 10 m — and it
is issued at **minute 30**. The decision must be taken by **minute 20**: after
that there is no longer time to move people.

## Derivation

The forecast cannot influence the action. A policy that waits for it has, at the
deadline, not started an evacuation — which is the shelter-in-place outcome.

```
expected loss, baseline trigger (always evacuate) = 10
expected loss, wait-for-forecast                  = 0.5 * 100 + 0.5 * 0 = 50
value of waiting for the forecast                 = 10 - 50 = -40
```

In the realised world the fire hits:

```
realised loss, baseline          = 10
realised loss, wait-for-forecast = 100
realised regret                  = 90
```

And yet the information is genuinely valuable in the abstract:

```
clairvoyant expected loss = 0.5 * 10 + 0.5 * 0 = 5
best fixed action         = evacuate, expected loss 10
EVPI                      = 5
realisable value          = 0      <- no timely policy can use it
```

## Four numbers that must be reported separately

| Quantity | Value | Meaning |
|---|---|---|
| skill score | 0.98 | the forecast is excellent |
| EVPI | 5 | knowing the outcome would be worth 5 |
| realisable value of information | **0** | nothing can be extracted by the deadline |
| realised value of waiting | **-90** | waiting for it was actively harmful |

A system that reports only the first number will conclude that the forecasting
programme is succeeding. A system that reports only EVPI will conclude that more
information is worth buying. Only the third and fourth numbers describe what
happens to the people in the scenario.

## Why this is the conceptually critical case

Forecast lead time is usually treated as a performance attribute — nice to have,
traded against accuracy. This benchmark makes it a **feasibility constraint**. A
forecast issued after the last useful decision time has exactly zero realisable
value regardless of its accuracy, and a decision process that is built around
waiting for it is strictly worse than one that acts on the prior.

The corollary is the design rule the F family keeps running into: the quantity
to optimise is not forecast accuracy at a fixed lead time, but accuracy
*conditional on being available before the decision deadline*. Those two
objectives can point in opposite directions, and WG-BM-031 shows them doing so.

The `forecast_always_trusted` mutation removes the timeliness check; the late
forecast is then applied to the decision, the value of waiting becomes +5, and
the benchmark fails. It is this benchmark's declared detector.
""",
    ))

    # ------------------------------------------------------------------ G4
    written.append(write_benchmark(
        directory="benchmarks/forecast_value/WG-BM-031_G4_crude_but_timely",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-031",
            "label": "G4",
            "title": "A crude, timely forecast beats an excellent, late one",
            "category": "forecast_value",
            "difficulty": "adversarial",
            "purpose": "Two forecasts in one decision: skill 0.98 at minute 30 and skill 0.40 at "
                       "minute 5, against a deadline of minute 20. The ranking by skill is the "
                       "reverse of the ranking by value.",
            "solver": "decision.value_of_information",
            "assumptions": {
                "decision_deadline_min": 20,
                "crude_forecast_resolves_the_binary_question": True,
                "accurate_forecast_arrives_late": True,
            },
            "expected_behavior": {
                "ranked_by_value": ["use_crude_early", "baseline_trigger", "use_accurate_late"],
                "skill_and_value_agree": False,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["skill_value_conflation", "timeliness_ignored"],
            "mutations_expected_to_fail": ["skill_implies_value", "forecast_always_trusted"],
            "hand_checkable": True,
        },
        inputs={
            "decision": {
                "description": "The WG-BM-030 decision with a second, much cruder forecast that "
                               "is available 15 minutes before the deadline. It is 800 m out on "
                               "the front position but it gets the binary question - does the "
                               "fire reach the town - right.",
                "scenarios": [
                    {"id": "s_hit", "probability": 0.5},
                    {"id": "s_miss", "probability": 0.5},
                ],
                "actions": ["evacuate", "shelter_in_place"],
                "loss": {
                    "evacuate": {"s_hit": 10.0, "s_miss": 10.0},
                    "shelter_in_place": {"s_hit": 100.0, "s_miss": 0.0},
                },
                "decision_deadline_min": 20.0,
                "default_action": "shelter_in_place",
                "truth_scenario": "s_hit",
                "information_sources": [
                    {
                        "id": "forecast_accurate_late",
                        "available_at_min": 30.0,
                        "signal": {"s_hit": "hit", "s_miss": "miss"},
                        "skill_score": 0.98,
                        "spatial_error_m": 10.0,
                    },
                    {
                        "id": "forecast_crude_early",
                        "available_at_min": 5.0,
                        "signal": {"s_hit": "hit", "s_miss": "miss"},
                        "skill_score": 0.4,
                        "spatial_error_m": 800.0,
                    },
                ],
                "policies": [
                    {"id": "baseline_trigger", "type": "fixed", "action": "evacuate"},
                    {
                        "id": "use_accurate_late",
                        "type": "informed",
                        "source": "forecast_accurate_late",
                        "fallback_action": "shelter_in_place",
                    },
                    {
                        "id": "use_crude_early",
                        "type": "informed",
                        "source": "forecast_crude_early",
                    },
                ],
                "baseline_policy": "baseline_trigger",
            }
        },
        expected={
            "benchmark_id": "WG-BM-031",
            "source": "hand_derivation",
            "derivation": (
                "The crude forecast is available at minute 5, inside the deadline, and although "
                "it is 800 m out on the front position it separates the two scenarios. Acting on "
                "it gives evacuate on 'hit' (10 beats 100) and shelter on 'miss' (0 beats 10), so "
                "its expected loss is 0.5 * 10 + 0.5 * 0 = 5 against the baseline's 10: a value "
                "of +5, which equals EVPI, so the crude forecast captures all the value there is. "
                "The accurate forecast arrives at minute 30, ten minutes late, so the policy that "
                "waits for it shelters by default and has expected loss 50, a value of -40. "
                "Ranked by value: crude (+5), baseline (0), accurate (-40). Ranked by skill: "
                "accurate (0.98), crude (0.40), baseline (none). The two rankings are reversed."
            ),
            "results": {
                "truth_scenario": "s_hit",
                "expected_loss_by_policy": {
                    "baseline_trigger": 10.0,
                    "use_accurate_late": 50.0,
                    "use_crude_early": 5.0,
                },
                "value_by_policy": {
                    "baseline_trigger": 0.0,
                    "use_accurate_late": -40.0,
                    "use_crude_early": 5.0,
                },
                "realised_loss_by_policy": {
                    "baseline_trigger": 10.0,
                    "use_accurate_late": 100.0,
                    "use_crude_early": 10.0,
                },
                "timely_information_sources": ["forecast_crude_early"],
                "late_information_sources": ["forecast_accurate_late"],
                "clairvoyant_expected_loss": 5.0,
                "evpi": 5.0,
                "realizable_value_of_information": 5.0,
                "ranked_by_value": ["use_crude_early", "baseline_trigger", "use_accurate_late"],
                "ranked_by_skill": ["use_accurate_late", "use_crude_early", "baseline_trigger"],
                "recommended_policy": "use_crude_early",
                "skill_and_value_agree": False,
            },
            "invariants": [
                {
                    "expression": "r['ranked_by_value'][0] == 'use_crude_early' and r['ranked_by_skill'][0] == 'use_accurate_late'",
                    "description": "the most valuable forecast is the least skilful one",
                },
                {
                    "expression": "abs(r['realizable_value_of_information'] - r['evpi']) < 1e-12",
                    "description": "the crude but timely forecast captures the entire EVPI",
                },
            ],
        },
        readme="""
# WG-BM-031 (G4) — Crude but timely

## Scenario

The WG-BM-030 decision — evacuate (cost 10) versus shelter in place (0 if the
fire misses, 100 if it hits), prior 50/50, deadline **minute 20** — with **two**
forecasts available:

| Forecast | Issued | Spatial error | Skill | Resolves hit/miss? |
|---|---|---|---|---|
| `forecast_accurate_late` | minute 30 | 10 m | 0.98 | yes, but too late |
| `forecast_crude_early` | minute 5 | 800 m | 0.40 | **yes, in time** |

The crude forecast is 800 m out on the front position and still gets the binary
question right: *does the fire reach the town?* That is the only question the
decision actually asks.

## Derivation

```
use_crude_early:     evacuate on "hit", shelter on "miss"
                     expected loss = 0.5 * 10 + 0.5 * 0 = 5
                     value         = 10 - 5 = +5

use_accurate_late:   arrives after the deadline -> shelters by default
                     expected loss = 0.5 * 100 + 0.5 * 0 = 50
                     value         = 10 - 50 = -40

EVPI = 10 - 5 = 5        realisable value = 5   (captured entirely by the crude forecast)
```

| Ranking | 1st | 2nd | 3rd |
|---|---|---|---|
| by **value** | `use_crude_early` (+5) | `baseline_trigger` (0) | `use_accurate_late` (-40) |
| by **skill** | `use_accurate_late` (0.98) | `use_crude_early` (0.40) | `baseline_trigger` |

**The rankings are exactly reversed.**

## Why the crude forecast captures the full EVPI

Because the decision is binary and the crude forecast resolves the binary
question. Spatial precision beyond "does it reach the town" is, for this
decision, unused information. The extra 790 m of accuracy in the late forecast
buys nothing at all, and the 10 minutes of extra lead time in the crude one buy
everything.

This generalises: the value of a forecast is bounded by the resolution of the
decision it informs. A binary decision can extract at most the value of a binary
signal. Increasing forecast resolution past the decision's own granularity has
zero marginal value, which is the same phenomenon WG-BM-028 shows from the other
direction.

## What this means for a forecasting programme

The relevant design question is not "how accurate can we get?" but "what is the
most useful thing we can say **before minute 20**?" Those are different
optimisation problems, and this pair of benchmarks (G3, G4) exists so that a
system cannot answer the first while claiming to have answered the second.

Two mutations are detected here: `skill_implies_value`, which picks
`use_accurate_late` as the recommendation, and `forecast_always_trusted`, which
makes the late forecast usable and erases the distinction.
""",
    ))

    # ------------------------------------------------------------------ G5
    written.append(write_benchmark(
        directory="benchmarks/forecast_value/WG-BM-032_G5_strong_baseline",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-032",
            "label": "G5",
            "title": "A conservative trigger already gets it right: forecast added value is zero",
            "category": "forecast_value",
            "difficulty": "intermediate",
            "purpose": "A cheap trip-wire policy takes exactly the same action as the "
                       "sophisticated forecast in every scenario. The added value of the "
                       "forecast is exactly 0, even though EVPI against a fixed action is 2.5.",
            "solver": "decision.value_of_information",
            "assumptions": {
                "trigger_available_at_min": 0,
                "trigger_resolves_the_same_question": True,
                "cost_of_the_forecast_not_modelled": True,
            },
            "expected_behavior": {
                "value_by_policy": {"forecast_policy": 0.0},
                "identical_actions_to_baseline": {"forecast_policy": True},
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["baseline_too_weak", "forecast_value_overclaimed"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "The purpose of this benchmark is to be passed by a system that correctly "
                     "reports zero. A suite without a zero-value case rewards complexity.",
        },
        inputs={
            "decision": {
                "description": "A fire-within-3-km trip wire is available from minute 0 and a "
                               "model forecast from minute 5. Both separate the same two "
                               "scenarios, so both drive the same actions.",
                "scenarios": [
                    {"id": "s_hit", "probability": 0.5},
                    {"id": "s_miss", "probability": 0.5},
                ],
                "actions": ["evacuate", "stay"],
                "loss": {
                    "evacuate": {"s_hit": 5.0, "s_miss": 5.0},
                    "stay": {"s_hit": 100.0, "s_miss": 0.0},
                },
                "decision_deadline_min": 20.0,
                "default_action": "evacuate",
                "truth_scenario": "s_hit",
                "information_sources": [
                    {
                        "id": "trigger_3km",
                        "available_at_min": 0.0,
                        "signal": {"s_hit": "tripped", "s_miss": "clear"},
                        "skill_score": 0.5,
                        "spatial_error_m": 3000.0,
                    },
                    {
                        "id": "forecast_model",
                        "available_at_min": 5.0,
                        "signal": {"s_hit": "hit", "s_miss": "miss"},
                        "skill_score": 0.95,
                        "spatial_error_m": 50.0,
                    },
                ],
                "policies": [
                    {"id": "trigger_policy", "type": "informed", "source": "trigger_3km"},
                    {"id": "forecast_policy", "type": "informed", "source": "forecast_model"},
                ],
                "baseline_policy": "trigger_policy",
            }
        },
        expected={
            "benchmark_id": "WG-BM-032",
            "source": "hand_derivation",
            "derivation": (
                "Both information sources separate s_hit from s_miss and both are available "
                "before the deadline, so both drive the same actions: evacuate when the fire is "
                "coming (5 beats 100) and stay when it is not (0 beats 5). Each policy therefore "
                "has expected loss 0.5 * 5 + 0.5 * 0 = 2.5, and the added value of the "
                "sophisticated forecast over the trip wire is exactly 0. "
                "Measured instead against the best fixed action, which is to evacuate always at "
                "expected loss 5, the value of perfect information is 5 - 2.5 = 2.5. So the "
                "information in this problem is worth 2.5 and the trip wire has already "
                "collected all of it. In the realised scenario s_hit both policies evacuate and "
                "both lose 5."
            ),
            "results": {
                "truth_scenario": "s_hit",
                "baseline_policy": "trigger_policy",
                "expected_loss_by_policy": {"trigger_policy": 2.5, "forecast_policy": 2.5},
                "value_by_policy": {"trigger_policy": 0.0, "forecast_policy": 0.0},
                "realised_loss_by_policy": {"trigger_policy": 5.0, "forecast_policy": 5.0},
                "identical_actions_to_baseline": {"trigger_policy": True, "forecast_policy": True},
                "clairvoyant_expected_loss": 2.5,
                "best_fixed_action": "evacuate",
                "best_fixed_expected_loss": 5.0,
                "evpi": 2.5,
                "realizable_value_of_information": 0.0,
                "timely_information_sources": ["forecast_model", "trigger_3km"],
            },
            "invariants": [
                {
                    "expression": "r['value_by_policy']['forecast_policy'] == 0.0",
                    "description": "the forecast adds exactly nothing to the trip-wire baseline",
                },
                {
                    "expression": "r['evpi'] > 0",
                    "description": "information is valuable in this problem; the baseline already has it",
                },
            ],
        },
        readme="""
# WG-BM-032 (G5) — Strong baseline

## Scenario

Evacuate (cost 5 either way) or stay (0 if the fire misses, 100 if it hits),
prior 50/50, deadline minute 20.

Two sources of information:

| Source | Available | Skill | What it says |
|---|---|---|---|
| `trigger_3km` — a fire-within-3-km trip wire | minute 0 | 0.50 | tripped / clear |
| `forecast_model` — a coupled fire-weather model | minute 5 | 0.95 | hit / miss |

Both separate the same two scenarios.

## Derivation

Both policies evacuate on the threatening signal (5 beats 100) and stay on the
benign one (0 beats 5):

```
expected loss, trigger policy  = 0.5 * 5 + 0.5 * 0 = 2.5
expected loss, forecast policy = 0.5 * 5 + 0.5 * 0 = 2.5
added value of the forecast    = 0
```

Measured against the best *fixed* action (always evacuate, expected loss 5):

```
EVPI = 5 - 2.5 = 2.5
```

So information is worth 2.5 in this problem, and **the trip wire has already
collected all of it**.

## Why a zero-value benchmark belongs in the suite

Every other benchmark in the G family shows a forecast doing something — helping
(G1, G4), hurting (G2, G6), or arriving too late to matter (G3). Without a case
whose correct answer is a flat zero, a benchmark suite silently rewards
complexity: any system that reports a positive value for its most sophisticated
component passes everything, and there is nothing to lose by overclaiming.

This case is also the common one in practice. Operational wildfire decisions are
frequently governed by conservative trigger points — distance to the fire, a red
flag warning, a pre-agreed evacuation zone — that were designed by people who
understood the problem. A new forecasting system has to beat *that*, not beat a
straw-man policy of doing nothing.

The comparison that matters is therefore always **against the best available
simple policy**, not against the absence of a policy. A system reporting the
value of its forecast relative to "no information" will report 2.5 here, and 2.5
is not what the forecast is worth.

## What is deliberately excluded

The cost of building, running and maintaining the forecast. Once the added
decision value is 0, any non-zero cost makes the net value negative, but this
suite does not model programme costs and so does not assert that.

## Expected

| Quantity | Value |
|---|---|
| added value of the forecast over the trigger | **0.0** |
| identical actions to the baseline | `true` |
| EVPI against the best fixed action | 2.5 |
| realisable value of information beyond the baseline | 0.0 |
""",
    ))

    # ------------------------------------------------------------------ G6
    scenarios_g6 = [{"id": f"s{i}", "probability": 0.2} for i in range(1, 6)]
    written.append(write_benchmark(
        directory="benchmarks/forecast_value/WG-BM-033_G6_forecast_harm",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-033",
            "label": "G6",
            "title": "Forecast harm: 80% accurate, and worse than the robust baseline",
            "category": "forecast_value",
            "difficulty": "adversarial",
            "purpose": "The forecast is right in four scenarios out of five and wrong in the one "
                       "that carries the consequences. Delta J is negative: acting on it is worse "
                       "than the robust policy.",
            "solver": "decision.value_of_information",
            "assumptions": {
                "forecast_errors_concentrated_in_the_tail": True,
                "signals_deterministic": True,
                "loss_units": "arbitrary but consistent",
            },
            "expected_behavior": {
                "value_by_policy": {"forecast_aware": -30.0},
                "recommended_policy": "robust_baseline",
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["skill_value_conflation", "error_consequence_correlation"],
            "mutations_expected_to_fail": ["skill_implies_value"],
            "hand_checkable": True,
        },
        inputs={
            "decision": {
                "description": "Five equally likely scenarios. Four are benign and one is "
                               "extreme. The forecast classifies the four benign scenarios "
                               "correctly and also calls the extreme one benign.",
                "scenarios": scenarios_g6,
                "actions": ["evacuate_early", "wait_and_see"],
                "loss": {
                    "evacuate_early": {"s1": 10.0, "s2": 10.0, "s3": 10.0, "s4": 10.0, "s5": 10.0},
                    "wait_and_see": {"s1": 0.0, "s2": 0.0, "s3": 0.0, "s4": 0.0, "s5": 200.0},
                },
                "decision_deadline_min": 20.0,
                "default_action": "evacuate_early",
                "truth_scenario": "s5",
                "information_sources": [
                    {
                        "id": "forecast_80pc",
                        "available_at_min": 5.0,
                        "signal": {
                            "s1": "benign",
                            "s2": "benign",
                            "s3": "benign",
                            "s4": "benign",
                            "s5": "benign",
                        },
                        "skill_score": 0.8,
                        "spatial_error_m": 150.0,
                    }
                ],
                "policies": [
                    {"id": "robust_baseline", "type": "fixed", "action": "evacuate_early"},
                    {
                        "id": "forecast_aware",
                        "type": "signal_map",
                        "source": "forecast_80pc",
                        "map": {"benign": "wait_and_see", "extreme": "evacuate_early"},
                    },
                ],
                "baseline_policy": "robust_baseline",
            }
        },
        expected={
            "benchmark_id": "WG-BM-033",
            "source": "hand_derivation",
            "derivation": (
                "The forecast says 'benign' in all five scenarios, so the forecast-aware policy "
                "waits in all five. Its expected loss is 0.8 * 0 + 0.2 * 200 = 40 against the "
                "robust baseline's 10, so the value of acting on the forecast is 10 - 40 = -30: "
                "Delta J is negative and the forecast is harmful. This happens although the "
                "forecast is correct in four cases out of five - a classification accuracy of "
                "0.8 - because its single error falls in the only scenario whose consequences "
                "are large. In the realised scenario s5 the forecast-aware policy loses 200 "
                "against the baseline's 10, a realised value of -190 and, since evacuating early "
                "is the best action there, a realised regret of 190. The clairvoyant expected "
                "loss is 0.8 * 0 + 0.2 * 10 = 2, so EVPI is 10 - 2 = 8: a forecast that caught "
                "the extreme scenario would have been worth 8, and this one is worth -30."
            ),
            "results": {
                "truth_scenario": "s5",
                "expected_loss_by_policy": {"robust_baseline": 10.0, "forecast_aware": 40.0},
                "value_by_policy": {"robust_baseline": 0.0, "forecast_aware": -30.0},
                "realised_loss_by_policy": {"robust_baseline": 10.0, "forecast_aware": 200.0},
                "realised_value_by_policy": {"robust_baseline": 0.0, "forecast_aware": -190.0},
                "realised_regret_by_policy": {"robust_baseline": 0.0, "forecast_aware": 190.0},
                "clairvoyant_expected_loss": 2.0,
                "best_fixed_action": "evacuate_early",
                "best_fixed_expected_loss": 10.0,
                "evpi": 8.0,
                "realizable_value_of_information": -30.0,
                "recommended_policy": "robust_baseline",
                "ranked_by_value": ["robust_baseline", "forecast_aware"],
                "ranked_by_skill": ["forecast_aware", "robust_baseline"],
                "skill_and_value_agree": False,
            },
            "invariants": [
                {
                    "expression": "r['value_by_policy']['forecast_aware'] < 0",
                    "description": "Delta J is negative: the forecast-aware policy is worse than the baseline",
                },
                {
                    "expression": "r['evpi'] > 0 > r['realizable_value_of_information']",
                    "description": "information would help; this particular forecast harms",
                },
            ],
        },
        readme="""
# WG-BM-033 (G6) — Forecast harm

## Scenario

Five equally likely scenarios. Four are benign; `s5` is extreme.

| | s1 | s2 | s3 | s4 | s5 |
|---|---|---|---|---|---|
| `evacuate_early` | 10 | 10 | 10 | 10 | 10 |
| `wait_and_see` | 0 | 0 | 0 | 0 | **200** |

The forecast calls all five scenarios benign. It is therefore **right 4 times
out of 5** — a classification accuracy of 0.8 — and wrong exactly once.

## Derivation

Acting on the forecast means waiting in every scenario:

```
expected loss, forecast-aware = 0.8 * 0 + 0.2 * 200 = 40
expected loss, robust baseline (always evacuate early) = 10
Delta J = 10 - 40 = -30          <- the forecast is harmful
```

In the realised world (`s5`):

```
realised loss, forecast-aware = 200
realised loss, baseline       = 10
realised regret               = 190
```

And yet information *would* help:

```
clairvoyant expected loss = 0.8 * 0 + 0.2 * 10 = 2
EVPI                      = 10 - 2 = 8
```

A forecast that caught the extreme scenario would be worth **+8**. This one is
worth **-30**.

## The mechanism: errors correlated with consequences

The forecast's single error is not randomly placed. It falls in the only
scenario where the choice of action matters. This is the normal situation rather
than a contrived one, for a structural reason: the scenarios a model finds hard
to predict — rapid escalation, unexpected wind shift, plume-driven behaviour —
are the same scenarios that produce extreme losses. Model error and consequence
are positively correlated almost by construction.

The consequence for evaluation is severe: **aggregate accuracy is nearly
uninformative about decision value when errors are consequence-correlated.** A
forecast can be made arbitrarily accurate on the benign majority without
improving, or while degrading, its decision value.

## What a system should do with this

Three defensible responses, none of which is "use the forecast because it is
80% accurate":

1. **Evaluate on a loss-weighted basis.** Score the forecast by the loss its
   errors induce, not by how often it is right.
2. **Use the forecast asymmetrically.** Let it trigger escalation but never
   stand down a precaution — a one-sided use is robust to exactly this error
   pattern.
3. **Report the tail explicitly.** A probabilistic forecast saying "benign, but
   5% chance of extreme" supports the right action; a deterministic "benign"
   cannot.

The `skill_implies_value` mutation recommends the forecast-aware policy because
its skill score is the higher one, and this benchmark is among its detectors.

## Expected

| Quantity | Value |
|---|---|
| forecast classification accuracy | 0.8 |
| Delta J (value of the forecast) | **-30** |
| realised regret in `s5` | 190 |
| EVPI | 8 |
| recommended policy | `robust_baseline` |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
