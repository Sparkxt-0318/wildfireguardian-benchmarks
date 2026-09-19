"""Author the J family: robust protectability toy cases (WG-BM-041..043)."""

from __future__ import annotations

from common import report, write_benchmark

SCRIPT = "author_protectability.py"
TOLERANCE = {"default": 1.0e-09}

ACCEPTABLE_LOSS = 10.0


def main() -> None:
    written = []

    # ------------------------------------------------------------------ J1
    written.append(write_benchmark(
        directory="benchmarks/forecast_value/WG-BM-041_J1_robust_action_exists",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-041",
            "label": "J1",
            "title": "Deep uncertainty, but one action is acceptable in every world",
            "category": "protectability",
            "difficulty": "basic",
            "purpose": "Two plausible worlds disagree completely about where the fire goes, and "
                       "the same action is acceptable in both. EVPI is exactly zero: the "
                       "resident is robustly protectable and no observation is worth making.",
            "solver": "decision.value_of_information",
            "assumptions": {
                "acceptable_loss_threshold": ACCEPTABLE_LOSS,
                "no_intervention_optimisation": True,
                "decision_deadline_min": 10,
            },
            "expected_behavior": {
                "evpi": 0.0,
                "realizable_value_of_information": 0.0,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["information_value_overclaimed", "robust_action_missed"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "This is a mathematical example, not an intervention optimiser. It fixes "
                     "what 'robustly protectable' has to mean before any optimisation is built.",
        },
        inputs={
            "decision": {
                "description": "A single resident. Two plausible worlds: the fire arrives from "
                               "the north or from the south. Evacuating in the right direction "
                               "is good and in the wrong direction is disastrous; reinforcing "
                               "the shelter in place is acceptable in both.",
                "scenarios": [
                    {"id": "w_north", "probability": 0.5},
                    {"id": "w_south", "probability": 0.5},
                ],
                "actions": ["reinforce_shelter", "evacuate_north", "evacuate_south"],
                "loss": {
                    "reinforce_shelter": {"w_north": 4.0, "w_south": 4.0},
                    "evacuate_north": {"w_north": 5.0, "w_south": 90.0},
                    "evacuate_south": {"w_north": 90.0, "w_south": 5.0},
                },
                "decision_deadline_min": 10.0,
                "default_action": "reinforce_shelter",
                "truth_scenario": "w_north",
                "information_sources": [
                    {
                        "id": "recon_flight",
                        "available_at_min": 5.0,
                        "signal": {"w_north": "north", "w_south": "south"},
                        "skill_score": 1.0,
                        "spatial_error_m": 0.0,
                    }
                ],
                "policies": [
                    {"id": "act_on_prior", "type": "fixed", "action": "reinforce_shelter"},
                    {"id": "wait_for_recon", "type": "informed", "source": "recon_flight"},
                ],
                "baseline_policy": "act_on_prior",
            }
        },
        expected={
            "benchmark_id": "WG-BM-041",
            "source": "hand_derivation",
            "derivation": (
                "Reinforcing the shelter costs 4 in both worlds. Evacuating in the correct "
                "direction costs 5 and in the wrong direction 90, so reinforcing is the best "
                "action in each world taken separately - not merely on average. "
                "Consequently the clairvoyant expected loss is 0.5 * 4 + 0.5 * 4 = 4, equal to "
                "the expected loss of the best fixed action, and EVPI = 0. "
                "The recon flight is timely, perfectly informative, and useless: on either signal "
                "the Bayes action is still to reinforce the shelter, so the informed policy's "
                "action map is identical to the baseline's and its value is 0. "
                "The worst case under the robust action is 4, which is inside the declared "
                "acceptable loss of 10, so the resident is robustly protectable."
            ),
            "results": {
                "truth_scenario": "w_north",
                "expected_loss_by_policy": {"act_on_prior": 4.0, "wait_for_recon": 4.0},
                "value_by_policy": {"act_on_prior": 0.0, "wait_for_recon": 0.0},
                "realised_loss_by_policy": {"act_on_prior": 4.0, "wait_for_recon": 4.0},
                "identical_actions_to_baseline": {"act_on_prior": True, "wait_for_recon": True},
                "clairvoyant_expected_loss": 4.0,
                "best_fixed_action": "reinforce_shelter",
                "best_fixed_expected_loss": 4.0,
                "evpi": 0.0,
                "realizable_value_of_information": 0.0,
                "timely_information_sources": ["recon_flight"],
                "policies": {
                    "act_on_prior": {"worst_case_loss": 4.0},
                    "wait_for_recon": {"worst_case_loss": 4.0},
                },
            },
            "invariants": [
                {
                    "expression": "r['evpi'] == 0.0",
                    "description": "perfect information is worth exactly nothing",
                },
                {
                    "expression": "r['policies']['act_on_prior']['worst_case_loss'] <= 10.0",
                    "description": "the robust action is acceptable in the worst case",
                },
            ],
        },
        readme=f"""
# WG-BM-041 (J1) — Uncertainty with a robust action available

## Scenario

One resident. Two plausible worlds, equally likely: the fire arrives from the
north, or from the south.

| | `w_north` | `w_south` |
|---|---|---|
| `reinforce_shelter` | **4** | **4** |
| `evacuate_north` | 5 | 90 |
| `evacuate_south` | 90 | 5 |

The declared acceptable loss threshold is **{ACCEPTABLE_LOSS:.0f}**.

A perfect reconnaissance flight is available at minute 5, comfortably before the
minute-10 decision deadline.

## Derivation

Reinforcing the shelter is the best action **in each world separately**, not
merely on average: 4 beats 5 in `w_north` and 4 beats 5 in `w_south`. Therefore

```
clairvoyant expected loss = 0.5 * 4 + 0.5 * 4 = 4
best fixed action         = reinforce_shelter, expected loss 4
EVPI                      = 4 - 4 = 0
```

The recon flight is timely and perfectly informative, and its value is **zero**:
on either signal the Bayes action is still to reinforce the shelter. The
informed policy's action map is identical to the baseline's.

The worst case under the robust action is 4, inside the acceptable threshold of
{ACCEPTABLE_LOSS:.0f}, so the resident is **robustly protectable**: there exists a single
action that is acceptable across the whole uncertainty set.

## Definitions this benchmark fixes

**Robustly protectable.** There exists an action whose loss is within the
acceptable threshold in every scenario of the declared uncertainty set. Note
what this does *not* require: it does not require knowing which scenario is
true, it does not require the scenarios to be probabilistically weighted, and it
does not require the action to be optimal in any of them.

**Value of information is relative to the decision, not to the uncertainty.**
There is a great deal of uncertainty here — the two worlds could hardly disagree
more about where the fire goes — and none of it is decision-relevant. Resolving
uncertainty is only worth something when the resolution would change what you
do.

## Why a zero-value case has to be in the suite

Without it, a system is rewarded for recommending observation, reconnaissance
and further modelling in every situation, since a positive recommendation is
never penalised. Reconnaissance flights are scarce, and tasking one to resolve
an uncertainty that cannot change the action is a real cost paid by whichever
decision genuinely needed it.

This benchmark is the reference point for WG-BM-042, which is the same structure
with the robust action removed.

## Expected

| Quantity | Value |
|---|---|
| EVPI | **0** |
| value of the recon flight | 0 |
| robust action | `reinforce_shelter` |
| worst-case loss of the robust action | 4 (threshold {ACCEPTABLE_LOSS:.0f}) |
| informed actions identical to baseline | `true` |
""",
    ))

    # ------------------------------------------------------------------ J2
    written.append(write_benchmark(
        directory="benchmarks/forecast_value/WG-BM-042_J2_observation_changes_protectability",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-042",
            "label": "J2",
            "title": "No robust action exists, and a timely observation supplies one",
            "category": "protectability",
            "difficulty": "intermediate",
            "purpose": "Two worlds require incompatible actions. Without information the best "
                       "fixed action loses 45 in expectation; a timely observation reduces that "
                       "to 0, so the observation is worth the full EVPI of 45.",
            "solver": "decision.value_of_information",
            "assumptions": {
                "acceptable_loss_threshold": ACCEPTABLE_LOSS,
                "observation_before_deadline": True,
                "decision_deadline_min": 10,
            },
            "expected_behavior": {
                "evpi": 45.0,
                "realizable_value_of_information": 45.0,
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["information_value_underclaimed", "protectability_misclassified"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
        },
        inputs={
            "decision": {
                "description": "The same two worlds, but sheltering is no longer survivable and "
                               "the two evacuation directions are mutually exclusive. A recon "
                               "flight at minute 5 distinguishes the worlds before the minute-10 "
                               "deadline.",
                "scenarios": [
                    {"id": "w_north", "probability": 0.5},
                    {"id": "w_south", "probability": 0.5},
                ],
                "actions": ["evacuate_north", "evacuate_south", "shelter"],
                "loss": {
                    "evacuate_north": {"w_north": 0.0, "w_south": 90.0},
                    "evacuate_south": {"w_north": 95.0, "w_south": 0.0},
                    "shelter": {"w_north": 50.0, "w_south": 50.0},
                },
                "decision_deadline_min": 10.0,
                "default_action": "shelter",
                "truth_scenario": "w_south",
                "information_sources": [
                    {
                        "id": "recon_flight",
                        "available_at_min": 5.0,
                        "signal": {"w_north": "north", "w_south": "south"},
                        "skill_score": 1.0,
                        "spatial_error_m": 0.0,
                    }
                ],
                "policies": [
                    {"id": "act_on_prior", "type": "fixed", "action": "evacuate_north"},
                    {"id": "wait_for_recon", "type": "informed", "source": "recon_flight"},
                ],
                "baseline_policy": "act_on_prior",
            }
        },
        expected={
            "benchmark_id": "WG-BM-042",
            "source": "hand_derivation",
            "derivation": (
                "Expected losses of the fixed actions: evacuate_north 0.5*0 + 0.5*90 = 45, "
                "evacuate_south 0.5*95 + 0.5*0 = 47.5, shelter 50. The best fixed action is "
                "evacuate_north at 45, and its worst case is 90, far outside the acceptable "
                "threshold of 10: no action is acceptable across both worlds, so the resident is "
                "not robustly protectable on the prior alone. "
                "The clairvoyant expected loss is 0.5*0 + 0.5*0 = 0, so EVPI = 45 - 0 = 45. "
                "The recon flight arrives at minute 5, before the minute-10 deadline, and "
                "distinguishes the worlds, so the informed policy evacuates north on 'north' and "
                "south on 'south', with expected loss 0. Its value is the full 45. "
                "In the realised world w_south the prior-based policy loses 90 and the informed "
                "policy loses 0."
            ),
            "results": {
                "truth_scenario": "w_south",
                "expected_loss_by_policy": {"act_on_prior": 45.0, "wait_for_recon": 0.0},
                "value_by_policy": {"act_on_prior": 0.0, "wait_for_recon": 45.0},
                "realised_loss_by_policy": {"act_on_prior": 90.0, "wait_for_recon": 0.0},
                "realised_value_by_policy": {"act_on_prior": 0.0, "wait_for_recon": 90.0},
                "clairvoyant_expected_loss": 0.0,
                "best_fixed_action": "evacuate_north",
                "best_fixed_expected_loss": 45.0,
                "evpi": 45.0,
                "realizable_value_of_information": 45.0,
                "timely_information_sources": ["recon_flight"],
                "late_information_sources": [],
                "identical_actions_to_baseline": {"act_on_prior": True, "wait_for_recon": False},
                "policies": {
                    "act_on_prior": {"worst_case_loss": 90.0},
                    "wait_for_recon": {"worst_case_loss": 0.0},
                },
            },
            "invariants": [
                {
                    "expression": "r['policies']['act_on_prior']['worst_case_loss'] > 10.0",
                    "description": "no fixed action is acceptable in both worlds",
                },
                {
                    "expression": "r['policies']['wait_for_recon']['worst_case_loss'] <= 10.0",
                    "description": "with the observation, the resident becomes protectable in every world",
                },
                {
                    "expression": "abs(r['realizable_value_of_information'] - r['evpi']) < 1e-12",
                    "description": "the timely observation captures the entire value of information",
                },
            ],
        },
        readme=f"""
# WG-BM-042 (J2) — Observation changes protectability

## Scenario

The same two worlds as WG-BM-041, with the robust action removed: sheltering is
no longer survivable, and the two evacuation directions are mutually exclusive.

| | `w_north` | `w_south` |
|---|---|---|
| `evacuate_north` | 0 | **90** |
| `evacuate_south` | **95** | 0 |
| `shelter` | 50 | 50 |

Acceptable loss threshold: **{ACCEPTABLE_LOSS:.0f}**. Decision deadline: minute 10.
A perfect recon flight reports at **minute 5**.

## Derivation

```
E[evacuate_north] = 0.5*0  + 0.5*90 = 45     <- best fixed action
E[evacuate_south] = 0.5*95 + 0.5*0  = 47.5
E[shelter]        = 50

worst case of the best fixed action = 90     >> threshold 10
```

**No action is acceptable across both worlds**, so on the prior alone the
resident is *not* robustly protectable.

```
clairvoyant expected loss = 0.5*0 + 0.5*0 = 0
EVPI = 45 - 0 = 45
```

The recon flight arrives 5 minutes before the deadline and separates the worlds,
so the informed policy evacuates north on "north" and south on "south":

```
expected loss with the observation = 0
value of the observation           = 45 = EVPI      (all of it)
worst case with the observation    = 0   <= threshold 10
```

**The observation converts a resident who is not robustly protectable into one
who is.** That, and not the reduction in expected loss, is the operationally
important statement.

## Contrast with WG-BM-041

| | WG-BM-041 (J1) | WG-BM-042 (J2) |
|---|---|---|
| uncertainty | identical | identical |
| robust action exists on the prior | **yes** | **no** |
| EVPI | 0 | 45 |
| worth tasking a recon flight | no | **yes** |

The uncertainty is the same in both. What differs is whether the action set
contains something acceptable everywhere. This is why "how uncertain are we?" is
the wrong question to ask when deciding whether to gather information, and
"would the answer change what we do?" is the right one.

## Expected

| Quantity | Value |
|---|---|
| best fixed action | `evacuate_north`, expected loss 45 |
| worst case without information | 90 (not protectable) |
| EVPI | 45 |
| realisable value of the observation | 45 |
| worst case with information | 0 (protectable) |
""",
    ))

    # ------------------------------------------------------------------ J3
    written.append(write_benchmark(
        directory="benchmarks/forecast_value/WG-BM-043_J3_observation_too_late",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-043",
            "label": "J3",
            "title": "The same observation, five minutes too late, is worth nothing",
            "category": "protectability",
            "difficulty": "adversarial",
            "purpose": "WG-BM-042 with the recon flight arriving at minute 15 instead of 5. EVPI "
                       "is unchanged at 45; the realisable value is 0 and waiting for it is worse "
                       "than acting on the prior.",
            "solver": "decision.value_of_information",
            "assumptions": {
                "acceptable_loss_threshold": ACCEPTABLE_LOSS,
                "observation_after_deadline": True,
                "decision_deadline_min": 10,
                "waiting_means_sheltering": True,
            },
            "expected_behavior": {
                "evpi": 45.0,
                "realizable_value_of_information": 0.0,
                "value_by_policy": {"wait_for_recon": -5.0},
            },
            "tolerance": TOLERANCE,
            "exactness": "exact_analytic",
            "detects": ["timeliness_ignored", "evpi_mistaken_for_realisable_value"],
            "mutations_expected_to_fail": ["forecast_always_trusted"],
            "hand_checkable": True,
        },
        inputs={
            "decision": {
                "description": "Identical to WG-BM-042 except that the recon flight reports at "
                               "minute 15, five minutes after both evacuation options have "
                               "expired. A decision maker who waits for it is sheltering by "
                               "default.",
                "scenarios": [
                    {"id": "w_north", "probability": 0.5},
                    {"id": "w_south", "probability": 0.5},
                ],
                "actions": ["evacuate_north", "evacuate_south", "shelter"],
                "loss": {
                    "evacuate_north": {"w_north": 0.0, "w_south": 90.0},
                    "evacuate_south": {"w_north": 95.0, "w_south": 0.0},
                    "shelter": {"w_north": 50.0, "w_south": 50.0},
                },
                "decision_deadline_min": 10.0,
                "default_action": "shelter",
                "truth_scenario": "w_north",
                "information_sources": [
                    {
                        "id": "recon_flight_late",
                        "available_at_min": 15.0,
                        "signal": {"w_north": "north", "w_south": "south"},
                        "skill_score": 1.0,
                        "spatial_error_m": 0.0,
                    }
                ],
                "policies": [
                    {"id": "act_on_prior", "type": "fixed", "action": "evacuate_north"},
                    {
                        "id": "wait_for_recon",
                        "type": "informed",
                        "source": "recon_flight_late",
                        "fallback_action": "shelter",
                    },
                ],
                "baseline_policy": "act_on_prior",
            }
        },
        expected={
            "benchmark_id": "WG-BM-043",
            "source": "hand_derivation",
            "derivation": (
                "The decision problem is identical to WG-BM-042, so the clairvoyant expected loss "
                "is still 0, the best fixed action is still evacuate_north at 45, and EVPI is "
                "still 45. Only the availability time changed, from minute 5 to minute 15, and "
                "the deadline is minute 10. "
                "The recon flight can therefore no longer influence the action. A decision maker "
                "who waits for it has, at the deadline, not evacuated, which is the shelter "
                "outcome: expected loss 0.5 * 50 + 0.5 * 50 = 50 against the baseline's 45, a "
                "value of -5. The realisable value of information is 0 because no timely policy "
                "can use the source. "
                "In the realised world w_north, acting on the prior happens to be exactly right "
                "and loses 0, while waiting loses 50. The worst case under the waiting policy is "
                "50, still outside the acceptable threshold of 10, so the observation does not "
                "make the resident protectable."
            ),
            "results": {
                "truth_scenario": "w_north",
                "expected_loss_by_policy": {"act_on_prior": 45.0, "wait_for_recon": 50.0},
                "value_by_policy": {"act_on_prior": 0.0, "wait_for_recon": -5.0},
                "realised_loss_by_policy": {"act_on_prior": 0.0, "wait_for_recon": 50.0},
                "realised_value_by_policy": {"act_on_prior": 0.0, "wait_for_recon": -50.0},
                "clairvoyant_expected_loss": 0.0,
                "best_fixed_action": "evacuate_north",
                "best_fixed_expected_loss": 45.0,
                "evpi": 45.0,
                "realizable_value_of_information": 0.0,
                "timely_information_sources": [],
                "late_information_sources": ["recon_flight_late"],
                "recommended_policy": "act_on_prior",
                "policies": {
                    "wait_for_recon": {"information_timely": False, "worst_case_loss": 50.0},
                },
            },
            "invariants": [
                {
                    "expression": "r['evpi'] == 45.0 and r['realizable_value_of_information'] == 0.0",
                    "description": "the same information, five minutes later, is worth nothing",
                },
                {
                    "expression": "r['value_by_policy']['wait_for_recon'] < 0",
                    "description": "waiting for the late observation is worse than acting on the prior",
                },
                {
                    "expression": "r['policies']['wait_for_recon']['worst_case_loss'] > 10.0",
                    "description": "the late observation does not make the resident protectable",
                },
            ],
        },
        readme=f"""
# WG-BM-043 (J3) — Observation arrives too late

## Scenario

**Identical to WG-BM-042 in every respect except one**: the recon flight reports
at **minute 15** instead of minute 5. The decision deadline is still minute 10.

| | `w_north` | `w_south` |
|---|---|---|
| `evacuate_north` | 0 | 90 |
| `evacuate_south` | 95 | 0 |
| `shelter` | 50 | 50 |

## Derivation

The decision problem is unchanged, so:

```
clairvoyant expected loss = 0
best fixed action         = evacuate_north, expected loss 45
EVPI                      = 45          <- exactly as in WG-BM-042
```

But the observation can no longer influence the action. A decision maker who
waits for it has, at minute 10, not evacuated — which is the shelter outcome:

```
expected loss, wait_for_recon = 0.5 * 50 + 0.5 * 50 = 50
expected loss, act_on_prior   = 45
value of waiting              = 45 - 50 = -5
realisable value of information = 0
```

In the realised world (`w_north`) acting on the prior happens to be exactly
right and loses 0, while waiting loses 50.

The worst case under the waiting policy is 50, still outside the acceptable
threshold of {ACCEPTABLE_LOSS:.0f}: **the late observation does not make the resident
protectable.**

## The three-way comparison

| | J1 (WG-BM-041) | J2 (WG-BM-042) | J3 (WG-BM-043) |
|---|---|---|---|
| robust action on the prior | yes | no | no |
| observation available before deadline | yes | yes | **no** |
| EVPI | 0 | 45 | **45** |
| realisable value of the observation | 0 | **45** | **0** |
| protectable at the end | yes | yes | **no** |

J1 and J3 both have zero realisable value, for opposite reasons: in J1 there is
nothing worth knowing, in J3 there is a great deal worth knowing and no way to
know it in time. A system that reports only "value of information = 0" for both
has collapsed two situations that demand completely different responses — accept
the robust action in J1, and change the observing system, the deadline, or the
action set in J3.

## The design consequence

EVPI is a property of the decision problem. Realisable value is a property of
the decision problem **and** the observing system's latency. A sensing
investment case built on EVPI alone will fund instruments whose data arrive
after every deadline they were bought to inform.

The corresponding engineering question is not "how accurate can this sensor be?"
but "what is the latest moment at which its output can still change an action,
and does it report before then?" — the same question WG-BM-030 (G3) asks of
forecasts.

The `forecast_always_trusted` mutation removes the timeliness check, making the
late observation usable and its value +45; this benchmark is one of its
declared detectors.

## Expected

| Quantity | Value |
|---|---|
| EVPI | 45 |
| realisable value of information | **0** |
| value of waiting for the recon | **-5** |
| worst case when waiting | 50 (threshold {ACCEPTABLE_LOSS:.0f}) |
| recommended policy | `act_on_prior` |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
