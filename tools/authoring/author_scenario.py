"""Author the H family: scenario / uncertainty benchmarks (WG-BM-034..036)."""

from __future__ import annotations

from common import report, write_benchmark

SCRIPT = "author_scenario.py"
TOLERANCE = {"default": 1.0e-09}

# H3: five base scenarios plus two rare extremes.
BASE_P = 0.1996        # rescaled base probability once the two extremes are added
EXTREME_P = 0.001


def main() -> None:
    written = []

    # ------------------------------------------------------------------ H1
    all_scenarios = ["s_both_closed", "s_both_open", "s_north_only", "s_south_only", "s_none_closed"]
    written.append(write_benchmark(
        directory="benchmarks/statistics/WG-BM-034_H1_correlated_edge_hazards",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-034",
            "label": "H1",
            "title": "Perfectly correlated road failures: multiplying marginals is wrong by 3.3x",
            "category": "scenario_uncertainty",
            "difficulty": "adversarial",
            "purpose": "Two roads with marginal failure probability 0.3 each fail together. The "
                       "probability of losing all egress is 0.3, not 0.09, and the difference "
                       "flips the decision.",
            "solver": "scenario.ensemble_analysis",
            "assumptions": {
                "failure_correlation": "perfect",
                "marginal_failure_probability": 0.3,
                "egress_lost_when": "both roads closed",
            },
            "expected_behavior": {
                "edge_failure": {
                    "joint_all_closed_probability": 0.3,
                    "joint_under_independence": 0.09,
                },
            },
            "tolerance": TOLERANCE,
            "exactness": "CLOSED_FORM",
            "detects": ["correlation_ignored", "joint_from_marginals"],
            "mutations_expected_to_fail": ["independent_edge_failures"],
            "hand_checkable": True,
        },
        inputs={
            "scenario_analysis": {
                "description": "Two egress roads out of the same valley, both threatened by the "
                               "same front from the same wind. Either both survive or both are "
                               "lost. The independence-assumed ensemble is included so the two "
                               "analyses can be compared directly.",
                "cvar_alpha": 0.9,
                "actions": ["prepare_for_isolation", "assume_egress"],
                "losses": {
                    "prepare_for_isolation": {s: 20.0 for s in all_scenarios},
                    "assume_egress": {
                        "s_both_closed": 100.0,
                        "s_both_open": 0.0,
                        "s_north_only": 0.0,
                        "s_south_only": 0.0,
                        "s_none_closed": 0.0,
                    },
                },
                "ensembles": [
                    {
                        "id": "correlated_truth",
                        "scenarios": [
                            {"id": "s_both_closed", "probability": 0.3},
                            {"id": "s_both_open", "probability": 0.7},
                        ],
                    },
                    {
                        "id": "independence_assumed",
                        "scenarios": [
                            {"id": "s_both_closed", "probability": 0.09},
                            {"id": "s_north_only", "probability": 0.21},
                            {"id": "s_south_only", "probability": 0.21},
                            {"id": "s_none_closed", "probability": 0.49},
                        ],
                    },
                ],
                "edge_failure": {
                    "ensemble": "correlated_truth",
                    "edges": ["north_road", "south_road"],
                    "states": {
                        "s_both_closed": {"north_road": "closed", "south_road": "closed"},
                        "s_both_open": {"north_road": "open", "south_road": "open"},
                    },
                },
                "ensemble_comparison": {
                    "from": "correlated_truth",
                    "to": "independence_assumed",
                    "action": "assume_egress",
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-034",
            "source": "hand_derivation",
            "derivation": (
                "Each road is closed in the single scenario s_both_closed, which has probability "
                "0.3, so each marginal closure probability is 0.3. The joint probability that "
                "both are closed is also 0.3, because the scenario set contains no world in which "
                "exactly one is closed. Multiplying the marginals gives 0.3 * 0.3 = 0.09, an "
                "understatement by a factor of 10/3 = 3.333. "
                "The decision consequence: preparing for isolation costs 20 regardless; assuming "
                "egress costs 100 if both roads are closed and 0 otherwise. Under the true "
                "correlated ensemble the expected loss of assuming egress is 0.3 * 100 = 30, "
                "worse than preparing, so the right action is to prepare. Under the "
                "independence-implied ensemble it is 0.09 * 100 = 9, better than preparing, so "
                "the recommended action flips to assuming egress. The independence assumption "
                "does not merely mis-state a probability; it reverses the decision."
            ),
            "results": {
                "cvar_alpha": 0.9,
                "edge_failure": {
                    "edges": ["north_road", "south_road"],
                    "marginal_closure_probability": {"north_road": 0.3, "south_road": 0.3},
                    "joint_all_closed_probability": 0.3,
                    "joint_under_independence": 0.09,
                    "independence_error_factor": 0.3 / (0.3 * 0.3),
                    "probability_no_egress": 0.3,
                    "correlation_matters": True,
                },
                "ensembles": {
                    "correlated_truth": {
                        "scenario_count": 2,
                        "expected_loss": {"prepare_for_isolation": 20.0, "assume_egress": 30.0},
                        "best_action_by_expected_loss": "prepare_for_isolation",
                        "cvar": {"prepare_for_isolation": 20.0, "assume_egress": 100.0},
                        "max_regret": {"prepare_for_isolation": 20.0, "assume_egress": 80.0},
                        "minimax_regret_action": "prepare_for_isolation",
                        "sup_regret": 20.0,
                        "clairvoyant_expected_loss": 6.0,
                        "evpi": 14.0,
                    },
                    "independence_assumed": {
                        "scenario_count": 4,
                        "expected_loss": {"prepare_for_isolation": 20.0, "assume_egress": 9.0},
                        "best_action_by_expected_loss": "assume_egress",
                        "clairvoyant_expected_loss": 1.8,
                        "evpi": 7.2,
                    },
                },
                "ensemble_comparison": {
                    "from": "correlated_truth",
                    "to": "independence_assumed",
                    "action": "assume_egress",
                    "expected_loss_change": -21.0,
                    "scenario_count_change": 2,
                },
            },
            "invariants": [
                {
                    "expression": "r['ensembles']['correlated_truth']['best_action_by_expected_loss'] != r['ensembles']['independence_assumed']['best_action_by_expected_loss']",
                    "description": "the independence assumption reverses the recommended action",
                },
                {
                    "expression": "r['edge_failure']['independence_error_factor'] > 3.0",
                    "description": "the joint failure probability is understated more than threefold",
                },
            ],
        },
        readme="""
# WG-BM-034 (H1) — Perfectly correlated edge hazards

## Scenario

A valley with two egress roads. Both are threatened by the same front driven by
the same wind, so in this scenario set either both survive or both are lost.

```
s_both_closed   p = 0.3    north closed, south closed
s_both_open     p = 0.7    north open,   south open
```

Decision: prepare for isolation (cost 20 whatever happens) or assume egress
(cost 0 if any road survives, 100 if none does).

## Derivation

Each road is closed only in `s_both_closed`, so:

```
marginal P(north closed) = 0.3
marginal P(south closed) = 0.3
true P(both closed)      = 0.3        <- read off the scenario set
P(both closed) assuming independence = 0.3 * 0.3 = 0.09
understatement factor    = 0.3 / 0.09 = 10/3 = 3.33
```

### The decision consequence

| | true correlated ensemble | independence-implied ensemble |
|---|---|---|
| `prepare_for_isolation` | 20 | 20 |
| `assume_egress` | `0.3 * 100 = ` **30** | `0.09 * 100 = ` **9** |
| recommended action | **prepare** | **assume egress** |

The independence assumption does not merely mis-state a probability by a factor
of three. It **reverses the decision**, and it does so in the direction of doing
less.

## Why this is not a corner case

Road failures in a wildfire are driven by a small number of shared causes: one
front, one wind field, one fuel state, often one ridge line. Conditional on the
day, they are close to comonotone. Marginal failure probabilities, on the other
hand, are the natural output of a per-edge hazard model, and multiplying them is
the natural next step. The combination is a standard and severe error:

* the understatement grows with the number of redundant roads — three
  perfectly-correlated roads at 0.3 each give `0.3` truth against `0.027`
  assumed, a factor of 11;
* it is worst exactly where redundancy is being claimed as a safety argument;
* it cannot be detected from the marginals, which are correct.

The only reliable defence is to carry **joint scenarios** rather than per-edge
probabilities through the pipeline, which is what this benchmark's input format
does deliberately.

The mutation `independent_edge_failures` reconstructs the joint from the
marginals; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| marginal closure probability, each road | 0.3 |
| true joint probability both closed | **0.3** |
| joint under independence | **0.09** |
| understatement factor | 3.33 |
| best action, true ensemble | `prepare_for_isolation` |
| best action, independence ensemble | `assume_egress` |
""",
    ))

    # ------------------------------------------------------------------ H2
    written.append(write_benchmark(
        directory="benchmarks/statistics/WG-BM-035_H2_mutually_exclusive_scenarios",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-035",
            "label": "H2",
            "title": "Mutually exclusive scenarios: averaging the inputs says both routes are fine",
            "category": "scenario_uncertainty",
            "difficulty": "adversarial",
            "purpose": "Route A is right in scenario 1 and fatal in scenario 2, and vice versa. "
                       "Averaging the fire fields produces a world in which neither route is "
                       "blocked and the expected loss is zero. Averaging the losses gives 50.",
            "solver": "scenario.ensemble_analysis",
            "assumptions": {
                "scenarios_mutually_exclusive": True,
                "averaged_world_losses_are_given": True,
                "cvar_alpha": 0.9,
            },
            "expected_behavior": {
                "averaged_world_best_action": "route_a",
                "ensembles": {"base": {"best_action_by_expected_loss": "hold"}},
            },
            "tolerance": TOLERANCE,
            "exactness": "CLOSED_FORM",
            "detects": ["average_of_inputs_fallacy", "scenario_blending"],
            "mutations_expected_to_fail": ["average_scenario_inputs"],
            "hand_checkable": True,
        },
        inputs={
            "scenario_analysis": {
                "description": "Two equally likely wind scenarios. In s1 the fire runs south and "
                               "closes route B; in s2 it runs north and closes route A. Averaging "
                               "the two fire fields puts a half-strength front on both sides, "
                               "which blocks neither route.",
                "cvar_alpha": 0.9,
                "actions": ["route_a", "route_b", "hold"],
                "losses": {
                    "route_a": {"s1": 0.0, "s2": 100.0},
                    "route_b": {"s1": 100.0, "s2": 0.0},
                    "hold": {"s1": 30.0, "s2": 30.0},
                },
                "ensembles": [
                    {
                        "id": "base",
                        "scenarios": [
                            {"id": "s1", "probability": 0.5, "note": "fire runs south"},
                            {"id": "s2", "probability": 0.5, "note": "fire runs north"},
                        ],
                    }
                ],
                "averaged_world": {
                    "description": "The mean of the two fire fields: a half-intensity front on "
                                   "each side, insufficient to close either road.",
                    "losses": {"route_a": 0.0, "route_b": 0.0, "hold": 30.0},
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-035",
            "source": "hand_derivation",
            "derivation": (
                "Expected losses over the scenario set: route_a 0.5*0 + 0.5*100 = 50, route_b "
                "0.5*100 + 0.5*0 = 50, hold 30. The best action by expected loss is to hold. "
                "The best achievable loss in each scenario is 0, so regret for route_a is 0 in s1 "
                "and 100 in s2 (maximum 100), likewise 100 for route_b, and 30 for hold; the "
                "minimax-regret action is also to hold, with a sup-regret of 30. The clairvoyant "
                "expected loss is 0, so EVPI is 30 - 0 = 30: knowing the wind direction would "
                "remove the whole loss. "
                "Averaging the two fire fields instead produces a world with a half-strength "
                "front on each side, which closes neither road, so both routes score 0 there and "
                "the averaged-world analysis recommends route_a. Taking route_a in the real "
                "problem costs 50 in expectation and 100 half the time."
            ),
            "results": {
                "cvar_alpha": 0.9,
                "ensembles": {
                    "base": {
                        "scenario_count": 2,
                        "expected_loss": {"route_a": 50.0, "route_b": 50.0, "hold": 30.0},
                        "best_action_by_expected_loss": "hold",
                        "cvar": {"route_a": 100.0, "route_b": 100.0, "hold": 30.0},
                        "max_regret": {"route_a": 100.0, "route_b": 100.0, "hold": 30.0},
                        "minimax_regret_action": "hold",
                        "sup_regret": 30.0,
                        "clairvoyant_expected_loss": 0.0,
                        "evpi": 30.0,
                        "worst_case_loss": {"route_a": 100.0, "route_b": 100.0, "hold": 30.0},
                    }
                },
                "averaged_world_loss": {"route_a": 0.0, "route_b": 0.0, "hold": 30.0},
                "averaged_world_best_action": "route_a",
            },
            "invariants": [
                {
                    "expression": "r['averaged_world_best_action'] != r['ensembles']['base']['best_action_by_expected_loss']",
                    "description": "averaging the inputs and averaging the losses disagree",
                },
                {
                    "expression": "r['averaged_world_loss']['route_a'] < r['ensembles']['base']['expected_loss']['route_a']",
                    "description": "the averaged world is more benign than any real scenario",
                },
            ],
        },
        readme="""
# WG-BM-035 (H2) — Mutually exclusive scenarios

## Scenario

Two equally likely wind scenarios. In `s1` the fire runs south and closes route
B; in `s2` it runs north and closes route A.

| | s1 (fire runs south) | s2 (fire runs north) |
|---|---|---|
| `route_a` | 0 | **100** |
| `route_b` | **100** | 0 |
| `hold` | 30 | 30 |

## Derivation

```
E[loss | route_a] = 0.5 * 0   + 0.5 * 100 = 50
E[loss | route_b] = 0.5 * 100 + 0.5 * 0   = 50
E[loss | hold]    = 30                              <- best
```

Regret against the best action in each scenario (0 in both):

```
max regret route_a = 100      max regret route_b = 100      max regret hold = 30
minimax-regret action = hold, sup-regret = 30
clairvoyant expected loss = 0       EVPI = 30
```

Both the expected-loss and the minimax-regret criteria pick `hold`, and knowing
the wind direction would be worth 30 — the entire loss.

## The averaged-input fallacy

Now average the two **fire fields** instead of the two **losses**. The mean
field has a half-intensity front on each side of the valley, and a half-intensity
front closes neither road:

```
loss in the averaged world:  route_a 0,  route_b 0,  hold 30
recommended action:          route_a
```

The averaged world is **more benign than any scenario that can actually
happen**. It contains no blocked road, because the blockage in `s1` and the
blockage in `s2` are in different places and each is diluted to half strength.
Acting on it gives route A, which costs 100 half the time.

This is not an artefact of a crude averaging scheme. It is a general property:
the loss function is not linear in the hazard field, so

```
loss(E[field])  !=  E[loss(field)]
```

and for threshold-shaped losses — a road is open or it is not — the left-hand
side is systematically the optimistic one. Averaging ensemble members into a
"mean fire perimeter" and then routing on it reproduces this error exactly.

## The correct order of operations

**Evaluate the decision in each scenario, then average the outcomes.** Never
average the scenarios and then evaluate once. The input format of this benchmark
enforces the distinction by making the averaged world a separately declared
object rather than something a solver can compute by accident.

The mutation `average_scenario_inputs` substitutes the averaged-world losses for
the ensemble expectation; this benchmark is its declared detector.

## Expected

| Quantity | Value |
|---|---|
| expected loss, route A / route B / hold | 50 / 50 / **30** |
| best action | `hold` |
| sup-regret of `hold` | 30 |
| EVPI | 30 |
| best action in the averaged world | **`route_a`** (wrong) |
""",
    ))

    # ------------------------------------------------------------------ H3
    base_ids = [f"s{i}" for i in range(1, 6)]
    all_ids_h3 = base_ids + ["s6_extreme", "s7_extreme"]
    losses_h3 = {
        "policy_a": {**{s: 10.0 for s in base_ids}, "s6_extreme": 300.0, "s7_extreme": 250.0},
        "policy_b": {
            "s1": 8.0, "s2": 8.0, "s3": 8.0, "s4": 8.0, "s5": 20.0,
            "s6_extreme": 12.0, "s7_extreme": 12.0,
        },
    }
    expected_a_extended = BASE_P * 10.0 * 5 + EXTREME_P * 300.0 + EXTREME_P * 250.0
    expected_b_extended = BASE_P * (8.0 * 4 + 20.0) + EXTREME_P * 12.0 * 2
    cvar_a_extended = (
        EXTREME_P * 300.0 + EXTREME_P * 250.0 + (0.1 - 2 * EXTREME_P) * 10.0
    ) / 0.1
    written.append(write_benchmark(
        directory="benchmarks/statistics/WG-BM-036_H3_ensemble_size_trap",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-036",
            "label": "H3",
            "title": "Adding two 0.1% scenarios moves expected loss by 0.5 and sup-regret by 8",
            "category": "scenario_uncertainty",
            "difficulty": "adversarial",
            "purpose": "Sup-regret is a maximum over the scenario set, so it grows mechanically "
                       "as scenarios are added, and the minimax-regret recommendation flips on "
                       "0.2% of probability mass. CVaR does not.",
            "solver": "scenario.ensemble_analysis",
            "assumptions": {
                "extreme_scenario_probability": EXTREME_P,
                "base_scenarios_rescaled": True,
                "cvar_alpha": 0.9,
            },
            "expected_behavior": {
                "ensemble_comparison": {
                    "sup_regret_change": 8.0,
                    "minimax_action_changed": True,
                },
            },
            "tolerance": TOLERANCE,
            "exactness": "CLOSED_FORM",
            "detects": ["sup_regret_scales_with_ensemble_size", "worst_case_criterion_instability"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "No mutation is needed here: the benchmark's content is a property of the "
                     "decision criteria themselves, which is exactly why it must be pinned.",
        },
        inputs={
            "scenario_analysis": {
                "description": "A five-member ensemble, then the same ensemble with two "
                               "low-probability extreme members added and the base members "
                               "rescaled to keep the total probability at one.",
                "cvar_alpha": 0.9,
                "actions": ["policy_a", "policy_b"],
                "losses": losses_h3,
                "ensembles": [
                    {
                        "id": "base",
                        "scenarios": [{"id": s, "probability": 0.2} for s in base_ids],
                    },
                    {
                        "id": "extended",
                        "scenarios": (
                            [{"id": s, "probability": BASE_P} for s in base_ids]
                            + [
                                {"id": "s6_extreme", "probability": EXTREME_P},
                                {"id": "s7_extreme", "probability": EXTREME_P},
                            ]
                        ),
                    },
                ],
                "ensemble_comparison": {"from": "base", "to": "extended", "action": "policy_a"},
            }
        },
        expected={
            "benchmark_id": "WG-BM-036",
            "source": "hand_derivation",
            "derivation": (
                "Base ensemble, five members at probability 0.2. policy_a loses 10 everywhere, so "
                "its expected loss is 10. policy_b loses 8 in s1..s4 and 20 in s5, so its "
                "expected loss is (8*4 + 20)/5 = 10.4. The best action per scenario is policy_b "
                "in s1..s4 and policy_a in s5, so policy_a's regret is 2 in s1..s4 and 0 in s5 "
                "(maximum 2) while policy_b's is 0 in s1..s4 and 10 in s5 (maximum 10). The "
                "minimax-regret action is policy_a with a sup-regret of 2. "
                "Now add s6 and s7, each with probability 0.001, rescaling the five base members "
                "to 0.1996 each. In the extremes policy_a loses 300 and 250 while policy_b loses "
                "12, so policy_a's regret becomes 288 and 238 and its maximum jumps to 288; "
                "policy_b's maximum stays at 10. The minimax-regret action flips to policy_b and "
                "the sup-regret rises from 2 to 10, a change of 8. "
                "Expected losses barely move: policy_a goes from 10 to 10.53 and policy_b from "
                "10.4 to about 10.4032. The 0.2% of probability mass that changes the worst-case "
                "recommendation changes the expected loss by half a unit. CVaR at 0.9 moves too, "
                "but proportionately to the mass added: policy_a goes from 10 to 15.3 and "
                "policy_b stays at 20."
            ),
            "results": {
                "cvar_alpha": 0.9,
                "ensembles": {
                    "base": {
                        "scenario_count": 5,
                        "expected_loss": {"policy_a": 10.0, "policy_b": 10.4},
                        "best_action_by_expected_loss": "policy_a",
                        "max_regret": {"policy_a": 2.0, "policy_b": 10.0},
                        "minimax_regret_action": "policy_a",
                        "sup_regret": 2.0,
                        "cvar": {"policy_a": 10.0, "policy_b": 20.0},
                        "worst_case_loss": {"policy_a": 10.0, "policy_b": 20.0},
                    },
                    "extended": {
                        "scenario_count": 7,
                        "expected_loss": {
                            "policy_a": expected_a_extended,
                            "policy_b": expected_b_extended,
                        },
                        "best_action_by_expected_loss": "policy_b",
                        "max_regret": {"policy_a": 288.0, "policy_b": 10.0},
                        "minimax_regret_action": "policy_b",
                        "sup_regret": 10.0,
                        "cvar": {"policy_a": cvar_a_extended, "policy_b": 20.0},
                        "worst_case_loss": {"policy_a": 300.0, "policy_b": 20.0},
                    },
                },
                "ensemble_comparison": {
                    "from": "base",
                    "to": "extended",
                    "action": "policy_a",
                    "expected_loss_change": expected_a_extended - 10.0,
                    "sup_regret_change": 8.0,
                    "cvar_change": cvar_a_extended - 10.0,
                    "minimax_action_changed": True,
                    "scenario_count_change": 2,
                },
            },
            "invariants": [
                {
                    "expression": "abs(r['ensemble_comparison']['expected_loss_change']) < 1.0 < r['ensemble_comparison']['sup_regret_change']",
                    "description": "expected loss barely moves while sup-regret jumps",
                },
                {
                    "expression": "r['ensemble_comparison']['minimax_action_changed'] is True",
                    "description": "the worst-case recommendation flips on 0.2% of probability mass",
                },
            ],
        },
        readme="""
# WG-BM-036 (H3) — Ensemble size trap

## Scenario

A five-member ensemble, each member at probability 0.2:

| | s1 | s2 | s3 | s4 | s5 |
|---|---|---|---|---|---|
| `policy_a` | 10 | 10 | 10 | 10 | 10 |
| `policy_b` | 8 | 8 | 8 | 8 | 20 |

Then the **same ensemble** with two extreme members added at probability 0.001
each, the base members rescaled to 0.1996 so the total is still 1:

| | s6 | s7 |
|---|---|---|
| `policy_a` | 300 | 250 |
| `policy_b` | 12 | 12 |

## Derivation

**Base ensemble**

```
E[policy_a] = 10                 E[policy_b] = (8*4 + 20)/5 = 10.4
best per scenario: policy_b in s1..s4, policy_a in s5
max regret: policy_a = 2,        policy_b = 10
minimax-regret action = policy_a,  sup-regret = 2
```

**Extended ensemble**

```
E[policy_a] = 0.1996*10*5 + 0.001*300 + 0.001*250 = 10.53
E[policy_b] = 0.1996*(8*4+20) + 0.001*12*2        = 10.4032
max regret: policy_a = 288,      policy_b = 10
minimax-regret action = policy_b,  sup-regret = 10
```

| Quantity | Base | Extended | Change |
|---|---|---|---|
| expected loss, `policy_a` | 10 | 10.53 | **+0.53** |
| expected loss, `policy_b` | 10.4 | 10.4032 | +0.003 |
| sup-regret | 2 | 10 | **+8** |
| minimax-regret action | `policy_a` | **`policy_b`** | flipped |
| CVaR(0.9), `policy_a` | 10 | 15.3 | +5.3 |
| CVaR(0.9), `policy_b` | 20 | 20 | 0 |

## What is actually happening

Sup-regret is a **maximum over the scenario set**. A maximum has no dependence
on probability at all: a scenario of probability 0.001 counts exactly as much as
one of probability 0.2, and a scenario of probability `1e-12` would count the
same again. Consequently:

* adding scenarios can only increase sup-regret, never decrease it;
* the recommendation under minimax regret is decided by whichever member happens
  to be the most extreme, so it is a function of **how the ensemble was
  sampled**, not only of the physics;
* two teams with the same model and different ensemble sizes will reach
  different "robust" recommendations and neither will be wrong on its own terms.

CVaR at a fixed level behaves differently because it is an average over a fixed
*probability mass*, not over a set of members. Adding 0.2% of mass moves
CVaR(0.9) by at most that mass times the loss difference. It is still a tail
measure, and it is still sensitive to the extremes, but it is sensitive
*proportionately*.

## What this benchmark asserts, and what it does not

It asserts the numbers above. It does **not** assert that CVaR is the right
criterion and minimax regret the wrong one. Sup-regret answers a legitimate
question — *what is the worst thing that can happen if I am wrong?* — and in a
setting where the scenario set is a genuine bounded uncertainty set rather than
a sample, it is exactly right.

What a system must not do is report a sup-regret without reporting the size and
provenance of the scenario set alongside it, or compare sup-regrets computed
over different ensembles as if they were commensurable. This benchmark exists so
that the mechanical dependence is visible and quantified rather than argued
about.

## No mutation

No mutation is declared for this benchmark. The behaviour it pins is a property
of the decision criteria themselves, not a bug that can be injected — which is
precisely why the numbers need to be written down.
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
