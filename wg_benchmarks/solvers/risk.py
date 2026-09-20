"""Reference solver for probabilistic decision risk (the L family).

Separates three questions that get run together:

* **Which action is best?** — and under *which declared objective*. Expected
  loss, CVaR and worst case are different objectives that rank actions
  differently, so the objective is an input, never an assumption. ``report_only``
  declines to name a winner, which is sometimes the honest answer.
* **Is the world state resolved?** — whether any scenario carries most of the
  probability mass.
* **Is the decision resolved?** — whether the recommended action would survive
  learning the true scenario, and whether it survives a small perturbation of
  the loss numbers.

Those last two are independent. An unresolved state can have a fully resolved
decision (WG-BM-061) and a resolved state can have a fragile one (WG-BM-062),
which is why the suite refuses to treat uncertainty about the world as
equivalent to uncertainty about what to do.
"""

from __future__ import annotations

from .. import mutations
from .scenario import cvar

INF = float("inf")


def solve(inputs: dict) -> dict:
    document = inputs["risk"]
    scenarios = {str(s["id"]): float(s["probability"]) for s in document["scenarios"]}
    mass = sum(scenarios.values())
    if abs(mass - 1.0) > 1e-12:
        raise ValueError(f"scenario probabilities sum to {mass}, not 1")
    actions = [str(a) for a in document["actions"]]
    losses = {
        str(a): {str(s): float(v) for s, v in row.items()}
        for a, row in document["losses"].items()
    }
    alpha = float(document.get("cvar_alpha", 0.9))
    objective = str(document.get("objective", "expected_loss"))

    expected = {a: sum(scenarios[s] * losses[a][s] for s in scenarios) for a in actions}
    tail = {
        a: cvar([(losses[a][s], scenarios[s]) for s in scenarios], alpha) for a in actions
    }
    worst = {a: max(losses[a][s] for s in scenarios) for a in actions}
    best_per_scenario = {s: min(losses[a][s] for a in actions) for s in scenarios}
    max_regret = {
        a: max(losses[a][s] - best_per_scenario[s] for s in scenarios) for a in actions
    }

    best_by_expected = min(sorted(actions), key=lambda a: expected[a])
    best_by_cvar = min(sorted(actions), key=lambda a: tail[a])
    best_by_worst = min(sorted(actions), key=lambda a: worst[a])

    by_objective = {
        "expected_loss": best_by_expected,
        "cvar": best_by_cvar,
        "worst_case": best_by_worst,
    }
    recommended = by_objective.get(objective)
    # MUTATION HOOK: take the expected-loss winner whatever objective was
    # declared.
    if mutations.active("objective_ignored_use_mean") and objective != "report_only":
        recommended = best_by_expected

    clairvoyant = sum(scenarios[s] * best_per_scenario[s] for s in scenarios)
    evpi = expected[best_by_expected] - clairvoyant
    optimal_everywhere = sorted(
        a for a in actions
        if all(losses[a][s] <= best_per_scenario[s] + 1e-12 for s in scenarios)
    )

    acceptable = document.get("acceptable_loss")
    robust_actions = (
        sorted(a for a in actions if worst[a] <= float(acceptable) + 1e-12)
        if acceptable is not None
        else []
    )

    resolution_threshold = float(document.get("state_resolution_threshold", 0.8))
    state_certainty = max(scenarios.values())
    most_likely = max(sorted(scenarios), key=lambda s: scenarios[s])
    state_resolved = state_certainty >= resolution_threshold - 1e-12

    # Sensitivity of the expected-loss recommendation to a single loss cell.
    margin = None
    min_perturbation = None
    if objective in ("expected_loss", "report_only") and len(actions) > 1:
        ordered = sorted(actions, key=lambda a: (expected[a], a))
        margin = expected[ordered[1]] - expected[ordered[0]]
        min_perturbation = min(
            (expected[b] - expected[ordered[0]]) / scenarios[s]
            for b in actions
            if b != ordered[0]
            for s in scenarios
            if scenarios[s] > 0
        )
    tolerance = float(document.get("perturbation_tolerance", 0.0))
    decision_stable = None if min_perturbation is None else min_perturbation > tolerance

    information_changes_action = evpi > 1e-12
    decision_resolved = (not information_changes_action) and bool(decision_stable)
    # MUTATION HOOK: an unresolved world state is treated as an unresolved
    # decision, so the system asks for information it cannot use.
    if mutations.active("unresolved_state_blocks_decision") and not state_resolved:
        decision_resolved = False

    return {
        "objective": objective,
        "cvar_alpha": alpha,
        "expected_loss": expected,
        "cvar": tail,
        "worst_case_loss": worst,
        "max_regret": max_regret,
        "best_by_expected_loss": best_by_expected,
        "best_by_cvar": best_by_cvar,
        "best_by_worst_case": best_by_worst,
        "rankings_conflict": len({best_by_expected, best_by_cvar, best_by_worst}) > 1,
        "recommended_action": recommended,
        "winner_declared": recommended is not None,
        "clairvoyant_expected_loss": clairvoyant,
        "evpi": evpi,
        "information_would_change_action": information_changes_action,
        "action_optimal_in_every_scenario": optimal_everywhere,
        "acceptable_loss": None if acceptable is None else float(acceptable),
        "robust_actions": robust_actions,
        "robust_action_exists": bool(robust_actions),
        "state_certainty": state_certainty,
        "most_likely_scenario": most_likely,
        "state_resolution_threshold": resolution_threshold,
        "state_resolved": state_resolved,
        "decision_margin": margin,
        "min_perturbation_to_flip": min_perturbation,
        "perturbation_tolerance": tolerance,
        "decision_stable": decision_stable,
        "decision_resolved": decision_resolved,
        "forecast_skill_score": document.get("forecast_skill_score"),
    }
