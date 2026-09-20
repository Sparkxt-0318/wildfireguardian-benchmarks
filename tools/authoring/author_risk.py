"""Author the L family: probabilistic decision risk (WG-BM-059..063)."""

from __future__ import annotations

from common import report, write_benchmark

SCRIPT = "author_risk.py"
TOL = {"default": 1.0e-12}

L3_W = (0.34, 0.33, 0.33)
L3_EVAC_N = L3_W[0] * 8.0 + L3_W[1] * 50.0 + L3_W[2] * 50.0
L3_EVAC_S = L3_W[0] * 50.0 + L3_W[1] * 8.0 + L3_W[2] * 50.0
L3_EVAC_E = L3_W[0] * 50.0 + L3_W[1] * 50.0 + L3_W[2] * 8.0
L3_MIN_PERTURBATION = (L3_EVAC_N - 6.0) / L3_W[0]

L4_EB = 0.97 * 10.0 + 0.03 * 17.0
L4_MARGIN = L4_EB - 10.0
L4_MIN_PERTURBATION = L4_MARGIN / 0.97


def main() -> None:
    written = []

    # ------------------------------------------------------------------ L1
    written.append(write_benchmark(
        directory="benchmarks/risk/WG-BM-059_L1_expectation_versus_worst_case",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-059",
            "label": "L1",
            "title": "Better average, worse worst case, and no winner declared",
            "category": "risk",
            "difficulty": "basic",
            "purpose": "Both metrics are computed exactly and neither is preferred. A suite that "
                       "always names a winner has an undeclared risk attitude built into it.",
            "solver": "risk.objective_comparison",
            "assumptions": {
                "objective": "report_only",
                "no_risk_attitude_assumed": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "scenario_ensemble",
                "expected_value": "reported for both criteria; no winner",
            },
            "expected_behavior": {
                "best_by_expected_loss": "policy_a",
                "best_by_worst_case": "policy_b",
                "winner_declared": False,
            },
            "tolerance": TOL,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["undeclared_risk_attitude", "premature_winner"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "No mutation is claimed. The content is that the solver declines to choose, "
                     "which is a property of the declared objective rather than a bug to inject.",
        },
        inputs={
            "risk": {
                "description": "Two staging policies over two weather scenarios. A is free on the "
                               "likely day and very costly on the unlikely one; B is mediocre on "
                               "both.",
                "objective": "report_only",
                "cvar_alpha": 0.9,
                "scenarios": [
                    {"id": "s_benign", "probability": 0.8},
                    {"id": "s_severe", "probability": 0.2},
                ],
                "actions": ["policy_a", "policy_b"],
                "losses": {
                    "policy_a": {"s_benign": 0.0, "s_severe": 60.0},
                    "policy_b": {"s_benign": 15.0, "s_severe": 25.0},
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-059",
            "source": "exhaustive_enumeration",
            "derivation": (
                "E[policy_a] = 0.8 * 0 + 0.2 * 60 = 12 and E[policy_b] = 0.8 * 15 + 0.2 * 25 = "
                "12 + 5 = 17, so A has the better average by 5. "
                "The worst case of A is 60 and of B is 25, so B is better there by 35. "
                "At alpha = 0.9 the worst tenth of the probability mass falls inside the severe "
                "scenario for both policies, so CVaR equals the severe-scenario loss: 60 for A "
                "and 25 for B. "
                "Regret against the best action in each scenario - 0 in benign, 25 in severe - is "
                "at most 35 for A and at most 15 for B, so B is also the minimax-regret choice. "
                "The clairvoyant expected loss is 0.8 * 0 + 0.2 * 25 = 5, so EVPI is 12 - 5 = 7. "
                "Three criteria, two different answers, and the declared objective is "
                "report_only, so no action is recommended."
            ),
            "results": {
                "objective": "report_only",
                "expected_loss": {"policy_a": 12.0, "policy_b": 17.0},
                "worst_case_loss": {"policy_a": 60.0, "policy_b": 25.0},
                "cvar": {"policy_a": 60.0, "policy_b": 25.0},
                "max_regret": {"policy_a": 35.0, "policy_b": 15.0},
                "best_by_expected_loss": "policy_a",
                "best_by_worst_case": "policy_b",
                "best_by_cvar": "policy_b",
                "rankings_conflict": True,
                "recommended_action": None,
                "winner_declared": False,
                "clairvoyant_expected_loss": 5.0,
                "evpi": 7.0,
            },
            "invariants": [
                {
                    "expression": "r['expected_loss']['policy_a'] < r['expected_loss']['policy_b']",
                    "description": "A wins on the average",
                },
                {
                    "expression": "r['worst_case_loss']['policy_b'] < r['worst_case_loss']['policy_a']",
                    "description": "B wins on the worst case",
                },
                {
                    "expression": "r['recommended_action'] is None",
                    "description": "and the suite declines to pick between them",
                },
            ],
        },
        readme="""
# WG-BM-059 (L1) — Expectation versus worst case

## Scenario

| | benign (p = 0.8) | severe (p = 0.2) |
|---|---|---|
| `policy_a` | 0 | **60** |
| `policy_b` | 15 | 25 |

## Derivation

```
E[policy_a] = 0.8 * 0  + 0.2 * 60 = 12          <- better average
E[policy_b] = 0.8 * 15 + 0.2 * 25 = 17

worst(policy_a) = 60
worst(policy_b) = 25                            <- better worst case

CVaR(0.9): the worst tenth of the mass lies inside the severe scenario for both,
so CVaR equals the severe loss:  60  and  25

max regret (best per scenario: 0 benign, 25 severe):  35  and  15
clairvoyant = 0.8 * 0 + 0.2 * 25 = 5            EVPI = 12 - 5 = 7
```

**A is better by 5 on the average and worse by 35 in the worst case.**

## Why no winner

The declared objective is `report_only`, and the result document's
`recommended_action` is `null`.

This is not indecision. Choosing between 5 units of expected loss and 35 units
of worst-case loss requires a **risk attitude**, and a risk attitude is a policy
input — it belongs to whoever is accountable for the outcome, not to the
software. A system that always returns a single ranked answer has one anyway; it
is simply undeclared, and in practice it is almost always "minimise the mean",
because that is the easiest thing to compute.

What the suite requires instead:

* both numbers are computed and reported;
* the objective is a declared input (`expected_loss`, `cvar`, `worst_case` or
  `report_only`);
* the recommendation follows the declared objective and nothing else.

WG-BM-060 exercises the same machinery with the objective set to CVaR, where
there *is* a right answer and ignoring the declaration produces the wrong one.

## Expected

| Quantity | `policy_a` | `policy_b` |
|---|---|---|
| expected loss | **12** | 17 |
| worst case | 60 | **25** |
| CVaR(0.9) | 60 | **25** |
| max regret | 35 | **15** |
| recommended | — | — |
""",
    ))

    # ------------------------------------------------------------------ L2
    written.append(write_benchmark(
        directory="benchmarks/risk/WG-BM-060_L2_expectation_versus_cvar",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-060",
            "label": "L2",
            "title": "Ranking reversal between the mean and CVaR, with the objective declared",
            "category": "risk",
            "difficulty": "intermediate",
            "purpose": "A three-outcome distribution where A has the better mean by 2.1 and a "
                       "CVaR five times worse. The declared objective is CVaR and the "
                       "recommendation must follow it.",
            "solver": "risk.objective_comparison",
            "assumptions": {
                "objective": "cvar",
                "cvar_alpha": 0.9,
                "tail_boundary_splits_an_atom": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "scenario_ensemble",
                "expected_value": "E 17 vs 19.1; CVaR(0.9) 160 vs 29",
            },
            "expected_behavior": {
                "best_by_expected_loss": "policy_a",
                "best_by_cvar": "policy_b",
                "recommended_action": "policy_b",
            },
            "tolerance": TOL,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["declared_objective_ignored", "tail_risk_ignored"],
            "mutations_expected_to_fail": ["objective_ignored_use_mean"],
            "hand_checkable": True,
        },
        inputs={
            "risk": {
                "description": "Two evacuation-timing policies over three outcomes. A is usually "
                               "free, occasionally mildly costly, and rarely catastrophic; B is "
                               "steadily mediocre with a bounded tail. The programme's declared "
                               "objective is CVaR at 0.9.",
                "objective": "cvar",
                "cvar_alpha": 0.9,
                "scenarios": [
                    {"id": "s_routine", "probability": 0.85},
                    {"id": "s_awkward", "probability": 0.10},
                    {"id": "s_extreme", "probability": 0.05},
                ],
                "actions": ["policy_a", "policy_b"],
                "losses": {
                    "policy_a": {"s_routine": 0.0, "s_awkward": 20.0, "s_extreme": 300.0},
                    "policy_b": {"s_routine": 18.0, "s_awkward": 18.0, "s_extreme": 40.0},
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-060",
            "source": "exhaustive_enumeration",
            "derivation": (
                "E[policy_a] = 0.85 * 0 + 0.10 * 20 + 0.05 * 300 = 0 + 2 + 15 = 17 and "
                "E[policy_b] = 0.85 * 18 + 0.10 * 18 + 0.05 * 40 = 15.3 + 1.8 + 2 = 19.1, so A "
                "has the better mean by 2.1. "
                "CVaR at 0.9 averages the worst tenth of the probability mass. For A that tenth "
                "is the whole 0.05 atom at 300 plus half of the 0.10 atom at 20: "
                "(0.05 * 300 + 0.05 * 20) / 0.1 = (15 + 1) / 0.1 = 160. For B the worst tenth is "
                "the 0.05 atom at 40 plus half the mass at 18: (0.05 * 40 + 0.05 * 18) / 0.1 = "
                "(2 + 0.9) / 0.1 = 29. A's conditional tail loss is five and a half times B's. "
                "The best action in each scenario is A in the routine case, B in the other two, "
                "so A's maximum regret is 260 and B's is 18, and B is also the minimax-regret "
                "choice. The clairvoyant expected loss is 0.85 * 0 + 0.10 * 18 + 0.05 * 40 = 3.8, "
                "so EVPI is 17 - 3.8 = 13.2. "
                "With the objective declared as CVaR the recommendation is policy_b. Reporting "
                "the expected-loss winner instead silently substitutes one risk attitude for "
                "another."
            ),
            "results": {
                "objective": "cvar",
                "cvar_alpha": 0.9,
                "expected_loss": {"policy_a": 17.0, "policy_b": 19.1},
                "cvar": {"policy_a": 160.0, "policy_b": 29.0},
                "worst_case_loss": {"policy_a": 300.0, "policy_b": 40.0},
                "max_regret": {"policy_a": 260.0, "policy_b": 18.0},
                "best_by_expected_loss": "policy_a",
                "best_by_cvar": "policy_b",
                "best_by_worst_case": "policy_b",
                "rankings_conflict": True,
                "recommended_action": "policy_b",
                "winner_declared": True,
                "clairvoyant_expected_loss": 3.8,
                "evpi": 13.2,
            },
            "invariants": [
                {
                    "expression": "r['expected_loss']['policy_a'] < r['expected_loss']['policy_b']",
                    "description": "A has the better mean",
                },
                {
                    "expression": "r['cvar']['policy_a'] > 5 * r['cvar']['policy_b']",
                    "description": "and a conditional tail loss over five times worse",
                },
                {
                    "expression": "r['recommended_action'] == r['best_by_cvar']",
                    "description": "the recommendation follows the declared objective",
                },
            ],
        },
        readme="""
# WG-BM-060 (L2) — Expectation versus CVaR

## Scenario

| | routine (0.85) | awkward (0.10) | extreme (0.05) |
|---|---|---|---|
| `policy_a` | 0 | 20 | **300** |
| `policy_b` | 18 | 18 | 40 |

Declared objective: **CVaR at alpha = 0.9.**

## Derivation

```
E[policy_a] = 0 + 2 + 15        = 17         <- better mean
E[policy_b] = 15.3 + 1.8 + 2    = 19.1
```

CVaR averages the worst tenth of the **probability mass**, so the tail boundary
falls inside an atom and the atom is split:

```
CVaR_0.9(A) = (0.05 * 300 + 0.05 * 20) / 0.1 = (15 + 1)  / 0.1 = 160
CVaR_0.9(B) = (0.05 * 40  + 0.05 * 18) / 0.1 = (2 + 0.9) / 0.1 = 29
```

A's conditional tail loss is **5.5 times** B's, for 2.1 units of better average.

```
max regret:  A 260,  B 18        ->  B is also minimax-regret
clairvoyant = 3.8                ->  EVPI = 13.2
```

**Declared objective is CVaR → recommend `policy_b`.**

## The atom split matters

This is the reason the benchmark has three outcomes rather than two. With two
outcomes the worst tenth of the mass usually sits entirely inside the worst
atom, and CVaR degenerates to the maximum — at which point an implementation
that computes the maximum and calls it CVaR passes. Here the boundary falls
strictly inside the `awkward` atom, and getting 160 rather than 300 (the
maximum) or 158 (dropping the partial atom) requires the proportional split.

## The interface with evaluation

The objective is an input, and the recommendation follows it. That matters for
`wildfireguardian-evaluation`: a policy comparison reported without its
objective is not interpretable, and two comparisons with different objectives
are not commensurable. The `objective_ignored_use_mean` mutation reports the
expected-loss winner whatever the configuration says; this benchmark is its
declared detector.

## Expected

| Quantity | `policy_a` | `policy_b` |
|---|---|---|
| expected loss | **17** | 19.1 |
| CVaR(0.9) | 160 | **29** |
| worst case | 300 | **40** |
| max regret | 260 | **18** |
| recommended (objective = CVaR) | | **yes** |
""",
    ))

    # ------------------------------------------------------------------ L3
    written.append(write_benchmark(
        directory="benchmarks/risk/WG-BM-061_L3_unresolved_state_resolved_decision",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-061",
            "label": "L3",
            "title": "The world is unresolved and the decision is not",
            "category": "risk",
            "difficulty": "adversarial",
            "purpose": "Three near-equal scenarios and one action that is optimal in all of them. "
                       "EVPI is exactly zero: uncertainty about the world does not imply a need "
                       "for more information.",
            "solver": "risk.objective_comparison",
            "assumptions": {
                "objective": "expected_loss",
                "state_resolution_threshold": 0.8,
                "acceptable_loss": 10,
                "perturbation_tolerance": 1.0,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "scenario_ensemble",
                "expected_value": "EVPI = 0 with maximum scenario probability 0.34",
            },
            "expected_behavior": {
                "state_resolved": False,
                "decision_resolved": True,
                "evpi": 0.0,
            },
            "tolerance": TOL,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["uncertainty_conflated_with_indecision", "information_demanded_unnecessarily"],
            "mutations_expected_to_fail": ["unresolved_state_blocks_decision"],
            "hand_checkable": True,
            "notes": "The governance case: this is the counterexample to 'we do not know which "
                     "scenario we are in, so we cannot act'.",
        },
        inputs={
            "risk": {
                "description": "The fire could break north, south or east, and the ensemble is "
                               "close to uniform. Evacuating in any one direction is a gamble; "
                               "reinforcing the community refuge is acceptable whichever way it "
                               "goes, and in fact optimal in every scenario.",
                "objective": "expected_loss",
                "cvar_alpha": 0.9,
                "acceptable_loss": 10.0,
                "state_resolution_threshold": 0.8,
                "perturbation_tolerance": 1.0,
                "scenarios": [
                    {"id": "omega_north", "probability": L3_W[0]},
                    {"id": "omega_south", "probability": L3_W[1]},
                    {"id": "omega_east", "probability": L3_W[2]},
                ],
                "actions": ["reinforce_refuge", "evacuate_north", "evacuate_south", "evacuate_east"],
                "losses": {
                    "reinforce_refuge": {
                        "omega_north": 6.0, "omega_south": 6.0, "omega_east": 6.0,
                    },
                    "evacuate_north": {
                        "omega_north": 8.0, "omega_south": 50.0, "omega_east": 50.0,
                    },
                    "evacuate_south": {
                        "omega_north": 50.0, "omega_south": 8.0, "omega_east": 50.0,
                    },
                    "evacuate_east": {
                        "omega_north": 50.0, "omega_south": 50.0, "omega_east": 8.0,
                    },
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-061",
            "source": "exhaustive_enumeration",
            "derivation": (
                "Reinforcing the refuge costs 6 in every scenario, and every evacuation costs at "
                "least 8 even in the scenario it was chosen for. Reinforcing is therefore the "
                "best action in each scenario taken separately, not merely on average, so the "
                "clairvoyant expected loss equals its expected loss of 6 and EVPI is exactly 0. "
                "The ensemble is almost uniform: the largest scenario weight is 0.34, far below "
                "the declared resolution threshold of 0.8, so the world state is unresolved. "
                "The decision is not. The runner-up, evacuating north, has an expected loss of "
                "35.72, so the margin is 29.72, and the smallest single-cell perturbation that "
                "would change the recommendation is 29.72 / 0.34 = 87.41 - far beyond the "
                "declared tolerance of 1. "
                "Reinforcing also has a worst case of 6, inside the acceptable loss of 10, so it "
                "is robust as well as optimal; no evacuation is, since each has a worst case of "
                "50."
            ),
            "results": {
                "objective": "expected_loss",
                "expected_loss": {
                    "reinforce_refuge": 6.0,
                    "evacuate_north": L3_EVAC_N,
                    "evacuate_south": L3_EVAC_S,
                    "evacuate_east": L3_EVAC_E,
                },
                "worst_case_loss": {
                    "reinforce_refuge": 6.0,
                    "evacuate_north": 50.0,
                    "evacuate_south": 50.0,
                    "evacuate_east": 50.0,
                },
                "recommended_action": "reinforce_refuge",
                "clairvoyant_expected_loss": 6.0,
                "evpi": 0.0,
                "information_would_change_action": False,
                "action_optimal_in_every_scenario": ["reinforce_refuge"],
                "robust_actions": ["reinforce_refuge"],
                "robust_action_exists": True,
                "state_certainty": L3_W[0],
                "state_resolved": False,
                "decision_margin": L3_EVAC_N - 6.0,
                "min_perturbation_to_flip": L3_MIN_PERTURBATION,
                "decision_stable": True,
                "decision_resolved": True,
            },
            "invariants": [
                {
                    "expression": "r['state_resolved'] is False and r['decision_resolved'] is True",
                    "description": "unresolved world, resolved decision",
                },
                {
                    "expression": "r['evpi'] == 0.0",
                    "description": "perfect information would change nothing",
                },
                {
                    "expression": "r['action_optimal_in_every_scenario'] == ['reinforce_refuge']",
                    "description": "one action is optimal in every scenario, not just on average",
                },
            ],
        },
        readme=f"""
# WG-BM-061 (L3) — Unresolved state, resolved decision

## Scenario

The fire could break north, south or east. The ensemble is close to uniform:
**0.34 / 0.33 / 0.33.**

| | north | south | east |
|---|---|---|---|
| `reinforce_refuge` | **6** | **6** | **6** |
| `evacuate_north` | 8 | 50 | 50 |
| `evacuate_south` | 50 | 8 | 50 |
| `evacuate_east` | 50 | 50 | 8 |

Declared: acceptable loss 10, state-resolution threshold 0.8, perturbation
tolerance 1.0.

## Derivation

Reinforcing costs 6 everywhere. Every evacuation costs at least 8 **even in the
scenario it was chosen for**, so reinforcing is the best action in each scenario
separately:

```
clairvoyant expected loss = 6 = E[reinforce_refuge]
EVPI = 0                                          exactly
```

```
largest scenario weight = 0.34  <  0.8   ->  state NOT resolved
runner-up expected loss = {L3_EVAC_N:.2f},  margin = {L3_EVAC_N - 6.0:.2f}
smallest single-cell perturbation that flips it = {L3_EVAC_N - 6.0:.2f} / 0.34 = {L3_MIN_PERTURBATION:.2f}  >>  1.0
                                         ->  decision IS resolved
```

Reinforcing is also **robust**: worst case 6, inside the acceptable loss of 10.
No evacuation is; each has a worst case of 50.

## The governance point

> Uncertainty about the world does not imply a need for more information.

The state here is as unresolved as a three-way ensemble can be, and the decision
is completely determined: perfect knowledge of which way the fire breaks would
change nothing and be worth nothing. A system that reports "cannot decide,
acquire more data" has answered the wrong question — and in an incident the cost
of that answer is the time spent waiting.

The right question is not *how uncertain are we?* but **would any resolution of
the uncertainty change what we do?** Those come apart in both directions:

| | WG-BM-061 (here) | WG-BM-062 |
|---|---|---|
| state resolved | **no** (0.34) | yes (0.97) |
| decision resolved | **yes** | **no** |

The `unresolved_state_blocks_decision` mutation reports an unresolved decision
whenever the state is unresolved; this benchmark and WG-BM-063 are its declared
detectors.

## Expected

| Quantity | Value |
|---|---|
| expected loss, reinforce | 6 |
| EVPI | **0** |
| optimal in every scenario | `reinforce_refuge` |
| state certainty | 0.34 → not resolved |
| perturbation needed to flip | {L3_MIN_PERTURBATION:.2f} → stable |
| decision resolved | **true** |
""",
    ))

    # ------------------------------------------------------------------ L4
    written.append(write_benchmark(
        directory="benchmarks/risk/WG-BM-062_L4_resolved_state_fragile_decision",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-062",
            "label": "L4",
            "title": "The world is 97 per cent resolved and the decision turns on 0.21",
            "category": "risk",
            "difficulty": "adversarial",
            "purpose": "The mirror image of WG-BM-061. State certainty is high, the two actions "
                       "differ by 0.21 in expected loss, and a perturbation of 0.22 to a single "
                       "loss cell reverses the recommendation.",
            "solver": "risk.objective_comparison",
            "assumptions": {
                "objective": "expected_loss",
                "state_resolution_threshold": 0.8,
                "perturbation_tolerance": 1.0,
                "loss_numbers_are_elicited_not_measured": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "scenario_ensemble",
                "expected_value": "10.00 vs 10.21; margin 0.21",
            },
            "expected_behavior": {
                "state_resolved": True,
                "decision_stable": False,
                "decision_resolved": False,
            },
            "tolerance": TOL,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["state_certainty_mistaken_for_decision_confidence", "fragile_recommendation"],
            "mutations_expected_to_fail": [],
            "hand_checkable": True,
            "notes": "No mutation is claimed: the content is a property of the loss numbers, not "
                     "an injectable bug. The benchmark exists so that a system reporting a "
                     "recommendation also reports how much it took to make it.",
        },
        inputs={
            "risk": {
                "description": "The fire's behaviour is nearly certain - 97 per cent on one "
                               "scenario - and the two available responses are separated by two "
                               "hundredths of their own magnitude. The loss numbers were elicited "
                               "from an incident commander, not measured.",
                "objective": "expected_loss",
                "cvar_alpha": 0.9,
                "acceptable_loss": 15.0,
                "state_resolution_threshold": 0.8,
                "perturbation_tolerance": 1.0,
                "scenarios": [
                    {"id": "omega_expected", "probability": 0.97},
                    {"id": "omega_surprise", "probability": 0.03},
                ],
                "actions": ["action_a", "action_b"],
                "losses": {
                    "action_a": {"omega_expected": 10.0, "omega_surprise": 10.0},
                    "action_b": {"omega_expected": 10.0, "omega_surprise": 17.0},
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-062",
            "source": "exhaustive_enumeration",
            "derivation": (
                "E[action_a] = 10 and E[action_b] = 0.97 * 10 + 0.03 * 17 = 9.7 + 0.51 = 10.21, "
                "so action_a is recommended by a margin of 0.21 - about two per cent of either "
                "action's own magnitude. "
                "The smallest change to a single loss cell that reverses the recommendation is "
                "0.21 divided by the probability of the scenario that cell belongs to, and the "
                "largest such probability is 0.97, giving 0.21 / 0.97 = 0.2164948453608247. The "
                "declared perturbation tolerance is 1.0, so the recommendation is not stable: "
                "revising any single loss estimate by one unit could flip it. "
                "Meanwhile the state is resolved: the leading scenario carries 0.97, far above "
                "the declared threshold of 0.8. Both actions are also acceptable - worst cases 10 "
                "and 17 against an acceptable loss of 15 puts action_a inside and action_b "
                "outside. "
                "Perfect information would not help either: action_a attains the minimum in both "
                "scenarios, so the clairvoyant expected loss is 10 and EVPI is 0. The fragility "
                "is in the loss elicitation, not in the uncertainty about the world."
            ),
            "results": {
                "objective": "expected_loss",
                "expected_loss": {"action_a": 10.0, "action_b": L4_EB},
                "worst_case_loss": {"action_a": 10.0, "action_b": 17.0},
                "recommended_action": "action_a",
                "clairvoyant_expected_loss": 10.0,
                "evpi": 0.0,
                "information_would_change_action": False,
                "action_optimal_in_every_scenario": ["action_a"],
                "robust_actions": ["action_a"],
                "state_certainty": 0.97,
                "most_likely_scenario": "omega_expected",
                "state_resolved": True,
                "decision_margin": L4_MARGIN,
                "min_perturbation_to_flip": L4_MIN_PERTURBATION,
                "perturbation_tolerance": 1.0,
                "decision_stable": False,
                "decision_resolved": False,
            },
            "invariants": [
                {
                    "expression": "r['state_resolved'] is True and r['decision_stable'] is False",
                    "description": "high state certainty, fragile decision",
                },
                {
                    "expression": "r['min_perturbation_to_flip'] < r['perturbation_tolerance']",
                    "description": "a perturbation inside the declared tolerance reverses the recommendation",
                },
                {
                    "expression": "r['decision_margin'] < 0.03 * r['expected_loss']['action_a']",
                    "description": "the margin is under three per cent of the loss scale",
                },
            ],
        },
        readme=f"""
# WG-BM-062 (L4) — Identifiable state, fragile decision

## Scenario

The fire's behaviour is nearly certain — **97 per cent** on one scenario.

| | expected (0.97) | surprise (0.03) |
|---|---|---|
| `action_a` | 10 | 10 |
| `action_b` | 10 | 17 |

The loss numbers were **elicited from an incident commander, not measured.**

## Derivation

```
E[action_a] = 10
E[action_b] = 0.97 * 10 + 0.03 * 17 = 10.21
margin      = {L4_MARGIN:.2f}                       about 2% of either action's magnitude
```

The smallest change to a **single loss cell** that reverses the recommendation
is the margin divided by that cell's scenario probability, minimised over cells:

```
{L4_MARGIN:.2f} / 0.97 = {L4_MIN_PERTURBATION:.4f}        <  declared tolerance 1.0
```

So revising any one loss estimate by a single unit could flip the answer.

```
state certainty = 0.97  >  0.8       ->  state RESOLVED
min perturbation = {L4_MIN_PERTURBATION:.4f}  <  1.0   ->  decision NOT stable
EVPI = 0                             ->  more data about the world would not help
```

## The mirror image of WG-BM-061

| | WG-BM-061 | WG-BM-062 (here) |
|---|---|---|
| state resolved | no (0.34) | **yes (0.97)** |
| decision resolved | **yes** | no |
| what would help | nothing | **better loss estimates** |

Both benchmarks have `EVPI = 0`, and for opposite reasons. There the action was
insensitive to the world; here the world is known and the action is sensitive to
**the loss numbers**, which no amount of observation will pin down.

That is the diagnostic value of separating the two axes. "We are 97% sure what
the fire will do" is a statement about the state, and it says nothing about
whether the recommendation that follows is worth acting on. A system that
reports only the state certainty has published the more comforting of the two
numbers.

## What a system should do here

Report the margin. `decision_margin: 0.21` next to `expected_loss: 10.00` tells
the reader that the recommendation is a coin toss dressed as an optimisation,
and that the productive next step is to re-elicit the loss of `action_b` in the
surprise scenario — not to gather more weather data.

No mutation is claimed for this benchmark: the fragility is a property of the
numbers, not a bug that can be injected.

## Expected

| Quantity | Value |
|---|---|
| expected loss, A / B | 10.00 / {L4_EB:.2f} |
| margin | **{L4_MARGIN:.2f}** |
| perturbation needed to flip | **{L4_MIN_PERTURBATION:.4f}** (tolerance 1.0) |
| state resolved | **true** (0.97) |
| decision stable | **false** |
| EVPI | 0 |
""",
    ))

    # ------------------------------------------------------------------ L5
    written.append(write_benchmark(
        directory="benchmarks/risk/WG-BM-063_L5_robust_action_despite_poor_skill",
        script=SCRIPT,
        meta={
            "benchmark_id": "WG-BM-063",
            "label": "L5",
            "title": "Poor forecast skill, stable decision",
            "category": "risk",
            "difficulty": "intermediate",
            "purpose": "A forecast with a skill score of 0.25 spread over four worlds, all of "
                       "which select the same staging action. Poor skill does not imply a poor "
                       "decision.",
            "solver": "risk.objective_comparison",
            "assumptions": {
                "objective": "expected_loss",
                "state_resolution_threshold": 0.8,
                "acceptable_loss": 8,
                "perturbation_tolerance": 1.0,
                "skill_score_is_metadata_only": True,
            },
            "information_structure": {
                "probabilistic": True,
                "forecast_type": "scenario_ensemble",
                "expected_value": "EVPI = 0 with a forecast skill score of 0.25",
            },
            "expected_behavior": {
                "evpi": 0.0,
                "decision_resolved": True,
                "state_resolved": False,
            },
            "tolerance": TOL,
            "exactness": "FINITE_ENUMERATION",
            "detects": ["skill_value_conflation", "uncertainty_conflated_with_indecision"],
            "mutations_expected_to_fail": ["unresolved_state_blocks_decision"],
            "hand_checkable": True,
        },
        inputs={
            "risk": {
                "description": "A poor forecast spreads 0.4 / 0.3 / 0.2 / 0.1 over four possible "
                               "fire behaviours. Staging at the central junction is the best "
                               "response to all four; staging north or south is a bet on the "
                               "forecast being right.",
                "objective": "expected_loss",
                "cvar_alpha": 0.9,
                "acceptable_loss": 8.0,
                "state_resolution_threshold": 0.8,
                "perturbation_tolerance": 1.0,
                "forecast_skill_score": 0.25,
                "scenarios": [
                    {"id": "omega_1", "probability": 0.4},
                    {"id": "omega_2", "probability": 0.3},
                    {"id": "omega_3", "probability": 0.2},
                    {"id": "omega_4", "probability": 0.1},
                ],
                "actions": ["stage_at_junction", "stage_north", "stage_south"],
                "losses": {
                    "stage_at_junction": {
                        "omega_1": 4.0, "omega_2": 4.0, "omega_3": 5.0, "omega_4": 5.0,
                    },
                    "stage_north": {
                        "omega_1": 6.0, "omega_2": 9.0, "omega_3": 12.0, "omega_4": 20.0,
                    },
                    "stage_south": {
                        "omega_1": 20.0, "omega_2": 12.0, "omega_3": 9.0, "omega_4": 6.0,
                    },
                },
            }
        },
        expected={
            "benchmark_id": "WG-BM-063",
            "source": "exhaustive_enumeration",
            "derivation": (
                "E[stage_at_junction] = 0.4*4 + 0.3*4 + 0.2*5 + 0.1*5 = 1.6 + 1.2 + 1.0 + 0.5 = "
                "4.3; E[stage_north] = 2.4 + 2.7 + 2.4 + 2.0 = 9.5; E[stage_south] = 8.0 + 3.6 + "
                "1.8 + 0.6 = 14.0. "
                "Staging at the junction is also the minimum in each scenario separately - 4, 4, "
                "5, 5 against 6, 9, 9 and 6 for the best alternative in each - so the clairvoyant "
                "expected loss is 4.3 and EVPI is exactly 0. "
                "The forecast is poor: it spreads 0.4 / 0.3 / 0.2 / 0.1 across four behaviours, "
                "its declared skill score is 0.25, and the largest scenario weight is 0.4, far "
                "below the resolution threshold of 0.8, so the state is unresolved. The decision "
                "is not: the runner-up is 5.2 behind, and the smallest single-cell perturbation "
                "that would flip it is 5.2 / 0.4 = 13.0, thirteen times the declared tolerance. "
                "The junction's worst case is 5, inside the acceptable loss of 8, so it is robust "
                "as well as optimal."
            ),
            "results": {
                "objective": "expected_loss",
                "expected_loss": {
                    "stage_at_junction": 4.3,
                    "stage_north": 9.5,
                    "stage_south": 14.0,
                },
                "worst_case_loss": {
                    "stage_at_junction": 5.0, "stage_north": 20.0, "stage_south": 20.0,
                },
                "cvar": {"stage_at_junction": 5.0, "stage_north": 20.0, "stage_south": 20.0},
                "recommended_action": "stage_at_junction",
                "clairvoyant_expected_loss": 4.3,
                "evpi": 0.0,
                "information_would_change_action": False,
                "action_optimal_in_every_scenario": ["stage_at_junction"],
                "robust_actions": ["stage_at_junction"],
                "state_certainty": 0.4,
                "state_resolved": False,
                "decision_margin": 5.2,
                "min_perturbation_to_flip": 13.0,
                "decision_stable": True,
                "decision_resolved": True,
                "forecast_skill_score": 0.25,
            },
            "invariants": [
                {
                    "expression": "r['forecast_skill_score'] < 0.5 and r['decision_resolved'] is True",
                    "description": "poor skill, resolved decision",
                },
                {
                    "expression": "r['evpi'] == 0.0",
                    "description": "improving the forecast could not improve the decision",
                },
                {
                    "expression": "r['min_perturbation_to_flip'] > 10 * r['perturbation_tolerance']",
                    "description": "the recommendation is stable by an order of magnitude",
                },
            ],
        },
        readme="""
# WG-BM-063 (L5) — Robust action despite poor forecast skill

## Scenario

A poor forecast (declared skill score **0.25**) spreads its weight across four
possible fire behaviours: **0.4 / 0.3 / 0.2 / 0.1.**

| | `omega_1` | `omega_2` | `omega_3` | `omega_4` |
|---|---|---|---|---|
| `stage_at_junction` | **4** | **4** | **5** | **5** |
| `stage_north` | 6 | 9 | 12 | 20 |
| `stage_south` | 20 | 12 | 9 | 6 |

## Derivation

```
E[stage_at_junction] = 1.6 + 1.2 + 1.0 + 0.5 = 4.3
E[stage_north]       = 2.4 + 2.7 + 2.4 + 2.0 = 9.5
E[stage_south]       = 8.0 + 3.6 + 1.8 + 0.6 = 14.0
```

The junction is also the minimum **in every scenario separately**, so

```
clairvoyant = 4.3     EVPI = 0
```

```
largest weight = 0.4  <  0.8          ->  state not resolved
margin = 5.2,  flip needs 5.2/0.4 = 13.0  >>  1.0   ->  decision stable
worst case 5  <=  acceptable loss 8   ->  robust
```

## Skill and value, once more

WG-BM-031 (G4) showed a crude forecast beating an accurate one because it
arrived in time. This shows something stronger: a forecast with a skill score of
0.25 supporting a decision that **perfect skill could not improve**, because
`EVPI = 0`.

The consequence for a forecasting programme is uncomfortable and worth stating
plainly: for a decision of this shape, forecast improvement has **no** decision
value, at any level of investment. The useful question is not "how good is the
forecast?" but "which decisions does its quality actually gate?" — and answering
that requires the loss structure, which is not part of any forecast evaluation.

Read together, the three cases separate what is usually one undifferentiated
worry:

| | uncertain about | fixable by |
|---|---|---|
| WG-BM-061 | which scenario | nothing — the action is already optimal |
| WG-BM-062 | the loss numbers | re-elicitation, not observation |
| WG-BM-063 (here) | the forecast | nothing — skill does not gate this decision |

## Expected

| Quantity | Value |
|---|---|
| expected loss, junction / north / south | 4.3 / 9.5 / 14.0 |
| optimal in every scenario | `stage_at_junction` |
| EVPI | **0** |
| forecast skill score | 0.25 |
| state resolved / decision resolved | **false** / **true** |
""",
    ))

    report(written)


if __name__ == "__main__":
    main()
