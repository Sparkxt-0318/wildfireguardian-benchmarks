"""Scenario-set reference solver for the uncertainty (H) benchmarks.

Handles three things a wildfire decision system routinely gets wrong:

1. **Correlation.**  Joint road-failure probability is read off the scenario
   set, never reconstructed from marginals.
2. **Where the average goes.**  Loss is averaged over scenarios; scenario
   *inputs* are never averaged into one pseudo-world.
3. **What worst case means.**  Sup-regret is reported next to a
   probability-weighted CVaR precisely so that the mechanical dependence of
   sup-regret on ensemble size is visible.
"""

from __future__ import annotations

from .. import mutations


def cvar(outcomes: list[tuple[float, float]], alpha: float) -> float:
    """Conditional value at risk of a discrete loss distribution.

    ``outcomes`` is a list of ``(loss, probability)``.  CVaR at level ``alpha``
    is the mean loss over the worst ``1 - alpha`` of the probability mass, with
    atoms split proportionally when the tail boundary falls inside one.
    """
    tail_mass = 1.0 - alpha
    if tail_mass <= 0:
        return max(loss for loss, _ in outcomes)
    remaining = tail_mass
    total = 0.0
    for loss, probability in sorted(outcomes, key=lambda item: -item[0]):
        take = min(probability, remaining)
        total += take * loss
        remaining -= take
        if remaining <= 1e-15:
            break
    return total / tail_mass


def analyse_ensemble(
    scenarios: dict[str, float], actions: list[str], losses: dict[str, dict[str, float]], alpha: float
) -> dict:
    expected = {
        action: sum(scenarios[s] * losses[action][s] for s in scenarios) for action in actions
    }
    best_per_scenario = {s: min(losses[a][s] for a in actions) for s in scenarios}
    regret = {
        action: {s: losses[action][s] - best_per_scenario[s] for s in scenarios} for action in actions
    }
    max_regret = {action: max(regret[action].values()) for action in actions}
    tail = {
        action: cvar([(losses[action][s], scenarios[s]) for s in scenarios], alpha)
        for action in actions
    }
    clairvoyant = sum(scenarios[s] * best_per_scenario[s] for s in scenarios)
    best_expected = min(sorted(actions), key=lambda a: expected[a])
    minimax_regret_action = min(sorted(actions), key=lambda a: max_regret[a])
    return {
        "scenario_count": len(scenarios),
        "expected_loss": expected,
        "cvar": tail,
        "max_regret": max_regret,
        "best_action_by_expected_loss": best_expected,
        "minimax_regret_action": minimax_regret_action,
        "sup_regret": max_regret[minimax_regret_action],
        "clairvoyant_expected_loss": clairvoyant,
        "evpi": expected[best_expected] - clairvoyant,
        # Restricted to this ensemble's scenarios: the shared loss table may also
        # carry rows for scenarios that belong to a different ensemble.
        "worst_case_loss": {
            action: max(losses[action][s] for s in scenarios) for action in actions
        },
    }


def solve(inputs: dict) -> dict:
    document = inputs["scenario_analysis"]
    actions = [str(a) for a in document["actions"]]
    losses = {
        str(action): {str(s): float(v) for s, v in row.items()}
        for action, row in document["losses"].items()
    }
    alpha = float(document.get("cvar_alpha", 0.9))

    ensembles = {}
    for raw in document["ensembles"]:
        scenarios = {str(s["id"]): float(s["probability"]) for s in raw["scenarios"]}
        mass = sum(scenarios.values())
        if abs(mass - 1.0) > 1e-9:
            raise ValueError(f"ensemble {raw['id']}: probabilities sum to {mass}")
        analysis = analyse_ensemble(scenarios, actions, losses, alpha)
        # MUTATION HOOK: collapse the ensemble into one averaged world and
        # evaluate the decision there instead of averaging the losses.
        if mutations.active("average_scenario_inputs") and document.get("averaged_world"):
            averaged = {
                str(a): float(v) for a, v in document["averaged_world"]["losses"].items()
            }
            analysis["expected_loss"] = averaged
            analysis["best_action_by_expected_loss"] = min(sorted(averaged), key=lambda a: averaged[a])
        ensembles[str(raw["id"])] = analysis

    result: dict = {"cvar_alpha": alpha, "ensembles": ensembles}

    if document.get("averaged_world"):
        averaged = {str(a): float(v) for a, v in document["averaged_world"]["losses"].items()}
        result["averaged_world_loss"] = averaged
        result["averaged_world_best_action"] = min(sorted(averaged), key=lambda a: averaged[a])

    failure = document.get("edge_failure")
    if failure:
        edges = [str(e) for e in failure["edges"]]
        ensemble_id = str(failure.get("ensemble", document["ensembles"][0]["id"]))
        scenarios = {
            str(s["id"]): float(s["probability"])
            for raw in document["ensembles"]
            if str(raw["id"]) == ensemble_id
            for s in raw["scenarios"]
        }
        states = {
            str(scenario): {str(e): str(v) for e, v in row.items()}
            for scenario, row in failure["states"].items()
        }
        marginals = {
            edge: sum(p for s, p in scenarios.items() if states[s][edge] == "closed")
            for edge in edges
        }
        joint_true = sum(
            p for s, p in scenarios.items() if all(states[s][edge] == "closed" for edge in edges)
        )
        product = 1.0
        for edge in edges:
            product *= marginals[edge]
        reported = joint_true
        # MUTATION HOOK: reconstruct the joint from the marginals as if the
        # roads failed independently.
        if mutations.active("independent_edge_failures"):
            reported = product
        result["edge_failure"] = {
            "edges": edges,
            "marginal_closure_probability": marginals,
            "joint_all_closed_probability": reported,
            "joint_under_independence": product,
            "independence_error_factor": (joint_true / product) if product > 0 else None,
            "probability_no_egress": reported,
            "correlation_matters": abs(joint_true - product) > 1e-12,
        }

    comparison = document.get("ensemble_comparison")
    if comparison:
        first, second = str(comparison["from"]), str(comparison["to"])
        a, b = ensembles[first], ensembles[second]
        action = str(comparison.get("action", a["best_action_by_expected_loss"]))
        result["ensemble_comparison"] = {
            "from": first,
            "to": second,
            "action": action,
            "expected_loss_change": b["expected_loss"][action] - a["expected_loss"][action],
            "sup_regret_change": b["sup_regret"] - a["sup_regret"],
            "cvar_change": b["cvar"][action] - a["cvar"][action],
            "minimax_action_changed": a["minimax_regret_action"] != b["minimax_regret_action"],
            "scenario_count_change": b["scenario_count"] - a["scenario_count"],
        }
    return result
