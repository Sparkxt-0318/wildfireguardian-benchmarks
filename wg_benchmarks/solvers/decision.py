"""Decision-value reference solver for the forecast-value (G) and robust
protectability (J) benchmarks.

A decision problem is a finite loss matrix over (action, scenario) pairs, a
prior over scenarios, a decision deadline, and a set of information sources each
with an availability time and a deterministic signal map.  Policies are
enumerated exhaustively; nothing is optimised numerically.

Three quantities are kept rigorously apart, because conflating them is the
failure mode the G family exists to catch:

``skill``
    A property of the forecast alone (spatial error, skill score).  Never used
    to choose an action.

``expected value``
    ``E[loss(baseline)] - E[loss(policy))]`` under the prior.  Positive means the
    information helped.

``realised value``
    The same difference evaluated in the single scenario that actually
    happened.  A forecast can have positive expected value and negative realised
    value, and a benchmark must say which one it pins down.

Timeliness is enforced: an information source that becomes available after the
decision deadline cannot influence the action, and a policy that waits for it
takes its declared fallback action instead.
"""

from __future__ import annotations

from .. import mutations

INF = float("inf")


def _expected(losses: dict[str, float], probabilities: dict[str, float]) -> float:
    return sum(probabilities[s] * losses[s] for s in probabilities)


def solve(inputs: dict) -> dict:
    document = inputs["decision"]
    scenarios = {str(s["id"]): float(s["probability"]) for s in document["scenarios"]}
    total = sum(scenarios.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"scenario probabilities sum to {total}, not 1")
    actions = [str(a) for a in document["actions"]]
    loss = {
        str(action): {str(s): float(v) for s, v in row.items()}
        for action, row in document["loss"].items()
    }
    deadline = float(document.get("decision_deadline_min", INF))
    default_action = str(document.get("default_action", actions[0]))
    truth = str(document["truth_scenario"])

    sources = {}
    for raw in document.get("information_sources", []):
        sources[str(raw["id"])] = {
            "available_at_min": float(raw.get("available_at_min", 0.0)),
            "signal": {str(k): str(v) for k, v in raw["signal"].items()},
            "skill_score": raw.get("skill_score"),
            "spatial_error_m": raw.get("spatial_error_m"),
        }

    def timely(source_id: str) -> bool:
        available = sources[source_id]["available_at_min"]
        # MUTATION HOOK: a forecast is applied to the decision whatever time it
        # arrives, so lateness costs nothing.
        if mutations.active("forecast_always_trusted"):
            return True
        return available <= deadline + 1e-12

    def posterior(source_id: str, signal_value: str) -> dict[str, float]:
        mapping = sources[source_id]["signal"]
        weights = {s: p for s, p in scenarios.items() if mapping.get(s) == signal_value}
        mass = sum(weights.values())
        if mass == 0:
            return dict(scenarios)
        return {s: p / mass for s, p in weights.items()}

    def bayes_action(source_id: str, signal_value: str) -> str:
        belief = posterior(source_id, signal_value)
        return min(
            sorted(actions),
            key=lambda a: sum(belief[s] * loss[a][s] for s in belief),
        )

    policies = {}
    for raw in document["policies"]:
        policy_id = str(raw["id"])
        kind = str(raw.get("type", "fixed"))
        fallback = str(raw.get("fallback_action", default_action))
        if kind == "fixed":
            action_by_scenario = {s: str(raw["action"]) for s in scenarios}
            informed = False
            source_id = None
        elif kind == "informed":
            source_id = str(raw["source"])
            informed = timely(source_id)
            if informed:
                action_by_scenario = {
                    s: bayes_action(source_id, sources[source_id]["signal"][s]) for s in scenarios
                }
            else:
                action_by_scenario = {s: fallback for s in scenarios}
        elif kind == "signal_map":
            source_id = str(raw["source"])
            informed = timely(source_id)
            mapping = {str(k): str(v) for k, v in raw["map"].items()}
            if informed:
                action_by_scenario = {
                    s: mapping[sources[source_id]["signal"][s]] for s in scenarios
                }
            else:
                action_by_scenario = {s: fallback for s in scenarios}
        else:  # pragma: no cover - guarded by schema
            raise ValueError(f"unknown policy type: {kind}")
        losses = {s: loss[action_by_scenario[s]][s] for s in scenarios}
        policies[policy_id] = {
            "type": kind,
            "source": source_id,
            "uses_information": informed,
            "information_timely": informed,
            "action_by_scenario": action_by_scenario,
            "action_in_truth": action_by_scenario[truth],
            "expected_loss": _expected(losses, scenarios),
            "realised_loss": losses[truth],
            "worst_case_loss": max(losses.values()),
            "skill_score": sources[source_id]["skill_score"] if source_id else None,
            "spatial_error_m": sources[source_id]["spatial_error_m"] if source_id else None,
        }

    baseline_id = str(document.get("baseline_policy", document["policies"][0]["id"]))
    baseline = policies[baseline_id]

    for policy in policies.values():
        policy["value_vs_baseline"] = baseline["expected_loss"] - policy["expected_loss"]
        policy["realised_value_vs_baseline"] = baseline["realised_loss"] - policy["realised_loss"]

    best_in_truth = min(loss[a][truth] for a in actions)
    for policy in policies.values():
        policy["realised_regret"] = policy["realised_loss"] - best_in_truth

    clairvoyant = sum(
        scenarios[s] * min(loss[a][s] for a in actions) for s in scenarios
    )
    best_fixed = min(
        sorted(actions), key=lambda a: _expected(loss[a], scenarios)
    )
    best_fixed_loss = _expected(loss[best_fixed], scenarios)
    evpi = best_fixed_loss - clairvoyant

    timely_sources = [sid for sid in sources if timely(sid)]
    realizable = None
    if sources:
        candidates = [
            p for p in policies.values() if p["uses_information"]
        ]
        if candidates:
            realizable = baseline["expected_loss"] - min(p["expected_loss"] for p in candidates)
        else:
            realizable = 0.0

    ranked_by_value = sorted(policies, key=lambda p: (-policies[p]["value_vs_baseline"], p))
    ranked_by_skill = sorted(
        policies,
        key=lambda p: (
            -(policies[p]["skill_score"] if policies[p]["skill_score"] is not None else -1.0),
            p,
        ),
    )
    recommended = ranked_by_value[0]
    # MUTATION HOOK: pick the most skilful forecast instead of the most useful
    # one.
    if mutations.active("skill_implies_value"):
        recommended = ranked_by_skill[0]

    return {
        "truth_scenario": truth,
        "decision_deadline_min": deadline,
        "baseline_policy": baseline_id,
        "policies": policies,
        "expected_loss_by_policy": {k: v["expected_loss"] for k, v in policies.items()},
        "realised_loss_by_policy": {k: v["realised_loss"] for k, v in policies.items()},
        "value_by_policy": {k: v["value_vs_baseline"] for k, v in policies.items()},
        "realised_value_by_policy": {k: v["realised_value_vs_baseline"] for k, v in policies.items()},
        "realised_regret_by_policy": {k: v["realised_regret"] for k, v in policies.items()},
        "best_loss_in_truth_scenario": best_in_truth,
        "action_in_truth_by_policy": {k: v["action_in_truth"] for k, v in policies.items()},
        "timely_information_sources": sorted(timely_sources),
        "late_information_sources": sorted(set(sources) - set(timely_sources)),
        "clairvoyant_expected_loss": clairvoyant,
        "best_fixed_action": best_fixed,
        "best_fixed_expected_loss": best_fixed_loss,
        "evpi": evpi,
        "realizable_value_of_information": realizable,
        "ranked_by_value": ranked_by_value,
        "ranked_by_skill": ranked_by_skill,
        "recommended_policy": recommended,
        "skill_and_value_agree": ranked_by_value[0] == ranked_by_skill[0],
        "identical_actions_to_baseline": {
            k: v["action_by_scenario"] == baseline["action_by_scenario"] for k, v in policies.items()
        },
    }
