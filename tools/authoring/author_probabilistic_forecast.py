"""Author K1-K5: predictive distributions, decision thresholds and coherent
ensembles (WG-BM-044..048).

The K family is split across two authoring scripts because it is large:
this one covers forecasts and ensembles, ``author_bayesian_inference.py``
covers posteriors and observations.
"""

from __future__ import annotations

import math

from common import report, write_benchmark

SCRIPT = "author_probabilistic_forecast.py"
TOL = {"default": 1.0e-12}


def phi(x: float, mean: float, sd: float) -> float:
    """P(X <= x) for X ~ N(mean, sd^2). The closed form, written out."""
    return 0.5 * (1.0 + math.erf((x - mean) / (sd * math.sqrt(2.0))))


# K1 ------------------------------------------------------------------------
K1_PA = phi(800.0, 1000.0, 50.0)
K1_PB = phi(800.0, 1000.0, 300.0)
K1_PSTAR = 8.0 / 100.0

# K2 ------------------------------------------------------------------------
K2_PA = phi(800.0, 910.0, 400.0)
K2_PB = phi(800.0, 940.0, 50.0)
K2_TRUE_MEAN = 0.97 * 900.0 + 0.03 * 700.0


def main() -> None:
    written = []

    # ------------------------------------------------------------------ K1
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-044_K1_same_mean_different_uncertainty",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-044",
            "label": "K1",
            "title": "Same mean, different uncertainty, different correct action",
            "category": "probabilistic_forecast",
            "difficulty": "basic",
            "purpose": "Two forecasts with identical mean and different spread. A point-estimate "
                       "policy cannot tell them apart; the correct action differs.",
            "solver": "probabilistic.predictive_threshold",
            "assumptions": {
                "predictive_distribution": "normal",
                "threshold_m": 800,
                "hazard_when": "below",
                "decision_rule": "minimise expected loss under the predictive distribution",
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "predictive_distribution",
                "loss_matrix": "use_road 0/100, long_way 8/8",
                "decision_threshold": K1_PSTAR,
            },
            "expected_behavior": {
                "decision_threshold_probability": K1_PSTAR,
                "point_estimate_distinguishes_forecasts": False,
                "distribution_distinguishes_forecasts": True,
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["forecast_uncertainty_discarded", "point_estimate_substituted_for_distribution"],
            "mutations_expected_to_fail": ["ignore_forecast_variance"],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "Predicted distance of the fire front from the valley road at the "
                               "moment the convoy would be on it. The road is unusable if the "
                               "front is within 800 m. Both forecasts centre on 1000 m; A is "
                               "sharp and B is broad.",
                "model": "predictive_threshold",
                "quantity": "front_distance_m",
                "threshold": 800.0,
                "hazard_when": "below",
                "hazard_state": "hazard",
                "clear_state": "clear",
                "actions": ["use_road", "long_way"],
                "loss": {
                    "use_road": {"hazard": 100.0, "clear": 0.0},
                    "long_way": {"hazard": 8.0, "clear": 8.0},
                },
                "forecasts": [
                    {"id": "forecast_a", "distribution": "normal", "mean": 1000.0, "sd": 50.0},
                    {"id": "forecast_b", "distribution": "normal", "mean": 1000.0, "sd": 300.0},
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-044",
            "source": "closed_form",
            "derivation": (
                "The decision threshold follows from the loss matrix alone. Writing p for the "
                "probability that the front is inside 800 m, the expected loss of using the road "
                "is 100p and of the long way is 8, so the actions are indifferent at "
                "p* = 8/100 = 0.08 and the road is used only below that. "
                "Forecast A is N(1000, 50^2), so p_A = Phi((800 - 1000)/50) = Phi(-4) = "
                "3.167124183311998e-05, which is far below 0.08: use the road. "
                "Forecast B is N(1000, 300^2), so p_B = Phi((800 - 1000)/300) = Phi(-2/3) = "
                "0.2524925375469229, which is above 0.08: take the long way. "
                "Both forecasts have mean 1000 m, so a policy that reads only the point estimate "
                "sees 1000 > 800 in both cases, calls the road clear in both cases, and cannot "
                "distinguish them. The distinction is entirely in the spread."
            ),
            "results": {
                "model": "predictive_threshold",
                "threshold": 800.0,
                "decision_threshold_probability": K1_PSTAR,
                "action_partition": [
                    {"p_from": 0.0, "p_to": K1_PSTAR, "action": "use_road"},
                    {"p_from": K1_PSTAR, "p_to": 1.0, "action": "long_way"},
                ],
                "hazard_probability_by_forecast": {
                    "forecast_a": K1_PA,
                    "forecast_b": K1_PB,
                },
                "action_by_forecast": {
                    "forecast_a": "use_road",
                    "forecast_b": "long_way",
                },
                "point_estimate_action_by_forecast": {
                    "forecast_a": "use_road",
                    "forecast_b": "use_road",
                },
                "point_estimate_distinguishes_forecasts": False,
                "distribution_distinguishes_forecasts": True,
                "forecasts": {
                    "forecast_a": {
                        "mean": 1000.0,
                        "sd": 50.0,
                        "expected_loss": {"use_road": 100.0 * K1_PA, "long_way": 8.0},
                    },
                    "forecast_b": {
                        "mean": 1000.0,
                        "sd": 300.0,
                        "expected_loss": {"use_road": 100.0 * K1_PB, "long_way": 8.0},
                    },
                },
            },
            "invariants": [
                {
                    "expression": "r['forecasts']['forecast_a']['mean'] == r['forecasts']['forecast_b']['mean']",
                    "description": "the two forecasts have exactly the same point prediction",
                },
                {
                    "expression": "r['action_by_forecast']['forecast_a'] != r['action_by_forecast']['forecast_b']",
                    "description": "and nevertheless require different actions",
                },
                {
                    "expression": "len(set(r['point_estimate_action_by_forecast'].values())) == 1",
                    "description": "a point-estimate policy cannot tell them apart",
                },
            ],
        },
        readme=f"""
# WG-BM-044 (K1) — Same mean, different uncertainty

## Scenario

A convoy may take the valley road (fast) or the long way round. The valley road
is unusable if the fire front is within **800 m** when the convoy is on it.

| | front inside 800 m | front clear |
|---|---|---|
| `use_road` | 100 | 0 |
| `long_way` | 8 | 8 |

Two forecasts of the front distance, **with the same mean**:

| Forecast | Distribution | Point estimate |
|---|---|---|
| A | `N(1000, 50^2)` | 1000 m |
| B | `N(1000, 300^2)` | 1000 m |

## Derivation

**The threshold comes from the loss matrix, not from convention.** With `p` the
probability that the front is inside 800 m:

```
E[use_road] = 100p        E[long_way] = 8
indifference: 100 p* = 8  ->  p* = 0.08
```

**Forecast A.**

```
p_A = Phi((800 - 1000) / 50) = Phi(-4) = {K1_PA:.10e}
```

`p_A << 0.08` → **use the road** (expected loss {100 * K1_PA:.6f} against 8).

**Forecast B.**

```
p_B = Phi((800 - 1000) / 300) = Phi(-2/3) = {K1_PB:.10f}
```

`p_B > 0.08` → **take the long way** (expected loss {100 * K1_PB:.4f} against 8).

## The point

Both forecasts say **1000 m**. A pipeline that carries the point estimate and
discards the spread produces one number, `1000 > 800`, and therefore one action,
in both cases — and that action is wrong under forecast B by a factor of three
in expected loss.

The spread is not a caveat attached to the forecast. Under a threshold decision
it **is** the forecast: the decision consumes `P(X <= 800)`, and the mean enters
only through that probability. Two forecasts with the same mean can sit on
opposite sides of the decision, which is what makes "the forecast said 1000 m" an
incomplete statement of what was predicted.

The `ignore_forecast_variance` mutation collapses each distribution to its mean;
this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| decision threshold `p*` | **0.08** |
| `P(front <= 800)` under A | `{K1_PA:.6e}` |
| `P(front <= 800)` under B | `{K1_PB:.6f}` |
| action under A / B | `use_road` / **`long_way`** |
| action from the point estimate, A and B | `use_road` / `use_road` |
""",
    ))

    # ------------------------------------------------------------------ K2
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-045_K2_better_point_worse_decision",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-045",
            "label": "K2",
            "title": "Better point error, worse decision: a 16 m forecast beaten by a 46 m one",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "Forecast A has a third of B's location error and a fat tail; B is further "
                       "out and tight. B attains the best achievable expected loss and A does not.",
            "solver": "probabilistic.predictive_threshold",
            "assumptions": {
                "predictive_distribution": "normal",
                "threshold_m": 800,
                "hazard_when": "below",
                "true_world_is_a_declared_finite_ensemble": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "predictive_distribution",
                "decision_threshold": 0.08,
                "expected_value": "expected loss under the declared true world distribution",
            },
            "expected_behavior": {
                "location_error_by_forecast": {"forecast_a": 16.0, "forecast_b": 46.0},
                "expected_loss_under_truth_by_forecast": {"forecast_a": 8.0, "forecast_b": 3.0},
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["deterministic_skill_mistaken_for_decision_value", "forecast_uncertainty_discarded"],
            "mutations_expected_to_fail": ["ignore_forecast_variance"],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "The WG-BM-044 decision with a declared true world: the front is "
                               "at 900 m with probability 0.97 and at 700 m with probability "
                               "0.03. Forecast A is nearly unbiased and very broad; forecast B is "
                               "biased high and sharp.",
                "model": "predictive_threshold",
                "quantity": "front_distance_m",
                "threshold": 800.0,
                "hazard_when": "below",
                "hazard_state": "hazard",
                "clear_state": "clear",
                "actions": ["use_road", "long_way"],
                "loss": {
                    "use_road": {"hazard": 100.0, "clear": 0.0},
                    "long_way": {"hazard": 8.0, "clear": 8.0},
                },
                "forecasts": [
                    {"id": "forecast_a", "distribution": "normal", "mean": 910.0, "sd": 400.0},
                    {"id": "forecast_b", "distribution": "normal", "mean": 940.0, "sd": 50.0},
                ],
                "true_world": {
                    "scenarios": [
                        {"id": "w_clear", "probability": 0.97, "value": 900.0},
                        {"id": "w_blocked", "probability": 0.03, "value": 700.0},
                    ]
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-045",
            "source": "closed_form",
            "derivation": (
                "The true world puts the front at 900 m with probability 0.97 and at 700 m with "
                "probability 0.03, so its mean is 0.97*900 + 0.03*700 = 894 m and the true "
                "probability of the hazard state is 0.03. Since 0.03 < p* = 0.08, the best action "
                "under the truth is to use the road, at an expected loss of 0.03*100 = 3. "
                "Forecast A is N(910, 400^2): its location error is |910 - 894| = 16 m, the "
                "smallest of the two, but Phi((800 - 910)/400) = Phi(-0.275) = 0.3916581191536052 "
                "is well above 0.08, so it takes the long way, at an expected loss of 8 in every "
                "world. "
                "Forecast B is N(940, 50^2): its location error is |940 - 894| = 46 m, nearly "
                "three times A's, but Phi((800 - 940)/50) = Phi(-2.8) = 0.002555130330427924 is "
                "below 0.08, so it uses the road, at an expected loss of 3 - exactly the best "
                "achievable. A's regret is 5 and B's is 0."
            ),
            "results": {
                "model": "predictive_threshold",
                "decision_threshold_probability": 0.08,
                "true_mean": K2_TRUE_MEAN,
                "true_hazard_probability": 0.03,
                "best_action_under_truth": "use_road",
                "best_expected_loss_under_truth": 3.0,
                "hazard_probability_by_forecast": {"forecast_a": K2_PA, "forecast_b": K2_PB},
                "action_by_forecast": {"forecast_a": "long_way", "forecast_b": "use_road"},
                "location_error_by_forecast": {"forecast_a": 16.0, "forecast_b": 46.0},
                "expected_loss_under_truth_by_forecast": {"forecast_a": 8.0, "forecast_b": 3.0},
                "regret_by_forecast": {"forecast_a": 5.0, "forecast_b": 0.0},
            },
            "invariants": [
                {
                    "expression": "r['location_error_by_forecast']['forecast_a'] < r['location_error_by_forecast']['forecast_b']",
                    "description": "forecast A has the better deterministic skill",
                },
                {
                    "expression": "r['expected_loss_under_truth_by_forecast']['forecast_a'] > r['expected_loss_under_truth_by_forecast']['forecast_b']",
                    "description": "and the worse decision outcome",
                },
                {
                    "expression": "r['regret_by_forecast']['forecast_b'] == 0.0",
                    "description": "the less accurate forecast attains the best achievable expected loss",
                },
            ],
        },
        readme=f"""
# WG-BM-045 (K2) — Better point error, worse decision distribution

## Scenario

The WG-BM-044 decision (`use_road` 0/100, `long_way` 8/8, threshold 800 m,
`p* = 0.08`) with a **declared true world**:

```
front at 900 m   with probability 0.97      (road clear)
front at 700 m   with probability 0.03      (road unusable)

true mean = 0.97 * 900 + 0.03 * 700 = 894 m
true P(hazard) = 0.03
```

Two forecasts:

| Forecast | Distribution | Location error vs 894 m | `P(front <= 800)` |
|---|---|---|---|
| A | `N(910, 400^2)` | **16 m** | `{K2_PA:.6f}` |
| B | `N(940, 50^2)` | 46 m | `{K2_PB:.6f}` |

## Derivation

Best achievable: `0.03 < 0.08`, so the road should be used, at an expected loss
of `0.03 * 100 = 3`.

```
Forecast A:  P = Phi((800-910)/400) = Phi(-0.275) = {K2_PA:.10f}  >  0.08  ->  long_way
             expected loss under the truth = 8      regret = 5

Forecast B:  P = Phi((800-940)/50)  = Phi(-2.8)   = {K2_PB:.10f}  <  0.08  ->  use_road
             expected loss under the truth = 3      regret = 0
```

**Forecast A has one third of B's location error and five units more regret.**

## Why this is not a trick

A's mean is almost exactly right and its distribution is almost uninformative:
with `sd = 400` it assigns 39% probability to a hazard that occurs 3% of the
time. B's mean is 46 m too far out and its distribution is nearly right about
the thing the decision consumes — the tail mass below 800 m.

A threshold decision reads a **tail probability**, and a tail probability is
determined by the mean *and* the spread together. Mean absolute error, RMSE and
displacement scores read only the first of those, so they can rank two forecasts
in the opposite order to any decision that depends on the second.

Read next to WG-BM-029, which makes the deterministic version of the same point:
there a 20 m error cost 92 while a 500 m error cost nothing, because what
mattered was the distance to the decision boundary. Here what matters is how much
probability mass the forecast puts on the wrong side of it.

## Expected

| Quantity | Forecast A | Forecast B |
|---|---|---|
| location error | **16 m** | 46 m |
| `P(front <= 800)` | 0.3917 | 0.0026 |
| action | `long_way` | `use_road` |
| expected loss under the truth | 8 | **3** |
| regret | 5 | **0** |
""",
    ))

    # ------------------------------------------------------------------ K3
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-046_K3_calibrated_probability_changes_action",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-046",
            "label": "K3",
            "title": "The action switches at p* = 0.2, which the loss matrix fixes and 0.5 does not",
            "category": "probabilistic_forecast",
            "difficulty": "basic",
            "purpose": "Derive the Bayes-optimal action as a function of the hazard probability "
                       "and verify the switch point. At p = 0.35 a half-probability rule gives the "
                       "wrong answer.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "two_states": True,
                "decision_rule": "minimise expected loss",
                "threshold_derived_from_loss_matrix": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "binary_probability",
                "loss_matrix": "proceed 120/0, divert 24/24",
                "decision_threshold": 0.2,
            },
            "expected_behavior": {
                "decision_threshold_probability": 0.2,
                "action_by_probe": {"0.1": "proceed", "0.35": "divert", "0.6": "divert"},
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["decision_threshold_not_derived_from_loss", "arbitrary_probability_cutoff"],
            "mutations_expected_to_fail": ["fixed_half_probability_threshold"],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "A single route with a calibrated probability of closing. Diverting "
                               "costs the same whatever happens; proceeding is free if the route "
                               "stays open and costly if it closes.",
                "model": "bayes_decision",
                "hypotheses": [
                    {"id": "H_closed", "prior": 0.1},
                    {"id": "H_open", "prior": 0.9},
                ],
                "hazard_hypothesis": "H_closed",
                "actions": ["proceed", "divert"],
                "loss": {
                    "proceed": {"H_closed": 120.0, "H_open": 0.0},
                    "divert": {"H_closed": 24.0, "H_open": 24.0},
                },
                "probe_probabilities": [0.1, 0.35, 0.6],
            }
        },
        expected={
            "benchmark_id": "WG-BM-046",
            "source": "closed_form",
            "derivation": (
                "With p the probability that the route closes, E[proceed] = 120p and "
                "E[divert] = 24. The two are indifferent when 120 p* = 24, so p* = 24/120 = 0.2, "
                "and proceeding is optimal strictly below it. "
                "At p = 0.1: E[proceed] = 12 < 24, proceed. "
                "At p = 0.35: E[proceed] = 42 > 24, divert. "
                "At p = 0.6: E[proceed] = 72 > 24, divert. "
                "A rule that diverts when p exceeds one half agrees at 0.1 and 0.6 by luck and "
                "disagrees at 0.35, where it proceeds into a route that is 35 per cent likely to "
                "close. Under the declared prior of 0.1 the prior-optimal action is to proceed, "
                "with expected loss 12; the clairvoyant expected loss is 0.1*24 + 0.9*0 = 2.4, so "
                "EVPI is 9.6."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.1,
                "prior_action": "proceed",
                "prior_expected_loss": 12.0,
                "decision_threshold_probability": 0.2,
                "action_partition": [
                    {"p_from": 0.0, "p_to": 0.2, "action": "proceed"},
                    {"p_from": 0.2, "p_to": 1.0, "action": "divert"},
                ],
                "clairvoyant_expected_loss": 2.4,
                "evpi": 9.6,
                "action_by_probe": {"0.1": "proceed", "0.35": "divert", "0.6": "divert"},
                "probes": {
                    "0.1": {"expected_loss": {"proceed": 12.0, "divert": 24.0}, "above_threshold": False},
                    "0.35": {"expected_loss": {"proceed": 42.0, "divert": 24.0}, "above_threshold": True},
                    "0.6": {"expected_loss": {"proceed": 72.0, "divert": 24.0}, "above_threshold": True},
                },
            },
            "invariants": [
                {
                    "expression": "abs(r['decision_threshold_probability'] - 0.2) < 1e-12",
                    "description": "the switch point is 0.2, not 0.5",
                },
                {
                    "expression": "r['action_by_probe']['0.35'] == 'divert'",
                    "description": "a probability below one half still requires the conservative action",
                },
            ],
        },
        readme="""
# WG-BM-046 (K3) — Calibrated uncertainty changes the action

## Scenario

One route, with a calibrated probability `p` of closing before the convoy is
through.

| | route closes | route stays open |
|---|---|---|
| `proceed` | 120 | 0 |
| `divert` | 24 | 24 |

## Derivation

```
E[proceed] = 120 p        E[divert] = 24
indifference:  120 p* = 24   ->   p* = 24 / 120 = 0.2
```

`proceed` is optimal strictly below 0.2 and `divert` at or above it.

| `p` | `E[proceed]` | `E[divert]` | Bayes action | action under a 0.5 rule |
|---|---|---|---|---|
| 0.10 | 12 | 24 | `proceed` | `proceed` (agrees by luck) |
| **0.35** | **42** | **24** | **`divert`** | **`proceed`** — wrong |
| 0.60 | 72 | 24 | `divert` | `divert` (agrees by luck) |

Under the declared prior of 0.1 the prior-optimal action is `proceed`, expected
loss 12; the clairvoyant expected loss is `0.1 * 24 + 0.9 * 0 = 2.4`, so EVPI is
9.6.

## The point

`p = 0.5` is not a decision threshold. It is the point at which one *hypothesis*
becomes more likely than another, which is a different question from which
*action* is better. The two coincide only when the loss matrix is symmetric, and
a wildfire loss matrix never is.

The probe at 0.35 exists because the other two agree with the wrong rule. A
benchmark whose cases all happen to agree with the bug does not detect it; this
is the same discipline that removed the overclaim from WG-BM-028.

WG-BM-047 takes the asymmetry to its operational extreme, where `p*` is 0.01.

## Expected

| Quantity | Value |
|---|---|
| `p*` | **0.2** |
| action at 0.1 / 0.35 / 0.6 | `proceed` / `divert` / `divert` |
| EVPI under the prior | 9.6 |
""",
    ))

    # ------------------------------------------------------------------ K4
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-047_K4_asymmetric_loss_threshold",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-047",
            "label": "K4",
            "title": "Asymmetric loss puts the threshold at one per cent",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "When an unnecessary precaution costs 5 and an entrapment costs 495, the "
                       "action switches at p* = 5/500 = 0.01. A half-probability rule proceeds at "
                       "p = 0.4, at 66 times the optimal expected loss.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "two_states": True,
                "conservative_action_fully_protects": True,
                "threshold_formula": "p* = L_conservative / (L_conservative + L_failure)",
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "binary_probability",
                "loss_matrix": "proceed 495/0, hold_back 0/5",
                "decision_threshold": 0.01,
            },
            "expected_behavior": {
                "decision_threshold_probability": 0.01,
                "action_by_probe": {"0.005": "proceed", "0.02": "hold_back", "0.4": "hold_back"},
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["decision_threshold_not_derived_from_loss", "loss_asymmetry_ignored"],
            "mutations_expected_to_fail": ["fixed_half_probability_threshold"],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "Send a crew down a spur road, or hold them back. Holding back "
                               "costs 5 in lost time when the road was in fact safe and nothing "
                               "when it was not; proceeding costs nothing when the road is safe "
                               "and 495 when the crew is caught.",
                "model": "bayes_decision",
                "hypotheses": [
                    {"id": "H_dangerous", "prior": 0.02},
                    {"id": "H_safe", "prior": 0.98},
                ],
                "hazard_hypothesis": "H_dangerous",
                "actions": ["proceed", "hold_back"],
                "loss": {
                    "proceed": {"H_dangerous": 495.0, "H_safe": 0.0},
                    "hold_back": {"H_dangerous": 0.0, "H_safe": 5.0},
                },
                "probe_probabilities": [0.005, 0.02, 0.4],
            }
        },
        expected={
            "benchmark_id": "WG-BM-047",
            "source": "closed_form",
            "derivation": (
                "Here the conservative action fully protects, so E[proceed] = p * L_failure and "
                "E[hold_back] = (1 - p) * L_conservative. Indifference gives "
                "p* L_f = (1 - p*) L_c, hence p* = L_c / (L_c + L_f) = 5 / (5 + 495) = 0.01. "
                "At p = 0.005: E[proceed] = 2.475 against E[hold_back] = 4.975, so proceed. "
                "At p = 0.02: E[proceed] = 9.9 against 4.9, so hold back. "
                "At p = 0.4: E[proceed] = 198 against 3.0, so hold back - and a half-probability "
                "rule would proceed, at 66 times the optimal expected loss. "
                "Under the declared prior of 0.02 the prior-optimal action is to hold back, at "
                "0.98 * 5 = 4.9; the clairvoyant expected loss is 0, because each state has a "
                "zero-loss action available, so EVPI is 4.9."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.02,
                "prior_action": "hold_back",
                "prior_expected_loss": 4.9,
                "decision_threshold_probability": 0.01,
                "action_partition": [
                    {"p_from": 0.0, "p_to": 0.01, "action": "proceed"},
                    {"p_from": 0.01, "p_to": 1.0, "action": "hold_back"},
                ],
                "clairvoyant_expected_loss": 0.0,
                "evpi": 4.9,
                "action_by_probe": {"0.005": "proceed", "0.02": "hold_back", "0.4": "hold_back"},
                "probes": {
                    "0.005": {"expected_loss": {"proceed": 2.475, "hold_back": 4.975}},
                    "0.02": {"expected_loss": {"proceed": 9.9, "hold_back": 4.9}},
                    "0.4": {"expected_loss": {"proceed": 198.0, "hold_back": 3.0}},
                },
            },
            "invariants": [
                {
                    "expression": "abs(r['decision_threshold_probability'] - 5.0 / (5.0 + 495.0)) < 1e-12",
                    "description": "p* equals L_conservative / (L_conservative + L_failure)",
                },
                {
                    "expression": "r['action_by_probe']['0.4'] == 'hold_back'",
                    "description": "a 40 per cent hazard probability is nowhere near permissive",
                },
                {
                    "expression": "r['probes']['0.4']['expected_loss']['proceed'] > 60 * r['probes']['0.4']['expected_loss']['hold_back']",
                    "description": "the half-probability rule is wrong by a factor over 60 here",
                },
            ],
        },
        readme="""
# WG-BM-047 (K4) — Asymmetric loss threshold

## Scenario

A crew can be sent down a spur road or held back.

| | road dangerous | road safe |
|---|---|---|
| `proceed` | **495** | 0 |
| `hold_back` | 0 | 5 |

Holding back costs 5 in lost time when the road was in fact safe, and nothing
when it was not. Proceeding costs nothing when the road is safe, and 495 when
the crew is caught.

## Derivation

The conservative action fully protects, so

```
E[proceed]   = p * L_failure
E[hold_back] = (1 - p) * L_conservative

p* L_f = (1 - p*) L_c   ->   p* = L_c / (L_c + L_f) = 5 / (5 + 495) = 0.01
```

| `p` | `E[proceed]` | `E[hold_back]` | Bayes action | 0.5 rule |
|---|---|---|---|---|
| 0.005 | 2.475 | 4.975 | `proceed` | `proceed` |
| 0.02 | 9.9 | 4.9 | `hold_back` | `proceed` — wrong |
| **0.40** | **198** | **3.0** | **`hold_back`** | **`proceed`** — wrong by 66x |

Under the prior of 0.02: prior action `hold_back`, expected loss 4.9;
clairvoyant expected loss 0; **EVPI = 4.9**.

## The point

The threshold is **1 per cent**. There is nothing unusual about the numbers: a
100:1 ratio between an entrapment and a delay is conservative if anything. The
consequence is that for most of the probability range the answer is "hold back",
and a system that waits for the hazard to become *likely* has already waited
forty times too long.

Note also what the formula depends on. Doubling both losses leaves `p*`
unchanged, so the threshold is a property of the **ratio** of the two costs, not
their scale — which is why it can be elicited from an incident commander who
would not put a number on either loss alone.

Two different matrices give two different formulas, and both appear in this
suite:

| Situation | Threshold |
|---|---|
| conservative action costs the same either way (WG-BM-046) | `p* = L_c / L_f` |
| conservative action fully protects (here) | `p* = L_c / (L_c + L_f)` |

Neither is 0.5, and an implementation must derive the threshold rather than
assume one. The `fixed_half_probability_threshold` mutation assumes one; this
benchmark and WG-BM-046 are its declared detectors.

## Expected

| Quantity | Value |
|---|---|
| `p*` | **0.01** |
| action at 0.005 / 0.02 / 0.4 | `proceed` / `hold_back` / `hold_back` |
| EVPI under the prior | 4.9 |
""",
    ))

    # ------------------------------------------------------------------ K5
    scenario_losses = {
        "assume_egress": {
            "omega_1": 0.0, "omega_2": 0.0, "omega_3": 0.0,
            "omega_4": 140.0, "omega_5": 140.0,
        },
        "prepare_isolation": {
            "omega_1": 40.0, "omega_2": 40.0, "omega_3": 40.0,
            "omega_4": 40.0, "omega_5": 40.0,
        },
    }
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-048_K5_coherent_scenario_ensemble",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-048",
            "label": "K5",
            "title": "A coherent ensemble: admissibility, normalisation and the joint",
            "category": "probabilistic_forecast",
            "difficulty": "intermediate",
            "purpose": "Four admissible worlds and one inadmissible one. Weights renormalise over "
                       "the admissible set, the joint closure probability is read off the "
                       "ensemble, and multiplying marginals flips the decision.",
            "solver": "probabilistic.scenario_ensemble",
            "assumptions": {
                "weight_semantics": "unnormalised, renormalised over admissible scenarios only",
                "inadmissible_scenarios_excluded": True,
                "joint_read_from_ensemble": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "scenario_ensemble",
                "independence_assumed": False,
                "expected_value": "expected loss over the renormalised admissible weights",
            },
            "expected_behavior": {
                "excluded_scenarios": ["omega_5"],
                "joint_all_closed_probability": 0.375,
                "best_action": "prepare_isolation",
                "best_action_under_independence": "assume_egress",
            },
            "tolerance": TOL,
            "exactness": "FINITE_ENUMERATION",
            "detects": [
                "scenario_weights_normalised_incorrectly",
                "correlation_ignored",
                "inadmissible_scenario_included",
            ],
            "mutations_expected_to_fail": [
                "renormalise_including_inadmissible",
                "independent_edge_failures",
            ],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "Five worlds emitted by an ensemble generator, describing the "
                               "joint state of the north and south roads. omega_5 is physically "
                               "inadmissible: it closes the north road under a south wind, which "
                               "the declared physics forbids, and it is flagged rather than "
                               "silently dropped so that the exclusion is visible.",
                "model": "scenario_ensemble",
                "weight_semantics": "unnormalised_over_admissible",
                "edges": ["north_road", "south_road"],
                "scenarios": [
                    {"id": "omega_1", "weight": 3.0, "admissible": True,
                     "state": {"north_road": "open", "south_road": "open"}},
                    {"id": "omega_2", "weight": 1.0, "admissible": True,
                     "state": {"north_road": "closed", "south_road": "open"}},
                    {"id": "omega_3", "weight": 1.0, "admissible": True,
                     "state": {"north_road": "open", "south_road": "closed"}},
                    {"id": "omega_4", "weight": 3.0, "admissible": True,
                     "state": {"north_road": "closed", "south_road": "closed"}},
                    {"id": "omega_5", "weight": 2.0, "admissible": False,
                     "reason": "closes the north road under a south wind; ruled out by the "
                               "declared spread physics",
                     "state": {"north_road": "closed", "south_road": "closed"}},
                ],
                "actions": ["assume_egress", "prepare_isolation"],
                "losses": scenario_losses,
            }
        },
        expected={
            "benchmark_id": "WG-BM-048",
            "source": "exhaustive_enumeration",
            "derivation": (
                "Four of the five worlds are admissible, with raw weights 3, 1, 1 and 3 summing "
                "to 8, so the renormalised weights are 0.375, 0.125, 0.125 and 0.375 and they sum "
                "to one. omega_5 is excluded, not down-weighted. "
                "The north road is closed in omega_2 and omega_4, so its marginal closure "
                "probability is 0.125 + 0.375 = 0.5, and by symmetry so is the south road's. "
                "Both are closed in omega_4 alone, so the joint probability of losing all egress "
                "is 0.375 - read off the ensemble, not reconstructed. Multiplying the marginals "
                "gives 0.5 * 0.5 = 0.25, understating it by a factor of 1.5. "
                "Assuming egress costs 140 when both roads are closed and nothing otherwise, so "
                "its expected loss is 0.375 * 140 = 52.5, worse than the flat 40 of preparing for "
                "isolation. Under the independence-implied distribution, which puts 0.25 on each "
                "of the four joint states, the expected loss of assuming egress is 0.25 * 140 = "
                "35, better than 40, and the recommendation flips. "
                "Had omega_5 been included in the normalisation, the weights would be 0.3, 0.1, "
                "0.1, 0.3, 0.2, the joint closure probability 0.5 and the expected loss of "
                "assuming egress 70 - a different answer again."
            ),
            "results": {
                "model": "scenario_ensemble",
                "declared_scenarios": 5,
                "admissible_scenarios": ["omega_1", "omega_2", "omega_3", "omega_4"],
                "excluded_scenarios": ["omega_5"],
                "normalised_weights": {
                    "omega_1": 0.375, "omega_2": 0.125, "omega_3": 0.125, "omega_4": 0.375,
                },
                "weight_sum": 1.0,
                "marginal_closure_probability": {"north_road": 0.5, "south_road": 0.5},
                "joint_all_closed_probability": 0.375,
                "joint_under_independence": 0.25,
                "independence_error_factor": 1.5,
                "expected_loss": {"assume_egress": 52.5, "prepare_isolation": 40.0},
                "best_action": "prepare_isolation",
                "expected_loss_under_independence": {
                    "assume_egress": 35.0, "prepare_isolation": 40.0,
                },
                "best_action_under_independence": "assume_egress",
            },
            "invariants": [
                {
                    "expression": "abs(r['weight_sum'] - 1.0) < 1e-12",
                    "description": "the admissible weights form a probability distribution",
                },
                {
                    "expression": "'omega_5' not in r['normalised_weights']",
                    "description": "the inadmissible world carries no weight at all",
                },
                {
                    "expression": "r['best_action'] != r['best_action_under_independence']",
                    "description": "multiplying the marginals reverses the recommendation",
                },
            ],
        },
        readme="""
# WG-BM-048 (K5) — Coherent scenario ensemble

## Scenario

Five worlds from an ensemble generator, describing the joint state of two roads.

| World | north | south | raw weight | admissible |
|---|---|---|---|---|
| `omega_1` | open | open | 3 | yes |
| `omega_2` | closed | open | 1 | yes |
| `omega_3` | open | closed | 1 | yes |
| `omega_4` | closed | closed | 3 | yes |
| `omega_5` | closed | closed | 2 | **no** — closes the north road under a south wind, which the declared physics forbids |

Declared semantics: **weights are unnormalised and are renormalised over the
admissible set only.**

## Derivation

```
admissible raw total = 3 + 1 + 1 + 3 = 8
weights = 0.375, 0.125, 0.125, 0.375        sum = 1
```

`omega_5` is **excluded**, not down-weighted, and it is flagged in the input
rather than silently deleted so that the exclusion is auditable.

```
P(north closed) = w2 + w4 = 0.125 + 0.375 = 0.5
P(south closed) = w3 + w4 = 0.125 + 0.375 = 0.5
P(both closed)  = w4                      = 0.375     <- read off the ensemble
product of marginals = 0.5 * 0.5          = 0.25      <- understates by 1.5x
```

Losses: `assume_egress` costs 140 when both roads are closed and 0 otherwise;
`prepare_isolation` costs 40 whatever happens.

```
E[assume_egress]     = 0.375 * 140 = 52.5
E[prepare_isolation] = 40                     ->  prepare
```

Under the independence-implied distribution (0.25 on each joint state):

```
E[assume_egress] = 0.25 * 140 = 35            ->  assume egress
```

**The recommendation flips.**

## Three ways to get this wrong, all pinned

1. **Multiply the marginals.** Both marginals are correct and their product is
   not the joint. The error is invisible from the marginals alone.
2. **Renormalise over everything.** Including `omega_5` gives weights
   0.3/0.1/0.1/0.3/0.2, a joint closure probability of 0.5, and an expected loss
   of 70 for `assume_egress` — a third distinct answer from the same file.
3. **Drop the inadmissible world silently.** Then nobody can tell whether the
   generator produced four worlds or five, and the ensemble's provenance is
   unrecoverable. The admissibility flag and the `excluded_scenarios` field
   exist so that the exclusion is a reported fact.

## Expected

| Quantity | Value |
|---|---|
| normalised weights | 0.375 / 0.125 / 0.125 / 0.375 |
| excluded | `omega_5` |
| `P(both closed)` | **0.375** |
| under independence | 0.25 |
| best action | `prepare_isolation` |
| best action under independence | `assume_egress` |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
