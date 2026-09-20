"""Author K6-K15: posteriors, the value of observations, and the ways an
observation can mislead (WG-BM-049..058).

Second half of the K family; ``author_probabilistic_forecast.py`` covers K1-K5.
"""

from __future__ import annotations

import math

from common import report, write_benchmark

SCRIPT = "author_bayesian_inference.py"
TOL = {"default": 1.0e-12}


def bits(p: float) -> float:
    """Binary entropy in bits."""
    return -sum(q * math.log2(q) for q in (p, 1.0 - p) if q > 0.0)


# ---------------------------------------------------------------- shared setups
EVAC_LOSS = {
    "evacuate": {"H_reaches": 0.0, "H_misses": 5.0},
    "stay": {"H_reaches": 20.0, "H_misses": 0.0},
}
EVAC_PSTAR = 5.0 / (5.0 + 20.0)

ROUTE_HYPOTHESES = [
    {"id": "omega_north", "prior": 0.5},
    {"id": "omega_south", "prior": 0.5},
]
ROUTE_LOSS = {
    "via_north": {"omega_north": 90.0, "omega_south": 0.0},
    "via_south": {"omega_north": 0.0, "omega_south": 90.0},
    "shelter": {"omega_north": 40.0, "omega_south": 40.0},
}
ROUTE_PARTITION = [
    {"p_from": 0.0, "p_to": 40.0 / 90.0, "action": "via_north"},
    {"p_from": 40.0 / 90.0, "p_to": 50.0 / 90.0, "action": "shelter"},
    {"p_from": 50.0 / 90.0, "p_to": 1.0, "action": "via_south"},
]

HAZARD_LOSS = {
    "proceed": {"H_dangerous": 90.0, "H_safe": 0.0},
    "divert": {"H_dangerous": 0.0, "H_safe": 10.0},
}
HAZARD_PSTAR = 10.0 / (10.0 + 90.0)

# K6
K6_POST_Z1 = (0.1 * 0.9) / (0.1 * 0.9 + 0.9 * 0.2)
K6_POST_Z0 = (0.1 * 0.1) / (0.1 * 0.1 + 0.9 * 0.8)
K6_MI = bits(0.1) - (0.27 * bits(K6_POST_Z1) + 0.73 * bits(K6_POST_Z0))
# K7
K7_POST_Z1 = (0.05 * 0.6) / (0.05 * 0.6 + 0.95 * 0.3)
K7_POST_Z0 = (0.05 * 0.4) / (0.05 * 0.4 + 0.95 * 0.7)
K7_MI = bits(0.05) - (0.315 * bits(K7_POST_Z1) + 0.685 * bits(K7_POST_Z0))
# K8 / K9 / K10
K8_MI = bits(0.5) - bits(0.8)
K10_WEAK_MI = bits(0.5) - bits(0.7)

# K11 / K12: two sensors that share an error mode, and the degenerate duplicate
K11_JOINT = {
    "H_dangerous": {"1,1": 0.76, "1,0": 0.04, "0,1": 0.04, "0,0": 0.16},
    "H_safe": {"1,1": 0.16, "1,0": 0.04, "0,1": 0.04, "0,0": 0.76},
}
K11_INDEPENDENT = {
    "H_dangerous": {"1,1": 0.64, "1,0": 0.16, "0,1": 0.16, "0,0": 0.04},
    "H_safe": {"1,1": 0.04, "1,0": 0.16, "0,1": 0.16, "0,0": 0.64},
}
K11_POST_00 = 0.16 / (0.16 + 0.76)
K11_POST_00_NAIVE = 0.04 / (0.04 + 0.64)
K11_POST_11 = 0.76 / (0.76 + 0.16)
K11_MI = 1.0 - (0.92 * bits(K11_POST_11) + 0.08 * 1.0)
K12_POST_00 = 0.2 / (0.2 + 0.8)
K12_MI = 1.0 - bits(0.8)

# K13: missingness caused by the hazard
K13_POST_MISSING = (0.05 * 0.6) / (0.05 * 0.6 + 0.95 * 0.05)
K13_POST_RECEIVED = (0.05 * 0.4) / (0.05 * 0.4 + 0.95 * 0.95)
K13_MI = bits(0.05) - (0.0775 * bits(K13_POST_MISSING) + 0.9225 * bits(K13_POST_RECEIVED))

# K14 / K15: one detector, two base rates
DETECTOR = {
    "H_fire": {"detect": 0.7, "no_detect": 0.3},
    "H_no_fire": {"detect": 0.05, "no_detect": 0.95},
}
K14_POST_NO_DETECT = (0.2 * 0.3) / (0.2 * 0.3 + 0.8 * 0.95)
K14_POST_DETECT = (0.2 * 0.7) / (0.2 * 0.7 + 0.8 * 0.05)
K14_MI = bits(0.2) - (0.18 * bits(K14_POST_DETECT) + 0.82 * bits(K14_POST_NO_DETECT))
K15_POST_DETECT = (0.02 * 0.7) / (0.02 * 0.7 + 0.98 * 0.05)
K15_POST_NO_DETECT = (0.02 * 0.3) / (0.02 * 0.3 + 0.98 * 0.95)
K15_MI = bits(0.02) - (0.063 * bits(K15_POST_DETECT) + 0.937 * bits(K15_POST_NO_DETECT))
K15_LOSS = {
    "monitor": {"H_fire": 200.0, "H_no_fire": 0.0},
    "divert_traffic": {"H_fire": 30.0, "H_no_fire": 6.0},
    "full_evacuation": {"H_fire": 0.0, "H_no_fire": 40.0},
}


def route_observation(name: str, strength: float, availability: float | None) -> dict:
    """An imperfect bearing sensor: P(signal_north | omega_north) = strength."""
    return {
        "id": name,
        "acquisition_time_min": 5.0,
        "availability_time_min": availability,
        "outcomes": ["signal_north", "signal_south"],
        "likelihood": {
            "omega_north": {"signal_north": strength, "signal_south": 1.0 - strength},
            "omega_south": {"signal_north": 1.0 - strength, "signal_south": strength},
        },
    }


def main() -> None:
    written = []

    # ------------------------------------------------------------------ K6
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-049_K6_posterior_update",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-049",
            "label": "K6",
            "title": "Observation, posterior, decision: the canonical update",
            "category": "probabilistic_forecast",
            "difficulty": "basic",
            "purpose": "Two hypotheses, known priors, known likelihoods. Bayes' rule moves the "
                       "belief across the decision threshold and the action changes from stay to "
                       "evacuate.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "finite_hypothesis_space": True,
                "likelihoods_known_exactly": True,
                "decision_rule": "minimise posterior expected loss",
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "prior": "P(H_reaches) = 0.1",
                "likelihood": "P(anomaly | reaches) = 0.9, P(anomaly | misses) = 0.2",
                "posterior": "P(H_reaches | anomaly) = 1/3",
                "decision_threshold": EVAC_PSTAR,
                "loss_matrix": "evacuate 0/5, stay 20/0",
            },
            "expected_behavior": {
                "prior_action": "stay",
                "decision_threshold_probability": EVAC_PSTAR,
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["posterior_not_used_for_decision", "likelihood_discarded", "bayes_rule_error"],
            "mutations_expected_to_fail": [
                "posterior_replaced_by_prior",
                "ignore_observation_likelihood",
            ],
            "hand_checkable": True,
            "notes": "This is the reference case for the whole observation-to-decision chain. "
                     "If a system fails here, nothing downstream in the K family is diagnostic.",
        },
        inputs={
            "probabilistic": {
                "description": "Will the fire reach the settlement? Prior 0.1. A satellite pass "
                               "reports a thermal anomaly on the intervening ridge, which is nine "
                               "times more likely if the fire is going to reach than if it is not.",
                "model": "bayes_decision",
                "hypotheses": [
                    {"id": "H_reaches", "prior": 0.1},
                    {"id": "H_misses", "prior": 0.9},
                ],
                "hazard_hypothesis": "H_reaches",
                "actions": ["evacuate", "stay"],
                "loss": EVAC_LOSS,
                "decision_deadline_min": 60.0,
                "observations": [
                    {
                        "id": "ridge_anomaly",
                        "acquisition_time_min": 5.0,
                        "availability_time_min": 12.0,
                        "outcomes": ["anomaly", "no_anomaly"],
                        "likelihood": {
                            "H_reaches": {"anomaly": 0.9, "no_anomaly": 0.1},
                            "H_misses": {"anomaly": 0.2, "no_anomaly": 0.8},
                        },
                        "realised": "anomaly",
                    }
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-049",
            "source": "closed_form",
            "derivation": (
                "The decision threshold comes from the loss matrix: evacuating costs 5 if the "
                "fire misses and nothing if it reaches, staying costs 20 if it reaches and "
                "nothing if it misses, so p* = 5 / (5 + 20) = 0.2. "
                "Under the prior of 0.1 the expected loss of staying is 0.1 * 20 = 2 against "
                "0.9 * 5 = 4.5 for evacuating, so the prior-optimal action is to stay. "
                "Bayes: P(anomaly) = 0.1 * 0.9 + 0.9 * 0.2 = 0.09 + 0.18 = 0.27, so "
                "P(reaches | anomaly) = 0.09 / 0.27 = 1/3 = 0.3333333333333333, which is above "
                "p*, and the action becomes evacuate at a posterior expected loss of "
                "(2/3) * 5 = 10/3. On the other branch P(no anomaly) = 0.01 + 0.72 = 0.73 and "
                "P(reaches | no anomaly) = 0.01 / 0.73 = 0.0136986301369863, well below p*, so "
                "the action stays. "
                "EVSI = 2 - (0.27 * 10/3 + 0.73 * 0.2739726027397260) = 2 - (0.9 + 0.2) = 0.9. "
                "Perfect information would be worth 2 - 0 = 2, since each hypothesis has a "
                "zero-loss action. The mutual information of the observation is 0.1448 bits."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.1,
                "prior_action": "stay",
                "prior_expected_loss": 2.0,
                "decision_threshold_probability": EVAC_PSTAR,
                "clairvoyant_expected_loss": 0.0,
                "evpi": 2.0,
                "observations": {
                    "ridge_anomaly": {
                        "available_before_deadline": True,
                        "evsi_statistical": 0.9,
                        "evsi_operational": 0.9,
                        "information_gain_bits": K6_MI,
                        "changes_action": True,
                        "realised_outcome": "anomaly",
                        "realised_posterior_hazard": K6_POST_Z1,
                        "realised_action": "evacuate",
                        "posterior_hazard_by_outcome": {
                            "anomaly": K6_POST_Z1,
                            "no_anomaly": K6_POST_Z0,
                        },
                        "action_by_outcome": {"anomaly": "evacuate", "no_anomaly": "stay"},
                    }
                },
            },
            "invariants": [
                {
                    "expression": "abs(r['observations']['ridge_anomaly']['realised_posterior_hazard'] - 1.0 / 3.0) < 1e-12",
                    "description": "the posterior is exactly one third",
                },
                {
                    "expression": "r['prior_action'] != r['observations']['ridge_anomaly']['realised_action']",
                    "description": "the observation changes the action",
                },
                {
                    "expression": "r['observations']['ridge_anomaly']['realised_posterior_hazard'] > r['decision_threshold_probability']",
                    "description": "and it changes it by crossing the loss-derived threshold",
                },
            ],
        },
        readme=f"""
# WG-BM-049 (K6) — Posterior update

## Scenario

Will the fire reach the settlement?

```
prior:  P(H_reaches) = 0.1        P(H_misses) = 0.9
```

A satellite pass reports a thermal anomaly on the intervening ridge:

```
P(anomaly | reaches) = 0.9        P(anomaly | misses) = 0.2
```

| | fire reaches | fire misses |
|---|---|---|
| `evacuate` | 0 | 5 |
| `stay` | 20 | 0 |

## Derivation

**Threshold from the loss matrix.**

```
p* = L_conservative / (L_conservative + L_failure) = 5 / (5 + 20) = 0.2
```

**Prior decision.** `E[stay] = 0.1 * 20 = 2` against `E[evacuate] = 0.9 * 5 = 4.5`
→ **stay**.

**Bayes.**

```
P(anomaly) = 0.1 * 0.9 + 0.9 * 0.2 = 0.09 + 0.18 = 0.27
P(reaches | anomaly) = 0.09 / 0.27 = 1/3 = 0.3333...        > p*  ->  evacuate

P(no anomaly) = 0.01 + 0.72 = 0.73
P(reaches | no anomaly) = 0.01 / 0.73 = 0.01370...          < p*  ->  stay
```

**Value.**

```
EVSI = 2 - (0.27 * 10/3 + 0.73 * 0.27397...) = 2 - (0.9 + 0.2) = 0.9
EVPI = 2 - 0 = 2
mutual information = {K6_MI:.10f} bits
```

## The chain this pins

```
observation  ->  likelihood  ->  posterior  ->  expected loss  ->  action
```

Every arrow is somewhere a system can break, and the four failure points are
different bugs with different signatures:

* **the likelihood is not used** — the posterior equals the prior (1/3 becomes
  0.1) and the action never changes;
* **the posterior is computed and then not used** — the reported posterior is
  correct and the action is still `stay`;
* **the normalisation is skipped** — `0.1 * 0.9 = 0.09` is reported as the
  posterior, which is below `p*`, so the action is wrong while the number looks
  plausible;
* **the threshold is not derived from the loss** — at 1/3 a half-probability
  rule also says stay.

The first two are injected as `ignore_observation_likelihood` and
`posterior_replaced_by_prior`, and this benchmark is the declared detector for
both. They are distinguishable in the result document: the first changes the
reported posterior, the second does not.

## Expected

| Quantity | Value |
|---|---|
| `p*` | 0.2 |
| `P(reaches \\| anomaly)` | **1/3** |
| `P(reaches \\| no anomaly)` | 0.013699 |
| prior action → posterior action | `stay` → **`evacuate`** |
| EVSI / EVPI | 0.9 / 2.0 |
""",
    ))

    # ------------------------------------------------------------------ K7
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-050_K7_information_without_decision_value",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-050",
            "label": "K7",
            "title": "The posterior moves, the action does not: EVSI is exactly zero",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "An observation with positive mutual information and zero decision value. "
                       "More information does not necessarily change or improve a decision.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "finite_hypothesis_space": True,
                "both_branches_evaluated": True,
                "decision_rule": "minimise posterior expected loss",
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "prior": "P(H_reaches) = 0.05",
                "likelihood": "P(haze | reaches) = 0.6, P(haze | misses) = 0.3",
                "decision_threshold": EVAC_PSTAR,
                "expected_value": "EVSI = 0 with mutual information 0.0131 bits",
            },
            "expected_behavior": {
                "observations": {"valley_haze": {"evsi_statistical": 0.0, "changes_action": False}},
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": [
                "information_gain_mistaken_for_decision_value",
                "observation_assumed_useful",
            ],
            "mutations_expected_to_fail": ["choose_by_information_gain"],
            "hand_checkable": True,
            "notes": "The most load-bearing benchmark in the K family for governance: it is the "
                     "counterexample to 'we are uncertain, therefore we should observe more'.",
        },
        inputs={
            "probabilistic": {
                "description": "The same evacuation decision with a lower prior and a weaker "
                               "observation: valley haze, twice as likely if the fire is going to "
                               "reach the settlement as if it is not. It is genuinely "
                               "informative and it cannot change what anyone does.",
                "model": "bayes_decision",
                "hypotheses": [
                    {"id": "H_reaches", "prior": 0.05},
                    {"id": "H_misses", "prior": 0.95},
                ],
                "hazard_hypothesis": "H_reaches",
                "actions": ["evacuate", "stay"],
                "loss": EVAC_LOSS,
                "decision_deadline_min": 60.0,
                "observations": [
                    {
                        "id": "valley_haze",
                        "acquisition_time_min": 5.0,
                        "availability_time_min": 10.0,
                        "outcomes": ["haze", "no_haze"],
                        "likelihood": {
                            "H_reaches": {"haze": 0.6, "no_haze": 0.4},
                            "H_misses": {"haze": 0.3, "no_haze": 0.7},
                        },
                        "realised": "haze",
                    }
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-050",
            "source": "closed_form",
            "derivation": (
                "The threshold is again p* = 0.2. Under the prior of 0.05 the expected loss of "
                "staying is 1.0 against 4.75 for evacuating, so the prior action is to stay. "
                "P(haze) = 0.05 * 0.6 + 0.95 * 0.3 = 0.03 + 0.285 = 0.315 and "
                "P(reaches | haze) = 0.03 / 0.315 = 0.09523809523809525. "
                "P(no haze) = 0.02 + 0.665 = 0.685 and "
                "P(reaches | no haze) = 0.02 / 0.685 = 0.029197080291970802. "
                "Both posteriors are below 0.2, so the action is to stay on both branches and "
                "the expected loss after the observation is "
                "0.315 * 1.9047619047619047 + 0.685 * 0.5839416058394161 = 0.6 + 0.4 = 1.0, "
                "identical to the prior expected loss. EVSI is therefore exactly 0. "
                "The observation is nonetheless informative: the belief moves from 0.05 to either "
                "0.0952 or 0.0292, and the mutual information is 0.0130871530523989 bits, which "
                "is strictly positive. "
                "Perfect information would still be worth 1.0, so the zero is a property of this "
                "particular observation and not of the decision problem."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.05,
                "prior_action": "stay",
                "prior_expected_loss": 1.0,
                "decision_threshold_probability": EVAC_PSTAR,
                "clairvoyant_expected_loss": 0.0,
                "evpi": 1.0,
                "observations": {
                    "valley_haze": {
                        "evsi_statistical": 0.0,
                        "evsi_operational": 0.0,
                        "information_gain_bits": K7_MI,
                        "changes_action": False,
                        "realised_posterior_hazard": K7_POST_Z1,
                        "realised_action": "stay",
                        "posterior_hazard_by_outcome": {
                            "haze": K7_POST_Z1,
                            "no_haze": K7_POST_Z0,
                        },
                        "action_by_outcome": {"haze": "stay", "no_haze": "stay"},
                    }
                },
                "observations_worth_acquiring": [],
                "recommended_observation": None,
            },
            "invariants": [
                {
                    "expression": "r['observations']['valley_haze']['information_gain_bits'] > 0",
                    "description": "the observation carries information",
                },
                {
                    "expression": "r['observations']['valley_haze']['evsi_statistical'] == 0.0",
                    "description": "and its decision value is exactly zero",
                },
                {
                    "expression": "len(set(r['observations']['valley_haze']['action_by_outcome'].values())) == 1",
                    "description": "the same action is optimal on every branch",
                },
                {
                    "expression": "r['evpi'] > 0",
                    "description": "perfect information would still help, so the zero belongs to this observation",
                },
                {
                    "expression": "r['observations_worth_acquiring'] == []",
                    "description": "and nothing here is worth acquiring",
                },
            ],
        },
        readme=f"""
# WG-BM-050 (K7) — Information with no decision value

## Scenario

The WG-BM-049 decision (`p* = 0.2`) with a lower prior and a weaker observation.

```
prior: P(H_reaches) = 0.05
P(haze | reaches) = 0.6      P(haze | misses) = 0.3
```

Valley haze is **twice as likely** if the fire is going to reach the settlement.
It is a real signal.

## Derivation

```
prior action: E[stay] = 0.05 * 20 = 1.0  vs  E[evacuate] = 0.95 * 5 = 4.75   ->  stay

P(haze)    = 0.03 + 0.285 = 0.315     P(reaches | haze)    = 0.03/0.315 = {K7_POST_Z1:.10f}
P(no haze) = 0.02 + 0.665 = 0.685     P(reaches | no haze) = 0.02/0.685 = {K7_POST_Z0:.10f}
```

Both posteriors are **below `p* = 0.2`**, so the action is `stay` on both
branches:

```
expected loss after observing = 0.315 * 1.90476 + 0.685 * 0.58394 = 0.6 + 0.4 = 1.0
EVSI = 1.0 - 1.0 = 0        exactly
```

Meanwhile:

```
mutual information I(H;Z) = {K7_MI:.10f} bits   >  0
EVPI                      = 1.0                    >  0
```

## Why this benchmark matters more than its size suggests

Three quantities are positive, zero and positive respectively, and they are
routinely treated as the same quantity:

| Quantity | Value | Means |
|---|---|---|
| mutual information | **0.0131 bits** | the observation tells you something |
| EVSI | **0** | it cannot change what you do |
| EVPI | **1.0** | knowing the truth *could* change what you do |

The governance consequence is direct. "We are uncertain, therefore we should
gather more information" is not valid. The correct question is whether the
information could move the belief **across a decision boundary**, and here it
provably cannot: the observation's strongest possible branch leaves the belief
at 0.095, less than half of `p*`.

Note the third row. The zero is a property of *this observation*, not of the
decision — perfect information would be worth 1.0. So the right conclusion is
not "stop looking" but "this particular sensor cannot settle it, and tasking it
is spending a pass for nothing".

The `choose_by_information_gain` mutation recommends acquisition on positive
entropy reduction; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| posterior after haze / no haze | 0.0952 / 0.0292 |
| action on both branches | `stay` |
| EVSI | **0** |
| mutual information | {K7_MI:.6f} bits |
| EVPI | 1.0 |
""",
    ))

    # ------------------------------------------------------------------ K8
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-051_K8_valuable_information",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-051",
            "label": "K8",
            "title": "Exact expected value of sample information: 22 against an EVPI of 40",
            "category": "probabilistic_forecast",
            "difficulty": "intermediate",
            "purpose": "Two worlds needing opposite actions. The prior-optimal action is to "
                       "shelter at a cost of 40; an imperfect bearing sensor reduces that to 18, "
                       "so EVSI is 22. Computed by enumeration, not simulation.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "finite_hypothesis_space": True,
                "finite_observation_space": True,
                "evsi_by_enumeration": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "prior": "P(omega_north) = 0.5",
                "likelihood": "P(signal_north | omega_north) = 0.8",
                "expected_value": "EVSI = 22, EVPI = 40",
            },
            "expected_behavior": {
                "prior_action": "shelter",
                "evsi_statistical_by_observation": {"bearing_sensor": 22.0},
                "evpi": 40.0,
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["evsi_miscomputed", "posterior_not_used_for_decision"],
            "mutations_expected_to_fail": [
                "posterior_replaced_by_prior",
                "ignore_observation_likelihood",
            ],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "The fire approaches from the north or from the south, equally "
                               "likely. Evacuating along the road on the fire's side is "
                               "disastrous; sheltering is mediocre either way. A bearing sensor "
                               "is right four times out of five.",
                "model": "bayes_decision",
                "hypotheses": ROUTE_HYPOTHESES,
                "hazard_hypothesis": "omega_north",
                "actions": ["via_north", "via_south", "shelter"],
                "loss": ROUTE_LOSS,
                "decision_deadline_min": 10.0,
                "observations": [route_observation("bearing_sensor", 0.8, 8.0)],
            }
        },
        expected={
            "benchmark_id": "WG-BM-051",
            "source": "closed_form",
            "derivation": (
                "Under the prior of 0.5 the expected losses are 45 for each evacuation route and "
                "40 for sheltering, so the prior-optimal action is to shelter at 40. "
                "P(signal_north) = 0.5 * 0.8 + 0.5 * 0.2 = 0.5, and by Bayes "
                "P(omega_north | signal_north) = 0.4 / 0.5 = 0.8. At that belief the expected "
                "losses are 72 for the northern road, 18 for the southern road and 40 for "
                "sheltering, so the action is to evacuate south at 18. The other branch is the "
                "mirror image: P(omega_north | signal_south) = 0.1 / 0.5 = 0.2, and the action is "
                "to evacuate north at 18. "
                "EVSI = 40 - (0.5 * 18 + 0.5 * 18) = 40 - 18 = 22. "
                "Perfect information would allow the correct road in each world at zero loss, so "
                "EVPI = 40 - 0 = 40 and the sensor captures 55 per cent of it. "
                "The optimal action as a function of P(omega_north) has three segments: the "
                "northern road below 4/9, sheltering between 4/9 and 5/9, and the southern road "
                "above 5/9 - so there is no single threshold to quote, which is itself worth "
                "pinning."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.5,
                "prior_action": "shelter",
                "prior_expected_loss": 40.0,
                "decision_threshold_probability": None,
                "action_partition": ROUTE_PARTITION,
                "clairvoyant_expected_loss": 0.0,
                "evpi": 40.0,
                "evsi_statistical_by_observation": {"bearing_sensor": 22.0},
                "evsi_operational_by_observation": {"bearing_sensor": 22.0},
                "observations": {
                    "bearing_sensor": {
                        "available_before_deadline": True,
                        "evsi_statistical": 22.0,
                        "evsi_operational": 22.0,
                        "information_gain_bits": K8_MI,
                        "changes_action": True,
                        "posterior_hazard_by_outcome": {
                            "signal_north": 0.8,
                            "signal_south": 0.2,
                        },
                        "action_by_outcome": {
                            "signal_north": "via_south",
                            "signal_south": "via_north",
                        },
                    }
                },
            },
            "invariants": [
                {
                    "expression": "r['observations']['bearing_sensor']['evsi_statistical'] < r['evpi']",
                    "description": "an imperfect observation is worth less than perfect information",
                },
                {
                    "expression": "len(set(r['observations']['bearing_sensor']['action_by_outcome'].values())) == 2",
                    "description": "the two branches call for different actions",
                },
                {
                    "expression": "len(r['action_partition']) == 3",
                    "description": "three actions means three optimality regions, not one threshold",
                },
            ],
        },
        readme=f"""
# WG-BM-051 (K8) — Valuable information

## Scenario

The fire approaches from the north or the south, equally likely. Evacuating
along the road on the fire's side is disastrous.

| | `omega_north` | `omega_south` |
|---|---|---|
| `via_north` | 90 | 0 |
| `via_south` | 0 | 90 |
| `shelter` | 40 | 40 |

A bearing sensor is right four times in five:
`P(signal_north | omega_north) = 0.8`.

## Derivation

**Prior.** `E[via_north] = E[via_south] = 45`, `E[shelter] = 40` → **shelter**,
expected loss 40.

**Posterior.**

```
P(signal_north) = 0.5 * 0.8 + 0.5 * 0.2 = 0.5
P(omega_north | signal_north) = 0.4 / 0.5 = 0.8
    E[via_north] = 72   E[via_south] = 18   E[shelter] = 40   ->  via_south, 18

P(omega_north | signal_south) = 0.1 / 0.5 = 0.2
    mirror image                                             ->  via_north, 18
```

**Value.**

```
EVSI = 40 - (0.5 * 18 + 0.5 * 18) = 40 - 18 = 22
EVPI = 40 - 0                                  = 40
the sensor captures 22/40 = 55% of the available value
```

Every number is a finite sum over two hypotheses and two outcomes. **No
simulation is required or permitted**: a Monte Carlo estimate of 22 would be an
approximation to a quantity that can be written down.

## Three optimality regions, not one threshold

With three actions the optimal choice as a function of `p = P(omega_north)` is
the lower envelope of three lines:

```
p < 4/9        via_north
4/9 < p < 5/9  shelter
p > 5/9        via_south
```

So "the threshold" does not exist here, and a system that reports one has
flattened a three-way decision into a two-way one. The benchmark pins the whole
partition.

## Expected

| Quantity | Value |
|---|---|
| prior action | `shelter`, loss 40 |
| posterior on `signal_north` | 0.8 → `via_south`, loss 18 |
| posterior on `signal_south` | 0.2 → `via_north`, loss 18 |
| **EVSI** | **22** |
| EVPI | 40 |
| mutual information | {K8_MI:.6f} bits |
""",
    ))

    # ------------------------------------------------------------------ K9
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-052_K9_information_arrives_too_late",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-052",
            "label": "K9",
            "title": "Statistical value 22, operational value 0: the sensor reports at minute 12",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "WG-BM-051 with acquisition at minute 5, availability at minute 12 and a "
                       "decision deadline at minute 10. The information exists and cannot be used.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "acquisition_time_min": 5,
                "availability_time_min": 12,
                "decision_deadline_min": 10,
                "no_partial_early_release": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "observation_time_min": 5.0,
                "availability_time_min": 12.0,
                "decision_deadline_min": 10.0,
                "expected_value": "EVSI 22 statistical, 0 operational",
            },
            "expected_behavior": {
                "evsi_statistical_by_observation": {"bearing_sensor": 22.0},
                "evsi_operational_by_observation": {"bearing_sensor": 0.0},
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["observation_timeliness_ignored", "evsi_mistaken_for_operational_value"],
            "mutations_expected_to_fail": ["ignore_availability_time"],
            "hand_checkable": True,
            "notes": "Canonical timing case for the OSSE: acquisition time is not availability "
                     "time, and availability time is what a decision can use.",
        },
        inputs={
            "probabilistic": {
                "description": "Identical to WG-BM-051 except that the bearing sensor's product "
                               "is not available until minute 12, and the evacuation decision "
                               "must be taken by minute 10.",
                "model": "bayes_decision",
                "hypotheses": ROUTE_HYPOTHESES,
                "hazard_hypothesis": "omega_north",
                "actions": ["via_north", "via_south", "shelter"],
                "loss": ROUTE_LOSS,
                "decision_deadline_min": 10.0,
                "observations": [route_observation("bearing_sensor", 0.8, 12.0)],
            }
        },
        expected={
            "benchmark_id": "WG-BM-052",
            "source": "closed_form",
            "derivation": (
                "The decision problem is identical to WG-BM-051, so the statistical quantities "
                "are unchanged: the prior action is to shelter at 40, each branch gives 18, and "
                "EVSI is 22 with an EVPI of 40. "
                "Only the timing differs. The sensor acquires at minute 5 and its product is "
                "available at minute 12, five minutes after the decision must be taken at minute "
                "10, so no policy can condition on it. The operational value of the observation "
                "is therefore 0, and the action remains the prior-optimal shelter. "
                "The gap between 22 and 0 is entirely a property of the observing system's "
                "latency, not of its accuracy: the same sensor with the same likelihoods is worth "
                "22 in WG-BM-051 and nothing here."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_action": "shelter",
                "prior_expected_loss": 40.0,
                "evpi": 40.0,
                "observations": {
                    "bearing_sensor": {
                        "acquisition_time_min": 5.0,
                        "availability_time_min": 12.0,
                        "available_before_deadline": False,
                        "evsi_statistical": 22.0,
                        "evsi_operational": 0.0,
                        "information_gain_bits": K8_MI,
                    }
                },
                "evsi_statistical_by_observation": {"bearing_sensor": 22.0},
                "evsi_operational_by_observation": {"bearing_sensor": 0.0},
            },
            "invariants": [
                {
                    "expression": "r['observations']['bearing_sensor']['evsi_statistical'] > 0",
                    "description": "the information exists",
                },
                {
                    "expression": "r['observations']['bearing_sensor']['evsi_operational'] == 0.0",
                    "description": "and no decision can use it",
                },
                {
                    "expression": "r['observations']['bearing_sensor']['available_before_deadline'] is False",
                    "description": "because it arrives after the deadline, which is reported explicitly",
                },
            ],
        },
        readme="""
# WG-BM-052 (K9) — Information arrives too late

## Scenario

**Identical to WG-BM-051** except for three timestamps:

```
acquisition time    =  5 min      the sensor takes the measurement
availability time   = 12 min      the product reaches the decision maker
decision deadline   = 10 min      after this the evacuation cannot start
```

## Derivation

The decision problem has not changed, so neither have the statistical
quantities:

```
prior action  = shelter, expected loss 40
each branch   = 18
EVSI          = 22
EVPI          = 40
```

The timing has changed, and the product arrives **two minutes after the last
moment it could matter**. No policy can condition on it.

```
EVSI, statistical  = 22
EVSI, operational  =  0
action             = shelter, the prior-optimal one
```

## The distinction this establishes for the OSSE

Three times are routinely collapsed into one, and they are different:

| Time | Meaning | Consequence of confusing it |
|---|---|---|
| acquisition | when the sensor looked | an evaluation dated here leaks the future (WG-BM-014) |
| **availability** | when the product could be used | the only one a decision can consume |
| deadline | when the action must be taken | a forecast after it has zero operational value |

An observing-system experiment that scores sensors on statistical information —
mutual information, EVSI, error reduction — will rank this sensor at 22 and
recommend building more of them. Its operational contribution is zero, and it
would remain zero if its accuracy were doubled.

The corollary is a design rule: the quantity to maximise is not information, and
not information per unit cost, but **information available before the deadline**.
Latency is a feasibility constraint, not a performance attribute.

The `ignore_availability_time` mutation sets the operational value equal to the
statistical one; this benchmark is its declared detector, together with
WG-BM-053, which shows the ranking consequence.

## Expected

| Quantity | Value |
|---|---|
| EVSI, statistical | 22 |
| EVSI, operational | **0** |
| available before the deadline | `false` |
| action taken | `shelter` (unchanged from the prior) |
""",
    ))

    # ------------------------------------------------------------------ K10
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-053_K10_weaker_but_timely_wins",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-053",
            "label": "K10",
            "title": "A weak timely sensor beats a perfect late one, 13 to 0",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "Two candidate observations on the same decision. Ranked by information "
                       "the perfect late sensor wins; ranked by operational value the weak early "
                       "one does. Quality and timing must be evaluated jointly.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "decision_deadline_min": 10,
                "observations_evaluated_independently": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "decision_deadline_min": 10.0,
                "expected_value": "operational VOI: weak-early 13, perfect-late 0",
            },
            "expected_behavior": {
                "recommended_observation": "weak_early",
                "value_and_information_agree": False,
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": [
                "observation_timeliness_ignored",
                "information_gain_mistaken_for_decision_value",
            ],
            "mutations_expected_to_fail": [
                "ignore_availability_time",
                "choose_by_information_gain",
            ],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "The WG-BM-051 decision with two candidate observing systems. A "
                               "perfect overflight reports at minute 12; a crude ground report, "
                               "right seven times in ten, reports at minute 4. The deadline is "
                               "minute 10.",
                "model": "bayes_decision",
                "hypotheses": ROUTE_HYPOTHESES,
                "hazard_hypothesis": "omega_north",
                "actions": ["via_north", "via_south", "shelter"],
                "loss": ROUTE_LOSS,
                "decision_deadline_min": 10.0,
                "observations": [
                    route_observation("perfect_late", 1.0, 12.0),
                    route_observation("weak_early", 0.7, 4.0),
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-053",
            "source": "closed_form",
            "derivation": (
                "The prior action is to shelter at an expected loss of 40. "
                "The perfect overflight resolves the world exactly: each branch has posterior 1 "
                "or 0 and the matching road costs nothing, so its statistical EVSI is the full "
                "40 and its mutual information is 1 bit. It is available at minute 12, after the "
                "minute-10 deadline, so its operational value is 0. "
                "The crude ground report gives P(signal_north) = 0.5 * 0.7 + 0.5 * 0.3 = 0.5 and "
                "P(omega_north | signal_north) = 0.35 / 0.5 = 0.7, at which the southern road "
                "costs 0.3 * 90 = 27 against 40 for sheltering, so the action changes and the "
                "branch loss is 27; the other branch is the mirror image. Its EVSI is "
                "40 - 27 = 13 and its mutual information is 0.1187 bits. It is available at "
                "minute 4, so all 13 is operational. "
                "Ranked by information the perfect sensor wins by a factor of eight; ranked by "
                "operational value the crude one wins 13 to 0. The two rankings are opposite."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_action": "shelter",
                "prior_expected_loss": 40.0,
                "evpi": 40.0,
                "evsi_statistical_by_observation": {"perfect_late": 40.0, "weak_early": 13.0},
                "evsi_operational_by_observation": {"perfect_late": 0.0, "weak_early": 13.0},
                "information_gain_by_observation": {
                    "perfect_late": 1.0,
                    "weak_early": K10_WEAK_MI,
                },
                "ranked_by_operational_value": ["weak_early", "perfect_late"],
                "ranked_by_information_gain": ["perfect_late", "weak_early"],
                "recommended_observation": "weak_early",
                "value_and_information_agree": False,
                "observations": {
                    "perfect_late": {"available_before_deadline": False},
                    "weak_early": {
                        "available_before_deadline": True,
                        "posterior_hazard_by_outcome": {
                            "signal_north": 0.7,
                            "signal_south": 0.3,
                        },
                        "action_by_outcome": {
                            "signal_north": "via_south",
                            "signal_south": "via_north",
                        },
                    },
                },
            },
            "invariants": [
                {
                    "expression": "r['evsi_operational_by_observation']['weak_early'] > r['evsi_operational_by_observation']['perfect_late']",
                    "description": "operationally the weaker sensor is strictly better",
                },
                {
                    "expression": "r['evsi_statistical_by_observation']['perfect_late'] > r['evsi_statistical_by_observation']['weak_early']",
                    "description": "statistically it is strictly worse",
                },
                {
                    "expression": "r['ranked_by_operational_value'][0] != r['ranked_by_information_gain'][0]",
                    "description": "the two rankings disagree on the winner",
                },
            ],
        },
        readme=f"""
# WG-BM-053 (K10) — Less informative but timely beats better information

## Scenario

The WG-BM-051 decision, with two candidate observing systems and a **minute-10
deadline**:

| Observation | Accuracy | Available | Mutual information |
|---|---|---|---|
| `perfect_late` | resolves the world exactly | minute 12 | 1.000 bits |
| `weak_early` | right 7 times in 10 | **minute 4** | {K10_WEAK_MI:.4f} bits |

## Derivation

Prior action: `shelter`, expected loss 40.

**Perfect overflight.** Each branch has posterior 1 or 0, the matching road
costs nothing, so `EVSI = 40 - 0 = 40`. Available at minute 12 → **operational
value 0**.

**Crude ground report.**

```
P(signal_north) = 0.5 * 0.7 + 0.5 * 0.3 = 0.5
P(omega_north | signal_north) = 0.35 / 0.5 = 0.7
    E[via_south] = 0.3 * 90 = 27   <  E[shelter] = 40   ->  via_south
mirror image on the other branch
EVSI = 40 - 27 = 13,  all of it operational
```

| Ranking | 1st | 2nd |
|---|---|---|
| by information | `perfect_late` (1.000 bits) | `weak_early` ({K10_WEAK_MI:.4f} bits) |
| by **operational value** | **`weak_early` (13)** | `perfect_late` (0) |

**The rankings are opposite.**

## What this tests

This is the WildfireGuardian thesis in its smallest form: **information quality
and timing must be evaluated jointly, because neither dominates the other.** A
factor-of-eight advantage in information is worth nothing against eight minutes
of latency.

Two consequences for an observing-system experiment:

1. A sensor-tasking objective built on information content will task the
   overflight and get nothing. The objective has to be
   `E[loss reduction | available before the deadline]`.
2. Improving the crude sensor's accuracy and improving the overflight's latency
   are not comparable investments, and only the second can change the
   overflight's contribution from zero.

Note also what is *not* claimed: the overflight is not useless in general. It is
useless for **this decision with this deadline**. Move the deadline to minute 15
and the ranking reverses again — which is exactly why the deadline is a declared
input and not a constant.

## Expected

| Quantity | `perfect_late` | `weak_early` |
|---|---|---|
| EVSI, statistical | 40 | 13 |
| EVSI, operational | **0** | **13** |
| mutual information | 1.000 bits | {K10_WEAK_MI:.4f} bits |
| recommended | | **yes** |
""",
    ))

    # ------------------------------------------------------------------ K11
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-054_K11_correlated_observation_errors",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-054",
            "label": "K11",
            "title": "Two sensors that fail together: independence turns 0.174 into 0.059",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "Identical marginals, a strongly correlated joint. Multiplying the "
                       "marginals produces an overconfident posterior and flips the action to "
                       "the unsafe one.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "joint_likelihood_declared": True,
                "marginals_identical_to_the_independent_case": True,
                "decision_rule": "minimise posterior expected loss",
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "likelihood": "declared joint over (z1, z2); marginals 0.8 / 0.2",
                "independence_assumed": False,
                "decision_threshold": HAZARD_PSTAR,
            },
            "expected_behavior": {
                "observations": {
                    "sensor_pair": {
                        "realised_posterior_hazard": K11_POST_00,
                        "realised_action": "divert",
                        "realised_action_under_independence": "proceed",
                    }
                },
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["observation_correlation_ignored", "overconfident_posterior"],
            "mutations_expected_to_fail": ["assume_conditional_independence"],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "Two smoke sensors on the same ridge, sharing a power supply and a "
                               "sight line. Each is individually right four times in five, and "
                               "they agree far more often than independence would imply. Both "
                               "report clear.",
                "model": "bayes_decision",
                "hypotheses": [
                    {"id": "H_dangerous", "prior": 0.5},
                    {"id": "H_safe", "prior": 0.5},
                ],
                "hazard_hypothesis": "H_dangerous",
                "actions": ["proceed", "divert"],
                "loss": HAZARD_LOSS,
                "decision_deadline_min": 30.0,
                "observations": [
                    {
                        "id": "sensor_pair",
                        "acquisition_time_min": 2.0,
                        "availability_time_min": 4.0,
                        "outcomes": ["1,1", "1,0", "0,1", "0,0"],
                        "likelihood": K11_JOINT,
                        "independent_likelihood": K11_INDEPENDENT,
                        "realised": "0,0",
                        "note": "independent_likelihood is the product of the per-sensor "
                                "marginals: what a system that assumed conditional independence "
                                "would multiply.",
                    }
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-054",
            "source": "closed_form",
            "derivation": (
                "Each sensor alone reports 1 with probability 0.8 given danger and 0.2 given "
                "safety: the declared joint reproduces exactly those marginals, since "
                "0.76 + 0.04 = 0.80 and 0.16 + 0.04 = 0.20. What differs is the dependence - the "
                "two agree with probability 0.92 rather than the 0.68 that independence implies. "
                "With a prior of 0.5 and both sensors reporting clear, "
                "P(dangerous | 0,0) = 0.16 / (0.16 + 0.76) = 4/23 = 0.17391304347826086. "
                "Multiplying the marginals instead gives 0.04 and 0.64, hence "
                "0.04 / 0.68 = 1/17 = 0.058823529411764705 - three times more confident that the "
                "route is safe. In log terms the true evidence is "
                "log2(0.16/0.76) = -2.2479275134435857 bits and the independence assumption "
                "claims exactly -4 bits, because it counts two full sensors' worth of evidence "
                "from two sensors that largely repeat each other. "
                "The loss matrix gives p* = 10 / (10 + 90) = 0.1. The true posterior 0.174 is "
                "above it, so the correct action is to divert; the overconfident 0.059 is below "
                "it, so a system assuming independence proceeds. "
                "Note that under the correct joint the observation never changes the action - "
                "every branch diverts, so EVSI is exactly 0. The independence assumption does not "
                "merely add noise: it manufactures a decision change out of an observation that "
                "should not have produced one."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.5,
                "prior_action": "divert",
                "prior_expected_loss": 5.0,
                "decision_threshold_probability": HAZARD_PSTAR,
                "evpi": 5.0,
                "observations": {
                    "sensor_pair": {
                        "evsi_statistical": 0.0,
                        "information_gain_bits": K11_MI,
                        "changes_action": False,
                        "realised_outcome": "0,0",
                        "realised_posterior_hazard": K11_POST_00,
                        "realised_action": "divert",
                        "realised_posterior_under_independence": K11_POST_00_NAIVE,
                        "realised_action_under_independence": "proceed",
                        "realised_log_likelihood_ratio_bits": math.log2(0.16 / 0.76),
                        "realised_log_likelihood_ratio_bits_under_independence": -4.0,
                    }
                },
            },
            "invariants": [
                {
                    "expression": "r['observations']['sensor_pair']['realised_posterior_hazard'] > r['decision_threshold_probability']",
                    "description": "the correct posterior is above the threshold",
                },
                {
                    "expression": "r['observations']['sensor_pair']['realised_posterior_under_independence'] < r['decision_threshold_probability']",
                    "description": "and the independence-assumed posterior is below it",
                },
                {
                    "expression": "r['observations']['sensor_pair']['realised_log_likelihood_ratio_bits_under_independence'] < r['observations']['sensor_pair']['realised_log_likelihood_ratio_bits']",
                    "description": "independence claims strictly more evidence than the data contain",
                },
            ],
        },
        readme=f"""
# WG-BM-054 (K11) — Correlated observation errors

## Scenario

Two smoke sensors on the same ridge, sharing a power supply and a sight line.
Each is individually right four times in five. **Both report clear.**

Declared joint likelihood:

| | `1,1` | `1,0` | `0,1` | `0,0` |
|---|---|---|---|---|
| `P(. \| dangerous)` | 0.76 | 0.04 | 0.04 | 0.16 |
| `P(. \| safe)` | 0.16 | 0.04 | 0.04 | 0.76 |

The marginals are exactly the independent ones — `0.76 + 0.04 = 0.80` — so
**nothing in a per-sensor calibration report would reveal the dependence.** What
differs is that the two agree with probability 0.92 instead of 0.68.

| | dangerous | safe |
|---|---|---|
| `proceed` | 90 | 0 |
| `divert` | 0 | 10 |

## Derivation

`p* = 10 / (10 + 90) = 0.1`. Prior 0.5.

```
true:          P(dangerous | 0,0) = 0.16 / (0.16 + 0.76) = 4/23  = {K11_POST_00:.10f}
independence:  P(dangerous | 0,0) = 0.04 / (0.04 + 0.64) = 1/17  = {K11_POST_00_NAIVE:.10f}
```

In evidence terms:

```
true log-likelihood ratio         = log2(0.16 / 0.76) = {math.log2(0.16/0.76):.6f} bits
independence-assumed              = log2(0.04 / 0.64) = -4.000000 bits
```

The independence assumption claims **two full sensors' worth of evidence from
two sensors that largely repeat each other.**

```
0.174 > 0.1  ->  divert       (correct)
0.059 < 0.1  ->  proceed      (a system assuming independence)
```

## The sharpest part

Under the **correct** joint, the observation never changes the action: every
branch diverts, so `EVSI = 0` exactly. The independence assumption does not
merely add noise to a correct answer — it **manufactures a decision change out
of an observation that should not have produced one**, and the change is towards
the unsafe action.

## Why this is the normal case in a fire

Sensor errors are correlated by construction: shared smoke plumes, shared cloud,
shared power, shared communications, shared calibration drift, shared model
background. Two agreeing readings from co-located instruments are close to one
reading, and the extreme version of that is WG-BM-055, where they *are* one
reading.

The defence is to carry the joint likelihood rather than per-sensor marginals.
The marginals here are correct and they do not contain the information needed to
avoid the error.

The `assume_conditional_independence` mutation replaces the declared joint by
the product of the marginals; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| true posterior after `0,0` | **0.17391** |
| posterior assuming independence | 0.05882 |
| true evidence | {math.log2(0.16/0.76):.4f} bits |
| evidence claimed by independence | −4.0000 bits |
| action, true / independence | `divert` / **`proceed`** |
| EVSI under the correct joint | 0 |
""",
    ))

    # ------------------------------------------------------------------ K12
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-055_K12_duplicate_evidence",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-055",
            "label": "K12",
            "title": "One measurement, two records: duplicate evidence must not double confidence",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "The degenerate limit of WG-BM-054. Two records carry the same underlying "
                       "measurement; counting both doubles the log-likelihood ratio from -2 to -4 "
                       "bits and flips the action.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "records_deduplicated_by_measurement_id": True,
                "duplicate_carries_no_new_information": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "likelihood": "degenerate joint: the two records always agree",
                "independence_assumed": False,
                "decision_threshold": HAZARD_PSTAR,
            },
            "expected_behavior": {
                "observations": {
                    "duplicated_report": {
                        "independent_measurements": 1,
                        "record_count": 2,
                        "realised_posterior_hazard": K12_POST_00,
                    }
                },
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["duplicate_evidence_double_counted", "record_count_mistaken_for_evidence"],
            "mutations_expected_to_fail": ["count_duplicate_evidence"],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "One ground observer's clear report reaches the system twice: once "
                               "over radio and once through the incident log, under different "
                               "record ids but the same measurement id. The two records can only "
                               "agree, because they are the same measurement.",
                "model": "bayes_decision",
                "hypotheses": [
                    {"id": "H_dangerous", "prior": 0.5},
                    {"id": "H_safe", "prior": 0.5},
                ],
                "hazard_hypothesis": "H_dangerous",
                "actions": ["proceed", "divert"],
                "loss": HAZARD_LOSS,
                "decision_deadline_min": 30.0,
                "observations": [
                    {
                        "id": "duplicated_report",
                        "acquisition_time_min": 2.0,
                        "availability_time_min": 4.0,
                        "outcomes": ["1,1", "0,0"],
                        "records": [
                            {"record_id": "radio_0471", "measurement_id": "obs_A"},
                            {"record_id": "log_1182", "measurement_id": "obs_A"},
                        ],
                        "likelihood": {
                            "H_dangerous": {"1,1": 0.8, "0,0": 0.2},
                            "H_safe": {"1,1": 0.2, "0,0": 0.8},
                        },
                        "independent_likelihood": {
                            "H_dangerous": {"1,1": 0.64, "0,0": 0.04},
                            "H_safe": {"1,1": 0.04, "0,0": 0.64},
                        },
                        "realised": "0,0",
                        "note": "independent_likelihood holds the products a double-counting "
                                "system would form; they are not a normalised distribution, "
                                "which is itself a symptom of the error.",
                    }
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-055",
            "source": "closed_form",
            "derivation": (
                "There is one measurement. Its likelihood is 0.8 for a positive report given "
                "danger and 0.2 given safety, so a clear report gives "
                "P(dangerous | clear) = 0.5 * 0.2 / (0.5 * 0.2 + 0.5 * 0.8) = 0.2, and the "
                "log-likelihood ratio is log2(0.2 / 0.8) = -2 bits exactly. "
                "A system that treats the two records as two independent observations multiplies "
                "0.2 * 0.2 = 0.04 against 0.8 * 0.8 = 0.64, obtaining 0.04 / 0.68 = 1/17 = "
                "0.058823529411764705 and a log-likelihood ratio of -4 bits: exactly twice the "
                "evidence, from exactly no extra data. "
                "With p* = 0.1 the correct posterior 0.2 is above the threshold and the action is "
                "to divert; the doubled posterior 0.0588 is below it and the action becomes "
                "proceed. "
                "Deduplication is by measurement id, not by record id: the two records have "
                "different record ids and are the same measurement, which is precisely the case "
                "an ingestion pipeline keyed on record id will get wrong."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.5,
                "prior_action": "divert",
                "prior_expected_loss": 5.0,
                "decision_threshold_probability": HAZARD_PSTAR,
                "observations": {
                    "duplicated_report": {
                        "record_count": 2,
                        "independent_measurements": 1,
                        "contains_duplicates": True,
                        "evsi_statistical": 0.0,
                        "information_gain_bits": K12_MI,
                        "realised_posterior_hazard": K12_POST_00,
                        "realised_action": "divert",
                        "realised_posterior_under_independence": K11_POST_00_NAIVE,
                        "realised_action_under_independence": "proceed",
                        "realised_log_likelihood_ratio_bits": -2.0,
                        "realised_log_likelihood_ratio_bits_under_independence": -4.0,
                    }
                },
            },
            "invariants": [
                {
                    "expression": "r['observations']['duplicated_report']['independent_measurements'] == 1",
                    "description": "two records, one measurement",
                },
                {
                    "expression": "abs(r['observations']['duplicated_report']['realised_log_likelihood_ratio_bits_under_independence'] - 2 * r['observations']['duplicated_report']['realised_log_likelihood_ratio_bits']) < 1e-12",
                    "description": "double counting doubles the evidence exactly",
                },
                {
                    "expression": "r['observations']['duplicated_report']['realised_action'] != r['observations']['duplicated_report']['realised_action_under_independence']",
                    "description": "and the doubling changes the action",
                },
            ],
        },
        readme="""
# WG-BM-055 (K12) — Duplicate sensor evidence

## Scenario

One ground observer reports the ridge clear. The report reaches the system
**twice** — once over radio, once through the incident log — under two different
record ids and one measurement id.

```
record radio_0471   measurement obs_A
record log_1182     measurement obs_A
```

The two records can only ever agree, because they are the same measurement.

## Derivation

One measurement, likelihood 0.8 / 0.2, prior 0.5:

```
P(dangerous | clear) = 0.5 * 0.2 / (0.5 * 0.2 + 0.5 * 0.8) = 0.2
log-likelihood ratio = log2(0.2 / 0.8) = -2 bits
```

Counting both records as independent observations:

```
0.2 * 0.2 = 0.04   against   0.8 * 0.8 = 0.64
P = 0.04 / 0.68 = 1/17 = 0.0588
log-likelihood ratio = -4 bits          exactly twice, from no extra data
```

With `p* = 0.1`:

```
0.2000 > 0.1  ->  divert     (correct)
0.0588 < 0.1  ->  proceed    (double counting)
```

## The degenerate limit of WG-BM-054

WG-BM-054 has two sensors that agree 92% of the time; here they agree 100% of
the time. The error is the same error, and its magnitude is the same **−2 bits
of fabricated evidence**. That is the useful way to think about correlated
evidence: independence is not a binary property, and duplication is the endpoint
of a continuum rather than a separate bug.

## Why record-level deduplication is the wrong key

The two records differ in every field an ingestion pipeline normally keys on:
different ids, different arrival times, different source systems, different
formats. They are the same *measurement*. Deduplication has to be by what was
measured, when and by whom — which means the measurement identity has to survive
ingestion, and in most pipelines it does not.

Common ways one measurement becomes several records:

* a report relayed through two channels, as here;
* a satellite product reprocessed and re-ingested under a new version;
* a mosaic in which adjacent tiles share a pixel;
* an ensemble whose members share initial conditions;
* a retrospective backfill overlapping a real-time feed.

Each of them inflates confidence in exactly this way, and each is invisible in
the per-record metadata.

## Expected

| Quantity | Value |
|---|---|
| records / independent measurements | 2 / **1** |
| correct posterior | 0.2 |
| posterior counting both | 0.0588 |
| evidence, correct / double-counted | −2 bits / **−4 bits** |
| action, correct / double-counted | `divert` / **`proceed`** |
""",
    ))

    # ------------------------------------------------------------------ K13
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-056_K13_fire_correlated_missingness",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-056",
            "label": "K13",
            "title": "Silence is evidence: a missing report raises P(dangerous) from 0.05 to 0.387",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "The probability that a report goes missing depends on the hazard, so "
                       "missingness is itself an observation. An MCAR assumption leaves the belief "
                       "at the prior and takes the unsafe action.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "missingness_mechanism": "MNAR",
                "missingness_likelihood_known": True,
                "silence_is_an_outcome_not_an_absence": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "prior": "P(H_dangerous) = 0.05",
                "likelihood": "P(missing | dangerous) = 0.6, P(missing | safe) = 0.05",
                "posterior": "P(dangerous | missing) = 12/31",
                "missingness_mechanism": "MNAR",
                "decision_threshold": HAZARD_PSTAR,
            },
            "expected_behavior": {
                "observations": {
                    "telemetry_status": {
                        "realised_posterior_hazard": K13_POST_MISSING,
                        "realised_action": "divert",
                    }
                },
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["missingness_mechanism_ignored", "informative_missingness"],
            "mutations_expected_to_fail": ["assume_missing_at_random"],
            "hand_checkable": True,
            "notes": "The Bayesian counterpart of WG-BM-016, which shows the same mechanism as an "
                     "estimation bias. Here it is a decision error.",
        },
        inputs={
            "probabilistic": {
                "description": "A remote weather station on the ridge reports every ten minutes. "
                               "Its report is twelve times more likely to go missing when the "
                               "fire is close - it loses mains power, then its radio path - than "
                               "when it is not. This cycle, no report arrived.",
                "model": "bayes_decision",
                "hypotheses": [
                    {"id": "H_dangerous", "prior": 0.05},
                    {"id": "H_safe", "prior": 0.95},
                ],
                "hazard_hypothesis": "H_dangerous",
                "actions": ["proceed", "divert"],
                "loss": HAZARD_LOSS,
                "decision_deadline_min": 30.0,
                "observations": [
                    {
                        "id": "telemetry_status",
                        "is_missingness_indicator": True,
                        "acquisition_time_min": 0.0,
                        "availability_time_min": 10.0,
                        "outcomes": ["report_received", "report_missing"],
                        "likelihood": {
                            "H_dangerous": {"report_received": 0.4, "report_missing": 0.6},
                            "H_safe": {"report_received": 0.95, "report_missing": 0.05},
                        },
                        "realised": "report_missing",
                    }
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-056",
            "source": "closed_form",
            "derivation": (
                "The missingness indicator is an observation like any other, with likelihood "
                "P(missing | dangerous) = 0.6 and P(missing | safe) = 0.05. "
                "P(missing) = 0.05 * 0.6 + 0.95 * 0.05 = 0.03 + 0.0475 = 0.0775, so "
                "P(dangerous | missing) = 0.03 / 0.0775 = 12/31 = 0.3870967741935484 - the belief "
                "moves from 0.05 to nearly 0.39 on the strength of a report that never arrived. "
                "Its log-likelihood ratio is log2(0.6 / 0.05) = 3.584962500721156 bits, which is "
                "more evidence than most positive detections carry. "
                "On the other branch, P(dangerous | received) = 0.02 / 0.9225 = "
                "0.021680216802168025: a report that does arrive is mild evidence of safety. "
                "With p* = 0.1 the prior action is to proceed at an expected loss of 4.5. After "
                "the missing report the action is to divert; after a received report it remains "
                "proceed. EVSI = 4.5 - (0.0775 * 6.129032258064516 + 0.9225 * 1.951219512195122) "
                "= 4.5 - (0.475 + 1.8) = 2.225. "
                "Under an MCAR assumption the missing report carries no information, the belief "
                "stays at 0.05, which is below p*, and the system proceeds into the hazard."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.05,
                "prior_action": "proceed",
                "prior_expected_loss": 4.5,
                "decision_threshold_probability": HAZARD_PSTAR,
                "observations": {
                    "telemetry_status": {
                        "evsi_statistical": 2.225,
                        "evsi_operational": 2.225,
                        "information_gain_bits": K13_MI,
                        "changes_action": True,
                        "realised_posterior_hazard": K13_POST_MISSING,
                        "realised_action": "divert",
                        "realised_log_likelihood_ratio_bits": math.log2(0.6 / 0.05),
                        "posterior_hazard_by_outcome": {
                            "report_received": K13_POST_RECEIVED,
                            "report_missing": K13_POST_MISSING,
                        },
                        "action_by_outcome": {
                            "report_received": "proceed",
                            "report_missing": "divert",
                        },
                    }
                },
            },
            "invariants": [
                {
                    "expression": "r['observations']['telemetry_status']['realised_posterior_hazard'] > 7 * r['prior_hazard']",
                    "description": "the missing report multiplies the hazard probability sevenfold",
                },
                {
                    "expression": "r['observations']['telemetry_status']['realised_log_likelihood_ratio_bits'] > 3.0",
                    "description": "silence carries more than three bits of evidence",
                },
                {
                    "expression": "r['observations']['telemetry_status']['action_by_outcome']['report_missing'] != r['prior_action']",
                    "description": "and it changes the action",
                },
            ],
        },
        readme=f"""
# WG-BM-056 (K13) — Fire-correlated missingness

## Scenario

A remote weather station reports every ten minutes. Its report is **twelve times
more likely to go missing when the fire is close** — mains power first, then the
radio path.

```
prior: P(H_dangerous) = 0.05

P(missing | dangerous) = 0.60
P(missing | safe)      = 0.05
```

**This cycle, no report arrived.**

## Derivation

The missingness indicator is an observation like any other:

```
P(missing) = 0.05 * 0.60 + 0.95 * 0.05 = 0.03 + 0.0475 = 0.0775
P(dangerous | missing) = 0.03 / 0.0775 = 12/31 = {K13_POST_MISSING:.10f}
```

The belief moves from **0.05 to 0.387** on the strength of a report that never
arrived. In evidence terms:

```
log2(0.60 / 0.05) = {math.log2(0.6/0.05):.6f} bits
```

— more evidence than many positive detections carry.

The other branch is mild reassurance:
`P(dangerous | received) = 0.02 / 0.9225 = {K13_POST_RECEIVED:.6f}`.

With `p* = 0.1`:

| | posterior | action |
|---|---|---|
| prior | 0.050 | `proceed` |
| report received | 0.022 | `proceed` |
| **report missing** | **0.387** | **`divert`** |

```
EVSI = 4.5 - (0.0775 * 6.12903 + 0.9225 * 1.95122) = 4.5 - 2.275 = 2.225
```

Under an **MCAR** assumption the missing report carries nothing, the belief stays
at 0.05, and the system **proceeds into the hazard**.

## Relation to WG-BM-016

WG-BM-016 (D4) shows the same mechanism as an **estimation** bias: averaging the
surviving sensors gives 0.0 against a truth of 0.6. This benchmark shows it as a
**decision** error, and adds the thing D4 could not: the exact posterior, and
therefore the exact amount of evidence that silence carries.

The two together make the operational point. A monitoring system that displays
"3 of 8 stations reporting" as a data-quality warning has the sign backwards:
the five silent stations are the most informative thing on the screen.

## What the benchmark does not claim

That `P(missing | dangerous) = 0.6` is knowable. It is stipulated here. In a
real network the missingness mechanism has to be estimated, and it is
confounded with ordinary outages — which is the gap WG-BM-016's README records
and this benchmark does not close.

## Expected

| Quantity | Value |
|---|---|
| `P(dangerous \| missing)` | **12/31 = 0.3871** |
| evidence in the silence | {math.log2(0.6/0.05):.4f} bits |
| action, correct / MCAR | `divert` / **`proceed`** |
| EVSI | 2.225 |
""",
    ))

    # ------------------------------------------------------------------ K14
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-057_K14_non_detection_is_not_absence",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-057",
            "label": "K14",
            "title": "No detection leaves P(fire) at 0.073, which is still above the threshold",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "A detector with a 30 per cent false-negative rate. After a negative "
                       "reading the posterior falls from 0.2 to 0.073 and the conservative action "
                       "is still correct. Non-detection does not license standing down.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "false_negative_rate": 0.3,
                "false_positive_rate": 0.05,
                "non_detection_is_evidence_not_proof": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "prior": "P(H_fire) = 0.2",
                "likelihood": "P(no detection | fire) = 0.3, P(no detection | no fire) = 0.95",
                "posterior": "P(fire | no detection) = 3/41",
                "decision_threshold": 0.05,
            },
            "expected_behavior": {
                "observations": {
                    "detector": {
                        "realised_posterior_hazard": K14_POST_NO_DETECT,
                        "realised_action": "divert",
                    }
                },
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["non_detection_read_as_absence", "false_negative_ignored"],
            "mutations_expected_to_fail": ["non_detection_is_absence"],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "An airborne detector overflies a drainage where fire is suspected. "
                               "It misses a real fire three times in ten and raises a false alarm "
                               "one time in twenty. It reports nothing.",
                "model": "bayes_decision",
                "hypotheses": [
                    {"id": "H_fire", "prior": 0.2},
                    {"id": "H_no_fire", "prior": 0.8},
                ],
                "hazard_hypothesis": "H_fire",
                "actions": ["proceed", "divert"],
                "loss": {
                    "proceed": {"H_fire": 95.0, "H_no_fire": 0.0},
                    "divert": {"H_fire": 0.0, "H_no_fire": 5.0},
                },
                "decision_deadline_min": 30.0,
                "observations": [
                    {
                        "id": "detector",
                        "acquisition_time_min": 2.0,
                        "availability_time_min": 6.0,
                        "outcomes": ["detect", "no_detect"],
                        "negative_outcome": "no_detect",
                        "positive_outcome": "detect",
                        "likelihood": DETECTOR,
                        "realised": "no_detect",
                    }
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-057",
            "source": "closed_form",
            "derivation": (
                "P(no detection) = 0.2 * 0.3 + 0.8 * 0.95 = 0.06 + 0.76 = 0.82, so "
                "P(fire | no detection) = 0.06 / 0.82 = 3/41 = 0.07317073170731707. The negative "
                "reading is genuinely informative - it cuts the fire probability from 0.2 to "
                "0.073, a factor of 2.7 - and it does not come close to zero. "
                "The loss matrix gives p* = 5 / (5 + 95) = 0.05, and 0.073 is above it, so the "
                "conservative action remains correct after the negative reading. The prior action "
                "was also to divert, at an expected loss of 0.8 * 5 = 4, and on the positive "
                "branch P(fire | detect) = 0.14 / 0.18 = 0.7777777777777777, which is also above "
                "p*. Since every branch diverts, EVSI is exactly 0: this detector cannot license "
                "standing down, whatever it reports. "
                "A system that reads a non-detection as proof of absence sets the posterior to 0, "
                "which is below p*, and proceeds into a drainage that is 7.3 per cent likely to "
                "be on fire."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.2,
                "prior_action": "divert",
                "prior_expected_loss": 4.0,
                "decision_threshold_probability": 0.05,
                "observations": {
                    "detector": {
                        "evsi_statistical": 0.0,
                        "information_gain_bits": K14_MI,
                        "changes_action": False,
                        "realised_posterior_hazard": K14_POST_NO_DETECT,
                        "realised_action": "divert",
                        "posterior_hazard_by_outcome": {
                            "detect": K14_POST_DETECT,
                            "no_detect": K14_POST_NO_DETECT,
                        },
                        "action_by_outcome": {"detect": "divert", "no_detect": "divert"},
                    }
                },
            },
            "invariants": [
                {
                    "expression": "r['observations']['detector']['realised_posterior_hazard'] > 0.0",
                    "description": "a non-detection never drives the probability of fire to zero",
                },
                {
                    "expression": "r['observations']['detector']['realised_posterior_hazard'] < r['prior_hazard']",
                    "description": "but it is real evidence, and the belief does fall",
                },
                {
                    "expression": "r['observations']['detector']['realised_posterior_hazard'] > r['decision_threshold_probability']",
                    "description": "and it stays above the threshold, so the action does not change",
                },
            ],
        },
        readme=f"""
# WG-BM-057 (K14) — Non-detection is not absence

## Scenario

An airborne detector overflies a drainage where fire is suspected.

```
prior: P(fire) = 0.2

P(no detection | fire)    = 0.30        <- it misses 3 real fires in 10
P(no detection | no fire) = 0.95
```

**It reports nothing.**

| | fire | no fire |
|---|---|---|
| `proceed` | 95 | 0 |
| `divert` | 0 | 5 |

## Derivation

```
P(no detection) = 0.2 * 0.30 + 0.8 * 0.95 = 0.06 + 0.76 = 0.82
P(fire | no detection) = 0.06 / 0.82 = 3/41 = {K14_POST_NO_DETECT:.10f}
```

The reading is **genuinely informative** — 0.2 falls to 0.073, a factor of 2.7 —
and it is **nowhere near zero**.

```
p* = 5 / (5 + 95) = 0.05
0.0732 > 0.05   ->  divert,  unchanged from the prior
```

Both branches divert (`P(fire | detect) = 0.14/0.18 = 0.778` is also above `p*`),
so `EVSI = 0`: **this detector cannot license standing down, whatever it
reports.**

## The two errors this separates

The benchmark is aimed at one error and guards against its opposite.

**"No detection means no fire."** Sets the posterior to 0, which is below `p*`,
and sends people into a drainage that is 7.3% likely to be burning. This is the
`non_detection_is_absence` mutation and this benchmark is its detector.

**"The detector is useless, ignore it."** Also wrong: the reading moved the
belief by a factor of 2.7, and that is worth having. What it did not do is cross
a decision boundary — and *that* is the question to ask of an observation, not
whether it was informative.

## Relation to WG-BM-017

WG-BM-017 (D5) makes the same point without probabilities: it distinguishes a
cell where the detector is reliable from one where it is not, and shows the
route choice flipping. This benchmark supplies the number that D5 could only
gesture at — after a negative reading from a detector with a 30% miss rate and a
20% prior, the fire probability is **7.3%**, and whether that is acceptable is a
question for the loss matrix, not for the detector.

## Expected

| Quantity | Value |
|---|---|
| `P(fire \| no detection)` | **3/41 = 0.0732** |
| `P(fire \| detection)` | 0.7778 |
| `p*` | 0.05 |
| action after non-detection | `divert` (unchanged) |
| EVSI | 0 |
""",
    ))

    # ------------------------------------------------------------------ K15
    written.append(write_benchmark(
        directory="benchmarks/probabilistic_forecast/WG-BM-058_K15_false_positive",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-058",
            "label": "K15",
            "title": "A detection raises P(fire) from 0.02 to 0.22, and 0.22 is not 1",
            "category": "probabilistic_forecast",
            "difficulty": "adversarial",
            "purpose": "Against a low base rate a detection is strong evidence and far from "
                       "proof. Treating it as certainty escalates from traffic diversion to full "
                       "evacuation and triples the expected loss.",
            "solver": "probabilistic.bayes_decision",
            "assumptions": {
                "false_positive_rate": 0.05,
                "base_rate": 0.02,
                "three_action_escalation_ladder": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "posterior_belief",
                "prior": "P(H_fire) = 0.02",
                "likelihood": "P(detect | fire) = 0.7, P(detect | no fire) = 0.05",
                "posterior": "P(fire | detect) = 2/9",
            },
            "expected_behavior": {
                "observations": {
                    "detector": {
                        "realised_posterior_hazard": K15_POST_DETECT,
                        "realised_action": "divert_traffic",
                    }
                },
            },
            "tolerance": TOL,
            "exactness": "CLOSED_FORM",
            "detects": ["detection_read_as_certainty", "base_rate_neglect"],
            "mutations_expected_to_fail": ["detection_is_certainty"],
            "hand_checkable": True,
        },
        inputs={
            "probabilistic": {
                "description": "The WG-BM-057 detector applied where fire is rare: a base rate of "
                               "2 per cent. It reports a detection. Three responses are available, "
                               "from monitoring through traffic diversion to a full evacuation.",
                "model": "bayes_decision",
                "hypotheses": [
                    {"id": "H_fire", "prior": 0.02},
                    {"id": "H_no_fire", "prior": 0.98},
                ],
                "hazard_hypothesis": "H_fire",
                "actions": ["monitor", "divert_traffic", "full_evacuation"],
                "loss": K15_LOSS,
                "decision_deadline_min": 30.0,
                "observations": [
                    {
                        "id": "detector",
                        "acquisition_time_min": 2.0,
                        "availability_time_min": 6.0,
                        "outcomes": ["detect", "no_detect"],
                        "negative_outcome": "no_detect",
                        "positive_outcome": "detect",
                        "likelihood": DETECTOR,
                        "realised": "detect",
                    }
                ],
            }
        },
        expected={
            "benchmark_id": "WG-BM-058",
            "source": "closed_form",
            "derivation": (
                "P(detect) = 0.02 * 0.7 + 0.98 * 0.05 = 0.014 + 0.049 = 0.063, so "
                "P(fire | detect) = 0.014 / 0.063 = 2/9 = 0.2222222222222222. The detection is "
                "strong evidence - it multiplies the fire probability by eleven - and it leaves "
                "more than three quarters of the posterior mass on there being no fire, because "
                "the base rate is low and there are 49 false alarms for every 14 true ones. "
                "At a posterior of 2/9 the expected losses are 200 * 2/9 = 44.44 for monitoring, "
                "6 * 7/9 + 30 * 2/9 = 11.33 for diverting traffic and 40 * 7/9 = 31.11 for a full "
                "evacuation, so the correct response is to divert traffic. Under the prior of "
                "0.02 it was to monitor, at an expected loss of 4, so the detection does change "
                "the action, and EVSI = 4 - (0.063 * 11.333333333333332 + 0.937 * "
                "1.2806830309498399) = 4 - 1.914 = 2.086. "
                "Treating the detection as certainty sets the posterior to 1, at which the "
                "expected losses are 200, 30 and 0, so the response escalates to a full "
                "evacuation. Evaluated at the true posterior that costs 31.11 against 11.33: "
                "nearly three times the loss, and the excess is borne as an unnecessary "
                "evacuation 78 per cent of the time. "
                "With three actions there is no single threshold. The optimal response is to "
                "monitor below 3/88, divert traffic between 3/88 and 17/32, and evacuate above "
                "17/32."
            ),
            "results": {
                "model": "bayes_decision",
                "prior_hazard": 0.02,
                "prior_action": "monitor",
                "prior_expected_loss": 4.0,
                "decision_threshold_probability": None,
                "action_partition": [
                    {"p_from": 0.0, "p_to": 6.0 / 176.0, "action": "monitor"},
                    {"p_from": 6.0 / 176.0, "p_to": 34.0 / 64.0, "action": "divert_traffic"},
                    {"p_from": 34.0 / 64.0, "p_to": 1.0, "action": "full_evacuation"},
                ],
                "observations": {
                    "detector": {
                        "evsi_statistical": 2.086,
                        "information_gain_bits": K15_MI,
                        "changes_action": True,
                        "realised_posterior_hazard": K15_POST_DETECT,
                        "realised_action": "divert_traffic",
                        "posterior_hazard_by_outcome": {
                            "detect": K15_POST_DETECT,
                            "no_detect": K15_POST_NO_DETECT,
                        },
                        "action_by_outcome": {
                            "detect": "divert_traffic",
                            "no_detect": "monitor",
                        },
                    }
                },
            },
            "invariants": [
                {
                    "expression": "r['observations']['detector']['realised_posterior_hazard'] > 10 * r['prior_hazard']",
                    "description": "a detection is strong evidence: the belief rises elevenfold",
                },
                {
                    "expression": "r['observations']['detector']['realised_posterior_hazard'] < 0.5",
                    "description": "and most of the posterior mass is still on there being no fire",
                },
                {
                    "expression": "r['observations']['detector']['realised_action'] == 'divert_traffic'",
                    "description": "the proportionate response, not the maximal one",
                },
                {
                    "expression": "len(r['action_partition']) == 3",
                    "description": "an escalation ladder has two switch points, not one threshold",
                },
            ],
        },
        readme=f"""
# WG-BM-058 (K15) — False positive

## Scenario

The WG-BM-057 detector, applied where fire is **rare**.

```
prior: P(fire) = 0.02

P(detect | fire)    = 0.70
P(detect | no fire) = 0.05
```

**It reports a detection.** Three responses are available:

| | fire | no fire |
|---|---|---|
| `monitor` | 200 | 0 |
| `divert_traffic` | 30 | 6 |
| `full_evacuation` | 0 | 40 |

## Derivation

```
P(detect) = 0.02 * 0.70 + 0.98 * 0.05 = 0.014 + 0.049 = 0.063
P(fire | detect) = 0.014 / 0.063 = 2/9 = {K15_POST_DETECT:.10f}
```

The detection multiplies the fire probability **elevenfold** — and leaves more
than three quarters of the mass on there being no fire, because at a 2% base rate
the detector generates 49 false alarms for every 14 true ones.

At `p = 2/9`:

```
monitor          200 * 2/9            = 44.44
divert_traffic   6 * 7/9 + 30 * 2/9   = 11.33      <- correct
full_evacuation  40 * 7/9             = 31.11
```

Under the prior the response was `monitor` (expected loss 4), so the detection
does change the action, and `EVSI = 4 - 1.914 = 2.086`.

**Treating the detection as certainty** sets `p = 1`, where the losses are 200,
30 and 0, so the response escalates to a full evacuation. Evaluated at the true
posterior that costs **31.11 against 11.33** — nearly three times the loss, and
the excess is borne as an unnecessary evacuation 78% of the time.

## The escalation ladder

Three actions give two switch points, not one threshold:

```
p < 3/88 = 0.0341        monitor
0.0341 < p < 0.53125     divert_traffic
p > 0.53125              full_evacuation
```

A detection at a 2% base rate lands in the middle band. That is the operational
content of the benchmark: the correct response to a credible detection is
usually the **proportionate** one, and a system that maps `detection -> maximum
response` has no middle band to land in.

## Why base-rate neglect is the standing risk here

Detection pipelines are tuned on their conditional performance — sensitivity and
specificity — and those two numbers do not determine the posterior. The same
detector that leaves `P(fire) = 0.22` here leaves `P(fire) = 0.78` in WG-BM-057,
where the base rate is 0.2. **Nothing about the detector changed.** Any system
that reports "fire detected" without the prevailing base rate has discarded the
input that does most of the work.

Repeated unnecessary escalation also has a cost this suite does not model:
the next warning is believed less. That is a real dynamic and there is no
benchmark for it; it is recorded in `reports/KNOWN_GAPS.md`.

## Expected

| Quantity | Value |
|---|---|
| `P(fire \| detect)` | **2/9 = 0.2222** |
| action | `divert_traffic` |
| action if the detection is treated as certain | `full_evacuation` |
| loss of that escalation, at the true posterior | 31.11 vs 11.33 |
| EVSI | 2.086 |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
